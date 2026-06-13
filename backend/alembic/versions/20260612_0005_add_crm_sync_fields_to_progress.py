"""为申请进度表增加 CRM 同步字段

Revision ID: 20260612_0005
Revises: 20260610_0004
Create Date: 2026-06-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260612_0005"
down_revision = "20260610_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "student_application_progress",
        sa.Column("crm_record_id", sa.String(length=100), nullable=True, comment="CRM系统记录ID"),
    )
    op.add_column(
        "student_application_progress",
        sa.Column(
            "crm_sync_status",
            sa.String(length=30),
            nullable=False,
            server_default="not_synced",
            comment="CRM同步状态：not_synced/syncing/synced/failed",
        ),
    )
    op.add_column(
        "student_application_progress",
        sa.Column("crm_last_sync_time", sa.DateTime(), nullable=True, comment="最近CRM同步时间"),
    )
    op.create_index("idx_progress_crm_record", "student_application_progress", ["crm_record_id"])


def downgrade() -> None:
    op.drop_index("idx_progress_crm_record", table_name="student_application_progress")
    op.drop_column("student_application_progress", "crm_last_sync_time")
    op.drop_column("student_application_progress", "crm_sync_status")
    op.drop_column("student_application_progress", "crm_record_id")
