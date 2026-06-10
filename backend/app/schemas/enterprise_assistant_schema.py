"""企业管理查询助手的响应结构定义。"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PageResult(BaseModel):
    """列表查询统一分页返回结构。"""

    total: int = Field(description="符合条件的总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    items: List[Any] = Field(default_factory=list, description="当前页数据列表")


class SummaryBlock(BaseModel):
    """统计/汇总接口统一摘要结构。"""

    text: str = Field(description="面向用户展示的汇总文本")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="机器可读的统计指标")


class LeadItem(BaseModel):
    """意向客户线索返回项。"""

    id: int
    lead_no: str
    customer_name: str
    phone: Optional[str] = None
    wechat_no: Optional[str] = None
    email: Optional[str] = None
    source_channel: Optional[str] = None
    education_level: Optional[str] = None
    school_name: Optional[str] = None
    major: Optional[str] = None
    current_grade: Optional[str] = None
    target_country: Optional[str] = None
    target_program: Optional[str] = None
    budget_range: Optional[str] = None
    background_info: Optional[str] = None
    follow_up_history: Optional[str] = None
    latest_follow_up_summary: Optional[str] = None
    status: str
    owner_employee_id: Optional[int] = None
    owner_name: Optional[str] = None
    last_follow_up_time: Optional[datetime] = None
    lost_reason: Optional[str] = None
    signed_time: Optional[datetime] = None
    create_time: datetime
    update_time: datetime


class DailyReportItem(BaseModel):
    """员工日报返回项。"""

    id: int
    employee_id: int
    employee_name: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    report_date: date
    raw_content: str
    summary: Optional[str] = None
    key_progress: Optional[str] = None
    risks: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    report_status: str
    create_time: datetime
    update_time: datetime


class DailyReportSummaryResult(BaseModel):
    """日报汇总返回结构，包含汇总文本、日报明细和未提交人员。"""

    summary: SummaryBlock
    reports: List[DailyReportItem]
    missing_employee_names: List[str]


class DepartmentMemberItem(BaseModel):
    """部门成员返回项。"""

    id: int
    employee_no: str
    employee_name: str
    role_code: str
    job_title: Optional[str] = None
    status: str


class DepartmentItem(BaseModel):
    """组织架构部门返回项。"""

    id: int
    department_name: str
    parent_id: Optional[int] = None
    leader_employee_id: Optional[int] = None
    leader_name: Optional[str] = None
    department_desc: Optional[str] = None
    sort_order: int
    status: str
    create_time: datetime
    update_time: datetime
    members: List[DepartmentMemberItem] = Field(default_factory=list)


class StudentProfileItem(BaseModel):
    """学生档案返回项。"""

    id: int
    user_id: Optional[int] = None
    student_no: Optional[str] = None
    student_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    current_school: Optional[str] = None
    current_grade: Optional[str] = None
    target_country: Optional[str] = None
    target_program: Optional[str] = None
    counselor_employee_id: Optional[int] = None
    teacher_employee_id: Optional[int] = None
    status: str
    create_time: datetime
    update_time: datetime


class StudentScoreItem(BaseModel):
    """学生成绩返回项。"""

    id: int
    student_id: int
    student_name: Optional[str] = None
    course_name: str
    score: Decimal
    exam_type: Optional[str] = None
    semester: Optional[str] = None
    exam_date: Optional[date] = None
    operator_employee_id: Optional[int] = None
    remark: Optional[str] = None
    create_time: datetime
    update_time: datetime


class StudentLeaveItem(BaseModel):
    """学生请假返回项。"""

    id: int
    request_no: str
    student_id: int
    student_name: Optional[str] = None
    leave_type: str
    reason: str
    start_time: datetime
    end_time: datetime
    status: str
    approver_employee_id: Optional[int] = None
    approver_name: Optional[str] = None
    approval_comment: Optional[str] = None
    approve_time: Optional[datetime] = None
    create_time: datetime
    update_time: datetime


class StudentFeedbackItem(BaseModel):
    """学生投诉反馈返回项。"""

    id: int
    ticket_no: str
    student_id: int
    student_name: Optional[str] = None
    ticket_type: str
    category: Optional[str] = None
    title: str
    content_summary: Optional[str] = None
    detail: Optional[str] = None
    priority_level: str
    status: str
    handler_employee_id: Optional[int] = None
    handler_name: Optional[str] = None
    solution: Optional[str] = None
    satisfaction_score: Optional[int] = None
    is_notified: int
    close_time: Optional[datetime] = None
    create_time: datetime
    update_time: datetime


class StudentApplicationProgressItem(BaseModel):
    """学生申请进度返回项。"""

    id: int
    student_id: int
    student_name: Optional[str] = None
    progress_stage: str
    target_country: Optional[str] = None
    school_name: Optional[str] = None
    program_name: Optional[str] = None
    progress_status: str
    progress_desc: Optional[str] = None
    handler_employee_id: Optional[int] = None
    handler_name: Optional[str] = None
    expected_finish_time: Optional[datetime] = None
    create_time: datetime
    update_time: datetime


class TodoSummaryResult(BaseModel):
    """待办统计返回结构，统计后同时返回三类待办明细。"""

    summary: SummaryBlock
    pending_leaves: List[StudentLeaveItem]
    feedback_tickets: List[StudentFeedbackItem]
    stale_leads: List[LeadItem]


class StatisticsSummaryResult(BaseModel):
    """管理统计返回结构，包含统计指标和统计范围内的明细数据。"""

    summary: SummaryBlock
    lead_count_by_status: Dict[str, int]
    lead_count_by_country: Dict[str, int]
    daily_report_count: int
    pending_leave_count: int
    pending_feedback_count: int
    leads: List[LeadItem]
    daily_reports: List[DailyReportItem]
    pending_leaves: List[StudentLeaveItem]
    pending_feedback_tickets: List[StudentFeedbackItem]


class OnboardingGuideResult(BaseModel):
    """新人入职指引返回结构。"""

    status: str
    message: str
    question: str
    category: Optional[str] = None
    answer: Optional[str] = None
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
