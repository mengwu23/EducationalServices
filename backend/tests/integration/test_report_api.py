from datetime import date
from pathlib import Path
from uuid import uuid4

from app.common.enums import DraftStatus, ExportStatus, ExportType, ReportStatus
from app.core.config import get_settings
from app.models.audit_log import AiToolCallLog, AuditLog
from app.models.draft import AiDraft
from app.models.report import AiReport, ReportExportRecord


def create_published_export(client, export_type: str = "word"):
    headers = {"X-User-Id": "1", "X-User-Role": "admin"}
    generate_response = client.post(
        "/api/v1/reports/generate-draft",
        json={
            "report_type": "complaint_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 1,
        },
        headers=headers,
    )
    assert generate_response.status_code == 200
    draft_id = generate_response.json()["data"]["id"]

    confirm_response = client.post(f"/api/v1/reports/drafts/{draft_id}/confirm", headers=headers)
    assert confirm_response.status_code == 200
    report_id = confirm_response.json()["data"]["id"]

    publish_response = client.post(f"/api/v1/reports/{report_id}/publish", headers=headers)
    assert publish_response.status_code == 200

    export_response = client.post(
        f"/api/v1/reports/{report_id}/exports",
        json={"export_type": export_type},
        headers=headers,
    )
    assert export_response.status_code == 200
    return export_response.json()["data"], headers


