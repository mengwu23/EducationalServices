"""智能报告展示用丰富种子数据脚本（多部门 / 四周跨度 / 大数据量）。

覆盖五类报告本次增强后的全部字段：
- 投诉周报：满意度 satisfaction_score、优先级 priority_level、超期工单、中文分类、同环比
- 客户经营：成交线索 signed+signed_time、流失 lost+lost_reason、四维画像、研判等级
- 员工日报：中文风险文本（供 top_risk_themes 提取）、关键进展、明日计划、多状态
- 心理周报：情绪标签、情绪分、风险分层、情绪摘要、互动时间、预警状态

用法（项目根目录，已配置 .env 的 DATABASE_URL）：
    python -m backend.scripts.seed_report_rich_demo
可重复执行（全部 merge）。department_id=1 为主展示部门。
"""

from datetime import date, datetime, timedelta

from backend.app.database import get_session_factory
from backend.app.models import (
    CrmLead,
    CustomerAnalysisRecord,
    EmployeeDailyReport,
    EmployeeProfile,
    EventLecture,
    EventRegistration,
    StudentFeedbackTicket,
    StudentProfile,
    StudentPsychAlert,
    StudentPsychProfile,
    SysDepartment,
    SysUser,
)

# 展示周期：2026-06-01 ~ 2026-06-28（四周）
PERIOD_START = date(2026, 6, 1)


def _dt(day_offset: int, hour: int = 9, minute: int = 0) -> datetime:
    """相对周期起点的日期时间。"""
    d = PERIOD_START + timedelta(days=day_offset)
    return datetime(d.year, d.month, d.day, hour, minute, 0)


def seed_dimensions(db) -> None:
    """部门、用户、员工、学生等基础维度。"""
    db.merge(SysDepartment(id=1, department_name="咨询一部"))
    db.merge(SysDepartment(id=2, department_name="咨询二部"))
    db.merge(SysDepartment(id=3, department_name="教学服务部"))

    # 用户：1 管理员 + 每部门若干员工 + 学生
    users = [
        SysUser(id=1, username="admin", real_name="系统管理员", user_type="admin"),
    ]
    # 员工 user 201-209，学生 user 301-312
    emp_names = ["张明", "李娜", "王强", "陈静", "刘洋", "赵敏", "孙磊", "周婷", "吴昊"]
    for i, name in enumerate(emp_names):
        users.append(SysUser(id=201 + i, username=f"emp{201+i}", real_name=name, user_type="employee"))
    stu_names = ["林晓", "黄睿", "徐悦", "马俊", "高媛", "罗杰", "何欣", "梁宇", "宋佳", "唐磊", "冯雪", "韩冰"]
    for i, name in enumerate(stu_names):
        users.append(SysUser(id=301 + i, username=f"stu{301+i}", real_name=name, user_type="student"))
    for u in users:
        db.merge(u)
    db.flush()

    # 员工档案：部门1配5人，部门2配2人，部门3配2人
    emp_dept = [1, 1, 1, 1, 1, 2, 2, 3, 3]
    emp_roles = ["sales", "sales", "service", "service", "sales", "sales", "service", "teacher", "teacher"]
    for i in range(9):
        db.merge(EmployeeProfile(
            id=201 + i, user_id=201 + i, department_id=emp_dept[i],
            employee_no=f"EMP{201+i}", employee_name=emp_names[i], role_code=emp_roles[i],
        ))
    db.flush()

    # 学生档案：分属不同顾问，含意向国家/项目维度
    stu_country = ["美国", "英国", "美国", "澳大利亚", "加拿大", "英国", "美国", "新加坡", "英国", "美国", "澳大利亚", "加拿大"]
    stu_program = ["计算机硕士", "商科硕士", "数据科学硕士", "本科预科", "高中转学",
                   "金融硕士", "计算机硕士", "商科硕士", "传媒硕士", "数据科学硕士", "本科预科", "工程硕士"]
    stu_counselor = [201, 201, 202, 202, 203, 206, 206, 208, 208, 201, 202, 203]
    for i in range(12):
        db.merge(StudentProfile(
            id=301 + i, user_id=301 + i,
            counselor_employee_id=stu_counselor[i], teacher_employee_id=208,
            student_no=f"STU{301+i}", student_name=stu_names[i],
            target_country=stu_country[i], target_program=stu_program[i],
        ))
    db.flush()

    # 活动讲座
    db.merge(EventLecture(
        id=100, event_no="EVT100", event_name="2026 留学规划公开课",
        event_type="offline", start_time=_dt(3, 14, 0),
    ))
    db.merge(EventLecture(
        id=101, event_no="EVT101", event_name="名校申请线上分享会",
        event_type="online", start_time=_dt(10, 19, 0),
    ))
    db.flush()


