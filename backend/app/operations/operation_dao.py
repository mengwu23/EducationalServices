"""企业业务办理助手的数据访问层。

提供草稿管理、客户线索写入等操作。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.common.enums import DraftStatus
from backend.app.models.crm_lead import CrmLead
from backend.app.models.draft import AiDraft
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.audit_log import AuditLog


class OperationDao:
    """封装业务办理助手的所有数据库操作。"""

    def __init__(self, db: Session):
        self.db = db

    # ======== AiDraft 操作 ========

    def create_draft(
        self,
        intent: str,
        content_json: Dict[str, Any],
        created_by: Optional[int] = None,
        status: str = DraftStatus.GENERATING,
    ) -> AiDraft:
        """创建操作草稿。"""
        draft = AiDraft(
            draft_no=f"OP-{datetime.now():%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
            draft_type="business_operation",
            biz_module="enterprise_operation",
            status=status,
            content_json=content_json,
            created_by=created_by,
        )
        self.db.add(draft)
        self.db.flush()
        return draft

    def get_draft(self, draft_id: int) -> Optional[AiDraft]:
        """获取草稿。"""
        stmt = select(AiDraft).where(AiDraft.id == draft_id, AiDraft.is_deleted.is_(False))
        return self.db.scalar(stmt)

    def update_draft_content(self, draft: AiDraft, content_json: Dict[str, Any]) -> AiDraft:
        """更新草稿内容。"""
        draft.content_json = content_json
        self.db.flush()
        return draft

    def update_draft_status(
        self,
        draft: AiDraft,
        status: str,
        confirmed_by: Optional[int] = None,
        reject_reason: Optional[str] = None,
    ) -> AiDraft:
        """更新草稿状态。"""
        draft.status = status
        if confirmed_by is not None:
            draft.confirmed_by = confirmed_by
            draft.confirmed_time = datetime.now()
        if reject_reason is not None:
            draft.reject_reason = reject_reason
        self.db.flush()
        return draft

    # ======== CrmLead 操作 ========

    def generate_lead_no(self) -> str:
        """生成线索编号。"""
        now = datetime.now()
        return f"LEAD-{now:%Y%m%d%H%M%S}-{uuid4().hex[:6].upper()}"

    def find_leads_by_phone(self, phone: str) -> List[CrmLead]:
        """按手机号查找已有客户（活跃 + 软删除均查）。"""
        stmt = select(CrmLead).where(CrmLead.phone == phone, CrmLead.is_delete == 0)
        return list(self.db.scalars(stmt).all())

    def find_leads_by_name(self, name: str) -> List[CrmLead]:
        """按姓名模糊查找已有客户。"""
        stmt = (
            select(CrmLead)
            .where(CrmLead.customer_name.like(f"%{name}%"), CrmLead.is_delete == 0)
            .order_by(CrmLead.create_time.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_employee_by_user_id(self, user_id: int) -> Optional[EmployeeProfile]:
        """根据用户 ID 查找员工档案。"""
        stmt = select(EmployeeProfile).where(
            EmployeeProfile.user_id == user_id,
            EmployeeProfile.is_delete == 0,
            EmployeeProfile.status == "active",
        )
        return self.db.scalar(stmt)

    def _next_lead_id(self) -> int:
        """获取下一个可用 ID（兼容 SQLite 不支持 BigInt 自增的场景）。"""
        max_id = self.db.query(func.max(CrmLead.id)).scalar()
        return (max_id or 0) + 1

    def create_lead(self, params: Dict[str, Any], owner_employee_id: Optional[int]) -> CrmLead:
        """创建客户线索。"""
        lead = CrmLead(
            id=self._next_lead_id(),
            lead_no=self.generate_lead_no(),
            customer_name=params.get("customer_name", ""),
            phone=params.get("phone"),
            wechat_no=params.get("wechat_no"),
            email=params.get("email"),
            source_channel=params.get("source_channel"),
            education_level=params.get("education_level"),
            school_name=params.get("school_name"),
            major=params.get("major"),
            current_grade=params.get("current_grade"),
            target_country=params.get("target_country"),
            target_program=params.get("target_program"),
            budget_range=params.get("budget_range"),
            background_info=params.get("background_info"),
            status="new",
            owner_employee_id=owner_employee_id,
        )
        self.db.add(lead)
        self.db.flush()
        return lead

    # ======== 审计日志 ========

    def add_audit_log(
        self,
        operator_user_id: int,
        action_type: str,
        biz_module: str,
        biz_object_type: str,
        biz_object_id: Optional[int],
        after_json: Optional[Dict[str, Any]] = None,
        draft_id: Optional[int] = None,
    ) -> AuditLog:
        """记录操作审计日志。"""
        log = AuditLog(
            operator_user_id=operator_user_id,
            action_type=action_type,
            biz_module=biz_module,
            biz_object_type=biz_object_type,
            biz_object_id=biz_object_id,
            after_json=after_json,
            draft_id=draft_id,
        )
        self.db.add(log)
        self.db.flush()
        return log

    # ======== 员工查询 ========

    def get_employee_name_by_id(self, employee_id: int) -> Optional[str]:
        """根据员工ID查询姓名。"""
        stmt = select(EmployeeProfile.employee_name).where(EmployeeProfile.id == employee_id)
        return self.db.scalar(stmt)

    # ======== 请假操作 ========

    def find_pending_leaves_by_approver(self, approver_employee_id: int) -> List:
        """查询某审批人的待审批请假。"""
        from backend.app.models.student_leave_request import StudentLeaveRequest
        from backend.app.models.student_profile import StudentProfile
        stmt = (
            select(StudentLeaveRequest, StudentProfile.student_name)
            .join(StudentProfile, StudentLeaveRequest.student_id == StudentProfile.id)
            .where(StudentLeaveRequest.status == "pending", StudentLeaveRequest.is_delete == 0)
            .order_by(StudentLeaveRequest.create_time.asc())
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], row[1]) for row in rows]

    def find_pending_leave_by_student_name(self, student_name: str) -> List:
        """按学生名查找待审批请假。"""
        from backend.app.models.student_leave_request import StudentLeaveRequest
        from backend.app.models.student_profile import StudentProfile
        stmt = (
            select(StudentLeaveRequest, StudentProfile.student_name)
            .join(StudentProfile, StudentLeaveRequest.student_id == StudentProfile.id)
            .where(
                StudentLeaveRequest.status == "pending",
                StudentLeaveRequest.is_delete == 0,
                StudentProfile.student_name.like(f"%{student_name}%"),
            )
            .order_by(StudentLeaveRequest.create_time.asc())
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], row[1]) for row in rows]

    def approve_leave(self, leave_id: int, status: str, approver_id: int,
                      comment: Optional[str] = None):
        """审批请假。"""
        from datetime import datetime
        from backend.app.models.student_leave_request import StudentLeaveRequest
        from sqlalchemy import select
        stmt = select(StudentLeaveRequest).where(StudentLeaveRequest.id == leave_id)
        leave = self.db.scalar(stmt)
        if not leave:
            return None
        leave.status = status
        leave.approver_employee_id = approver_id
        leave.approve_time = datetime.now()
        if comment:
            leave.approval_comment = comment
        self.db.flush()
        return leave

    # ======== 投诉操作 ========

    def find_feedback_by_handler(self, handler_employee_id: int, statuses: Optional[List[str]] = None) -> List:
        """查询某处理人的投诉反馈。"""
        from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
        from backend.app.models.student_profile import StudentProfile
        query = (
            select(StudentFeedbackTicket, StudentProfile.student_name)
            .join(StudentProfile, StudentFeedbackTicket.student_id == StudentProfile.id)
            .filter(StudentFeedbackTicket.is_delete == 0)
        )
        if statuses:
            query = query.filter(StudentFeedbackTicket.status.in_(statuses))
        rows = self.db.execute(query.order_by(StudentFeedbackTicket.create_time.desc())).all()
        return [(row[0], row[1]) for row in rows]

    def find_feedback_by_student_name(self, student_name: str) -> List:
        """按学生名查找投诉。"""
        from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
        from backend.app.models.student_profile import StudentProfile
        stmt = (
            select(StudentFeedbackTicket, StudentProfile.student_name)
            .join(StudentProfile, StudentFeedbackTicket.student_id == StudentProfile.id)
            .where(
                StudentFeedbackTicket.is_delete == 0,
                StudentProfile.student_name.like(f"%{student_name}%"),
            )
            .order_by(StudentFeedbackTicket.create_time.desc())
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], row[1]) for row in rows]

    def update_feedback(self, ticket_id: int, **kwargs) -> Optional[Any]:
        """更新投诉工单字段。"""
        from datetime import datetime
        from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
        from sqlalchemy import select
        stmt = select(StudentFeedbackTicket).where(StudentFeedbackTicket.id == ticket_id)
        ticket = self.db.scalar(stmt)
        if not ticket:
            return None
        for k, v in kwargs.items():
            if hasattr(ticket, k):
                setattr(ticket, k, v)
        if kwargs.get("status") in ("resolved", "closed"):
            ticket.close_time = datetime.now()
        self.db.flush()
        return ticket

    # ======== 学生操作 ========

    def find_students_by_name(self, name: str) -> List:
        """按姓名查找学生。"""
        from backend.app.models.student_profile import StudentProfile
        stmt = select(StudentProfile).where(
            StudentProfile.student_name.like(f"%{name}%"),
            StudentProfile.is_delete == 0,
        ).order_by(StudentProfile.id.desc())
        return list(self.db.scalars(stmt).all())

    def create_student_score(self, student_id: int, course_name: str, score: float,
                             exam_type=None, semester=None, exam_date=None,
                             remark=None, operator_employee_id=None):
        """创建成绩记录。"""
        from backend.app.models.student_score import StudentScore
        from sqlalchemy import func
        max_id = self.db.query(func.max(StudentScore.id)).scalar()
        next_id = (max_id or 0) + 1
        record = StudentScore(
            id=next_id,
            student_id=student_id,
            course_name=course_name,
            score=score,
            exam_type=exam_type,
            semester=semester,
            exam_date=exam_date,
            operator_employee_id=operator_employee_id,
            remark=remark,
        )
        self.db.add(record)
        self.db.flush()
        return record

    # ======== 日报操作 ========

    def find_today_report(self, employee_id: int, report_date) -> Optional['EmployeeDailyReport']:
        """查询某员工某天的日报。"""
        from backend.app.models.employee_daily_report import EmployeeDailyReport
        stmt = select(EmployeeDailyReport).where(
            EmployeeDailyReport.employee_id == employee_id,
            EmployeeDailyReport.report_date == report_date,
            EmployeeDailyReport.is_delete == 0,
        )
        return self.db.scalar(stmt)

    def _next_report_id(self) -> int:
        """获取下一个日报 ID（兼容 SQLite 不支持 BigInt 自增）。"""
        from backend.app.models.employee_daily_report import EmployeeDailyReport
        max_id = self.db.query(func.max(EmployeeDailyReport.id)).scalar()
        return (max_id or 0) + 1

    def create_daily_report(
        self, employee_id: int, department_id: Optional[int], params: Dict[str, Any]
    ) -> 'EmployeeDailyReport':
        """创建日报。"""
        from datetime import date, datetime
        from backend.app.models.employee_daily_report import EmployeeDailyReport
        raw_date = params.get("report_date", date.today())
        if isinstance(raw_date, str):
            report_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        elif isinstance(raw_date, date):
            report_date = raw_date
        else:
            report_date = date.today()
        report = EmployeeDailyReport(
            id=self._next_report_id(),
            employee_id=employee_id,
            department_id=department_id,
            report_date=report_date,
            raw_content=params.get("raw_content", ""),
            summary=params.get("summary"),
            key_progress=params.get("key_progress"),
            risks=params.get("risks"),
            tomorrow_plan=params.get("tomorrow_plan"),
            report_status="submitted",
        )
        self.db.add(report)
        self.db.flush()
        return report

    def update_daily_report(self, report: 'EmployeeDailyReport', params: Dict[str, Any]) -> 'EmployeeDailyReport':
        """更新已有日报。"""
        report.raw_content = params.get("raw_content", report.raw_content)
        if params.get("summary"):
            report.summary = params["summary"]
        if params.get("key_progress"):
            report.key_progress = params["key_progress"]
        if params.get("risks"):
            report.risks = params["risks"]
        if params.get("tomorrow_plan"):
            report.tomorrow_plan = params["tomorrow_plan"]
        report.report_status = "submitted"
        self.db.flush()
        return report
