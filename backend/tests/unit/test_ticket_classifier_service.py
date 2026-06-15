"""投诉工单 AI 分类与根因打标服务单元测试。"""

from backend.app.services.ticket_classifier_service import TICKET_CATEGORIES, TicketClassifierService


class FakeLlm:
    """假 LLM：可控返回值，记录调用。"""

    def __init__(self, available=True, result=None, raises=False):
        self._available = available
        self._result = result or {}
        self._raises = raises
        self.calls = []

    def is_available(self):
        return self._available

    def complete_json(self, system_prompt, user_content, **kwargs):
        self.calls.append(user_content)
        if self._raises:
            raise ValueError("boom")
        return self._result


def test_classify_returns_none_when_llm_unavailable():
    svc = TicketClassifierService(FakeLlm(available=False))
    assert svc.is_available() is False
    assert svc.classify("标题", "正文") is None


def test_classify_maps_valid_category_and_root_cause():
    fake = FakeLlm(result={"category": "visa", "root_cause": "签证材料反复补交导致延误"})
    svc = TicketClassifierService(fake)
    result = svc.classify("签证问题", "我的签证一直办不下来")
    assert result["category"] == "签证办理"
    assert result["content_summary"] == "签证材料反复补交导致延误"
    assert "签证" in fake.calls[0]


def test_classify_falls_back_to_other_for_unknown_category():
    fake = FakeLlm(result={"category": "不存在的分类", "root_cause": "xx"})
    svc = TicketClassifierService(fake)
    result = svc.classify("t", "d")
    assert result["category"] == "其他"
    assert result["category"] in TICKET_CATEGORIES.values()


def test_classify_accepts_chinese_category_label():
    fake = FakeLlm(result={"category": "教学课程", "root_cause": "课程进度不匹配"})
    svc = TicketClassifierService(fake)
    result = svc.classify("课程问题", "老师讲得太快")
    assert result["category"] == "教学课程"


def test_classify_truncates_long_root_cause():
    fake = FakeLlm(result={"category": "course", "root_cause": "原" * 500})
    svc = TicketClassifierService(fake)
    result = svc.classify("t", "d")
    assert len(result["content_summary"]) <= 200


def test_classify_empty_root_cause_becomes_none():
    fake = FakeLlm(result={"category": "course", "root_cause": ""})
    svc = TicketClassifierService(fake)
    result = svc.classify("t", "d")
    assert result["content_summary"] is None


def test_classify_returns_none_on_llm_exception():
    fake = FakeLlm(raises=True)
    svc = TicketClassifierService(fake)
    assert svc.classify("t", "d") is None
