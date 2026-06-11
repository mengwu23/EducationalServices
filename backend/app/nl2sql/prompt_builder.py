"""NL2SQL Prompt 组装器。"""

from .schema_context import build_schema_text

SYSTEM_PROMPT = """你是企业管理查询助手的 MySQL 查询专家。根据给定数据库结构，把用户中文问题转换成一条安全的 MySQL SELECT 语句。

硬性规则：
1. 只输出一条 SELECT 语句。
2. 禁止输出 INSERT、UPDATE、DELETE、DROP、ALTER、CREATE、TRUNCATE 等写操作。
3. 不要输出解释、Markdown、代码块或注释。
4. 不允许 SELECT *，必须明确列出字段。
5. 表名和字段名必须来自数据库结构，不得臆造。
6. 所有出现的业务表都必须过滤 is_delete = 0。
7. 默认最多返回 100 行；用户指定前N名、最近N条时按用户数量 LIMIT。
8. 如果问题不是数据查询，或数据库结构无法支持，只返回 UNSUPPORTED。
9. 遇到“成绩前五/成绩排名”这类问题，如果没有指定课程，默认按学生平均分 AVG(student_score.score) 排名。
10. 涉及多表查询时使用显式 JOIN ... ON。
"""

FEW_SHOT_EXAMPLES = [
    {
        "question": "成绩前五的学生是谁？",
        "sql": (
            "SELECT sp.id AS student_id, sp.student_name, AVG(ss.score) AS avg_score "
            "FROM student_profile sp "
            "JOIN student_score ss ON sp.id = ss.student_id "
            "WHERE sp.is_delete = 0 AND ss.is_delete = 0 "
            "GROUP BY sp.id, sp.student_name "
            "ORDER BY avg_score DESC "
            "LIMIT 5"
        ),
    },
    {
        "question": "张三的各科成绩是多少？",
        "sql": (
            "SELECT sp.student_name, ss.course_name, ss.score, ss.exam_type, ss.semester, ss.exam_date "
            "FROM student_profile sp "
            "JOIN student_score ss ON sp.id = ss.student_id "
            "WHERE sp.student_name = '张三' AND sp.is_delete = 0 AND ss.is_delete = 0 "
            "ORDER BY ss.exam_date DESC "
            "LIMIT 100"
        ),
    },
    {
        "question": "每个客户状态有多少线索？",
        "sql": (
            "SELECT cl.status, COUNT(cl.id) AS lead_count "
            "FROM crm_lead cl "
            "WHERE cl.is_delete = 0 "
            "GROUP BY cl.status "
            "ORDER BY lead_count DESC "
            "LIMIT 100"
        ),
    },
    {
        "question": "最近7天提交了多少份日报？",
        "sql": (
            "SELECT edr.report_date, COUNT(edr.id) AS report_count "
            "FROM employee_daily_report edr "
            "WHERE edr.report_date >= DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND edr.is_delete = 0 "
            "GROUP BY edr.report_date "
            "ORDER BY edr.report_date DESC "
            "LIMIT 100"
        ),
    },
    {
        "question": "待处理的投诉反馈有哪些？",
        "sql": (
            "SELECT sft.ticket_no, sp.student_name, sft.ticket_type, sft.priority_level, sft.status, sft.title "
            "FROM student_feedback_ticket sft "
            "JOIN student_profile sp ON sft.student_id = sp.id "
            "WHERE sft.status IN ('pending', 'processing') AND sft.is_delete = 0 AND sp.is_delete = 0 "
            "ORDER BY sft.create_time DESC "
            "LIMIT 100"
        ),
    },
    {
        "question": "今天天气怎么样？",
        "sql": "UNSUPPORTED",
    },
]


def build_messages(question: str, schema_text: str | None = None) -> list[dict[str, str]]:
    """组装发送给 LLM 的 messages。"""
    schema = schema_text or build_schema_text()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"数据库结构：\n{schema}"},
    ]
    for example in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": example["question"]})
        messages.append({"role": "assistant", "content": example["sql"]})
    messages.append({"role": "user", "content": question})
    return messages
