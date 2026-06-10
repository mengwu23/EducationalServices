"""补充更新时间和逻辑删除字段

Revision ID: 20260610_0002
Revises: 20260609_0001
Create Date: 2026-06-10
"""
from alembic import op
import sqlalchemy as sa


revision = "20260610_0002"
down_revision = "20260609_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_log", sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column("audit_log", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column(
        "ai_tool_call_log",
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.add_column(
        "ai_tool_call_log",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.add_column("ai_draft", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("ai_report", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column(
        "report_export_record",
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.add_column(
        "report_export_record",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("report_export_record", "is_deleted")
    op.drop_column("report_export_record", "update_time")
    op.drop_column("ai_report", "is_deleted")
    op.drop_column("ai_draft", "is_deleted")
    op.drop_column("ai_tool_call_log", "is_deleted")
    op.drop_column("ai_tool_call_log", "update_time")
    op.drop_column("audit_log", "is_deleted")
    op.drop_column("audit_log", "update_time")
