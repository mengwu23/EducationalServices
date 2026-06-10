import json
import json
from typing import Any

import httpx

from app.common.enums import ReportType
from app.core.config import Settings, get_settings


class DifyClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

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
        elif report_type == ReportType.EMPLOYEE_DAILY_SUMMARY:
            title = "员工日报汇总报告（日）"
            summary = f"本日共汇总日报 {source_data.get('total_reports', 0)} 份。"
            sections = [
                {
                    "heading": "日报提交概览",
                    "content": "按单日统计员工日报提交、草稿、归档和风险摘要情况。",
                    "metrics": [
                        {"name": "total_reports", "value": source_data.get("total_reports", 0)},
                        {"name": "submitted_reports", "value": source_data.get("submitted_reports", 0)},
                        {"name": "draft_reports", "value": source_data.get("draft_reports", 0)},
                        {"name": "archived_reports", "value": source_data.get("archived_reports", 0)},
                        {"name": "risk_reports", "value": source_data.get("risk_reports", 0)},
                        {"name": "tomorrow_plan_reports", "value": source_data.get("tomorrow_plan_reports", 0)},
                    ],
                }
            ]
        elif report_type == ReportType.EMPLOYEE_WEEKLY_SUMMARY:
            title = "员工日报汇总报告（周）"
            summary = f"本周共汇总日报 {source_data.get('total_reports', 0)} 份。"
            sections = [
                {
                    "heading": "周度日报趋势",
                    "content": "按周统计日报总量、提交员工数、每日趋势和风险摘要数量。",
                    "metrics": [
                        {"name": "total_reports", "value": source_data.get("total_reports", 0)},
                        {"name": "distinct_employees", "value": source_data.get("distinct_employees", 0)},
                        {"name": "risk_reports", "value": source_data.get("risk_reports", 0)},
                    ],
                },
                {
                    "heading": "每日提交趋势",
                    "content": "展示本周期内各日期日报提交数量。",
                    "metrics": [
                        {"name": day, "value": count} for day, count in source_data.get("daily_trend", {}).items()
                    ],
                },
            ]
        elif report_type == ReportType.STUDENT_PSYCH_WEEKLY:
            title = "学生心理健康周报"
            summary = f"本周纳入心理画像 {source_data.get('total_profiles', 0)} 份，预警 {source_data.get('total_alerts', 0)} 条。"
            sections = [
                {
                    "heading": "心理风险概览",
                    "content": "按风险等级、情绪标签和平均情绪分观察学生心理健康趋势。",
                    "metrics": [
                        {"name": key, "value": value}
                        for key, value in source_data.get("risk_level_counts", {}).items()
                    ]
                    + [
                        {"name": "average_emotion_score", "value": source_data.get("average_emotion_score")},
                        {"name": "total_alerts", "value": source_data.get("total_alerts", 0)},
                    ],
                },
                {
                    "heading": "预警处理概览",
                    "content": "按预警状态和预警风险等级统计本周期心理健康跟进情况。",
                    "metrics": [
                        {"name": key, "value": value}
                        for key, value in source_data.get("alert_status_counts", {}).items()
                    ],
                },
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
        url = f"{self.settings.dify_api_base_url.rstrip('/')}/v1/workflows/run"
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
            response = client.post(url, json=payload, headers=headers)
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
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Dify 返回内容无法解析为报告草稿") from exc
            if isinstance(parsed, dict):
                return parsed
        raise RuntimeError("Dify 返回内容无法解析为报告草稿")

    def _normalize_report_draft(self, draft: dict[str, Any]) -> dict[str, Any]:
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
