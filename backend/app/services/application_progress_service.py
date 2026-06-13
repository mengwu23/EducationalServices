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

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.common.exceptions import NotFoundException, BadRequestError
from backend.app.daos.application_progress_dao import ApplicationProgressDao
from backend.app.models.crm_lead import CrmLead
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

    def sync_from_crm(
        self,
        crm_system: str,
        crm_record_id: Optional[str],
        student_id: Optional[int] = None,
        progress_stage: Optional[str] = None,
        progress_status: Optional[str] = None,
        progress_desc: Optional[str] = None,
    ) -> dict:
        """从现有客户线索表同步生成/更新学生申请进度。"""
        lead = self._get_crm_lead(crm_record_id)
        student = self._resolve_student_for_lead(lead, student_id)

        stage = progress_stage or "school_apply"
        status = progress_status or self._map_lead_status_to_progress_status(lead.status)
        if stage not in self.VALID_STAGES:
            raise BadRequestError(f"Invalid stage: {stage}")
        if status not in self.VALID_STATUSES:
            raise BadRequestError(f"Invalid status: {status}")

        now = datetime.now()
        normalized_crm_record_id = self._normalized_crm_record_id(lead)
        update_kwargs = {
            "student_id": student.id,
            "progress_stage": stage,
            "target_country": lead.target_country or student.target_country,
            "school_name": lead.school_name,
            "program_name": lead.target_program,
            "progress_status": status,
            "progress_desc": progress_desc or self._build_progress_desc_from_lead(lead),
            "handler_employee_id": lead.owner_employee_id or student.counselor_employee_id,
            "crm_record_id": normalized_crm_record_id,
            "crm_sync_status": "synced",
            "crm_last_sync_time": now,
        }

        progress = (
            self.dao.get_by_crm_record_id(normalized_crm_record_id)
            or self.dao.get_by_crm_record_id(str(crm_record_id))
        )
        action = "updated"
        if progress is None:
            progress = self.dao.create(**update_kwargs)
            action = "created"
        else:
            progress = self.dao.update(progress.id, **update_kwargs)

        self.db.commit()
        return {
            "sync_direction": "to_local",
            "crm_system": crm_system,
            "crm_record_id": normalized_crm_record_id,
            "action": action,
            "lead": self._lead_snapshot(lead),
            "student_id": student.id,
            "progress": self._to_response(progress, student_name=student.student_name),
        }

    def sync_to_crm(
        self,
        progress_id: Optional[int],
        crm_system: str,
        crm_record_id: Optional[str] = None,
    ) -> dict:
        """将本地申请进度回写到现有客户线索表。"""
        if progress_id is None:
            raise BadRequestError("progress_id is required when sync_direction=to_crm")

        progress = self.dao.get_by_id(progress_id)
        if progress is None:
            raise NotFoundException("Progress record not found")

        lead_record_id = crm_record_id or progress.crm_record_id
        lead = self._get_crm_lead(lead_record_id)

        now = datetime.now()
        summary = self._build_follow_up_summary(progress)
        lead.latest_follow_up_summary = summary
        lead.follow_up_history = self._append_follow_up_history(lead.follow_up_history, summary, now)
        lead.last_follow_up_time = now
        if progress.target_country:
            lead.target_country = progress.target_country
        if progress.program_name:
            lead.target_program = progress.program_name
        if progress.handler_employee_id:
            lead.owner_employee_id = progress.handler_employee_id
        if lead.status == "new":
            lead.status = "following"

        normalized_crm_record_id = self._normalized_crm_record_id(lead)
        progress = self.dao.update(
            progress.id,
            crm_record_id=normalized_crm_record_id,
            crm_sync_status="synced",
            crm_last_sync_time=now,
        )

        self.db.commit()
        return {
            "sync_direction": "to_crm",
            "crm_system": crm_system,
            "crm_record_id": normalized_crm_record_id,
            "action": "updated",
            "lead": self._lead_snapshot(lead),
            "progress": self._to_response(progress),
        }

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
            crm_record_id=getattr(progress, "crm_record_id", None),
            crm_sync_status=getattr(progress, "crm_sync_status", None),
            crm_last_sync_time=getattr(progress, "crm_last_sync_time", None),
            create_time=progress.create_time,
            update_time=progress.update_time,
        )

    def _get_crm_lead(self, crm_record_id: Optional[str]) -> CrmLead:
        if not crm_record_id:
            raise BadRequestError("crm_record_id is required")

        record_id = str(crm_record_id).strip()
        query = self.db.query(CrmLead).filter(CrmLead.is_delete == 0)
        lead = None
        if record_id.isdigit():
            lead = query.filter(CrmLead.id == int(record_id)).first()
        if lead is None:
            lead = query.filter(CrmLead.lead_no == record_id).first()
        if lead is None:
            raise NotFoundException(f"CRM lead not found: {crm_record_id}")
        return lead

    def _resolve_student_for_lead(self, lead: CrmLead, student_id: Optional[int]) -> StudentProfile:
        if student_id is not None:
            student = self._get_student(student_id)
            if student is None:
                raise NotFoundException("Student not found")
            return student

        filters = []
        if lead.phone:
            filters.append(StudentProfile.phone == lead.phone)
        if lead.email:
            filters.append(StudentProfile.email == lead.email)
        if lead.customer_name:
            filters.append(StudentProfile.student_name == lead.customer_name)

        for condition in filters:
            student = self.db.query(StudentProfile).filter(
                condition,
                StudentProfile.is_delete == 0,
            ).first()
            if student is not None:
                return student

        student = StudentProfile(
            student_no=self._next_crm_student_no(lead),
            student_name=lead.customer_name,
            phone=lead.phone,
            email=lead.email,
            current_school=lead.school_name,
            current_grade=lead.current_grade,
            target_country=lead.target_country,
            target_program=lead.target_program,
            counselor_employee_id=lead.owner_employee_id,
            teacher_employee_id=lead.owner_employee_id,
        )
        if self.db.get_bind().dialect.name == "sqlite":
            student.id = (self.db.query(func.max(StudentProfile.id)).scalar() or 0) + 1
        self.db.add(student)
        self.db.flush()
        return student

    def _next_crm_student_no(self, lead: CrmLead) -> str:
        raw_base = f"CRM-{lead.lead_no or lead.id}"
        base = raw_base[:45]
        candidate = base
        suffix = 1
        while self.db.query(StudentProfile).filter(StudentProfile.student_no == candidate).first() is not None:
            suffix += 1
            candidate = f"{base}-{suffix}"[:50]
        return candidate

    @staticmethod
    def _normalized_crm_record_id(lead: CrmLead) -> str:
        return str(lead.id)

    @staticmethod
    def _map_lead_status_to_progress_status(lead_status: str) -> str:
        mapping = {
            "new": "pending",
            "following": "processing",
            "signed": "processing",
            "lost": "blocked",
            "invalid": "blocked",
        }
        return mapping.get(lead_status, "processing")

    @staticmethod
    def _build_progress_desc_from_lead(lead: CrmLead) -> str:
        parts = [f"由客户线索 {lead.lead_no} 同步生成"]
        if lead.latest_follow_up_summary:
            parts.append(f"最近跟进：{lead.latest_follow_up_summary}")
        if lead.background_info:
            parts.append(f"客户背景：{lead.background_info}")
        return "；".join(parts)

    def _build_follow_up_summary(self, progress) -> str:
        stage_label = PROGRESS_STAGES.get(progress.progress_stage, progress.progress_stage)
        status_label = PROGRESS_STATUSES.get(progress.progress_status, progress.progress_status)
        student_name = self._get_student_name(progress.student_id) or f"学生{progress.student_id}"
        summary = f"{student_name}申请进度更新：{stage_label} - {status_label}"
        if progress.school_name:
            summary += f"，院校：{progress.school_name}"
        if progress.program_name:
            summary += f"，项目：{progress.program_name}"
        if progress.progress_desc:
            summary += f"，说明：{progress.progress_desc}"
        return summary

    @staticmethod
    def _append_follow_up_history(history: Optional[str], summary: str, sync_time: datetime) -> str:
        item = f"[{sync_time.strftime('%Y-%m-%d %H:%M:%S')}] {summary}"
        if not history:
            return item
        return f"{history}\n{item}"

    @staticmethod
    def _lead_snapshot(lead: CrmLead) -> dict:
        return {
            "id": lead.id,
            "lead_no": lead.lead_no,
            "customer_name": lead.customer_name,
            "phone": lead.phone,
            "email": lead.email,
            "status": lead.status,
            "target_country": lead.target_country,
            "target_program": lead.target_program,
            "owner_employee_id": lead.owner_employee_id,
            "latest_follow_up_summary": lead.latest_follow_up_summary,
        }

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
