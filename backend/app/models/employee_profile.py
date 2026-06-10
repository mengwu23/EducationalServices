from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.sql import func

from backend.app.database import Base


class EmployeeProfile(Base):
    __tablename__ = "employee_profile"
    __table_args__ = (
        UniqueConstraint("user_id", name="uk_employee_user_id"),
        UniqueConstraint("employee_no", name="uk_employee_no"),
        Index("idx_employee_department_id", "department_id"),
        Index("idx_employee_role_code", "role_code"),
        Index("idx_employee_status", "status"),
        {"comment": "员工档案表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="员工ID")
    user_id = Column(BigInteger, ForeignKey("sys_user.id"), nullable=False, comment="关联用户ID")
    employee_no = Column(String(50), nullable=False, comment="员工编号")
    employee_name = Column(String(100), nullable=False, comment="员工姓名")
    department_id = Column(BigInteger, ForeignKey("sys_department.id"), nullable=True, comment="所属部门ID")
    role_code = Column(String(50), nullable=False, comment="角色编码：sales顾问/teacher老师/service客服/manager主管/admin管理员")
    job_title = Column(String(100), nullable=True, comment="岗位名称")
    status = Column(String(20), nullable=False, default="active", server_default="active", comment="员工状态：active在职/resigned离职/disabled停用")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
