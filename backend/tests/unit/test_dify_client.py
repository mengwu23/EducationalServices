import json

import pytest

from backend.app.common.enums import ReportType
from backend.app.core.config import Settings
from backend.app.integrations.dify_client import DifyClient


class FakeDifyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, payload):
        self.payload = payload
        self.requests = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, json=None, headers=None):
        self.requests.append({"url": url, "json": json, "headers": headers})
        return FakeDifyResponse(self.payload)


def build_client(monkeypatch, payload):
    fake_client = FakeHttpClient(payload)
    monkeypatch.setattr("app.integrations.dify_client.httpx.Client", lambda timeout: fake_client)
    settings = Settings(
        dify_mock_enabled=False,
        dify_api_key="test-key",
        dify_api_base_url="http://dify.local",
    )
    return DifyClient(settings), fake_client


def test_real_dify_parses_report_object(monkeypatch):
    payload = {
        "data": {
            "outputs": {
                "report": {
                    "title": "真实Dify报告",
                    "summary": "摘要",
                    "sections": [{"heading": "概览", "content": "正文", "metrics": []}],
                }
            }
        }
    }
    client, fake_http = build_client(monkeypatch, payload)

    draft = client.generate_report_draft(
        ReportType.COMPLAINT_WEEKLY,
        {"total_tickets": 1},
        {"date_start": "2026-06-01"},
        "trace-1",
    )

    assert draft["title"] == "真实Dify报告"
    assert draft["risks"] == []
    assert draft["recommendations"] == []
    assert draft["source_refs"] == []
    assert fake_http.requests[0]["headers"]["Authorization"] == "Bearer test-key"
    inputs = fake_http.requests[0]["json"]["inputs"]
    assert inputs["source_data"] == json.dumps({"total_tickets": 1}, ensure_ascii=False)
    assert inputs["filters"] == json.dumps({"date_start": "2026-06-01"}, ensure_ascii=False)


def test_real_dify_parses_report_json_string(monkeypatch):
    report = {
        "title": "JSON字符串报告",
        "summary": "摘要",
        "sections": [{"heading": "趋势", "content": "正文", "metrics": []}],
    }
    payload = {"data": {"outputs": {"report": json.dumps(report, ensure_ascii=False)}}}
    client, _ = build_client(monkeypatch, payload)

    draft = client.generate_report_draft(ReportType.CUSTOMER_OPERATION, {}, {}, "trace-2")

    assert draft["title"] == "JSON字符串报告"
    assert draft["sections"][0]["heading"] == "趋势"


def test_real_dify_parses_text_json_string(monkeypatch):
    report = {
        "title": "Text字段报告",
        "summary": "摘要",
        "sections": [{"heading": "概览", "content": "正文", "metrics": []}],
    }
    payload = {"data": {"outputs": {"text": json.dumps(report, ensure_ascii=False)}}}
    client, _ = build_client(monkeypatch, payload)

    draft = client.generate_report_draft(ReportType.EMPLOYEE_WEEKLY_SUMMARY, {}, {}, "trace-3")

    assert draft["title"] == "Text字段报告"


def test_real_dify_parses_think_prefixed_json(monkeypatch):
    report = {
        "title": "思考模式报告",
        "summary": "摘要",
        "sections": [{"heading": "概览", "content": "正文", "metrics": []}],
    }
    payload = {"data": {"outputs": {"report": f"<think>内部推理内容</think>{json.dumps(report, ensure_ascii=False)}"}}}
    client, _ = build_client(monkeypatch, payload)

    draft = client.generate_report_draft(ReportType.COMPLAINT_WEEKLY, {}, {}, "trace-think")

    assert draft["title"] == "思考模式报告"


def test_real_dify_parses_markdown_fenced_json(monkeypatch):
    report = {
        "title": "代码块报告",
        "summary": "摘要",
        "sections": [{"heading": "概览", "content": "正文", "metrics": []}],
    }
    payload = {"data": {"outputs": {"report": f"```json\n{json.dumps(report, ensure_ascii=False)}\n```"}}}
    client, _ = build_client(monkeypatch, payload)

    draft = client.generate_report_draft(ReportType.CUSTOMER_OPERATION, {}, {}, "trace-fence")

    assert draft["title"] == "代码块报告"


