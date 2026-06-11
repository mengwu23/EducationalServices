"""口述日报提交处理器。

负责：
1. 接收口述日报 → LLM 整理结构化内容
2. 查询当天已有日报 → 提示是否更新
3. 确认后写入 employee_daily_report 表
"""

from datetime import date
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
from ..intent_schemas import SUBMIT_DAILY_REPORT_SCHEMA, IntentSchema


class SubmitDailyReportHandler(OperationHandler):
    """口述日报提交处理器。"""

    def __init__(self, db_session, llm_client: Optional[OperationLlmClient] = None):
        self.dao = OperationDao(db_session)
        self.llm = llm_client or OperationLlmClient()
        self._card_title = "日报提交确认"

    @property
    def intent(self) -> str:
        return "submit_daily_report"

    @property
    def schema(self) -> IntentSchema:
        return SUBMIT_DAILY_REPORT_SCHEMA

    # ==================== 核心流程 ====================

    def create_draft(self, params: Dict[str, Any], user: CurrentUser) -> OperationResponse:
        """首次创建日报草稿。"""
        # 1. 校验必填字段
        missing = self._check_required(params)
        if missing:
            return self._build_missing_response(missing)

        raw_content = params.get("raw_content", "")

        # 2. 获取员工信息
        employee = self.dao.get_employee_by_user_id(user.id)
        if not employee:
            return OperationResponse(
                status="failed",
                message="当前用户未关联员工档案，无法提交日报",
                intent=self.intent,
            )

        # 3. 检查当天是否已有日报
        today = date.today()
        existing = self.dao.find_today_report(employee.id, today)
        update_mode = existing is not None

        # 4. 创建草稿
        draft_content = {
            "_intent": self.intent,
            "employee_id": employee.id,
            "department_id": employee.department_id,
            "report_date": today.isoformat(),
            "raw_content": raw_content,
            "summary": params.get("summary"),
            "key_progress": params.get("key_progress"),
            "risks": params.get("risks"),
            "tomorrow_plan": params.get("tomorrow_plan"),
            "is_update": update_mode,
        }
        draft = self.dao.create_draft(
            intent=self.intent,
            content_json=draft_content,
            created_by=user.id,
            status=DraftStatus.PENDING_CONFIRM,
        )

        msg_parts = []
        if update_mode:
            msg_parts.append(f"你今天已有日报，是否确认更新？")
        else:
            msg_parts.append(f"AI已整理你的日报")

        return self._build_confirm_response(draft, draft_content, msg_parts, employee)

    def supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        """追问补全（日报修改/追加）。"""
        content = dict(draft.content_json)

        # 用新 query 补全字段
        merged = self.llm.supplement_fields(query, content)
        merged["raw_content"] = content.get("raw_content", "") + "\n" + query

        self.dao.update_draft_content(draft, merged)

        missing = self._check_required(merged)
        if missing:
            return self._build_missing_response(missing)

        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)

        employee = self.dao.get_employee_by_user_id(user.id)
        return self._build_confirm_response(draft, merged, ["日报已更新"], employee)

    def execute(self, draft: AiDraft, user: CurrentUser) -> ExecuteResult:
        """确认执行，写入日报。"""
        content = dict(draft.content_json)
        employee_id = content.get("employee_id")
        is_update = content.get("is_update", False)

        if not employee_id:
            return ExecuteResult(status="failed", message="草稿数据不完整，缺少员工ID")

        # 写入或更新日报
        if is_update:
            existing = self.dao.find_today_report(employee_id, date.today())
            if existing:
                self.dao.update_daily_report(existing, content)
                report_id = existing.id
            else:
                report = self.dao.create_daily_report(
                    employee_id, content.get("department_id"), content
                )
                report_id = report.id
        else:
            report = self.dao.create_daily_report(
                employee_id, content.get("department_id"), content
            )
            report_id = report.id

        # 更新草稿状态
        self.dao.update_draft_status(
            draft, status=DraftStatus.CONFIRMED, confirmed_by=user.id,
        )

        # 审计日志
        self.dao.add_audit_log(
            operator_user_id=user.id,
            action_type="update" if is_update else "create",
            biz_module="enterprise_operation",
            biz_object_type="employee_daily_report",
            biz_object_id=report_id,
            after_json=content,
            draft_id=draft.id,
        )

        action_label = "更新" if is_update else "提交"
        employee_name = self.dao.get_employee_name_by_id(employee_id)
        return ExecuteResult(
            status="success",
            message=f"日报已{action_label}成功（{employee_name} - {content.get('report_date', '今天')}）",
            biz_object_type="employee_daily_report",
            biz_object_id=report_id,
            details={
                "id": report_id,
                "employee_id": employee_id,
                "employee_name": employee_name,
                "report_date": content.get("report_date"),
                "is_update": is_update,
            },
        )

    # ==================== 内部方法 ====================

    def _check_required(self, params: Dict[str, Any]) -> List[MissingField]:
        """检查必填字段。"""
        missing: List[MissingField] = []
        for key in self.schema.required_keys:
            value = params.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(
                    MissingField(
                        key=key, label=self.get_field_label(key),
                        question=f"请输入{self.get_field_label(key)}",
                    )
                )
        return missing

    def _build_confirm_response(
        self, draft: AiDraft, content: Dict[str, Any],
        msg_parts: List[str], employee=None,
    ) -> OperationResponse:
        """构建确认卡片。"""
        fields = [
            FieldItem(key="raw_content", label="原始内容", value=content.get("raw_content", ""), required=True, editable=True),
        ]
        if content.get("summary"):
            fields.append(FieldItem(key="summary", label="AI摘要", value=content["summary"], required=False, editable=True))
        if content.get("key_progress"):
            fields.append(FieldItem(key="key_progress", label="关键进展", value=content["key_progress"], required=False, editable=True))
        if content.get("risks"):
            fields.append(FieldItem(key="risks", label="风险问题", value=content["risks"], required=False, editable=True))
        if content.get("tomorrow_plan"):
            fields.append(FieldItem(key="tomorrow_plan", label="明日计划", value=content["tomorrow_plan"], required=False, editable=True))

        employee_name = employee.employee_name if employee else "未知"
        summary = content.get("summary") or content.get("raw_content", "")[:30]

        return OperationResponse(
            status="pending_confirm",
            message="；".join(msg_parts),
            draft_id=draft.id,
            intent=self.intent,
            confirmation_card=ConfirmationCard(
                title=self._card_title,
                intent=self.intent,
                fields=fields,
                summary=f"{employee_name} - {summary}",
            ),
        )

    def _build_missing_response(self, missing: List[MissingField]) -> OperationResponse:
        field_names = "、".join([m.label for m in missing])
        return OperationResponse(
            status="missing_fields",
            message=f"请补充以下信息：{field_names}",
            intent=self.intent,
            missing_fields=missing,
        )
