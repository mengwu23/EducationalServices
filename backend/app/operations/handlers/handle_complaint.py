"""投诉反馈处理器。

支持操作：
- query：查询待处理投诉
- process：标记为处理中
- resolve：填写处理方案
- close：关闭工单
- notify：标记已通知学生
"""

from typing import Any, Dict, List, Optional

from backend.app.common.enums import DraftStatus
from backend.app.core.security import CurrentUser
from backend.app.models.draft import AiDraft

from ..base_handler import OperationHandler
from ..llm_client import OperationLlmClient
from ..operation_dao import OperationDao
from ..schemas import (
    ConfirmationCard, ExecuteResult, FieldItem, MissingField, OperationResponse,
)
from ..intent_schemas import HANDLE_COMPLAINT_SCHEMA, IntentSchema

STATUS_NAMES = {"pending": "待处理", "processing": "处理中", "resolved": "已解决", "closed": "已关闭"}
ACTION_LABELS = {"process": "处理中", "resolve": "已解决", "close": "已关闭", "notify": "已通知"}


class HandleComplaintHandler(OperationHandler):

    def __init__(self, db_session, llm_client: Optional[OperationLlmClient] = None):
        self.dao = OperationDao(db_session)
        self.llm = llm_client or OperationLlmClient()
        self._card_title = "投诉处理确认"

    @property
    def intent(self) -> str:
        return "handle_complaint"

    @property
    def schema(self) -> IntentSchema:
        return HANDLE_COMPLAINT_SCHEMA

    def create_draft(self, params: Dict[str, Any], user: CurrentUser) -> OperationResponse:
        action = params.get("action", "query")

        if action == "query":
            return self._handle_query(user)

        # process / resolve / close / notify
        student_name = params.get("student_name")
        if not student_name:
            return OperationResponse(
                status="missing_fields", message="请指定学生姓名",
                intent=self.intent,
                missing_fields=[MissingField(key="student_name", label="学生姓名", question="请输入学生姓名")],
            )

        tickets = self.dao.find_feedback_by_student_name(student_name)
        if not tickets:
            return OperationResponse(status="failed", message=f"未找到「{student_name}」的投诉记录", intent=self.intent)
        if len(tickets) > 1:
            return self._build_multi_response(tickets, action, params, user)

        ticket, name = tickets[0]
        return self._build_draft(ticket, name, action, params, user)

    def supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        content = dict(draft.content_json)
        merged = self.llm.supplement_fields(query, content)
        self.dao.update_draft_content(draft, merged)
        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)
        return OperationResponse(status="pending_confirm", message="已更新", draft_id=draft.id, intent=self.intent)

    def execute(self, draft: AiDraft, user: CurrentUser) -> ExecuteResult:
        content = dict(draft.content_json)
        ticket_id = content.get("ticket_id")
        action = content.get("action", "process")
        solution = content.get("solution")
        content_summary = content.get("content_summary")
        emp = self.dao.get_employee_by_user_id(user.id)
        handler_id = emp.id if emp else None

        kwargs = {}
        if action == "process":
            kwargs["status"] = "processing"
            kwargs["handler_employee_id"] = handler_id
        elif action == "resolve":
            kwargs["status"] = "resolved"
            if solution:
                kwargs["solution"] = solution
        elif action == "close":
            kwargs["status"] = "closed"
            if solution:
                kwargs["solution"] = solution
        elif action == "notify":
            kwargs["is_notified"] = 1

        if content_summary:
            kwargs["content_summary"] = content_summary

        ticket = self.dao.update_feedback(ticket_id, **kwargs)
        if not ticket:
            return ExecuteResult(status="failed", message="工单不存在")

        self.dao.update_draft_status(draft, DraftStatus.CONFIRMED, confirmed_by=user.id)
        self.dao.add_audit_log(
            operator_user_id=user.id, action_type="update",
            biz_module="enterprise_operation", biz_object_type="student_feedback_ticket",
            biz_object_id=ticket.id, after_json=kwargs, draft_id=draft.id,
        )

        label = ACTION_LABELS.get(action, action)
        student_name = content.get("student_name", "")
        return ExecuteResult(
            status="success", message=f"「{student_name}」的投诉已{label}",
            biz_object_type="student_feedback_ticket", biz_object_id=ticket.id,
        )

    # ---------- internal ----------

    def _handle_query(self, user: CurrentUser) -> OperationResponse:
        emp = self.dao.get_employee_by_user_id(user.id)
        if not emp:
            return OperationResponse(status="failed", message="无员工档案", intent=self.intent)
        tickets = self.dao.find_feedback_by_handler(emp.id, statuses=["pending", "processing"])
        if not tickets:
            return OperationResponse(status="success", message="当前没有待处理的投诉", intent=self.intent)
        lines = [f"你有 {len(tickets)} 条待处理投诉："]
        for i, (t, name) in enumerate(tickets, 1):
            sn = STATUS_NAMES.get(t.status, t.status)
            lines.append(f"{i}. {name} - {t.title}（{sn}）")
        return OperationResponse(status="success", message="\n".join(lines), intent=self.intent)

    def _build_multi_response(self, tickets, action, params, user):
        from ..schemas import CandidateItem
        items = []
        cnt = {"_intent": self.intent, "_state": "ticket_selection", "action": action,
               "solution": params.get("solution"), "content_summary": params.get("content_summary"), "_candidates": []}
        for t, name in tickets:
            items.append({"id": t.id, "desc": f"{name} - {t.title}"})
            cnt["_candidates"].append({"id": t.id, "desc": f"{name} - {t.title}"})
        draft = self.dao.create_draft(intent=self.intent, content_json=cnt, created_by=user.id, status=DraftStatus.GENERATING)
        return OperationResponse(status="requires_selection", candidates=[CandidateItem(id=it["id"], label=it["desc"]) for it in items],
                                 draft_id=draft.id, intent=self.intent, selection_type="ticket_selection")

    def _build_draft(self, ticket, name, action, params, user):
        content = {
            "_intent": self.intent, "action": action, "ticket_id": ticket.id,
            "student_name": name, "title": ticket.title, "solution": params.get("solution"),
            "content_summary": params.get("content_summary"),
        }
        draft = self.dao.create_draft(intent=self.intent, content_json=content, created_by=user.id, status=DraftStatus.PENDING_CONFIRM)
        label = ACTION_LABELS.get(action, action)
        fields = [
            FieldItem(key="student_name", label="学生姓名", value=name, required=True, editable=False),
            FieldItem(key="title", label="投诉标题", value=ticket.title, required=False, editable=False),
            FieldItem(key="action", label="操作", value=label, required=True, editable=False),
        ]
        if params.get("solution"):
            fields.append(FieldItem(key="solution", label="处理方案", value=params["solution"], required=False))
        return OperationResponse(status="pending_confirm", message=f"确认将「{name}」的投诉标记为「{label}」？",
                                 draft_id=draft.id, intent=self.intent,
                                 confirmation_card=ConfirmationCard(title=self._card_title, intent=self.intent, fields=fields,
                                                                    summary=f"{label}：{name} - {ticket.title}"))
