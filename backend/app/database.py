"""统一管理 SQLAlchemy 引擎、基类和数据库会话依赖。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ORM 层共用的数据库连接配置。
user = "root"
password = "123456"
host = "localhost"
port = "3306"
database = "education_service_ai"

# 所有 DAO 查询共用同一个数据库引擎。
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
    pool_size=5,
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
