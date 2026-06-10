"""客户画像研判的 HTTP 接口。"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.responses import success
from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.customer_judgement_schema import (
    CustomerJudgementRequest,
    JudgementListRequest,
)
from app.services.customer_judgement_service import CustomerJudgementService

router = APIRouter(prefix="/api/v1/customer-judgement", tags=["客户画像研判"])


@router.post("/analyze", summary="提交客户画像研判")
def analyze_customer(
    request: CustomerJudgementRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """提交客户信息文本，调用 Dify 工作流进行智能画像研判。"""
    data = CustomerJudgementService(db).analyze_customer(request, user)
    return success(data)


@router.get("/records", summary="查询研判记录列表")
def list_records(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    status: str | None = Query(default=None, description="筛选状态"),
    lead_id: int | None = Query(default=None, description="筛选关联线索ID"),
    match_level: str | None = Query(default=None, description="筛选匹配等级"),
    date_start: date | None = Query(default=None, description="创建开始日期"),
    date_end: date | None = Query(default=None, description="创建结束日期"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """分页查询研判记录列表，支持按状态、线索、匹配等级、日期范围筛选。"""
    req = JudgementListRequest(
        page=page,
        page_size=page_size,
        status=status,
        lead_id=lead_id,
        match_level=match_level,
        date_start=date_start,
        date_end=date_end,
    )
    data = CustomerJudgementService(db).list_analysis_records(req, user)
    return success(data)


@router.get("/records/{record_id}", summary="查询研判记录详情")
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """获取单条研判记录的完整详情，包含 AI 研判结果。"""
    data = CustomerJudgementService(db).get_analysis_record(record_id, user)
    return success(data)
