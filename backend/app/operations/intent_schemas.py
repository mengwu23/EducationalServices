"""所有业务操作的意图定义与字段 Schema。

每个 IntentSchema 描述一个操作所需的字段及其规则，
供 LLM 解析和 Handler 校验时共用。
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FieldDef:
    """字段定义。"""
    key: str
    label: str
    required: bool = False
    description: str = ""
    example: str = ""


@dataclass
class IntentSchema:
    """操作意图的字段描述。"""
    intent: str
    description: str
    fields: List[FieldDef] = field(default_factory=list)

    @property
    def required_keys(self) -> List[str]:
        return [f.key for f in self.fields if f.required]

    @property
    def optional_keys(self) -> List[str]:
        return [f.key for f in self.fields if not f.required]

    def get_label(self, key: str) -> str:
        for f in self.fields:
            if f.key == key:
                return f.label
        return key


# ============================
# 意向客户录入 (create_lead)
# ============================

CREATE_LEAD_SCHEMA = IntentSchema(
    intent="create_lead",
    description="新增意向客户",
    fields=[
        FieldDef(key="customer_name", label="客户姓名", required=True, description="客户姓名", example="王同学"),
        FieldDef(key="phone", label="手机号", required=True, description="客户手机号", example="13812345678"),
        FieldDef(key="wechat_no", label="微信号", required=False, description="客户微信号", example="wx_abc123"),
        FieldDef(key="email", label="邮箱", required=False, description="客户邮箱", example="wang@example.com"),
        FieldDef(key="source_channel", label="来源渠道", required=False, description="客户来源渠道", example="讲座报名"),
        FieldDef(key="education_level", label="学历阶段", required=False, description="客户当前学历阶段", example="本科"),
        FieldDef(key="school_name", label="当前学校", required=False, description="客户就读学校", example="XX大学"),
        FieldDef(key="major", label="专业", required=False, description="客户所学专业", example="计算机科学"),
        FieldDef(key="current_grade", label="当前年级", required=False, description="客户当前年级", example="大三"),
        FieldDef(key="target_country", label="意向国家", required=False, description="留学目标国家", example="英国"),
        FieldDef(key="target_program", label="意向项目", required=False, description="留学目标项目", example="硕士申请"),
        FieldDef(key="budget_range", label="预算区间", required=False, description="客户预算范围", example="30万"),
        FieldDef(key="background_info", label="客户背景", required=False, description="客户背景补充信息", example="雅思6.5，GPA3.5"),
    ],
)


# ============================
# 客户状态更新 (update_lead_status)
# ============================

UPDATE_LEAD_STATUS_SCHEMA = IntentSchema(
    intent="update_lead_status",
    description="更新客户状态",
    fields=[
        FieldDef(key="customer_name", label="客户姓名", required=True, description="要更新状态的客户名", example="王同学"),
        FieldDef(key="status", label="新状态", required=True, description="目标状态：new/following/signed/lost/invalid", example="signed"),
        FieldDef(key="latest_follow_up_summary", label="跟进摘要", required=False, description="最近跟进记录摘要", example="家长下周再来咨询"),
        FieldDef(key="lost_reason", label="流失原因", required=False, description="流失原因（状态改为lost时必填）", example="预算不足"),
    ],
)


# ============================
# 口述日报提交 (submit_daily_report)
# ============================

SUBMIT_DAILY_REPORT_SCHEMA = IntentSchema(
    intent="submit_daily_report",
    description="提交日报",
    fields=[
        FieldDef(key="raw_content", label="原始内容", required=True, description="日报原始口述内容", example="今天跟进了5个客户..."),
        FieldDef(key="summary", label="AI摘要", required=True, description="日报工作总结摘要", example="跟进5个客户，处理1个投诉"),
        FieldDef(key="key_progress", label="关键进展", required=True, description="今日关键进展", example="王同学已约下周面谈"),
        FieldDef(key="risks", label="风险问题", required=True, description="风险与问题", example="李同学转化意愿不稳定"),
        FieldDef(key="tomorrow_plan", label="明日计划", required=True, description="明日工作计划", example="重点推进英国项目客户"),
    ],
)


# ============================
# 学生成绩录入 (enter_student_score)
# ============================

ENTER_STUDENT_SCORE_SCHEMA = IntentSchema(
    intent="enter_student_score",
    description="录入学生成绩",
    fields=[
        FieldDef(key="student_name", label="学生姓名", required=True, description="学生姓名", example="张同学"),
        FieldDef(key="course_name", label="课程名称", required=True, description="课程或科目名称", example="雅思听力"),
        FieldDef(key="score", label="成绩", required=True, description="成绩分数（0-100）", example="7"),
        FieldDef(key="exam_type", label="考试类型", required=True, description="考试类型：模考/期中/期末等", example="模考"),
        FieldDef(key="semester", label="学期", required=True, description="学期", example="2026春季"),
        FieldDef(key="exam_date", label="考试日期", required=True, description="考试日期", example="2026-06-10"),
        FieldDef(key="remark", label="备注", required=True, description="备注", example="雅思模考成绩"),
    ],
)


# ============================
# 请假审批 (approve_leave)
# ============================

APPROVE_LEAVE_SCHEMA = IntentSchema(
    intent="approve_leave",
    description="审批学生请假",
    fields=[
        FieldDef(key="action", label="操作", required=True, description="query/approve/reject", example="approve"),
        FieldDef(key="student_name", label="学生姓名", required=True, description="要审批的学生名", example="张三"),
        FieldDef(key="approval_comment", label="审批意见", required=False, description="审批备注", example="同意请假"),
        FieldDef(key="leave_type", label="请假类型", required=False, description="sick/personal/other", example="sick"),
    ],
)


# ============================
# 投诉反馈处理 (handle_complaint)
# ============================

HANDLE_COMPLAINT_SCHEMA = IntentSchema(
    intent="handle_complaint",
    description="处理投诉反馈",
    fields=[
        FieldDef(key="action", label="操作", required=True, description="query/process/resolve/close/notify", example="process"),
        FieldDef(key="student_name", label="学生姓名", required=True, description="投诉学生名", example="张同学"),
        FieldDef(key="status", label="目标状态", required=False, description="processing/resolved/closed", example="processing"),
        FieldDef(key="solution", label="处理方案", required=False, description="处理方案或结果", example="已联系学生了解情况"),
        FieldDef(key="content_summary", label="摘要", required=False, description="内容摘要", example="投诉宿舍维修慢"),
    ],
)


# ============================
# Schema 注册表
# ============================

INTENT_SCHEMA_REGISTRY: Dict[str, IntentSchema] = {
    "create_lead": CREATE_LEAD_SCHEMA,
    "update_lead_status": UPDATE_LEAD_STATUS_SCHEMA,
    "submit_daily_report": SUBMIT_DAILY_REPORT_SCHEMA,
    "enter_student_score": ENTER_STUDENT_SCORE_SCHEMA,
    "approve_leave": APPROVE_LEAVE_SCHEMA,
    "handle_complaint": HANDLE_COMPLAINT_SCHEMA,
}
