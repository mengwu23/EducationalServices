import json

import pytest

from backend.app.common.exceptions import AppException
from backend.app.services import student_assistant_service
from backend.app.services.student_assistant_service import StudentAssistantService


class FakeSettings:
    dify_mock_enabled = False
    dify_api_url = "http://dify.local/v1/chat-messages"


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_student_assistant_dify_mock_returns_local_reply(monkeypatch):
    settings = FakeSettings()
    settings.dify_mock_enabled = True
    monkeypatch.setattr(student_assistant_service, "settings", settings)

    result = StudentAssistantService._call_dify("", "宿舍网络不稳定怎么办")

    assert "宿舍网络不稳定怎么办" in result["answer"]
    assert result["conversation_id"] == "mock-student-assistant-conversation"


def test_student_assistant_dify_missing_key_raises_app_exception(monkeypatch):
    monkeypatch.setattr(student_assistant_service, "settings", FakeSettings())

    with pytest.raises(AppException) as exc_info:
        StudentAssistantService._call_dify("", "英国硕士申请需要哪些材料")

    assert exc_info.value.status_code == 503
    assert exc_info.value.code == 50301


def test_student_assistant_dify_success(monkeypatch):
    monkeypatch.setattr(student_assistant_service, "settings", FakeSettings())

    def fake_urlopen(req, timeout):
        assert req.headers["Authorization"] == "Bearer test-key"
        assert timeout == 60
        return FakeResponse(
            json.dumps(
                {"answer": "ok", "conversation_id": "conv-1"},
                ensure_ascii=False,
            ).encode("utf-8")
        )

    monkeypatch.setattr(student_assistant_service.urllib.request, "urlopen", fake_urlopen)

    result = StudentAssistantService._call_dify("test-key", "hello")

    assert result == {"answer": "ok", "conversation_id": "conv-1"}


def test_student_assistant_dify_invalid_json_raises_app_exception(monkeypatch):
    monkeypatch.setattr(student_assistant_service, "settings", FakeSettings())
    monkeypatch.setattr(
        student_assistant_service.urllib.request,
        "urlopen",
        lambda req, timeout: FakeResponse(b"not-json"),
    )

    with pytest.raises(AppException) as exc_info:
        StudentAssistantService._call_dify("test-key", "hello")

    assert exc_info.value.status_code == 503
    assert exc_info.value.code == 50304
