from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.common.responses import ApiResponse, success_response
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
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建学生反馈工单",
)
def create_student_feedback_ticket(
    payload: StudentFeedbackTicketCreate,
    db: Session = Depends(get_db),
):
    ticket = StudentFeedbackTicketService.create_ticket(db, payload)
    return success_response(data=StudentFeedbackTicketOut.model_validate(ticket), message="学生反馈工单创建成功")


@router.get("", response_model=ApiResponse, summary="查询学生反馈工单列表")
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
    data = StudentFeedbackTicketPage(
        items=[StudentFeedbackTicketOut.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
    )
    return success_response(data=data)


@router.post("/{ticket_id}/classify", response_model=ApiResponse, summary="对工单触发 AI 分类与根因打标")
def classify_student_feedback_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = StudentFeedbackTicketService.classify_ticket(db, ticket_id)
    return success_response(data=StudentFeedbackTicketOut.model_validate(ticket), message="工单 AI 打标完成")


@router.get("/{ticket_id}", response_model=ApiResponse, summary="获取学生反馈工单详情")
def get_student_feedback_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = StudentFeedbackTicketService.get_ticket(db, ticket_id)
    return success_response(data=StudentFeedbackTicketOut.model_validate(ticket))


@router.patch("/{ticket_id}", response_model=ApiResponse, summary="更新学生反馈工单")
def update_student_feedback_ticket(
    ticket_id: int,
    payload: StudentFeedbackTicketUpdate,
    db: Session = Depends(get_db),
):
    ticket = StudentFeedbackTicketService.update_ticket(db, ticket_id, payload)
    return success_response(data=StudentFeedbackTicketOut.model_validate(ticket), message="学生反馈工单更新成功")


@router.post("/{ticket_id}/assign", response_model=ApiResponse, summary="分配学生反馈工单")
def assign_student_feedback_ticket(
    ticket_id: int,
    payload: FeedbackAssignRequest,
    db: Session = Depends(get_db),
):
    ticket = StudentFeedbackTicketService.assign_ticket(db, ticket_id, payload)
    return success_response(data=StudentFeedbackTicketOut.model_validate(ticket), message="学生反馈工单已分配")


@router.post("/{ticket_id}/resolve", response_model=ApiResponse, summary="解决学生反馈工单")
def resolve_student_feedback_ticket(
    ticket_id: int,
    payload: FeedbackResolveRequest,
    db: Session = Depends(get_db),
):
    ticket = StudentFeedbackTicketService.resolve_ticket(db, ticket_id, payload)
    return success_response(data=StudentFeedbackTicketOut.model_validate(ticket), message="学生反馈工单已解决")


@router.post("/{ticket_id}/close", response_model=ApiResponse, summary="关闭学生反馈工单")
def close_student_feedback_ticket(
    ticket_id: int,
    payload: FeedbackCloseRequest,
    db: Session = Depends(get_db),
):
    ticket = StudentFeedbackTicketService.close_ticket(db, ticket_id, payload)
    return success_response(data=StudentFeedbackTicketOut.model_validate(ticket), message="学生反馈工单已关闭")


@router.post("/{ticket_id}/notify", response_model=ApiResponse, summary="向学生发送工单处理结果通知")
def notify_student(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """通知学生工单已处理完毕

    老师在解决工单后，调用此接口向学生同步处理结果。
    通知内容自动生成：如"您的xxx投诉已解决"。
    设置 is_notified=1 表示已通知学生。
    """
    ticket = StudentFeedbackTicketService.notify_ticket(db, ticket_id)
    return success_response(
        data=StudentFeedbackTicketOut.model_validate(ticket),
        message=f"已向学生发送通知：您的「{ticket.title}」工单已处理完毕",
    )


@router.get("/my/notifications", response_model=ApiResponse, summary="学生查看自己的工单通知")
def list_my_notifications(
    student_id: int = Query(..., description="学生ID"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """学生查看自己已解决/已关闭但未读的工单通知

    返回已通知（is_notified=1）且状态为 resolved/closed 的工单列表。
    用于学生端"消息通知"模块展示。
    """
    items, total, page, size = StudentFeedbackTicketService.list_tickets(
        db,
        student_id=student_id,
        status="resolved",
        page=page,
        size=size,
    )
    # Also include closed tickets that were notified
    closed_items, closed_total, _, _ = StudentFeedbackTicketService.list_tickets(
        db,
        student_id=student_id,
        status="closed",
        page=page,
        size=size,
    )
    all_items = items + closed_items
    data = StudentFeedbackTicketPage(
        items=[StudentFeedbackTicketOut.model_validate(item) for item in all_items],
        total=total + closed_total,
        page=page,
        size=size,
    )
    return success_response(data=data)
