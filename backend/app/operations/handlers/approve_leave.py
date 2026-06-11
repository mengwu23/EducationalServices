"""请假审批处理器。

处理两个子场景：
1. 查询待审批请假（action=query）：直接返回列表
2. 审批/驳回请假（action=approve/reject）：确认卡片 → 执行
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.app.common.enums import DraftStatus
from backend.app.core.security import CurrentUser
from backend.app.models.draft import AiDraft

from ..base_handler import OperationHandler
from ..llm_client import OperationLlmClient
from ..operation_dao import OperationDao
from ..schemas import (
    ConfirmationCard,
    ExecuteResult,
    FieldItem,
    MissingField,
    OperationResponse,
)
from ..intent_schemas import APPROVE_LEAVE_SCHEMA, IntentSchema

LEAVE_TYPE_NAMES = {"sick": "病假", "personal": "事假", "other": "其他"}


class ApproveLeaveHandler(OperationHandler):
    """请假审批处理器。"""

    def __init__(self, db_session, llm_client: Optional[OperationLlmClient] = None):
        self.dao = OperationDao(db_session)
        self.llm = llm_client or OperationLlmClient()
        self._card_title = "请假审批确认"

    @property
    def intent(self) -> str:
        return "approve_leave"

    @property
    def schema(self) -> IntentSchema:
        return APPROVE_LEAVE_SCHEMA

    def create_draft(self, params: Dict[str, Any], user: CurrentUser) -> OperationResponse:
        action = params.get("action", "query")

        if action == "query":
            return self._handle_query(user)

        # approve / reject
        student_name = params.get("student_name")
        if not student_name:
            return OperationResponse(
                status="missing_fields", message="请指定要审批的学生",
                intent=self.intent,
                missing_fields=[MissingField(key="student_name", label="学生姓名", question="请输入学生姓名")],
            )

        leaves = self.dao.find_pending_leave_by_student_name(student_name)
        if not leaves:
            return OperationResponse(
                status="failed", message=f"未找到「{student_name}」的待审批请假",
                intent=self.intent,
            )
        if len(leaves) > 1:
            return self._build_multi_leave_response(leaves, action, params, user)

        leave, name = leaves[0]
        status_code = "approved" if action == "approve" else "rejected"
        action_label = "通过" if action == "approve" else "驳回"

        content = {
            "_intent": self.intent, "action": action, "leave_id": leave.id,
            "student_name": name, "leave_type": LEAVE_TYPE_NAMES.get(leave.leave_type, leave.leave_type),
            "start_time": str(leave.start_time), "end_time": str(leave.end_time),
            "approval_comment": params.get("approval_comment"),
        }
        draft = self.dao.create_draft(
            intent=self.intent, content_json=content,
            created_by=user.id, status=DraftStatus.PENDING_CONFIRM,
        )
        fields = [
            FieldItem(key="student_name", label="学生姓名", value=name, required=True, editable=False),
            FieldItem(key="leave_type", label="请假类型", value=LEAVE_TYPE_NAMES.get(leave.leave_type, leave.leave_type), required=False, editable=False),
            FieldItem(key="action", label="审批操作", value=action_label, required=True, editable=False),
        ]
        if params.get("approval_comment"):
            fields.append(FieldItem(key="approval_comment", label="审批意见", value=params["approval_comment"], required=False))

        return OperationResponse(
            status="pending_confirm",
            message=f"确认{action_label}「{name}」的请假申请？",
            draft_id=draft.id, intent=self.intent,
            confirmation_card=ConfirmationCard(title=self._card_title, intent=self.intent, fields=fields,
                                               summary=f"{action_label}{name}的{LEAVE_TYPE_NAMES.get(leave.leave_type, leave.leave_type)}"),
        )

    def supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        content = dict(draft.content_json)
        merged = self.llm.supplement_fields(query, content)
        self.dao.update_draft_content(draft, merged)
        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)
        return OperationResponse(status="pending_confirm", message="审批信息已更新", draft_id=draft.id, intent=self.intent)

    def execute(self, draft: AiDraft, user: CurrentUser) -> ExecuteResult:
        content = dict(draft.content_json)
        leave_id = content.get("leave_id")
        action = content.get("action", "approve")
        comment = content.get("approval_comment")
        emp = self.dao.get_employee_by_user_id(user.id)
        approver_id = emp.id if emp else None

        status_code = "approved" if action == "approve" else "rejected"
        leave = self.dao.approve_leave(leave_id, status_code, approver_id, comment)
        if not leave:
            return ExecuteResult(status="failed", message="请假记录不存在")

        self.dao.update_draft_status(draft, DraftStatus.CONFIRMED, confirmed_by=user.id)
        self.dao.add_audit_log(
            operator_user_id=user.id, action_type="update",
            biz_module="enterprise_operation", biz_object_type="student_leave_request",
            biz_object_id=leave.id, after_json={"status": status_code, "comment": comment},
            draft_id=draft.id,
        )

        action_label = "已通过" if action == "approve" else "已驳回"
        student_name = content.get("student_name", "")
        return ExecuteResult(
            status="success", message=f"「{student_name}」的请假申请{action_label}",
            biz_object_type="student_leave_request", biz_object_id=leave.id,
            details={"student_name": student_name, "status": status_code},
        )

    # ---------- internal ----------

    def _handle_query(self, user: CurrentUser) -> OperationResponse:
        emp = self.dao.get_employee_by_user_id(user.id)
        if not emp:
            return OperationResponse(status="failed", message="当前用户未关联员工档案", intent=self.intent)
        leaves = self.dao.find_pending_leaves_by_approver(emp.id)
        if not leaves:
            return OperationResponse(status="success", message="当前没有待审批的请假申请", intent=self.intent)

        lines = [f"你有 {len(leaves)} 条待审批请假："]
        for i, (leave, name) in enumerate(leaves, 1):
            lt = LEAVE_TYPE_NAMES.get(leave.leave_type, leave.leave_type)
            lines.append(f"{i}. {name}，{lt}，{str(leave.start_time)[:10]} 至 {str(leave.end_time)[:10]}")
        return OperationResponse(status="success", message="\n".join(lines), intent=self.intent)

    def _build_multi_leave_response(self, leaves, action, params, user):
        items = []
        content = {
            "_intent": self.intent, "_state": "leave_selection", "action": action,
            "student_name": params.get("student_name"), "approval_comment": params.get("approval_comment"),
            "_candidates": [],
        }
        for leave, name in leaves:
            items.append({"id": leave.id, "student_name": name,
                          "desc": f"{name}({LEAVE_TYPE_NAMES.get(leave.leave_type, leave.leave_type)})"})
            content["_candidates"].append({"id": leave.id, "desc": f"{name}({LEAVE_TYPE_NAMES.get(leave.leave_type, leave.leave_type)})"})
        draft = self.dao.create_draft(intent=self.intent, content_json=content, created_by=user.id, status=DraftStatus.GENERATING)
        from ..schemas import CandidateItem
        return OperationResponse(
            status="requires_selection", message=f"找到 {len(leaves)} 条待审批请假",
            draft_id=draft.id, intent=self.intent, selection_type="leave_selection",
            candidates=[CandidateItem(id=it["id"], label=it["desc"]) for it in items],
        )
