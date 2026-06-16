from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.security import CurrentUser
from backend.app.daos.report_dao import ReportDAO
from backend.app.models.audit_log import AiToolCallLog, AuditLog


class AuditLogService:
    def __init__(self, db: Session):
        self.dao = ReportDAO(db)

    def record(
        self,
        user: CurrentUser | None,
        action_type: str,
        biz_module: str = "report",
        biz_object_type: str | None = None,
        biz_object_id: int | None = None,
        draft_id: int | None = None,
        trace_id: str | None = None,
        result: str = "success",
        error_message: str | None = None,
        before_json: dict[str, Any] | None = None,
        after_json: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.dao.add_audit_log(
            AuditLog(
                operator_user_id=user.id if user else None,
                operator_role=user.role if user else None,
                action_type=action_type,
                biz_module=biz_module,
                biz_object_type=biz_object_type,
                biz_object_id=biz_object_id,
                before_json=before_json,
                after_json=after_json,
                draft_id=draft_id,
                trace_id=trace_id,
                result=result,
                error_message=error_message,
            )
        )

    def record_tool_call(
        self,
        tool_name: str,
        arguments_summary: dict[str, Any],
        result_summary: dict[str, Any] | None,
        caller: str = "dify",
        conversation_id: str | None = None,
        trace_id: str | None = None,
        draft_id: int | None = None,
        status: str = "success",
        error_message: str | None = None,
    ) -> AiToolCallLog | None:
        try:
            return self.dao.add_tool_call_log(
                AiToolCallLog(
                    tool_name=tool_name,
                    caller=caller,
                    conversation_id=conversation_id,
                    trace_id=trace_id,
                    arguments_summary=arguments_summary,
                    result_summary=result_summary,
                    draft_id=draft_id,
                    status=status,
                    error_message=error_message,
                )
            )
        except Exception:
            # ai_tool_call_log 表可能不存在，记录失败不影响主流程
            self.dao.db.rollback()
            return None
