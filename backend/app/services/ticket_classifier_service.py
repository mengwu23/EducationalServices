"""投诉工单 AI 分类与根因打标服务。

对工单 detail 正文调用 DeepSeek，输出标准化分类标签和根因摘要，
分别写回 category 字段和闲置的 content_summary 字段，
为投诉周报的"AI 智能分类"和"根因归因"需求补齐上游数据。

设计要点：
- 未配置 LLM API Key 时 classify() 返回 None，调用方跳过打标，不阻塞工单创建。
- 分类标签限定在固定枚举内，避免模型自由发挥导致脏数据。
- LLM 调用异常被吞掉并返回 None，AI 打标失败绝不影响主业务流程。
"""

from typing import Any

from backend.app.integrations.llm_text_client import LlmTextClient

# 工单分类枚举（与报告层 CATEGORY_MAP 对齐：course/service/visa/school/life/finance）
TICKET_CATEGORIES = {
    "course": "教学课程",
    "service": "服务顾问",
    "visa": "签证办理",
    "school": "院校申请",
    "life": "生活服务",
    "finance": "财务费用",
    "other": "其他",
}

_SYSTEM_PROMPT = (
    "你是教育留学服务公司的投诉工单分类助手。根据用户提供的工单正文，"
    "完成两件事：\n"
    "1. 从以下固定分类中选择最匹配的一个英文分类键：\n"
    "   course(教学课程)、service(服务顾问)、visa(签证办理)、school(院校申请)、"
    "life(生活服务)、finance(财务费用)、other(其他)。\n"
    "2. 用一句话（不超过60字）概括投诉的核心根因。\n"
    "只输出一个 JSON 对象，不要输出任何解释或代码块，格式：\n"
    '{"category": "分类键", "root_cause": "根因摘要"}'
)


class TicketClassifierService:
    """投诉工单 AI 分类 + 根因打标。"""

    def __init__(self, llm_client: LlmTextClient | None = None):
        self.llm_client = llm_client or LlmTextClient()

    def is_available(self) -> bool:
        return self.llm_client.is_available()

    def classify(self, title: str, detail: str) -> dict[str, Any] | None:
        """对工单做分类与根因打标。

        返回 {"category": <英文分类键>, "content_summary": <根因摘要>}；
        LLM 不可用或调用/解析失败时返回 None（调用方据此跳过写回）。
        """
        if not self.llm_client.is_available():
            return None

        user_content = f"工单标题：{title or '（无）'}\n工单正文：{detail or '（无）'}"
        try:
            result = self.llm_client.complete_json(_SYSTEM_PROMPT, user_content, max_tokens=300)
        except Exception:
            # AI 打标失败不影响工单主流程
            return None

        category = result.get("category")
        if category not in TICKET_CATEGORIES:
            category = "other"
        root_cause = (result.get("root_cause") or "").strip()[:200]
        return {
            "category": category,
            "content_summary": root_cause or None,
        }
