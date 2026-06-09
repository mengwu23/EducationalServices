from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SysDepartment(Base):
    __tablename__ = "sys_department"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class EmployeeProfile(Base):
    __tablename__ = "employee_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("sys_department.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class StudentProfile(Base):
    __tablename__ = "student_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    advisor_employee_id: Mapped[int | None] = mapped_column(ForeignKey("employee_profile.id"), nullable=True)


class StudentFeedbackTicket(Base):
    __tablename__ = "student_feedback_ticket"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("student_profile.id"), nullable=True)
    handler_employee_id: Mapped[int | None] = mapped_column(ForeignKey("employee_profile.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(80), default="unknown", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    close_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class CrmLead(Base):
    __tablename__ = "crm_lead"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("sys_department.id"), nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)


class CustomerAnalysisRecord(Base):
    __tablename__ = "customer_analysis_record"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("crm_lead.id"), nullable=True)
    result_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)


class EventRegistration(Base):
    __tablename__ = "event_registration"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("crm_lead.id"), nullable=True)
    event_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="registered", nullable=False)
    register_date: Mapped[date] = mapped_column(Date, nullable=False)
