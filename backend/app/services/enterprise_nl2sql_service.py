"""企业管理 NL2SQL 编排服务。"""

import time
from typing import Protocol

from fastapi import HTTPException, status
from openai import OpenAI
from sqlalchemy.orm import Session

from ..core.config import Settings, get_settings
from ..nl2sql.prompt_builder import build_messages
from ..nl2sql.schema_context import build_schema_text
from ..nl2sql.sql_executor import SqlExecutionError, execute_sql
from ..nl2sql.sql_formatter import extract_sql, format_sql
from ..nl2sql.sql_validator import check_syntax, ensure_is_delete_filter, validate_sql
from ..schemas.enterprise_nl2sql_schema import EnterpriseNl2SqlQueryResult


class SqlGenerator(Protocol):
    """LLM SQL 生成器协议，便于测试时注入假模型。"""

    def generate_sql(self, query: str) -> tuple[str, int]:
        """根据用户问数内容生成 SQL，并返回 LLM 调用耗时。"""


class OpenAiCompatibleSqlGenerator:
    """使用 OpenAI 兼容协议调用 DeepSeek 等模型生成 SQL。"""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        if not self.settings.nl2sql_llm_api_key:
            raise RuntimeError("未配置 NL2SQL_LLM_API_KEY")
        api_key = self.settings.nl2sql_llm_api_key
        base_url = self.settings.nl2sql_llm_base_url
        self.client = OpenAI(**{"api_key": api_key, "base_url": base_url})

    def generate_sql(self, query: str) -> tuple[str, int]:
        """调用 LLM，把自然语言问题转换成 SQL。"""
        messages = build_messages(query, build_schema_text())
        started_at = time.time()
        response = self.client.chat.completions.create(
            model=self.settings.nl2sql_llm_model,
            messages=messages,
            temperature=0,
            max_tokens=800,
            stream=False,
        )
        cost_ms = int((time.time() - started_at) * 1000)
        raw_sql = response.choices[0].message.content or ""
        return extract_sql(raw_sql), cost_ms


class EnterpriseNl2SqlService:
    """串联 LLM 生成、SQL 校验、语法预检和数据库执行的核心服务。"""

    def __init__(self, db: Session, sql_generator: SqlGenerator | None = None):
        self.db = db
        self.sql_generator = sql_generator

    def query(self, query: str, return_sql: bool = True) -> EnterpriseNl2SqlQueryResult:
        """执行一次自然语言问数，最终结果来自数据库真实查询。"""
        total_started_at = time.time()

        try:
            sql_generator = self.sql_generator or OpenAiCompatibleSqlGenerator()
            generated_sql, llm_cost_ms = sql_generator.generate_sql(query)
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"NL2SQL LLM 调用失败：{exc}") from exc

        formatted_sql = format_sql(generated_sql)
        valid, error_message = validate_sql(formatted_sql)
        if not valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        guarded_sql = ensure_is_delete_filter(formatted_sql)
        syntax_ok, syntax_error = check_syntax(guarded_sql, self.db)
        if not syntax_ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SQL 语法校验失败：{syntax_error}")

        try:
            result = execute_sql(guarded_sql, self.db)
        except SqlExecutionError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SQL 执行失败：{exc}") from exc

        total_cost_ms = int((time.time() - total_started_at) * 1000)
        return EnterpriseNl2SqlQueryResult(
            query=query,
            sql=guarded_sql if return_sql else None,
            columns=result["columns"],
            rows=result["rows"],
            row_count=result["row_count"],
            cost_ms=max(total_cost_ms, llm_cost_ms),
            is_cached=False,
        )
