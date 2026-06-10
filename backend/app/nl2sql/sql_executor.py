"""NL2SQL SQL 执行器。"""

from datetime import date, datetime
from decimal import Decimal
import re

from sqlalchemy import text

MAX_ROWS = 1000
QUERY_TIMEOUT_MS = 10000


class SqlExecutionError(Exception):
    """SQL 执行失败。"""


def execute_sql(sql: str, db) -> dict:
    """执行已通过校验的 SELECT SQL，并返回 columns/rows/row_count。"""
    sql_to_execute = _ensure_limit(sql.strip().rstrip(";"))
    if sql_to_execute.upper().startswith("SELECT"):
        sql_to_execute = f"SELECT /*+ MAX_EXECUTION_TIME({QUERY_TIMEOUT_MS}) */ {sql_to_execute[6:].lstrip()}"

    try:
        result = db.execute(text(sql_to_execute))
        if not result.returns_rows:
            return {"columns": [], "rows": [], "row_count": 0}
        columns = list(result.keys())
        rows = [[_serialize_value(value) for value in row] for row in result.fetchall()]
        return {"columns": columns, "rows": rows, "row_count": len(rows)}
    except Exception as exc:
        raise SqlExecutionError(str(exc)) from exc


def _ensure_limit(sql: str) -> str:
    """用户或模型未指定 LIMIT 时追加最大行数限制。"""
    if re.search(r"\bLIMIT\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql} LIMIT {MAX_ROWS}"


def _serialize_value(value):
    """把数据库返回值转换为 JSON 友好的类型。"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
