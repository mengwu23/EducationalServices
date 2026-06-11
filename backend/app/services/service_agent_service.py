from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.common.exceptions import BusinessError, NotFoundError, ReportGenerationError
from backend.app.core.config import Settings, get_settings
from backend.app.daos.service_agent_dao import ServiceAgentDAO
from backend.app.integrations.dify_client import DifyClient
from backend.app.models.event_registration import EventRegistration
from backend.app.schemas.service_agent_schema import (
    ActivitySignupRequest,
    ServiceAgentEventSearchRequest,
    ServiceAgentFaqSearchRequest,
    ServiceAgentMessageRequest,
    ServiceAgentProjectSearchRequest,
)


class ServiceAgentService:
    def __init__(
        self,
        db: Session,
        dify_client: DifyClient | None = None,
        settings: Settings | None = None,
    ):
        self.db = db
        self.settings = settings or get_settings()
        self.dao = ServiceAgentDAO(db)
        self.dify_client = dify_client or DifyClient(self.settings)

    def handle_visitor_message(self, request: ServiceAgentMessageRequest) -> dict[str, Any]:
        """转发访客消息到 Dify 客服 Agent，直接返回 Agent 的回复。"""
        trace_id = f"sa-{uuid4().hex[:12]}"
        visitor_id = request.conversation_id or f"visitor-{uuid4().hex[:12]}"
        try:
            ai_result = self.dify_client.call_service_agent(
                query=request.message,
                conversation_id=request.conversation_id,
                visitor_id=visitor_id,
                trace_id=trace_id,
            )
            return {
                "visitor_id": visitor_id,
                "conversation_id": ai_result.get("conversation_id") or request.conversation_id,
                "visitor_message": request.message,
                "reply_text": ai_result.get("answer", ""),
                "suggested_questions": ai_result.get("suggested_questions", []),
                "trace_id": trace_id,
            }
        except Exception as exc:
            self.db.rollback()
            raise ReportGenerationError(f"客服回复生成失败：{exc}") from exc

    def search_faq(self, request: ServiceAgentFaqSearchRequest) -> list[dict[str, Any]]:
        rows = self.dao.search_faq(request.keyword, request.category, request.limit)
        return [self._faq_to_dict(row) for row in rows]

    def search_projects(self, request: ServiceAgentProjectSearchRequest) -> list[dict[str, Any]]:
        rows = self.dao.search_projects(
            request.keyword,
            request.project_type,
            request.target_country,
            request.education_level,
            request.limit,
        )
        return [self._project_to_dict(row) for row in rows]

    def list_events(self, request: ServiceAgentEventSearchRequest) -> list[dict[str, Any]]:
        rows = self.dao.list_events(request.keyword, request.event_type, request.status, request.limit)
        return [self._event_to_dict(row) for row in rows]

    def create_activity_signup(self, request: ActivitySignupRequest) -> dict[str, Any]:
        event = self.dao.get_event(request.event_id)
        if not event:
            raise NotFoundError("活动不存在")
        if event.status != "open":
            raise BusinessError("当前活动不可报名")

        registration = self.dao.add_registration(
            EventRegistration(
                event_id=event.id,
                lead_id=request.lead_id,
                visitor_name=request.visitor_name,
                visitor_phone=request.visitor_phone,
                registration_status="registered",
                remark=request.remark,
            )
        )
        self.dao.touch_event_after_registration(event)
        self.db.commit()
        self.db.refresh(registration)
        return self._registration_to_dict(registration)

    @staticmethod
    def _faq_to_dict(row) -> dict[str, Any]:
        return {
            "id": row.id,
            "category": row.category,
            "question": row.question,
            "answer": row.answer,
            "keywords": row.keywords,
        }

    @staticmethod
    def _project_to_dict(row) -> dict[str, Any]:
        return {
            "id": row.id,
            "project_name": row.project_name,
            "project_type": row.project_type,
            "target_country": row.target_country,
            "target_education_level": row.target_education_level,
            "target_audience": row.target_audience,
            "project_desc": row.project_desc,
            "price_range": row.price_range,
        }

    @staticmethod
    def _event_to_dict(row) -> dict[str, Any]:
        return {
            "id": row.id,
            "event_no": row.event_no,
            "event_name": row.event_name,
            "event_type": row.event_type,
            "topic": row.topic,
            "speaker": row.speaker,
            "start_time": row.start_time.isoformat() if row.start_time else None,
            "end_time": row.end_time.isoformat() if row.end_time else None,
            "location": row.location,
            "online_url": row.online_url,
            "max_participants": row.max_participants,
            "current_participants": row.current_participants,
            "status": row.status,
        }

    @staticmethod
    def _registration_to_dict(row: EventRegistration) -> dict[str, Any]:
        return {
            "id": row.id,
            "event_id": row.event_id,
            "lead_id": row.lead_id,
            "visitor_name": row.visitor_name,
            "visitor_phone": row.visitor_phone,
            "registration_status": row.registration_status,
            "remark": row.remark,
            "create_time": row.create_time,
        }

