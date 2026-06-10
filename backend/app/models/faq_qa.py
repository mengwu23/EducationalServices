from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.database import Base


class FaqQa(Base):
    __tablename__ = "faq_qa"
    __table_args__ = (
        Index("idx_faq_scope", "module_scope"),
        Index("idx_faq_category", "category"),
        Index("idx_faq_status", "status"),
        {"comment": "FAQ标准问答表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="FAQ ID")
    module_scope = Column(String(50), nullable=False, comment="适用模块：customer_service/enterprise_assistant/student_assistant/common")
    category = Column(String(100), nullable=True, comment="问题分类")
    question = Column(String(800), nullable=False, comment="标准问题")
    answer = Column(Text, nullable=False, comment="标准答案")
    keywords = Column(String(500), nullable=True, comment="关键词")
    status = Column(String(20), nullable=False, default="enabled", server_default="enabled", comment="状态：enabled启用/disabled停用")
    sort_order = Column(Integer, nullable=False, default=0, server_default="0", comment="排序号")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
