"""学生情绪语义识别服务。

学生通过情绪打卡输入一段自我描述文本，调用 DeepSeek 识别情绪标签、
情绪分值（0-100）和情绪摘要，转换为 EmotionUpdateRequest 供心理画像更新。
为心理健康周报的"情绪识别"和"文化冲突识别"需求补齐上游数据。

设计要点：
- 标签枚举与 dify_client.EMOTION_TAG_MAP 对齐，新增 cultural_conflict(文化冲突)。
- 高风险标签（depressed/cultural_conflict 等）+ 低情绪分自动映射 risk_level。
- 未配置 LLM 或调用失败时 recognize() 返回 None，调用方据此跳过。
"""

from typing import Any

from backend.app.common.enums import PsychRiskLevel
from backend.app.integrations.llm_text_client import LlmTextClient

# 情绪标签枚举（与 dify_client.EMOTION_TAG_MAP 对齐，新增 cultural_conflict）
EMOTION_TAGS = {
    "anxious": "焦虑",
    "stable": "平稳",
    "depressed": "低落",
    "excited": "亢奋",
    "lonely": "孤独",
    "stressed": "压力大",
    "happy": "积极",
    "neutral": "平静",
    "cultural_conflict": "文化冲突",
}

# 高风险情绪标签：识别到时风险等级至少为 high
_HIGH_RISK_TAGS = {"depressed", "cultural_conflict", "lonely"}

_SYSTEM_PROMPT = (
    "你是留学生心理关怀助手。根据学生的情绪打卡文本，识别其当前情绪状态。\n"
    "1. 从以下固定标签中选择最匹配的一个英文标签键：\n"
    "   anxious(焦虑)、stable(平稳)、depressed(低落)、excited(亢奋)、lonely(孤独)、"
    "stressed(压力大)、happy(积极)、neutral(平静)、cultural_conflict(文化冲突)。\n"
    "   其中 cultural_conflict 用于识别因海外文化差异、语言障碍、融入困难导致的困扰。\n"
    "2. 给出情绪分值（0-100 的整数，越高越积极健康）。\n"
    "3. 用一句话（不超过80字）概括学生的情绪状态。\n"
    "只输出一个 JSON 对象，不要输出任何解释或代码块，格式：\n"
    '{"emotion_tag": "标签键", "emotion_score": 数值, "summary": "情绪摘要"}'
)


class EmotionRecognitionService:
    """学生情绪文本语义识别。"""

    def __init__(self, llm_client: LlmTextClient | None = None):
        self.llm_client = llm_client or LlmTextClient()

    def is_available(self) -> bool:
        return self.llm_client.is_available()

    def recognize(self, text: str) -> dict[str, Any] | None:
        """识别情绪打卡文本，返回情绪字段字典。

        返回 {"emotion_tag", "emotion_score", "summary", "risk_level"}；
        LLM 不可用或调用/解析失败时返回 None。
        """
        if not self.llm_client.is_available():
            return None
        if not text or not text.strip():
            return None

        try:
            result = self.llm_client.complete_json(_SYSTEM_PROMPT, text.strip(), max_tokens=300)
        except Exception:
            return None

        tag = result.get("emotion_tag")
        if tag not in EMOTION_TAGS:
            tag = "neutral"

        score = self._coerce_score(result.get("emotion_score"))
        summary = (result.get("summary") or "").strip()[:300] or None
        risk_level = self._infer_risk_level(tag, score)

        return {
            "emotion_tag": tag,
            "emotion_score": score,
            "summary": summary,
            "risk_level": risk_level,
        }

    @staticmethod
    def _coerce_score(value: Any) -> int | None:
        try:
            score = int(round(float(value)))
        except (TypeError, ValueError):
            return None
        return max(0, min(100, score))

    @staticmethod
    def _infer_risk_level(tag: str, score: int | None) -> str:
        """依据情绪标签和分值推断风险等级。"""
        if score is not None and score <= 20:
            return PsychRiskLevel.CRITICAL.value
        if tag in _HIGH_RISK_TAGS or (score is not None and score <= 40):
            return PsychRiskLevel.HIGH.value
        if tag in {"anxious", "stressed"} or (score is not None and score <= 60):
            return PsychRiskLevel.MEDIUM.value
        return PsychRiskLevel.LOW.value
