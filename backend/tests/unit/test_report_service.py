from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.common.enums import ExportType, ReportType
from app.common.exceptions import ReportGenerationError
from app.core.config import Settings
from app.core.security import CurrentUser
from app.models.audit_log import AuditLog
from app.models.draft import AiDraft
from app.models.report import ReportExportRecord
from app.schemas.report_schema import ReportGenerateDraftRequest
from app.services.report_service import ReportService


class FailingDifyClient:
    def generate_report_draft(self, report_type, source_data, filters, trace_id=None):
        raise RuntimeError("Dify 模拟失败")


def build_request(report_type=ReportType.COMPLAINT_WEEKLY):
    return ReportGenerateDraftRequest(
        report_type=report_type,
        date_start=date(2026, 6, 1),
        date_end=date(2026, 6, 7),
        department_id=1,
        owner_user_id=2 if report_type == ReportType.CUSTOMER_OPERATION else None,
    )


def test_admin_generate_complaint_weekly_draft(db_session):
    service = ReportService(db_session)

    draft = service.generate_draft(build_request(), CurrentUser(id=1, role="admin"))

    assert draft["status"] == "pending_confirm"
    assert draft["content_json"]["title"] == "投诉处理周报"


def test_employee_generate_customer_operation_draft(db_session):
    service = ReportService(db_session)

    draft = service.generate_draft(
        build_request(ReportType.CUSTOMER_OPERATION),
        CurrentUser(id=2, role="employee"),
    )

    assert draft["status"] == "pending_confirm"
    assert draft["content_json"]["title"] == "客户经营分析报"


def test_employee_cannot_publish_report(db_session):
    service = ReportService(db_session)
    draft = service.generate_draft(build_request(), CurrentUser(id=1, role="admin"))
    report = service.confirm_draft(draft["id"], CurrentUser(id=1, role="admin"))

    with pytest.raises(HTTPException) as exc_info:
        service.publish_report(report["id"], CurrentUser(id=2, role="employee"))

    assert exc_info.value.status_code == 403


def test_admin_confirm_draft_creates_ai_report(db_session):
    service = ReportService(db_session)
    draft = service.generate_draft(build_request(), CurrentUser(id=1, role="admin"))

    report = service.confirm_draft(draft["id"], CurrentUser(id=1, role="admin"))

    assert report["title"] == "投诉处理周报"
    assert report["status"] == "confirmed"
    assert report["source_draft_id"] == draft["id"]


def test_dify_failure_creates_failed_draft_and_audit_log(db_session):
    service = ReportService(db_session, dify_client=FailingDifyClient())

    with pytest.raises(ReportGenerationError):
        service.generate_draft(build_request(), CurrentUser(id=1, role="admin"))

    failed_draft = db_session.query(AiDraft).filter(AiDraft.status == "generation_failed").one()
    failed_log = db_session.query(AuditLog).filter(AuditLog.result == "fail").one()
    assert failed_draft.content_json["error_message"] == "Dify 模拟失败"
    assert failed_log.error_message == "Dify 模拟失败"


def test_export_word_creates_file_and_record(db_session):
    export_dir = Path("storage/test_reports") / uuid4().hex
    settings = Settings(report_export_dir=str(export_dir), dify_mock_enabled=True)
    service = ReportService(db_session, settings=settings)
    draft = service.generate_draft(build_request(), CurrentUser(id=1, role="admin"))
    report = service.confirm_draft(draft["id"], CurrentUser(id=1, role="admin"))
    service.publish_report(report["id"], CurrentUser(id=1, role="admin"))

    export = service.export_report(report["id"], ExportType.WORD, CurrentUser(id=1, role="admin"))

    assert export["status"] == "success"
    assert Path(export["file_path"]).exists()


def test_export_pdf_failure_writes_record_and_audit_log(db_session):
    export_dir = Path("storage/test_reports") / uuid4().hex
    settings = Settings(report_export_dir=str(export_dir), report_pdf_converter_path="", dify_mock_enabled=True)
    service = ReportService(db_session, settings=settings)
    draft = service.generate_draft(build_request(), CurrentUser(id=1, role="admin"))
    report = service.confirm_draft(draft["id"], CurrentUser(id=1, role="admin"))
    service.publish_report(report["id"], CurrentUser(id=1, role="admin"))

    with pytest.raises(HTTPException) as exc_info:
        service.export_report(report["id"], ExportType.PDF, CurrentUser(id=1, role="admin"))

    assert exc_info.value.status_code == 500
    failed_record = db_session.query(ReportExportRecord).filter(ReportExportRecord.status == "fail").one()
    failed_log = db_session.query(AuditLog).filter(AuditLog.action_type == "export", AuditLog.result == "fail").one()
    assert "PDF 转换器" in failed_record.error_message
    assert "PDF 转换器" in failed_log.error_message