def seed_complaint_tickets(db) -> None:
    """投诉工单：覆盖满意度、优先级、中文分类、超期工单、同环比（含上一周期数据）。"""
    cats = ["教学", "服务", "顾问", "签证", "院校申请", "生活服务", "教学", "教学", "签证", "财务"]
    prios = ["normal", "urgent", "normal", "severe", "normal", "normal", "urgent", "severe", "normal", "normal"]
    stats = ["resolved", "resolved", "processing", "pending", "resolved", "closed", "processing", "pending", "resolved", "resolved"]
    sats = [5, 4, None, None, 5, 3, None, None, 4, 2]
    handlers = [201, 202, 203, 201, 204, 202, 201, 203, 204, 201]
    close_hours = [6, 20, 0, 0, 30, 50, 0, 0, 12, 72]
    for i in range(10):
        create = _dt(i % 7, 10, 0)  # 落在第1周
        close = create + timedelta(hours=close_hours[i]) if stats[i] in ("resolved", "closed") else None
        db.merge(StudentFeedbackTicket(
            id=1000 + i, ticket_no=f"FB{1000+i}", student_id=301 + (i % 12),
            handler_employee_id=handlers[i], ticket_type="complaint",
            category=cats[i], title=f"{cats[i]}相关投诉{i+1}",
            detail=f"学生反映{cats[i]}环节存在问题，要求尽快处理。",
            priority_level=prios[i], status=stats[i],
            satisfaction_score=sats[i], close_time=close, create_time=create,
        ))
    # 两条人为超期：pending/processing 且创建时间在 72 小时前
    overdue_base = datetime.now() - timedelta(hours=72)
    for j in range(2):
        db.merge(StudentFeedbackTicket(
            id=1100 + j, ticket_no=f"FB{1100+j}", student_id=301 + j,
            handler_employee_id=201, ticket_type="complaint",
            category="签证", title=f"签证超期未处理工单{j+1}",
            detail="签证材料审核长期未推进，已超 48 小时。",
            priority_level="urgent", status="pending" if j == 0 else "processing",
            create_time=overdue_base,
        ))
    # 上一周期（05-25~05-31）：用于同环比对比
    for k in range(6):
        prev_create = datetime(2026, 5, 25, 10, 0, 0) + timedelta(days=k % 7)
        db.merge(StudentFeedbackTicket(
            id=1200 + k, ticket_no=f"FB{1200+k}", student_id=301 + (k % 12),
            handler_employee_id=201, ticket_type="complaint",
            category="教学", title=f"上周期投诉{k+1}",
            detail="上一统计周期的历史投诉，用于同环比对比。",
            priority_level="normal", status="resolved",
            satisfaction_score=4, close_time=prev_create + timedelta(hours=10),
            create_time=prev_create,
        ))