def test_real_dify_extracts_embedded_json_object(monkeypatch):
    report = {
        "title": "嵌入JSON报告",
        "summary": "摘要",
        "sections": [{"heading": "概览", "content": "正文", "metrics": []}],
    }
    payload = {"data": {"outputs": {"report": f"前缀说明 {json.dumps(report, ensure_ascii=False)} 后缀说明"}}}
    client, _ = build_client(monkeypatch, payload)

    draft = client.generate_report_draft(ReportType.EMPLOYEE_DAILY_SUMMARY, {}, {}, "trace-embedded")

    assert draft["title"] == "嵌入JSON报告"


def test_real_dify_rejects_failed_tool_call(monkeypatch):
    report = {
        "tool_call_success": False,
        "tool_status_code": 422,
        "tool_error": "owner_user_id 不能是空字符串",
        "title": "错误报告",
        "summary": "摘要",
        "sections": [{"heading": "概览", "content": "正文", "metrics": []}],
    }
    payload = {"data": {"outputs": {"report": json.dumps(report, ensure_ascii=False)}}}
    client, _ = build_client(monkeypatch, payload)

    with pytest.raises(RuntimeError, match="Dify AI Tool 调用失败"):
        client.generate_report_draft(ReportType.COMPLAINT_WEEKLY, {}, {}, "trace-tool-fail")


def test_real_dify_rejects_non_200_tool_status(monkeypatch):
    report = {
        "tool_call_success": True,
        "tool_status_code": "401",
        "tool_error": "AI Tools 调用密钥无效",
        "title": "错误报告",
        "summary": "摘要",
        "sections": [{"heading": "概览", "content": "正文", "metrics": []}],
    }
    payload = {"data": {"outputs": {"report": json.dumps(report, ensure_ascii=False)}}}
    client, _ = build_client(monkeypatch, payload)

    with pytest.raises(RuntimeError, match="Dify AI Tool 调用失败"):
        client.generate_report_draft(ReportType.COMPLAINT_WEEKLY, {}, {}, "trace-tool-status")


def test_real_dify_rejects_failure_content_without_status_flag(monkeypatch):
    report = {
        "tool_call_success": True,
        "tool_status_code": 200,
        "tool_error": "",
        "title": "错误报告",
        "summary": "调用 FastAPI AI Tool 时发生参数校验错误。",
        "sections": [
            {
                "heading": "数据获取状态",
                "content": "owner_user_id 字段传入空字符串，导致请求被拒绝（HTTP 422）。",
                "metrics": [],
            }
        ],
        "risks": [],
        "recommendations": [],
        "source_refs": ["FastAPI AI Tool返回的HTTP 422错误信息"],
    }
    payload = {"data": {"outputs": {"report": json.dumps(report, ensure_ascii=False)}}}
    client, _ = build_client(monkeypatch, payload)

    with pytest.raises(RuntimeError, match="模型输出包含工具失败"):
        client.generate_report_draft(ReportType.STUDENT_PSYCH_WEEKLY, {}, {}, "trace-failure-content")


def test_real_dify_invalid_json_raises_clear_error(monkeypatch):
    payload = {"data": {"outputs": {"report": "{not-json"}}}
    client, _ = build_client(monkeypatch, payload)

    with pytest.raises(RuntimeError, match="Dify 返回内容无法解析"):
        client.generate_report_draft(ReportType.COMPLAINT_WEEKLY, {}, {}, "trace-4")


def test_real_dify_missing_title_raises_clear_error(monkeypatch):
    payload = {"data": {"outputs": {"report": {"summary": "缺少标题"}}}}
    client, _ = build_client(monkeypatch, payload)

    with pytest.raises(RuntimeError, match="Dify 返回内容无法解析"):
        client.generate_report_draft(ReportType.COMPLAINT_WEEKLY, {}, {}, "trace-5")


def test_real_dify_without_api_key_raises_clear_error():
    client = DifyClient(Settings(dify_mock_enabled=False, dify_api_key=""))

    with pytest.raises(RuntimeError, match="未配置 Dify API Key"):
        client.generate_report_draft(ReportType.COMPLAINT_WEEKLY, {}, {}, "trace-6")
