from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.ai_tools.service_agent_tools import (
    create_activity_signup as tool_create_activity_signup,
    list_open_events,
    recommend_course_projects,
    search_customer_service_faq,
)
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

router = APIRouter()


@router.post("/messages", summary="访客发送客服消息并直接返回回复")
def send_message(request: ServiceAgentMessageRequest, db: Session = Depends(get_db)):
    data = ServiceAgentService(db).handle_visitor_message(request)
    return success(data, trace_id=data.get("trace_id"))


@router.get("/faqs", summary="查询客服 FAQ")
def search_faq(
    keyword: str | None = Query(default=None, max_length=200, description="关键词"),
    category: str | None = Query(default=None, max_length=100, description="FAQ 分类"),
    limit: int = Query(default=5, ge=1, le=20, description="返回条数"),
    trace_id: str | None = Query(default=None, description="链路追踪 ID"),
    db: Session = Depends(get_db),
):
    request = ServiceAgentFaqSearchRequest(
        keyword=keyword,
        category=category,
        limit=limit,
        trace_id=trace_id,
        caller="other",
    )
    return success(ServiceAgentService(db).search_faq(request), trace_id=trace_id)


@router.get("/projects", summary="查询课程与项目推荐")
def search_projects(
    keyword: str | None = Query(default=None, max_length=200, description="关键词"),
    project_type: str | None = Query(default=None, max_length=50, description="项目类型"),
    target_country: str | None = Query(default=None, max_length=100, description="目标国家"),
    education_level: str | None = Query(default=None, max_length=100, description="学历阶段"),
    limit: int = Query(default=5, ge=1, le=20, description="返回条数"),
    trace_id: str | None = Query(default=None, description="链路追踪 ID"),
    db: Session = Depends(get_db),
):
    request = ServiceAgentProjectSearchRequest(
        keyword=keyword,
        project_type=project_type,
        target_country=target_country,
        education_level=education_level,
        limit=limit,
        trace_id=trace_id,
        caller="other",
    )
    return success(ServiceAgentService(db).search_projects(request), trace_id=trace_id)


@router.get("/events", summary="查询可报名活动")
def list_events(
    keyword: str | None = Query(default=None, max_length=200, description="关键词"),
    event_type: str | None = Query(default=None, max_length=30, description="活动类型"),
    status: str | None = Query(default="open", max_length=30, description="活动状态"),
    limit: int = Query(default=10, ge=1, le=50, description="返回条数"),
    trace_id: str | None = Query(default=None, description="链路追踪 ID"),
    db: Session = Depends(get_db),
):
    request = ServiceAgentEventSearchRequest(
        keyword=keyword,
        event_type=event_type,
        status=status,
        limit=limit,
        trace_id=trace_id,
        caller="other",
    )
    return success(ServiceAgentService(db).list_events(request), trace_id=trace_id)


@router.post("/activity-signups", summary="创建活动报名并直接写入报名表")
def create_activity_signup(request: ActivitySignupRequest, db: Session = Depends(get_db)):
    data = ServiceAgentService(db).create_activity_signup(request)
    return success(data, trace_id=request.trace_id)


@router.post(
    "/dify-tools/search_customer_service_faq",
    summary="Dify 工具：查询客服 FAQ",
    include_in_schema=False,
)
def dify_search_customer_service_faq(request: ServiceAgentFaqSearchRequest, db: Session = Depends(get_db)):
    data = search_customer_service_faq(db, request)
    return success({"tool_name": "search_customer_service_faq", "result": data}, trace_id=request.trace_id)


@router.post(
    "/dify-tools/recommend_course_projects",
    summary="Dify 工具：查询课程与项目推荐",
    include_in_schema=False,
)
def dify_recommend_course_projects(request: ServiceAgentProjectSearchRequest, db: Session = Depends(get_db)):
    data = recommend_course_projects(db, request)
    return success({"tool_name": "recommend_course_projects", "result": data}, trace_id=request.trace_id)


@router.post(
    "/dify-tools/list_open_events",
    summary="Dify 工具：查询可报名活动",
    include_in_schema=False,
)
def dify_list_open_events(request: ServiceAgentEventSearchRequest, db: Session = Depends(get_db)):
    data = list_open_events(db, request)
    return success({"tool_name": "list_open_events", "result": data}, trace_id=request.trace_id)


@router.post(
    "/dify-tools/create_activity_signup",
    summary="Dify 工具：创建活动报名并直接写入报名表",
    include_in_schema=False,
)
def dify_create_activity_signup(request: ActivitySignupRequest, db: Session = Depends(get_db)):
    data = tool_create_activity_signup(db, request)
    return success({"tool_name": "create_activity_signup", "result": data}, trace_id=request.trace_id)

