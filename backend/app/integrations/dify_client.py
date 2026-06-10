import json
from typing import Any

import httpx

from app.common.enums import ReportType
from app.core.config import Settings, get_settings


class DifyClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    # ------------------------------------------------------------------
    # 客户画像研判
    # ------------------------------------------------------------------

    def call_customer_judgement(
        self,
        customer_info_text: str,
        sys_query: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """调用 Dify 客户画像研判工作流，返回结构化研判结果。"""
        if self.settings.dify_mock_enabled:
            return _mock_customer_judgement_result()
        return self._call_dify_judgement_workflow(customer_info_text, sys_query, trace_id)

    def _call_dify_judgement_workflow(
        self,
        customer_info_text: str,
        sys_query: str | None,
        trace_id: str | None,
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
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=120) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        # 优先从 outputs 取（兼容 workflow 模式），其次从 answer 取（chat 模式）
        raw = data.get("data", {}).get("outputs", {})
        if not raw or not isinstance(raw, dict) or "executive_summary" not in raw:
            answer_text = data.get("data", {}).get("answer", "")
            raw = _parse_llm_json(answer_text)
        if not isinstance(raw, dict) or "executive_summary" not in raw:
            raise RuntimeError("Dify 返回内容无法解析为客户研判结果")
        return raw

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
        "executive_summary": "学员张三，25岁，北大计算机本科，GPA 3.5，托福100，意向美国计算机硕士。学历背景优异，语言成绩达标，与产品A高度匹配。建议优先推介美国TOP30硕士申请服务。",
        "is_target_customer": True,
        "overall_match_score": 88,
        "overall_match_level": "high",
        "customer_profile": {
            "core_tags": ["985本科", "计算机专业", "美国留学", "高GPA", "托福100+"],
            "education_level": "本科",
            "school_name": "北京大学",
            "major": "计算机科学与技术",
            "current_grade": "已毕业",
            "language_scores": "托福100",
            "target_country": "美国",
            "target_program": "计算机硕士",
            "budget_range": "30万以内",
            "key_strengths": "985院校背景，GPA优秀，语言成绩达标，专业热门，意向明确",
            "potential_risks": "美国TOP30竞争激烈，GRE成绩未知，科研/实习经历未提及",
        },
        "product_a_evaluation": {
            "product_name": "美国硕士申请服务",
            "conclusion": "match",
            "match_score": 90,
            "match_level": "high",
            "dimension_analysis": [
                {
                    "dimension": "学历背景",
                    "customer_value": "北京大学本科",
                    "rule_requirement": "985/211院校优先",
                    "is_match": True,
                    "evidence": "北京大学计算机科学与技术专业本科毕业",
                },
                {
                    "dimension": "GPA要求",
                    "customer_value": "GPA 3.5",
                    "rule_requirement": "GPA≥3.0",
                    "is_match": True,
                    "evidence": "GPA 3.5",
                },
                {
                    "dimension": "语言成绩",
                    "customer_value": "托福100分",
                    "rule_requirement": "托福≥90或雅思≥6.5",
                    "is_match": True,
                    "evidence": "托福100分",
                },
            ],
            "summary_reason": "学历、GPA、语言成绩均满足产品A的准入要求，匹配度高",
            "missing_info": [],
            "actionable_advice": "优先推介美国TOP30硕士申请全流程服务，强调同背景成功案例",
        },
        "product_b_evaluation": {
            "product_name": "学术背景提升服务",
            "conclusion": "insufficient_info",
            "match_score": 60,
            "match_level": "medium",
            "dimension_analysis": [
                {
                    "dimension": "科研经历",
                    "customer_value": "未提供",
                    "rule_requirement": "需有科研项目或论文发表经历",
                    "is_match": False,
                    "evidence": "未提供",
                },
                {
                    "dimension": "竞赛获奖",
                    "customer_value": "未提供",
                    "rule_requirement": "需有省级以上竞赛获奖",
                    "is_match": False,
                    "evidence": "未提供",
                },
            ],
            "summary_reason": "缺少科研经历和竞赛信息，无法完整评估",
            "missing_info": ["科研项目经历", "竞赛获奖情况", "实习经历"],
            "actionable_advice": "通过微信追问客户的科研经历和竞赛获奖情况",
        },
        "reason_summary": "客户学历背景优秀，满足产品A（美国硕士申请）的核心准入条件，综合匹配度88分，属于高价值目标客户",
        "suggestion": "优先跟进产品A，同时补充产品B所需的科研/竞赛信息后再做完整评估",
        "final_next_steps": [
            "安排资深顾问1对1咨询，重点介绍美国TOP30硕士申请成功案例",
            "发送产品A资料包和费用方案",
            "通过微信追问GRE成绩、科研经历、竞赛获奖情况",
        ],
    }
