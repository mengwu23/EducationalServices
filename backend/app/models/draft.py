from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class AiDraft(Base):
    __tablename__ = "ai_draft"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    draft_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    draft_type: Mapped[str] = mapped_column(String(50), nullable=False)
    biz_module: Mapped[str] = mapped_column(String(50), nullable=False)
    biz_object_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    biz_object_id: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="generating", nullable=False)
    content_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_trace_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    confirmed_by: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    confirmed_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
