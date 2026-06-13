"""
分页模型模块（仅请假审批模块所需）
====================================

定义分页查询的请求参数和响应结构。
Controller 中使用 PageQuery 作为 Query 参数，
Service 返回查询结果后，用 PageResponse 包装返回给前端。
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

# 泛型变量 T，表示分页数据中单个元素的类型
T = TypeVar("T")


def normalize_page(page: int = 1, size: int = 20) -> tuple[int, int]:
    page = max(page or 1, 1)
    size = min(max(size or 20, 1), 100)
    return page, size


class PageQuery(BaseModel):
    """分页查询参数

    作为 FastAPI Query 参数注入到 GET 请求中。
    前端无需传 page_size 时可省略，使用默认值 20。

    使用示例：
        @router.get("/leaves")
        def list_leaves(query: PageQuery = Depends()):
            ...
    """
    page: int = Field(default=1, ge=1, description="当前页码，从 1 开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数，取值范围 1-100")


class PageResponse(BaseModel):
    """分页响应模型

    泛型模型，T 为列表中元素的具体类型。
    使用时需指定具体类型，例如：PageResponse[LeaveResponse]

    使用示例：
        return PageResponse[LeaveResponse](
            items=leave_list,
            total=100,
            page=1,
            page_size=20,
        )
    """
    items: List[T] = Field(default_factory=list, description="当前页的数据列表")
    total: int = Field(..., ge=0, description="符合条件的数据总数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, description="每页条数")

    @property
    def total_pages(self) -> int:
        """计算总页数

        根据 total 和 page_size 自动计算。
        不需要额外存储，按需计算即可。
        """
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size
