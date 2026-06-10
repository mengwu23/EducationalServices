from pydantic import BaseModel, Field


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


def normalize_page(page: int = 1, size: int = 20) -> tuple[int, int]:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    return page, size
