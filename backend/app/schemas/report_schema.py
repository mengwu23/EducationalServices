from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.common.enums import ExportType, ReportType


class ReportGenerateDraftRequest(BaseModel):
    report_type: ReportType
    date_start: date
    date_end: date
    department_id: int | None = None
    owner_user_id: int | None = None
    trace_id: str | None = None


class ReportSection(BaseModel):
    heading: str
    content: str
    metrics: list[dict[str, Any]] = Field(default_factory=list)


class ReportContent(BaseModel):
    title: str
    summary: str
    sections: list[ReportSection] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class ReportDraftResponse(BaseModel):
    id: int
    draft_no: str
    status: str
    content_json: dict[str, Any]
    trace_id: str | None = None


class ReportRejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class ReportResponse(BaseModel):
    id: int
    report_no: str
    report_type: str
    title: str
    status: str
    content_json: dict[str, Any]
    source_draft_id: int
    date_start: date
    date_end: date
    department_id: int | None
    created_by: int | None
    published_by: int | None
    published_time: datetime | None


class ReportExportRequest(BaseModel):
    export_type: ExportType


class ReportExportResponse(BaseModel):
    id: int
    report_id: int
    export_type: str
    file_name: str
    file_path: str
    status: str
    error_message: str | None


class AiToolReportSourceDataRequest(BaseModel):
    report_type: ReportType
    date_start: date
    date_end: date
    department_id: int | None = None
    owner_user_id: int | None = None
    conversation_id: str | None = None
    trace_id: str | None = None
    caller: Literal["dify", "other"] = "dify"

    @field_validator("department_id", "owner_user_id", mode="before")
    @classmethod
    def blank_optional_int_to_none(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and value.strip().lower() in {"", "null", "none"}:
            return None
        return value
