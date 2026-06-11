"""Customer judgement API endpoints."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.common.responses import success
from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.customer_judgement_schema import (
    CustomerJudgementRequest,
    JudgementListRequest,
)
from app.services.customer_judgement_service import CustomerJudgementService

router = APIRouter(prefix="/api/v1/customer-judgement")


@router.post("/analyze", summary="Submit customer info for judgement")
def analyze_customer(
    text: Annotated[str, Form(description="Customer info text (required)")],
    sys_query: Annotated[str | None, Form(description="Extra analysis requirement")] = None,
    lead_id: Annotated[int | None, Form(description="Linked CRM lead ID")] = None,
    target_product: Annotated[str | None, Form(description="Target product")] = None,
    files: Optional[list[UploadFile]] = File(None, description="Attachments (PDF/Word/Excel/image)"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Submit customer info text with optional attachments. Dify workflow analyses and returns structured result."""
    request = CustomerJudgementRequest(
        text=text,
        sys_query=sys_query,
        lead_id=lead_id,
        target_product=target_product,
    )
    data = CustomerJudgementService(db).analyze_customer(request, user, files or [])
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
