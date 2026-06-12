"""
心理关怀模块 — API 路由层（Controller）
==========================================

定义心理关怀模块的所有 RESTful 接口。

接口前缀：/api/v1/student-assistant/psych

路由列表：
    GET    /psych/profile                   — 学生查看自己的心理画像
    PATCH  /psych/profile/emotion           — 更新情绪状态（AI预留接口）
    GET    /psych/profiles                  — 员工查看所有学生心理画像
    GET    /psych/alerts                    — 学生查看自己的预警记录
    POST   /psych/alerts                    — 创建预警（AI/人工共用）
    GET    /psych/alerts/pending            — 员工查看待处理预警
    GET    /psych/alerts/pending/count      — 统计待处理预警数量
    GET    /psych/alerts/history            — 员工查看自己的处理历史
    POST   /psych/alerts/{alert_id}/action  — 处理预警（process/resolve/close）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.common.exceptions import AppException
from backend.app.common.pagination import PageQuery
from backend.app.common.responses import ApiResponse, error_response, success_response
from backend.app.core.security import require_permissions
from backend.app.database import get_db
from backend.app.schemas.student_psych_schema import (
    EmotionCheckinRequest,
    PsychAlertActionRequest,
    PsychAlertCreateRequest,
    PsychAlertListQuery,
    PsychProfileListQuery,
)
from backend.app.services.student_psych_service import StudentPsychService

# 创建路由
router = APIRouter(
    prefix="/api/v1/student-assistant/psych",
    tags=["心理关怀"],
)


# ============================================================
# 当前用户依赖（复用占位实现）
# ============================================================
# TODO: 接入正式 JWT 鉴权后，替换为 core/security.py 中的 get_current_user

from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    """当前登录用户信息"""
    user_id: int = Field(..., description="用户ID（sys_user.id）")
    user_type: str = Field(..., description="用户角色：student=学生 / employee=员工 / admin=管理员")


def get_current_user(
    user_id: Optional[int] = Query(default=None, description="用户ID（sys_user.id），如 11=李娜, 1=陈远"),
    user_type: Optional[str] = Query(default=None, description="用户角色：传 student 测试学生功能，传 employee 测试员工功能"),
) -> CurrentUser:
    """获取当前登录用户（开发测试用）"""
    return CurrentUser(
        user_id=user_id or 1,
        user_type=user_type or "student",
    )


# ============================================================
# 接口定义
# ============================================================
# 注意：静态路由必须在参数化路由之前定义

# ----------------------------------------------------------
# GET /psych/profile — 学生查看自己的心理画像
# ----------------------------------------------------------

@router.get("/profile", response_model=ApiResponse, summary="查看自己的心理画像")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """学生查看自己的心理状态画像

    返回当前学生的情绪标签、情绪分数、风险等级和情绪摘要。
    每人只有一条心理画像记录。
    """
    try:
        service = StudentPsychService(db)
        result = service.get_my_profile(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
        )
        return success_response(data=result)
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# ----------------------------------------------------------
# POST /psych/profile/checkin — 学生情绪打卡（AI 识别）
# ----------------------------------------------------------

@router.post("/profile/checkin", response_model=ApiResponse, summary="学生情绪打卡（AI 识别情绪）")
def emotion_checkin(
    data: EmotionCheckinRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """学生提交情绪打卡文本，由 AI 识别情绪标签、分值和摘要并更新心理画像。

    学生输入一段自我情绪描述，系统调用 DeepSeek 识别情绪状态
    （含焦虑/孤独/文化冲突等留学场景标签），自动更新本人心理画像。
    需配置 LLM API Key，否则返回服务未就绪提示。
    """
    try:
        service = StudentPsychService(db)
        result = service.emotion_checkin(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            content=data.content,
        )
        return success_response(data=result, message="情绪打卡完成")
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# GET /psych/profiles — 员工查看所有学生心理画像
# ----------------------------------------------------------

@router.get("/profiles", response_model=ApiResponse, summary="查看所有学生心理画像（员工端）")
def list_all_profiles(
    query: PsychProfileListQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:read")),
):
    """员工查看所有学生的心理画像列表

    支持按风险等级筛选（low / medium / high / critical）。
    用于掌握整体学生心理状态分布。
    """
    try:
        service = StudentPsychService(db)
        items, total = service.list_all_profiles(
            current_user_type=current_user.user_type,
            query=query,
        )

        data = {
            "items": items,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": (total + query.page_size - 1) // query.page_size if total > 0 else 0,
        }
        return success_response(data=data)
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# GET /psych/alerts — 学生查看自己的预警记录
# ----------------------------------------------------------

@router.get("/alerts", response_model=ApiResponse, summary="查看自己的预警记录（学生端）")
def list_my_alerts(
    query: PsychAlertListQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:own")),
):
    """学生查看自己的心理预警记录

    支持按状态筛选（pending / processing / resolved / closed）。
    可查看预警触发原因、风险等级、处理进度等信息。
    """
    try:
        service = StudentPsychService(db)
        items, total = service.list_my_alerts(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            query=query,
        )

        data = {
            "items": items,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": (total + query.page_size - 1) // query.page_size if total > 0 else 0,
        }
        return success_response(data=data)
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# POST /psych/alerts — 创建预警（AI/人工共用）
# ----------------------------------------------------------

@router.post("/alerts", response_model=ApiResponse, summary="创建预警（AI/人工共用）")
def create_alert(
    data: PsychAlertCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:manage")),
):
    """创建心理预警

    人工或 AI 检测到高风险时调用此接口。
    后续 Dify 聊天时发现 high/critical 风险，自动调用此接口创建预警。

    请求体：
    {
        "student_id": 1,
        "trigger_reason": "学生表达出强烈焦虑和自暴自弃倾向",
        "risk_level": "high"
    }
    """
    try:
        service = StudentPsychService(db)
        result = service.create_alert(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            data=data,
        )
        return success_response(data=result, message="预警已创建")
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# GET /psych/alerts/pending — 员工查看待处理预警
# ----------------------------------------------------------
# 注意：此路由必须在 /alerts/{alert_id} 之前定义

@router.get("/alerts/pending", response_model=ApiResponse, summary="查看待处理预警（员工端）")
def list_pending_alerts(
    query: PageQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:read")),
):
    """员工查看所有待处理和跟进中的预警

    包含 status=pending（未处理）和 status=processing（跟进中）的记录。
    按创建时间倒序排列，最新的预警排最前。
    """
    try:
        service = StudentPsychService(db)
        items, total = service.list_pending_alerts(
            current_user_type=current_user.user_type,
            query=query,
        )

        data = {
            "items": items,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": (total + query.page_size - 1) // query.page_size if total > 0 else 0,
        }
        return success_response(data=data)
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# GET /psych/alerts/pending/count — 统计待处理预警数量
# ----------------------------------------------------------

@router.get("/alerts/pending/count", response_model=ApiResponse, summary="统计待处理预警数量")
def count_pending_alerts(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:read")),
):
    """统计当前待处理和跟进中的预警总数

    用于员工首页右上角徽标或"待处理"卡片展示。
    """
    try:
        service = StudentPsychService(db)
        count = service.count_pending_alerts(
            current_user_type=current_user.user_type,
        )
        return success_response(data={"count": count})
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# GET /psych/alerts/history — 员工查看自己的处理历史
# ----------------------------------------------------------

@router.get("/alerts/history", response_model=ApiResponse, summary="查看自己的预警处理历史（员工端）")
def list_processed_alerts(
    query: PageQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:read")),
):
    """员工查看自己处理过的预警历史

    包括自己跟进中、已解除、已关闭的所有预警。
    """
    try:
        service = StudentPsychService(db)
        items, total = service.list_processed_alerts(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            query=query,
        )

        data = {
            "items": items,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": (total + query.page_size - 1) // query.page_size if total > 0 else 0,
        }
        return success_response(data=data)
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# POST /psych/alerts/{alert_id}/action — 处理预警
# ----------------------------------------------------------

@router.post("/alerts/{alert_id}/action", response_model=ApiResponse, summary="处理预警（跟进/解除/关闭）")
def handle_alert(
    alert_id: int,
    data: PsychAlertActionRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_psych:manage")),
):
    """处理心理预警

    支持三个动作：
        process — 开始跟进，标记当前员工为处理人，状态→processing
        resolve — 解除预警，需填写处理结果，状态→resolved
        close   — 关闭预警，记录关闭时间，状态→closed

    请求体：
    {
        "action": "resolve",
        "handle_result": "已安排心理老师进行两次疏导，学生情绪明显好转"
    }

    状态流转：
        pending → process → processing
        processing → resolve → resolved
        resolved → close → closed
    """
    try:
        service = StudentPsychService(db)

        # 根据 action 分发到不同的处理方法
        if data.action == "process":
            result = service.process_alert(
                current_user_id=current_user.user_id,
                current_user_type=current_user.user_type,
                alert_id=alert_id,
            )
            return success_response(data=result, message="已开始跟进")

        elif data.action == "resolve":
            result = service.resolve_alert(
                current_user_id=current_user.user_id,
                current_user_type=current_user.user_type,
                alert_id=alert_id,
                handle_result=data.handle_result,
            )
            return success_response(data=result, message="预警已解除")

        elif data.action == "close":
            result = service.close_alert(
                current_user_id=current_user.user_id,
                current_user_type=current_user.user_type,
                alert_id=alert_id,
            )
            return success_response(data=result, message="预警已关闭")

        else:
            return error_response(
                code=42200,
                message=f"不支持的动作：{data.action}，仅支持 process / resolve / close",
            )

    except AppException as e:
        return error_response(code=e.code, message=e.message)
