import uuid
from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
    trace_id: str = ""


def success_response(data: Any = None, message: str = "success") -> ApiResponse:
    return ApiResponse(
        code=0,
        message=message,
        data=data,
        trace_id=_generate_trace_id(),
    )


def error_response(code: int, message: str, data: Any = None) -> ApiResponse:
    return ApiResponse(
        code=code,
        message=message,
        data=data,
        trace_id=_generate_trace_id(),
    )


def success(data: Any = None, message: str = "success", trace_id: str | None = None) -> dict[str, Any]:
    return {
        "code": 0,
        "message": message,
        "data": data,
        "trace_id": trace_id or _generate_trace_id(),
    }


def _generate_trace_id() -> str:
    return uuid.uuid4().hex
