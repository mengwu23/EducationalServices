"""创建智能报告模块基础表

Revision ID: 20260609_0001
Revises:
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa


revision = "20260609_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sys_department",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
    )
    op.create_table(
        "sys_user",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "employee_profile",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("department_id", sa.BigInteger(), sa.ForeignKey("sys_department.id"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
    )
    op.create_table(
        "student_profile",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("advisor_employee_id", sa.BigInteger(), sa.ForeignKey("employee_profile.id"), nullable=True),
    )
    op.create_table(
        "student_feedback_ticket",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.BigInteger(), sa.ForeignKey("student_profile.id"), nullable=True),
        sa.Column("handler_employee_id", sa.BigInteger(), sa.ForeignKey("employee_profile.id"), nullable=True),
        sa.Column("category", sa.String(80), nullable=False, server_default="unknown"),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("close_time", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "crm_lead",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="new"),
        sa.Column("source", sa.String(80), nullable=True),
        sa.Column("owner_user_id", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("department_id", sa.BigInteger(), sa.ForeignKey("sys_department.id"), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "customer_analysis_record",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("lead_id", sa.BigInteger(), sa.ForeignKey("crm_lead.id"), nullable=True),
        sa.Column("result_level", sa.String(50), nullable=True),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "event_registration",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("lead_id", sa.BigInteger(), sa.ForeignKey("crm_lead.id"), nullable=True),
        sa.Column("event_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="registered"),
        sa.Column("register_date", sa.Date(), nullable=False),
    )
    op.create_table(
        "ai_draft",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("draft_no", sa.String(50), nullable=False, unique=True),
        sa.Column("draft_type", sa.String(50), nullable=False),
        sa.Column("biz_module", sa.String(50), nullable=False),
        sa.Column("biz_object_type", sa.String(80), nullable=True),
        sa.Column("biz_object_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="generating"),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("source_trace_id", sa.String(100), nullable=True),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("confirmed_by", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("confirmed_time", sa.DateTime(), nullable=True),
        sa.Column("reject_reason", sa.String(500), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("operator_user_id", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("operator_role", sa.String(50), nullable=True),
        sa.Column("action_type", sa.String(80), nullable=False),
        sa.Column("biz_module", sa.String(50), nullable=False),
        sa.Column("biz_object_type", sa.String(80), nullable=True),
        sa.Column("biz_object_id", sa.BigInteger(), nullable=True),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("draft_id", sa.BigInteger(), sa.ForeignKey("ai_draft.id"), nullable=True),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("result", sa.String(30), nullable=False, server_default="success"),
        sa.Column("error_message", sa.String(1000), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "ai_tool_call_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("caller", sa.String(50), nullable=False, server_default="dify"),
        sa.Column("conversation_id", sa.String(100), nullable=True),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("arguments_summary", sa.JSON(), nullable=True),
        sa.Column("result_summary", sa.JSON(), nullable=True),
        sa.Column("draft_id", sa.BigInteger(), sa.ForeignKey("ai_draft.id"), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="success"),
        sa.Column("error_message", sa.String(1000), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "ai_report",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("report_no", sa.String(50), nullable=False, unique=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="confirmed"),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("source_draft_id", sa.BigInteger(), sa.ForeignKey("ai_draft.id"), nullable=False),
        sa.Column("date_start", sa.Date(), nullable=False),
        sa.Column("date_end", sa.Date(), nullable=False),
        sa.Column("department_id", sa.BigInteger(), sa.ForeignKey("sys_department.id"), nullable=True),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("published_by", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("published_time", sa.DateTime(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "report_export_record",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("report_id", sa.BigInteger(), sa.ForeignKey("ai_report.id"), nullable=False),
        sa.Column("export_type", sa.String(20), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("error_message", sa.String(1000), nullable=True),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("sys_user.id"), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("report_export_record")
    op.drop_table("ai_report")
    op.drop_table("ai_tool_call_log")
    op.drop_table("audit_log")
    op.drop_table("ai_draft")
    op.drop_table("event_registration")
    op.drop_table("customer_analysis_record")
    op.drop_table("crm_lead")
    op.drop_table("student_feedback_ticket")
    op.drop_table("student_profile")
    op.drop_table("employee_profile")
    op.drop_table("sys_user")
    op.drop_table("sys_department")
