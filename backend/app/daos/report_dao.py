from datetime import date
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.common.enums import ReportType
from app.models.audit_log import AiToolCallLog, AuditLog
from app.models.crm_lead import CrmLead
from app.models.customer_analysis_record import CustomerAnalysisRecord
from app.models.employee_daily_report import EmployeeDailyReport
from app.models.employee_profile import EmployeeProfile
from app.models.event_registration import EventRegistration
from app.models.student_profile import StudentProfile
from app.models.student_feedback_ticket import StudentFeedbackTicket
from app.models.student_psych_alert import StudentPsychAlert
from app.models.student_psych_profile import StudentPsychProfile
from app.models.draft import AiDraft
from app.models.report import AiReport, ReportExportRecord


class ReportDAO:
    def __init__(self, db: Session):
        self.db = db

    def query_report_source_data(
        self,
        report_type: str,
        date_start: date,
        date_end: date,
        department_id: int | None = None,
        owner_user_id: int | None = None,
    ) -> dict[str, Any]:
        if report_type == ReportType.COMPLAINT_WEEKLY:
            return self._query_complaint_weekly(date_start, date_end, department_id)
        if report_type == ReportType.CUSTOMER_OPERATION:
            return self._query_customer_operation(date_start, date_end, department_id, owner_user_id)
        if report_type == ReportType.EMPLOYEE_DAILY_SUMMARY:
            return self._query_employee_daily_summary(date_start, department_id)
        if report_type == ReportType.EMPLOYEE_WEEKLY_SUMMARY:
            return self._query_employee_weekly_summary(date_start, date_end, department_id)
        if report_type == ReportType.STUDENT_PSYCH_WEEKLY:
            return self._query_student_psych_weekly(date_start, date_end, department_id)
        raise ValueError(f"不支持的报告类型：{report_type}")

    def _query_complaint_weekly(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        stmt = (
            select(StudentFeedbackTicket.status, func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
            )
            .group_by(StudentFeedbackTicket.status)
        )
        if department_id is not None:
            stmt = stmt.where(EmployeeProfile.department_id == department_id, EmployeeProfile.is_delete == 0)
        rows = self.db.execute(stmt).all()
        status_counts = {status: count for status, count in rows}
        total = sum(status_counts.values())
        return {
            "report_type": ReportType.COMPLAINT_WEEKLY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_tickets": total,
            "status_counts": status_counts,
        }

    def _query_customer_operation(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
        owner_user_id: int | None,
    ) -> dict[str, Any]:
        employee_filters = []
        if department_id is not None:
            employee_filters.append(EmployeeProfile.department_id == department_id)
        if owner_user_id is not None:
            employee_filters.append(EmployeeProfile.user_id == owner_user_id)
        employee_filters.append(EmployeeProfile.is_delete == 0)

        lead_stmt = (
            select(func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(func.date(CrmLead.create_time).between(date_start, date_end), CrmLead.is_delete == 0, *employee_filters)
        )
        analysis_stmt = (
            select(func.count(CustomerAnalysisRecord.id))
            .join(CrmLead, CustomerAnalysisRecord.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(CustomerAnalysisRecord.create_time).between(date_start, date_end),
                CustomerAnalysisRecord.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
        )
        registration_stmt = (
            select(func.count(EventRegistration.id))
            .join(CrmLead, EventRegistration.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(EventRegistration.create_time).between(date_start, date_end),
                EventRegistration.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
        )

        return {
            "report_type": ReportType.CUSTOMER_OPERATION,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "owner_user_id": owner_user_id,
            "new_leads": self.db.scalar(lead_stmt) or 0,
            "analysis_records": self.db.scalar(analysis_stmt) or 0,
            "event_registrations": self.db.scalar(registration_stmt) or 0,
        }

    def _query_employee_daily_summary(
        self,
        report_date: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        filters = [
            EmployeeDailyReport.report_date == report_date,
            EmployeeDailyReport.is_delete == 0,
        ]
        if department_id is not None:
            filters.append(EmployeeDailyReport.department_id == department_id)

        status_counts = self._count_employee_daily_status(filters)
        return {
            "report_type": ReportType.EMPLOYEE_DAILY_SUMMARY,
            "date_start": str(report_date),
            "date_end": str(report_date),
            "department_id": department_id,
            "total_reports": sum(status_counts.values()),
            "status_counts": status_counts,
            "submitted_reports": status_counts.get("submitted", 0),
            "draft_reports": status_counts.get("draft", 0),
            "archived_reports": status_counts.get("archived", 0),
            "risk_reports": self._count_employee_daily_text_field(filters, EmployeeDailyReport.risks),
            "tomorrow_plan_reports": self._count_employee_daily_text_field(filters, EmployeeDailyReport.tomorrow_plan),
        }

    def _query_employee_weekly_summary(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        filters = [
            EmployeeDailyReport.report_date.between(date_start, date_end),
            EmployeeDailyReport.is_delete == 0,
        ]
        if department_id is not None:
            filters.append(EmployeeDailyReport.department_id == department_id)

        trend_rows = self.db.execute(
            select(EmployeeDailyReport.report_date, func.count(EmployeeDailyReport.id))
            .where(*filters)
            .group_by(EmployeeDailyReport.report_date)
            .order_by(EmployeeDailyReport.report_date)
        ).all()
        return {
            "report_type": ReportType.EMPLOYEE_WEEKLY_SUMMARY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_reports": self.db.scalar(select(func.count(EmployeeDailyReport.id)).where(*filters)) or 0,
            "distinct_employees": self.db.scalar(
                select(func.count(func.distinct(EmployeeDailyReport.employee_id))).where(*filters)
            )
            or 0,
            "status_counts": self._count_employee_daily_status(filters),
            "daily_trend": {str(report_date): count for report_date, count in trend_rows},
            "risk_reports": self._count_employee_daily_text_field(filters, EmployeeDailyReport.risks),
        }

    def _count_employee_daily_status(self, filters: list[Any]) -> dict[str, int]:
        rows = self.db.execute(
            select(EmployeeDailyReport.report_status, func.count(EmployeeDailyReport.id))
            .where(*filters)
            .group_by(EmployeeDailyReport.report_status)
        ).all()
        return {status: count for status, count in rows}

    def _count_employee_daily_text_field(self, filters: list[Any], field) -> int:
        return (
            self.db.scalar(
                select(func.count(EmployeeDailyReport.id)).where(
                    *filters,
                    field.is_not(None),
                    field != "",
                )
            )
            or 0
        )

    def _query_student_psych_weekly(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        profile_stmt = (
            select(StudentPsychProfile.risk_level, func.count(StudentPsychProfile.id))
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
            )
            .group_by(StudentPsychProfile.risk_level)
        )
        profile_stmt = self._apply_student_department_filter(profile_stmt, department_id)
        risk_level_counts = {level: count for level, count in self.db.execute(profile_stmt).all()}

        emotion_stmt = (
            select(StudentPsychProfile.latest_emotion_tag, func.count(StudentPsychProfile.id))
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                StudentPsychProfile.latest_emotion_tag.is_not(None),
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
            )
            .group_by(StudentPsychProfile.latest_emotion_tag)
        )
        emotion_stmt = self._apply_student_department_filter(emotion_stmt, department_id)
        emotion_tag_counts = {tag: count for tag, count in self.db.execute(emotion_stmt).all()}

        avg_stmt = (
            select(func.avg(StudentPsychProfile.emotion_score))
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                StudentPsychProfile.emotion_score.is_not(None),
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
            )
        )
        avg_stmt = self._apply_student_department_filter(avg_stmt, department_id)
        average_score = self.db.scalar(avg_stmt)

        alert_status_stmt = (
            select(StudentPsychAlert.status, func.count(StudentPsychAlert.id))
            .join(StudentProfile, StudentPsychAlert.student_id == StudentProfile.id)
            .where(
                StudentPsychAlert.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychAlert.create_time).between(date_start, date_end),
            )
            .group_by(StudentPsychAlert.status)
        )
        alert_status_stmt = self._apply_student_department_filter(alert_status_stmt, department_id)
        alert_status_counts = {status: count for status, count in self.db.execute(alert_status_stmt).all()}

        alert_risk_stmt = (
            select(StudentPsychAlert.risk_level, func.count(StudentPsychAlert.id))
            .join(StudentProfile, StudentPsychAlert.student_id == StudentProfile.id)
            .where(
                StudentPsychAlert.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychAlert.create_time).between(date_start, date_end),
            )
            .group_by(StudentPsychAlert.risk_level)
        )
        alert_risk_stmt = self._apply_student_department_filter(alert_risk_stmt, department_id)
        alert_risk_level_counts = {level: count for level, count in self.db.execute(alert_risk_stmt).all()}

        return {
            "report_type": ReportType.STUDENT_PSYCH_WEEKLY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_profiles": sum(risk_level_counts.values()),
            "risk_level_counts": risk_level_counts,
            "emotion_tag_counts": emotion_tag_counts,
            "average_emotion_score": round(float(average_score), 2) if average_score is not None else None,
            "total_alerts": sum(alert_status_counts.values()),
            "alert_status_counts": alert_status_counts,
            "alert_risk_level_counts": alert_risk_level_counts,
        }

    def _apply_student_department_filter(self, stmt, department_id: int | None):
        if department_id is None:
            return stmt
        Counselor = aliased(EmployeeProfile)
        Teacher = aliased(EmployeeProfile)
        return (
            stmt.outerjoin(Counselor, StudentProfile.counselor_employee_id == Counselor.id)
            .outerjoin(Teacher, StudentProfile.teacher_employee_id == Teacher.id)
            .where(
                or_(
                    and_(Counselor.department_id == department_id, Counselor.is_delete == 0),
                    and_(Teacher.department_id == department_id, Teacher.is_delete == 0),
                )
            )
        )

    def add_draft(self, draft: AiDraft) -> AiDraft:
        self.db.add(draft)
        self.db.flush()
        return draft

    def get_draft(self, draft_id: int) -> AiDraft | None:
        stmt = select(AiDraft).where(AiDraft.id == draft_id, AiDraft.is_deleted.is_(False))
        return self.db.scalar(stmt)

    def list_report_drafts(self) -> list[AiDraft]:
        stmt = (
            select(AiDraft)
            .where(AiDraft.biz_module == "report", AiDraft.is_deleted.is_(False))
            .order_by(AiDraft.create_time.desc())
        )
        return list(self.db.scalars(stmt).all())

    def add_report(self, report: AiReport) -> AiReport:
        self.db.add(report)
        self.db.flush()
        return report

    def get_report(self, report_id: int) -> AiReport | None:
        stmt = select(AiReport).where(AiReport.id == report_id, AiReport.is_deleted.is_(False))
        return self.db.scalar(stmt)

    def list_reports(self) -> list[AiReport]:
        stmt = select(AiReport).where(AiReport.is_deleted.is_(False)).order_by(AiReport.create_time.desc())
        return list(self.db.scalars(stmt).all())

    def add_export_record(self, record: ReportExportRecord) -> ReportExportRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def list_export_records(self, report_id: int) -> list[ReportExportRecord]:
        stmt = (
            select(ReportExportRecord)
            .where(ReportExportRecord.report_id == report_id, ReportExportRecord.is_deleted.is_(False))
            .order_by(ReportExportRecord.create_time.desc())
        )
        return list(self.db.scalars(stmt).all())

    def add_audit_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.flush()
        return log

    def add_tool_call_log(self, log: AiToolCallLog) -> AiToolCallLog:
        self.db.add(log)
        self.db.flush()
        return log
