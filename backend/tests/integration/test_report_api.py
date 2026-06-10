from app.core.config import get_settings
from app.models.audit_log import AiToolCallLog


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
