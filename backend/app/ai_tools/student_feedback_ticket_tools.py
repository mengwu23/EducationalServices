from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.common.enums import FeedbackPriorityLevel, FeedbackTicketType
from backend.app.schemas.student_feedback_ticket_schema import StudentFeedbackTicketCreate
from backend.app.services.student_feedback_ticket_service import StudentFeedbackTicketService


class FeedbackTicketToolCreate(BaseModel):
    student_id: int
    ticket_type: FeedbackTicketType = FeedbackTicketType.COMPLAINT
    category: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=300)
    detail: str = Field(..., min_length=1)
    content_summary: Optional[str] = None
    priority_level: FeedbackPriorityLevel = FeedbackPriorityLevel.NORMAL


class FeedbackTicketToolList(BaseModel):
    student_id: Optional[int] = None
    status: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


def create_feedback_ticket(db: Session, payload: FeedbackTicketToolCreate) -> dict:
    ticket = StudentFeedbackTicketService.create_ticket(
        db,
        StudentFeedbackTicketCreate(**payload.dict()),
    )
    return {
        "id": ticket.id,
        "ticket_no": ticket.ticket_no,
        "student_id": ticket.student_id,
        "ticket_type": ticket.ticket_type,
        "priority_level": ticket.priority_level,
        "status": ticket.status,
        "title": ticket.title,
    }


def list_feedback_tickets(db: Session, payload: FeedbackTicketToolList) -> dict:
    items, total, page, size = StudentFeedbackTicketService.list_tickets(
        db,
        student_id=payload.student_id,
        status=payload.status,
        page=1,
        size=payload.limit,
    )
    return {
        "items": [
            {
                "id": item.id,
                "ticket_no": item.ticket_no,
                "student_id": item.student_id,
                "title": item.title,
                "priority_level": item.priority_level,
                "status": item.status,
                "handler_employee_id": item.handler_employee_id,
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "size": size,
    }
