from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.ai_tools.registry import invoke_ai_tool
from backend.app.ai_tools.report_tools import query_report_source_data
from backend.app.common.responses import ApiResponse, success_response
from backend.app.core.security import verify_ai_tools_secret
from backend.app.database import get_db
from backend.app.schemas.ai_tool_schema import AiToolInvokeRequest
from backend.app.schemas.report_schema import AiToolReportSourceDataRequest

router = APIRouter(prefix="/ai-tools", tags=["AI 工具"], dependencies=[Depends(verify_ai_tools_secret)])


@router.get("", response_model=ApiResponse, summary="查询 AI 工具列表")
def list_ai_tools():
    return success_response(
        data=[
            {
                "tool_name": "query_report_source_data",
                "description": "查询智能报告生成所需的聚合数据摘要",
            }
        ]
    )


@router.post(
    "/{tool_name:path}/invoke",
    response_model=ApiResponse,
    summary="调用已注册的 AI 工具",
)
def invoke_registered_ai_tool(
    tool_name: str,
    payload: AiToolInvokeRequest,
    db: Session = Depends(get_db),
):
    return success_response(
        data={
            "tool_name": tool_name,
            "result": invoke_ai_tool(tool_name, db, payload.arguments),
        }
    )


@router.post("/query_report_source_data", response_model=ApiResponse, summary="查询报告生成源数据")
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
    return success_response(
        data={
            "tool_name": "query_report_source_data",
            "result": data,
            "draft_id": None,
            "requires_confirmation": False,
        }
    )
