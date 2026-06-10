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


class LeaveType(str, Enum):
    SICK = "sick"
    PERSONAL = "personal"
    OTHER = "other"


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class UserType(str, Enum):
    EMPLOYEE = "employee"
    STUDENT = "student"
    CUSTOMER = "customer"
    ADMIN = "admin"


class PsychRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PsychAlertStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Role(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    STUDENT = "student"
    VISITOR = "visitor"


class ReportType(str, Enum):
    COMPLAINT_WEEKLY = "complaint_weekly"
    CUSTOMER_OPERATION = "customer_operation"


class DraftStatus(str, Enum):
    GENERATING = "generating"
    PENDING_CONFIRM = "pending_confirm"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    GENERATION_FAILED = "generation_failed"
    PENDING_SECOND_CONFIRM = "pending_second_confirm"


class ReportStatus(str, Enum):
    CONFIRMED = "confirmed"
    PUBLISHED = "published"


class ExportType(str, Enum):
    WORD = "word"
    PDF = "pdf"


class ExportStatus(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"
