import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


pytestmark = pytest.mark.skipif(
    not os.getenv("MYSQL_TEST_DATABASE_URL"),
    reason="MYSQL_TEST_DATABASE_URL is not configured",
)


@pytest.fixture(scope="module")
def mysql_client():
    database_url = os.environ["MYSQL_TEST_DATABASE_URL"]
    os.environ["DATABASE_URL"] = database_url
    os.environ["DIFY_MOCK_ENABLED"] = "true"

    from app.core.config import get_settings

    get_settings.cache_clear()
    engine = create_engine(database_url, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    from app.db.session import get_db
    from app.main import create_app

    app = create_app()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
    get_settings.cache_clear()


def test_mysql_ai_tool_returns_seeded_report_source_data(mysql_client):
    response = mysql_client.post(
        "/api/v1/ai-tools/query_report_source_data",
        json={
            "report_type": "student_psych_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 10,
            "conversation_id": "mysql-conv",
            "trace_id": "mysql-trace",
        },
    )

    assert response.status_code == 200
    result = response.json()["data"]["result"]
    assert result["total_profiles"] >= 2
    assert result["total_alerts"] >= 2


def test_mysql_five_report_types_generate_drafts(mysql_client):
    headers = {"X-User-Id": "1", "X-User-Role": "admin"}
    for report_type in [
        "complaint_weekly",
        "customer_operation",
        "employee_daily_summary",
        "employee_weekly_summary",
        "student_psych_weekly",
    ]:
        response = mysql_client.post(
            "/api/v1/reports/generate-draft",
            json={
                "report_type": report_type,
                "date_start": "2026-06-01",
                "date_end": "2026-06-07",
                "department_id": 10,
                "owner_user_id": 102 if report_type == "customer_operation" else None,
            },
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["data"]["content_json"]["report_type"] == report_type


def test_mysql_generate_publish_export_download_flow(mysql_client):
    headers = {"X-User-Id": "1", "X-User-Role": "admin"}
    generate_response = mysql_client.post(
        "/api/v1/reports/generate-draft",
        json={
            "report_type": "complaint_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 10,
        },
        headers=headers,
    )
    assert generate_response.status_code == 200
    draft_id = generate_response.json()["data"]["id"]

    confirm_response = mysql_client.post(f"/api/v1/reports/drafts/{draft_id}/confirm", headers=headers)
    assert confirm_response.status_code == 200
    report_id = confirm_response.json()["data"]["id"]

    publish_response = mysql_client.post(f"/api/v1/reports/{report_id}/publish", headers=headers)
    assert publish_response.status_code == 200

    export_response = mysql_client.post(
        f"/api/v1/reports/{report_id}/exports",
        json={"export_type": "word"},
        headers=headers,
    )
    assert export_response.status_code == 200
    export_id = export_response.json()["data"]["id"]

    download_response = mysql_client.get(f"/api/v1/reports/exports/{export_id}/download", headers=headers)
    assert download_response.status_code == 200
    assert download_response.content.startswith(b"PK")
