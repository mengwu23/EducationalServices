"""学生申请进度表实体。"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.sql import func

from ..database import Base


class StudentApplicationProgress(Base):
    """存储院校申请、签证等办理进度。"""
    __tablename__ = "student_application_progress"
    __table_args__ = (
        Index("idx_progress_student_id", "student_id"),
        Index("idx_progress_stage", "progress_stage"),
        Index("idx_progress_status", "progress_status"),
        Index("idx_progress_handler", "handler_employee_id"),
        {"comment": "学生申请进度表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="申请进度ID")
    student_id = Column(BigInteger, ForeignKey("student_profile.id"), nullable=False, comment="学生ID")
    progress_stage = Column(String(80), nullable=False, comment="进度阶段：essay文书/school_apply院校申请/visa签证/offer录取/other其他")
    target_country = Column(String(100), nullable=True, comment="目标国家")
    school_name = Column(String(200), nullable=True, comment="申请院校")
    program_name = Column(String(200), nullable=True, comment="申请项目")
    progress_status = Column(String(50), nullable=False, default="processing", server_default="processing", comment="进度状态：pending待开始/processing处理中/completed已完成/blocked受阻")
    progress_desc = Column(Text, nullable=True, comment="进度说明")
    handler_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="负责人员工ID")
    expected_finish_time = Column(DateTime, nullable=True, comment="预计完成时间")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
