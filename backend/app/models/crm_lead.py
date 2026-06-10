"""客户线索表实体。"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class CrmLead(Base):
    """存储客户身份、负责人以及跟进进度信息。"""
    __tablename__ = "crm_lead"
    __table_args__ = (
        UniqueConstraint("lead_no", name="uk_lead_no"),
        Index("idx_lead_phone", "phone"),
        Index("idx_lead_owner", "owner_employee_id"),
        Index("idx_lead_status", "status"),
        Index("idx_lead_target_country", "target_country"),
        Index("idx_lead_create_time", "create_time"),
        {"comment": "意向客户线索表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="意向客户ID")
    lead_no = Column(String(50), nullable=False, comment="线索编号")
    customer_name = Column(String(100), nullable=False, comment="客户姓名")
    phone = Column(String(30), nullable=True, comment="手机号")
    wechat_no = Column(String(100), nullable=True, comment="微信号")
    email = Column(String(120), nullable=True, comment="邮箱")
    source_channel = Column(String(100), nullable=True, comment="来源渠道")
    education_level = Column(String(100), nullable=True, comment="学历阶段")
    school_name = Column(String(200), nullable=True, comment="学校名称")
    major = Column(String(200), nullable=True, comment="专业")
    current_grade = Column(String(100), nullable=True, comment="当前年级")
    target_country = Column(String(100), nullable=True, comment="意向国家")
    target_program = Column(String(200), nullable=True, comment="意向项目")
    budget_range = Column(String(100), nullable=True, comment="预算区间")
    background_info = Column(Text, nullable=True, comment="客户背景补充信息")
    follow_up_history = Column(Text, nullable=True, comment="前期简化保存历史跟进内容，后续可拆成crm_lead_followup表")
    latest_follow_up_summary = Column(String(1000), nullable=True, comment="最近跟进摘要")
    status = Column(String(30), nullable=False, default="new", server_default="new", comment="线索状态：new新增/following跟进中/signed已签约/lost已流失/invalid无效")
    owner_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="负责员工ID")
    last_follow_up_time = Column(DateTime, nullable=True, comment="最近跟进时间")
    lost_reason = Column(String(500), nullable=True, comment="流失原因")
    signed_time = Column(DateTime, nullable=True, comment="签约时间")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
