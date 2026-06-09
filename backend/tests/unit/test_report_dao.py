from datetime import date

from app.common.enums import ReportType
from app.daos.report_dao import ReportDAO


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
