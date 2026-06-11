import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import date, datetime, timedelta
from app.db.session import SessionLocal
from app.models.crm_lead import CrmLead
from app.models.customer_analysis_record import CustomerAnalysisRecord
from app.models.employee_daily_report import EmployeeDailyReport
from app.models.employee_profile import EmployeeProfile
from app.models.event_registration import EventRegistration
from app.models.student_feedback_ticket import StudentFeedbackTicket
from app.models.student_profile import StudentProfile
from app.models.student_psych_alert import StudentPsychAlert
from app.models.student_psych_profile import StudentPsychProfile

random.seed(42)
TODAY = date.today()
THIS_WEEK_START = TODAY - timedelta(days=TODAY.weekday())

def week_dates(offset_weeks=0):
    monday = THIS_WEEK_START - timedelta(weeks=offset_weeks)
    return monday, monday + timedelta(days=6)

def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))

db = SessionLocal()
DEPT_IDS = [10, 20]
EMP_IDS = [101, 102, 103]
STUDENT_IDS = [101, 102, 103, 104, 105, 106]
STUDENT_IDS = [1, 2, 3, 101, 102, 103]
sources = ["官网", "转介绍", "活动引流", "广告投放", "展会获客", "异业合作"]
statuses = ["新线索", "已联系", "已分析", "已谈判", "已成交", "已流失"]
budgets = ["5-10万", "10-20万", "20-30万", "30-50万", "50万+"]
match_levels = ["高意向", "中意向", "低意向", "无意向"]
categories = ["服务态度投诉", "办理时效投诉", "专业能力投诉", "费用争议", "签证办理", "院校申请", "生活服务"]
ticket_types = ["投诉", "建议", "咨询"]
emotion_tags = ["焦虑", "孤独", "适应困难", "学业压力", "人际困扰", "文化冲突", "稳定", "积极"]

lead_id_seq = 300
for week_offset, count in [(0, 25), (1, 18)]:
    for i in range(count):
        lead_id_seq += 1
        monday, friday = week_dates(week_offset)
        dt = rand_date(monday, friday)
        db.merge(CrmLead(
            id=lead_id_seq, lead_no=f"LEAD-{lead_id_seq:06d}", customer_name=f"客户{lead_id_seq}",
            phone=f"138{lead_id_seq:05d}", source_channel=random.choice(sources),
            status=random.choice(statuses), owner_employee_id=random.choice(EMP_IDS),
            budget_range=random.choice(budgets),
            target_country=random.choice(["美国","英国","加拿大","澳大利亚","新加坡"]),
            create_time=datetime(dt.year, dt.month, dt.day, random.randint(9,18),0,0), is_delete=0, update_time=datetime.now()))
print(f"CRM leads: {lead_id_seq-300} inserted")

analysis_id = 200
for i in range(20):
    analysis_id += 1
    monday, friday = week_dates(0 if i < 13 else 1)
    dt = rand_date(monday, friday)
    db.merge(CustomerAnalysisRecord(
        id=analysis_id, analysis_no=f"ANAL-{analysis_id:06d}", lead_id=random.randint(301, lead_id_seq),
        match_level=random.choice(match_levels), reason_summary=random.choice([
            "学生背景优秀，留学意愿强烈", "语言成绩待达标，需跟进", "预算有限，需推荐性价比方案",
            "目标不清晰，需规划咨询", "对院校排名有要求，需匹配项目"]),
        target_product=random.choice(["硕士申请","本科申请","语言培训","背景提升"]),
        status="已完成", create_time=datetime(dt.year, dt.month, dt.day, random.randint(9,18),0,0),
        is_delete=0, update_time=datetime.now()))
print(f"Analysis: 20 inserted")

event_id = 150
for i in range(12):
    event_id += 1
    monday, friday = week_dates(0 if i < 8 else 1)
    dt = rand_date(monday, friday)
    db.merge(EventRegistration(
        id=event_id, event_id=100+random.randint(0,5), lead_id=random.randint(301, lead_id_seq),
        registration_status=random.choice(["已报名","已参加","已转化"]),
        visitor_name=f"访客{event_id}", visitor_phone=f"139{event_id:05d}",
        create_time=datetime(dt.year, dt.month, dt.day, random.randint(9,18),0,0),
        is_delete=0, update_time=datetime.now()))
print(f"Event registrations: 12 inserted")

