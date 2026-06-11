"""数据库会话兼容入口。"""

from backend.app.database import get_db, get_engine, get_session_factory

engine = get_engine
SessionLocal = get_session_factory

__all__ = ["SessionLocal", "engine", "get_db", "get_engine", "get_session_factory"]
