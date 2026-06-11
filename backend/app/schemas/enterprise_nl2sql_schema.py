"""企业管理 NL2SQL 响应结构。"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class EnterpriseNl2SqlQueryResult(BaseModel):
    """自然语言问数响应。"""

    query: str
    sql: Optional[str] = None
    columns: List[str] = Field(default_factory=list)
    rows: List[List[Any]] = Field(default_factory=list)
    row_count: int = 0
    cost_ms: int = 0
    is_cached: bool = False
