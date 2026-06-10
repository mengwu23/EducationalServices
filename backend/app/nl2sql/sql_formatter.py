"""SQL 格式化工具。"""

import sqlparse


def extract_sql(raw: str) -> str:
    """从 LLM 原始输出中提取 SQL，兼容模型误返回 Markdown 代码块的情况。"""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        lines = text.splitlines()
        if lines and lines[0].lower() in {"sql", "mysql"}:
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text


def format_sql(sql: str) -> str:
    """美化 SQL，便于日志和接口返回展示。"""
    return sqlparse.format(sql.strip(), keyword_case="upper", reindent=True).rstrip(";")
