"""企业管理查询助手的数据访问层。"""

from datetime import date, datetime, time, timedelta
from typing import Optional, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Query, Session

from ..models.crm_lead import CrmLead
from ..models.employee_daily_report import EmployeeDailyReport
from ..models.employee_profile import EmployeeProfile
from ..models.student_application_progress import StudentApplicationProgress
from ..models.student_feedback_ticket import StudentFeedbackTicket
from ..models.student_leave_request import StudentLeaveRequest
from ..models.student_profile import StudentProfile
from ..models.student_score import StudentScore
from ..models.sys_department import SysDepartment


class EnterpriseAssistantDao:
    """封装企业管理查询助手所有数据库查询。"""

    def __init__(self, db: Session):
        self.db = db

    def paginate(self, query: Query, page: int, page_size: int) -> Tuple[int, list]:
        """对 SQLAlchemy 查询统一分页，返回总数和当前页数据。"""
        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, rows

    def _apply_datetime_range(self, query: Query, column, start_date: Optional[date], end_date: Optional[date]) -> Query:
        """给 datetime 字段追加日期范围条件。"""
        if start_date:
            query = query.filter(column >= datetime.combine(start_date, time.min))
        if end_date:
            query = query.filter(column <= datetime.combine(end_date, time.max))
        return query

    def _active_student_id_query(self, student_name: Optional[str] = None) -> Query:
        """生成未软删除学生子查询，供成绩、请假、反馈、申请进度联动过滤。"""
        query = self.db.query(StudentProfile.id).filter(StudentProfile.is_delete == 0)
        if student_name:
            query = query.filter(StudentProfile.student_name.like(f"%{student_name}%"))
        return query

    def build_lead_query(
        self,
        customer_name: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None,
        target_country: Optional[str] = None,
        owner_employee_id: Optional[int] = None,
        owner_department_id: Optional[int] = None,
        created_start: Optional[date] = None,
        created_end: Optional[date] = None,
        stale_days: Optional[int] = None,
    ) -> Query:
        """构建客户线索查询，过滤软删除数据并补充负责人姓名。"""
        query = (
            self.db.query(CrmLead, EmployeeProfile.employee_name.label("owner_name"))
            .outerjoin(EmployeeProfile, and_(CrmLead.owner_employee_id == EmployeeProfile.id, EmployeeProfile.is_delete == 0))
            .filter(CrmLead.is_delete == 0)
        )
        if customer_name:
            query = query.filter(CrmLead.customer_name.like(f"%{customer_name}%"))
        if phone:
            query = query.filter(CrmLead.phone.like(f"%{phone}%"))
        if status:
            query = query.filter(CrmLead.status == status)
        if target_country:
            query = query.filter(CrmLead.target_country.like(f"%{target_country}%"))
        if owner_employee_id:
            query = query.filter(CrmLead.owner_employee_id == owner_employee_id)
        if owner_department_id:
            query = query.filter(EmployeeProfile.department_id == owner_department_id)
        if stale_days:
            cutoff = datetime.now() - timedelta(days=stale_days)
            query = query.filter(CrmLead.status == "following")
            query = query.filter(or_(CrmLead.last_follow_up_time.is_(None), CrmLead.last_follow_up_time <= cutoff))
        query = self._apply_datetime_range(query, CrmLead.create_time, created_start, created_end)
        return query.order_by(CrmLead.update_time.desc(), CrmLead.id.desc())

    def build_daily_report_query(
        self,
        employee_id: Optional[int] = None,
        department_id: Optional[int] = None,
        report_start: Optional[date] = None,
        report_end: Optional[date] = None,
        report_status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Query:
        """构建员工日报查询，联表返回员工姓名和部门名称。"""
        query = (
            self.db.query(
                EmployeeDailyReport,
                EmployeeProfile.employee_name.label("employee_name"),
                SysDepartment.department_name.label("department_name"),
            )
            .join(EmployeeProfile, and_(EmployeeDailyReport.employee_id == EmployeeProfile.id, EmployeeProfile.is_delete == 0))
            .outerjoin(SysDepartment, and_(EmployeeDailyReport.department_id == SysDepartment.id, SysDepartment.is_delete == 0))
            .filter(EmployeeDailyReport.is_delete == 0)
        )
        if employee_id:
            query = query.filter(EmployeeDailyReport.employee_id == employee_id)
        if department_id:
            query = query.filter(EmployeeDailyReport.department_id == department_id)
        if report_start:
            query = query.filter(EmployeeDailyReport.report_date >= report_start)
        if report_end:
            query = query.filter(EmployeeDailyReport.report_date <= report_end)
        if report_status:
            query = query.filter(EmployeeDailyReport.report_status == report_status)
        if keyword:
            query = query.filter(
                or_(
                    EmployeeDailyReport.raw_content.like(f"%{keyword}%"),
                    EmployeeDailyReport.summary.like(f"%{keyword}%"),
                    EmployeeDailyReport.key_progress.like(f"%{keyword}%"),
                    EmployeeDailyReport.risks.like(f"%{keyword}%"),
                    EmployeeDailyReport.tomorrow_plan.like(f"%{keyword}%"),
                )
            )
        return query.order_by(EmployeeDailyReport.report_date.desc(), EmployeeDailyReport.id.desc())

    def list_active_employees(self, department_id: Optional[int] = None) -> list[EmployeeProfile]:
        """查询在职且未软删除的员工，用于日报未提交统计。"""
        query = self.db.query(EmployeeProfile).filter(EmployeeProfile.status == "active", EmployeeProfile.is_delete == 0)
        if department_id:
            query = query.filter(EmployeeProfile.department_id == department_id)
        return query.order_by(EmployeeProfile.employee_name.asc()).all()

    def build_department_query(
        self,
        department_id: Optional[int] = None,
        department_name: Optional[str] = None,
        employee_name: Optional[str] = None,
        leader_employee_id: Optional[int] = None,
        status: Optional[str] = "enabled",
    ) -> Query:
        """构建组织架构查询，可按部门字段和成员姓名过滤。"""
        query = self.db.query(SysDepartment).filter(SysDepartment.is_delete == 0)
        if department_id:
            query = query.filter(SysDepartment.id == department_id)
        if department_name:
            query = query.filter(SysDepartment.department_name.like(f"%{department_name}%"))
        if leader_employee_id:
            query = query.filter(SysDepartment.leader_employee_id == leader_employee_id)
        if status:
            query = query.filter(SysDepartment.status == status)
        if employee_name:
            query = query.join(EmployeeProfile, and_(EmployeeProfile.department_id == SysDepartment.id, EmployeeProfile.is_delete == 0))
            query = query.filter(EmployeeProfile.employee_name.like(f"%{employee_name}%"))
        return query.order_by(SysDepartment.sort_order.asc(), SysDepartment.id.asc())

    def list_department_members(self, department_ids: list[int]) -> dict[int, list[EmployeeProfile]]:
        """批量查询部门成员并按部门分组。"""
        if not department_ids:
            return {}
        employees = (
            self.db.query(EmployeeProfile)
            .filter(EmployeeProfile.department_id.in_(department_ids), EmployeeProfile.status == "active", EmployeeProfile.is_delete == 0)
            .order_by(EmployeeProfile.employee_name.asc())
            .all()
        )
        grouped = {department_id: [] for department_id in department_ids}
        for employee in employees:
            grouped.setdefault(employee.department_id, []).append(employee)
        return grouped

    def build_student_query(
        self,
        student_id: Optional[int] = None,
        student_name: Optional[str] = None,
        phone: Optional[str] = None,
        current_school: Optional[str] = None,
        target_country: Optional[str] = None,
        status: Optional[str] = "active",
    ) -> Query:
        """构建学生档案查询。"""
        query = self.db.query(StudentProfile).filter(StudentProfile.is_delete == 0)
        if student_id:
            query = query.filter(StudentProfile.id == student_id)
        if student_name:
            query = query.filter(StudentProfile.student_name.like(f"%{student_name}%"))
        if phone:
            query = query.filter(StudentProfile.phone.like(f"%{phone}%"))
        if current_school:
            query = query.filter(StudentProfile.current_school.like(f"%{current_school}%"))
        if target_country:
            query = query.filter(StudentProfile.target_country.like(f"%{target_country}%"))
        if status:
            query = query.filter(StudentProfile.status == status)
        return query.order_by(StudentProfile.id.desc())

    def build_score_query(
        self,
        student_id: Optional[int] = None,
        student_name: Optional[str] = None,
        course_name: Optional[str] = None,
        exam_type: Optional[str] = None,
        semester: Optional[str] = None,
        exam_start: Optional[date] = None,
        exam_end: Optional[date] = None,
    ) -> Query:
        """构建学生成绩查询，联表返回学生姓名。"""
        query = (
            self.db.query(StudentScore, StudentProfile.student_name.label("student_name"))
            .join(StudentProfile, and_(StudentScore.student_id == StudentProfile.id, StudentProfile.is_delete == 0))
            .filter(StudentScore.is_delete == 0)
        )
        if student_id:
            query = query.filter(StudentScore.student_id == student_id)
        if student_name:
            query = query.filter(StudentProfile.student_name.like(f"%{student_name}%"))
        if course_name:
            query = query.filter(StudentScore.course_name.like(f"%{course_name}%"))
        if exam_type:
            query = query.filter(StudentScore.exam_type == exam_type)
        if semester:
            query = query.filter(StudentScore.semester.like(f"%{semester}%"))
        if exam_start:
            query = query.filter(StudentScore.exam_date >= exam_start)
        if exam_end:
            query = query.filter(StudentScore.exam_date <= exam_end)
        return query.order_by(StudentScore.exam_date.desc(), StudentScore.id.desc())

    def build_leave_query(
        self,
        student_id: Optional[int] = None,
        student_name: Optional[str] = None,
        request_no: Optional[str] = None,
        leave_type: Optional[str] = None,
        status: Optional[str] = None,
        approver_employee_id: Optional[int] = None,
        approver_department_id: Optional[int] = None,
        start_time_from: Optional[datetime] = None,
        start_time_to: Optional[datetime] = None,
    ) -> Query:
        """构建学生请假查询，联表返回学生姓名和审批人姓名。"""
        query = (
            self.db.query(
                StudentLeaveRequest,
                StudentProfile.student_name.label("student_name"),
                EmployeeProfile.employee_name.label("approver_name"),
            )
            .join(StudentProfile, and_(StudentLeaveRequest.student_id == StudentProfile.id, StudentProfile.is_delete == 0))
            .outerjoin(EmployeeProfile, and_(StudentLeaveRequest.approver_employee_id == EmployeeProfile.id, EmployeeProfile.is_delete == 0))
            .filter(StudentLeaveRequest.is_delete == 0)
        )
        if student_id:
            query = query.filter(StudentLeaveRequest.student_id == student_id)
        if student_name:
            query = query.filter(StudentProfile.student_name.like(f"%{student_name}%"))
        if request_no:
            query = query.filter(StudentLeaveRequest.request_no.like(f"%{request_no}%"))
        if leave_type:
            query = query.filter(StudentLeaveRequest.leave_type == leave_type)
        if status:
            query = query.filter(StudentLeaveRequest.status == status)
        if approver_employee_id:
            query = query.filter(StudentLeaveRequest.approver_employee_id == approver_employee_id)
        if approver_department_id:
            employee_ids = self.db.query(EmployeeProfile.id).filter(
                EmployeeProfile.department_id == approver_department_id,
                EmployeeProfile.is_delete == 0,
            )
            query = query.filter(StudentLeaveRequest.approver_employee_id.in_(employee_ids))
        if start_time_from:
            query = query.filter(StudentLeaveRequest.start_time >= start_time_from)
        if start_time_to:
            query = query.filter(StudentLeaveRequest.start_time <= start_time_to)
        return query.order_by(StudentLeaveRequest.create_time.desc(), StudentLeaveRequest.id.desc())

    def build_feedback_query(
        self,
        student_id: Optional[int] = None,
        student_name: Optional[str] = None,
        ticket_no: Optional[str] = None,
        ticket_type: Optional[str] = None,
        category: Optional[str] = None,
        priority_level: Optional[str] = None,
        status: Optional[str] = None,
        statuses: Optional[list[str]] = None,
        handler_employee_id: Optional[int] = None,
        handler_department_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> Query:
        """构建投诉反馈查询，联表返回学生姓名和处理人姓名。"""
        query = (
            self.db.query(
                StudentFeedbackTicket,
                StudentProfile.student_name.label("student_name"),
                EmployeeProfile.employee_name.label("handler_name"),
            )
            .join(StudentProfile, and_(StudentFeedbackTicket.student_id == StudentProfile.id, StudentProfile.is_delete == 0))
            .outerjoin(EmployeeProfile, and_(StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id, EmployeeProfile.is_delete == 0))
            .filter(StudentFeedbackTicket.is_delete == 0)
        )
        if student_id:
            query = query.filter(StudentFeedbackTicket.student_id == student_id)
        if student_name:
            query = query.filter(StudentProfile.student_name.like(f"%{student_name}%"))
        if ticket_no:
            query = query.filter(StudentFeedbackTicket.ticket_no.like(f"%{ticket_no}%"))
        if ticket_type:
            query = query.filter(StudentFeedbackTicket.ticket_type == ticket_type)
        if category:
            query = query.filter(StudentFeedbackTicket.category == category)
        if priority_level:
            query = query.filter(StudentFeedbackTicket.priority_level == priority_level)
        if status:
            query = query.filter(StudentFeedbackTicket.status == status)
        if statuses:
            query = query.filter(StudentFeedbackTicket.status.in_(statuses))
        if handler_employee_id:
            query = query.filter(StudentFeedbackTicket.handler_employee_id == handler_employee_id)
        if handler_department_id:
            employee_ids = self.db.query(EmployeeProfile.id).filter(
                EmployeeProfile.department_id == handler_department_id,
                EmployeeProfile.is_delete == 0,
            )
            query = query.filter(StudentFeedbackTicket.handler_employee_id.in_(employee_ids))
        if keyword:
            query = query.filter(
                or_(
                    StudentFeedbackTicket.title.like(f"%{keyword}%"),
                    StudentFeedbackTicket.content_summary.like(f"%{keyword}%"),
                    StudentFeedbackTicket.detail.like(f"%{keyword}%"),
                    StudentFeedbackTicket.solution.like(f"%{keyword}%"),
                )
            )
        return query.order_by(StudentFeedbackTicket.create_time.desc(), StudentFeedbackTicket.id.desc())

    def build_application_progress_query(
        self,
        student_id: Optional[int] = None,
        student_name: Optional[str] = None,
        progress_stage: Optional[str] = None,
        target_country: Optional[str] = None,
        school_name: Optional[str] = None,
        program_name: Optional[str] = None,
        progress_status: Optional[str] = None,
        handler_employee_id: Optional[int] = None,
    ) -> Query:
        """构建学生申请进度查询，联表返回学生姓名和处理人姓名。"""
        query = (
            self.db.query(
                StudentApplicationProgress,
                StudentProfile.student_name.label("student_name"),
                EmployeeProfile.employee_name.label("handler_name"),
            )
            .join(StudentProfile, and_(StudentApplicationProgress.student_id == StudentProfile.id, StudentProfile.is_delete == 0))
            .outerjoin(EmployeeProfile, and_(StudentApplicationProgress.handler_employee_id == EmployeeProfile.id, EmployeeProfile.is_delete == 0))
            .filter(StudentApplicationProgress.is_delete == 0)
        )
        if student_id:
            query = query.filter(StudentApplicationProgress.student_id == student_id)
        if student_name:
            query = query.filter(StudentProfile.student_name.like(f"%{student_name}%"))
        if progress_stage:
            query = query.filter(StudentApplicationProgress.progress_stage == progress_stage)
        if target_country:
            query = query.filter(StudentApplicationProgress.target_country.like(f"%{target_country}%"))
        if school_name:
            query = query.filter(StudentApplicationProgress.school_name.like(f"%{school_name}%"))
        if program_name:
            query = query.filter(StudentApplicationProgress.program_name.like(f"%{program_name}%"))
        if progress_status:
            query = query.filter(StudentApplicationProgress.progress_status == progress_status)
        if handler_employee_id:
            query = query.filter(StudentApplicationProgress.handler_employee_id == handler_employee_id)
        return query.order_by(StudentApplicationProgress.update_time.desc(), StudentApplicationProgress.id.desc())

    def count_leads_by_status(self, department_id: Optional[int], start_date: Optional[date], end_date: Optional[date]) -> dict[str, int]:
        """按客户状态统计线索数量。"""
        query = self.build_lead_query(owner_department_id=department_id, created_start=start_date, created_end=end_date)
        rows = query.order_by(None).with_entities(CrmLead.status, func.count(CrmLead.id)).group_by(CrmLead.status).all()
        return {status or "未填写": count for status, count in rows}

    def count_leads_by_country(self, department_id: Optional[int], start_date: Optional[date], end_date: Optional[date]) -> dict[str, int]:
        """按目标国家统计线索数量。"""
        query = self.build_lead_query(owner_department_id=department_id, created_start=start_date, created_end=end_date)
        rows = query.order_by(None).with_entities(CrmLead.target_country, func.count(CrmLead.id)).group_by(CrmLead.target_country).all()
        return {country or "未填写": count for country, count in rows}