ticket_id = 150
for i in range(20):
    ticket_id += 1
    monday, friday = week_dates(0 if i < 14 else 1)
    dt = rand_date(monday, friday)
    cat = random.choice(categories)
    ttype = "投诉" if "投诉" in cat else random.choice(ticket_types)
    status = random.choice(["pending","processing","resolved"])
    dt_dt = datetime(dt.year, dt.month, dt.day, random.randint(9, 18), 0, 0)
    close_dt = dt_dt + timedelta(hours=random.randint(1, 72)) if status == "resolved" else None
    db.merge(StudentFeedbackTicket(
        id=ticket_id, ticket_no=f"TKT-{ticket_id:06d}", student_id=random.choice(STUDENT_IDS),
        handler_employee_id=random.choice(EMP_IDS), category=cat, ticket_type=ttype, status=status,
        title=f"{cat}相关{ttype}", content_summary=random.choice([
            "客户不满服务流程","材料提交后超时未反馈","顾问回答不准确影响信任",
            "费用明细不清晰","签证进度缓慢","院校推荐不匹配","住宿安排有问题"]),
        priority_level=random.choice(["高","中","低"]),
        create_time=datetime(dt.year, dt.month, dt.day, random.randint(9,18),0,0),
        close_time=datetime(close_dt.year, close_dt.month, close_dt.day, close_dt.hour, 0, 0) if close_dt else None,
        is_delete=0, update_time=datetime.now()))
print(f"Tickets: 20 inserted")

for i, sid in enumerate(STUDENT_IDS):
    monday, friday = week_dates(1)
    dt = rand_date(monday, friday)
    db.merge(StudentPsychProfile(
        id=100+i, student_id=sid, latest_emotion_tag=random.choice(emotion_tags),
        emotion_score=random.randint(30,95), risk_level=["low","medium","high","low","medium","low"][i],
        emotion_summary=random.choice(["考试季压力大","跨文化适应良好","轻度孤独感","学业滞后焦虑","生活适应良好","与室友沟通问题"]),
        create_time=datetime(dt.year, dt.month, dt.day, random.randint(9, 18), 0, 0),
        last_interaction_time=datetime(dt.year, dt.month, dt.day, random.randint(9, 18), 0, 0),
        is_delete=0, update_time=datetime.now()))
print(f"Psych profiles: 6 merged")

for i in range(10):
    monday, friday = week_dates(0 if i < 7 else 1)
    dt = rand_date(monday, friday)
    db.merge(StudentPsychAlert(
        id=100+i, alert_no=f"ALERT-{100+i:06d}", student_id=random.choice(STUDENT_IDS),
        trigger_reason=random.choice(["连续低分触发预警","主动申请心理咨询","教师反馈课堂异常","社交参与显著减少","家长反馈沟通减少"]),
        risk_level=random.choice(["low","medium","high"]),
        status=random.choice(["pending","processing","resolved"]),
        teacher_employee_id=random.choice(EMP_IDS),
        create_time=datetime(dt.year, dt.month, dt.day, random.randint(9,18),0,0),
        is_delete=0, update_time=datetime.now()))
print(f"Psych alerts: 10 inserted")

for week_offset in [0, 1]:
    monday, friday = week_dates(week_offset)
    for day_offset in range(5):
        rd = monday + timedelta(days=day_offset)
        for emp_id in EMP_IDS[:2]:
            db.merge(EmployeeDailyReport(
                employee_id=emp_id, department_id=10, report_date=rd,
                raw_content=random.choice(["今日跟进客户...", "完成日常工作...", "处理投诉并回访..."]),
                summary=random.choice([f"完成咨询{random.randint(2,5)}组",f"签约{random.randint(1,3)}组",f"完成方案{random.randint(2,4)}份"]),
                key_progress=random.choice([f"跟进高意向客户{random.randint(3,5)}组",f"完成院校匹配方案",f"回访完成10组"]),
                risks=random.choice(["预算问题推进缓慢","材料补充中","人手不足",""]),
                tomorrow_plan=random.choice([f"预约面谈{random.randint(2,4)}组",f"整理材料{random.randint(3,5)}份","跟进签证进度",""]),
                report_status=random.choice(["submitted","submitted","submitted","draft"]),
                is_delete=0, update_time=datetime.now()))
print("Daily reports: added 2 employees x 10 days")

db.commit()
db.close()
print("\nDONE - Enhanced seed data ready")
