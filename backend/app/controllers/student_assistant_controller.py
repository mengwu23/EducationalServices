"""学生智能助手 — 公共 API 路由。"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.core.security import CurrentUser, require_permissions
from backend.app.database import get_db
from backend.app.models.faq_qa import FaqQa
from backend.app.services.student_assistant_service import StudentAssistantService

router = APIRouter(
    prefix="/api/v1/student-assistant",
    tags=["学生智能助手"],
)


@router.get("/life-support/faq", summary="生活支持 FAQ 查询")
def list_life_support_faq(
    keyword: str | None = Query(default=None, description="关键词，匹配问题、答案或关键词字段"),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """查询学生助手可用的生活支持 FAQ。"""
    query = db.query(FaqQa).filter(
        FaqQa.module_scope.in_(("student_assistant", "common")),
        FaqQa.status == "enabled",
        FaqQa.is_delete == 0,
    )
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                FaqQa.question.like(pattern),
                FaqQa.answer.like(pattern),
                FaqQa.keywords.like(pattern),
            )
        )

    rows = query.order_by(FaqQa.sort_order.asc(), FaqQa.id.desc()).limit(limit).all()
    return {
        "items": [
            {
                "id": row.id,
                "category": row.category,
                "question": row.question,
                "answer": row.answer,
                "keywords": row.keywords,
            }
            for row in rows
        ],
        "keyword": keyword,
        "total": len(rows),
    }


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
    user_id: int | None = Field(default=None, description="兼容旧前端字段，实际以 JWT 当前用户为准")


@router.post("/psych/chat", summary="心理关怀 AI 对话")
def chat_psych(
    payload: PsychChatRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """DeepSeek 心理关怀对话。每次更新画像，高危自动预警。"""
    return StudentAssistantService.chat_psych(db, payload.message, current_user.id)
