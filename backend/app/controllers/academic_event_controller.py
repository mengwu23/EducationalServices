from datetime import datetime, timedelta
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


# ── 学业风险检测与智能提醒 ──

@router.get("/approaching-deadlines", response_model=ApiResponse, summary="查询临期/逾期学业事件")
def list_approaching_deadlines(
    student_id: Optional[int] = Query(default=None, description="学生ID，不传则查全部"),
    within_days: int = Query(default=7, ge=1, le=90, description="未来N天内到期的事件"),
    include_overdue: bool = Query(default=True, description="是否包含已逾期事件"),
    db: Session = Depends(get_db),
):
    """查询即将到期或已逾期的学业事件（学业风险检测）

    用于：
    - 学生端：显示即将到期的论文DDL、考试时间
    - 老师端：掌握学生的学业风险分布
    - 企业助手/Dify：自动推送临期提醒

    参数：
        within_days=7  — 查询未来7天内到期的事件
        include_overdue=true — 同时返回已过期但未完成的事件
    """
    now = datetime.now()
    deadline_before = now + timedelta(days=within_days)

    items, total, page, size = AcademicEventService.list_events(
        db,
        student_id=student_id,
        status="active",
        deadline_from=now if include_overdue else None,
        deadline_to=deadline_before,
        page=1,
        size=100,
    )
    data = AcademicEventPage(
        items=[AcademicEventOut.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )
    return success_response(
        data=data,
        message=f"查询到 {total} 条临期/逾期学业事件（{within_days}天内到期）",
    )


@router.get("/upcoming-reminders", response_model=ApiResponse, summary="查询即将触发提醒的学业事件")
def list_upcoming_reminders(
    student_id: Optional[int] = Query(default=None, description="学生ID"),
    db: Session = Depends(get_db),
):
    """查询设置了提醒且提醒时间已到/临近的学业事件

    用于：
    - 定时任务扫描：找出需要触发提醒的事件
    - 学生端：查看自己设置的考试/DDL提醒列表
    - 企业助手：向学生推送提醒消息

    返回 reminder_time 已到或即将到达（1小时内）的活跃事件。
    """
    now = datetime.now()
    reminder_window_start = now - timedelta(hours=1)  # 1小时内应触发
    reminder_window_end = now + timedelta(hours=1)

    from backend.app.daos.academic_event_dao import AcademicEventDAO
    from backend.app.models.academic_event import AcademicEvent

    query = db.query(AcademicEvent).filter(
        AcademicEvent.status == "active",
        AcademicEvent.reminder_time.isnot(None),
        AcademicEvent.reminder_time >= reminder_window_start,
        AcademicEvent.reminder_time <= reminder_window_end,
        AcademicEvent.is_delete == 0,
    )
    if student_id is not None:
        query = query.filter(AcademicEvent.student_id == student_id)

    items = query.order_by(AcademicEvent.reminder_time.asc()).all()
    total = len(items)

    data = AcademicEventPage(
        items=[AcademicEventOut.model_validate(item) for item in items],
        total=total,
        page=1,
        size=max(total, 1),
    )
    return success_response(
        data=data,
        message=f"查询到 {total} 条待触发提醒的学业事件",
    )
