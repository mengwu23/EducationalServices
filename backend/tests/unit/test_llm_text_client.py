"""共享 LLM 文本客户端单元测试。"""

from backend.app.core.config import Settings
from backend.app.integrations.llm_text_client import LlmTextClient


def _client_without_key():
    return LlmTextClient(Settings(nl2sql_llm_api_key=""))


def test_is_available_false_without_key():
    assert _client_without_key().is_available() is False


def test_is_available_true_with_key():
    client = LlmTextClient(Settings(nl2sql_llm_api_key="sk-test"))
    assert client.is_available() is True


def test_parse_json_object_plain():
    parsed = LlmTextClient._parse_json_object('{"a": 1, "b": "x"}')
    assert parsed == {"a": 1, "b": "x"}


def test_parse_json_object_with_code_fence():
    text = '```json\n{"category": "visa", "root_cause": "签证延误"}\n```'
    parsed = LlmTextClient._parse_json_object(text)
    assert parsed["category"] == "visa"


def test_parse_json_object_with_think_tag_and_prose():
    text = '<think>让我想想</think>这是结果：{"emotion_tag": "lonely", "emotion_score": 30}'
    parsed = LlmTextClient._parse_json_object(text)
    assert parsed["emotion_tag"] == "lonely"
    assert parsed["emotion_score"] == 30


def test_parse_json_object_returns_none_on_garbage():
    assert LlmTextClient._parse_json_object("完全不是 JSON") is None
    assert LlmTextClient._parse_json_object("") is None
