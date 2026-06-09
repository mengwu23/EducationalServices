from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.enums import ReportType
from app.models.audit_log import AiToolCallLog, AuditLog
from app.models.business import (
    CrmLead,
    CustomerAnalysisRecord,
    EmployeeProfile,
    EventRegistration,
    StudentFeedbackTicket,
)
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
            .where(func.date(StudentFeedbackTicket.create_time).between(date_start, date_end))
            .group_by(StudentFeedbackTicket.status)
        )
        if department_id is not None:
            stmt = stmt.where(EmployeeProfile.department_id == department_id)
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
        lead_stmt = select(func.count(CrmLead.id)).where(func.date(CrmLead.create_time).between(date_start, date_end))
        analysis_stmt = (
            select(func.count(CustomerAnalysisRecord.id))
            .join(CrmLead, CustomerAnalysisRecord.lead_id == CrmLead.id)
            .where(func.date(CustomerAnalysisRecord.create_time).between(date_start, date_end))
        )
        registration_stmt = (
            select(func.count(EventRegistration.id))
            .join(CrmLead, EventRegistration.lead_id == CrmLead.id)
            .where(EventRegistration.register_date.between(date_start, date_end))
        )
        if department_id is not None:
            lead_stmt = lead_stmt.where(CrmLead.department_id == department_id)
            analysis_stmt = analysis_stmt.where(CrmLead.department_id == department_id)
            registration_stmt = registration_stmt.where(CrmLead.department_id == department_id)
        if owner_user_id is not None:
            lead_stmt = lead_stmt.where(CrmLead.owner_user_id == owner_user_id)
            analysis_stmt = analysis_stmt.where(CrmLead.owner_user_id == owner_user_id)
            registration_stmt = registration_stmt.where(CrmLead.owner_user_id == owner_user_id)

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

    def add_draft(self, draft: AiDraft) -> AiDraft:
        self.db.add(draft)
        self.db.flush()
        return draft

    def get_draft(self, draft_id: int) -> AiDraft | None:
        return self.db.get(AiDraft, draft_id)

    def list_report_drafts(self) -> list[AiDraft]:
        stmt = select(AiDraft).where(AiDraft.biz_module == "report").order_by(AiDraft.create_time.desc())
        return list(self.db.scalars(stmt).all())

    def add_report(self, report: AiReport) -> AiReport:
        self.db.add(report)
        self.db.flush()
        return report

    def get_report(self, report_id: int) -> AiReport | None:
        return self.db.get(AiReport, report_id)

    def list_reports(self) -> list[AiReport]:
        stmt = select(AiReport).order_by(AiReport.create_time.desc())
        return list(self.db.scalars(stmt).all())

    def add_export_record(self, record: ReportExportRecord) -> ReportExportRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def list_export_records(self, report_id: int) -> list[ReportExportRecord]:
        stmt = (
            select(ReportExportRecord)
            .where(ReportExportRecord.report_id == report_id)
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
