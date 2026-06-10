"""供 Dify 或其他代理调用企业助手时使用的工具适配层。"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from ..schemas.enterprise_assistant_schema import (
    DailyReportQueryRequest,
    DailyReportSummaryRequest,
    DepartmentQueryRequest,
    EnterpriseAssistantActor,
    FaqQueryRequest,
    LeadQueryRequest,
    StatisticsQueryRequest,
    StudentBusinessQueryRequest,
    TodoQueryRequest,
)
from ..services.enterprise_assistant_service import EnterpriseAssistantService

# 暴露给编排层的工具注册表。
ENTERPRISE_ASSISTANT_TOOLS = {
    "query_leads": "查询意向客户、客户状态和最近跟进信息",
    "query_daily_reports": "查询员工日报明细",
    "summarize_daily_reports": "汇总团队日报",
    "query_departments": "查询组织架构、部门和员工信息",
    "query_enterprise_faqs": "查询企业内部制度与流程 FAQ",
    "query_student_business": "查询学生成绩、请假和投诉反馈等业务信息",
    "query_todos": "查询当前员工待办事项",
    "query_management_statistics": "查询当前权限范围内的管理统计",
}


def get_enterprise_assistant_tools() -> Dict[str, str]:
    """返回工具名称及其中文说明。"""
    return ENTERPRISE_ASSISTANT_TOOLS


def execute_enterprise_assistant_tool(tool_name: str, arguments: Dict[str, Any], db: Session):
    """将外部工具调用分发到企业助手服务层。"""
    service = EnterpriseAssistantService(db)
    actor = _actor(arguments)
    payload = _payload(arguments)

    if tool_name == "query_leads":
        return _to_dict(service.query_leads(LeadQueryRequest(actor=actor, **payload)))
    if tool_name == "query_daily_reports":
        return _to_dict(service.query_daily_reports(DailyReportQueryRequest(actor=actor, **payload)))
    if tool_name == "summarize_daily_reports":
        return _to_dict(service.summarize_daily_reports(DailyReportSummaryRequest(actor=actor, **payload)))
    if tool_name == "query_departments":
        return _to_dict(service.query_departments(DepartmentQueryRequest(actor=actor, **payload)))
    if tool_name == "query_enterprise_faqs":
        return _to_dict(service.query_faqs(FaqQueryRequest(actor=actor, **payload)))
    if tool_name == "query_student_business":
        return _to_dict(service.query_student_business(StudentBusinessQueryRequest(actor=actor, **payload)))
    if tool_name == "query_todos":
        return _to_dict(service.query_todos(TodoQueryRequest(actor=actor, **payload)))
    if tool_name == "query_management_statistics":
        return _to_dict(service.query_statistics(StatisticsQueryRequest(actor=actor, **payload)))

    raise ValueError(f"Unsupported enterprise assistant tool: {tool_name}")


def _to_dict(result: Any) -> Dict[str, Any]:
    """兼容 Pydantic v1/v2，统一转换为普通字典。"""
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result.dict()


def _actor(arguments: Dict[str, Any]) -> EnterpriseAssistantActor:
    """从工具参数中提取操作者上下文。"""
    actor_data = arguments.get("actor") or {}
    return EnterpriseAssistantActor(**actor_data)


def _payload(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """去掉 actor 字段，只保留业务过滤参数。"""
    return {key: value for key, value in arguments.items() if key != "actor"}
