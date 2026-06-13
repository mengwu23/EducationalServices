from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.academic_event import AcademicEvent


class AcademicEventDAO:
    @staticmethod
    def create(db: Session, data: dict) -> AcademicEvent:
        event = AcademicEvent(**data)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_by_id(db: Session, event_id: int) -> Optional[AcademicEvent]:
        return db.query(AcademicEvent).filter(AcademicEvent.id == event_id).first()

    @staticmethod
    def list(
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
    ) -> tuple[list[AcademicEvent], int]:
        query = db.query(AcademicEvent)
        if student_id is not None:
            query = query.filter(AcademicEvent.student_id == student_id)
        if event_type:
            query = query.filter(AcademicEvent.event_type == event_type)
        if status:
            query = query.filter(AcademicEvent.status == status)
        if deadline_from:
            query = query.filter(AcademicEvent.deadline_time >= deadline_from)
        if deadline_to:
            query = query.filter(AcademicEvent.deadline_time <= deadline_to)
        if keyword:
            like_value = f"%{keyword}%"
            query = query.filter(AcademicEvent.title.like(like_value))

        total = query.count()
        items = (
            query.order_by(AcademicEvent.deadline_time.asc(), AcademicEvent.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return items, total

    @staticmethod
    def update(db: Session, event: AcademicEvent, data: dict) -> AcademicEvent:
        for key, value in data.items():
            setattr(event, key, value)
        db.commit()
        db.refresh(event)
        return event
