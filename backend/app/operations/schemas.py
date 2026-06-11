"""企业业务办理助手的请求/响应 Pydantic 模型。"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IntentEnum(str, Enum):
    """当前支持的业务操作意图。"""
    CREATE_LEAD = "create_lead"
    UPDATE_LEAD_STATUS = "update_lead_status"
    SUBMIT_DAILY_REPORT = "submit_daily_report"
    ENTER_STUDENT_SCORE = "enter_student_score"
    APPROVE_LEAVE = "approve_leave"
    HANDLE_COMPLAINT = "handle_complaint"


class ExecuteRequest(BaseModel):
    """统一执行入口请求。"""
    query: str = Field(description="用户的自然语言输入")
    conversation_id: Optional[str] = Field(default=None, description="Dify/LLM 会话 ID，用于多轮追问时回传")
    draft_id: Optional[int] = Field(default=None, description="追问场景：已有的草稿 ID")
    extra_context: Optional[Dict[str, Any]] = Field(default=None, description="辅助上下文，如当前页面客户列表等")


class ConfirmRequest(BaseModel):
    """确认/拒绝草稿请求。"""
    draft_id: int = Field(description="草稿 ID")
    action: str = Field(description="操作：confirm 确认 / reject 拒绝")
    reject_reason: Optional[str] = Field(default=None, description="拒绝原因，拒绝时建议填写")


class FieldItem(BaseModel):
    """确认卡片中的一个字段项。"""
    key: str = Field(description="字段键名")
    label: str = Field(description="字段展示标签")
    value: Any = Field(default=None, description="字段值")
    required: bool = Field(default=False, description="是否必填")
    editable: bool = Field(default=True, description="是否允许编辑")


class ConfirmationCard(BaseModel):
    """确认卡片数据。"""
    title: str = Field(description="确认卡片标题")
    intent: str = Field(description="操作意图")
    fields: List[FieldItem] = Field(default_factory=list, description="字段列表")
    summary: Optional[str] = Field(default=None, description="AI 生成的文字摘要")


class MissingField(BaseModel):
    """缺失字段提示项。"""
    key: str = Field(description="缺失字段键名")
    label: str = Field(description="缺失字段展示名称")
    question: str = Field(description="向用户追问的问题")


class CandidateItem(BaseModel):
    """选择候选项（如同名客户列表）。"""
    id: int = Field(description="候选对象 ID")
    label: str = Field(description="候选展示文本")
    description: Optional[str] = Field(default=None, description="补充说明")


class OperationResponse(BaseModel):
    """统一操作响应。"""
    status: str = Field(description="状态：pending_confirm / missing_fields / requires_selection / success / failed")
    message: str = Field(default="", description="面向用户的消息文本")
    draft_id: Optional[int] = Field(default=None, description="草稿 ID，后续确认或追问时回传")
    intent: Optional[str] = Field(default=None, description="识别的操作意图")
    confirmation_card: Optional[ConfirmationCard] = Field(default=None, description="确认卡片（status=pending_confirm 时）")
    missing_fields: List[MissingField] = Field(default_factory=list, description="缺失字段列表（status=missing_fields 时）")
    candidates: List[CandidateItem] = Field(default_factory=list, description="选择候选项列表（status=requires_selection 时）")
    selection_type: Optional[str] = Field(default=None, description="选择类型，如 customer_selection")
    question: Optional[str] = Field(default=None, description="向用户提出的问题")
    conversation_id: Optional[str] = Field(default=None, description="LLM 会话 ID，多轮对话回传")
    error: Optional[str] = Field(default=None, description="错误信息（status=failed 时）")


class ExecuteResult(BaseModel):
    """执行结果。"""
    status: str = Field(description="执行状态：success / failed")
    message: str = Field(description="结果描述")
    biz_object_type: Optional[str] = Field(default=None, description="操作对象类型，如 crm_lead")
    biz_object_id: Optional[int] = Field(default=None, description="操作对象 ID")
    details: Optional[Dict[str, Any]] = Field(default=None, description="返回给前端的详细数据")
