"""企业管理查询助手的 HTTP 接口。"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.enterprise_assistant_service import EnterpriseAssistantService

router = APIRouter(prefix="/api/v1/enterprise-query")


def success_response(data, trace_id: str | None = None):
    """将业务数据包装成统一响应结构。"""
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "trace_id": trace_id,
    }


def _service(db: Session) -> EnterpriseAssistantService:
    """为当前请求创建企业管理查询助手服务。"""
    return EnterpriseAssistantService(db)


@router.get("/leads/search", summary="按字段查询意向客户")
def search_leads(
    customer_name: Optional[str] = Query(default=None, description="客户姓名，支持模糊查询"),
    phone: Optional[str] = Query(default=None, description="手机号，支持模糊查询"),
    status: Optional[str] = Query(default=None, description="线索状态：new/following/signed/lost/invalid"),
    target_country: Optional[str] = Query(default=None, description="意向国家，支持模糊查询"),
    owner_employee_id: Optional[int] = Query(default=None, description="负责员工ID"),
    created_start: Optional[date] = Query(default=None, description="创建开始日期，格式：YYYY-MM-DD"),
    created_end: Optional[date] = Query(default=None, description="创建结束日期，格式：YYYY-MM-DD"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按客户姓名、手机号、状态、国家、负责人、创建时间等字段查询客户线索。"""
    data = _service(db).search_leads(
        customer_name=customer_name,
        phone=phone,
        status=status,
        target_country=target_country,
        owner_employee_id=owner_employee_id,
        created_start=created_start,
        created_end=created_end,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/daily-reports/search", summary="按字段查询员工日报")
def search_daily_reports(
    employee_id: Optional[int] = Query(default=None, description="员工ID"),
    department_id: Optional[int] = Query(default=None, description="部门ID"),
    report_start: Optional[date] = Query(default=None, description="日报开始日期，格式：YYYY-MM-DD"),
    report_end: Optional[date] = Query(default=None, description="日报结束日期，格式：YYYY-MM-DD"),
    report_status: Optional[str] = Query(default=None, description="日报状态：draft/submitted/archived"),
    keyword: Optional[str] = Query(default=None, description="在日报原文、摘要、进展、风险、计划中模糊搜索"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按员工、部门、日报日期、日报状态和关键字查询员工日报。"""
    data = _service(db).search_daily_reports(
        employee_id=employee_id,
        department_id=department_id,
        report_start=report_start,
        report_end=report_end,
        report_status=report_status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/daily-reports/summary", summary="汇总员工日报并返回明细")
def summarize_daily_reports(
    report_start: date = Query(description="汇总开始日期，格式：YYYY-MM-DD"),
    report_end: date = Query(description="汇总结束日期，格式：YYYY-MM-DD"),
    department_id: Optional[int] = Query(default=None, description="部门ID"),
    report_status: Optional[str] = Query(default=None, description="日报状态：draft/submitted/archived"),
    detail_limit: int = Query(default=200, ge=1, le=500, description="返回日报明细数量上限"),
    db: Session = Depends(get_db),
):
    """按部门和日期范围汇总日报，同时返回参与汇总的日报明细和未提交人员。"""
    data = _service(db).summarize_daily_reports(
        department_id=department_id,
        report_start=report_start,
        report_end=report_end,
        report_status=report_status,
        detail_limit=detail_limit,
    )
    return success_response(data)


@router.get("/departments/search", summary="按字段查询组织架构")
def search_departments(
    department_id: Optional[int] = Query(default=None, description="部门ID"),
    department_name: Optional[str] = Query(default=None, description="部门名称，支持模糊查询"),
    employee_name: Optional[str] = Query(default=None, description="部门成员姓名，支持模糊查询"),
    leader_employee_id: Optional[int] = Query(default=None, description="部门负责人ID"),
    status: Optional[str] = Query(default="enabled", description="部门状态：enabled/disabled"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按部门名称、负责人、成员姓名和状态查询组织架构。"""
    data = _service(db).search_departments(
        department_id=department_id,
        department_name=department_name,
        employee_name=employee_name,
        leader_employee_id=leader_employee_id,
        status=status,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/students/search", summary="按字段查询学生档案")
def search_students(
    student_id: Optional[int] = Query(default=None, description="学生ID"),
    student_name: Optional[str] = Query(default=None, description="学生姓名，支持模糊查询"),
    phone: Optional[str] = Query(default=None, description="手机号，支持模糊查询"),
    current_school: Optional[str] = Query(default=None, description="当前学校，支持模糊查询"),
    target_country: Optional[str] = Query(default=None, description="目标国家，支持模糊查询"),
    status: Optional[str] = Query(default="active", description="学生状态：active/graduated/inactive"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按学生姓名、手机号、学校、目标国家、学生状态等字段查询学生档案。"""
    data = _service(db).search_students(
        student_id=student_id,
        student_name=student_name,
        phone=phone,
        current_school=current_school,
        target_country=target_country,
        status=status,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/student-scores/search", summary="按字段查询学生成绩")
def search_student_scores(
    student_id: Optional[int] = Query(default=None, description="学生ID"),
    student_name: Optional[str] = Query(default=None, description="学生姓名，支持模糊查询"),
    course_name: Optional[str] = Query(default=None, description="课程名称，支持模糊查询"),
    exam_type: Optional[str] = Query(default=None, description="考试类型：daily/midterm/final/makeup/other"),
    semester: Optional[str] = Query(default=None, description="学期，支持模糊查询"),
    exam_start: Optional[date] = Query(default=None, description="考试开始日期，格式：YYYY-MM-DD"),
    exam_end: Optional[date] = Query(default=None, description="考试结束日期，格式：YYYY-MM-DD"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按学生、课程、考试类型、学期、考试日期查询学生成绩。"""
    data = _service(db).search_student_scores(
        student_id=student_id,
        student_name=student_name,
        course_name=course_name,
        exam_type=exam_type,
        semester=semester,
        exam_start=exam_start,
        exam_end=exam_end,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/student-leaves/search", summary="按字段查询学生请假")
def search_student_leaves(
    student_id: Optional[int] = Query(default=None, description="学生ID"),
    student_name: Optional[str] = Query(default=None, description="学生姓名，支持模糊查询"),
    request_no: Optional[str] = Query(default=None, description="请假单号，支持模糊查询"),
    leave_type: Optional[str] = Query(default=None, description="请假类型：sick/personal/other"),
    status: Optional[str] = Query(default=None, description="审批状态：pending/approved/rejected/cancelled"),
    approver_employee_id: Optional[int] = Query(default=None, description="审批员工ID"),
    start_time_from: Optional[datetime] = Query(default=None, description="请假开始时间下限，格式：YYYY-MM-DDTHH:MM:SS"),
    start_time_to: Optional[datetime] = Query(default=None, description="请假开始时间上限，格式：YYYY-MM-DDTHH:MM:SS"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按学生、请假单号、请假类型、审批状态、审批人和请假时间查询请假记录。"""
    data = _service(db).search_student_leaves(
        student_id=student_id,
        student_name=student_name,
        request_no=request_no,
        leave_type=leave_type,
        status=status,
        approver_employee_id=approver_employee_id,
        start_time_from=start_time_from,
        start_time_to=start_time_to,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/student-feedback/search", summary="按字段查询投诉反馈")
def search_student_feedback(
    student_id: Optional[int] = Query(default=None, description="学生ID"),
    student_name: Optional[str] = Query(default=None, description="学生姓名，支持模糊查询"),
    ticket_no: Optional[str] = Query(default=None, description="工单编号，支持模糊查询"),
    ticket_type: Optional[str] = Query(default=None, description="工单类型：complaint/suggestion/consult"),
    category: Optional[str] = Query(default=None, description="反馈分类"),
    priority_level: Optional[str] = Query(default=None, description="优先级：normal/urgent/severe"),
    status: Optional[str] = Query(default=None, description="处理状态：pending/processing/resolved/closed"),
    handler_employee_id: Optional[int] = Query(default=None, description="当前处理人员工ID"),
    keyword: Optional[str] = Query(default=None, description="标题、摘要、详情、方案模糊搜索"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按学生、工单号、类型、分类、优先级、状态、处理人和关键字查询投诉反馈。"""
    data = _service(db).search_student_feedback(
        student_id=student_id,
        student_name=student_name,
        ticket_no=ticket_no,
        ticket_type=ticket_type,
        category=category,
        priority_level=priority_level,
        status=status,
        handler_employee_id=handler_employee_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/student-application-progress/search", summary="按字段查询申请进度")
def search_application_progresses(
    student_id: Optional[int] = Query(default=None, description="学生ID"),
    student_name: Optional[str] = Query(default=None, description="学生姓名，支持模糊查询"),
    progress_stage: Optional[str] = Query(default=None, description="进度阶段：essay/school_apply/visa/offer/other"),
    target_country: Optional[str] = Query(default=None, description="目标国家，支持模糊查询"),
    school_name: Optional[str] = Query(default=None, description="申请院校，支持模糊查询"),
    program_name: Optional[str] = Query(default=None, description="申请项目，支持模糊查询"),
    progress_status: Optional[str] = Query(default=None, description="进度状态：pending/processing/completed/blocked"),
    handler_employee_id: Optional[int] = Query(default=None, description="负责人员工ID"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """按学生、进度阶段、国家、院校、项目、进度状态和处理人查询申请进度。"""
    data = _service(db).search_application_progresses(
        student_id=student_id,
        student_name=student_name,
        progress_stage=progress_stage,
        target_country=target_country,
        school_name=school_name,
        program_name=program_name,
        progress_status=progress_status,
        handler_employee_id=handler_employee_id,
        page=page,
        page_size=page_size,
    )
    return success_response(data)


@router.get("/todos/summary", summary="统计员工待办并返回明细")
def summarize_todos(
    stale_lead_days: int = Query(default=3, ge=1, le=365, description="客户超过多少天未跟进算待办"),
    detail_limit: int = Query(default=100, ge=1, le=500, description="每类待办明细返回数量上限"),
    db: Session = Depends(get_db),
):
    """统计待审批请假、待处理反馈和超时未跟进客户，同时返回三类待办明细。"""
    data = _service(db).summarize_todos(stale_lead_days=stale_lead_days, detail_limit=detail_limit)
    return success_response(data)


@router.get("/statistics/summary", summary="查询管理统计并返回明细")
def summarize_statistics(
    department_id: Optional[int] = Query(default=None, description="部门ID"),
    start_date: Optional[date] = Query(default=None, description="统计开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[date] = Query(default=None, description="统计结束日期，格式：YYYY-MM-DD"),
    detail_limit: int = Query(default=100, ge=1, le=500, description="每类统计明细返回数量上限"),
    db: Session = Depends(get_db),
):
    """统计客户、日报、请假、反馈指标，同时返回统计范围内的主要明细数据。"""
    data = _service(db).summarize_statistics(
        department_id=department_id,
        start_date=start_date,
        end_date=end_date,
        detail_limit=detail_limit,
    )
    return success_response(data)


@router.get("/onboarding/guide", summary="新人入职指引问答")
def query_onboarding_guide(
    question: str = Query(description="新人入职、制度或业务流程问题"),
    db: Session = Depends(get_db),
):
    """调用本地 Dify 公司规章 RAG 应用，回答新人入职相关问题。"""
    data = _service(db).query_onboarding_guide(question=question)
    return success_response(data)
