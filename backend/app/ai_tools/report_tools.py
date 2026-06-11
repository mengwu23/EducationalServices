from sqlalchemy.orm import Session

from backend.app.services.report_service import ReportService


def query_report_source_data(
    db: Session,
    report_type,
    date_start,
    date_end,
    department_id: int | None,
    owner_user_id: int | None,
    caller: str,
    conversation_id: str | None,
    trace_id: str | None,
) -> dict:
    service = ReportService(db)
    return service.query_source_data_for_tool(
        report_type,
        date_start,
        date_end,
        department_id,
        owner_user_id,
        caller,
        conversation_id,
        trace_id,
    )
