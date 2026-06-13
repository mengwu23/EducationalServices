from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ServiceAgentMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, description="访客消息")
    conversation_id: str | None = Field(default=None, max_length=100, description="会话ID（用于多轮对话，首次不填）")

    @field_validator("conversation_id", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class ServiceAgentMessageResponse(BaseModel):
    visitor_id: str
    conversation_id: str | None = None
    visitor_message: str
    reply_text: str
    intent: str | None = None
    suggested_actions: list[dict[str, Any]] = Field(default_factory=list)
    references: list[dict[str, Any]] = Field(default_factory=list)
    trace_id: str | None = None


class ServiceAgentFaqSearchRequest(BaseModel):
    keyword: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=5, ge=1, le=20)
    conversation_id: str | None = None
    trace_id: str | None = None
    caller: Literal["dify", "other"] = "dify"


class ServiceAgentProjectSearchRequest(BaseModel):
    keyword: str | None = Field(default=None, max_length=200)
    project_type: str | None = Field(default=None, max_length=50)
    target_country: str | None = Field(default=None, max_length=100)
    education_level: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=5, ge=1, le=20)
    conversation_id: str | None = None
    trace_id: str | None = None
    caller: Literal["dify", "other"] = "dify"


class ServiceAgentEventSearchRequest(BaseModel):
    keyword: str | None = Field(default=None, max_length=200)
    event_type: str | None = Field(default=None, max_length=30)
    status: str | None = Field(default="open", max_length=30)
    limit: int = Field(default=10, ge=1, le=50)
    conversation_id: str | None = None
    trace_id: str | None = None
    caller: Literal["dify", "other"] = "dify"


class ActivitySignupRequest(BaseModel):
    event_id: int
    visitor_name: str = Field(min_length=1, max_length=100)
    visitor_phone: str | None = Field(default=None, max_length=30)
    lead_id: int | None = None
    remark: str | None = Field(default=None, max_length=500)
    conversation_id: str | None = None
    trace_id: str | None = None
    caller: Literal["dify", "other"] = "dify"


class ActivitySignupResponse(BaseModel):
    id: int
    event_id: int
    lead_id: int | None = None
    visitor_name: str
    visitor_phone: str | None = None
    registration_status: str
    remark: str | None = None
    create_time: datetime | None = None

