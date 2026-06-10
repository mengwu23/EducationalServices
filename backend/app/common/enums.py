from enum import Enum


class AcademicEventType(str, Enum):
    PAPER_DEADLINE = "paper_deadline"
    EXAM = "exam"
    COURSE_DEADLINE = "course_deadline"
    OTHER = "other"


class AcademicEventStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FeedbackTicketType(str, Enum):
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    CONSULT = "consult"


class FeedbackPriorityLevel(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    SEVERE = "severe"


class FeedbackTicketStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"
