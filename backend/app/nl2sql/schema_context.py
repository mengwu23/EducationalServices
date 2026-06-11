"""NL2SQL Schema 上下文构建器。"""

from functools import lru_cache

from sqlalchemy import inspect

from ..database import engine

# 只开放企业管理查询助手“查”相关业务表，避免模型看到内部系统表后乱查。
BUSINESS_TABLES = {
    "sys_department",
    "employee_profile",
    "crm_lead",
    "employee_daily_report",
    "student_profile",
    "student_score",
    "student_leave_request",
    "student_feedback_ticket",
    "student_application_progress",
}

TABLE_COMMENTS = {
    "sys_department": "部门组织架构表，存储部门名称、负责人和启停状态。",
    "employee_profile": "员工档案表，存储员工姓名、部门、角色和在职状态。",
    "crm_lead": "意向客户线索表，存储客户姓名、手机号、目标国家、负责人和跟进状态。",
    "employee_daily_report": "员工日报表，存储日报日期、原文、摘要、风险和明日计划。",
    "student_profile": "学生档案表，存储学生姓名、手机号、学校、目标国家和负责员工。",
    "student_score": "学生成绩表，存储课程、分数、考试类型、学期和考试日期。",
    "student_leave_request": "学生请假申请表，存储请假类型、起止时间和审批状态。",
    "student_feedback_ticket": "学生投诉反馈工单表，存储工单类型、优先级、处理状态和处理人。",
    "student_application_progress": "学生申请进度表，存储文书、院校申请、签证、offer 等进度。",
}

FIELD_COMMENTS = {
    "crm_lead.status": "线索状态：new新增/following跟进中/signed已签约/lost已流失/invalid无效",
    "employee_daily_report.report_status": "日报状态：draft草稿/submitted已提交/archived已归档",
    "student_profile.status": "学生状态：active服务中/graduated已结课/inactive停用",
    "student_score.score": "成绩分数，范围0到100；成绩排名默认按平均分从高到低。",
    "student_score.exam_type": "考试类型：daily平时/midterm期中/final期末/makeup补考/other其他",
    "student_leave_request.leave_type": "请假类型：sick病假/personal事假/other其他",
    "student_leave_request.status": "审批状态：pending待审批/approved已通过/rejected已驳回/cancelled已撤销",
    "student_feedback_ticket.ticket_type": "工单类型：complaint投诉/suggestion建议/consult咨询",
    "student_feedback_ticket.priority_level": "优先级：normal普通/urgent紧急/severe严重",
    "student_feedback_ticket.status": "处理状态：pending待处理/processing处理中/resolved已解决/closed已关闭",
    "student_application_progress.progress_stage": "进度阶段：essay文书/school_apply院校申请/visa签证/offer录取/other其他",
    "student_application_progress.progress_status": "进度状态：pending待开始/processing处理中/completed已完成/blocked受阻",
}

JOIN_PATHS = [
    "crm_lead.owner_employee_id = employee_profile.id，用于查询客户负责人姓名或负责人部门。",
    "employee_daily_report.employee_id = employee_profile.id，用于查询日报员工姓名。",
    "employee_daily_report.department_id = sys_department.id，用于查询日报所属部门。",
    "student_score.student_id = student_profile.id，用于按学生查询成绩。",
    "student_leave_request.student_id = student_profile.id，用于按学生查询请假。",
    "student_leave_request.approver_employee_id = employee_profile.id，用于查询审批人。",
    "student_feedback_ticket.student_id = student_profile.id，用于按学生查询反馈。",
    "student_feedback_ticket.handler_employee_id = employee_profile.id，用于查询反馈处理人。",
    "student_application_progress.student_id = student_profile.id，用于按学生查询申请进度。",
    "student_application_progress.handler_employee_id = employee_profile.id，用于查询进度处理人。",
    "employee_profile.department_id = sys_department.id，用于按部门统计员工、日报、客户负责人。",
]

AGG_DEFAULTS = [
    "成绩前几名/成绩排名：如果用户没有指定课程，默认按学生平均分 AVG(student_score.score) 降序排名，并按 student_profile.id, student_profile.student_name 分组。",
    "成绩最高：默认按单条成绩 score 降序；如果问学生排名，默认按平均分。",
    "客户数量：默认 COUNT(crm_lead.id)。",
    "学生数量：默认 COUNT(student_profile.id)。",
    "日报数量：默认 COUNT(employee_daily_report.id)。",
    "待办：待审批请假 status='pending'，待处理反馈 status IN ('pending','processing')。",
]


@lru_cache(maxsize=1)
def build_schema_text() -> str:
    """反射当前数据库结构，组装给 LLM 使用的表结构说明。"""
    inspector = inspect(engine)
    existing_tables = [table for table in inspector.get_table_names() if table in BUSINESS_TABLES]
    sections: list[str] = []

    for table_name in sorted(existing_tables):
        sections.append(f"## {table_name} - {TABLE_COMMENTS.get(table_name, '')}")
        for column in inspector.get_columns(table_name):
            column_name = column["name"]
            column_type = str(column["type"])
            nullable = "NULL" if column.get("nullable", True) else "NOT NULL"
            primary_key = " [PK]" if column.get("primary_key") else ""
            comment = column.get("comment") or FIELD_COMMENTS.get(f"{table_name}.{column_name}", "")
            sections.append(f"  {column_name}  {column_type}  {nullable}{primary_key}  -- {comment}")
        sections.append("")

    sections.append("## 推荐 JOIN 路径")
    sections.extend([f"  - {path}" for path in JOIN_PATHS])
    sections.append("")

    sections.append("## 聚合口径约定")
    sections.extend([f"  - {rule}" for rule in AGG_DEFAULTS])
    sections.append("")

    sections.append("## 硬性数据规则")
    sections.append("  - 所有业务表都有 is_delete 字段，0 表示未删除，1 表示已删除。")
    sections.append("  - 生成 SQL 时必须过滤每个业务表的 is_delete = 0。")
    return "\n".join(sections)


def get_allowed_tables() -> set[str]:
    """返回允许 NL2SQL 查询的业务表名集合。"""
    return set(BUSINESS_TABLES)
