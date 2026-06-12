from backend.app.models.crm_lead import CrmLead
from backend.app.models.student_profile import StudentProfile
from backend.app.services.application_progress_service import ApplicationProgressService


def test_sync_from_crm_creates_student_and_progress(db_session):
    service = ApplicationProgressService(db_session)

    result = service.sync_from_crm(crm_system="crm_lead", crm_record_id="LEAD001")

    progress = result["progress"]
    assert result["sync_direction"] == "to_local"
    assert result["action"] == "created"
    assert progress.crm_record_id == "1"
    assert progress.crm_sync_status == "synced"
    assert progress.progress_stage == "school_apply"
    assert progress.progress_status == "pending"
    assert progress.student_name == "王家长"

    student = db_session.query(StudentProfile).filter(StudentProfile.student_no == "CRM-LEAD001").one()
    assert student.student_name == "王家长"


def test_sync_to_crm_updates_lead_follow_up(db_session):
    service = ApplicationProgressService(db_session)
    local_result = service.sync_from_crm(crm_system="crm_lead", crm_record_id="LEAD001")
    progress_id = local_result["progress"].id

    result = service.sync_to_crm(
        progress_id=progress_id,
        crm_system="crm_lead",
        crm_record_id="LEAD001",
    )

    assert result["sync_direction"] == "to_crm"
    assert result["action"] == "updated"

    lead = db_session.get(CrmLead, 1)
    assert lead.latest_follow_up_summary is not None
    assert "申请进度更新" in lead.latest_follow_up_summary
    assert lead.follow_up_history is not None
    assert "申请进度更新" in lead.follow_up_history
    assert lead.last_follow_up_time is not None
    assert result["progress"].crm_sync_status == "synced"


def test_crm_sync_endpoint_to_local(client):
    response = client.post(
        "/api/application-progress/crm/sync",
        json={
            "crm_system": "crm_lead",
            "crm_record_id": "LEAD001",
            "sync_direction": "to_local",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["message"] == "同步完成"
    assert body["data"]["sync_direction"] == "to_local"
    assert body["data"]["progress"]["crm_sync_status"] == "synced"
