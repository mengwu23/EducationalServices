"""SQL formatting helpers."""

try:
    import sqlparse
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    sqlparse = None


def extract_sql(raw: str) -> str:
    """Extract SQL from raw LLM output, including fenced code blocks."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        lines = text.splitlines()
        if lines and lines[0].lower() in {"sql", "mysql"}:
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text


def format_sql(sql: str) -> str:
    """Format SQL for display and logging."""
    sql_text = sql.strip()
    if sqlparse is None:
        return sql_text.rstrip(";")
    return sqlparse.format(sql_text, keyword_case="upper", reindent=True).rstrip(";")
