from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.sql import func

from app.database import Base


class AcademicEvent(Base):
    __tablename__ = "academic_event"
    __table_args__ = (
        Index("idx_academic_student_id", "student_id"),
        Index("idx_academic_type", "event_type"),
        Index("idx_academic_deadline_time", "deadline_time"),
        Index("idx_academic_status", "status"),
        {"comment": "学业考务事件表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="学业考务事件ID")
    student_id = Column(BigInteger, ForeignKey("student_profile.id"), nullable=True, comment="学生ID，为空表示公共事件")
    event_type = Column(String(50), nullable=False, comment="事件类型：paper_deadline论文DDL/exam考试/course_deadline课程截止/other其他")
    title = Column(String(300), nullable=False, comment="事件标题")
    event_desc = Column(Text, nullable=True, comment="事件说明")
    course_name = Column(String(200), nullable=True, comment="关联课程")
    deadline_time = Column(DateTime, nullable=False, comment="截止或考试时间")
    reminder_time = Column(DateTime, nullable=True, comment="提醒时间")
    status = Column(String(30), nullable=False, default="active", server_default="active", comment="状态：active有效/completed已完成/cancelled已取消")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
