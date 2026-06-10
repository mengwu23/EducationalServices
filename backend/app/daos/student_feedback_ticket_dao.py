from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.student_feedback_ticket import StudentFeedbackTicket


class StudentFeedbackTicketDAO:
    @staticmethod
    def create(db: Session, data: dict) -> StudentFeedbackTicket:
        ticket = StudentFeedbackTicket(**data)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_by_id(db: Session, ticket_id: int) -> Optional[StudentFeedbackTicket]:
        return db.query(StudentFeedbackTicket).filter(StudentFeedbackTicket.id == ticket_id).first()

    @staticmethod
    def get_by_ticket_no(db: Session, ticket_no: str) -> Optional[StudentFeedbackTicket]:
        return db.query(StudentFeedbackTicket).filter(StudentFeedbackTicket.ticket_no == ticket_no).first()

    @staticmethod
    def list(
        db: Session,
        *,
        student_id: Optional[int] = None,
        status: Optional[str] = None,
        handler_employee_id: Optional[int] = None,
        category: Optional[str] = None,
        priority_level: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[StudentFeedbackTicket], int]:
        query = db.query(StudentFeedbackTicket)
        if student_id is not None:
            query = query.filter(StudentFeedbackTicket.student_id == student_id)
        if status:
            query = query.filter(StudentFeedbackTicket.status == status)
        if handler_employee_id is not None:
            query = query.filter(StudentFeedbackTicket.handler_employee_id == handler_employee_id)
        if category:
            query = query.filter(StudentFeedbackTicket.category == category)
        if priority_level:
            query = query.filter(StudentFeedbackTicket.priority_level == priority_level)
        if keyword:
            like_value = f"%{keyword}%"
            query = query.filter(StudentFeedbackTicket.title.like(like_value))

        total = query.count()
        items = (
            query.order_by(StudentFeedbackTicket.create_time.desc(), StudentFeedbackTicket.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return items, total

    @staticmethod
    def update(db: Session, ticket: StudentFeedbackTicket, data: dict) -> StudentFeedbackTicket:
        for key, value in data.items():
            setattr(ticket, key, value)
        db.commit()
        db.refresh(ticket)
        return ticket
