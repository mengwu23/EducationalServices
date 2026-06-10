from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# 请求模型
# ------------------------------------------------------------------


class CustomerJudgementRequest(BaseModel):
    """提交客户画像研判的请求体。"""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="待研判的客户信息文本，支持自由格式",
    )
    sys_query: str | None = Field(
        default=None,
        max_length=1000,
        description="补充研判要求，将传递给 Dify 工作流",
    )
    lead_id: int | None = Field(default=None, description="关联的意向客户线索ID")
    target_product: str | None = Field(default=None, max_length=100, description="指定研判目标产品")


class JudgementListRequest(BaseModel):
    """研判记录列表查询参数。"""

    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=200, description="每页数量")
    status: str | None = Field(default=None, description="筛选状态：pending/completed/failed")
    lead_id: int | None = Field(default=None, description="筛选关联线索ID")
    match_level: str | None = Field(default=None, description="筛选匹配等级：high/medium/low")
    date_start: date | None = Field(default=None, description="创建开始日期")
    date_end: date | None = Field(default=None, description="创建结束日期")


# ------------------------------------------------------------------
# 响应模型 —— AI 研判结果子结构
# ------------------------------------------------------------------


class CustomerProfileInfo(BaseModel):
    """客户画像信息。"""

    core_tags: list[str] = Field(default_factory=list)
    education_level: str | None = None
    school_name: str | None = None
    major: str | None = None
    current_grade: str | None = None
    language_scores: str | None = None
    target_country: str | None = None
    target_program: str | None = None
    budget_range: str | None = None
    key_strengths: str | None = None
    potential_risks: str | None = None


class DimensionAnalysis(BaseModel):
    """单个维度的研判分析。"""

    dimension: str = ""
    customer_value: str | None = None
    rule_requirement: str | None = None
    is_match: bool = False
    evidence: str | None = None


class ProductEvaluation(BaseModel):
    """单个产品的研判结果。"""

    product_name: str | None = None
    conclusion: str = ""  # match / mismatch / insufficient_info
    match_score: int | None = None
    match_level: str | None = None
    dimension_analysis: list[DimensionAnalysis] = Field(default_factory=list)
    summary_reason: str | None = None
    missing_info: list[str] = Field(default_factory=list)
    actionable_advice: str | None = None


class CustomerJudgementResult(BaseModel):
    """Dify LLM 返回的完整研判结果。"""

    executive_summary: str | None = None
    is_target_customer: bool | None = None
    overall_match_score: int | None = None
    overall_match_level: str | None = None
    customer_profile: CustomerProfileInfo | None = None
    product_a_evaluation: ProductEvaluation | None = None
    product_b_evaluation: ProductEvaluation | None = None
    reason_summary: str | None = None
    suggestion: str | None = None
    final_next_steps: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------
# 响应模型 —— 列表 / 详情
# ------------------------------------------------------------------


class JudgementRecordItem(BaseModel):
    """研判记录列表项。"""

    id: int
    analysis_no: str
    source_type: str
    source_file_name: str | None = None
    target_product: str | None = None
    lead_id: int | None = None
    is_target_customer: int | None = None
    match_score: Decimal | None = None
    match_level: str | None = None
    reason_summary: str | None = None
    suggestion: str | None = None
    status: str
    submitter_user_id: int | None = None
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class JudgementRecordDetail(JudgementRecordItem):
    """研判记录详情，包含原始输入和 AI 研判结果。"""

    raw_content: str | None = None
    executive_summary: str | None = None
    ai_result: CustomerJudgementResult | None = None


class PaginatedJudgementResponse(BaseModel):
    """分页研判记录列表。"""

    total: int
    page: int
    page_size: int
    items: list[JudgementRecordItem]
