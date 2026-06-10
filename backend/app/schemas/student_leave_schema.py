"""
请假审批模块 — Pydantic 请求/响应模型
========================================

定义请假审批模块中所有 API 的请求体和响应体结构。

按功能拆分：
    - LeaveCreateRequest：学生提交请假
    - LeaveApproveRequest：员工审批（驳回时填写原因）
    - LeaveCancelRequest：学生取消请假
    - LeaveResponse：返回给前端的请假完整数据
    - LeaveListQuery：请假列表的查询参数（含分页 + 筛选）
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.common.enums import LeaveStatus, LeaveType
from app.common.pagination import PageQuery


# ============================================================
# 请求模型
# ============================================================

class LeaveCreateRequest(BaseModel):
    """提交请假申请 — 请求体

    学生提交请假时需要提供的字段。
    leave_type 使用枚举，前端传字符串（如 "sick"）即可，Pydantic 自动校验。
    """
    leave_type: LeaveType = Field(..., description="请假类型：sick 病假 / personal 事假 / other 其他")
    reason: str = Field(..., min_length=1, max_length=500, description="请假原因")
    start_time: datetime = Field(..., description="请假开始时间，ISO 格式（如 2026-06-10T09:00:00）")
    end_time: datetime = Field(..., description="请假结束时间，ISO 格式")

    # --- 业务规则校验 ---

    @field_validator("reason")
    @classmethod
    def reason_not_blank(cls, v: str) -> str:
        """校验请假原因不能为纯空白字符"""
        if not v.strip():
            raise ValueError("请假原因不能为空")
        return v.strip()

    @field_validator("end_time")
    @classmethod
    def end_time_after_start_time(cls, v: datetime, info) -> datetime:
        """校验结束时间不能早于或等于开始时间

        注意：Pydantic v2 中通过 info.data 获取其他字段的值。
        """
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("结束时间必须晚于开始时间")
        return v


class LeaveApproveRequest(BaseModel):
    """审批驳回 — 请求体

    审批通过时不需要请求体（路径参数即可）。
    审批驳回时，建议填写驳回原因，方便学生了解原因。
    """
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="驳回原因，审批驳回时建议填写",
    )


class LeaveCancelRequest(BaseModel):
    """取消请假 — 请求体

    学生取消请假时，可选填取消原因。
    """
    reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="取消原因（可选）",
    )


# ============================================================
# 查询参数
# ============================================================

class LeaveListQuery(PageQuery):
    """请假列表查询参数

    继承 PageQuery 的分页参数，额外支持按状态和时间范围筛选。

    使用示例：
        GET /api/v1/student-assistant/leaves?page=1&page_size=10&status=pending

    注意：student_id 不放在这里，而是从当前登录用户中获取。
          员工查询待审批列表时，通过当前用户 ID 筛选 approver_employee_id。
    """
    status: Optional[LeaveStatus] = Field(default=None, description="按状态筛选（pending / approved / rejected / cancelled）")
    date_from: Optional[datetime] = Field(default=None, description="起始时间，按 create_time 筛选")
    date_to: Optional[datetime] = Field(default=None, description="结束时间，按 create_time 筛选")


# ============================================================
# 响应模型
# ============================================================

class LeaveResponse(BaseModel):
    """请假信息 — 响应体

    包含请假单的完整信息，用于列表和详情接口返回。
    其中 student_name 和 approver_name 由 Service 层通过关联查询填充。
    """
    id: int = Field(..., description="请假申请 ID")
    request_no: str = Field(..., description="请假单号")
    student_id: int = Field(..., description="学生 ID")
    student_name: Optional[str] = Field(default=None, description="学生姓名（由 Service 层关联填充）")
    leave_type: str = Field(..., description="请假类型")
    reason: str = Field(..., description="请假原因")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    status: str = Field(..., description="审批状态")
    approver_employee_id: Optional[int] = Field(default=None, description="审批员工 ID")
    approver_name: Optional[str] = Field(default=None, description="审批人姓名（由 Service 层关联填充）")
    approval_comment: Optional[str] = Field(default=None, description="审批意见")
    approve_time: Optional[datetime] = Field(default=None, description="审批时间")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="最后更新时间")

    model_config = {
        # 允许从 ORM 模型实例化（DAO 返回 SQLAlchemy 对象，直接用 model_validate）
        "from_attributes": True,
    }
