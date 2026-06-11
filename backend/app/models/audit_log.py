from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operator_user_id: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    operator_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    biz_module: Mapped[str] = mapped_column(String(50), nullable=False)
    biz_object_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    biz_object_id: Mapped[int | None] = mapped_column(nullable=True)
    before_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    draft_id: Mapped[int | None] = mapped_column(ForeignKey("ai_draft.id"), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    result: Mapped[str] = mapped_column(String(30), default="success", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AiToolCallLog(Base):
    __tablename__ = "ai_tool_call_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    caller: Mapped[str] = mapped_column(String(50), default="dify", nullable=False)
    conversation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    arguments_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    draft_id: Mapped[int | None] = mapped_column(ForeignKey("ai_draft.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="success", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
