from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai_tools.report_tools import query_report_source_data
from app.ai_tools.service_agent_tools import (
    TOOL_DESCRIPTIONS as SERVICE_AGENT_TOOL_DESCRIPTIONS,
    create_activity_signup,
    list_open_events,
    recommend_course_projects,
    search_customer_service_faq,
)
from app.common.responses import success
from app.db.session import get_db
from app.schemas.report_schema import AiToolReportSourceDataRequest
from app.schemas.service_agent_schema import (
    ActivitySignupRequest,
    ServiceAgentEventSearchRequest,
    ServiceAgentFaqSearchRequest,
    ServiceAgentProjectSearchRequest,
)

router = APIRouter(prefix="/api/v1/ai-tools", tags=["Dify 工具接口"])


@router.get("", summary="查询可供 Dify 调用的工具列表")
def list_ai_tools():
    tools = [
        {
            "tool_name": "query_report_source_data",
            "description": "查询智能报告生成所需的聚合数据摘要",
        }
    ]
    tools.extend(
        {"tool_name": tool_name, "description": description}
        for tool_name, description in SERVICE_AGENT_TOOL_DESCRIPTIONS.items()
    )
    return success(tools)


@router.post("/query_report_source_data", summary="Dify 工具：查询报告源数据")
def report_source_data(request: AiToolReportSourceDataRequest, db: Session = Depends(get_db)):
    data = query_report_source_data(
        db,
        request.report_type,
        request.date_start,
        request.date_end,
        request.department_id,
        request.owner_user_id,
        request.caller,
        request.conversation_id,
        request.trace_id,
    )
    return success(
        {
            "tool_name": "query_report_source_data",
            "result": data,
        },
        trace_id=request.trace_id,
    )


@router.post("/search_customer_service_faq", summary="Dify 工具：查询客服 FAQ")
def service_agent_faq(request: ServiceAgentFaqSearchRequest, db: Session = Depends(get_db)):
    data = search_customer_service_faq(db, request)
    return success(
        {
            "tool_name": "search_customer_service_faq",
            "result": data,
        },
        trace_id=request.trace_id,
    )


@router.post("/recommend_course_projects", summary="Dify 工具：查询课程与项目推荐")
def service_agent_projects(request: ServiceAgentProjectSearchRequest, db: Session = Depends(get_db)):
    data = recommend_course_projects(db, request)
    return success(
        {
            "tool_name": "recommend_course_projects",
            "result": data,
        },
        trace_id=request.trace_id,
    )


@router.post("/list_open_events", summary="Dify 工具：查询可报名活动")
def service_agent_events(request: ServiceAgentEventSearchRequest, db: Session = Depends(get_db)):
    data = list_open_events(db, request)
    return success(
        {
            "tool_name": "list_open_events",
            "result": data,
        },
        trace_id=request.trace_id,
    )


@router.post("/create_activity_signup", summary="Dify 工具：创建活动报名并直接写入报名表")
def service_agent_signup(request: ActivitySignupRequest, db: Session = Depends(get_db)):
    data = create_activity_signup(db, request)
    return success(
        {
            "tool_name": "create_activity_signup",
            "result": data,
        },
        trace_id=request.trace_id,
    )

