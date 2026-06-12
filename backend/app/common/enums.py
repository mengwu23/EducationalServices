from enum import Enum


class StrEnum(str, Enum):
    """Python 3.10 compatible replacement for enum.StrEnum."""

    def __str__(self) -> str:
        return self.value


class Role(StrEnum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    STUDENT = "student"
    VISITOR = "visitor"


class ReportType(StrEnum):
    COMPLAINT_WEEKLY = "complaint_weekly"
    CUSTOMER_OPERATION = "customer_operation"
    EMPLOYEE_DAILY_SUMMARY = "employee_daily_summary"
    EMPLOYEE_WEEKLY_SUMMARY = "employee_weekly_summary"
    STUDENT_PSYCH_WEEKLY = "student_psych_weekly"


class DraftStatus(StrEnum):
    GENERATING = "generating"
    PENDING_CONFIRM = "pending_confirm"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    GENERATION_FAILED = "generation_failed"
    PENDING_SECOND_CONFIRM = "pending_second_confirm"


class ReportStatus(StrEnum):
    CONFIRMED = "confirmed"
    PUBLISHED = "published"


class ExportType(StrEnum):
    WORD = "word"
    PDF = "pdf"


class ExportStatus(StrEnum):
    SUCCESS = "success"
    FAIL = "fail"


class AcademicEventType(StrEnum):
    PAPER_DEADLINE = "paper_deadline"
    EXAM = "exam"
    COURSE_DEADLINE = "course_deadline"
    OTHER = "other"


class AcademicEventStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PsychAlertStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"


class PsychRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserType(StrEnum):
    STUDENT = "student"
    EMPLOYEE = "employee"
    ADMIN = "admin"


class LeaveStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(StrEnum):
    SICK = "sick"
    PERSONAL = "personal"
    OTHER = "other"


class FeedbackPriorityLevel(StrEnum):
    NORMAL = "normal"
    URGENT = "urgent"
    SEVERE = "severe"


class FeedbackTicketType(StrEnum):
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    CONSULT = "consult"


class FeedbackTicketStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"
