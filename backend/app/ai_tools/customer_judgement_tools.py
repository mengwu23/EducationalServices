"""供 Dify 或其他代理调用客户研判工具时的适配层。"""

from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.security import CurrentUser
from backend.app.schemas.customer_judgement_schema import CustomerJudgementRequest
from backend.app.services.customer_judgement_service import CustomerJudgementService

# 暴露给编排层的工具注册表。
CUSTOMER_JUDGEMENT_TOOLS = {
    "analyze_customer": "提交客户信息进行智能画像研判，返回匹配评分、维度分析和后续跟进建议",
}


def get_customer_judgement_tools() -> dict[str, str]:
    """返回工具名称及其中文说明。"""
    return CUSTOMER_JUDGEMENT_TOOLS


def execute_customer_judgement_tool(tool_name: str, arguments: dict[str, Any], db: Session) -> dict[str, Any]:
    """将外部工具调用分发到客户研判服务层。"""
    if tool_name == "analyze_customer":
        text = arguments.get("text", "")
        if not text:
            raise ValueError("arguments.text 为必填字段")
        request = CustomerJudgementRequest(
            text=text,
            sys_query=arguments.get("sys_query"),
            lead_id=arguments.get("lead_id"),
            target_product=arguments.get("target_product"),
        )
        # 工具调用使用系统身份
        service = CustomerJudgementService(db)
        return service.analyze_customer(request, CurrentUser(id=0, role="admin"))

    raise ValueError(f"Unsupported customer judgement tool: {tool_name}")
