"""
统一响应格式模块（仅请假审批模块所需）
========================================

定义系统统一的 API 响应结构，所有接口返回值都遵循此格式：

成功响应：
    {
        "code": 0,
        "message": "success",
        "data": { ... },
        "trace_id": "a1b2c3d4e5f6"
    }

错误响应：
    {
        "code": 40401,
        "message": "请假申请不存在",
        "data": null,
        "trace_id": "a1b2c3d4e5f6"
    }
"""

import uuid
from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一 API 响应模型

    所有接口（包括正常返回和异常返回）都使用此模型序列化。
    通过 response_model=ApiResponse 在路由装饰器中声明。

    Attributes:
        code: 业务状态码，0 表示成功，非 0 表示具体错误类型
        message: 提示信息，成功时为 "success"，失败时为具体错误描述
        data: 实际业务数据，可为任意 JSON 可序列化类型
        trace_id: 请求链路追踪 ID，用于日志串联和问题排查
    """
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
    trace_id: str = ""


def success_response(data: Any = None, message: str = "success") -> ApiResponse:
    """生成成功响应

    使用示例：
        return success_response(leave_data)
        return success_response({"id": 1, "status": "pending"}, "请假提交成功")
        return success_response()  # 仅返回 code=0, message="success"

    Args:
        data: 业务数据，可为 dict、list、Pydantic 模型等
        message: 成功提示，默认为 "success"

    Returns:
        统一格式的成功响应
    """
    return ApiResponse(
        code=0,
        message=message,
        data=data,
        trace_id=_generate_trace_id(),
    )


def error_response(code: int, message: str, data: Any = None) -> ApiResponse:
    """生成错误响应

    使用示例：
        return error_response(40400, "请假申请不存在")
        return error_response(40300, "只有学生才能提交请假")

    Args:
        code: 业务错误码（非 0），与 exceptions 模块中的 code 对应
        message: 错误描述
        data: 可选的附加错误数据

    Returns:
        统一格式的错误响应
    """
    return ApiResponse(
        code=code,
        message=message,
        data=data,
        trace_id=_generate_trace_id(),
    )


def _generate_trace_id() -> str:
    """生成请求链路追踪 ID

    使用 UUID 的十六进制紧凑格式，比带连字符的标准格式更短。
    示例输出：a1b2c3d4e5f6789012345678abcdef01
    """
    return uuid.uuid4().hex
