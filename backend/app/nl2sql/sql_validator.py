"""NL2SQL 安全校验与软删除条件补全。"""

import re

from sqlalchemy import text

from .schema_context import get_allowed_tables

FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "INSERT",
    "UPDATE",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "LOAD",
    "GRANT",
    "REVOKE",
    "RENAME",
    "EXECUTE",
    "INTO OUTFILE",
    "INTO DUMPFILE",
    "LOAD_FILE",
    "SLEEP",
    "BENCHMARK",
]


def validate_sql(sql: str) -> tuple[bool, str]:
    """校验 LLM 生成 SQL 是否满足只读、安全、业务表白名单要求。"""
    if not sql or not sql.strip():
        return False, "SQL 为空"

    clean_sql = _strip_comments(sql).strip().rstrip(";")
    upper_sql = clean_sql.upper()

    if upper_sql == "UNSUPPORTED":
        return False, "该问题无法转换为当前业务数据库查询"
    if not re.match(r"^SELECT\b", upper_sql):
        return False, "只允许执行 SELECT 查询"
    if ";" in clean_sql:
        return False, "只允许单条 SQL，不允许包含分号拼接多语句"
    if re.search(r"\bSELECT\s+\*", upper_sql) or re.search(r"\b[a-zA-Z_][\w]*\s*\.\s*\*", clean_sql):
        return False, "不允许 SELECT *，必须明确查询字段"

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(r"\b" + re.escape(keyword) + r"\b", upper_sql):
            return False, f"SQL 包含禁止关键字：{keyword}"

    tables = extract_table_aliases(clean_sql)
    if not tables:
        return False, "SQL 中未识别到业务表"

    allowed_tables = get_allowed_tables()
    illegal_tables = [table for table in tables if table not in allowed_tables]
    if illegal_tables:
        return False, f"SQL 包含未授权表：{', '.join(illegal_tables)}"

    return True, "ok"


def ensure_is_delete_filter(sql: str) -> str:
    """为每个 FROM/JOIN 业务表补充 is_delete = 0 条件。"""
    normalized_sql = sql.strip().rstrip(";")
    tables = extract_table_aliases(normalized_sql)
    for table_name, alias in tables.items():
        column_ref = f"{alias}.is_delete"
        if re.search(r"\b" + re.escape(column_ref) + r"\b", normalized_sql, flags=re.IGNORECASE):
            continue
        normalized_sql = _append_where_condition(normalized_sql, f"{column_ref} = 0")
    return normalized_sql


def check_syntax(sql: str, db) -> tuple[bool, str]:
    """用 EXPLAIN 对 SQL 做执行前语法检查。"""
    try:
        db.execute(text(f"EXPLAIN {sql}"))
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def extract_table_aliases(sql: str) -> dict[str, str]:
    """提取 FROM/JOIN 中的表名和别名，返回 {table_name: alias}。"""
    result: dict[str, str] = {}
    pattern = r"\b(?:FROM|JOIN)\s+`?([a-zA-Z_][\w]*)`?(?:\s+(?:AS\s+)?`?([a-zA-Z_][\w]*)`?)?"
    for table_name, alias in re.findall(pattern, sql, flags=re.IGNORECASE):
        upper_alias = (alias or "").upper()
        if upper_alias in {"WHERE", "ON", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "GROUP", "ORDER", "LIMIT", "HAVING"}:
            alias = ""
        result[table_name.lower()] = alias or table_name
    return result


def _strip_comments(sql: str) -> str:
    """移除 SQL 注释，避免用注释绕过关键字检查。"""
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", "", sql)
    return sql


def _append_where_condition(sql: str, condition: str) -> str:
    """把补充条件插入到 GROUP BY / HAVING / ORDER BY / LIMIT 之前。"""
    boundary_pattern = r"\b(GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT)\b"
    match = re.search(boundary_pattern, sql, flags=re.IGNORECASE)
    head = sql[: match.start()].rstrip() if match else sql.rstrip()
    tail = sql[match.start() :] if match else ""

    if re.search(r"\bWHERE\b", head, flags=re.IGNORECASE):
        head = f"{head} AND {condition}"
    else:
        head = f"{head} WHERE {condition}"
    return f"{head} {tail}".strip()
