"""客户状态更新处理器。

负责：
1. 查找客户 → 同名客户需选择
2. 校验状态合法性 → 同一状态提示无变更
3. lost 状态需填写流失原因
4. 确认执行 → 更新 crm_lead 状态和相关字段
"""

import re
from typing import Any, Dict, List, Optional

from backend.app.common.enums import DraftStatus
from backend.app.core.security import CurrentUser
from backend.app.models.draft import AiDraft

from ..base_handler import OperationHandler
from ..llm_client import OperationLlmClient
from ..operation_dao import OperationDao
from ..schemas import (
    CandidateItem,
    ConfirmationCard,
    ExecuteResult,
    FieldItem,
    MissingField,
    OperationResponse,
)
from ..intent_schemas import UPDATE_LEAD_STATUS_SCHEMA, IntentSchema


class UpdateLeadStatusHandler(OperationHandler):
    """客户状态更新处理器。"""

    # 状态码 → 中文名
    STATUS_NAMES = {
        "new": "新增",
        "following": "跟进中",
        "signed": "已签约",
        "lost": "已流失",
        "invalid": "无效",
    }

    # 允许的状态转移（未来可扩展）
    VALID_STATUSES = set(STATUS_NAMES.keys())

    def __init__(self, db_session, llm_client: Optional[OperationLlmClient] = None):
        self.dao = OperationDao(db_session)
        self.llm = llm_client or OperationLlmClient()
        self._card_title = "更新客户状态确认"

    @property
    def intent(self) -> str:
        return "update_lead_status"

    @property
    def schema(self) -> IntentSchema:
        return UPDATE_LEAD_STATUS_SCHEMA

    # ==================== 核心流程 ====================

    def create_draft(self, params: Dict[str, Any], user: CurrentUser) -> OperationResponse:
        """首次创建草稿。"""
        # 1. 校验必填字段
        missing = self._check_required(params)
        if missing:
            return self._build_missing_response(missing)

        customer_name = params["customer_name"]
        target_status = params["status"]

        # 2. 校验状态合法性
        if target_status not in self.VALID_STATUSES:
            return OperationResponse(
                status="failed",
                message=f"不支持的状态「{target_status}」，可选：{', '.join(self.STATUS_NAMES.values())}",
                intent=self.intent,
            )

        # 3. 查找客户
        leads = self.dao.find_leads_by_name(customer_name)

        if not leads:
            return OperationResponse(
                status="failed",
                message=f"未找到名为「{customer_name}」的客户",
                intent=self.intent,
            )

        # 处理同名客户 → 让用户选择
        if len(leads) > 1:
            return self._build_selection_response(leads, params, user)

        # 唯一客户
        lead = leads[0]

        # 检查是否已是同一状态
        if lead.status == target_status:
            return OperationResponse(
                status="failed",
                message=f"客户「{customer_name}」当前状态已经是「{self.STATUS_NAMES.get(target_status, target_status)}」，无需更新",
                intent=self.intent,
            )

        # 如果改为 lost，检查是否有流失原因
        if target_status == "lost" and not params.get("lost_reason"):
            return self._build_lost_reason_response(customer_name, target_status)

        # 创建草稿
        draft_content = {
            "_intent": self.intent,
            "customer_id": lead.id,
            "customer_name": customer_name,
            "current_status": lead.status,
            "new_status": target_status,
            "latest_follow_up_summary": params.get("latest_follow_up_summary"),
            "lost_reason": params.get("lost_reason"),
        }
        draft = self.dao.create_draft(
            intent=self.intent,
            content_json=draft_content,
            created_by=user.id,
            status=DraftStatus.PENDING_CONFIRM,
        )

        return self._build_confirm_response(draft, lead, target_status)

    def supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        """追问补全。

        支持：
        1. 选择客户（同名时）
        2. 补充流失原因
        """
        content = dict(draft.content_json)
        state = content.get("_state", "")

        if state == "customer_selection":
            return self._handle_selection(draft, query, user)

        if state == "awaiting_lost_reason":
            return self._handle_lost_reason_supplement(draft, query, user)

        # 通用字段补全
        merged = self.llm.supplement_fields(query, content)
        self.dao.update_draft_content(draft, merged)

        missing = self._check_required(merged)
        if missing:
            return self._build_missing_response(missing)

        # 重新检查 lost_reason
        if merged.get("new_status") == "lost" and not merged.get("lost_reason"):
            return self._build_lost_reason_response(
                merged.get("customer_name", ""),
                merged["new_status"],
            )

        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)
        return self._build_confirm_from_draft(draft, merged)

    def execute(self, draft: AiDraft, user: CurrentUser) -> ExecuteResult:
        """确认执行，更新数据库。"""
        content = dict(draft.content_json)
        customer_id = content.get("customer_id")
        new_status = content.get("new_status")

        if not customer_id or not new_status:
            return ExecuteResult(status="failed", message="草稿数据不完整，缺少客户ID或目标状态")

        # 获取客户记录
        from backend.app.models.crm_lead import CrmLead
        from sqlalchemy import select

        stmt = select(CrmLead).where(CrmLead.id == customer_id, CrmLead.is_delete == 0)
        lead = self.dao.db.scalar(stmt)
        if lead is None:
            return ExecuteResult(status="failed", message=f"客户记录不存在: {customer_id}")

        old_status = lead.status

        # 更新字段
        lead.status = new_status
        lead.latest_follow_up_summary = content.get("latest_follow_up_summary") or lead.latest_follow_up_summary

        from datetime import datetime
        if new_status == "signed":
            lead.signed_time = datetime.now()
        if new_status == "lost":
            lead.lost_reason = content.get("lost_reason")

        self.dao.db.flush()

        # 更新草稿状态
        self.dao.update_draft_status(
            draft,
            status=DraftStatus.CONFIRMED,
            confirmed_by=user.id,
        )

        # 审计日志
        self.dao.add_audit_log(
            operator_user_id=user.id,
            action_type="update",
            biz_module="enterprise_operation",
            biz_object_type="crm_lead",
            biz_object_id=lead.id,
            after_json={"old_status": old_status, "new_status": new_status, **content},
            draft_id=draft.id,
        )

        status_name = self.STATUS_NAMES.get(new_status, new_status)
        return ExecuteResult(
            status="success",
            message=f"客户「{lead.customer_name}」状态已从「{self.STATUS_NAMES.get(old_status, old_status)}」更新为「{status_name}」",
            biz_object_type="crm_lead",
            biz_object_id=lead.id,
            details={
                "id": lead.id,
                "customer_name": lead.customer_name,
                "old_status": old_status,
                "new_status": new_status,
                "new_status_name": status_name,
                "update_time": datetime.now().isoformat(),
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
                        key=key,
                        label=self.get_field_label(key),
                        question=f"请输入{self.get_field_label(key)}",
                    )
                )
        return missing

    def _build_selection_response(
        self, leads: list, params: Dict[str, Any], user: CurrentUser
    ) -> OperationResponse:
        """构建同名客户选择响应。"""
        candidates = []
        for lead in leads:
            owner_name = self.dao.get_employee_name_by_id(lead.owner_employee_id) if lead.owner_employee_id else "未分配"
            status_name = self.STATUS_NAMES.get(lead.status, lead.status)
            phone_display = f"，电话{lead.phone}" if lead.phone else ""
            label = f"{lead.customer_name}（{status_name}）负责人{owner_name}{phone_display}"
            candidates.append(CandidateItem(id=lead.id, label=label))

        # 创建草稿暂存搜索结果
        draft_content = {
            "_intent": self.intent,
            "_state": "customer_selection",
            "customer_name": params.get("customer_name"),
            "new_status": params.get("status"),
            "latest_follow_up_summary": params.get("latest_follow_up_summary"),
            "lost_reason": params.get("lost_reason"),
            "_candidates": [{"id": c.id, "label": c.label} for c in candidates],
        }
        draft = self.dao.create_draft(
            intent=self.intent,
            content_json=draft_content,
            created_by=user.id,
            status=DraftStatus.GENERATING,
        )

        customer_name = params.get("customer_name", "")
        return OperationResponse(
            status="requires_selection",
            message=f"找到多个名为「{customer_name}」的客户，请选择要更新状态的客户",
            draft_id=draft.id,
            intent=self.intent,
            selection_type="customer_selection",
            candidates=candidates,
            question=f"找到{len(leads)}个同名客户，请选择（回复编号或客户名）",
        )

    def _handle_selection(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        """处理客户选择。"""
        content = dict(draft.content_json)
        candidates_data = content.get("_candidates", [])
        customer_name = content.get("customer_name", "")
        target_status = content.get("new_status")

        selected_id = None

        # 策略1：匹配"第N个"
        idx_match = re.search(r"第[零一二三四五六七八九十\d]+[个个位]", query)
        if idx_match:
            idx_text = idx_match.group(0)
            idx = self._chinese_to_int(idx_text)
            if idx and 0 < idx <= len(candidates_data):
                selected_id = candidates_data[idx - 1]["id"]

        # 策略2：按电话号匹配
        if selected_id is None:
            phone_match = re.search(r"(\d{7,15})", query)
            if phone_match:
                phone = phone_match.group(1)
                for c in candidates_data:
                    c_label = c.get("label", "")
                    if phone in c_label:
                        from backend.app.models.crm_lead import CrmLead
                        from sqlalchemy import select
                        stmt = select(CrmLead).where(CrmLead.id == c["id"])
                        lead = self.dao.db.scalar(stmt)
                        if lead and lead.phone and phone in lead.phone:
                            selected_id = c["id"]
                            break

        # 策略3：按姓名再查一次
        if selected_id is None:
            parsed = self.llm.parse_intent(query)
            new_name = parsed.parameters.get("customer_name")
            phone = parsed.parameters.get("phone")
            if new_name or phone:
                leads = self.dao.find_leads_by_name(new_name or customer_name)
                for lead in leads:
                    if phone and lead.phone and phone in lead.phone:
                        selected_id = lead.id
                        break
                if selected_id is None and leads:
                    for c in candidates_data:
                        if c["id"] == leads[0].id:
                            selected_id = c["id"]
                            break

        if selected_id is None:
            return OperationResponse(
                status="requires_selection",
                message=f"未识别你的选择，请从以下客户中选择",
                draft_id=draft.id,
                intent=self.intent,
                selection_type="customer_selection",
                candidates=[
                    CandidateItem(id=c["id"], label=c["label"]) for c in candidates_data
                ],
                question='请回复序号（如"第一个"）或客户电话',
            )

        # 获取客户完整信息
        from backend.app.models.crm_lead import CrmLead
        from sqlalchemy import select
        stmt = select(CrmLead).where(CrmLead.id == selected_id, CrmLead.is_delete == 0)
        lead = self.dao.db.scalar(stmt)
        if lead is None:
            return OperationResponse(status="failed", message=f"客户记录不存在: {selected_id}")

        # 检查是否同一状态
        if lead.status == target_status:
            self.dao.update_draft_status(draft, DraftStatus.REJECTED, confirmed_by=user.id, reject_reason="状态无变更")
            return OperationResponse(
                status="failed",
                message=f"客户「{lead.customer_name}」当前状态已经是「{self.STATUS_NAMES.get(target_status, target_status)}」，无需更新",
            )

        # 检查 lost 需原因
        if target_status == "lost" and not content.get("lost_reason"):
            # 更新草稿进入待流失原因状态
            content["customer_id"] = lead.id
            content["_state"] = "awaiting_lost_reason"
            self.dao.update_draft_content(draft, content)
            return self._build_lost_reason_response(lead.customer_name, target_status)

        # 更新草稿
        content["customer_id"] = lead.id
        content["_state"] = ""
        self.dao.update_draft_content(draft, content)
        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)

        return self._build_confirm_response(draft, lead, target_status)

    def _handle_lost_reason_supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        """处理流失原因补充。"""
        content = dict(draft.content_json)
        merged = self.llm.supplement_fields(query, content)

        lost_reason = merged.get("lost_reason") or content.get("lost_reason")
        if not lost_reason:
            return self._build_lost_reason_response(
                content.get("customer_name", ""),
                content.get("new_status", "lost"),
            )

        content["lost_reason"] = lost_reason
        content["_state"] = ""
        self.dao.update_draft_content(draft, content)
        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)

        from backend.app.models.crm_lead import CrmLead
        from sqlalchemy import select
        stmt = select(CrmLead).where(CrmLead.id == content.get("customer_id"), CrmLead.is_delete == 0)
        lead = self.dao.db.scalar(stmt)

        return self._build_confirm_response(draft, lead, content.get("new_status"))

    def _build_lost_reason_response(self, customer_name: str, target_status: str) -> OperationResponse:
        """构建流失原因追问响应。"""
        return OperationResponse(
            status="missing_fields",
            message=f"将客户「{customer_name}」状态改为「{self.STATUS_NAMES.get(target_status, target_status)}」需要填写流失原因",
            intent=self.intent,
            missing_fields=[
                MissingField(
                    key="lost_reason",
                    label="流失原因",
                    question="请填写客户流失原因",
                )
            ],
        )

    def _build_confirm_response(
        self, draft: AiDraft, lead, target_status: str
    ) -> OperationResponse:
        """构建确认卡片响应。"""
        old_status_name = self.STATUS_NAMES.get(lead.status, lead.status)
        new_status_name = self.STATUS_NAMES.get(target_status, target_status)

        fields = [
            FieldItem(key="customer_name", label="客户姓名", value=lead.customer_name, required=True, editable=False),
            FieldItem(key="current_status", label="当前状态", value=old_status_name, required=False, editable=False),
            FieldItem(key="new_status", label="目标状态", value=new_status_name, required=True, editable=False),
        ]
        if lead.phone:
            fields.append(FieldItem(key="phone", label="手机号", value=lead.phone, required=False, editable=False))
        owner_name = self.dao.get_employee_name_by_id(lead.owner_employee_id) if lead.owner_employee_id else None
        if owner_name:
            fields.append(FieldItem(key="owner_name", label="负责人", value=owner_name, required=False, editable=False))

        summary = f"客户「{lead.customer_name}」状态从「{old_status_name}」更新为「{new_status_name}」"

        return OperationResponse(
            status="pending_confirm",
            message=f"确认将客户「{lead.customer_name}」状态从「{old_status_name}」更新为「{new_status_name}」？",
            draft_id=draft.id,
            intent=self.intent,
            confirmation_card=ConfirmationCard(
                title=self._card_title,
                intent=self.intent,
                fields=fields,
                summary=summary,
            ),
        )

    def _build_confirm_from_draft(self, draft: AiDraft, content: Dict[str, Any]) -> OperationResponse:
        """从草稿内容构建确认卡片。"""
        customer_id = content.get("customer_id")
        if not customer_id:
            return OperationResponse(
                status="missing_fields",
                message="缺少客户信息，请重新操作",
                intent=self.intent,
                missing_fields=[MissingField(key="customer_name", label="客户姓名", question="请输入客户姓名")],
            )

        from backend.app.models.crm_lead import CrmLead
        from sqlalchemy import select
        stmt = select(CrmLead).where(CrmLead.id == customer_id, CrmLead.is_delete == 0)
        lead = self.dao.db.scalar(stmt)
        if lead is None:
            return OperationResponse(status="failed", message=f"客户记录不存在: {customer_id}")

        return self._build_confirm_response(draft, lead, content.get("new_status", ""))

    def _build_missing_response(self, missing: List[MissingField]) -> OperationResponse:
        """构建缺失字段响应。"""
        field_names = "、".join([m.label for m in missing])
        return OperationResponse(
            status="missing_fields",
            message=f"请补充以下信息：{field_names}",
            intent=self.intent,
            missing_fields=missing,
        )

    @staticmethod
    def _chinese_to_int(text: str) -> Optional[int]:
        """中文数字转阿拉伯数字。"""
        cn_map = {
            "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
            "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
        }
        digits = re.findall(r"[一二三四五六七八九十\d]", text)
        if not digits:
            return None
        if digits[0].isdigit():
            return int(digits[0])
        return cn_map.get(digits[0])
