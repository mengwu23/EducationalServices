from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.common.enums import AcademicEventStatus
from backend.app.common.exceptions import BadRequestError, NotFoundError
from backend.app.common.pagination import normalize_page
from backend.app.daos.academic_event_dao import AcademicEventDAO
from backend.app.models.academic_event import AcademicEvent
from backend.app.schemas.academic_event_schema import AcademicEventCreate, AcademicEventUpdate


class AcademicEventService:
    @staticmethod
    def _get_or_raise(db: Session, event_id: int) -> AcademicEvent:
        event = AcademicEventDAO.get_by_id(db, event_id)
        if event is None:
            raise NotFoundError("Academic event not found")
        return event

    @staticmethod
    def _validate_time(deadline_time: datetime, reminder_time: Optional[datetime]) -> None:
        if reminder_time and reminder_time > deadline_time:
            raise BadRequestError("Reminder time cannot be later than deadline time")

    @classmethod
    def create_event(cls, db: Session, payload: AcademicEventCreate) -> AcademicEvent:
        data = payload.dict()
        data["event_type"] = payload.event_type.value
        data["status"] = payload.status.value
        cls._validate_time(data["deadline_time"], data.get("reminder_time"))
        return AcademicEventDAO.create(db, data)

    @staticmethod
    def list_events(
        db: Session,
        *,
        student_id: Optional[int] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        deadline_from: Optional[datetime] = None,
        deadline_to: Optional[datetime] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[AcademicEvent], int, int, int]:
        page, size = normalize_page(page, size)
        items, total = AcademicEventDAO.list(
            db,
            student_id=student_id,
            event_type=event_type,
            status=status,
            deadline_from=deadline_from,
            deadline_to=deadline_to,
            keyword=keyword,
            page=page,
            size=size,
        )
        return items, total, page, size

    @classmethod
    def get_event(cls, db: Session, event_id: int) -> AcademicEvent:
        return cls._get_or_raise(db, event_id)

    @classmethod
    def update_event(cls, db: Session, event_id: int, payload: AcademicEventUpdate) -> AcademicEvent:
        event = cls._get_or_raise(db, event_id)
        data = payload.dict(exclude_unset=True)
        if "event_type" in data and data["event_type"] is not None:
            data["event_type"] = data["event_type"].value
        if "status" in data and data["status"] is not None:
            data["status"] = data["status"].value

        deadline_time = data.get("deadline_time", event.deadline_time)
        reminder_time = data.get("reminder_time", event.reminder_time)
        cls._validate_time(deadline_time, reminder_time)
        return AcademicEventDAO.update(db, event, data)

    @classmethod
    def complete_event(cls, db: Session, event_id: int) -> AcademicEvent:
        event = cls._get_or_raise(db, event_id)
        if event.status != AcademicEventStatus.ACTIVE.value:
            raise BadRequestError("Only active academic events can be completed")
        return AcademicEventDAO.update(db, event, {"status": AcademicEventStatus.COMPLETED.value})

    @classmethod
    def cancel_event(cls, db: Session, event_id: int) -> AcademicEvent:
        event = cls._get_or_raise(db, event_id)
        if event.status == AcademicEventStatus.COMPLETED.value:
            raise BadRequestError("Completed academic events cannot be cancelled")
        return AcademicEventDAO.update(db, event, {"status": AcademicEventStatus.CANCELLED.value})
