"""统一管理 SQLAlchemy 引擎、基础模型和数据库会话依赖。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.core.config import get_settings

Base = declarative_base()

_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def get_engine() -> Engine:
    """按需创建数据库引擎，避免应用导入阶段因缺少 DATABASE_URL 直接失败。"""
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("未配置 DATABASE_URL")

    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        _engine = create_engine(
            settings.database_url,
            pool_size=5,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """返回复用的数据库会话工厂。"""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory


def get_db() -> Generator[OrmSession, None, None]:
    """按请求提供数据库会话，并在请求结束后关闭。"""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
