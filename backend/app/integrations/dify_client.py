import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx

from backend.app.common.enums import ReportType
from backend.app.core.config import Settings, get_settings


class DifyClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    # ------------------------------------------------------------------
    # 文件上传
    # ------------------------------------------------------------------

    def upload_file(self, file_path: str, file_content: bytes, mime_type: str = "application/octet-stream") -> dict[str, Any]:
        """上传文件到 Dify，返回 upload_file_id 等信息。"""
        api_key = self.settings.dify_cj_api_key or self.settings.dify_api_key
        if not api_key:
            raise RuntimeError("未配置 Dify API Key")
        url = f"{self.settings.dify_api_base_url.rstrip('/')}/files/upload"
        file_name = Path(file_path).name
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=120) as client:
            response = client.post(
                url,
                data={"user": "education-service-backend"},
                files={"file": (file_name, file_content, mime_type)},
                headers=headers,
            )
            response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # 客户画像研判
    # ------------------------------------------------------------------

    def call_customer_judgement(
        self,
        customer_info_text: str,
        sys_query: str | None = None,
        trace_id: str | None = None,
        file_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """调用 Dify 客户画像研判工作流，返回结构化研判结果。"""
        if self.settings.dify_mock_enabled:
            return _mock_customer_judgement_result()
        return self._call_dify_judgement_workflow(customer_info_text, sys_query, trace_id, file_ids)

    def _call_dify_judgement_workflow(
        self,
        customer_info_text: str,
        sys_query: str | None,
        trace_id: str | None,
        file_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        api_key = self.settings.dify_cj_api_key or self.settings.dify_api_key
        if not api_key:
            raise RuntimeError("未配置 Dify API Key（DIFY_CJ_API_KEY 或 DIFY_API_KEY）")
        url = f"{self.settings.dify_api_base_url.rstrip('/')}/chat-messages"
        payload: dict[str, Any] = {
            "inputs": {"customer_info_text": customer_info_text},
            "query": sys_query or "请对该客户信息进行画像研判",
            "response_mode": "blocking",
            "user": "education-service-backend",
        }
        if file_ids:
            payload["files"] = [
                {"type": "document", "transfer_method": "local_file", "upload_file_id": fid}
                for fid in file_ids
            ]
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=120) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        # 兼容多种响应结构：data.data.outputs / data.data.answer / data.answer
        answer_text = (
            data.get("answer", "")
            or data.get("data", {}).get("answer", "")
            or data.get("data", {}).get("outputs", {}).get("result", "")
        )
        if not answer_text:
            raise RuntimeError(f"Dify 返回内容为空，完整响应: {json.dumps(data, ensure_ascii=False)[:500]}")
        try:
            raw = _parse_llm_json(answer_text)
        except Exception:
            raise RuntimeError(f"Dify 返回内容非 JSON，原文: {answer_text[:300]}")
        # 接受单对象或数组（批量模式）
        if isinstance(raw, list):
            if len(raw) == 0:
                raise RuntimeError("Dify 返回空数组")
            if not isinstance(raw[0], dict) or "executive_summary" not in raw[0]:
                raise RuntimeError(f"Dify 返回数组元素缺少 executive_summary 字段: {json.dumps(raw[:2], ensure_ascii=False)[:300]}")
        elif isinstance(raw, dict):
            if "executive_summary" not in raw:
                raise RuntimeError(f"Dify 返回 JSON 缺少 executive_summary 字段: {json.dumps(raw, ensure_ascii=False)[:300]}")
        else:
            raise RuntimeError(f"Dify 返回格式错误，期望Object或Array: {str(raw)[:200]}")
        return raw

    def call_service_agent(
        self,
        query: str,
        conversation_id: str | None = None,
        visitor_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """调用 Dify 客服 Agent，直接返回回复。知识检索由 Agent 内部完成。"""
        if self.settings.dify_mock_enabled:
            return _mock_service_agent_result(query, conversation_id)
        api_key = self.settings.dify_service_agent_api_key or self.settings.dify_api_key
        if not api_key:
            raise RuntimeError("未配置 Dify 客服 Agent API Key")
        url = f"{self.settings.dify_api_base_url.rstrip('/')}/chat-messages"
        payload = {
            "inputs": {
                "visitor_id": visitor_id,
                "trace_id": trace_id,
            },
            "query": query,
            "response_mode": "blocking",
            "user": visitor_id or "visitor",
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=120) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        answer = data.get("answer") or data.get("data", {}).get("answer") or ""
        outputs = data.get("data", {}).get("outputs", {}) if isinstance(data.get("data"), dict) else {}
        parsed_outputs = outputs if isinstance(outputs, dict) else {}
        if not parsed_outputs and answer:
            try:
                parsed_outputs = _parse_llm_json(answer)
                answer = parsed_outputs.get("reply_text") or parsed_outputs.get("answer") or answer
            except Exception:
                parsed_outputs = {}
        return {
            "answer": answer,
            "conversation_id": data.get("conversation_id") or data.get("data", {}).get("conversation_id") or conversation_id,
            "intent": parsed_outputs.get("intent"),
            "suggested_actions": parsed_outputs.get("suggested_actions", []),
            "references": parsed_outputs.get("references", []),
            "raw": data,
        }

    # ------------------------------------------------------------------
    # 报告生成（已有）
    # ------------------------------------------------------------------

    def generate_report_draft(
        self,
        report_type: str,
        source_data: dict[str, Any],
        filters: dict[str, Any],
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        if self.settings.dify_mock_enabled:
            return self._mock_report_draft(report_type, source_data)
        return self._call_dify_report_workflow(report_type, source_data, filters, trace_id)

    def _mock_report_draft(self, report_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        if report_type == ReportType.COMPLAINT_WEEKLY:
            title = "投诉处理周报"
            summary = f"本周期共处理投诉 {source_data.get('total_tickets', 0)} 条。"
            sections = [
                {
                    "heading": "投诉概览",
                    "content": "按状态统计本周期投诉处理进展，供管理员复盘服务响应。",
                    "metrics": [{"name": key, "value": value} for key, value in source_data.get("status_counts", {}).items()],
                }
            ]
        elif report_type == ReportType.CUSTOMER_OPERATION:
            title = "客户经营分析报"
            summary = f"本周期新增线索 {source_data.get('new_leads', 0)} 条。"
            sections = [
                {
                    "heading": "客户转化概览",
                    "content": "汇总线索、客户研判和活动报名数据，辅助判断经营质量。",
                    "metrics": [
                        {"name": "new_leads", "value": source_data.get("new_leads", 0)},
                        {"name": "analysis_records", "value": source_data.get("analysis_records", 0)},
                        {"name": "event_registrations", "value": source_data.get("event_registrations", 0)},
                    ],
                }
            ]
        else:
            raise ValueError("不支持的报告类型")
        return {
            "title": title,
            "summary": summary,
            "sections": sections,
            "risks": [],
            "recommendations": ["请结合业务负责人反馈复核 AI 报告草稿。"],
            "source_refs": [source_data.get("report_type", report_type)],
        }

    def _call_dify_report_workflow(
        self,
        report_type: str,
        source_data: dict[str, Any],
        filters: dict[str, Any],
        trace_id: str | None,
    ) -> dict[str, Any]:
        if not self.settings.dify_api_key:
            raise RuntimeError("未配置 Dify API Key")
        url = f"{self.settings.dify_api_base_url.rstrip('/')}/workflows/run"
        payload = {
            "inputs": {
                "report_type": report_type,
                "source_data": source_data,
                "filters": filters,
                "trace_id": trace_id,
            },
            "response_mode": "blocking",
            "user": "education-service-backend",
        }
        headers = {"Authorization": f"Bearer {self.settings.dify_api_key}"}
        with httpx.Client(timeout=60) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        outputs = data.get("data", {}).get("outputs", {})
        draft = outputs.get("report") or outputs
        if not isinstance(draft, dict) or "title" not in draft:
            raise RuntimeError("Dify 返回内容无法解析为报告草稿")
        return draft


# ------------------------------------------------------------------
# 模块级辅助函数
# ------------------------------------------------------------------


def _parse_llm_json(text: str) -> dict[str, Any]:
    """从 LLM 返回文本中提取 JSON 对象。

    兼容以下情况：
    - 纯 JSON 字符串
    - 被 ```json ... ``` 包裹的 JSON
    - 被 ``` ... ``` 包裹的 JSON
    """
    if not text or not text.strip():
        raise RuntimeError("Dify 返回内容为空")
    text = text.strip()
    # 去掉 Markdown 代码块标记
    if text.startswith("```"):
        lines = text.split("\n")
        # 去掉首行 ```json 或 ```
        if len(lines) > 1:
            lines = lines[1:]
        # 去掉末行 ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def _mock_customer_judgement_result() -> dict[str, Any]:
    """当 Dify 处于 Mock 模式时返回示例研判结果。"""
    return {
        "executive_summary": "学员王明，22岁，南大软件工程大四，GPA 3.6，雅思6.5，意向新加坡国立大学计算机硕士。学历与语言满足产品A要求，与新加坡2+2+1本硕连读项目高度匹配。",
        "is_target_customer": True,
        "overall_match_score": 85,
        "overall_match_level": "high",
        "customer_profile": {
            "core_tags": ["本科在读", "计算机专业", "新加坡留学", "雅思达标"],
            "education_level": "本科大四在读",
            "school_name": "南京大学",
            "major": "软件工程",
            "current_grade": "大四",
            "language_level": "雅思6.5",
            "target_country": "新加坡",
            "target_program": "计算机硕士",
            "budget_range": "25-30万/年",
            "key_strengths": "985院校背景，GPA良好，英语达标，实习经历加分，意向明确",
            "potential_risks": "新加坡公立大学竞争激烈，建议同时申请私立大学保底",
        },
        "product_a_evaluation": {
            "product_name": "新加坡国际本硕升学计划",
            "conclusion": "match",
            "match_score": 85,
            "match_level": "high",
            "recommended_program": "2+2+1本硕连读或直接申请硕士",
            "dimension_analysis": [
                {
                    "dimension": "学历背景",
                    "customer_value": "南京大学（985）软件工程本科大四",
                    "rule_requirement": "认可的本科学历",
                    "is_match": True,
                    "evidence": "南京大学软件工程本科大四在读，GPA 3.6/4.0",
                },
                {
                    "dimension": "语言能力",
                    "customer_value": "雅思6.5",
                    "rule_requirement": "雅思≥6.0或通过入学测试",
                    "is_match": True,
                    "evidence": "雅思6.5分",
                },
                {
                    "dimension": "预算能力",
                    "customer_value": "25-30万/年",
                    "rule_requirement": "新加坡留学年均费用约20-30万",
                    "is_match": True,
                    "evidence": "预算25-30万/年",
                },
            ],
            "summary_reason": "学历、语言、预算均满足新加坡留学准入要求，推荐本硕连读路径",
            "missing_info": [],
            "actionable_advice": "优先推介新加坡公立大学硕士申请，同时准备私立大学作为备选方案",
        },
        "product_b_evaluation": {
            "product_name": "中德精英人才共建计划",
            "conclusion": "insufficient_info",
            "match_score": 40,
            "match_level": "low",
            "recommended_program": "暂无推荐",
            "dimension_analysis": [
                {
                    "dimension": "语言能力",
                    "customer_value": "雅思6.5，德语零基础",
                    "rule_requirement": "德语B1水平",
                    "is_match": False,
                    "evidence": "英语较好但无德语基础",
                },
                {
                    "dimension": "职业规划",
                    "customer_value": "意向读硕士深造",
                    "rule_requirement": "双元制面向就业导向",
                    "is_match": False,
                    "evidence": "意向申请硕士，非就业导向",
                },
            ],
            "summary_reason": "客户目标是硕士深造而非技能就业，且无德语基础，德国双元制不匹配",
            "missing_info": [],
            "actionable_advice": "不推荐德国方向，集中资源推进新加坡方案",
        },
        "reason_summary": "满足新加坡国际本硕升学计划的学历与语言要求，推荐本硕连读路径",
        "suggestion": "集中跟进新加坡方向，安排顾问1对1咨询公立大学申请方案",
        "final_next_steps": [
            "安排新加坡留学顾问1对1咨询",
            "发送新加坡公立大学硕士项目资料和成功案例",
            "准备成绩单和推荐信等申请材料",
        ],
    }


def _mock_service_agent_result(
    query: str,
    conversation_id: str | None,
) -> dict[str, Any]:
    return {
        "answer": f"您好！我是粤教服务留学小助手~\n\n关于「{query[:30]}...」的问题，我来为您解答：\n\n根据我们最新的留学政策，建议您先确定意向国家（新加坡或德国），然后根据学历背景选择合适的项目。\n\n如果您方便的话，可以留一下您的姓名和手机号，我让专业顾问给您做详细方案~",
        "conversation_id": conversation_id or "mock-conv-001",
        "suggested_questions": [
            "新加坡本科申请需要什么条件？",
            "德国双元制培训怎么报名？",
            "帮我推荐适合我的留学方案",
        ],
    }
