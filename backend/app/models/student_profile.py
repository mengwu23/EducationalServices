"""学生档案表实体。"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class StudentProfile(Base):
    """存储学生身份信息、目标规划和负责员工。"""
    __tablename__ = "student_profile"
    __table_args__ = (
        UniqueConstraint("user_id", name="uk_student_user_id"),
        UniqueConstraint("student_no", name="uk_student_no"),
        Index("idx_student_name", "student_name"),
        Index("idx_student_phone", "phone"),
        Index("idx_student_counselor", "counselor_employee_id"),
        Index("idx_student_teacher", "teacher_employee_id"),
        Index("idx_student_status", "status"),
        {"comment": "学生档案表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="学生ID")
    user_id = Column(BigInteger, ForeignKey("sys_user.id"), nullable=True, comment="关联用户ID，未开通账号时可为空")
    student_no = Column(String(50), nullable=True, comment="学生编号")
    student_name = Column(String(100), nullable=False, comment="学生姓名")
    phone = Column(String(30), nullable=True, comment="手机号")
    email = Column(String(120), nullable=True, comment="邮箱")
    current_school = Column(String(200), nullable=True, comment="当前学校")
    current_grade = Column(String(100), nullable=True, comment="当前年级/阶段")
    target_country = Column(String(100), nullable=True, comment="目标留学国家")
    target_program = Column(String(200), nullable=True, comment="目标申请项目")
    counselor_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="负责顾问员工ID")
    teacher_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="负责老师员工ID")
    status = Column(String(30), nullable=False, default="active", server_default="active", comment="学生状态：active服务中/graduated已结课/inactive停用")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
