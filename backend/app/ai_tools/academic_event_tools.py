from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.common.enums import AcademicEventType
from backend.app.schemas.academic_event_schema import AcademicEventCreate
from backend.app.services.academic_event_service import AcademicEventService


class AcademicEventToolCreate(BaseModel):
    student_id: Optional[int] = None
    event_type: AcademicEventType = AcademicEventType.OTHER
    title: str = Field(..., min_length=1, max_length=300)
    event_desc: Optional[str] = None
    course_name: Optional[str] = None
    deadline_time: datetime
    reminder_time: Optional[datetime] = None


class AcademicEventToolList(BaseModel):
    student_id: Optional[int] = None
    limit: int = Field(default=10, ge=1, le=50)


def create_academic_event(db: Session, payload: AcademicEventToolCreate) -> dict:
    event = AcademicEventService.create_event(db, AcademicEventCreate(**payload.dict()))
    return {
        "id": event.id,
        "student_id": event.student_id,
        "event_type": event.event_type,
        "title": event.title,
        "deadline_time": event.deadline_time.isoformat(),
        "reminder_time": event.reminder_time.isoformat() if event.reminder_time else None,
        "status": event.status,
    }


def list_active_academic_events(db: Session, payload: AcademicEventToolList) -> dict:
    items, total, page, size = AcademicEventService.list_events(
        db,
        student_id=payload.student_id,
        status="active",
        page=1,
        size=payload.limit,
    )
    return {
        "items": [
            {
                "id": item.id,
                "student_id": item.student_id,
                "event_type": item.event_type,
                "title": item.title,
                "deadline_time": item.deadline_time.isoformat(),
                "reminder_time": item.reminder_time.isoformat() if item.reminder_time else None,
                "status": item.status,
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "size": size,
    }
