"""企业管理 NL2SQL 智能问数接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.enterprise_nl2sql_service import EnterpriseNl2SqlService

router = APIRouter(prefix="/api/v1/enterprise-query/nl2sql")

# 在 Swagger docs 的接口 summary 中直接展示 NL2SQL 可查询范围，方便前端和测试人员确认能力边界。


def success_response(data, trace_id: str | None = None):
    """统一包装 NL2SQL 接口响应。"""
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "trace_id": trace_id,
    }


@router.post("/query", summary='NL2SQL智能问数')
def query_by_natural_language(
    query: str = Query(..., min_length=1, max_length=1000, description="NL2SQL 智能问数：可查组织部门(sys_department)、员工档案(employee_profile)、"
    "客户线索(crm_lead)、员工日报(employee_daily_report)、学生档案(student_profile)、"
    "学生成绩(student_score)、学生请假(student_leave_request)、"
    "投诉反馈(student_feedback_ticket)、申请进度(student_application_progress)；"
    "支持明细查询、条件筛选、排序、分组统计、TopN 排名"),
    db: Session = Depends(get_db),
):
    """接收 query 字符串，转换成安全 SQL 后查询数据库真实结果。"""
    result = EnterpriseNl2SqlService(db).query(query)
    return success_response(result)
