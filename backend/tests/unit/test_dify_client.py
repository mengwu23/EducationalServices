import json

import pytest

from app.common.enums import ReportType
from app.core.config import Settings
from app.integrations.dify_client import DifyClient


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
