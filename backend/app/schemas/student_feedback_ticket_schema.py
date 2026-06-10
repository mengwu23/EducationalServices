from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app.common.enums import (
    FeedbackPriorityLevel,
    FeedbackTicketStatus,
    FeedbackTicketType,
)


class StudentFeedbackTicketBase(BaseModel):
    student_id: int
    ticket_type: FeedbackTicketType = FeedbackTicketType.COMPLAINT
    category: Optional[str] = Field(default=None, max_length=100)
    title: str = Field(..., min_length=1, max_length=300)
    content_summary: Optional[str] = None
    detail: str = Field(..., min_length=1)
    priority_level: FeedbackPriorityLevel = FeedbackPriorityLevel.NORMAL


class StudentFeedbackTicketCreate(StudentFeedbackTicketBase):
    ticket_no: Optional[str] = Field(default=None, max_length=50)
    handler_employee_id: Optional[int] = None


class StudentFeedbackTicketUpdate(BaseModel):
    ticket_type: Optional[FeedbackTicketType] = None
    category: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    content_summary: Optional[str] = None
    detail: Optional[str] = Field(default=None, min_length=1)
    priority_level: Optional[FeedbackPriorityLevel] = None
    status: Optional[FeedbackTicketStatus] = None
    handler_employee_id: Optional[int] = None
    solution: Optional[str] = None
    satisfaction_score: Optional[int] = Field(default=None, ge=1, le=5)
    is_notified: Optional[int] = Field(default=None, ge=0, le=1)


class FeedbackAssignRequest(BaseModel):
    handler_employee_id: int


class FeedbackResolveRequest(BaseModel):
    solution: str = Field(..., min_length=1)
    notify_student: bool = True


class FeedbackCloseRequest(BaseModel):
    satisfaction_score: Optional[int] = Field(default=None, ge=1, le=5)


class StudentFeedbackTicketOut(BaseModel):
    id: int
    ticket_no: str
    student_id: int
    ticket_type: FeedbackTicketType
    category: Optional[str] = None
    title: str
    content_summary: Optional[str] = None
    detail: str
    priority_level: FeedbackPriorityLevel
    status: FeedbackTicketStatus
    handler_employee_id: Optional[int] = None
    solution: Optional[str] = None
    satisfaction_score: Optional[int] = None
    is_notified: int
    close_time: Optional[datetime] = None
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentFeedbackTicketPage(BaseModel):
    items: List[StudentFeedbackTicketOut]
    total: int
    page: int
    size: int
