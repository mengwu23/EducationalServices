from sqlalchemy import BigInteger, Column, DateTime, Index, String, UniqueConstraint
from sqlalchemy.sql import func

from backend.app.database import Base


class SysUser(Base):
    __tablename__ = "sys_user"
    __table_args__ = (
        UniqueConstraint("username", name="uk_user_username"),
        Index("idx_user_phone", "phone"),
        Index("idx_user_type", "user_type"),
        Index("idx_user_status", "status"),
        {"comment": "统一用户表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(80), nullable=False, comment="登录账号")
    password_hash = Column(String(255), nullable=True, comment="密码哈希，若接入第三方登录可为空")
    real_name = Column(String(100), nullable=False, comment="真实姓名")
    user_type = Column(String(20), nullable=False, comment="用户类型：employee员工/student学生/customer访客/admin管理员")
    phone = Column(String(30), nullable=True, comment="手机号")
    email = Column(String(120), nullable=True, comment="邮箱")
    status = Column(String(20), nullable=False, default="enabled", server_default="enabled", comment="账号状态：enabled启用/disabled禁用")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
