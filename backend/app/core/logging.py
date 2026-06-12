"""项目日志配置。"""

from __future__ import annotations

import logging
import time
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import sqlparse
from sqlalchemy import event
from sqlalchemy.engine import Engine


LOG_DIR = Path(__file__).resolve().parents[1] / "logging"
LOG_RETENTION_DAYS = 7

_CONFIGURED = False
_SQL_LOGGING_ENGINES: set[int] = set()


class DailyFileHandler(logging.Handler):
    """按自然日期写入 prefix-YYYY-MM-DD.log，并保留最近若干天。"""

    def __init__(self, log_dir: Path, prefix: str, retention_days: int = LOG_RETENTION_DAYS):
        super().__init__()
        self.log_dir = log_dir
        self.prefix = prefix
        self.retention_days = retention_days
        self.current_date: date | None = None
        self.stream = None
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._cleanup_old_logs()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._ensure_stream()
            message = self.format(record)
            self.stream.write(message + "\n")
            self.flush()
        except Exception:
            self.handleError(record)

    def flush(self) -> None:
        if self.stream and not self.stream.closed:
            self.stream.flush()

    def close(self) -> None:
        if self.stream and not self.stream.closed:
            self.stream.close()
        super().close()

    def _ensure_stream(self) -> None:
        today = date.today()
        if self.current_date == today and self.stream and not self.stream.closed:
            return
        if self.stream and not self.stream.closed:
            self.stream.close()
        self.current_date = today
        self._cleanup_old_logs()
        log_file = self.log_dir / f"{self.prefix}-{today.isoformat()}.log"
        self.stream = log_file.open("a", encoding="utf-8")

    def _cleanup_old_logs(self) -> None:
        cutoff = date.today() - timedelta(days=self.retention_days - 1)
        for path in self.log_dir.glob(f"{self.prefix}-*.log"):
            log_date = _extract_log_date(path, self.prefix)
            if log_date and log_date < cutoff:
                path.unlink(missing_ok=True)


def configure_logging() -> None:
    """初始化项目日志。"""
    global _CONFIGURED
    if _CONFIGURED:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app_handler = DailyFileHandler(LOG_DIR, "app")
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    error_handler = DailyFileHandler(LOG_DIR, "error")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    _CONFIGURED = True
    logging.getLogger("app").info("日志系统初始化完成，日志目录：%s", LOG_DIR)


def configure_sql_logging(engine: Engine) -> None:
    """为 SQLAlchemy Engine 注册 SQL 执行日志。"""
    configure_logging()
    engine_id = id(engine)
    if engine_id in _SQL_LOGGING_ENGINES:
        return
    _SQL_LOGGING_ENGINES.add(engine_id)

    sql_logger = logging.getLogger("app.sql")

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.perf_counter()
        context._formatted_sql_for_log = _format_sql_for_log(cursor, statement, parameters)

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        start_time = getattr(context, "_query_start_time", None)
        duration_ms = (time.perf_counter() - start_time) * 1000 if start_time else 0
        formatted_sql = getattr(context, "_formatted_sql_for_log", None) or _format_sql_for_log(
            cursor, statement, parameters
        )
        rowcount = getattr(cursor, "rowcount", None)
        sql_logger.info(
            "SQL 执行完成 | 耗时 %.2f ms | 行数 %s | executemany=%s\n%s",
            duration_ms,
            rowcount,
            executemany,
            formatted_sql,
        )

    @event.listens_for(engine, "handle_error")
    def handle_error(exception_context):
        duration_ms = 0
        start_time = getattr(exception_context.execution_context, "_query_start_time", None)
        if start_time:
            duration_ms = (time.perf_counter() - start_time) * 1000
        formatted_sql = getattr(exception_context.execution_context, "_formatted_sql_for_log", None)
        if not formatted_sql and exception_context.statement:
            formatted_sql = _format_statement(exception_context.statement, exception_context.parameters)
        sql_logger.exception(
            "SQL 执行失败 | 耗时 %.2f ms | 错误：%s\n%s",
            duration_ms,
            exception_context.original_exception,
            formatted_sql or "",
        )


def log_exception(logger: logging.Logger, message: str, exc: BaseException) -> None:
    """记录异常堆栈到运行日志和错误日志。"""
    logger.error("%s：%s\n%s", message, exc, "".join(traceback.format_exception(exc)))


def _format_sql_for_log(cursor: Any, statement: str, parameters: Any) -> str:
    actual_sql = _try_render_actual_sql(cursor, statement, parameters)
    return _format_statement(actual_sql or statement, None if actual_sql else parameters)


def _try_render_actual_sql(cursor: Any, statement: str, parameters: Any) -> str | None:
    mogrify = getattr(cursor, "mogrify", None)
    if not callable(mogrify) or parameters in (None, (), []):
        return None
    try:
        rendered = mogrify(statement, parameters)
    except Exception:
        return None
    if isinstance(rendered, bytes):
        return rendered.decode("utf-8", errors="replace")
    return str(rendered)


def _format_statement(statement: str, parameters: Any) -> str:
    formatted = sqlparse.format(
        statement,
        keyword_case="upper",
        reindent=True,
        strip_comments=False,
    )
    if parameters not in (None, (), []):
        formatted = f"{formatted}\n-- 参数：{parameters!r}"
    return formatted


def _extract_log_date(path: Path, prefix: str) -> date | None:
    stem = path.stem
    expected_prefix = f"{prefix}-"
    if not stem.startswith(expected_prefix):
        return None
    try:
        return datetime.strptime(stem.removeprefix(expected_prefix), "%Y-%m-%d").date()
    except ValueError:
        return None
