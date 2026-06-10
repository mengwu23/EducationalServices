from datetime import date, datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.enums import DraftStatus, ExportStatus, ExportType, ReportStatus
from app.common.exceptions import BusinessError, NotFoundError, ReportGenerationError
from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, require_roles
from app.daos.report_dao import ReportDAO
from app.integrations.dify_client import DifyClient
from app.models.report import AiReport, ReportExportRecord
from app.schemas.report_schema import ReportGenerateDraftRequest
from app.services.audit_log_service import AuditLogService
from app.services.draft_service import DraftService
from app.services.report_export_service import ReportExportService


class ReportService:
    def __init__(
        self,
        db: Session,
        dify_client: DifyClient | None = None,
        settings: Settings | None = None,
    ):
        self.db = db
        self.settings = settings or get_settings()
        self.dao = ReportDAO(db)
        self.draft_service = DraftService(db)
        self.audit_service = AuditLogService(db)
        self.dify_client = dify_client or DifyClient(self.settings)
        self.export_service = ReportExportService(self.settings)

    def generate_draft(self, request: ReportGenerateDraftRequest, user: CurrentUser) -> dict[str, Any]:
        require_roles(user, {"admin", "employee"})
        trace_id = request.trace_id or f"report-{uuid4().hex}"
        filters = {
            "date_start": request.date_start.isoformat(),
            "date_end": request.date_end.isoformat(),
            "department_id": request.department_id,
            "owner_user_id": request.owner_user_id,
        }
        try:
            source_data = self.dao.query_report_source_data(
                request.report_type,
                request.date_start,
                request.date_end,
                request.department_id,
                request.owner_user_id,
            )
            draft_content = self.dify_client.generate_report_draft(
                request.report_type,
                source_data,
                filters,
                trace_id,
            )
            content_json = {
                **draft_content,
                "report_type": request.report_type,
                "filters": filters,
                "source_data": source_data,
            }
            draft = self.draft_service.create_report_draft(content_json, user, DraftStatus.PENDING_CONFIRM, trace_id)
            self.audit_service.record(
                user,
                action_type="generate_draft",
                biz_object_type="ai_draft",
                biz_object_id=draft.id,
                draft_id=draft.id,
                trace_id=trace_id,
                after_json={"report_type": request.report_type, "status": draft.status},
            )
            self.db.commit()
            self.db.refresh(draft)
            return self._draft_to_dict(draft)
        except Exception as exc:
            self.db.rollback()
            failed_draft = self.draft_service.create_report_draft(
                {
                    "report_type": request.report_type,
                    "filters": filters,
                    "error_message": str(exc),
                },
                user,
                DraftStatus.GENERATION_FAILED,
                trace_id,
            )
            self.audit_service.record(
                user,
                action_type="generate_draft",
                biz_object_type="ai_draft",
                biz_object_id=failed_draft.id,
                draft_id=failed_draft.id,
                trace_id=trace_id,
                result="fail",
                error_message=str(exc),
            )
            self.db.commit()
            raise ReportGenerationError(f"报告草稿生成失败：{exc}") from exc

    def list_drafts(self, user: CurrentUser) -> list[dict[str, Any]]:
        require_roles(user, {"admin", "employee"})
        drafts = self.draft_service.list_report_drafts()
        if user.role == "employee":
            drafts = [draft for draft in drafts if draft.created_by == user.id]
        return [self._draft_to_dict(draft) for draft in drafts]

    def get_draft(self, draft_id: int, user: CurrentUser) -> dict[str, Any]:
        require_roles(user, {"admin", "employee"})
        draft = self._get_visible_draft(draft_id, user)
        return self._draft_to_dict(draft)

    def reject_draft(self, draft_id: int, reason: str, user: CurrentUser) -> dict[str, Any]:
        require_roles(user, {"admin"})
        draft = self._get_visible_draft(draft_id, user)
        if draft.status != DraftStatus.PENDING_CONFIRM:
            raise BusinessError("只有待确认报告草稿可以驳回")
        self.draft_service.reject(draft, user, reason)
        self.audit_service.record(
            user,
            action_type="reject",
            biz_object_type="ai_draft",
            biz_object_id=draft.id,
            draft_id=draft.id,
            trace_id=draft.source_trace_id,
            after_json={"reason": reason, "status": draft.status},
        )
        self.db.commit()
        self.db.refresh(draft)
        return self._draft_to_dict(draft)

    def confirm_draft(self, draft_id: int, user: CurrentUser) -> dict[str, Any]:
        require_roles(user, {"admin"})
        draft = self._get_visible_draft(draft_id, user)
        if draft.status != DraftStatus.PENDING_CONFIRM:
            raise BusinessError("只有待确认报告草稿可以确认")
        content = draft.content_json
        filters = content.get("filters", {})
        report = self.dao.add_report(
            AiReport(
                report_no=f"RP-{datetime.now():%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
                report_type=content.get("report_type", "unknown"),
                title=content.get("title", "未命名报告"),
                status=ReportStatus.CONFIRMED,
                content_json=content,
                source_draft_id=draft.id,
                date_start=date.fromisoformat(filters["date_start"]),
                date_end=date.fromisoformat(filters["date_end"]),
                department_id=filters.get("department_id"),
                created_by=user.id,
            )
        )
        self.draft_service.mark_confirmed(draft, user)
        self.audit_service.record(
            user,
            action_type="confirm",
            biz_object_type="ai_report",
            biz_object_id=report.id,
            draft_id=draft.id,
            trace_id=draft.source_trace_id,
            after_json={"report_id": report.id, "status": report.status},
        )
        self.db.commit()
        self.db.refresh(report)
        return self._report_to_dict(report)

    def list_reports(self, user: CurrentUser) -> list[dict[str, Any]]:
        require_roles(user, {"admin", "employee"})
        reports = self.dao.list_reports()
        if user.role == "employee":
            reports = [report for report in reports if report.created_by == user.id]
        return [self._report_to_dict(report) for report in reports]

    def get_report(self, report_id: int, user: CurrentUser) -> dict[str, Any]:
        require_roles(user, {"admin", "employee"})
        report = self._get_visible_report(report_id, user)
        return self._report_to_dict(report)

    def publish_report(self, report_id: int, user: CurrentUser) -> dict[str, Any]:
        require_roles(user, {"admin"})
        report = self._get_visible_report(report_id, user)
        if report.status == ReportStatus.PUBLISHED:
            return self._report_to_dict(report)
        report.status = ReportStatus.PUBLISHED
        report.published_by = user.id
        report.published_time = datetime.now()
        self.audit_service.record(
            user,
            action_type="publish",
            biz_object_type="ai_report",
            biz_object_id=report.id,
            draft_id=report.source_draft_id,
            after_json={"status": report.status},
        )
        self.db.commit()
        self.db.refresh(report)
        return self._report_to_dict(report)

    def export_report(self, report_id: int, export_type: str, user: CurrentUser) -> dict[str, Any]:
        require_roles(user, {"admin"})
        report = self._get_visible_report(report_id, user)
        if report.status != ReportStatus.PUBLISHED:
            raise BusinessError("只有已发布报告可以导出")
        try:
            file_name, file_path = self.export_service.export(report, export_type)
            record = self.dao.add_export_record(
                ReportExportRecord(
                    report_id=report.id,
                    export_type=export_type,
                    file_name=file_name,
                    file_path=file_path,
                    status=ExportStatus.SUCCESS,
                    created_by=user.id,
                )
            )
            self.audit_service.record(
                user,
                action_type="export",
                biz_object_type="ai_report",
                biz_object_id=report.id,
                draft_id=report.source_draft_id,
                after_json={"export_type": export_type, "file_path": file_path},
            )
            self.db.commit()
            self.db.refresh(record)
            return self._export_to_dict(record)
        except Exception as exc:
            record = self.dao.add_export_record(
                ReportExportRecord(
                    report_id=report.id,
                    export_type=export_type,
                    file_name=f"{report.report_no}.{self._export_extension(export_type)}",
                    file_path="",
                    status=ExportStatus.FAIL,
                    error_message=str(exc),
                    created_by=user.id,
                )
            )
            self.audit_service.record(
                user,
                action_type="export",
                biz_object_type="ai_report",
                biz_object_id=report.id,
                draft_id=report.source_draft_id,
                result="fail",
                error_message=str(exc),
                after_json={"export_type": export_type},
            )
            self.db.commit()
            self.db.refresh(record)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"报告导出失败：{exc}",
            ) from exc

    def list_export_records(self, report_id: int, user: CurrentUser) -> list[dict[str, Any]]:
        require_roles(user, {"admin", "employee"})
        self._get_visible_report(report_id, user)
        return [self._export_to_dict(record) for record in self.dao.list_export_records(report_id)]

    def query_source_data_for_tool(
        self,
        report_type: str,
        date_start,
        date_end,
        department_id: int | None,
        owner_user_id: int | None,
        caller: str,
        conversation_id: str | None,
        trace_id: str | None,
    ) -> dict[str, Any]:
        arguments = {
            "report_type": report_type,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "owner_user_id": owner_user_id,
        }
        try:
            result = self.dao.query_report_source_data(report_type, date_start, date_end, department_id, owner_user_id)
            self.audit_service.record_tool_call(
                "query_report_source_data",
                arguments,
                result,
                caller=caller,
                conversation_id=conversation_id,
                trace_id=trace_id,
            )
            self.db.commit()
            return result
        except Exception as exc:
            self.audit_service.record_tool_call(
                "query_report_source_data",
                arguments,
                None,
                caller=caller,
                conversation_id=conversation_id,
                trace_id=trace_id,
                status="fail",
                error_message=str(exc),
            )
            self.db.commit()
            raise

    def _get_visible_draft(self, draft_id: int, user: CurrentUser):
        draft = self.draft_service.get_report_draft(draft_id)
        if not draft:
            raise NotFoundError("报告草稿不存在")
        if user.role == "employee" and draft.created_by != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该报告草稿")
        return draft

    def _get_visible_report(self, report_id: int, user: CurrentUser):
        report = self.dao.get_report(report_id)
        if not report:
            raise NotFoundError("报告不存在")
        if user.role == "employee" and report.created_by != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该报告")
        return report

    def _draft_to_dict(self, draft) -> dict[str, Any]:
        return {
            "id": draft.id,
            "draft_no": draft.draft_no,
            "status": draft.status,
            "content_json": draft.content_json,
            "trace_id": draft.source_trace_id,
        }

    def _report_to_dict(self, report: AiReport) -> dict[str, Any]:
        return {
            "id": report.id,
            "report_no": report.report_no,
            "report_type": report.report_type,
            "title": report.title,
            "status": report.status,
            "content_json": report.content_json,
            "source_draft_id": report.source_draft_id,
            "date_start": report.date_start,
            "date_end": report.date_end,
            "department_id": report.department_id,
            "created_by": report.created_by,
            "published_by": report.published_by,
            "published_time": report.published_time,
        }

    def _export_to_dict(self, record: ReportExportRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "report_id": record.report_id,
            "export_type": record.export_type,
            "file_name": record.file_name,
            "file_path": record.file_path,
            "status": record.status,
            "error_message": record.error_message,
        }

    def _export_extension(self, export_type: str) -> str:
        return "pdf" if export_type == ExportType.PDF else "docx"
