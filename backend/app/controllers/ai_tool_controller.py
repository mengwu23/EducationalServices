from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.ai_tools.registry import invoke_ai_tool
from backend.app.common.responses import ApiResponse, success_response
from backend.app.database import get_db
from backend.app.schemas.ai_tool_schema import AiToolInvokeRequest

router = APIRouter(prefix="/ai-tools", tags=["AI 工具"])


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
