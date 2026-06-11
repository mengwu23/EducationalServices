"""业务操作编排器。

负责：
1. parse 阶段：调用 LLM 解析 query → 路由到 Handler → 创建草稿/返回结果
2. supplement 阶段：已有 draft_id 时，调用 Handler 补全字段
3. 确认阶段：用户确认后，调用 Handler 执行写库
"""

from typing import Optional

from backend.app.core.security import CurrentUser
from .handlers import get_handler
from .handlers.approve_leave import ApproveLeaveHandler
from .handlers.create_lead import CreateLeadHandler
from .handlers.handle_complaint import HandleComplaintHandler
from .handlers.enter_student_score import EnterStudentScoreHandler
from .handlers.submit_daily_report import SubmitDailyReportHandler
from .handlers.update_lead_status import UpdateLeadStatusHandler
from .llm_client import OperationLlmClient
from .schemas import ExecuteRequest, ConfirmRequest, OperationResponse, ExecuteResult

class OperationOrchestrator:
    """统一编排入口。"""

    def __init__(self, db_session, llm_client: Optional[OperationLlmClient] = None):
        self.db = db_session
        self.llm = llm_client or OperationLlmClient()

    def execute(self, req: ExecuteRequest, user: CurrentUser) -> OperationResponse:
        """统一执行入口。

        流程：
        1. 有 draft_id → 追问补全
        2. 无 draft_id → LLM 解析 → 路由到 Handler
        """
        if req.draft_id:
            return self._handle_supplement(req, user)
        return self._handle_parse(req, user)

    def confirm(self, req: ConfirmRequest, user: CurrentUser) -> ExecuteResult:
        """确认/拒绝草稿。

        确认：调用 Handler.execute() 写库
        拒绝：更新草稿状态为 rejected

        幂等说明：
        - 草稿已 confirmed → 直接返回成功（防重复点击）
        - 草稿已 rejected → 提示已拒绝
        """
        from .operation_dao import OperationDao

        dao = OperationDao(self.db)
        draft = dao.get_draft(req.draft_id)
        if draft is None:
            return ExecuteResult(status="failed", message=f"草稿不存在: {req.draft_id}")

        # 幂等处理：已确认的草稿直接返回成功
        if draft.status == "confirmed":
            return ExecuteResult(status="success", message="该操作已确认执行")

        # 已拒绝的草稿提示
        if draft.status == "rejected":
            return ExecuteResult(status="failed", message="该草稿已被拒绝，无法再次确认")

        if draft.status != "pending_confirm":
            return ExecuteResult(status="failed", message=f"草稿状态不允许确认: {draft.status}")

        if req.action == "reject":
            dao.update_draft_status(
                draft,
                status="rejected",
                confirmed_by=user.id,
                reject_reason=req.reject_reason or "",
            )
            return ExecuteResult(status="success", message="已拒绝该操作")

        if req.action != "confirm":
            return ExecuteResult(status="failed", message=f"不支持的操作: {req.action}")

        # 确认执行：从草稿 content_json 中获取 intent 并分派
        intent = draft.content_json.get("_intent") if isinstance(draft.content_json, dict) else None
        actual_intent = intent or "create_lead"

        handler = self._resolve_handler(actual_intent)
        return handler.execute(draft, user)

    # ==================== 内部方法 ====================

    def _handle_parse(self, req: ExecuteRequest, user: CurrentUser) -> OperationResponse:
        """首次解析：LLM → 路由 Handler。"""
        parsed = self.llm.parse_intent(req.query, req.conversation_id)

        # 路由到对应的 Handler
        handler = self._resolve_handler(parsed.intent)
        response = handler.create_draft(parsed.parameters, user)

        # 回传 conversation_id
        response.conversation_id = parsed.conversation_id

        # 标记 intent（后续 confirm 时要用）
        if response.draft_id and parsed.intent:
            from .operation_dao import OperationDao
            dao = OperationDao(self.db)
            draft = dao.get_draft(response.draft_id)
            if draft and isinstance(draft.content_json, dict):
                content = dict(draft.content_json)
                content["_intent"] = parsed.intent
                dao.update_draft_content(draft, content)

        return response

    def _handle_supplement(self, req: ExecuteRequest, user: CurrentUser) -> OperationResponse:
        """追问补全。"""
        from .operation_dao import OperationDao

        dao = OperationDao(self.db)
        draft = dao.get_draft(req.draft_id)
        if draft is None:
            return OperationResponse(
                status="failed",
                message=f"草稿不存在: {req.draft_id}",
            )

        # 从 content_json 中获取 intent
        intent = "create_lead"
        if isinstance(draft.content_json, dict):
            intent = draft.content_json.get("_intent", "create_lead")

        handler = self._resolve_handler(intent)
        return handler.supplement(draft, req.query, user)

    def _resolve_handler(self, intent: str):
        """获取 Handler 实例。"""
        from .operation_dao import OperationDao

        if intent == "create_lead":
            return CreateLeadHandler(self.db, self.llm)
        if intent == "update_lead_status":
            return UpdateLeadStatusHandler(self.db, self.llm)
        if intent == "submit_daily_report":
            return SubmitDailyReportHandler(self.db, self.llm)
        if intent == "enter_student_score":
            return EnterStudentScoreHandler(self.db, self.llm)
        if intent == "approve_leave":
            return ApproveLeaveHandler(self.db, self.llm)
        if intent == "handle_complaint":
            return HandleComplaintHandler(self.db, self.llm)
        return get_handler(intent)
