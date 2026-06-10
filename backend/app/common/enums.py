from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    STUDENT = "student"
    VISITOR = "visitor"


class ReportType(StrEnum):
    COMPLAINT_WEEKLY = "complaint_weekly"
    CUSTOMER_OPERATION = "customer_operation"


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
