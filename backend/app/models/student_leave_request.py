"""学生请假申请表实体。"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class StudentLeaveRequest(Base):
    """存储学生请假申请及审批结果。"""
    __tablename__ = "student_leave_request"
    __table_args__ = (
        UniqueConstraint("request_no", name="uk_leave_request_no"),
        Index("idx_leave_student_id", "student_id"),
        Index("idx_leave_status", "status"),
        Index("idx_leave_approver", "approver_employee_id"),
        {"comment": "学生请假申请表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="请假申请ID")
    request_no = Column(String(50), nullable=False, comment="请假单号")
    student_id = Column(BigInteger, ForeignKey("student_profile.id"), nullable=False, comment="学生ID")
    leave_type = Column(String(50), nullable=False, comment="请假类型：sick病假/personal事假/other其他")
    reason = Column(Text, nullable=False, comment="请假原因")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    status = Column(String(30), nullable=False, default="pending", server_default="pending", comment="审批状态：pending待审批/approved已通过/rejected已驳回/cancelled已撤销")
    approver_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="审批员工ID")
    approval_comment = Column(String(1000), nullable=True, comment="审批意见")
    approve_time = Column(DateTime, nullable=True, comment="审批时间")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
