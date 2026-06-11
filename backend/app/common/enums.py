from enum import Enum


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
