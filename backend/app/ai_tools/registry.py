from typing import Optional

from pydantic import BaseModel, Field

from backend.app.ai_tools.academic_event_tools import (
    AcademicEventToolCreate,
    AcademicEventToolList,
    create_academic_event,
    list_active_academic_events,
)
from backend.app.ai_tools.student_feedback_ticket_tools import (
    FeedbackTicketToolCreate,
    FeedbackTicketToolList,
    create_feedback_ticket,
    list_feedback_tickets,
)
from backend.app.common.exceptions import NotFoundError


# ── 学生请假审批工具（供 Dify/AI 调用）──

class LeaveApproveToolArgs(BaseModel):
    """企业助手/Dify 审批通过请假参数。"""
    leave_id: int = Field(..., description="请假申请ID")
    employee_id: int = Field(..., description="审批员工ID（employee_profile.id）")


class LeaveRejectToolArgs(BaseModel):
    """企业助手/Dify 驳回请假参数。"""
    leave_id: int = Field(..., description="请假申请ID")
    employee_id: int = Field(..., description="审批员工ID（employee_profile.id）")
    comment: Optional[str] = Field(default=None, description="驳回原因")


def approve_student_leave(db, payload: LeaveApproveToolArgs) -> dict:
    from backend.app.services.student_leave_service import StudentLeaveService
    service = StudentLeaveService(db)
    result = service.approve_leave(
        current_user_id=payload.employee_id,
        current_user_type="employee",
        leave_id=payload.leave_id,
    )
    return {
        "success": True,
        "leave_id": result.id,
        "request_no": result.request_no,
        "student_name": result.student_name,
        "status": result.status,
        "message": f"Leave {result.request_no} approved",
    }


def reject_student_leave(db, payload: LeaveRejectToolArgs) -> dict:
    from backend.app.services.student_leave_service import StudentLeaveService
    service = StudentLeaveService(db)
    result = service.reject_leave(
        current_user_id=payload.employee_id,
        current_user_type="employee",
        leave_id=payload.leave_id,
        comment=payload.comment,
    )
    return {
        "success": True,
        "leave_id": result.id,
        "request_no": result.request_no,
        "student_name": result.student_name,
        "status": result.status,
        "message": f"Leave {result.request_no} rejected",
    }


# ── 心理关怀预警工具（供 Dify/AI 调用）──

class PsychAlertListToolArgs(BaseModel):
    """查询心理预警列表参数。"""
    status: Optional[str] = Field(default=None, description="按状态筛选：pending/processing/resolved/closed")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数")


class PsychAlertProcessToolArgs(BaseModel):
    """处理心理预警参数。"""
    alert_id: int = Field(..., description="预警ID")
    employee_id: int = Field(..., description="操作员工ID")
    action: str = Field(..., description="处理动作：process/resolve/close")
    handle_result: Optional[str] = Field(default=None, description="处理结果（resolve时填写）")


def list_student_psych_alerts(db, payload: PsychAlertListToolArgs) -> dict:
    from backend.app.models.student_psych_alert import StudentPsychAlert
    from backend.app.services.student_psych_service import StudentPsychService

    query = db.query(StudentPsychAlert).filter(StudentPsychAlert.is_delete == 0)
    if payload.status:
        query = query.filter(StudentPsychAlert.status == payload.status)

    total = query.count()
    items = (
        query.order_by(StudentPsychAlert.create_time.desc())
        .offset((payload.page - 1) * payload.page_size)
        .limit(payload.page_size)
        .all()
    )

    service = StudentPsychService(db)
    result_items = []
    for item in items:
        student_name = service._get_student_name_by_id(item.student_id)
        teacher_name = None
        if item.teacher_employee_id:
            teacher_name = service._get_employee_name_by_id(item.teacher_employee_id)
        result_items.append({
            "id": item.id,
            "alert_no": item.alert_no,
            "student_id": item.student_id,
            "student_name": student_name,
            "trigger_reason": item.trigger_reason,
            "risk_level": item.risk_level,
            "status": item.status,
            "teacher_employee_id": item.teacher_employee_id,
            "teacher_name": teacher_name,
            "handle_result": item.handle_result,
            "close_time": item.close_time.isoformat() if item.close_time else None,
            "create_time": item.create_time.isoformat() if item.create_time else None,
            "update_time": item.update_time.isoformat() if item.update_time else None,
        })

    return {"items": result_items, "total": total, "page": payload.page, "page_size": payload.page_size}


def process_student_psych_alert(db, payload: PsychAlertProcessToolArgs) -> dict:
    from backend.app.services.student_psych_service import StudentPsychService

    service = StudentPsychService(db)

    msg_map = {
        "process": "已开始跟进",
        "resolve": "已解除",
        "close": "已关闭",
    }
    if payload.action == "process":
        result = service.process_alert(
            current_user_id=payload.employee_id,
            current_user_type="employee",
            alert_id=payload.alert_id,
        )
    elif payload.action == "resolve":
        result = service.resolve_alert(
            current_user_id=payload.employee_id,
            current_user_type="employee",
            alert_id=payload.alert_id,
            handle_result=payload.handle_result,
        )
    elif payload.action == "close":
        result = service.close_alert(
            current_user_id=payload.employee_id,
            current_user_type="employee",
            alert_id=payload.alert_id,
        )
    else:
        raise ValueError(f"不支持的操作类型：{payload.action}")

    msg = f"预警 {result.alert_no} {msg_map[payload.action]}"

    return {
        "success": True,
        "alert_id": result.id,
        "alert_no": result.alert_no,
        "student_name": result.student_name,
        "status": result.status,
        "message": msg,
    }


# ── 统一工具注册表 ──

AI_TOOL_REGISTRY = {
    "academic_event.create": {
        "handler": create_academic_event,
        "schema": AcademicEventToolCreate,
    },
    "academic_event.list_active": {
        "handler": list_active_academic_events,
        "schema": AcademicEventToolList,
    },
    "student_feedback_ticket.create": {
        "handler": create_feedback_ticket,
        "schema": FeedbackTicketToolCreate,
    },
    "student_feedback_ticket.list": {
        "handler": list_feedback_tickets,
        "schema": FeedbackTicketToolList,
    },
    # 学生请假审批
    "student_leave.approve": {
        "handler": approve_student_leave,
        "schema": LeaveApproveToolArgs,
    },
    "student_leave.reject": {
        "handler": reject_student_leave,
        "schema": LeaveRejectToolArgs,
    },
    # 心理关怀预警
    "student_psych_alert.list": {
        "handler": list_student_psych_alerts,
        "schema": PsychAlertListToolArgs,
    },
    "student_psych_alert.process": {
        "handler": process_student_psych_alert,
        "schema": PsychAlertProcessToolArgs,
    },
}


def get_ai_tool(name: str):
    return AI_TOOL_REGISTRY.get(name)


def invoke_ai_tool(name: str, db, arguments: dict):
    tool = get_ai_tool(name)
    if tool is None:
        raise NotFoundError("AI tool is not registered")
    payload = tool["schema"](**arguments)
    return tool["handler"](db, payload)
