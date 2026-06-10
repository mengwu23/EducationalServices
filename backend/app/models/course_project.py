"""课程与项目目录表实体。"""

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.sql import func

from ..database import Base


class CourseProject(Base):
    """描述可以推荐给客户的课程、服务或项目。"""
    __tablename__ = "course_project"
    __table_args__ = (
        Index("idx_project_type", "project_type"),
        Index("idx_project_country", "target_country"),
        Index("idx_project_status", "status"),
        {"comment": "课程与项目表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="课程项目ID")
    project_name = Column(String(200), nullable=False, comment="课程或项目名称")
    project_type = Column(String(50), nullable=False, comment="项目类型：language语言培训/background背景提升/application留学申请/upgrade学历提升")
    target_country = Column(String(100), nullable=True, comment="适用国家")
    target_education_level = Column(String(100), nullable=True, comment="适用学历阶段")
    target_audience = Column(String(500), nullable=True, comment="适合人群")
    project_desc = Column(Text, nullable=True, comment="项目详情")
    price_range = Column(String(100), nullable=True, comment="价格区间")
    status = Column(String(20), nullable=False, default="enabled", server_default="enabled", comment="状态：enabled上架/disabled下架")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
