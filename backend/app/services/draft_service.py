from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.common.enums import DraftStatus
from app.core.security import CurrentUser
from app.daos.report_dao import ReportDAO
from app.models.draft import AiDraft


class DraftService:
    def __init__(self, db: Session):
        self.dao = ReportDAO(db)

    def create_report_draft(
        self,
        content_json: dict,
        user: CurrentUser,
        status: DraftStatus = DraftStatus.PENDING_CONFIRM,
        trace_id: str | None = None,
    ) -> AiDraft:
        return self.dao.add_draft(
            AiDraft(
                draft_no=f"DR-{datetime.now():%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
                draft_type="report",
                biz_module="report",
                status=status,
                content_json=content_json,
                source_trace_id=trace_id,
                created_by=user.id,
            )
        )

    def get_report_draft(self, draft_id: int) -> AiDraft | None:
        draft = self.dao.get_draft(draft_id)
        if draft and draft.biz_module == "report":
            return draft
        return None

    def list_report_drafts(self) -> list[AiDraft]:
        return self.dao.list_report_drafts()

    def mark_confirmed(self, draft: AiDraft, user: CurrentUser) -> AiDraft:
        draft.status = DraftStatus.CONFIRMED
        draft.confirmed_by = user.id
        draft.confirmed_time = datetime.now()
        return draft

    def reject(self, draft: AiDraft, user: CurrentUser, reason: str) -> AiDraft:
        draft.status = DraftStatus.REJECTED
        draft.confirmed_by = user.id
        draft.confirmed_time = datetime.now()
        draft.reject_reason = reason
        return draft
