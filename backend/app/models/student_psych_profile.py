"""学生心理画像表实体。"""

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class StudentPsychProfile(Base):
    """存储学生长期心理状态画像信息。"""
    __tablename__ = "student_psych_profile"
    __table_args__ = (
        CheckConstraint("emotion_score IS NULL OR (emotion_score >= 0 AND emotion_score <= 100)", name="chk_psych_emotion_score"),
        UniqueConstraint("student_id", name="uk_psych_student_id"),
        Index("idx_psych_risk_level", "risk_level"),
        {"comment": "学生心理健康画像表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="心理健康画像ID")
    student_id = Column(BigInteger, ForeignKey("student_profile.id"), nullable=False, comment="学生ID")
    latest_emotion_tag = Column(String(100), nullable=True, comment="最新情绪标签")
    emotion_score = Column(Integer, nullable=True, comment="情绪分值0-100，越高越积极")
    risk_level = Column(String(30), nullable=False, default="low", server_default="low", comment="风险等级：low低/medium中/high高/critical危急")
    last_interaction_time = Column(DateTime, nullable=True, comment="最近心理相关交互时间")
    emotion_summary = Column(Text, nullable=True, comment="长期情绪摘要")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
