from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class BadRequestError(HTTPException):
    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class ConflictError(HTTPException):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)
