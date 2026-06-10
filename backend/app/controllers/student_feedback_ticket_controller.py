from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.student_feedback_ticket_schema import (
    FeedbackAssignRequest,
    FeedbackCloseRequest,
    FeedbackResolveRequest,
    StudentFeedbackTicketCreate,
    StudentFeedbackTicketOut,
    StudentFeedbackTicketPage,
    StudentFeedbackTicketUpdate,
)
from backend.app.services.student_feedback_ticket_service import StudentFeedbackTicketService

router = APIRouter(prefix="/student-feedback-tickets", tags=["学生反馈工单"])


@router.post(
    "",
    response_model=StudentFeedbackTicketOut,
    status_code=status.HTTP_201_CREATED,
    summary="创建学生反馈工单",
)
def create_student_feedback_ticket(
    payload: StudentFeedbackTicketCreate,
    db: Session = Depends(get_db),
):
    return StudentFeedbackTicketService.create_ticket(db, payload)


@router.get("", response_model=StudentFeedbackTicketPage, summary="查询学生反馈工单列表")
def list_student_feedback_tickets(
    student_id: Optional[int] = Query(default=None),
    status_value: Optional[str] = Query(default=None, alias="status"),
    handler_employee_id: Optional[int] = Query(default=None),
    category: Optional[str] = Query(default=None),
    priority_level: Optional[str] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total, page, size = StudentFeedbackTicketService.list_tickets(
        db,
        student_id=student_id,
        status=status_value,
        handler_employee_id=handler_employee_id,
        category=category,
        priority_level=priority_level,
        keyword=keyword,
        page=page,
        size=size,
    )
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{ticket_id}", response_model=StudentFeedbackTicketOut, summary="获取学生反馈工单详情")
def get_student_feedback_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return StudentFeedbackTicketService.get_ticket(db, ticket_id)


@router.patch("/{ticket_id}", response_model=StudentFeedbackTicketOut, summary="更新学生反馈工单")
def update_student_feedback_ticket(
    ticket_id: int,
    payload: StudentFeedbackTicketUpdate,
    db: Session = Depends(get_db),
):
    return StudentFeedbackTicketService.update_ticket(db, ticket_id, payload)


@router.post("/{ticket_id}/assign", response_model=StudentFeedbackTicketOut, summary="分配学生反馈工单")
def assign_student_feedback_ticket(
    ticket_id: int,
    payload: FeedbackAssignRequest,
    db: Session = Depends(get_db),
):
    return StudentFeedbackTicketService.assign_ticket(db, ticket_id, payload)


@router.post("/{ticket_id}/resolve", response_model=StudentFeedbackTicketOut, summary="解决学生反馈工单")
def resolve_student_feedback_ticket(
    ticket_id: int,
    payload: FeedbackResolveRequest,
    db: Session = Depends(get_db),
):
    return StudentFeedbackTicketService.resolve_ticket(db, ticket_id, payload)


@router.post("/{ticket_id}/close", response_model=StudentFeedbackTicketOut, summary="关闭学生反馈工单")
def close_student_feedback_ticket(
    ticket_id: int,
    payload: FeedbackCloseRequest,
    db: Session = Depends(get_db),
):
    return StudentFeedbackTicketService.close_ticket(db, ticket_id, payload)
