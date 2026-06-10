from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func

from backend.app.database import Base


class CustomerAnalysisRecord(Base):
    __tablename__ = "customer_analysis_record"
    __table_args__ = (
        CheckConstraint("match_score IS NULL OR (match_score >= 0 AND match_score <= 100)", name="chk_analysis_match_score"),
        UniqueConstraint("analysis_no", name="uk_analysis_no"),
        Index("idx_analysis_lead_id", "lead_id"),
        Index("idx_analysis_status", "status"),
        Index("idx_analysis_score", "match_score"),
        {"comment": "客户研判记录表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="客户研判记录ID")
    analysis_no = Column(String(50), nullable=False, comment="研判编号")
    source_type = Column(String(30), nullable=False, comment="来源类型：text文本/pdf简历/excel表格/manual手工录入")
    source_file_name = Column(String(300), nullable=True, comment="来源文件名")
    raw_content = Column(LONGTEXT, nullable=True, comment="待研判原始内容")
    target_product = Column(String(100), nullable=True, comment="研判目标产品或服务")
    lead_id = Column(BigInteger, ForeignKey("crm_lead.id"), nullable=True, comment="关联意向客户ID")
    is_target_customer = Column(Integer, nullable=True, comment="是否符合目标客户画像：1是/0否，未研判为空")
    match_score = Column(Numeric(5, 2), nullable=True, comment="匹配分数0-100")
    match_level = Column(String(30), nullable=True, comment="匹配等级：high高/medium中/low低")
    reason_summary = Column(Text, nullable=True, comment="研判理由摘要")
    suggestion = Column(Text, nullable=True, comment="后续跟进建议")
    status = Column(String(30), nullable=False, default="pending", server_default="pending", comment="状态：pending待研判/completed已完成/failed失败")
    submitter_user_id = Column(BigInteger, ForeignKey("sys_user.id"), nullable=True, comment="提交人用户ID")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
