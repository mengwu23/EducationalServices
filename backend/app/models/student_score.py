"""学生成绩表实体。"""

from sqlalchemy import BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.sql import func

from ..database import Base


class StudentScore(Base):
    """存储成绩、考试信息及录入责任人。"""
    __tablename__ = "student_score"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="chk_student_score_range"),
        Index("idx_score_student_id", "student_id"),
        Index("idx_score_course_name", "course_name"),
        Index("idx_score_semester", "semester"),
        Index("idx_score_exam_date", "exam_date"),
        {"comment": "学生成绩表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="学生成绩ID")
    student_id = Column(BigInteger, ForeignKey("student_profile.id"), nullable=False, comment="学生ID")
    course_name = Column(String(200), nullable=False, comment="课程名称")
    score = Column(Numeric(5, 2), nullable=False, comment="成绩分数")
    exam_type = Column(String(50), nullable=True, comment="考试类型：daily平时/midterm期中/final期末/makeup补考/other其他")
    semester = Column(String(100), nullable=True, comment="学期")
    exam_date = Column(Date, nullable=True, comment="考试日期")
    operator_employee_id = Column(BigInteger, ForeignKey("employee_profile.id"), nullable=True, comment="录入员工ID")
    remark = Column(String(500), nullable=True, comment="备注")
    is_delete = Column(Integer, nullable=False, default=0, server_default="0", comment="软删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
