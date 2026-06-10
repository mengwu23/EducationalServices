"""统一管理 SQLAlchemy 引擎、基类和数据库会话依赖。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .core.config import get_settings

# ORM 层共用的数据库连接配置，只从环境变量或 .env 读取，不在代码中硬编码账号密码。
settings = get_settings()
if not settings.database_url:
    raise RuntimeError("未配置 DATABASE_URL")

# 所有 DAO 查询共用同一个数据库引擎。
engine = create_engine(
    settings.database_url,
    pool_size=5,
    pool_pre_ping=True,
)

# 所有 ORM 实体类都继承这个基类。
Base = declarative_base()

# 会话工厂，供 FastAPI 依赖和服务层复用。
Session = sessionmaker(bind=engine)


def get_db():
    """按请求提供数据库会话，并在请求结束后关闭。"""
    db = Session()
    try:
        yield db
    finally:
        db.close()
