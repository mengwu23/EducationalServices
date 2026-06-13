"""
学生申请进度追踪 — API 路由层（Controller）
============================================

接口前缀：/api/application-progress

学生端：
    GET  /my-progress              — 学生查看自己的申请进度列表
    GET  /my-progress/timeline     — 学生查看自己的进度时间线

通用查询：
    GET  /                          — 查询进度列表（支持多维筛选）
    GET  /{progress_id}             — 获取进度详情
    GET  /stages                    — 获取阶段/状态参考数据

管理端（员工/管理员）：
    POST /                          — 创建进度记录
    PATCH /{progress_id}            — 更新进度记录
    GET  /stats/blocked-count       — 统计受阻进度数量

CRM 集成预留：
    POST /crm/sync                  — CRM 数据同步（预留，待 CRM 合并后实现）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.common.responses import ApiResponse, error_response, success_response
from backend.app.core.security import CurrentUser, require_permissions
from backend.app.database import get_db
from backend.app.schemas.application_progress_schema import (
    CRMSyncRequest,
    ProgressCreateRequest,
    ProgressListResponse,
    ProgressTimelineResponse,
    ProgressUpdateRequest,
)
from backend.app.services.application_progress_service import ApplicationProgressService

router = APIRouter(prefix="/api/application-progress", tags=["申请进度追踪"])


# ══════════════════════════════════════════════════════════
# 学生端接口
# ══════════════════════════════════════════════════════════

@router.get("/my-progress", response_model=ApiResponse, summary="学生查看自己的申请进度")
def list_my_progress(
    progress_stage: Optional[str] = Query(default=None, description="按阶段筛选：essay/school_apply/visa/offer/other"),
    progress_status: Optional[str] = Query(default=None, description="按状态筛选：pending/processing/completed/blocked"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:own")),
):
    """学生自助查询自己的留学申请进度

    涵盖文书审核、院校申请、签证办理、录取通知等各阶段。
    学生只能查看当前登录账号关联的所有进度记录。
    """
    service = ApplicationProgressService(db)
    try:
        items, total = service.list_my_progress(
            student_user_id=current_user.id,
            page=page,
            page_size=page_size,
            progress_stage=progress_stage,
            progress_status=progress_status,
        )
        return success_response(data=ProgressListResponse(
            items=items, total=total, page=page, page_size=page_size,
        ))
    except Exception as e:
        return error_response(code=40000, message=str(e))


@router.get("/my-progress/timeline", response_model=ApiResponse, summary="学生查看自己的进度时间线")
def get_my_timeline(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:own")),
):
    """学生查看自己的申请进度时间线

    按阶段汇总最新状态，生成可视化的进度概览。
    返回各阶段的当前状态、负责人和预计完成时间。
    """
    service = ApplicationProgressService(db)
    try:
        timeline = service.get_timeline(student_user_id=current_user.id)
        return success_response(data=timeline)
    except Exception as e:
        return error_response(code=40000, message=str(e))


# ══════════════════════════════════════════════════════════
# 通用查询接口
# ══════════════════════════════════════════════════════════

@router.get("", response_model=ApiResponse, summary="查询申请进度列表")
def list_progress(
    student_id: Optional[int] = Query(default=None, description="学生ID"),
    progress_stage: Optional[str] = Query(default=None, description="进度阶段"),
    progress_status: Optional[str] = Query(default=None, description="进度状态"),
    handler_employee_id: Optional[int] = Query(default=None, description="负责人ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:read")),
):
    """多维筛选查询申请进度列表（员工/管理员用）。"""
    service = ApplicationProgressService(db)
    try:
        items, total = service.list_progress(
            student_id=student_id,
            progress_stage=progress_stage,
            progress_status=progress_status,
            handler_employee_id=handler_employee_id,
            page=page,
            page_size=page_size,
        )
        return success_response(data=ProgressListResponse(
            items=items, total=total, page=page, page_size=page_size,
        ))
    except Exception as e:
        return error_response(code=40000, message=str(e))


@router.get("/stages", response_model=ApiResponse, summary="获取阶段/状态参考数据")
def get_stages_reference():
    """返回进度阶段和状态的中英文对照参考数据。"""
    return success_response(data=ApplicationProgressService.get_stages_reference())


@router.get("/{progress_id}", response_model=ApiResponse, summary="获取进度详情")
def get_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:read")),
):
    """获取单条申请进度记录的详细信息。"""
    service = ApplicationProgressService(db)
    try:
        result = service.get_progress(progress_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(code=40000, message=str(e))


# ══════════════════════════════════════════════════════════
# 管理端接口
# ══════════════════════════════════════════════════════════

@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, summary="创建申请进度记录")
def create_progress(
    payload: ProgressCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:write")),
):
    """员工/管理员为学生创建一条申请进度记录。

    请求体：
    {
        "student_id": 1,
        "progress_stage": "essay",
        "progress_status": "processing",
        "progress_desc": "推荐信已提交，个人陈述修改中",
        "handler_employee_id": 3,
        "school_name": "Harvard University",
        "expected_finish_time": "2026-07-15T00:00:00"
    }
    """
    service = ApplicationProgressService(db)
    try:
        result = service.create_progress(payload)
        return success_response(data=result, message="申请进度创建成功")
    except Exception as e:
        return error_response(code=40000, message=str(e))


@router.patch("/{progress_id}", response_model=ApiResponse, summary="更新申请进度记录")
def update_progress(
    progress_id: int,
    payload: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:write")),
):
    """员工/管理员更新申请进度（部分更新）。"""
    service = ApplicationProgressService(db)
    try:
        result = service.update_progress(progress_id, payload)
        return success_response(data=result, message="申请进度更新成功")
    except Exception as e:
        return error_response(code=40000, message=str(e))


@router.get("/stats/blocked-count", response_model=ApiResponse, summary="统计受阻进度数量")
def get_blocked_count(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:read")),
):
    """统计当前所有处于「受阻」状态的申请进度总数。

    用于管理仪表盘展示异常进度数量。
    """
    service = ApplicationProgressService(db)
    try:
        count = service.count_blocked()
        return success_response(data={"blocked_count": count})
    except Exception as e:
        return error_response(code=40000, message=str(e))


# ══════════════════════════════════════════════════════════
# CRM 集成预留（待 CRM 系统合并后实现）
# ══════════════════════════════════════════════════════════

@router.post("/crm/sync", response_model=ApiResponse, summary="[预留] CRM数据同步")
def crm_sync(
    payload: CRMSyncRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("application_progress:write")),
):
    """CRM 数据同步接口（预留）。

    当前 CRM 系统尚未合并，此接口返回 501 Not Implemented。
    后续接入 CRM 后：
    - sync_direction='to_local'：从 CRM 拉取进度数据到本地
    - sync_direction='to_crm'：将本地进度数据推送到 CRM
    """
    service = ApplicationProgressService(db)
    try:
        if payload.sync_direction == "to_local":
            result = service.sync_from_crm(
                crm_system=payload.crm_system,
                crm_record_id=payload.crm_record_id,
                student_id=payload.student_id,
                progress_stage=payload.progress_stage,
                progress_status=payload.progress_status,
                progress_desc=payload.progress_desc,
            )
        elif payload.sync_direction == "to_crm":
            result = service.sync_to_crm(
                progress_id=payload.progress_id,
                crm_system=payload.crm_system,
                crm_record_id=payload.crm_record_id,
            )
        else:
            raise ValueError("sync_direction must be to_local or to_crm")
        return success_response(data=result, message="同步完成")
    except NotImplementedError as e:
        return error_response(code=50100, message=str(e))
    except Exception as e:
        return error_response(code=40000, message=str(e))
