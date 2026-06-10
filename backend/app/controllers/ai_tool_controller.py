from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai_tools.report_tools import query_report_source_data
from app.common.responses import success
from app.core.security import verify_ai_tools_secret
from app.db.session import get_db
from app.schemas.report_schema import AiToolReportSourceDataRequest

router = APIRouter(prefix="/api/v1/ai-tools", tags=["ai-tools"], dependencies=[Depends(verify_ai_tools_secret)])


@router.get("")
def list_ai_tools():
    return success(
        [
            {
                "tool_name": "query_report_source_data",
                "description": "查询智能报告生成所需的聚合数据摘要",
            }
        ]
    )


@router.post("/query_report_source_data")
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
            "draft_id": None,
            "requires_confirmation": False,
        },
        trace_id=request.trace_id,
    )
