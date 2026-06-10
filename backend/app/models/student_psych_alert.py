from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class StudentPsychAlert(Base):
    __tablename__ = "student_psych_alert"
    __table_args__ = (
        UniqueConstraint("alert_no", name="uk_psych_alert_no"),
        Index("idx_psych_alert_student_id", "student_id"),
        Index("idx_psych_alert_status", "status"),
        Index("idx_psych_alert_risk_level", "risk_level"),
        {"comment": "学生心理预警表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="心理预警ID")
    alert_no = Column(String(50), nullable=False, comment="预警编号")
    student_id = Column(BigInteger, ForeignKey("student_profile.id"), nullable=False, comment="学生ID")
    trigger_reason = Column(Text, nullable=False, comment="触发原因")
    risk_level = Column(String(30), nullable=False, comment="风险等级：medium中/high高/critical危急")
    status = Column(String(30), nullable=False, default="pending", server_default="pending", comment="处理状态：pending未处理/processing跟进中/resolved已解除/closed已关闭")
    teacher_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="负责跟进老师ID")
    handle_result = Column(Text, nullable=True, comment="处理结果")
    close_time = Column(DateTime, nullable=True, comment="关闭时间")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="逻辑删除：0未删除/1已删除")
