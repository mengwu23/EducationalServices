from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.common.enums import FeedbackTicketStatus
from backend.app.common.exceptions import BadRequestError, ConflictError, NotFoundError
from backend.app.common.pagination import normalize_page
from backend.app.daos.student_feedback_ticket_dao import StudentFeedbackTicketDAO
from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
from backend.app.schemas.student_feedback_ticket_schema import (
    FeedbackAssignRequest,
    FeedbackCloseRequest,
    FeedbackResolveRequest,
    StudentFeedbackTicketCreate,
    StudentFeedbackTicketUpdate,
)


class StudentFeedbackTicketService:
    @staticmethod
    def _generate_ticket_no() -> str:
        return f"FB{datetime.now().strftime('%Y%m%d')}{uuid4().hex[:8].upper()}"

    @staticmethod
    def _get_or_raise(db: Session, ticket_id: int) -> StudentFeedbackTicket:
        ticket = StudentFeedbackTicketDAO.get_by_id(db, ticket_id)
        if ticket is None:
            raise NotFoundError("Student feedback ticket not found")
        return ticket

    @classmethod
    def create_ticket(cls, db: Session, payload: StudentFeedbackTicketCreate) -> StudentFeedbackTicket:
        data = payload.dict()
        data["ticket_type"] = payload.ticket_type.value
        data["priority_level"] = payload.priority_level.value
        data["status"] = FeedbackTicketStatus.PENDING.value
        data["ticket_no"] = data.get("ticket_no") or cls._generate_ticket_no()

        if StudentFeedbackTicketDAO.get_by_ticket_no(db, data["ticket_no"]):
            raise ConflictError("Ticket number already exists")

        try:
            return StudentFeedbackTicketDAO.create(db, data)
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError("Failed to create feedback ticket") from exc

    @staticmethod
    def list_tickets(
        db: Session,
        *,
        student_id: int | None = None,
        status: str | None = None,
        handler_employee_id: int | None = None,
        category: str | None = None,
        priority_level: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[StudentFeedbackTicket], int, int, int]:
        page, size = normalize_page(page, size)
        items, total = StudentFeedbackTicketDAO.list(
            db,
            student_id=student_id,
            status=status,
            handler_employee_id=handler_employee_id,
            category=category,
            priority_level=priority_level,
            keyword=keyword,
            page=page,
            size=size,
        )
        return items, total, page, size

    @classmethod
    def get_ticket(cls, db: Session, ticket_id: int) -> StudentFeedbackTicket:
        return cls._get_or_raise(db, ticket_id)

    @classmethod
    def update_ticket(
        cls,
        db: Session,
        ticket_id: int,
        payload: StudentFeedbackTicketUpdate,
    ) -> StudentFeedbackTicket:
        ticket = cls._get_or_raise(db, ticket_id)
        data = payload.dict(exclude_unset=True)
        for enum_key in ("ticket_type", "priority_level", "status"):
            if enum_key in data and data[enum_key] is not None:
                data[enum_key] = data[enum_key].value
        if data.get("status") == FeedbackTicketStatus.CLOSED.value and ticket.close_time is None:
            data["close_time"] = datetime.now()
        return StudentFeedbackTicketDAO.update(db, ticket, data)

    @classmethod
    def assign_ticket(
        cls,
        db: Session,
        ticket_id: int,
        payload: FeedbackAssignRequest,
    ) -> StudentFeedbackTicket:
        ticket = cls._get_or_raise(db, ticket_id)
        if ticket.status == FeedbackTicketStatus.CLOSED.value:
            raise BadRequestError("Closed feedback tickets cannot be assigned")
        return StudentFeedbackTicketDAO.update(
            db,
            ticket,
            {
                "handler_employee_id": payload.handler_employee_id,
                "status": FeedbackTicketStatus.PROCESSING.value,
            },
        )

    @classmethod
    def resolve_ticket(
        cls,
        db: Session,
        ticket_id: int,
        payload: FeedbackResolveRequest,
    ) -> StudentFeedbackTicket:
        ticket = cls._get_or_raise(db, ticket_id)
        if ticket.status == FeedbackTicketStatus.CLOSED.value:
            raise BadRequestError("Closed feedback tickets cannot be resolved again")
        return StudentFeedbackTicketDAO.update(
            db,
            ticket,
            {
                "solution": payload.solution,
                "status": FeedbackTicketStatus.RESOLVED.value,
                "is_notified": 1 if payload.notify_student else ticket.is_notified,
            },
        )

    @classmethod
    def notify_ticket(cls, db: Session, ticket_id: int) -> StudentFeedbackTicket:
        """标记工单已通知学生

        老师在解决工单后调用此方法，向学生同步"您的xxx投诉已解决"通知。
        设置 is_notified=1 标记已通知。

        Args:
            db: 数据库会话
            ticket_id: 工单 ID

        Returns:
            更新后的工单对象

        Raises:
            NotFoundError: 工单不存在
            BadRequestError: 工单状态不允许通知（仅 resolved/closed 可通知）
        """
        ticket = cls._get_or_raise(db, ticket_id)
        if ticket.status not in (FeedbackTicketStatus.RESOLVED.value, FeedbackTicketStatus.CLOSED.value):
            raise BadRequestError("Only resolved or closed feedback tickets can be notified to student")
        return StudentFeedbackTicketDAO.update(db, ticket, {"is_notified": 1})

    @classmethod
    def close_ticket(
        cls,
        db: Session,
        ticket_id: int,
        payload: FeedbackCloseRequest,
    ) -> StudentFeedbackTicket:
        ticket = cls._get_or_raise(db, ticket_id)
        if ticket.status != FeedbackTicketStatus.RESOLVED.value:
            raise BadRequestError("Only resolved feedback tickets can be closed")
        data = {
            "status": FeedbackTicketStatus.CLOSED.value,
            "close_time": datetime.now(),
        }
        if payload.satisfaction_score is not None:
            data["satisfaction_score"] = payload.satisfaction_score
        return StudentFeedbackTicketDAO.update(db, ticket, data)
