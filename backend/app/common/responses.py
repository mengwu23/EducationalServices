from typing import Any


def success(data: Any = None, message: str = "success", trace_id: str | None = None) -> dict[str, Any]:
    return {
        "code": 0,
        "message": message,
        "data": data,
        "trace_id": trace_id,
    }
