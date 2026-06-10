"""活动报名表实体。"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class EventRegistration(Base):
    """存储讲座或活动的访客报名记录。"""
    __tablename__ = "event_registration"
    __table_args__ = (
        Index("idx_registration_event_id", "event_id"),
        Index("idx_registration_lead_id", "lead_id"),
        Index("idx_registration_phone", "visitor_phone"),
        {"comment": "活动报名表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="活动报名ID")
    event_id = Column(BigInteger, ForeignKey("event_lecture.id"), nullable=False, comment="活动ID")
    lead_id = Column(BigInteger, ForeignKey("crm_lead.id"), nullable=True, comment="关联意向客户ID，可为空")
    visitor_name = Column(String(100), nullable=False, comment="报名人姓名")
    visitor_phone = Column(String(30), nullable=True, comment="报名人手机号")
    registration_status = Column(String(30), nullable=False, default="registered", server_default="registered", comment="报名状态：registered已报名/cancelled已取消/attended已参加/no_show未到场")
    remark = Column(String(500), nullable=True, comment="备注")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="报名时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
