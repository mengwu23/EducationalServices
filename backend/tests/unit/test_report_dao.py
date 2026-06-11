from datetime import date

from backend.app.common.enums import ReportType
from backend.app.daos.report_dao import ReportDAO
from backend.app.models.draft import AiDraft
from backend.app.models.report import AiReport, ReportExportRecord


def test_query_complaint_weekly_by_date_and_department(db_session):
    dao = ReportDAO(db_session)

    result = dao.query_report_source_data(
        ReportType.COMPLAINT_WEEKLY,
        date(2026, 6, 1),
        date(2026, 6, 7),
        department_id=1,
    )

    assert result["total_tickets"] == 2
    assert result["status_counts"] == {"closed": 1, "open": 1}


def test_query_customer_operation_by_owner(db_session):
    dao = ReportDAO(db_session)

    result = dao.query_report_source_data(
        ReportType.CUSTOMER_OPERATION,
        date(2026, 6, 1),
        date(2026, 6, 7),
        department_id=1,
        owner_user_id=2,
    )

    assert result["new_leads"] == 1
    assert result["analysis_records"] == 1
    assert result["event_registrations"] == 1


def test_query_employee_daily_summary_by_single_date_and_department(db_session):
    dao = ReportDAO(db_session)

    result = dao.query_report_source_data(
        ReportType.EMPLOYEE_DAILY_SUMMARY,
        date(2026, 6, 2),
        date(2026, 6, 2),
        department_id=1,
    )

    assert result["total_reports"] == 2
    assert result["status_counts"] == {"draft": 1, "submitted": 1}
    assert result["submitted_reports"] == 1
    assert result["draft_reports"] == 1
    assert result["archived_reports"] == 0
    assert result["risk_reports"] == 1
    assert result["tomorrow_plan_reports"] == 2


def test_query_employee_weekly_summary_by_date_range_and_department(db_session):
    dao = ReportDAO(db_session)

    result = dao.query_report_source_data(
        ReportType.EMPLOYEE_WEEKLY_SUMMARY,
        date(2026, 6, 1),
        date(2026, 6, 7),
        department_id=1,
    )

    assert result["total_reports"] == 3
    assert result["distinct_employees"] == 2
    assert result["status_counts"] == {"archived": 1, "draft": 1, "submitted": 1}
    assert result["daily_trend"] == {"2026-06-02": 2, "2026-06-03": 1}
    assert result["risk_reports"] == 2


def test_query_student_psych_weekly_by_department(db_session):
    dao = ReportDAO(db_session)

    result = dao.query_report_source_data(
        ReportType.STUDENT_PSYCH_WEEKLY,
        date(2026, 6, 1),
        date(2026, 6, 7),
        department_id=1,
    )

    assert result["total_profiles"] == 2
    assert result["risk_level_counts"] == {"high": 1, "medium": 1}
    assert result["emotion_tag_counts"] == {"anxious": 1, "stable": 1}
    assert result["average_emotion_score"] == 55
    assert result["total_alerts"] == 2
    assert result["alert_status_counts"] == {"pending": 1, "resolved": 1}
    assert result["alert_risk_level_counts"] == {"high": 1, "medium": 1}


def test_dao_filters_soft_deleted_drafts_reports_and_exports(db_session):
    dao = ReportDAO(db_session)
    deleted_draft = dao.add_draft(
        AiDraft(
            draft_no="DR-DELETED",
            draft_type="report",
            biz_module="report",
            status="pending_confirm",
            content_json={"title": "已删除草稿"},
            created_by=1,
            is_deleted=True,
        )
    )
    deleted_report = dao.add_report(
        AiReport(
            report_no="RP-DELETED",
            report_type="complaint_weekly",
            title="已删除报告",
            status="confirmed",
            content_json={"title": "已删除报告"},
            source_draft_id=deleted_draft.id,
            date_start=date(2026, 6, 1),
            date_end=date(2026, 6, 7),
            created_by=1,
            is_deleted=True,
        )
    )
    active_draft = dao.add_draft(
        AiDraft(
            draft_no="DR-ACTIVE",
            draft_type="report",
            biz_module="report",
            status="pending_confirm",
            content_json={"title": "有效草稿"},
            created_by=1,
        )
    )
    active_report = dao.add_report(
        AiReport(
            report_no="RP-ACTIVE",
            report_type="complaint_weekly",
            title="有效报告",
            status="confirmed",
            content_json={"title": "有效报告"},
            source_draft_id=active_draft.id,
            date_start=date(2026, 6, 1),
            date_end=date(2026, 6, 7),
            created_by=1,
        )
    )
    deleted_export = dao.add_export_record(
        ReportExportRecord(
            report_id=active_report.id,
            export_type="word",
            file_name="deleted.docx",
            file_path="storage/deleted.docx",
            status="success",
            created_by=1,
            is_deleted=True,
        )
    )
    db_session.commit()

    assert dao.get_draft(deleted_draft.id) is None
    assert deleted_draft.id not in [draft.id for draft in dao.list_report_drafts()]
    assert dao.get_report(deleted_report.id) is None
    assert deleted_report.id not in [report.id for report in dao.list_reports()]
    assert deleted_export.id not in [record.id for record in dao.list_export_records(active_report.id)]
