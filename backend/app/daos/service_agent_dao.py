from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.course_project import CourseProject
from app.models.event_lecture import EventLecture
from app.models.event_registration import EventRegistration
from app.models.faq_qa import FaqQa


class ServiceAgentDAO:
    def __init__(self, db: Session):
        self.db = db

    def search_faq(self, keyword: str | None, category: str | None, limit: int) -> list[FaqQa]:
        stmt = (
            select(FaqQa)
            .where(
                FaqQa.status == "enabled",
                FaqQa.is_delete == 0,
                FaqQa.module_scope.in_(["customer_service", "common"]),
            )
            .order_by(FaqQa.sort_order.asc(), FaqQa.id.desc())
            .limit(limit)
        )
        if category:
            stmt = stmt.where(FaqQa.category == category)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(FaqQa.question.like(like), FaqQa.answer.like(like), FaqQa.keywords.like(like)))
        return list(self.db.scalars(stmt).all())

    def search_projects(
        self,
        keyword: str | None,
        project_type: str | None,
        target_country: str | None,
        education_level: str | None,
        limit: int,
    ) -> list[CourseProject]:
        stmt = (
            select(CourseProject)
            .where(CourseProject.status == "enabled", CourseProject.is_delete == 0)
            .order_by(CourseProject.id.desc())
            .limit(limit)
        )
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    CourseProject.project_name.like(like),
                    CourseProject.project_desc.like(like),
                    CourseProject.target_audience.like(like),
                )
            )
        if project_type:
            stmt = stmt.where(CourseProject.project_type == project_type)
        if target_country:
            stmt = stmt.where(CourseProject.target_country.like(f"%{target_country}%"))
        if education_level:
            stmt = stmt.where(CourseProject.target_education_level.like(f"%{education_level}%"))
        return list(self.db.scalars(stmt).all())

    def list_events(self, keyword: str | None, event_type: str | None, status: str | None, limit: int) -> list[EventLecture]:
        stmt = (
            select(EventLecture)
            .where(EventLecture.is_delete == 0)
            .order_by(EventLecture.start_time.asc())
            .limit(limit)
        )
        if status:
            stmt = stmt.where(EventLecture.status == status)
        if event_type:
            stmt = stmt.where(EventLecture.event_type == event_type)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    EventLecture.event_name.like(like),
                    EventLecture.topic.like(like),
                    EventLecture.speaker.like(like),
                )
            )
        return list(self.db.scalars(stmt).all())

    def get_event(self, event_id: int) -> EventLecture | None:
        stmt = select(EventLecture).where(EventLecture.id == event_id, EventLecture.is_delete == 0)
        return self.db.scalar(stmt)

    def add_registration(self, registration: EventRegistration) -> EventRegistration:
        if registration.id is None and self.db.bind and self.db.bind.dialect.name == "sqlite":
            registration.id = (self.db.scalar(select(func.max(EventRegistration.id))) or 0) + 1
        self.db.add(registration)
        self.db.flush()
        return registration

    @staticmethod
    def touch_event_after_registration(event: EventLecture) -> None:
        event.current_participants = (event.current_participants or 0) + 1
        if event.max_participants and event.current_participants >= event.max_participants:
            event.status = "full"
        event.update_time = datetime.now()

