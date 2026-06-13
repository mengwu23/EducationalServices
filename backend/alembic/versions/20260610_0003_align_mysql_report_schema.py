"""补齐 MySQL 联调所需的 ORM 表结构

Revision ID: 20260610_0003
Revises: 20260610_0002
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.compiler import compiles

from backend.app import models  # noqa: F401
from backend.app.database import Base


revision = "20260610_0003"
down_revision = "20260610_0002"
branch_labels = None
depends_on = None


@compiles(LONGTEXT, "sqlite")
def compile_longtext_for_sqlite(_type, compiler, **kw):
    return "TEXT"


def _copy_column_for_existing_table(column: sa.Column) -> sa.Column:
    copied = column.copy()
    if copied.primary_key:
        return copied
    if copied.default is None and copied.server_default is None:
        copied.nullable = True
    return copied


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            table.create(bind=bind, checkfirst=True)
            continue

        existing_columns = {column["name"] for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name not in existing_columns:
                op.add_column(table.name, _copy_column_for_existing_table(column))

        existing_indexes = {index["name"] for index in inspector.get_indexes(table.name)}
        for index in table.indexes:
            if index.name and index.name not in existing_indexes:
                op.create_index(index.name, table.name, [column.name for column in index.columns])


def downgrade() -> None:
    pass
