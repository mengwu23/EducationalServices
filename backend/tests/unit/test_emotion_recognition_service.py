"""学生情绪语义识别服务单元测试。"""

from backend.app.common.enums import PsychRiskLevel
from backend.app.services.emotion_recognition_service import EMOTION_TAGS, EmotionRecognitionService


class FakeLlm:
    def __init__(self, available=True, result=None, raises=False):
        self._available = available
        self._result = result or {}
        self._raises = raises

    def is_available(self):
        return self._available

    def complete_json(self, system_prompt, user_content, **kwargs):
        if self._raises:
            raise ValueError("boom")
        return self._result


def test_recognize_none_when_unavailable():
    svc = EmotionRecognitionService(FakeLlm(available=False))
    assert svc.recognize("我很难过") is None


def test_recognize_none_on_empty_text():
    svc = EmotionRecognitionService(FakeLlm())
    assert svc.recognize("   ") is None


def test_recognize_cultural_conflict_tag():
    fake = FakeLlm(result={"emotion_tag": "cultural_conflict", "emotion_score": 35, "summary": "文化适应困难"})
    svc = EmotionRecognitionService(fake)
    result = svc.recognize("周围都是外国人，跟不上节奏")
    assert result["emotion_tag"] == "cultural_conflict"
    assert "cultural_conflict" in EMOTION_TAGS
    # 文化冲突属高风险标签
    assert result["risk_level"] == PsychRiskLevel.HIGH.value


def test_recognize_unknown_tag_falls_back_to_neutral():
    fake = FakeLlm(result={"emotion_tag": "未知", "emotion_score": 80, "summary": "x"})
    svc = EmotionRecognitionService(fake)
    result = svc.recognize("还行")
    assert result["emotion_tag"] == "neutral"


def test_recognize_critical_risk_on_very_low_score():
    fake = FakeLlm(result={"emotion_tag": "depressed", "emotion_score": 10, "summary": "极度低落"})
    svc = EmotionRecognitionService(fake)
    result = svc.recognize("我撑不下去了")
    assert result["risk_level"] == PsychRiskLevel.CRITICAL.value


def test_recognize_score_clamped_to_range():
    fake = FakeLlm(result={"emotion_tag": "happy", "emotion_score": 150, "summary": "x"})
    svc = EmotionRecognitionService(fake)
    result = svc.recognize("超级开心")
    assert result["emotion_score"] == 100


def test_recognize_low_risk_for_happy_high_score():
    fake = FakeLlm(result={"emotion_tag": "happy", "emotion_score": 90, "summary": "状态好"})
    svc = EmotionRecognitionService(fake)
    result = svc.recognize("最近很顺利")
    assert result["risk_level"] == PsychRiskLevel.LOW.value


def test_recognize_none_on_exception():
    svc = EmotionRecognitionService(FakeLlm(raises=True))
    assert svc.recognize("文本") is None


def test_recognize_invalid_score_becomes_none():
    fake = FakeLlm(result={"emotion_tag": "stable", "emotion_score": "高", "summary": "x"})
    svc = EmotionRecognitionService(fake)
    result = svc.recognize("平稳")
    assert result["emotion_score"] is None
