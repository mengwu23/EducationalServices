"""活动与讲座表实体。"""

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class EventLecture(Base):
    """存储讲座或活动流程中使用的基础元数据。"""
    __tablename__ = "event_lecture"
    __table_args__ = (
        UniqueConstraint("event_no", name="uk_event_no"),
        Index("idx_event_start_time", "start_time"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_status", "status"),
        {"comment": "活动与讲座表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="活动讲座ID")
    event_no = Column(String(50), nullable=False, comment="活动编号")
    event_name = Column(String(200), nullable=False, comment="活动名称")
    event_type = Column(String(30), nullable=False, comment="活动类型：online线上/offline线下")
    topic = Column(String(300), nullable=True, comment="活动主题")
    speaker = Column(String(200), nullable=True, comment="主讲人")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    location = Column(String(300), nullable=True, comment="线下地点")
    online_url = Column(String(500), nullable=True, comment="线上链接")
    max_participants = Column(Integer, nullable=True, comment="最大报名人数")
    current_participants = Column(Integer, nullable=False, default=0, server_default="0", comment="当前报名人数")
    status = Column(String(30), nullable=False, default="open", server_default="open", comment="活动状态：open报名中/full已满/closed已结束/cancelled已取消")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
