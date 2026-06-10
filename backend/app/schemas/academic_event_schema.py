from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app.common.enums import AcademicEventStatus, AcademicEventType


class AcademicEventBase(BaseModel):
    student_id: Optional[int] = None
    event_type: AcademicEventType
    title: str = Field(..., min_length=1, max_length=300)
    event_desc: Optional[str] = None
    course_name: Optional[str] = Field(default=None, max_length=200)
    deadline_time: datetime
    reminder_time: Optional[datetime] = None


class AcademicEventCreate(AcademicEventBase):
    status: AcademicEventStatus = AcademicEventStatus.ACTIVE


class AcademicEventUpdate(BaseModel):
    student_id: Optional[int] = None
    event_type: Optional[AcademicEventType] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    event_desc: Optional[str] = None
    course_name: Optional[str] = Field(default=None, max_length=200)
    deadline_time: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    status: Optional[AcademicEventStatus] = None


class AcademicEventOut(BaseModel):
    id: int
    student_id: Optional[int] = None
    event_type: AcademicEventType
    title: str
    event_desc: Optional[str] = None
    course_name: Optional[str] = None
    deadline_time: datetime
    reminder_time: Optional[datetime] = None
    status: AcademicEventStatus
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


class AcademicEventPage(BaseModel):
    items: List[AcademicEventOut]
    total: int
    page: int
    size: int
