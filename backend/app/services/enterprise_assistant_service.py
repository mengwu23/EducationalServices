"""企业管理查询助手的业务服务层。"""

from datetime import date, datetime
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from ..daos.enterprise_assistant_dao import EnterpriseAssistantDao
from ..schemas.enterprise_assistant_schema import (
    DailyReportItem,
    DailyReportSummaryResult,
    DepartmentItem,
    DepartmentMemberItem,
    LeadItem,
    OnboardingGuideResult,
    PageResult,
    StatisticsSummaryResult,
    StudentApplicationProgressItem,
    StudentFeedbackItem,
    StudentLeaveItem,
    StudentProfileItem,
    StudentScoreItem,
    SummaryBlock,
    TodoSummaryResult,
)


class EnterpriseAssistantService:
    """承接接口参数，组织 DAO 查询并转换为接口返回结构。"""

    def __init__(self, db: Session):
        self.dao = EnterpriseAssistantDao(db)

    def search_leads(
        self,
        customer_name: Optional[str],
        phone: Optional[str],
        status: Optional[str],
        target_country: Optional[str],
        owner_employee_id: Optional[int],
        created_start: Optional[date],
        created_end: Optional[date],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按客户线索字段查询分页列表。"""
        query = self.dao.build_lead_query(
            customer_name=customer_name,
            phone=phone,
            status=status,
            target_country=target_country,
            owner_employee_id=owner_employee_id,
            created_start=created_start,
            created_end=created_end,
        )
        total, rows = self.dao.paginate(query, page, page_size)
        return PageResult(total=total, page=page, page_size=page_size, items=[self._lead_item(*row) for row in rows])

    def search_daily_reports(
        self,
        employee_id: Optional[int],
        department_id: Optional[int],
        report_start: Optional[date],
        report_end: Optional[date],
        report_status: Optional[str],
        keyword: Optional[str],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按日报字段查询分页列表。"""
        query = self.dao.build_daily_report_query(
            employee_id=employee_id,
            department_id=department_id,
            report_start=report_start,
            report_end=report_end,
            report_status=report_status,
            keyword=keyword,
        )
        total, rows = self.dao.paginate(query, page, page_size)
        return PageResult(total=total, page=page, page_size=page_size, items=[self._daily_report_item(*row) for row in rows])

    def summarize_daily_reports(
        self,
        department_id: Optional[int],
        report_start: date,
        report_end: date,
        report_status: Optional[str],
        detail_limit: int,
    ) -> DailyReportSummaryResult:
        """汇总日报并返回参与汇总的日报明细。"""
        query = self.dao.build_daily_report_query(
            department_id=department_id,
            report_start=report_start,
            report_end=report_end,
            report_status=report_status,
        )
        rows = query.limit(detail_limit).all()
        reports = [self._daily_report_item(*row) for row in rows]
        active_employees = self.dao.list_active_employees(department_id)
        submitted_employee_ids = {report.employee_id for report in reports}
        missing_employee_names = [employee.employee_name for employee in active_employees if employee.id not in submitted_employee_ids]

        metrics = {
            "report_count": len(reports),
            "missing_employee_count": len(missing_employee_names),
            "employee_count": len(active_employees),
            "risk_count": len([report for report in reports if report.risks]),
        }
        summary = SummaryBlock(text=f"本次共汇总 {len(reports)} 份日报，未提交 {len(missing_employee_names)} 人。", metrics=metrics)
        return DailyReportSummaryResult(summary=summary, reports=reports, missing_employee_names=missing_employee_names)

    def search_departments(
        self,
        department_id: Optional[int],
        department_name: Optional[str],
        employee_name: Optional[str],
        leader_employee_id: Optional[int],
        status: Optional[str],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按组织架构字段查询分页列表。"""
        query = self.dao.build_department_query(
            department_id=department_id,
            department_name=department_name,
            employee_name=employee_name,
            leader_employee_id=leader_employee_id,
            status=status,
        )
        total, departments = self.dao.paginate(query, page, page_size)
        members_by_department = self.dao.list_department_members([department.id for department in departments])
        items = [self._department_item(department, members_by_department.get(department.id, [])) for department in departments]
        return PageResult(total=total, page=page, page_size=page_size, items=items)

    def search_students(
        self,
        student_id: Optional[int],
        student_name: Optional[str],
        phone: Optional[str],
        current_school: Optional[str],
        target_country: Optional[str],
        status: Optional[str],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按学生档案字段查询分页列表。"""
        query = self.dao.build_student_query(
            student_id=student_id,
            student_name=student_name,
            phone=phone,
            current_school=current_school,
            target_country=target_country,
            status=status,
        )
        total, rows = self.dao.paginate(query, page, page_size)
        return PageResult(total=total, page=page, page_size=page_size, items=[self._student_item(row) for row in rows])

    def search_student_scores(
        self,
        student_id: Optional[int],
        student_name: Optional[str],
        course_name: Optional[str],
        exam_type: Optional[str],
        semester: Optional[str],
        exam_start: Optional[date],
        exam_end: Optional[date],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按成绩字段查询分页列表。"""
        query = self.dao.build_score_query(
            student_id=student_id,
            student_name=student_name,
            course_name=course_name,
            exam_type=exam_type,
            semester=semester,
            exam_start=exam_start,
            exam_end=exam_end,
        )
        total, rows = self.dao.paginate(query, page, page_size)
        return PageResult(total=total, page=page, page_size=page_size, items=[self._score_item(*row) for row in rows])

    def search_student_leaves(
        self,
        student_id: Optional[int],
        student_name: Optional[str],
        request_no: Optional[str],
        leave_type: Optional[str],
        status: Optional[str],
        approver_employee_id: Optional[int],
        start_time_from: Optional[datetime],
        start_time_to: Optional[datetime],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按请假字段查询分页列表。"""
        query = self.dao.build_leave_query(
            student_id=student_id,
            student_name=student_name,
            request_no=request_no,
            leave_type=leave_type,
            status=status,
            approver_employee_id=approver_employee_id,
            start_time_from=start_time_from,
            start_time_to=start_time_to,
        )
        total, rows = self.dao.paginate(query, page, page_size)
        return PageResult(total=total, page=page, page_size=page_size, items=[self._leave_item(*row) for row in rows])

    def search_student_feedback(
        self,
        student_id: Optional[int],
        student_name: Optional[str],
        ticket_no: Optional[str],
        ticket_type: Optional[str],
        category: Optional[str],
        priority_level: Optional[str],
        status: Optional[str],
        handler_employee_id: Optional[int],
        keyword: Optional[str],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按反馈工单字段查询分页列表。"""
        query = self.dao.build_feedback_query(
            student_id=student_id,
            student_name=student_name,
            ticket_no=ticket_no,
            ticket_type=ticket_type,
            category=category,
            priority_level=priority_level,
            status=status,
            handler_employee_id=handler_employee_id,
            keyword=keyword,
        )
        total, rows = self.dao.paginate(query, page, page_size)
        return PageResult(total=total, page=page, page_size=page_size, items=[self._feedback_item(*row) for row in rows])

    def search_application_progresses(
        self,
        student_id: Optional[int],
        student_name: Optional[str],
        progress_stage: Optional[str],
        target_country: Optional[str],
        school_name: Optional[str],
        program_name: Optional[str],
        progress_status: Optional[str],
        handler_employee_id: Optional[int],
        page: int,
        page_size: int,
    ) -> PageResult:
        """按学生申请进度字段查询分页列表。"""
        query = self.dao.build_application_progress_query(
            student_id=student_id,
            student_name=student_name,
            progress_stage=progress_stage,
            target_country=target_country,
            school_name=school_name,
            program_name=program_name,
            progress_status=progress_status,
            handler_employee_id=handler_employee_id,
        )
        total, rows = self.dao.paginate(query, page, page_size)
        return PageResult(total=total, page=page, page_size=page_size, items=[self._progress_item(*row) for row in rows])

    def summarize_todos(self, stale_lead_days: int, detail_limit: int) -> TodoSummaryResult:
        """统计待办并返回请假、反馈、超时客户三类明细。"""
        leave_query = self.dao.build_leave_query(status="pending")
        feedback_query = self.dao.build_feedback_query(statuses=["pending", "processing"])
        stale_lead_query = self.dao.build_lead_query(stale_days=stale_lead_days)

        pending_leave_count = leave_query.count()
        feedback_count = feedback_query.count()
        stale_lead_count = stale_lead_query.count()
        pending_leaves = [self._leave_item(*row) for row in leave_query.limit(detail_limit).all()]
        feedback_items = [self._feedback_item(*row) for row in feedback_query.limit(detail_limit).all()]
        stale_leads = [self._lead_item(*row) for row in stale_lead_query.limit(detail_limit).all()]

        metrics = {
            "pending_leave_count": pending_leave_count,
            "feedback_count": feedback_count,
            "stale_lead_count": stale_lead_count,
            "stale_lead_days": stale_lead_days,
            "detail_limit": detail_limit,
        }
        total = pending_leave_count + feedback_count + stale_lead_count
        summary = SummaryBlock(text=f"当前共有 {total} 条待办。", metrics=metrics)
        return TodoSummaryResult(summary=summary, pending_leaves=pending_leaves, feedback_tickets=feedback_items, stale_leads=stale_leads)

    def summarize_statistics(
        self,
        department_id: Optional[int],
        start_date: Optional[date],
        end_date: Optional[date],
        detail_limit: int,
    ) -> StatisticsSummaryResult:
        """生成管理统计，并返回统计范围内的主要明细数据。"""
        lead_count_by_status = self.dao.count_leads_by_status(department_id, start_date, end_date)
        lead_count_by_country = self.dao.count_leads_by_country(department_id, start_date, end_date)

        lead_query = self.dao.build_lead_query(owner_department_id=department_id, created_start=start_date, created_end=end_date)
        daily_query = self.dao.build_daily_report_query(department_id=department_id, report_start=start_date, report_end=end_date)
        leave_query = self.dao.build_leave_query(status="pending", approver_department_id=department_id)
        feedback_query = self.dao.build_feedback_query(statuses=["pending", "processing"], handler_department_id=department_id)

        daily_report_count = daily_query.count()
        pending_leave_count = leave_query.count()
        pending_feedback_count = feedback_query.count()
        leads = [self._lead_item(*row) for row in lead_query.limit(detail_limit).all()]
        daily_reports = [self._daily_report_item(*row) for row in daily_query.limit(detail_limit).all()]
        pending_leaves = [self._leave_item(*row) for row in leave_query.limit(detail_limit).all()]
        pending_feedback_tickets = [self._feedback_item(*row) for row in feedback_query.limit(detail_limit).all()]

        metrics = {
            "lead_total": sum(lead_count_by_status.values()),
            "daily_report_count": daily_report_count,
            "pending_leave_count": pending_leave_count,
            "pending_feedback_count": pending_feedback_count,
            "detail_limit": detail_limit,
        }
        summary = SummaryBlock(
            text=(
                f"当前统计范围内共有 {metrics['lead_total']} 条客户线索、"
                f"{daily_report_count} 份日报、{pending_leave_count} 条待审批请假、"
                f"{pending_feedback_count} 条待处理反馈。"
            ),
            metrics=metrics,
        )
        return StatisticsSummaryResult(
            summary=summary,
            lead_count_by_status=lead_count_by_status,
            lead_count_by_country=lead_count_by_country,
            daily_report_count=daily_report_count,
            pending_leave_count=pending_leave_count,
            pending_feedback_count=pending_feedback_count,
            leads=leads,
            daily_reports=daily_reports,
            pending_leaves=pending_leaves,
            pending_feedback_tickets=pending_feedback_tickets,
        )

    def query_onboarding_guide(self, question: str, category: Optional[str]) -> OnboardingGuideResult:
        """预留新人入职指引入口，后续接入本地 Dify RAG 知识库。"""
        return OnboardingGuideResult(
            status="reserved",
            message="新人入职指引模块已预留，后续将接入本地 Dify RAG 知识库。",
            question=question,
            category=category,
        )

    def _lead_item(self, lead: Any, owner_name: Optional[str]) -> LeadItem:
        """将客户线索 ORM 行转换为接口返回对象。"""
        return LeadItem(
            id=lead.id,
            lead_no=lead.lead_no,
            customer_name=lead.customer_name,
            phone=lead.phone,
            wechat_no=lead.wechat_no,
            email=lead.email,
            source_channel=lead.source_channel,
            education_level=lead.education_level,
            school_name=lead.school_name,
            major=lead.major,
            current_grade=lead.current_grade,
            target_country=lead.target_country,
            target_program=lead.target_program,
            budget_range=lead.budget_range,
            background_info=lead.background_info,
            follow_up_history=lead.follow_up_history,
            latest_follow_up_summary=lead.latest_follow_up_summary,
            status=lead.status,
            owner_employee_id=lead.owner_employee_id,
            owner_name=owner_name,
            last_follow_up_time=lead.last_follow_up_time,
            lost_reason=lead.lost_reason,
            signed_time=lead.signed_time,
            create_time=lead.create_time,
            update_time=lead.update_time,
        )

    def _daily_report_item(self, report: Any, employee_name: Optional[str], department_name: Optional[str]) -> DailyReportItem:
        """将日报 ORM 行转换为接口返回对象。"""
        return DailyReportItem(
            id=report.id,
            employee_id=report.employee_id,
            employee_name=employee_name,
            department_id=report.department_id,
            department_name=department_name,
            report_date=report.report_date,
            raw_content=report.raw_content,
            summary=report.summary,
            key_progress=report.key_progress,
            risks=report.risks,
            tomorrow_plan=report.tomorrow_plan,
            report_status=report.report_status,
            create_time=report.create_time,
            update_time=report.update_time,
        )

    def _department_item(self, department: Any, members: List[Any]) -> DepartmentItem:
        """将部门和成员 ORM 行转换为接口返回对象。"""
        leader_name = next((member.employee_name for member in members if member.id == department.leader_employee_id), None)
        return DepartmentItem(
            id=department.id,
            department_name=department.department_name,
            parent_id=department.parent_id,
            leader_employee_id=department.leader_employee_id,
            leader_name=leader_name,
            department_desc=department.department_desc,
            sort_order=department.sort_order,
            status=department.status,
            create_time=department.create_time,
            update_time=department.update_time,
            members=[
                DepartmentMemberItem(
                    id=member.id,
                    employee_no=member.employee_no,
                    employee_name=member.employee_name,
                    role_code=member.role_code,
                    job_title=member.job_title,
                    status=member.status,
                )
                for member in members
            ],
        )

    def _student_item(self, student: Any) -> StudentProfileItem:
        """将学生档案 ORM 行转换为接口返回对象。"""
        return StudentProfileItem(
            id=student.id,
            user_id=student.user_id,
            student_no=student.student_no,
            student_name=student.student_name,
            phone=student.phone,
            email=student.email,
            current_school=student.current_school,
            current_grade=student.current_grade,
            target_country=student.target_country,
            target_program=student.target_program,
            counselor_employee_id=student.counselor_employee_id,
            teacher_employee_id=student.teacher_employee_id,
            status=student.status,
            create_time=student.create_time,
            update_time=student.update_time,
        )

    def _score_item(self, score: Any, student_name: Optional[str]) -> StudentScoreItem:
        """将成绩 ORM 行转换为接口返回对象。"""
        return StudentScoreItem(
            id=score.id,
            student_id=score.student_id,
            student_name=student_name,
            course_name=score.course_name,
            score=score.score,
            exam_type=score.exam_type,
            semester=score.semester,
            exam_date=score.exam_date,
            operator_employee_id=score.operator_employee_id,
            remark=score.remark,
            create_time=score.create_time,
            update_time=score.update_time,
        )

    def _leave_item(self, leave: Any, student_name: Optional[str], approver_name: Optional[str]) -> StudentLeaveItem:
        """将请假 ORM 行转换为接口返回对象。"""
        return StudentLeaveItem(
            id=leave.id,
            request_no=leave.request_no,
            student_id=leave.student_id,
            student_name=student_name,
            leave_type=leave.leave_type,
            reason=leave.reason,
            start_time=leave.start_time,
            end_time=leave.end_time,
            status=leave.status,
            approver_employee_id=leave.approver_employee_id,
            approver_name=approver_name,
            approval_comment=leave.approval_comment,
            approve_time=leave.approve_time,
            create_time=leave.create_time,
            update_time=leave.update_time,
        )

    def _feedback_item(self, ticket: Any, student_name: Optional[str], handler_name: Optional[str]) -> StudentFeedbackItem:
        """将反馈工单 ORM 行转换为接口返回对象。"""
        return StudentFeedbackItem(
            id=ticket.id,
            ticket_no=ticket.ticket_no,
            student_id=ticket.student_id,
            student_name=student_name,
            ticket_type=ticket.ticket_type,
            category=ticket.category,
            title=ticket.title,
            content_summary=ticket.content_summary,
            detail=ticket.detail,
            priority_level=ticket.priority_level,
            status=ticket.status,
            handler_employee_id=ticket.handler_employee_id,
            handler_name=handler_name,
            solution=ticket.solution,
            satisfaction_score=ticket.satisfaction_score,
            is_notified=ticket.is_notified,
            close_time=ticket.close_time,
            create_time=ticket.create_time,
            update_time=ticket.update_time,
        )

    def _progress_item(self, progress: Any, student_name: Optional[str], handler_name: Optional[str]) -> StudentApplicationProgressItem:
        """将申请进度 ORM 行转换为接口返回对象。"""
        return StudentApplicationProgressItem(
            id=progress.id,
            student_id=progress.student_id,
            student_name=student_name,
            progress_stage=progress.progress_stage,
            target_country=progress.target_country,
            school_name=progress.school_name,
            program_name=progress.program_name,
            progress_status=progress.progress_status,
            progress_desc=progress.progress_desc,
            handler_employee_id=progress.handler_employee_id,
            handler_name=handler_name,
            expected_finish_time=progress.expected_finish_time,
            create_time=progress.create_time,
            update_time=progress.update_time,
        )
