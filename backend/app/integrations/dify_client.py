import re
import time
from typing import Any

import httpx

from backend.app.common.enums import ReportType
from backend.app.core.config import Settings, get_settings

COMPLAINT_WEEKLY_REPORT = "complaint_weekly"
CUSTOMER_OPERATION_REPORT = "customer_operation"


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
            # 标准 Dify Chat App 请求体：用户问题只通过 query 传入。
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

    def _post_with_retry(self, client: httpx.Client, url: str, payload: dict[str, Any], headers: dict[str, str]) -> httpx.Response:
        """Dify 或模型服务偶发 502/503/504 时多次重试，降低临时网关错误对前端的影响。"""
        retry_status_codes = {502, 503, 504}
        response: httpx.Response | None = None
        for attempt in range(4):
            response = client.post(url, json=payload, headers=headers)
            if response.status_code not in retry_status_codes:
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
        if report_type == COMPLAINT_WEEKLY_REPORT:
            title = "投诉处理周报"
            summary = f"本周期共处理投诉 {source_data.get('total_tickets', 0)} 条。"
            sections = [
                {
                    "heading": "投诉概览",
                    "content": "按状态统计本周期投诉处理进展，供管理员复盘服务响应。",
                    "metrics": [{"name": key, "value": value} for key, value in source_data.get("status_counts", {}).items()],
                }
            ]
        elif report_type == CUSTOMER_OPERATION_REPORT:
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
        url = f"{self.settings.dify_api_base_url.rstrip('/')}/v1/workflows/run"
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