def seed_customer_operation(db) -> None:
    """CRM 线索 + 研判 + 活动报名：覆盖新增/成交/流失、四维画像、研判等级、转化周期。"""
    channels = ["event", "referral", "online_ad", "wechat", "phone"]
    countries = ["美国", "英国", "美国", "澳大利亚", "加拿大", "英国", "美国", "新加坡"]
    programs = ["计算机硕士", "商科硕士", "数据科学硕士", "本科预科", "金融硕士",
                "传媒硕士", "计算机硕士", "工程硕士"]
    budgets = ["30-50万", "50-80万", "50-80万", "20-30万", "80万以上", "30-50万", "50-80万", "20-30万"]
    edus = ["本科", "本科", "硕士", "高中", "本科", "本科", "硕士", "高中"]

    # 本周期新增线索（第1周 06-01~06-07），部门1负责人 201-205
    # 状态分布：new / following / signed（成交）/ lost（流失）
    lead_status = ["signed", "following", "new", "signed", "lost", "following", "new", "lost"]
    lead_owner = [201, 202, 203, 201, 204, 205, 202, 203]
    lost_reasons = [None, None, None, None, "预算不足", None, None, "竞品更优惠"]
    signed_offsets = {0: 4, 3: 3}  # lead 索引 -> 签约相对创建的天数（确保签约日落在统计周期内）
    for i in range(8):
        create = _dt(i % 7, 9, 0)
        signed_time = None
        if lead_status[i] == "signed":
            signed_time = create + timedelta(days=signed_offsets.get(i, 5))
        db.merge(CrmLead(
            id=2000 + i, lead_no=f"LEAD{2000+i}", customer_name=f"客户{i+1}",
            phone=f"138{2000+i:08d}"[:11], status=lead_status[i],
            source_channel=channels[i % len(channels)],
            target_country=countries[i], target_program=programs[i],
            budget_range=budgets[i], education_level=edus[i],
            owner_employee_id=lead_owner[i], lost_reason=lost_reasons[i],
            signed_time=signed_time, create_time=create,
        ))
    db.flush()

    # 研判记录（关联本周期线索），match_level 高/中/低分层
    match_levels = ["high", "medium", "low", "high", "medium", "high"]
    analysis_lead = [2000, 2001, 2002, 2003, 2005, 2006]
    for i in range(6):
        db.merge(CustomerAnalysisRecord(
            id=2100 + i, analysis_no=f"AN{2100+i}", source_type="manual",
            lead_id=analysis_lead[i], target_product="留学申请服务",
            is_target_customer=1 if match_levels[i] == "high" else 0,
            match_score=[92, 75, 48, 88, 70, 95][i], match_level=match_levels[i],
            reason_summary=f"客户背景与目标项目匹配度{match_levels[i]}。",
            status="completed", create_time=_dt(i % 7, 11, 0),
        ))

    # 活动报名（关联线索），含已报名/已参加/已转化
    reg_status = ["registered", "attended", "registered", "attended", "cancelled"]
    reg_lead = [2000, 2001, 2002, 2003, 2004]
    for i in range(5):
        db.merge(EventRegistration(
            id=2200 + i, lead_id=reg_lead[i], event_id=100 if i % 2 == 0 else 101,
            visitor_name=f"客户{i+1}", visitor_phone=f"139{2200+i:08d}"[:11],
            registration_status=reg_status[i], create_time=_dt(i % 7, 15, 0),
        ))

    # 上一周期线索（05-25~05-31）用于同环比
    for k in range(3):
        db.merge(CrmLead(
            id=2300 + k, lead_no=f"LEAD{2300+k}", customer_name=f"上周期客户{k+1}",
            status="new", source_channel="event", owner_employee_id=201,
            target_country="美国", target_program="计算机硕士",
            budget_range="50-80万", education_level="本科",
            create_time=datetime(2026, 5, 26, 9, 0, 0) + timedelta(days=k),
        ))


def seed_employee_reports(db) -> None:
    """员工日报：跨四周、多员工、多状态，含中文风险文本供关键词提取。"""
    # 中文风险文本：刻意复用"客户/签约/资料/沟通/进度"等关键词制造高频主题
    risk_pool = [
        "部分客户长期联系不上，跟进进度受阻",
        "签约资料准备时间紧张，存在延期风险",
        "与院校沟通不畅，材料审核进度滞后",
        "客户预算与项目不匹配，签约存在不确定性",
        "资料翻译时间过长，影响整体进度",
        None, None,  # 部分日报无风险
    ]
    progress_pool = [
        "完成 3 位高意向客户的研判跟进",
        "推进 2 份签约合同的资料准备",
        "组织线上分享会并回访报名客户",
        "完成学生背景评估和选校方案",
        "跟进投诉工单并安抚客户情绪",
        "整理本周线索并更新跟进记录",
        "完成明日活动的场地和物料确认",
    ]
    plan_pool = [
        "继续跟进高意向客户，推动签约",
        "完成合同资料终审并提交",
        "回访活动报名客户，筛选意向",
        "输出选校方案初稿",
        "闭环处理中投诉工单",
    ]
    statuses = ["submitted", "submitted", "submitted", "draft", "archived"]
    # 部门1员工 201-205，跨四周每周工作日提交
    dept1_emps = [201, 202, 203, 204, 205]
    rid = 3000
    for week in range(4):
        for day in range(5):  # 周一到周五
            offset = week * 7 + day
            # 每天 3-5 名员工提交，制造提交率波动和峰谷日
            n_submit = 5 if day in (0, 1) else (3 if day == 2 else 4)
            for e in range(n_submit):
                emp = dept1_emps[e]
                risk = risk_pool[(offset + e) % len(risk_pool)]
                db.merge(EmployeeDailyReport(
                    id=rid, employee_id=emp, department_id=1,
                    report_date=(PERIOD_START + timedelta(days=offset)),
                    raw_content=f"员工{emp}第{week+1}周第{day+1}天工作记录",
                    summary=progress_pool[(offset + e) % len(progress_pool)],
                    key_progress=progress_pool[(offset + e) % len(progress_pool)],
                    risks=risk,
                    tomorrow_plan=plan_pool[(offset + e) % len(plan_pool)] if e % 2 == 0 else None,
                    report_status=statuses[(offset + e) % len(statuses)],
                ))
                rid += 1
    # 部门2 少量日报（覆盖率对比）
    for day in range(3):
        db.merge(EmployeeDailyReport(
            id=rid, employee_id=206, department_id=2,
            report_date=(PERIOD_START + timedelta(days=day)),
            raw_content="部门2日报", summary="部门2进展",
            key_progress="完成部门2客户跟进", report_status="submitted",
        ))
        rid += 1


