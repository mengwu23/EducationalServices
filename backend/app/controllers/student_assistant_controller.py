"""学生智能助手 — 公共 API 路由。"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.student_assistant_schema import LifeFaqResult
from backend.app.services.student_assistant_service import StudentAssistantService

router = APIRouter(
    prefix="/api/v1/student-assistant",
    tags=["学生智能助手"],
)


@router.get("/life-support/faq", response_model=LifeFaqResult, summary="搜索本地生活知识库")
def search_life_faq(
    keyword: str = Query(..., min_length=1), limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """本地 FAQ 知识库搜索。"""
    return StudentAssistantService.search_life_faq(db, keyword, limit)


@router.post("/life-support/chat", summary="生活助手 AI 对话")
def chat_life_assistant(query: str = Query(..., min_length=1)):
    """Dify 生活支持助手。"""
    result = StudentAssistantService.ask_life_assistant(query)
    return {"answer": result["answer"], "conversation_id": result["conversation_id"]}


@router.post("/policy/chat", summary="留学政策 AI 咨询")
def chat_policy_assistant(query: str = Query(..., min_length=1)):
    """Dify 留学政策助手。"""
    result = StudentAssistantService.ask_policy_assistant(query)
    return {"answer": result["answer"], "conversation_id": result["conversation_id"]}


class PsychChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: int = Field(...)


@router.post("/psych/chat", summary="心理关怀 AI 对话")
def chat_psych(payload: PsychChatRequest, db: Session = Depends(get_db)):
    """DeepSeek 心理关怀对话。每次更新画像，高危自动预警。"""
    return StudentAssistantService.chat_psych(db, payload.message, payload.user_id)
