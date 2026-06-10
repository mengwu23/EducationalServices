from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from backend.app.database import Base


class EmployeeDailyReport(Base):
    __tablename__ = "employee_daily_report"
    __table_args__ = (
        UniqueConstraint("employee_id", "report_date", name="uk_daily_report_employee_date"),
        Index("idx_daily_report_department", "department_id"),
        Index("idx_daily_report_date", "report_date"),
        {"comment": "员工日报表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="员工日报ID")
    employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=False, comment="员工ID")
    department_id = Column(BigInteger, ForeignKey("sys_department.id"), nullable=True, comment="所属部门ID")
    report_date = Column(Date, nullable=False, comment="日报日期")
    raw_content = Column(Text, nullable=False, comment="原始口述或输入内容")
    summary = Column(Text, nullable=True, comment="AI摘要")
    key_progress = Column(Text, nullable=True, comment="关键进展")
    risks = Column(Text, nullable=True, comment="风险与问题")
    tomorrow_plan = Column(Text, nullable=True, comment="明日计划")
    report_status = Column(String(20), nullable=False, default="submitted", server_default="submitted", comment="状态：draft草稿/submitted已提交/archived已归档")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
