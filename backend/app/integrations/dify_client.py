import json
import re
import time
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
        # 兼容多种响应结构
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

    # ------------------------------------------------------------------
    # 客服 Agent
    # ------------------------------------------------------------------

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
    # 报告生成
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

    def ask_onboarding_guide(
        self,
        question: str,
        category: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """调用新人入职指引 Dify Chat App，并返回模型回答和会话信息。"""
        if not self.settings.dify_onboarding_api_key:
            raise RuntimeError("未配置新人入职指引 Dify API Key")

        base_url = self.settings.dify_onboarding_api_base_url.rstrip("/")
        url = f"{base_url}/chat-messages" if base_url.endswith("/v1") else f"{base_url}/v1/chat-messages"
        payload = {
            "inputs": {},
            "query": question,
            "response_mode": "blocking",
            "user": "enterprise-onboarding-guide",
        }
        headers = {
            "Authorization": f"Bearer {self.settings.dify_onboarding_api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=60) as client:
            response = self._post_with_retry(client, url, payload, headers)
            response.raise_for_status()

        data = response.json()
        answer = data.get("answer")
        if not answer:
            raise RuntimeError("Dify 返回内容中缺少 answer 字段")
        return {
            "answer": self._strip_think_tags(answer),
            "conversation_id": data.get("conversation_id"),
            "message_id": data.get("message_id") or data.get("id"),
            "metadata": data.get("metadata") or {},
        }

    def _post_with_retry(
        self,
        client: httpx.Client,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:
        """Dify 或模型服务偶发 502/503/504 时重试，降低临时网关错误影响。"""
        retry_status_codes = {502, 503, 504}
        response: httpx.Response | None = None
        for attempt in range(4):
            response = client.post(url, json=payload, headers=headers)
            status_code = getattr(response, "status_code", 200)
            if status_code not in retry_status_codes:
                return response
            if attempt < 3:
                time.sleep(0.8 * (attempt + 1))
        if response is None:
            raise RuntimeError("Dify 请求未返回响应")
        return response

    def _strip_think_tags(self, answer: str) -> str:
        """清理部分推理模型返回的 <think>...</think> 内容，只把最终回答给前端。"""
        return re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()

    def _mock_report_draft(self, report_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        if report_type == ReportType.COMPLAINT_WEEKLY:
            total = source_data.get("total_tickets", 0)
            status_counts = source_data.get("status_counts", {})
            resolved = status_counts.get("resolved", 0)
            pending = status_counts.get("pending", 0)
            processing = status_counts.get("processing", 0)
            resolve_rate = f"{round(resolved / total * 100, 1) if total > 0 else 0}%"
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")
            title = f"投诉处理周报（{date_start} 至 {date_end}）"
            summary = (
                f"本周期共收到 {total} 件投诉，已解决 {resolved} 件（解决率 {resolve_rate}），"
                f"处理中 {processing} 件，待处理 {pending} 件。"
                f"整体投诉量处于可控范围，{'待处理工单需优先跟进，避免积压升级' if pending > 0 else '工单流转正常'}。"
            )
            sections = [
                {
                    "heading": "整体概况",
                    "content": (
                        f"本周期投诉工单总量为 {total} 件，覆盖待处理、处理中、已解决三种状态。"
                        f"相较前序周期如有数据变化需逐项分析原因。"
                    ),
                    "metrics": [
                        {"name": "投诉总量", "value": total},
                    ],
                },
                {
                    "heading": "工单状态与处理进展",
                    "content": (
                        f"已解决 {resolved} 件（{resolve_rate}），处理中 {processing} 件，待处理 {pending} 件。"
                        f"{'待处理占比偏高，需关注是否有工单未及时分配处理人' if pending >= total * 0.3 else '各状态分布较为均衡，处理节奏正常。'}"
                    ),
                    "metrics": [
                        {"name": "已解决", "value": resolved},
                        {"name": "处理中", "value": processing},
                        {"name": "待处理", "value": pending},
                        {"name": "解决率", "value": resolve_rate},
                    ],
                },
                {
                    "heading": "风险预警",
                    "content": (
                        f"当前待处理工单 {pending} 件，{'如超 48 小时无更新存在客户投诉升级风险，建议优先分配处理人并设定处理时限' if pending > 0 else '暂无积压风险。'}。"
                    ),
                    "metrics": [],
                },
                {
                    "heading": "改善建议",
                    "content": (
                        "建议加强工单分派机制，确保每件投诉在 24 小时内匹配处理人；"
                        "定期复盘高频投诉类别，制定专项 SOP 减少同类问题重复发生；"
                        "建立满意度回访机制，对已解决工单进行 48 小时内回访确认。"
                    ),
                    "metrics": [],
                },
            ]
            risks = [
                f"待处理工单 {pending} 件未闭环，存在客户满意度下降和服务升级风险"
                if pending > 0
                else "本周工单全部闭环，暂无服务风险"
            ]
            recommendations = [
                "建议优先处理待处理工单，确保 48 小时内首次响应",
                "对高频投诉类别进行专项分析，制定预防性 SOP",
                "建立工单处理时效看板，透明化团队服务效率",
            ]
            source_refs = [
                f"数据来源：student_feedback_ticket 投诉工单表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.CUSTOMER_OPERATION:
            new_leads = source_data.get("new_leads", 0)
            analysis_records = source_data.get("analysis_records", 0)
            event_regs = source_data.get("event_registrations", 0)
            lead_source = source_data.get("lead_source_breakdown", {})
            lead_status = source_data.get("lead_status_breakdown", {})
            analysis_result = source_data.get("analysis_result_breakdown", {})
            event_reg = source_data.get("event_registration_breakdown", {})
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")
            prev = source_data.get("prev_period", {})
            lead_trend = source_data.get("lead_trend", {})
            churn_source = source_data.get("churn_source_breakdown", {})
            top_churn_source = max(churn_source, key=churn_source.get) if churn_source else "未归类"
            prev_leads = prev.get("leads", 0)
            delta_pct = lead_trend.get("delta_pct", 0)
            trend_label = lead_trend.get("label", "持平")
            prev_analysis = prev.get("analysis", 0)
            prev_events = prev.get("events", 0)

            source_text = "、".join(f"{k}({v}条)" for k, v in lead_source.items()) if lead_source else "暂无渠道数据"
            status_text = "、".join(f"{k}({v}条)" for k, v in lead_status.items()) if lead_status else "暂无阶段数据"
            result_text = "、".join(f"{k}({v}条)" for k, v in analysis_result.items()) if analysis_result else "暂无研判等级数据"
            title = f"全域客户经营分析报告（{date_start} 至 {date_end}）"

            lead_to_analysis = round(analysis_records / new_leads * 100, 1) if new_leads > 0 else 0
            signed_count = lead_status.get("已成交", lead_status.get("已签约", 0))
            lost_count = lead_status.get("已流失", lead_status.get("废弃", lead_status.get("已关单", 0)))
            high_intent = analysis_result.get("高意向", analysis_result.get("high", 0))
            active_event_regs = event_reg.get("已报名", event_reg.get("registered", 0))
            converted_event_regs = event_reg.get("已转化", event_reg.get("converted", event_reg.get("已参加", 0)))

            summary = (
                f"本周期新增线索 {new_leads} 条，完成客户研判 {analysis_records} 条，"
                f"活动报名 {event_regs} 人次。线索研判覆盖率 {lead_to_analysis}%，"
                f"{'成交 ' + str(signed_count) + ' 单' if signed_count > 0 else '暂无已成交客户'}。"
                f"{'存在 ' + str(lost_count) + ' 条流失线索需关注归因' if lost_count > 0 else ''}"
            )

            sections = [
                {
                    "heading": "意向客户 - 线索获取与渠道分布",
                    "content": (
                        f"本周期新增客户线索 {new_leads} 条。线索来源渠道分布：{source_text}。"
                        f"线索当前所处阶段：{status_text}。"
                        "建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。"
                    ),
                    "metrics": [
                        {"name": "新增线索", "value": new_leads},
                        *[{"name": f"渠道-{k}", "value": v} for k, v in lead_source.items()],
                    ],
                },
                {
                    "heading": "意向客户 - 研判转化漏斗",
                    "content": (
                        f"完成客户研判 {analysis_records} 条，研判覆盖率 {lead_to_analysis}%。"
                        f"研判等级分布：{result_text}。"
                        f"高意向客户 {high_intent} 条，是近期转化重点跟进对象。"
                        f"{'研判覆盖率偏低，部分线索尚未进入研判阶段，存在流失风险' if lead_to_analysis < 50 else '研判覆盖率正常。'} "
                        f"从\"线索\"到\"研判\"的转化漏斗目前为 {new_leads} → {analysis_records}。"
                    ),
                    "metrics": [
                        {"name": "研判数", "value": analysis_records},
                        {"name": "研判覆盖率", "value": f"{lead_to_analysis}%"},
                        *[{"name": f"研判-{k}", "value": v} for k, v in analysis_result.items()],
                        {"name": "上周研判数", "value": prev_analysis},
                    ],
                },
                {
                    "heading": "成交客户 - 转化路径与高价值特征",
                    "content": (
                        f"本周期成交客户 {signed_count} 单"
                        f"{'，线索到成交转化率 ' + f'{round(signed_count / new_leads * 100, 1)}%' if new_leads > 0 else ''}。"
                        f"从研判分布来看，{result_text}，"
                        f"高意向客户是成交主力来源。"
                        f"{'研判等级为高意向的客户应纳入优先跟进序列，加速转化' if high_intent > 0 else ''}。"
                        f"{'暂无成交客户，建议复盘从研判到签约环节的转化障碍' if signed_count == 0 else ''}"
                    ),
                    "metrics": [
                        {"name": "成交客户数", "value": signed_count},
                        {"name": "线索→成交转化率", "value": f"{round(signed_count / new_leads * 100, 1)}%" if new_leads > 0 else "N/A"},
                    ],
                },
                {
                    "heading": "活动参与与转化跟踪",
                    "content": (
                        f"活动报名总计 {event_regs} 人次，"
                        f"其中已报名 {active_event_regs} 人次、已转化 {converted_event_regs} 人次。"
                        "活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，"
                        f"{'将活动报名 → 研判 → 签约的转化链打通' if converted_event_regs < active_event_regs else '活动转化效果良好'}。"
                    ),
                    "metrics": [
                        {"name": "活动报名总人次", "value": event_regs},
                        *[{"name": f"活动-{k}", "value": v} for k, v in event_reg.items()],
                    ],
                },
                {
                    "heading": "流失客户 - 归因分析与预警",
                    "content": (
                        f"本周期流失线索 {lost_count} 条，占线索总量的 "
                        f"{f'{round(lost_count / (new_leads + lost_count) * 100, 1)}%' if (new_leads + lost_count) > 0 else 'N/A'}。"
                        f"当前处于\"废弃/已关单\"状态的线索 {lost_count} 条，"
                        f"{'建议逐条复盘流失原因（如价格、竞品、需求不匹配），沉淀流失特征模型' if lost_count > 0 else '暂无流失线索，客户留存状况良好。'}"
                    ),
                    "metrics": [
                        {"name": "流失线索数", "value": lost_count},
                        {"name": "流失占比", "value": f"{round(lost_count / (new_leads + lost_count) * 100, 1)}%" if (new_leads + lost_count) > 0 else "0%"},
                    ],
                },
                {
                    "heading": "客群特征与画像提炼",
                    "content": (
                        f"基于本周期数据，线索来源以 {max(lead_source, key=lead_source.get) if lead_source else '未归类'} 为主"
                        f"（占比 {f'{round(max(lead_source.values()) / sum(lead_source.values()) * 100, 1)}%' if lead_source else 'N/A'}）。"
                        f"研判后高意向客群占比 {f'{round(high_intent / analysis_records * 100, 1)}%' if analysis_records > 0 else 'N/A'}。"
                        "当前客群画像：以活动引流和转介绍为主要获客方式，高意向客户特征集中在研判结果为\"高意向\"的群体。"
                        "建议后续补充客户行业、规模、预算等维度数据，进一步提升画像精准度。"
                    ),
                    "metrics": [],
                },
                {
                    "heading": "全链路经营建议",
                    "content": (
                        "建议建立线索分级机制，优先跟进高意向线索；"
                        "定期复盘研判转化漏斗，定位各环节流失原因；"
                        "将活动报名客户纳入专项跟进序列，提升活动线索转化率；"
                        "建立流失预警模型，对长期无互动线索自动标记并推送挽回策略；"
                        "按月/周输出客户经营健康度看板，支撑全链路决策闭环。"
                    ),
                    "metrics": [],
                },
            ]
            risks = []
            if new_leads > 0 and analysis_records < new_leads * 0.5:
                risks.append(f"线索研判覆盖率仅 {lead_to_analysis}%，半数以上线索未进入研判，存在大量线索沉默流失风险")
            if lost_count > 0:
                risks.append(f"已流失 {lost_count} 条线索（主要来自 {top_churn_source} 渠道），建议重点复盘该渠道线索质量和跟进流程")
            if delta_pct < -20 and new_leads > 0:
                risks.append(f"线索量较上周下降 {abs(delta_pct)}%，获客能力出现明显下滑，建议排查渠道投放和营销活动效果")
            if signed_count == 0 and new_leads > 0:
                risks.append("本周期零成交，线索到签约的转化链路存在阻断，需紧急排查瓶颈环节")
            if not risks:
                risks = ["暂无重大经营风险，建议保持当前跟进节奏"]
            recommendations = [
                "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
                "对活动报名客户建立 48 小时回访机制，推动转化",
                "建立线索分级标准，按意向度匹配跟进强度",
                "每周复盘流失线索共性特征，沉淀流失预防 SOP",
                "将高意向客户纳入重点跟进看板，确保闭环管理",
            ]
            source_refs = [
                f"数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.EMPLOYEE_DAILY_SUMMARY:
            total = source_data.get("total_reports", 0)
            submitted = source_data.get("submitted_reports", 0)
            draft = source_data.get("draft_reports", 0)
            archived = source_data.get("archived_reports", 0)
            risk_reports = source_data.get("risk_reports", 0)
            tomorrow_plan = source_data.get("tomorrow_plan_reports", 0)
            date_start = source_data.get("date_start", "")
            title = f"员工日报汇总报告（{date_start}）"
            summary = (
                f"本日共汇总日报 {total} 份，已提交 {submitted} 份（提交率 {f'{round(submitted / total * 100, 1)}%' if total > 0 else 'N/A'}），"
                f"草稿 {draft} 份，归档 {archived} 份。"
                f"{'存在风险摘要的日报占比偏高，需重点关注' if total > 0 and risk_reports / total > 0.3 else '整体工作执行平稳。'}"
            )
            sections = [
                {
                    "heading": "日报提交概览",
                    "content": (
                        f"本日日报提交率 {f'{round(submitted / total * 100, 1)}%' if total > 0 else 'N/A'}，"
                        f"其中已提交 {submitted} 份、草稿 {draft} 份、已归档 {archived} 份。"
                        f"{'存在未提交或草稿状态的日报，建议了解原因并推动补交' if total - submitted > 0 else '全员已提交。'}"
                    ),
                    "metrics": [
                        {"name": "总日报数", "value": total},
                        {"name": "已提交", "value": submitted},
                        {"name": "草稿", "value": draft},
                        {"name": "已归档", "value": archived},
                    ],
                },
                {
                    "heading": "工作进展与潜在风险",
                    "content": (
                        f"含风险摘要的日报 {risk_reports} 份，填报明日计划 {tomorrow_plan} 份。"
                        f"{'风险摘要集中出现，建议汇总分析风险类型并制定应对方案' if risk_reports > 0 else '暂无风险上报。'}"
                        f"{'明日计划填报率偏低，团队工作计划清晰度有待提升' if total > 0 and tomorrow_plan < total * 0.5 else ''}"
                    ),
                    "metrics": [
                        {"name": "风险摘要日报", "value": risk_reports},
                        {"name": "明日计划日报", "value": tomorrow_plan},
                    ],
                },
                {
                    "heading": "管理建议",
                    "content": (
                        "推动未提交和草稿状态日报在当日完成补交；"
                        "对风险摘要日报进行专题复盘，提炼共性问题；"
                        "强化明日计划填报要求，提升团队工作的可预见性。"
                    ),
                    "metrics": [],
                },
            ]
            risks = [
                f"日报提交率 {f'{round(submitted / total * 100, 1)}%' if total > 0 else 'N/A'}，"
                f"{total - submitted} 份未提交，工作透明度存在风险" if total > submitted else "全员已提交，暂无执行风险"
            ]
            recommendations = [
                "建立日报提交截止时间提醒，确保当日日清日结",
                "对风险摘要日报进行集中分析，制定应对方案",
                "将明日计划填报纳入日报考核标准",
            ]
            source_refs = [
                f"数据来源：employee_daily_report 员工日报表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.EMPLOYEE_WEEKLY_SUMMARY:
            total = source_data.get("total_reports", 0)
            distinct = source_data.get("distinct_employees", 0)
            risk_reports = source_data.get("risk_reports", 0)
            daily_trend = source_data.get("daily_trend", {})
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")
            title = f"员工日报汇总报告（{date_start} 至 {date_end}）"
            summary = (
                f"本周共汇总日报 {total} 份，涉及 {distinct} 名员工。"
                f"{'日报覆盖率偏低，需关注未提交员工' if distinct > 0 and total / distinct < 5 else '平均每人提交 ' + str(round(total / distinct, 1)) if distinct > 0 else ''}份。"
                f"{'含风险摘要日报占比偏高' if total > 0 and risk_reports / total > 0.3 else '整体工作执行正常。'}"
            )
            sections = [
                {
                    "heading": "周度提交趋势",
                    "content": (
                        f"本周共 {distinct} 人提交日报，总量 {total} 份。"
                        "逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。"
                    ),
                    "metrics": [
                        {"name": "总日报数", "value": total},
                        {"name": "提交员工数", "value": distinct},
                    ],
                },
                {
                    "heading": "每日提交趋势",
                    "content": "逐日提交量变化如下。' + ('工作日提交量高于周末，符合正常规律。' if len(daily_trend) >= 3 else '数据周期较短，建议积累更多数据做趋势分析。')",
                    "metrics": [
                        {"name": day, "value": count}
                        for day, count in daily_trend.items()
                    ],
                },
                {
                    "heading": "工作质量与风险观察",
                    "content": (
                        f"含风险摘要日报 {risk_reports} 份（占比 {f'{round(risk_reports / total * 100, 1)}%' if total > 0 else 'N/A'}）。"
                        f"{'风险摘要占比较高，建议汇总分析风险类型分布' if total > 0 and risk_reports / total > 0.3 else '风险披露比例适中。'}"
                    ),
                    "metrics": [
                        {"name": "风险摘要日报", "value": risk_reports},
                        {"name": "风险摘要占比", "value": f"{round(risk_reports / total * 100, 1)}%" if total > 0 else "N/A"},
                    ],
                },
                {
                    "heading": "管理建议",
                    "content": (
                        "针对提交量波动的日期了解原因，评估是否需要工作安排优化；"
                        "定期汇总风险摘要日报，提炼共性问题和改进方向；"
                        "推动部门内日报标准化，提升工作可量化程度。"
                    ),
                    "metrics": [],
                },
            ]
            risks = [
                f"日报覆盖率偏低（{distinct} 人提交），部分员工工作情况不可见" if distinct > 0 and total < distinct * 3 else "暂无重大管理风险"
            ]
            recommendations = [
                "推动全员日报提交，确保工作进展透明化",
                "汇总本周风险摘要，形成团队风险清单",
                "建立日报质量评分机制，提升填报内容质量",
            ]
            source_refs = [
                f"数据来源：employee_daily_report 员工日报表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.STUDENT_PSYCH_WEEKLY:
            total_profiles = source_data.get("total_profiles", 0)
            total_alerts = source_data.get("total_alerts", 0)
            risk_level_counts = source_data.get("risk_level_counts", {})
            emotion_tag_counts = source_data.get("emotion_tag_counts", {})
            alert_status_counts = source_data.get("alert_status_counts", {})
            avg_score = source_data.get("average_emotion_score", 0)
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")
            title = f"学生心理健康周报（{date_start} 至 {date_end}）"
            summary = (
                f"本周纳入心理画像 {total_profiles} 份，平均情绪分 {avg_score}，"
                f"触发预警 {total_alerts} 条。"
                f"{'整体心理健康处于关注区间，需介入高风险个案' if avg_score < 70 or risk_level_counts.get('high', 0) > 0 else '整体心理状态平稳。'}"
            )
            sections = [
                {
                    "heading": "整体心理态势",
                    "content": (
                        f"本周共 {total_profiles} 名学生完成心理画像评估，整体平均情绪分 {avg_score}。"
                        f"{'平均情绪分偏低，需关注学生群体的整体心理健康趋势' if avg_score < 70 else '情绪分处于正常区间，群体心理状态平稳。'}"
                        f"建议结合留学周期（当前处于学期中段，课业压力可能上升）进行综合研判。"
                    ),
                    "metrics": [
                        {"name": "心理画像数", "value": total_profiles},
                        {"name": "平均情绪分", "value": f"{avg_score} (满分 100)"},
                    ],
                },
                {
                    "heading": "风险分层分析",
                    "content": (
                        f"高风险管理：{risk_level_counts.get('high', 0)} 人，中等风险：{risk_level_counts.get('medium', 0)} 人，"
                        f"低风险：{risk_level_counts.get('low', 0)} 人。"
                        f"{'存在高风险学生，建议立即启动深度访谈和心理干预方案' if risk_level_counts.get('high', 0) > 0 else '无高风险学生，继续保持常规关注。'}"
                    ),
                    "metrics": [
                        {"name": "高风险", "value": risk_level_counts.get("high", 0)},
                        {"name": "中风险", "value": risk_level_counts.get("medium", 0)},
                        {"name": "低风险", "value": risk_level_counts.get("low", 0)},
                    ],
                },
                {
                    "heading": "情绪标签与趋势",
                    "content": (
                        f"本周主要情绪标签分布：" +
                        "、".join(f"{tag}({cnt})" for tag, cnt in emotion_tag_counts.items()) +
                        ("。" if emotion_tag_counts else "暂无情绪标签数据。") +
                        f"{'焦虑标签占比突出，可能与近期考试或学业压力相关' if emotion_tag_counts.get('焦虑', 0) > 0 else ''}"
                    ),
                    "metrics": [
                        {"name": tag, "value": cnt}
                        for tag, cnt in emotion_tag_counts.items()
                    ],
                },
                {
                    "heading": "预警处理与关怀建议",
                    "content": (
                        f"预警总量 {total_alerts} 条，已处理 {alert_status_counts.get('resolved', 0)} 条，"
                        f"待处理 {alert_status_counts.get('pending', 0)} 条。"
                        f"{'存在未处理预警，需立即跟进高风险学生' if alert_status_counts.get('pending', 0) > 0 else '预警全部闭环处理。'}"
                        "建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。"
                    ),
                    "metrics": [
                        {"name": "预警总量", "value": total_alerts},
                        {"name": "已处理", "value": alert_status_counts.get("resolved", 0)},
                        {"name": "待处理", "value": alert_status_counts.get("pending", 0)},
                    ],
                },
            ]
            risks = [
                f"存在 {risk_level_counts.get('high', 0)} 名高风险学生需紧急干预" if risk_level_counts.get('high', 0) > 0 else "暂无高危预警",
                f"整体平均情绪分 {avg_score}，低于健康阈值" if avg_score < 70 else "",
                f"尚有 {alert_status_counts.get('pending', 0)} 条预警待处理" if alert_status_counts.get('pending', 0) > 0 else "",
            ]
            risks = [r for r in risks if r]
            recommendations = [
                "对高风险学生启动 48 小时内深度访谈",
                "组织本学期中段心理健康主题分享活动",
                "建立心理健康预警回访机制，确保干预闭环",
                "针对焦虑标签突出的学生，协调学业支持资源",
            ]
            source_refs = [
                f"数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
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
                "source_data": json.dumps(source_data, ensure_ascii=False),
                "filters": json.dumps(filters, ensure_ascii=False),
                "trace_id": trace_id,
            },
            "response_mode": "blocking",
            "user": "education-service-backend",
        }
        headers = {"Authorization": f"Bearer {self.settings.dify_api_key}"}
        with httpx.Client(timeout=60) as client:
            response = self._post_with_retry(client, url, payload, headers)
            response.raise_for_status()
        data = response.json()
        outputs = data.get("data", {}).get("outputs", {})
        draft = self._extract_report_output(outputs)
        return self._normalize_report_draft(draft)

    def _extract_report_output(self, outputs: Any) -> dict[str, Any]:
        if isinstance(outputs, dict):
            for key in ("report", "text", "result"):
                value = outputs.get(key)
                if value:
                    return self._coerce_report_dict(value)
            return self._coerce_report_dict(outputs)
        return self._coerce_report_dict(outputs)

    def _coerce_report_dict(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            for candidate in self._candidate_json_strings(value):
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict):
                    return parsed
        raise RuntimeError("Dify 返回内容无法解析为报告草稿")

    def _candidate_json_strings(self, text: str) -> list[str]:
        stripped = text.strip()
        without_think = re.sub(r"<think>.*?</think>", "", stripped, flags=re.IGNORECASE | re.DOTALL).strip()
        candidates = [stripped, without_think]

        fence_match = re.search(r"```(?:json)?\s*(.*?)```", without_think, flags=re.IGNORECASE | re.DOTALL)
        if fence_match:
            candidates.append(fence_match.group(1).strip())

        embedded_json = self._extract_first_json_object(without_think)
        if embedded_json:
            candidates.append(embedded_json)

        unique_candidates = []
        for candidate in candidates:
            if candidate and candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates

    def _extract_first_json_object(self, text: str) -> str | None:
        start = text.find("{")
        if start < 0:
            return None

        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        return None

    def _normalize_report_draft(self, draft: dict[str, Any]) -> dict[str, Any]:
        self._raise_for_failed_tool_call(draft)
        self._raise_for_failure_content(draft)
        title = draft.get("title")
        if not isinstance(title, str) or not title.strip():
            raise RuntimeError("Dify 返回内容无法解析为报告草稿")
        sections = draft.get("sections", [])
        if not isinstance(sections, list):
            sections = []
        normalized_sections = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            metrics = section.get("metrics", [])
            normalized_sections.append(
                {
                    "heading": str(section.get("heading", "")),
                    "content": str(section.get("content", "")),
                    "metrics": metrics if isinstance(metrics, list) else [],
                }
            )
        return {
            **draft,
            "title": title.strip(),
            "summary": str(draft.get("summary", "")),
            "sections": normalized_sections,
            "risks": draft.get("risks") if isinstance(draft.get("risks"), list) else [],
            "recommendations": draft.get("recommendations")
            if isinstance(draft.get("recommendations"), list)
            else [],
            "source_refs": draft.get("source_refs") if isinstance(draft.get("source_refs"), list) else [],
        }

    def _raise_for_failed_tool_call(self, draft: dict[str, Any]) -> None:
        tool_call_success = draft.get("tool_call_success")
        tool_status_code = self._coerce_status_code(draft.get("tool_status_code"))

        success_is_false = tool_call_success is False or (
            isinstance(tool_call_success, str) and tool_call_success.strip().lower() in {"false", "0", "no"}
        )
        status_is_failed = tool_status_code is not None and tool_status_code != 200
        if success_is_false or status_is_failed:
            error = draft.get("tool_error") or draft.get("summary") or "Dify AI Tool 返回失败状态"
            raise RuntimeError(f"Dify AI Tool 调用失败：{error}")

    def _raise_for_failure_content(self, draft: dict[str, Any]) -> None:
        content = json.dumps(draft, ensure_ascii=False)
        failure_markers = (
            "HTTP 422",
            "HTTP 401",
            "HTTP 403",
            "FastAPI AI Tool返回",
            "FastAPI AI Tool 返回",
            "参数校验错误",
            "请求被拒绝",
            "query_report_source_data未成功执行",
            "query_report_source_data 未成功执行",
            "无可用数据表",
        )
        if any(marker in content for marker in failure_markers):
            raise RuntimeError("Dify AI Tool 调用失败：模型输出包含工具失败或参数校验错误内容")

    def _coerce_status_code(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


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
        if len(lines) > 1:
            lines = lines[1:]
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
