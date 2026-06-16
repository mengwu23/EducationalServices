"""学生智能助手 — 公共 API 路由。"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from backend.app.core.security import CurrentUser, require_permissions
from backend.app.database import get_db
from backend.app.models.draft import AiDraft
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


class PsychDraftConfirmRequest(BaseModel):
    pass


class PsychDraftRejectRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500, description="驳回原因（可选）")


@router.post("/psych/chat", summary="心理关怀 AI 对话")
def chat_psych(
    payload: PsychChatRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """DeepSeek 心理关怀对话。

    生成 AI 情绪分析草稿（存入 ai_draft 表），学生确认后才写入心理画像。
    符合 PRD "所有 AI 输出先草稿确认" 的要求。
    """
    return StudentAssistantService.chat_psych(db, payload.message, current_user.id)


@router.get("/psych/drafts", summary="查询心理对话历史")
def list_psych_drafts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """查询当前学生的心理对话草稿历史（分页）。

    复用 ai_draft 表，按 biz_module="student_psych" + created_by 过滤。
    """
    q = db.query(AiDraft).filter(
        AiDraft.biz_module == "student_psych",
        AiDraft.created_by == current_user.id,
        AiDraft.is_deleted == False,
    )
    total = q.count()
    drafts = q.order_by(desc(AiDraft.create_time)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for d in drafts:
        c = d.content_json or {}
        items.append({
            "id": d.id,
            "draft_no": d.draft_no,
            "user_message": c.get("user_message", ""),
            "ai_reply": c.get("reply", c.get("ai_reply", "")),
            "emotion_tag": c.get("emotion_tag"),
            "emotion_score": c.get("emotion_score"),
            "risk_level": c.get("risk_level"),
            "confidence": c.get("confidence"),
            "status": d.status,
            "confirmed_time": d.confirmed_time.isoformat() if d.confirmed_time else None,
            "reject_reason": d.reject_reason,
            "create_time": d.create_time.isoformat() if d.create_time else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/psych/drafts/{draft_id}/confirm", summary="确认心理情绪记录")
def confirm_psych_draft(
    draft_id: int,
    payload: PsychDraftConfirmRequest = PsychDraftConfirmRequest(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """学生确认 AI 情绪分析结果，确认后写入心理画像。

    只有待确认状态的草稿才能确认。
    """
    try:
        return StudentAssistantService.confirm_psych_draft(db, draft_id, current_user.id)
    except ValueError as exc:
        from backend.app.common.exceptions import StateConflictException
        raise StateConflictException(str(exc))


@router.post("/psych/drafts/{draft_id}/reject", summary="驳回心理情绪记录")
def reject_psych_draft(
    draft_id: int,
    payload: PsychDraftRejectRequest = PsychDraftRejectRequest(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """学生驳回 AI 情绪分析结果，驳回后不更新心理画像。

    只有待确认状态的草稿才能驳回。
    """
    try:
        return StudentAssistantService.reject_psych_draft(
            db, draft_id, current_user.id, reason=payload.reason,
        )
    except ValueError as exc:
        from backend.app.common.exceptions import StateConflictException
        raise StateConflictException(str(exc))
