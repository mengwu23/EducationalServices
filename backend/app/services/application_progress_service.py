"""
学生申请进度追踪 — 业务逻辑层（Service）
========================================

负责：
1. 业务规则校验（阶段/状态合法性）
2. 关联数据组装（学生姓名、负责人姓名）
3. 时间线生成
4. 事务管理

CRM 集成预留：
    - crm_sync_status / crm_record_id 字段已在模型中预留
    - sync_from_crm() / sync_to_crm() 方法已预留签名
    - 待 CRM 系统合并后实现具体同步逻辑
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.common.exceptions import NotFoundException, BadRequestError
from backend.app.daos.application_progress_dao import ApplicationProgressDao
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.student_profile import StudentProfile
from backend.app.models.sys_user import SysUser
from backend.app.schemas.application_progress_schema import (
    PROGRESS_STAGES,
    PROGRESS_STATUSES,
    ProgressCreateRequest,
    ProgressListResponse,
    ProgressResponse,
    ProgressTimelineItem,
    ProgressTimelineResponse,
    ProgressUpdateRequest,
    StagesReferenceResponse,
)


class ApplicationProgressService:
    """学生申请进度业务服务。"""

    VALID_STAGES = set(PROGRESS_STAGES.keys())
    VALID_STATUSES = set(PROGRESS_STATUSES.keys())

    def __init__(self, db: Session):
        self.db = db
        self.dao = ApplicationProgressDao(db)

    # ── 创建进度 ──

    def create_progress(self, data: ProgressCreateRequest) -> ProgressResponse:
        if data.progress_stage not in self.VALID_STAGES:
            raise BadRequestError(f"Invalid stage: {data.progress_stage}")
        if data.progress_status not in self.VALID_STATUSES:
            raise BadRequestError(f"Invalid status: {data.progress_status}")

        student = self._get_student(data.student_id)
        if student is None:
            raise NotFoundException("Student not found")

        progress = self.dao.create(
            student_id=data.student_id,
            progress_stage=data.progress_stage,
            target_country=data.target_country,
            school_name=data.school_name,
            program_name=data.program_name,
            progress_status=data.progress_status,
            progress_desc=data.progress_desc,
            handler_employee_id=data.handler_employee_id,
            expected_finish_time=data.expected_finish_time,
        )
        self.db.commit()
        return self._to_response(progress, student_name=student.student_name)

    # ── 查询进度列表 ──

    def list_progress(
        self,
        student_id: Optional[int] = None,
        progress_stage: Optional[str] = None,
        progress_status: Optional[str] = None,
        handler_employee_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProgressResponse], int]:
        items, total = self.dao.list_all(
            student_id=student_id,
            progress_stage=progress_stage,
            progress_status=progress_status,
            handler_employee_id=handler_employee_id,
            page=page,
            page_size=page_size,
        )
        results = [self._to_response(item) for item in items]
        return results, total

    # ── 学生查看自己的进度 ──

    def list_my_progress(
        self,
        student_user_id: int,
        page: int = 1,
        page_size: int = 20,
        progress_stage: Optional[str] = None,
        progress_status: Optional[str] = None,
    ) -> tuple[list[ProgressResponse], int]:
        student = self._get_student_by_user_id(student_user_id)
        if student is None:
            raise NotFoundException("Student profile not found")

        items, total = self.dao.list_by_student(
            student_id=student.id,
            page=page,
            page_size=page_size,
            progress_stage=progress_stage,
            progress_status=progress_status,
        )
        results = [self._to_response(item, student_name=student.student_name) for item in items]
        return results, total

    # ── 获取详情 ──

    def get_progress(self, progress_id: int) -> ProgressResponse:
        progress = self.dao.get_by_id(progress_id)
        if progress is None:
            raise NotFoundException("Progress record not found")
        return self._to_response(progress)

    # ── 更新进度 ──

    def update_progress(self, progress_id: int, data: ProgressUpdateRequest) -> ProgressResponse:
        progress = self.dao.get_by_id(progress_id)
        if progress is None:
            raise NotFoundException("Progress record not found")

        update_kwargs = {}
        if data.progress_stage is not None:
            if data.progress_stage not in self.VALID_STAGES:
                raise BadRequestError(f"Invalid stage: {data.progress_stage}")
            update_kwargs["progress_stage"] = data.progress_stage
        if data.progress_status is not None:
            if data.progress_status not in self.VALID_STATUSES:
                raise BadRequestError(f"Invalid status: {data.progress_status}")
            update_kwargs["progress_status"] = data.progress_status
        for field in ("target_country", "school_name", "program_name",
                       "progress_desc", "handler_employee_id", "expected_finish_time"):
            val = getattr(data, field)
            if val is not None:
                update_kwargs[field] = val

        progress = self.dao.update(progress_id, **update_kwargs)
        self.db.commit()
        return self._to_response(progress)

    # ── 时间线 ──

    def get_timeline(self, student_user_id: int) -> ProgressTimelineResponse:
        student = self._get_student_by_user_id(student_user_id)
        if student is None:
            raise NotFoundException("Student profile not found")

        items = self.dao.get_timeline(student.id)
        stage_count = self.dao.count_by_stage(student.id)

        timeline = []
        for item in items:
            timeline.append(ProgressTimelineItem(
                id=item.id,
                stage=item.progress_stage,
                stage_label=PROGRESS_STAGES.get(item.progress_stage, item.progress_stage),
                status=item.progress_status,
                status_label=PROGRESS_STATUSES.get(item.progress_status, item.progress_status),
                desc=item.progress_desc,
                handler_name=self._get_employee_name(item.handler_employee_id),
                school_name=item.school_name,
                expected_finish_time=item.expected_finish_time,
                update_time=item.update_time,
            ))

        # 生成概览
        completed = stage_count.get("completed", 0) if hasattr(self, '_dummy') else sum(
            1 for t in timeline if t.status == "completed"
        )
        blocked = sum(1 for t in timeline if t.status == "blocked")
        total_stages = len(timeline)

        summary_parts = [f"共 {total_stages} 个阶段"]
        if completed > 0:
            summary_parts.append(f"{completed} 个已完成")
        if blocked > 0:
            summary_parts.append(f"{blocked} 个受阻")

        return ProgressTimelineResponse(
            student_id=student.id,
            student_name=student.student_name,
            stages=timeline,
            summary="，".join(summary_parts),
        )

    # ── 参考数据 ──

    @staticmethod
    def get_stages_reference() -> StagesReferenceResponse:
        return StagesReferenceResponse(
            stages=PROGRESS_STAGES,
            statuses=PROGRESS_STATUSES,
        )

    # ── 受阻统计 ──

    def count_blocked(self) -> int:
        return self.dao.count_blocked()

    # ══════════════════════════════════════════════════════════
    # CRM 集成预留（待 CRM 系统合并后实现）
    # ══════════════════════════════════════════════════════════

    def sync_from_crm(self, crm_system: str, crm_record_id: str) -> dict:
        """从 CRM 系统拉取进度数据（预留）。

        TODO: 接入 CRM 后实现：
        1. 根据 crm_system 选择对应的 CRM 适配器
        2. 通过 crm_record_id 查询 CRM 系统中的申请进度
        3. 将 CRM 数据映射为本地 StudentApplicationProgress 记录
        4. 更新 crm_sync_status = 'synced'
        """
        raise NotImplementedError(
            f"CRM integration not yet implemented. "
            f"System={crm_system}, record_id={crm_record_id}"
        )

    def sync_to_crm(self, progress_id: int, crm_system: str) -> dict:
        """将本地进度数据推送到 CRM 系统（预留）。

        TODO: 接入 CRM 后实现：
        1. 查询本地进度记录
        2. 根据 crm_system 选择对应的 CRM 适配器
        3. 将本地数据映射为 CRM 系统的字段格式
        4. 推送并更新本地 crm_sync_status = 'synced'
        """
        raise NotImplementedError(
            f"CRM integration not yet implemented. "
            f"Progress={progress_id}, system={crm_system}"
        )

    # ── 私有辅助 ──

    def _to_response(
        self, progress, student_name: Optional[str] = None,
    ) -> ProgressResponse:
        if student_name is None:
            student_name = self._get_student_name(progress.student_id)
        handler_name = self._get_employee_name(progress.handler_employee_id)

        return ProgressResponse(
            id=progress.id,
            student_id=progress.student_id,
            student_name=student_name,
            progress_stage=progress.progress_stage,
            progress_stage_label=PROGRESS_STAGES.get(progress.progress_stage),
            target_country=progress.target_country,
            school_name=progress.school_name,
            program_name=progress.program_name,
            progress_status=progress.progress_status,
            progress_status_label=PROGRESS_STATUSES.get(progress.progress_status),
            progress_desc=progress.progress_desc,
            handler_employee_id=progress.handler_employee_id,
            handler_name=handler_name,
            expected_finish_time=progress.expected_finish_time,
            # CRM 预留字段 — 当前返回 None
            crm_record_id=None,
            crm_sync_status=None,
            crm_last_sync_time=None,
            create_time=progress.create_time,
            update_time=progress.update_time,
        )

    def _get_student(self, student_id: int) -> Optional[StudentProfile]:
        return self.db.query(StudentProfile).filter(
            StudentProfile.id == student_id,
            StudentProfile.is_delete == 0,
        ).first()

    def _get_student_by_user_id(self, user_id: int) -> Optional[StudentProfile]:
        return self.db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id,
            StudentProfile.is_delete == 0,
        ).first()

    def _get_student_name(self, student_id: int) -> Optional[str]:
        student = self._get_student(student_id)
        return student.student_name if student else None

    def _get_employee_name(self, employee_id: Optional[int]) -> Optional[str]:
        if employee_id is None:
            return None
        emp = self.db.query(EmployeeProfile).filter(
            EmployeeProfile.id == employee_id,
            EmployeeProfile.is_delete == 0,
        ).first()
        if emp is None:
            return None
        user = self.db.query(SysUser).filter(SysUser.id == emp.user_id).first()
        return user.real_name if user else emp.employee_name
