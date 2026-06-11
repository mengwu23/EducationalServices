from app.models.course_project import CourseProject
from app.models.event_registration import EventRegistration
from app.models.faq_qa import FaqQa
from app.schemas.service_agent_schema import (
    ActivitySignupRequest,
    ServiceAgentMessageRequest,
    ServiceAgentProjectSearchRequest,
)
from app.services.service_agent_service import ServiceAgentService


def seed_service_agent_content(db_session):
    db_session.add_all(
        [
            FaqQa(
                id=1,
                module_scope="customer_service",
                category="company",
                question="你们提供哪些留学服务？",
                answer="我们提供留学规划、申请指导、语言培训和背景提升服务。",
                keywords="留学,服务,申请",
            ),
            CourseProject(
                id=1,
                project_name="新加坡硕士申请规划",
                project_type="application",
                target_country="新加坡",
                target_education_level="本科",
                target_audience="计划申请新加坡硕士的本科学生",
                project_desc="覆盖选校定位、材料规划和申请节奏管理。",
                price_range="咨询后报价",
            ),
        ]
    )
    db_session.commit()


def test_visitor_message_returns_reply_directly(db_session):
    seed_service_agent_content(db_session)
    service = ServiceAgentService(db_session)

    reply = service.handle_visitor_message(ServiceAgentMessageRequest(message="你们提供哪些留学服务？"))

    assert reply["visitor_message"] == "你们提供哪些留学服务？"
    assert reply["reply_text"]
    assert reply["trace_id"]


def test_activity_signup_creates_registration_directly(db_session):
    service = ServiceAgentService(db_session)

    result = service.create_activity_signup(
        ActivitySignupRequest(
            event_id=100,
            visitor_name="王同学",
            visitor_phone="13800000001",
            remark="对新加坡项目感兴趣",
        )
    )

    assert result["visitor_name"] == "王同学"
    assert result["registration_status"] == "registered"
    assert db_session.query(EventRegistration).filter(EventRegistration.visitor_phone == "13800000001").count() == 1


def test_project_search_returns_enabled_projects(db_session):
    seed_service_agent_content(db_session)
    service = ServiceAgentService(db_session)

    result = service.search_projects(ServiceAgentProjectSearchRequest(target_country="新加坡"))

    assert result[0]["project_name"] == "新加坡硕士申请规划"

