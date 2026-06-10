from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.common.responses import ApiResponse, success_response
from backend.app.database import get_db
from backend.app.schemas.academic_event_schema import (
    AcademicEventCreate,
    AcademicEventOut,
    AcademicEventPage,
    AcademicEventUpdate,
)
from backend.app.services.academic_event_service import AcademicEventService

router = APIRouter(prefix="/academic-events", tags=["学业事件"])


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建学业事件",
)
def create_academic_event(payload: AcademicEventCreate, db: Session = Depends(get_db)):
    event = AcademicEventService.create_event(db, payload)
    return success_response(data=AcademicEventOut.model_validate(event), message="学业事件创建成功")


@router.get("", response_model=ApiResponse, summary="查询学业事件列表")
def list_academic_events(
    student_id: Optional[int] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    status_value: Optional[str] = Query(default=None, alias="status"),
    deadline_from: Optional[datetime] = Query(default=None),
    deadline_to: Optional[datetime] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total, page, size = AcademicEventService.list_events(
        db,
        student_id=student_id,
        event_type=event_type,
        status=status_value,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        keyword=keyword,
        page=page,
        size=size,
    )
    data = AcademicEventPage(
        items=[AcademicEventOut.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )
    return success_response(data=data)


@router.get("/{event_id}", response_model=ApiResponse, summary="获取学业事件详情")
def get_academic_event(event_id: int, db: Session = Depends(get_db)):
    event = AcademicEventService.get_event(db, event_id)
    return success_response(data=AcademicEventOut.model_validate(event))


@router.patch("/{event_id}", response_model=ApiResponse, summary="更新学业事件")
def update_academic_event(
    event_id: int,
    payload: AcademicEventUpdate,
    db: Session = Depends(get_db),
):
    event = AcademicEventService.update_event(db, event_id, payload)
    return success_response(data=AcademicEventOut.model_validate(event), message="学业事件更新成功")


@router.post("/{event_id}/complete", response_model=ApiResponse, summary="完成学业事件")
def complete_academic_event(event_id: int, db: Session = Depends(get_db)):
    event = AcademicEventService.complete_event(db, event_id)
    return success_response(data=AcademicEventOut.model_validate(event), message="学业事件已完成")


@router.post("/{event_id}/cancel", response_model=ApiResponse, summary="取消学业事件")
def cancel_academic_event(event_id: int, db: Session = Depends(get_db)):
    event = AcademicEventService.cancel_event(db, event_id)
    return success_response(data=AcademicEventOut.model_validate(event), message="学业事件已取消")
