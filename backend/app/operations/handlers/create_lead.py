"""意向客户录入处理器。

负责：
1. 首次解析：校验必填字段 → 创建草稿 → 返回确认卡片或追问
2. 追问补全：提取新字段 → 更新草稿 → 再次校验
3. 确认执行：生成 lead_no → 写入 crm_lead → 审计日志
"""

from typing import Any, Dict, List, Optional

from backend.app.common.enums import DraftStatus
from backend.app.core.security import CurrentUser
from backend.app.models.draft import AiDraft

from ..base_handler import OperationHandler
from ..llm_client import OperationLlmClient, ParsedIntent
from ..operation_dao import OperationDao
from ..schemas import (
    ConfirmationCard,
    ExecuteResult,
    FieldItem,
    MissingField,
    OperationResponse,
)
from ..intent_schemas import CREATE_LEAD_SCHEMA, IntentSchema


class CreateLeadHandler(OperationHandler):
    """意向客户录入处理器。"""

    def __init__(self, db_session, llm_client: Optional[OperationLlmClient] = None):
        self.dao = OperationDao(db_session)
        self.llm = llm_client or OperationLlmClient()
        # 确认卡片标题
        self._card_title = "新增意向客户确认"

    @property
    def intent(self) -> str:
        return "create_lead"

    @property
    def schema(self) -> IntentSchema:
        return CREATE_LEAD_SCHEMA

    # ==================== 核心流程 ====================

    def create_draft(self, params: Dict[str, Any], user: CurrentUser) -> OperationResponse:
        """首次创建草稿。"""
        # 1. 校验必填字段
        missing = self._check_required(params)
        if missing:
            return self._build_missing_response(missing)

        # 2. 查重检测（同手机号）
        duplicate_warning = self._check_duplicate(params)

        # 3. 创建草稿
        draft = self.dao.create_draft(
            intent=self.intent,
            content_json=params,
            created_by=user.id,
            status=DraftStatus.PENDING_CONFIRM,
        )

        # 4. 返回确认卡片
        return self._build_confirm_response(draft, params, duplicate_warning)

    def supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        """追问补全字段。"""
        existing = dict(draft.content_json)

        # 1. LLM 提取新字段
        merged = self.llm.supplement_fields(query, existing)

        # 2. 更新草稿
        self.dao.update_draft_content(draft, merged)

        # 3. 重新校验
        missing = self._check_required(merged)
        if missing:
            # 查出新增的缺失字段（排除原有已有的）
            existing_non_empty = {k for k, v in existing.items() if v}
            new_missing = [m for m in missing if m.key not in existing_non_empty]
            return self._build_missing_response(new_missing if new_missing else missing)

        # 4. 查重检测
        duplicate_warning = self._check_duplicate(merged)

        # 5. 更新状态
        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)

        return self._build_confirm_response(draft, merged, duplicate_warning)

    def execute(self, draft: AiDraft, user: CurrentUser) -> ExecuteResult:
        """确认执行，写入数据库。"""
        params = dict(draft.content_json)

        # 1. 获取当前员工的 employee_profile
        employee = self.dao.get_employee_by_user_id(user.id)
        owner_employee_id = employee.id if employee else None

        # 2. 创建客户线索
        lead = self.dao.create_lead(params, owner_employee_id)

        # 3. 更新草稿状态
        self.dao.update_draft_status(
            draft,
            status=DraftStatus.CONFIRMED,
            confirmed_by=user.id,
        )

        # 4. 记录审计日志
        self.dao.add_audit_log(
            operator_user_id=user.id,
            action_type="create",
            biz_module="enterprise_operation",
            biz_object_type="crm_lead",
            biz_object_id=lead.id,
            after_json={**params, "lead_no": lead.lead_no, "id": lead.id},
            draft_id=draft.id,
        )

        # 5. 返回结果
        owner_name = self.dao.get_employee_name_by_id(owner_employee_id) if owner_employee_id else None
        return ExecuteResult(
            status="success",
            message=f"客户「{lead.customer_name}」已成功创建，线索编号 {lead.lead_no}",
            biz_object_type="crm_lead",
            biz_object_id=lead.id,
            details={
                "id": lead.id,
                "lead_no": lead.lead_no,
                "customer_name": lead.customer_name,
                "phone": lead.phone,
                "owner_employee_id": owner_employee_id,
                "owner_name": owner_name,
                "status": lead.status,
                "create_time": lead.create_time.isoformat() if lead.create_time else None,
            },
        )

    # ==================== 内部方法 ====================

    def _check_required(self, params: Dict[str, Any]) -> List[MissingField]:
        """检查必填字段，返回缺失列表。"""
        missing: List[MissingField] = []
        for key in self.schema.required_keys:
            value = params.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(
                    MissingField(
                        key=key,
                        label=self.get_field_label(key),
                        question=f"请输入{self.get_field_label(key)}",
                    )
                )
        return missing

    def _check_duplicate(self, params: Dict[str, Any]) -> Optional[str]:
        """检查是否存在同手机号客户，返回警告文本。"""
        phone = params.get("phone")
        if not phone:
            return None
        existing = self.dao.find_leads_by_phone(phone)
        if existing:
            names = "、".join([f"「{c.customer_name}」" for c in existing[:3]])
            if len(existing) > 3:
                names += f"等{len(existing)}位客户"
            return f"手机号 {phone} 已存在关联客户：{names}，请注意可能重复录入。"
        return None

    def _build_confirm_response(
        self,
        draft: AiDraft,
        params: Dict[str, Any],
        duplicate_warning: Optional[str] = None,
    ) -> OperationResponse:
        """构建确认卡片响应。"""
        fields = []
        for field_def in self.schema.fields:
            value = params.get(field_def.key)
            if value is not None:
                fields.append(
                    FieldItem(
                        key=field_def.key,
                        label=field_def.label,
                        value=value,
                        required=field_def.required,
                        editable=True,
                    )
                )

        summary_parts = []
        name = params.get("customer_name", "")
        phone = params.get("phone", "")
        if name:
            summary_parts.append(f"客户姓名：{name}")
        if phone:
            summary_parts.append(f"手机号：{phone}")
        target = params.get("target_country", "")
        program = params.get("target_program", "")
        if target and program:
            summary_parts.append(f"意向：{target}{program}")
        elif target:
            summary_parts.append(f"意向国家：{target}")
        summary = "；".join(summary_parts) if summary_parts else None

        message_parts = []
        name_part = f"客户「{name}」" if name else "客户"
        message_parts.append(f"AI识别到你要新增{name_part}")
        if duplicate_warning:
            message_parts.append(f"⚠️ {duplicate_warning}")

        return OperationResponse(
            status="pending_confirm",
            message="；".join(message_parts),
            draft_id=draft.id,
            intent=self.intent,
            confirmation_card=ConfirmationCard(
                title=self._card_title,
                intent=self.intent,
                fields=fields,
                summary=summary,
            ),
        )

    def _build_missing_response(self, missing: List[MissingField]) -> OperationResponse:
        """构建缺失字段追问响应。"""
        field_names = "、".join([m.label for m in missing])
        return OperationResponse(
            status="missing_fields",
            message=f"请补充以下信息：{field_names}",
            intent=self.intent,
            missing_fields=missing,
        )
