"""
心理关怀模块 — Pydantic 请求/响应模型
========================================

定义心理关怀模块中所有 API 的请求体和响应体结构。

请求模型：
    PsychAlertCreateRequest  — 创建预警（AI/人工共用）
    PsychAlertActionRequest  — 处理预警（跟进/解除/关闭）
    EmotionUpdateRequest     — 更新情绪状态（AI 预留接口）

响应模型：
    PsychProfileResponse     — 心理画像（含学生姓名）
    PsychAlertResponse       — 预警详情（含学生姓名、老师姓名）

查询参数：
    PsychProfileListQuery    — 画像列表（按风险等级筛选）
    PsychAlertListQuery      — 预警列表（按状态筛选）
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.app.common.enums import PsychAlertStatus, PsychRiskLevel
from backend.app.common.pagination import PageQuery


# ============================================================
# 请求模型
# ============================================================

class PsychAlertCreateRequest(BaseModel):
    """创建预警 — 请求体

    人工或 AI 检测到高风险时调用此接口创建预警记录。
    AI 聊天模块识别到 high / critical 风险时自动调用。

    使用示例（后续 AI 调用）：
        POST /psych/alerts
        {
            "student_id": 1,
            "trigger_reason": "学生表达出自杀倾向，情绪评分降至20分",
            "risk_level": "critical"
        }
    """
    student_id: int = Field(..., description="学生 ID（student_profile.id）")
    trigger_reason: str = Field(..., min_length=1, max_length=1000, description="触发原因，描述为何触发预警")
    risk_level: PsychRiskLevel = Field(..., description="风险等级：medium 中风险 / high 高风险 / critical 危急")


class PsychAlertActionRequest(BaseModel):
    """处理预警 — 请求体

    三个动作共用此模型：
        process — 开始跟进，标记处理人为当前员工
        resolve — 解除预警，需填写处理结果
        close   — 关闭预警

    使用示例：
        POST /psych/alerts/1/action
        {
            "action": "resolve",
            "handle_result": "已安排心理老师进行两次疏导，学生情绪明显好转"
        }
    """
    action: str = Field(..., description="处理动作：process 开始跟进 / resolve 解除 / close 关闭")
    handle_result: Optional[str] = Field(default=None, max_length=2000, description="处理结果，resolve 和 close 时建议填写")


class EmotionUpdateRequest(BaseModel):
    """更新情绪状态 — 请求体

    AI 预留接口，后续 Dify 聊天时实时更新学生的情绪状态。
    人工也可以调用此接口手动更新。

    使用示例（后续 AI 调用）：
        PATCH /psych/profile/emotion
        {
            "emotion_tag": "学业压力",
            "emotion_score": 45,
            "risk_level": "high",
            "summary": "近期作业压力增大，情绪波动明显"
        }
    """
    emotion_tag: Optional[str] = Field(default=None, max_length=100, description='情绪标签，如「学业压力」「平稳」「焦虑」')
    emotion_score: Optional[int] = Field(default=None, ge=0, le=100, description="情绪分值 0-100，越高越积极")
    risk_level: Optional[PsychRiskLevel] = Field(default=None, description="风险等级：low / medium / high / critical")
    summary: Optional[str] = Field(default=None, max_length=1000, description="情绪摘要，AI 总结的近期情绪状态")


# ============================================================
# 查询参数
# ============================================================

class PsychProfileListQuery(PageQuery):
    """心理画像列表查询参数

    继承 PageQuery 的分页参数，额外支持按风险等级筛选。
    用于员工端查看所有学生的心理状态概览。

    使用示例：
        GET /psych/profiles?page=1&page_size=20&risk_level=high
    """
    risk_level: Optional[PsychRiskLevel] = Field(default=None, description="按风险等级筛选：low / medium / high / critical")


class PsychAlertListQuery(PageQuery):
    """预警列表查询参数

    继承 PageQuery 的分页参数，额外支持按状态筛选。

    使用示例：
        GET /psych/alerts?page=1&page_size=10&status=pending
    """
    status: Optional[PsychAlertStatus] = Field(default=None, description="按状态筛选：pending / processing / resolved / closed")


# ============================================================
# 响应模型
# ============================================================

class PsychProfileResponse(BaseModel):
    """心理画像 — 响应体

    包含学生的完整心理状态信息。
    student_name 由 Service 层通过关联查询填充。

    使用方式：
        PsychProfileResponse.model_validate(orm_obj)
    """
    id: int = Field(..., description="心理画像 ID")
    student_id: int = Field(..., description="学生 ID")
    student_name: Optional[str] = Field(default=None, description="学生姓名（由 Service 层关联填充）")
    latest_emotion_tag: Optional[str] = Field(default=None, description="最新情绪标签")
    emotion_score: Optional[int] = Field(default=None, description="情绪分值 0-100")
    risk_level: str = Field(..., description="风险等级")
    last_interaction_time: Optional[datetime] = Field(default=None, description="最近心理交互时间")
    emotion_summary: Optional[str] = Field(default=None, description="长期情绪摘要")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="最后更新时间")

    model_config = {
        "from_attributes": True,
    }


class PsychAlertResponse(BaseModel):
    """预警详情 — 响应体

    包含预警的完整信息，含关联的学生姓名和老师姓名。
    """
    id: int = Field(..., description="预警 ID")
    alert_no: str = Field(..., description="预警编号")
    student_id: int = Field(..., description="学生 ID")
    student_name: Optional[str] = Field(default=None, description="学生姓名（由 Service 层关联填充）")
    trigger_reason: str = Field(..., description="触发原因")
    risk_level: str = Field(..., description="风险等级")
    status: str = Field(..., description="处理状态")
    teacher_employee_id: Optional[int] = Field(default=None, description="跟进老师员工 ID")
    teacher_name: Optional[str] = Field(default=None, description="老师姓名（由 Service 层关联填充）")
    handle_result: Optional[str] = Field(default=None, description="处理结果")
    close_time: Optional[datetime] = Field(default=None, description="关闭时间")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="最后更新时间")

    model_config = {
        "from_attributes": True,
    }
