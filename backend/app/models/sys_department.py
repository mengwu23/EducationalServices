from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func

from backend.app.database import Base


class SysDepartment(Base):
    __tablename__ = "sys_department"
    __table_args__ = (
        Index("idx_department_parent_id", "parent_id"),
        Index("idx_department_status", "status"),
        {"comment": "部门组织架构表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="部门ID")
    department_name = Column(String(100), nullable=False, comment="部门名称")
    parent_id = Column(BigInteger, ForeignKey("sys_department.id"), nullable=True, comment="上级部门ID，顶级部门为空")
    leader_employee_id = Column(BigInteger, nullable=True, comment="部门负责人ID，前期只存ID不强制外键，避免循环依赖")
    department_desc = Column(String(500), nullable=True, comment="部门职责说明")
    sort_order = Column(Integer, nullable=False, default=0, server_default="0", comment="排序号")
    status = Column(String(20), nullable=False, default="enabled", server_default="enabled", comment="状态：enabled启用/disabled停用")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
