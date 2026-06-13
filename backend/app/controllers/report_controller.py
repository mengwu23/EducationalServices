from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.common.responses import success
from backend.app.core.security import CurrentUser, require_permissions
from backend.app.db.session import get_db
from backend.app.schemas.report_schema import ReportExportRequest, ReportGenerateDraftRequest, ReportRejectRequest
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.post("/generate-draft")
def generate_draft(
    request: ReportGenerateDraftRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("report:generate")),
):
    data = ReportService(db).generate_draft(request, user)
    return success(data, trace_id=data.get("trace_id"))


@router.get("/drafts")
def list_drafts(db: Session = Depends(get_db), user: CurrentUser = Depends(require_permissions("report:read"))):
    return success(ReportService(db).list_drafts(user))


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permissions("report:read"))):
    return success(ReportService(db).get_draft(draft_id, user))


@router.post("/drafts/{draft_id}/confirm")
def confirm_draft(draft_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permissions("report:review"))):
    return success(ReportService(db).confirm_draft(draft_id, user))


@router.post("/drafts/{draft_id}/reject")
def reject_draft(
    draft_id: int,
    request: ReportRejectRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("report:review")),
):
    return success(ReportService(db).reject_draft(draft_id, request.reason, user))


@router.get("")
def list_reports(db: Session = Depends(get_db), user: CurrentUser = Depends(require_permissions("report:read"))):
    return success(ReportService(db).list_reports(user))


@router.get("/exports/{export_id}/download")
def download_export_file(
    export_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("report:export")),
):
    download = ReportService(db).prepare_export_download(export_id, user)
    return FileResponse(
        path=download["file_path"],
        media_type=download["media_type"],
        filename=download["file_name"],
    )


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permissions("report:read"))):
    return success(ReportService(db).get_report(report_id, user))


@router.post("/{report_id}/publish")
def publish_report(report_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(require_permissions("report:review"))):
    return success(ReportService(db).publish_report(report_id, user))


@router.post("/{report_id}/exports")
def export_report(
    report_id: int,
    request: ReportExportRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("report:export")),
):
    return success(ReportService(db).export_report(report_id, request.export_type, user))


@router.get("/{report_id}/exports")
def list_export_records(
    report_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("report:read")),
):
    return success(ReportService(db).list_export_records(report_id, user))