def test_generate_draft_api_supports_five_report_types(client):
    headers = {"X-User-Id": "1", "X-User-Role": "admin"}
    report_types = [
        "complaint_weekly",
        "customer_operation",
        "employee_daily_summary",
        "employee_weekly_summary",
        "student_psych_weekly",
    ]

    for report_type in report_types:
        response = client.post(
            "/api/v1/reports/generate-draft",
            json={
                "report_type": report_type,
                "date_start": "2026-06-01",
                "date_end": "2026-06-07",
                "department_id": 1,
                "owner_user_id": 2 if report_type == "customer_operation" else None,
            },
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["data"]["content_json"]["report_type"] == report_type


def test_generate_confirm_publish_export_word_flow(client):
    headers = {"X-User-Id": "1", "X-User-Role": "admin"}
    generate_response = client.post(
        "/api/v1/reports/generate-draft",
        json={
            "report_type": "complaint_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 1,
        },
        headers=headers,
    )
    assert generate_response.status_code == 200
    draft_id = generate_response.json()["data"]["id"]

    confirm_response = client.post(f"/api/v1/reports/drafts/{draft_id}/confirm", headers=headers)
    assert confirm_response.status_code == 200
    report_id = confirm_response.json()["data"]["id"]

    publish_response = client.post(f"/api/v1/reports/{report_id}/publish", headers=headers)
    assert publish_response.status_code == 200
    assert publish_response.json()["data"]["status"] == "published"

    export_response = client.post(
        f"/api/v1/reports/{report_id}/exports",
        json={"export_type": "word"},
        headers=headers,
    )
    assert export_response.status_code == 200
    assert export_response.json()["data"]["status"] == "success"


def test_download_word_export_file(client, db_session):
    export_data, headers = create_published_export(client, "word")

    response = client.get(f"/api/v1/reports/exports/{export_data['id']}/download", headers=headers)

    assert response.status_code == 200
    assert response.content.startswith(b"PK")
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
    audit_log = db_session.query(AuditLog).filter(AuditLog.action_type == "download_export").one()
    assert audit_log.result == "success"


def test_download_pdf_export_file(client):
    export_data, headers = create_published_export(client, "pdf")

    response = client.get(f"/api/v1/reports/exports/{export_data['id']}/download", headers=headers)

    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
    assert "application/pdf" in response.headers["content-type"]


def test_employee_can_download_own_export_record(client, db_session):
    export_dir = Path("storage/reports")
    export_dir.mkdir(parents=True, exist_ok=True)
    file_path = export_dir / f"employee-{uuid4().hex}.docx"
    file_path.write_bytes(b"PK employee report")
    draft = AiDraft(
        draft_no=f"DR-{uuid4().hex}",
        draft_type="report",
        biz_module="report",
        status=DraftStatus.CONFIRMED,
        content_json={},
        created_by=2,
        confirmed_by=1,
    )
    db_session.add(draft)
    db_session.flush()
    report = AiReport(
        report_no=f"RP-{uuid4().hex}",
        report_type="complaint_weekly",
        title="员工报告",
        status=ReportStatus.PUBLISHED,
        content_json={},
        source_draft_id=draft.id,
        date_start=date(2026, 6, 1),
        date_end=date(2026, 6, 7),
        department_id=1,
        created_by=2,
        published_by=1,
    )
    db_session.add(report)
    db_session.flush()
    record = ReportExportRecord(
        report_id=report.id,
        export_type=ExportType.WORD,
        file_name=file_path.name,
        file_path=str(file_path),
        status=ExportStatus.SUCCESS,
        created_by=1,
    )
    db_session.add(record)
    db_session.commit()

    response = client.get(
        f"/api/v1/reports/exports/{record.id}/download",
        headers={"X-User-Id": "2", "X-User-Role": "employee"},
    )

    assert response.status_code == 200
    assert response.content == b"PK employee report"


def test_employee_cannot_download_other_report_export(client):
    export_data, _headers = create_published_export(client, "word")

    response = client.get(
        f"/api/v1/reports/exports/{export_data['id']}/download",
        headers={"X-User-Id": "2", "X-User-Role": "employee"},
    )

    assert response.status_code == 403


def test_student_cannot_download_export(client):
    export_data, _headers = create_published_export(client, "word")

    response = client.get(
        f"/api/v1/reports/exports/{export_data['id']}/download",
        headers={"X-User-Id": "3", "X-User-Role": "student"},
    )

    assert response.status_code == 403


def test_download_failed_export_record_returns_error(client, db_session):
    export_data, headers = create_published_export(client, "word")
    record = db_session.get(ReportExportRecord, export_data["id"])
    record.status = ExportStatus.FAIL
    record.error_message = "export failed"
    db_session.commit()

    response = client.get(f"/api/v1/reports/exports/{record.id}/download", headers=headers)

    assert response.status_code == 400


def test_download_missing_file_returns_not_found_and_audit_log(client, db_session):
    export_data, headers = create_published_export(client, "word")
    record = db_session.get(ReportExportRecord, export_data["id"])
    Path(record.file_path).unlink()

    response = client.get(f"/api/v1/reports/exports/{record.id}/download", headers=headers)

    assert response.status_code == 404
    audit_log = db_session.query(AuditLog).filter(AuditLog.action_type == "download_export").one()
    assert audit_log.result == "fail"


def test_download_export_path_outside_export_dir_returns_forbidden(client, db_session):
    export_data, headers = create_published_export(client, "word")
    record = db_session.get(ReportExportRecord, export_data["id"])
    record.file_path = str(Path("outside-report.docx").resolve())
    db_session.commit()

    response = client.get(f"/api/v1/reports/exports/{record.id}/download", headers=headers)

    assert response.status_code == 403


def test_employee_cannot_publish_report_api(client):
    admin_headers = {"X-User-Id": "1", "X-User-Role": "admin"}
    employee_headers = {"X-User-Id": "2", "X-User-Role": "employee"}
    draft_response = client.post(
        "/api/v1/reports/generate-draft",
        json={
            "report_type": "complaint_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 1,
        },
        headers=admin_headers,
    )
    draft_id = draft_response.json()["data"]["id"]
    report_id = client.post(f"/api/v1/reports/drafts/{draft_id}/confirm", headers=admin_headers).json()["data"]["id"]

    response = client.post(f"/api/v1/reports/{report_id}/publish", headers=employee_headers)

    assert response.status_code == 403


def test_student_cannot_generate_report_api(client):
    response = client.post(
        "/api/v1/reports/generate-draft",
        json={
            "report_type": "complaint_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 1,
        },
        headers={"X-User-Id": "3", "X-User-Role": "student"},
    )

    assert response.status_code == 403


def test_missing_date_range_returns_validation_error(client):
    response = client.post(
        "/api/v1/reports/generate-draft",
        json={"report_type": "complaint_weekly", "department_id": 1},
        headers={"X-User-Id": "1", "X-User-Role": "admin"},
    )

    assert response.status_code == 422


def test_ai_tool_query_report_source_data_writes_log(client, db_session):
    response = client.post(
        "/api/v1/ai-tools/query_report_source_data",
        json={
            "report_type": "customer_operation",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 1,
            "owner_user_id": 2,
            "conversation_id": "conv-1",
            "trace_id": "trace-1",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["tool_name"] == "query_report_source_data"
    assert data["result"]["new_leads"] == 1
    tool_log = db_session.query(AiToolCallLog).filter(AiToolCallLog.tool_name == "query_report_source_data").one()
    assert tool_log.trace_id == "trace-1"


def test_ai_tool_query_report_source_data_supports_new_report_type(client):
    response = client.post(
        "/api/v1/ai-tools/query_report_source_data",
        json={
            "report_type": "student_psych_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 1,
            "conversation_id": "conv-psych",
            "trace_id": "trace-psych",
        },
    )

    assert response.status_code == 200
    result = response.json()["data"]["result"]
    assert result["total_profiles"] == 2
    assert result["total_alerts"] == 2


def test_ai_tool_secret_is_required_when_configured(client, monkeypatch):
    monkeypatch.setenv("AI_TOOLS_SECRET", "test-ai-tool-secret")
    get_settings.cache_clear()
    try:
        missing_response = client.get("/api/v1/ai-tools")
        assert missing_response.status_code == 401

        invalid_response = client.post(
            "/api/v1/ai-tools/query_report_source_data",
            headers={"X-AI-Tools-Secret": "wrong-secret"},
            json={
                "report_type": "complaint_weekly",
                "date_start": "2026-06-01",
                "date_end": "2026-06-07",
                "department_id": None,
                "owner_user_id": None,
                "conversation_id": "conv-secret",
                "trace_id": "trace-secret",
            },
        )
        assert invalid_response.status_code == 401

        valid_response = client.post(
            "/api/v1/ai-tools/query_report_source_data",
            headers={"X-AI-Tools-Secret": "test-ai-tool-secret"},
            json={
                "report_type": "complaint_weekly",
                "date_start": "2026-06-01",
                "date_end": "2026-06-07",
                "department_id": None,
                "owner_user_id": None,
                "conversation_id": "conv-secret",
                "trace_id": "trace-secret",
            },
        )
        assert valid_response.status_code == 200
        assert valid_response.json()["data"]["result"]["total_tickets"] == 2
    finally:
        get_settings.cache_clear()
