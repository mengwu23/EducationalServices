from fastapi import HTTPException, status


class AppException(Exception):
    def __init__(self, code: int, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class NotFoundException(AppException):
    def __init__(self, message: str = "请求的资源不存在", code: int = 40400):
        super().__init__(code=code, message=message, status_code=404)


class PermissionDeniedException(AppException):
    def __init__(self, message: str = "权限不足", code: int = 40300):
        super().__init__(code=code, message=message, status_code=403)


class StateConflictException(AppException):
    def __init__(self, message: str = "当前状态不允许此操作", code: int = 40900):
        super().__init__(code=code, message=message, status_code=409)


class ValidationErrorException(AppException):
    def __init__(self, message: str = "参数校验失败", code: int = 42200):
        super().__init__(code=code, message=message, status_code=422)


class NotFoundError(HTTPException):
    def __init__(self, message: str = "Resource not found", detail: str | None = None) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail or message)


class BadRequestError(HTTPException):
    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class ConflictError(HTTPException):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class BusinessError(HTTPException):
    def __init__(self, detail: str, code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=code, detail=detail)


class ReportGenerationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
