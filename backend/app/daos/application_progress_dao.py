"""
学生申请进度追踪 — 数据访问层（DAO）
====================================

封装所有数据库查询和写入操作，不包含业务逻辑。
事务由 Service 层管理。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.app.models.student_application_progress import StudentApplicationProgress


class ApplicationProgressDao:
    """学生申请进度数据访问类。"""

    def __init__(self, db: Session):
        self.db = db

    # ── 单条查询 ──

    def get_by_id(self, progress_id: int) -> Optional[StudentApplicationProgress]:
        return self.db.query(StudentApplicationProgress).filter(
            StudentApplicationProgress.id == progress_id,
            StudentApplicationProgress.is_delete == 0,
        ).first()

    def get_by_crm_record_id(self, crm_record_id: str) -> Optional[StudentApplicationProgress]:
        return self.db.query(StudentApplicationProgress).filter(
            StudentApplicationProgress.crm_record_id == crm_record_id,
            StudentApplicationProgress.is_delete == 0,
        ).order_by(desc(StudentApplicationProgress.update_time)).first()

    # ── 写入 ──

    def create(self, **kwargs) -> StudentApplicationProgress:
        if "id" not in kwargs and self.db.get_bind().dialect.name == "sqlite":
            next_id = (self.db.query(func.max(StudentApplicationProgress.id)).scalar() or 0) + 1
            kwargs["id"] = next_id
        progress = StudentApplicationProgress(**kwargs)
        self.db.add(progress)
        self.db.flush()
        return progress

    def update(self, progress_id: int, **kwargs) -> Optional[StudentApplicationProgress]:
        progress = self.get_by_id(progress_id)
        if progress is None:
            return None
        for field, value in kwargs.items():
            setattr(progress, field, value)
        self.db.flush()
        return progress

    # ── 列表查询 ──

    def list_by_student(
        self,
        student_id: int,
        page: int = 1,
        page_size: int = 20,
        progress_stage: Optional[str] = None,
        progress_status: Optional[str] = None,
    ) -> tuple[list[StudentApplicationProgress], int]:
        filters = [
            StudentApplicationProgress.student_id == student_id,
            StudentApplicationProgress.is_delete == 0,
        ]
        if progress_stage:
            filters.append(StudentApplicationProgress.progress_stage == progress_stage)
        if progress_status:
            filters.append(StudentApplicationProgress.progress_status == progress_status)

        q = self.db.query(StudentApplicationProgress).filter(*filters)
        total = q.count()
        items = q.order_by(
            desc(StudentApplicationProgress.update_time)
        ).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        student_id: Optional[int] = None,
        progress_stage: Optional[str] = None,
        progress_status: Optional[str] = None,
        handler_employee_id: Optional[int] = None,
    ) -> tuple[list[StudentApplicationProgress], int]:
        filters = [StudentApplicationProgress.is_delete == 0]
        if student_id is not None:
            filters.append(StudentApplicationProgress.student_id == student_id)
        if progress_stage:
            filters.append(StudentApplicationProgress.progress_stage == progress_stage)
        if progress_status:
            filters.append(StudentApplicationProgress.progress_status == progress_status)
        if handler_employee_id is not None:
            filters.append(StudentApplicationProgress.handler_employee_id == handler_employee_id)

        q = self.db.query(StudentApplicationProgress).filter(*filters)
        total = q.count()
        items = q.order_by(
            desc(StudentApplicationProgress.update_time)
        ).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    # ── 时间线查询 ──

    def get_timeline(self, student_id: int) -> list[StudentApplicationProgress]:
        """查询学生各阶段最新进度（按阶段分组取最新一条）。"""
        from sqlalchemy import and_

        # 获取该学生所有未删除的进度记录，按阶段分组取最新
        subq = (
            self.db.query(
                StudentApplicationProgress.progress_stage,
                StudentApplicationProgress.id,
            )
            .filter(
                StudentApplicationProgress.student_id == student_id,
                StudentApplicationProgress.is_delete == 0,
            )
            .order_by(
                StudentApplicationProgress.progress_stage,
                StudentApplicationProgress.update_time.desc(),
            )
            .subquery()
        )

        # 每个阶段取第一条（最新的）
        items = (
            self.db.query(StudentApplicationProgress)
            .filter(
                StudentApplicationProgress.id.in_(
                    self.db.query(subq.c.id).group_by(subq.c.progress_stage)
                )
            )
            .order_by(desc(StudentApplicationProgress.update_time))
            .all()
        )

        # 如果没有记录，返回简单按阶段排序的结果
        if not items:
            items = (
                self.db.query(StudentApplicationProgress)
                .filter(
                    StudentApplicationProgress.student_id == student_id,
                    StudentApplicationProgress.is_delete == 0,
                )
                .order_by(desc(StudentApplicationProgress.update_time))
                .all()
            )

        return items

    # ── 统计 ──

    def count_by_stage(self, student_id: int) -> dict[str, int]:
        """按阶段统计学生的进度记录数。"""
        from sqlalchemy import func
        rows = (
            self.db.query(
                StudentApplicationProgress.progress_stage,
                func.count(StudentApplicationProgress.id),
            )
            .filter(
                StudentApplicationProgress.student_id == student_id,
                StudentApplicationProgress.is_delete == 0,
            )
            .group_by(StudentApplicationProgress.progress_stage)
            .all()
        )
        return {stage: count for stage, count in rows}

    def count_blocked(self) -> int:
        """统计受阻的进度总数（用于管理概览）。"""
        return self.db.query(StudentApplicationProgress).filter(
            StudentApplicationProgress.progress_status == "blocked",
            StudentApplicationProgress.is_delete == 0,
        ).count()
