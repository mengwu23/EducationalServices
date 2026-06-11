from datetime import date
from datetime import timedelta
from typing import Any

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session, aliased

from backend.app.common.enums import ReportType
from backend.app.models.audit_log import AiToolCallLog, AuditLog
from backend.app.models.crm_lead import CrmLead
from backend.app.models.customer_analysis_record import CustomerAnalysisRecord
from backend.app.models.draft import AiDraft
from backend.app.models.employee_daily_report import EmployeeDailyReport
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.event_registration import EventRegistration
from backend.app.models.report import AiReport, ReportExportRecord
from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
from backend.app.models.student_profile import StudentProfile
from backend.app.models.student_psych_alert import StudentPsychAlert
from backend.app.models.student_psych_profile import StudentPsychProfile
from backend.app.models.sys_department import SysDepartment


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
        category_rows = self.db.execute(
            select(StudentFeedbackTicket.category, func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
            .group_by(StudentFeedbackTicket.category)
        ).all()
        category_counts = {cat or "未分类": count for cat, count in category_rows}
        type_rows = self.db.execute(
            select(StudentFeedbackTicket.ticket_type, func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
            .group_by(StudentFeedbackTicket.ticket_type)
        ).all()
        ticket_type_counts = {tt or "未分类": count for tt, count in type_rows}
        time_rows = self.db.execute(
            select(StudentFeedbackTicket.create_time, StudentFeedbackTicket.close_time)
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.close_time.is_not(None),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
        ).all()
        hours_list = [
            (close - create).total_seconds() / 3600
            for create, close in time_rows
        ]
        avg_hours = round(sum(hours_list) / len(hours_list), 1) if hours_list else None
        return {
            "report_type": ReportType.COMPLAINT_WEEKLY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_tickets": total,
            "status_counts": status_counts,
            "category_counts": category_counts,
            "ticket_type_counts": ticket_type_counts,
            "avg_processing_hours": round(float(avg_hours), 1) if avg_hours else None,
        }

    def _query_customer_operation(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
        owner_user_id: int | None,
    ) -> dict[str, Any]:
        from datetime import timedelta

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


        source_rows = self.db.execute(
            select(CrmLead.source_channel, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(func.date(CrmLead.create_time).between(date_start, date_end), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.source_channel)
        ).all()
        lead_source_breakdown = {s or "???": c for s, c in source_rows}

        status_rows = self.db.execute(
            select(CrmLead.status, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.status)
        ).all()
        lead_status_breakdown = {s or "???": c for s, c in status_rows}

        result_rows = self.db.execute(
            select(CustomerAnalysisRecord.match_level, func.count(CustomerAnalysisRecord.id))
            .join(CrmLead, CustomerAnalysisRecord.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(CustomerAnalysisRecord.create_time).between(date_start, date_end),
                CustomerAnalysisRecord.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
            .group_by(CustomerAnalysisRecord.match_level)
        ).all()
        analysis_result_breakdown = {r or "???": c for r, c in result_rows}

        event_status_rows = self.db.execute(
            select(EventRegistration.registration_status, func.count(EventRegistration.id))
            .join(CrmLead, EventRegistration.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(EventRegistration.create_time).between(date_start, date_end),
                EventRegistration.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
            .group_by(EventRegistration.registration_status)
        ).all()
        event_registration_breakdown = {s or "???": c for s, c in event_status_rows}

        new_leads = self.db.scalar(lead_stmt) or 0
        analysis_records = self.db.scalar(analysis_stmt) or 0
        event_regs = self.db.scalar(registration_stmt) or 0

        # === 同环比数据：上周同期 ===
        period_days = (date_end - date_start).days or 7
        prev_start = date_start - timedelta(days=period_days)
        prev_end = date_end - timedelta(days=period_days)
        prev_lead_stmt = (
            select(func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(func.date(CrmLead.create_time).between(prev_start, prev_end), CrmLead.is_delete == 0, *employee_filters)
        )
        prev_leads = self.db.scalar(prev_lead_stmt) or 0
        prev_analysis = self.db.scalar(analysis_stmt.where(func.date(CustomerAnalysisRecord.create_time).between(prev_start, prev_end))) or 0
        prev_events = self.db.scalar(registration_stmt.where(func.date(EventRegistration.create_time).between(prev_start, prev_end))) or 0
        lead_delta_pct = round((new_leads - prev_leads) / prev_leads * 100, 1) if prev_leads > 0 else (100 if new_leads > 0 else 0)
        trend_label = "上升" if lead_delta_pct > 5 else ("下降" if lead_delta_pct < -5 else "持平")

        # === 流失归因：按渠道和阶段细分 ===
        lost_statuses = ["已流失", "废弃", "已关单", "lost", "closed"]
        churn_source_rows = self.db.execute(
            select(CrmLead.source_channel, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(CrmLead.status.in_(lost_statuses), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.source_channel)
        ).all()
        churn_source_breakdown = {s or "未归类": c for s, c in churn_source_rows}

        churn_stage_rows = self.db.execute(
            select(CrmLead.status, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(CrmLead.status.in_(lost_statuses), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.status)
        ).all()
        churn_stage_breakdown = {s or "未归类": c for s, c in churn_stage_rows}

        return {
            "report_type": ReportType.CUSTOMER_OPERATION,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "owner_user_id": owner_user_id,
            "new_leads": new_leads,
            "analysis_records": analysis_records,
            "event_registrations": event_regs,
            "lead_source_breakdown": lead_source_breakdown,
            "lead_status_breakdown": lead_status_breakdown,
            "analysis_result_breakdown": analysis_result_breakdown,
            "event_registration_breakdown": event_registration_breakdown,
            "prev_period": {
                "date_start": str(prev_start),
                "date_end": str(prev_end),
                "leads": prev_leads,
                "analysis": prev_analysis,
                "events": prev_events,
            },
            "lead_trend": {"delta_pct": lead_delta_pct, "label": trend_label},
            "churn_source_breakdown": churn_source_breakdown,
            "churn_stage_breakdown": churn_stage_breakdown,
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

        progress_rows = self.db.execute(
            select(EmployeeDailyReport.summary, EmployeeDailyReport.key_progress, EmployeeProfile.employee_name)
            .join(EmployeeProfile, EmployeeDailyReport.employee_id == EmployeeProfile.id, isouter=True)
            .where(*filters, or_(EmployeeDailyReport.summary.is_not(None), EmployeeDailyReport.key_progress.is_not(None)))
            .limit(5)
        ).all()
        key_progress_items = [
            {"emp": row.employee_name or "", "text": (row.key_progress or row.summary or "")[:120]}
            for row in progress_rows if (row.key_progress or row.summary or "").strip()
        ]

        risk_rows = self.db.execute(
            select(EmployeeDailyReport.risks, EmployeeProfile.employee_name)
            .join(EmployeeProfile, EmployeeDailyReport.employee_id == EmployeeProfile.id, isouter=True)
            .where(*filters, EmployeeDailyReport.risks.is_not(None), EmployeeDailyReport.risks != "")
            .limit(5)
        ).all()
        risk_items = [
            {"emp": row.employee_name or "", "text": (row.risks or "")[:120]}
            for row in risk_rows
        ]

        sub_list_rows = self.db.execute(
            select(EmployeeProfile.employee_name, EmployeeDailyReport.report_status,
                   EmployeeDailyReport.risks, EmployeeDailyReport.tomorrow_plan)
            .join(EmployeeDailyReport, EmployeeProfile.id == EmployeeDailyReport.employee_id, isouter=True)
            .where(
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0,
            )
            .limit(20)
        ).all()
        dept_emp_count = len(sub_list_rows)
        submission_rate = f"{round(sum(status_counts.values()) / dept_emp_count * 100, 1)}%" if dept_emp_count > 0 else "N/A"

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
            "key_progress_items": key_progress_items,
            "risk_items": risk_items,
            "submission_rate": submission_rate,
            "employee_submission_list": [dict(r._mapping) for r in sub_list_rows[:10]],
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

        total = self.db.scalar(select(func.count(EmployeeDailyReport.id)).where(*filters)) or 0
        distinct = self.db.scalar(
            select(func.count(func.distinct(EmployeeDailyReport.employee_id))).where(*filters)
        ) or 0
        trend = {str(report_date): count for report_date, count in trend_rows}
        risk_count = self._count_employee_daily_text_field(filters, EmployeeDailyReport.risks)

        dept_emp_count = self.db.scalar(
            select(func.count(EmployeeProfile.id))
            .where(
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0,
            )
        ) or 1
        week_days = max(len(trend), 1)
        week_submission_rate = f"{round(total / (dept_emp_count * week_days) * 100, 1)}%" if dept_emp_count > 0 else "N/A"

        risk_text_rows = self.db.execute(
            select(EmployeeDailyReport.risks)
            .where(*filters, EmployeeDailyReport.risks.is_not(None), EmployeeDailyReport.risks != "")
            .limit(30)
        ).all()
        risk_keywords: dict[str, int] = {}
        for (rtext,) in risk_text_rows:
            for kw in ["??", "??", "??", "??", "??", "??", "??", "??", "??", "??"]:
                if kw in (rtext or ""):
                    risk_keywords[kw] = risk_keywords.get(kw, 0) + 1
        top_risk_themes = sorted(risk_keywords.items(), key=lambda x: x[1], reverse=True)[:5]

        trend_dates = sorted(trend.keys())
        peak_day = max(trend, key=trend.get) if trend else None
        valley_day = min(trend, key=trend.get) if trend else None

        return {
            "report_type": ReportType.EMPLOYEE_WEEKLY_SUMMARY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_reports": total,
            "distinct_employees": distinct,
            "status_counts": self._count_employee_daily_status(filters),
            "daily_trend": trend,
            "risk_reports": risk_count,
            "week_submission_rate": week_submission_rate,
            "top_risk_themes": top_risk_themes,
            "peak_submission_day": peak_day,
            "valley_submission_day": valley_day,
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

    def get_export_record(self, export_id: int) -> ReportExportRecord | None:
        stmt = select(ReportExportRecord).where(
            ReportExportRecord.id == export_id,
            ReportExportRecord.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

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
