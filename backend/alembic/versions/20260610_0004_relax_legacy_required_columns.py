"""放宽旧迁移遗留必填字段

Revision ID: 20260610_0004
Revises: 20260610_0003
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import TypeEngine


revision = "20260610_0004"
down_revision = "20260610_0003"
branch_labels = None
depends_on = None


def _alter_nullable(table_name: str, column_name: str, column_type: TypeEngine, nullable: bool) -> None:
    op.alter_column(table_name, column_name, existing_type=column_type, nullable=nullable)


def upgrade() -> None:
    if op.get_bind().dialect.name != "mysql":
        return

    _alter_nullable("sys_department", "name", sa.String(length=100), True)
    _alter_nullable("sys_user", "role", sa.String(length=50), True)
    _alter_nullable("employee_profile", "name", sa.String(length=100), True)
    _alter_nullable("student_profile", "name", sa.String(length=100), True)
    _alter_nullable("crm_lead", "name", sa.String(length=100), True)
    _alter_nullable("event_registration", "register_date", sa.Date(), True)


def downgrade() -> None:
    if op.get_bind().dialect.name != "mysql":
        return

    _alter_nullable("event_registration", "register_date", sa.Date(), False)
    _alter_nullable("crm_lead", "name", sa.String(length=100), False)
    _alter_nullable("student_profile", "name", sa.String(length=100), False)
    _alter_nullable("employee_profile", "name", sa.String(length=100), False)
    _alter_nullable("sys_user", "role", sa.String(length=50), False)
    _alter_nullable("sys_department", "name", sa.String(length=100), False)
