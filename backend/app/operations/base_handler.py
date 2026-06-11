"""OperationHandler 抽象基类。

所有业务操作处理器继承此类，实现：
- create_draft : 首次解析后创建草稿
- supplement   : 追问补全字段
- execute      : 确认后执行写库
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.app.core.security import CurrentUser
from backend.app.models.draft import AiDraft

from .schemas import ExecuteResult, OperationResponse
from .intent_schemas import IntentSchema


class OperationHandler(ABC):
    """操作处理器基类。"""

    @property
    @abstractmethod
    def intent(self) -> str:
        """返回操作意图标识，如 'create_lead'。"""
        ...

    @property
    @abstractmethod
    def schema(self) -> IntentSchema:
        """返回该操作的字段 Schema。"""
        ...

    @abstractmethod
    def create_draft(self, params: Dict[str, Any], user: CurrentUser) -> OperationResponse:
        """首次创建草稿。

        接收 LLM 解析后的参数，校验必填字段，
        如有缺失返回追问列表，完整则创建 AiDraft 并返回确认卡片。
        """
        ...

    @abstractmethod
    def supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        """追问补全。

        根据用户新输入的 query 提取缺失字段并更新草稿，
        完成后返回确认卡片，仍缺字段则继续追问。
        """
        ...

    @abstractmethod
    def execute(self, draft: AiDraft, user: CurrentUser) -> ExecuteResult:
        """确认执行，将草稿内容写入数据库。"""
        ...

    def get_field_label(self, key: str) -> str:
        """获取字段的中文展示名。"""
        return self.schema.get_label(key)

    def get_required_keys(self) -> list:
        return self.schema.required_keys
