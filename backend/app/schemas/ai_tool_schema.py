from typing import Any, Dict

from pydantic import BaseModel, Field


class AiToolInvokeRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict)


class AiToolInvokeResponse(BaseModel):
    tool_name: str
    result: Any
