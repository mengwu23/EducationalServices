from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.responses import success
from app.db.session import get_db
from app.schemas.service_agent_schema import (
    ActivitySignupRequest,
    ServiceAgentEventSearchRequest,
    ServiceAgentFaqSearchRequest,
    ServiceAgentMessageRequest,
    ServiceAgentProjectSearchRequest,
)
from app.services.service_agent_service import ServiceAgentService

router = APIRouter(prefix="/api/v1/service-agent", tags=["客服 Agent"])


@router.post("/messages", summary="访客发送客服消息并直接返回回复")
def send_message(request: ServiceAgentMessageRequest, db: Session = Depends(get_db)):
    data = ServiceAgentService(db).handle_visitor_message(request)
    return success(data, trace_id=data.get("trace_id"))


@router.post("/faq/search", summary="查询客服 FAQ")
def search_faq(request: ServiceAgentFaqSearchRequest, db: Session = Depends(get_db)):
    return success(ServiceAgentService(db).search_faq(request), trace_id=request.trace_id)


@router.post("/projects/search", summary="查询课程与项目推荐")
def search_projects(request: ServiceAgentProjectSearchRequest, db: Session = Depends(get_db)):
    return success(ServiceAgentService(db).search_projects(request), trace_id=request.trace_id)


@router.post("/events/search", summary="查询可报名活动")
def list_events(request: ServiceAgentEventSearchRequest, db: Session = Depends(get_db)):
    return success(ServiceAgentService(db).list_events(request), trace_id=request.trace_id)


@router.post("/activity-signups", summary="创建活动报名并直接写入报名表")
def create_activity_signup(request: ActivitySignupRequest, db: Session = Depends(get_db)):
    data = ServiceAgentService(db).create_activity_signup(request)
    return success(data, trace_id=request.trace_id)