def seed_psych(db) -> None:
    """心理画像 + 预警：覆盖情绪标签、风险分层、情绪分、摘要、互动趋势、预警状态。"""
    # 学生 301-310 心理画像，情绪标签英文原值（DAO 不翻译，模板层映射中文）
    emotion_tags = ["anxious", "stable", "depressed", "lonely", "stressed",
                    "anxious", "happy", "anxious", "lonely", "stable"]
    risk_levels = ["high", "medium", "critical", "high", "medium",
                   "high", "low", "medium", "high", "low"]
    scores = [42, 68, 25, 38, 55, 45, 82, 60, 35, 75]
    summaries = [
        "近期学业压力大，频繁表达焦虑，需重点关注",
        "情绪整体平稳，适应良好",
        "出现明显低落情绪，社交回避，建议立即干预",
        "表达强烈孤独感，与同学交流少",
        "考试临近压力上升，睡眠质量下降",
        "签证延误引发焦虑，担心入学受影响",
        "状态积极，主动参与社群活动",
        "偶有焦虑，整体可控",
        "跨文化适应困难，想家情绪明显",
        "情绪稳定，学习计划清晰",
    ]
    # 互动时间分布在第1周不同日期，制造互动趋势峰谷
    interaction_days = [0, 1, 1, 2, 2, 2, 3, 4, 5, 6]
    for i in range(10):
        db.merge(StudentPsychProfile(
            id=3500 + i, student_id=301 + i,
            latest_emotion_tag=emotion_tags[i], emotion_score=scores[i],
            risk_level=risk_levels[i],
            last_interaction_time=_dt(interaction_days[i], 9 + (i % 6), 0),
            emotion_summary=summaries[i],
        ))
    db.flush()

    # 心理预警：覆盖 high/critical/medium，pending/processing/resolved 多状态
    alert_specs = [
        (301, "critical", "pending", "情绪分骤降，触发危急预警"),
        (303, "critical", "processing", "持续低落且社交回避，跟进中"),
        (304, "high", "pending", "孤独感强烈，待安排访谈"),
        (301, "high", "resolved", "焦虑预警已完成一对一疏导"),
        (306, "high", "pending", "签证焦虑触发预警"),
        (305, "medium", "resolved", "压力预警已回访"),
        (309, "high", "processing", "跨文化适应预警跟进中"),
    ]
    for j, (sid, risk, status, reason) in enumerate(alert_specs):
        close = _dt(j % 7, 18, 0) if status == "resolved" else None
        db.merge(StudentPsychAlert(
            id=3600 + j, alert_no=f"ALERT{3600+j}", student_id=sid,
            trigger_reason=reason, risk_level=risk, status=status,
            handle_result="已安排心理咨询" if status == "resolved" else None,
            teacher_employee_id=208, close_time=close,
            create_time=_dt(j % 7, 10, 0),
        ))


def purge_report_data(db) -> None:
    """清空报告相关业务表数据（保留表结构与 alembic_version）。

    按外键依赖逆序删除：子表 → lead/student → 维度表。
    """
    # 子表（依赖 lead / student / employee）
    for model in (
        EventRegistration,
        CustomerAnalysisRecord,
        StudentPsychAlert,
        StudentPsychProfile,
        StudentFeedbackTicket,
        EmployeeDailyReport,
        CrmLead,
        EventLecture,
        StudentProfile,
        EmployeeProfile,
    ):
        db.query(model).delete(synchronize_session=False)
    db.flush()


def seed_all(session_factory=None, purge: bool = True) -> None:
    """写入全部展示数据。session_factory 用于测试注入（默认连真实库）。

    purge=True 时先清空报告相关表的旧数据，确保报告输出纯净。
    """
    factory = session_factory or get_session_factory()
    db = factory()
    try:
        if purge:
            purge_report_data(db)
            print("已清空报告相关表旧数据")
        seed_dimensions(db)
        seed_complaint_tickets(db)
        seed_customer_operation(db)
        seed_employee_reports(db)
        seed_psych(db)
        db.commit()
        print("五类报告展示数据全部写入完成（部门1为主展示部门）")
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
