"""
学生申请进度追踪 — Pydantic 请求/响应模型
============================================

进度阶段（progress_stage）：
    essay         — 文书审核
    school_apply  — 院校申请
    visa          — 签证办理
    offer         — 录取通知
    other         — 其他

进度状态（progress_status）：
    pending    — 待开始
    processing — 处理中
    completed  — 已完成
    blocked    — 受阻

CRM 集成预留点：
    crm_record_id     — 关联 CRM 系统中的记录 ID
    crm_sync_status   — CRM 数据同步状态
    crm_last_sync_time — 最近一次 CRM 同步时间
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 进度阶段 & 状态常量 ──

PROGRESS_STAGES = {
    "essay": "文书审核",
    "school_apply": "院校申请",
    "visa": "签证办理",
    "offer": "录取通知",
    "other": "其他",
}

PROGRESS_STATUSES = {
    "pending": "待开始",
    "processing": "处理中",
    "completed": "已完成",
    "blocked": "受阻",
}


# ── 请求模型 ──

class ProgressCreateRequest(BaseModel):
    """创建申请进度记录。"""
    student_id: int = Field(..., description="学生ID")
    progress_stage: str = Field(..., description="进度阶段：essay/school_apply/visa/offer/other")
    target_country: Optional[str] = Field(default=None, max_length=100, description="目标国家")
    school_name: Optional[str] = Field(default=None, max_length=200, description="申请院校")
    program_name: Optional[str] = Field(default=None, max_length=200, description="申请项目")
    progress_status: str = Field(default="processing", description="状态：pending/processing/completed/blocked")
    progress_desc: Optional[str] = Field(default=None, description="进度说明")
    handler_employee_id: Optional[int] = Field(default=None, description="负责人员工ID")
    expected_finish_time: Optional[datetime] = Field(default=None, description="预计完成时间")


class ProgressUpdateRequest(BaseModel):
    """更新申请进度记录（部分更新）。"""
    progress_stage: Optional[str] = Field(default=None, description="进度阶段")
    target_country: Optional[str] = Field(default=None, max_length=100)
    school_name: Optional[str] = Field(default=None, max_length=200)
    program_name: Optional[str] = Field(default=None, max_length=200)
    progress_status: Optional[str] = Field(default=None, description="状态")
    progress_desc: Optional[str] = Field(default=None, description="进度说明")
    handler_employee_id: Optional[int] = Field(default=None, description="负责人员工ID")
    expected_finish_time: Optional[datetime] = Field(default=None, description="预计完成时间")


# ── 响应模型 ──

class ProgressResponse(BaseModel):
    """申请进度 — 响应体。"""
    id: int
    student_id: int
    student_name: Optional[str] = Field(default=None, description="学生姓名（关联填充）")
    progress_stage: str
    progress_stage_label: Optional[str] = Field(default=None, description="阶段中文名")
    target_country: Optional[str] = None
    school_name: Optional[str] = None
    program_name: Optional[str] = None
    progress_status: str
    progress_status_label: Optional[str] = Field(default=None, description="状态中文名")
    progress_desc: Optional[str] = None
    handler_employee_id: Optional[int] = None
    handler_name: Optional[str] = Field(default=None, description="负责人姓名（关联填充）")
    expected_finish_time: Optional[datetime] = None

    # ── CRM 集成预留字段 ──
    crm_record_id: Optional[str] = Field(default=None, description="CRM系统记录ID（预留）")
    crm_sync_status: Optional[str] = Field(default=None, description="CRM同步状态：not_synced/syncing/synced/failed（预留）")
    crm_last_sync_time: Optional[datetime] = Field(default=None, description="最近CRM同步时间（预留）")

    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}


class ProgressListResponse(BaseModel):
    """申请进度列表 — 响应体。"""
    items: list[ProgressResponse]
    total: int
    page: int
    page_size: int


class ProgressTimelineItem(BaseModel):
    """进度时间线节点。"""
    id: int
    stage: str
    stage_label: str
    status: str
    status_label: str
    desc: Optional[str] = None
    handler_name: Optional[str] = None
    school_name: Optional[str] = None
    expected_finish_time: Optional[datetime] = None
    update_time: datetime


class ProgressTimelineResponse(BaseModel):
    """学生申请进度时间线。"""
    student_id: int
    student_name: str
    stages: list[ProgressTimelineItem]
    summary: str = Field(default="", description="进度概览文本")


class StagesReferenceResponse(BaseModel):
    """进度阶段参考数据。"""
    stages: dict[str, str] = Field(default_factory=dict, description="阶段编码→中文名")
    statuses: dict[str, str] = Field(default_factory=dict, description="状态编码→中文名")


# ── CRM 同步预留 ──

class CRMSyncRequest(BaseModel):
    """CRM 数据同步请求。"""
    crm_system: str = Field(default="crm_lead", description="CRM系统标识，当前支持本地crm_lead")
    crm_record_id: Optional[str] = Field(default=None, description="CRM系统中的记录ID，支持crm_lead.id或lead_no")
    sync_direction: str = Field(default="to_local", description="同步方向：to_local从CRM拉取/to_crm推送到CRM")
    progress_id: Optional[int] = Field(default=None, description="本地申请进度ID，to_crm时建议传入")
    student_id: Optional[int] = Field(default=None, description="本地学生ID，to_local时可指定同步到哪个学生")
    progress_stage: Optional[str] = Field(default=None, description="同步生成/更新的进度阶段")
    progress_status: Optional[str] = Field(default=None, description="同步生成/更新的进度状态")
    progress_desc: Optional[str] = Field(default=None, description="同步生成/更新的进度说明")
