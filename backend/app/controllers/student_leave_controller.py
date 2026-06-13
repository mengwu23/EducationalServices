"""
请假审批模块 — API 路由层（Controller）
==========================================

定义请假审批模块的所有 RESTful 接口。

接口前缀：/api/v1/student-assistant/leaves

路由列表：
    POST   /leaves                     — 学生提交请假
    GET    /leaves                     — 学生查自己的请假列表
    GET    /leaves/pending             — 员工查所有待审批列表
    GET    /leaves/pending/count       — 统计待审批数量（员工首页角标用）
    GET    /leaves/history             — 员工查自己的审批历史
    GET    /leaves/{leave_id}          — 查询请假详情
    POST   /leaves/{leave_id}/approve  — 员工审批通过
    POST   /leaves/{leave_id}/reject   — 员工审批驳回（可带原因）
    POST   /leaves/{leave_id}/cancel   — 学生取消请假

认证说明：
    当前使用 JWT 解析登录用户，并按权限码控制学生端和员工端接口。
    学生端接口只能访问当前登录学生自己的请假数据。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.common.exceptions import AppException
from backend.app.common.responses import ApiResponse, error_response, success_response
from backend.app.core.security import CurrentUser, require_any_permission, require_permissions
from backend.app.database import get_db
from backend.app.schemas.student_leave_schema import (
    LeaveApprovalQuery,
    LeaveApproveRequest,
    LeaveCancelRequest,
    LeaveCreateRequest,
    LeaveListQuery,
)
from backend.app.services.student_leave_service import StudentLeaveService

# 创建路由，prefix 定义统一前缀，tags 用于 OpenAPI 文档分组
router = APIRouter(
    prefix="/api/v1/student-assistant/leaves",
    tags=["学生请假审批"],
)


# ============================================================
# 接口定义
# ============================================================
# 注意路由定义顺序：静态路由（/pending/count）必须在动态路由（/{leave_id}）之前，
# 否则 FastAPI 会将 "pending" 匹配为 leave_id。

# ----------------------------------------------------------
# POST /leaves — 学生提交请假
# ----------------------------------------------------------

@router.post("", response_model=ApiResponse, summary="提交请假申请")
def create_leave(
    data: LeaveCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:own")),
):
    """学生提交请假申请

    请求体：
    {
        "leave_type": "sick",           // 必填，sick/personal/other
        "reason": "感冒发烧，需休息一天", // 必填，1-500字
        "start_time": "2026-06-10T09:00:00",  // 必填，ISO格式
        "end_time": "2026-06-10T18:00:00"     // 必填，须晚于start_time
    }

    返回：
    {
        "code": 0,
        "message": "请假提交成功",
        "data": { LeaveResponse },
        "trace_id": "..."
    }
    """
    try:
        service = StudentLeaveService(db)
        result = service.create_leave(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            data=data,
        )
        return success_response(data=result, message="请假提交成功")
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# GET /leaves — 学生查自己的请假列表（分页+筛选）
# ----------------------------------------------------------

@router.get("", response_model=ApiResponse, summary="学生查询自己的请假列表")
def list_my_leaves(
    query: LeaveListQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:own")),
):
    """学生查询自己的请假记录列表（分页 + 按状态/时间筛选）

    查询参数（Query String）：
        page=1          — 页码，默认1
        page_size=20    — 每页条数，默认20，最大100
        status=pending  — 按状态筛选（可选）
        date_from=...   — 开始时间起（可选）
        date_to=...     — 开始时间止（可选）
    """
    try:
        service = StudentLeaveService(db)
        items, total = service.list_my_leaves(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            query=query,
        )

        # 包装为分页格式返回
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
# GET /leaves/pending — 员工查所有待审批列表
# ----------------------------------------------------------
# 注意：这条路由必须在 /{leave_id} 之前定义

@router.get("/pending", response_model=ApiResponse, summary="员工查询待审批列表")
def list_pending_leaves(
    query: LeaveApprovalQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:read")),
):
    """员工查询所有待审批的请假列表

    所有 status=pending 的请假都会显示，不按审批人过滤。
    员工看到全部后自行判断谁来审批。

    查询参数（Query String）：
        page=1           — 页码，默认1
        page_size=8      — 每页条数，默认20
        leave_type=sick  — 按请假类型筛选（可选）
        student_name=张  — 按学生姓名模糊搜索（可选）
    """
    try:
        service = StudentLeaveService(db)
        items, total = service.list_all_pending(
            current_user_type=current_user.user_type,
            query=query,
            leave_type=query.leave_type.value if query.leave_type else None,
            student_name=query.student_name,
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
# GET /leaves/pending/count — 统计待审批数量（首页角标）
# ----------------------------------------------------------
# 注意：这条路由必须在 /pending 之后但在 /{leave_id} 之前

@router.get("/pending/count", response_model=ApiResponse, summary="统计待审批请假数量")
def count_pending_leaves(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:read")),
):
    """统计当前待审批的请假总数

    用于员工首页右上角徽标或"待处理"卡片展示。
    """
    try:
        service = StudentLeaveService(db)
        count = service.count_pending(
            current_user_type=current_user.user_type,
        )
        return success_response(data={"count": count})
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# GET /leaves/history — 员工查自己的审批历史
# ----------------------------------------------------------

@router.get("/history", response_model=ApiResponse, summary="员工查询自己的审批历史")
def list_approval_history(
    query: LeaveApprovalQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:read")),
):
    """员工查询自己审批过的请假记录（已通过/已驳回）

    查询参数（Query String）：
        page=1             — 页码，默认1
        page_size=6        — 每页条数，默认20
        status=approved    — 按状态筛选（可选）
        leave_type=sick    — 按请假类型筛选（可选）
        student_name=张    — 按学生姓名模糊搜索（可选）
    """
    try:
        service = StudentLeaveService(db)
        items, total = service.list_approval_history(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            query=query,
            status=query.status,
            leave_type=query.leave_type.value if query.leave_type else None,
            student_name=query.student_name,
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
# GET /leaves/{leave_id} — 查询请假详情
# ----------------------------------------------------------

@router.get("/{leave_id}", response_model=ApiResponse, summary="查询请假详情")
def get_leave_detail(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_any_permission("student_leave:own", "student_leave:read")),
):
    """查询请假申请的完整信息

    权限规则：
        - 学生：只能查自己的请假
        - 员工：只能查自己审批过的请假
        - 管理员：可查任意请假
    """
    try:
        service = StudentLeaveService(db)
        result = service.get_leave_detail(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            leave_id=leave_id,
        )
        return success_response(data=result)
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# POST /leaves/{leave_id}/approve — 审批通过
# ----------------------------------------------------------

@router.post("/{leave_id}/approve", response_model=ApiResponse, summary="审批通过请假")
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:approve")),
):
    """员工审批通过请假申请

    审批通过不需要请求体，路径中的 leave_id 指定目标请假。
    审批人由当前登录用户自动确定。
    """
    try:
        service = StudentLeaveService(db)
        result = service.approve_leave(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            leave_id=leave_id,
        )
        return success_response(data=result, message="请假已审批通过")
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# POST /leaves/{leave_id}/reject — 审批驳回
# ----------------------------------------------------------

@router.post("/{leave_id}/reject", response_model=ApiResponse, summary="驳回请假申请")
def reject_leave(
    leave_id: int,
    data: LeaveApproveRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:approve")),
):
    """员工驳回请假申请

    请求体（可选）：
    {
        "comment": "请假理由不充分，请补充说明"  // 驳回原因，建议填写
    }
    """
    try:
        service = StudentLeaveService(db)
        result = service.reject_leave(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            leave_id=leave_id,
            comment=data.comment,
        )
        return success_response(data=result, message="请假已驳回")
    except AppException as e:
        return error_response(code=e.code, message=e.message)


# ----------------------------------------------------------
# POST /leaves/{leave_id}/cancel — 学生取消请假
# ----------------------------------------------------------

@router.post("/{leave_id}/cancel", response_model=ApiResponse, summary="学生取消请假")
def cancel_leave(
    leave_id: int,
    data: LeaveCancelRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permissions("student_leave:own")),
):
    """学生取消请假申请（仅待审批状态可取消）

    请求体（可选）：
    {
        "reason": "已跟老师沟通，不需要请假了"
    }
    """
    try:
        service = StudentLeaveService(db)
        result = service.cancel_leave(
            current_user_id=current_user.user_id,
            current_user_type=current_user.user_type,
            leave_id=leave_id,
        )
        return success_response(data=result, message="请假已取消")
    except AppException as e:
        return error_response(code=e.code, message=e.message)
