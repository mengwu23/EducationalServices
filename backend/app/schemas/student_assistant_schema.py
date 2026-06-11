"""学生智能助手 — 公共 Schema。"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class LifeFaqItem(BaseModel):
    id: int
    category: Optional[str] = None
    question: str
    answer: str
    model_config = ConfigDict(from_attributes=True)


class LifeFaqResult(BaseModel):
    items: List[LifeFaqItem]
    keyword: str
    total: int
