from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class StudentFeedbackTicket(Base):
    __tablename__ = "student_feedback_ticket"
    __table_args__ = (
        CheckConstraint("satisfaction_score IS NULL OR (satisfaction_score BETWEEN 1 AND 5)", name="chk_feedback_satisfaction"),
        UniqueConstraint("ticket_no", name="uk_feedback_ticket_no"),
        Index("idx_feedback_student_id", "student_id"),
        Index("idx_feedback_status", "status"),
        Index("idx_feedback_handler", "handler_employee_id"),
        Index("idx_feedback_category", "category"),
        {"comment": "学生投诉与售后反馈工单表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="反馈工单ID")
    ticket_no = Column(String(50), nullable=False, comment="工单编号")
    student_id = Column(BigInteger, ForeignKey("student_profile.id"), nullable=False, comment="学生ID")
    ticket_type = Column(String(30), nullable=False, default="complaint", server_default="complaint", comment="工单类型：complaint投诉/suggestion建议/consult咨询")
    category = Column(String(100), nullable=True, comment="反馈分类：教学/服务/顾问/财务/签证/院校申请/生活服务/其他")
    title = Column(String(300), nullable=False, comment="反馈标题")
    content_summary = Column(Text, nullable=True, comment="AI摘要")
    detail = Column(Text, nullable=False, comment="详细反馈内容")
    priority_level = Column(String(30), nullable=False, default="normal", server_default="normal", comment="优先级：normal普通/urgent紧急/severe严重")
    status = Column(String(30), nullable=False, default="pending", server_default="pending", comment="状态：pending待处理/processing处理中/resolved已解决/closed已关闭")
    handler_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="当前处理人员工ID")
    solution = Column(Text, nullable=True, comment="处理方案或最终结果")
    satisfaction_score = Column(Integer, nullable=True, comment="满意度评分1-5")
    is_notified = Column(Integer, nullable=False, default=0, server_default="0", comment="是否已通知学生：1是/0否")
    close_time = Column(DateTime, nullable=True, comment="关闭时间")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
