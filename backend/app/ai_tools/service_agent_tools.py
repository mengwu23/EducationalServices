from sqlalchemy.orm import Session

from app.schemas.service_agent_schema import (
    ActivitySignupRequest,
    ServiceAgentEventSearchRequest,
    ServiceAgentFaqSearchRequest,
    ServiceAgentProjectSearchRequest,
)
from app.services.service_agent_service import ServiceAgentService

TOOL_DESCRIPTIONS = {
    "search_customer_service_faq": "查询客服 FAQ，适用于公司信息、业务规则、留学政策等高频问答",
    "recommend_course_projects": "按访客背景和意向查询可推荐课程或项目",
    "list_open_events": "查询当前可报名活动和讲座",
    "create_activity_signup": "根据对话中抽取的报名字段创建活动报名，并直接写入报名表",
}


def search_customer_service_faq(db: Session, request: ServiceAgentFaqSearchRequest):
    return ServiceAgentService(db).search_faq(request)


def recommend_course_projects(db: Session, request: ServiceAgentProjectSearchRequest):
    return ServiceAgentService(db).search_projects(request)


def list_open_events(db: Session, request: ServiceAgentEventSearchRequest):
    return ServiceAgentService(db).list_events(request)


def create_activity_signup(db: Session, request: ActivitySignupRequest):
    return ServiceAgentService(db).create_activity_signup(request)

