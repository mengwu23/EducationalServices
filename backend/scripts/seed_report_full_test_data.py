"""写入报告模块全量验收测试数据。"""

from datetime import date, datetime

from backend.app.db.session import SessionLocal
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
from scripts.seed_report_mysql import seed_report_data


def seed_full_report_data() -> None:
    """补充覆盖五类智能报告的验收数据，支持重复执行。"""
    seed_report_data()
    db = SessionLocal()
    try:
        db.merge(SysDepartment(id=10, department_name="Full Acceptance Consulting"))
        db.merge(SysDepartment(id=20, department_name="Full Acceptance Archive"))

        users = [
            SysUser(id=101, username="full_admin", real_name="Full Admin", user_type="admin"),
            SysUser(id=102, username="full_employee_a", real_name="Full Employee A", user_type="employee"),
            SysUser(id=103, username="full_employee_b", real_name="Full Employee B", user_type="employee"),
            SysUser(id=104, username="full_employee_other", real_name="Full Employee Other", user_type="employee"),
            SysUser(id=105, username="full_student_a", real_name="Full Student A", user_type="student"),
            SysUser(id=106, username="full_student_b", real_name="Full Student B", user_type="student"),
            SysUser(id=107, username="full_student_c", real_name="Full Student C", user_type="student"),
        ]
        for user in users:
            db.merge(user)
        db.flush()

        employees = [
            EmployeeProfile(id=101, user_id=102, department_id=10, employee_no="FULL-EMP-101", employee_name="Full Employee A", role_code="sales"),
            EmployeeProfile(id=102, user_id=103, department_id=10, employee_no="FULL-EMP-102", employee_name="Full Employee B", role_code="service"),
            EmployeeProfile(id=103, user_id=104, department_id=20, employee_no="FULL-EMP-103", employee_name="Full Employee Other", role_code="teacher"),
        ]
        for employee in employees:
            db.merge(employee)
        db.flush()

        students = [
            StudentProfile(
                id=101,
                user_id=105,
                student_no="FULL-STU-101",
                student_name="Full Student A",
                counselor_employee_id=101,
                teacher_employee_id=102,
                target_country="英国",
                target_program="商科硕士",
            ),
            StudentProfile(
                id=102,
                user_id=106,
                student_no="FULL-STU-102",
                student_name="Full Student B",
                counselor_employee_id=101,
                teacher_employee_id=102,
                target_country="澳大利亚",
                target_program="本科预科",
            ),
            StudentProfile(
                id=103,
                user_id=107,
                student_no="FULL-STU-103",
                student_name="Full Student C",
                counselor_employee_id=103,
                teacher_employee_id=103,
                target_country="加拿大",
                target_program="高中转学",
            ),
        ]
        for student in students:
            db.merge(student)
        db.flush()

        db.merge(
            EventLecture(
                id=1001,
                event_no="FULL-EVT-1001",
                event_name="2026 留学规划公开课",
                event_type="online",
                topic="申请时间线与背景提升",
                speaker="顾问 A",
                start_time=datetime(2026, 6, 4, 19, 0, 0),
                end_time=datetime(2026, 6, 4, 20, 30, 0),
                online_url="https://example.test/live/full-1001",
                max_participants=200,
                current_participants=56,
            )
        )

        tickets = [
            StudentFeedbackTicket(
                id=1001,
                ticket_no="FULL-FB-1001",
                student_id=101,
                handler_employee_id=102,
                category="教学",
                title="课程节奏偏快",
                detail="学生反馈近期课程节奏偏快，希望增加课后答疑。",
                priority_level="urgent",
                status="pending",
                create_time=datetime(2026, 6, 1, 10, 0, 0),
            ),
            StudentFeedbackTicket(
                id=1002,
                ticket_no="FULL-FB-1002",
                student_id=102,
                handler_employee_id=102,
                category="服务",
                title="材料反馈延迟",
                detail="家长反馈申请材料反馈时间较长，需要客服解释进度。",
                priority_level="normal",
                status="processing",
                create_time=datetime(2026, 6, 3, 11, 30, 0),
            ),
            StudentFeedbackTicket(
                id=1003,
                ticket_no="FULL-FB-1003",
                student_id=101,
                handler_employee_id=102,
                category="签证",
                title="签证材料已处理",
                detail="签证材料疑问已由顾问处理完成。",
                priority_level="normal",
                status="resolved",
                solution="已补充材料清单并预约一对一说明。",
                satisfaction_score=5,
                close_time=datetime(2026, 6, 6, 15, 0, 0),
                create_time=datetime(2026, 6, 5, 9, 15, 0),
            ),
            StudentFeedbackTicket(
                id=1004,
                ticket_no="FULL-FB-1004",
                student_id=103,
                handler_employee_id=103,
                category="生活服务",
                title="跨部门测试工单",
                detail="该工单属于其他部门，不应进入部门 10 的统计。",
                status="closed",
                create_time=datetime(2026, 6, 2, 14, 0, 0),
            ),
            StudentFeedbackTicket(
                id=1005,
                ticket_no="FULL-FB-1005",
                student_id=101,
                handler_employee_id=102,
                category="财务",
                title="逻辑删除工单",
                detail="该记录用于验证 is_delete=1 不进入统计。",
                status="pending",
                is_delete=1,
                create_time=datetime(2026, 6, 2, 14, 30, 0),
            ),
        ]
        for ticket in tickets:
            db.merge(ticket)

        leads = [
            CrmLead(
                id=1001,
                lead_no="FULL-LEAD-1001",
                customer_name="王同学家长",
                phone="13900001001",
                source_channel="公开课",
                education_level="本科",
                target_country="英国",
                target_program="硕士申请",
                budget_range="30-50万",
                status="new",
                owner_employee_id=101,
                create_time=datetime(2026, 6, 1, 9, 0, 0),
            ),
            CrmLead(
                id=1002,
                lead_no="FULL-LEAD-1002",
                customer_name="李同学家长",
                phone="13900001002",
                source_channel="转介绍",
                education_level="高中",
                target_country="澳大利亚",
                target_program="本科预科",
                budget_range="20-40万",
                status="following",
                owner_employee_id=101,
                create_time=datetime(2026, 6, 3, 10, 0, 0),
            ),
            CrmLead(
                id=1003,
                lead_no="FULL-LEAD-1003",
                customer_name="其他部门线索",
                status="signed",
                owner_employee_id=103,
                create_time=datetime(2026, 6, 4, 10, 0, 0),
            ),
            CrmLead(
                id=1004,
                lead_no="FULL-LEAD-1004",
                customer_name="逻辑删除线索",
                status="new",
                owner_employee_id=101,
                is_delete=1,
                create_time=datetime(2026, 6, 5, 10, 0, 0),
            ),
        ]
        for lead in leads:
            db.merge(lead)
        db.flush()

        analysis_records = [
            CustomerAnalysisRecord(
                id=1001,
                analysis_no="FULL-AN-1001",
                source_type="manual",
                lead_id=1001,
                is_target_customer=1,
                match_score=88,
                match_level="high",
                reason_summary="预算、国家和专业目标匹配度高。",
                suggestion="建议安排顾问深度咨询。",
                status="completed",
                submitter_user_id=102,
                create_time=datetime(2026, 6, 2, 10, 0, 0),
            ),
            CustomerAnalysisRecord(
                id=1002,
                analysis_no="FULL-AN-1002",
                source_type="manual",
                lead_id=1002,
                is_target_customer=1,
                match_score=72,
                match_level="medium",
                reason_summary="目标明确但预算需进一步确认。",
                suggestion="建议补充预算与成绩材料。",
                status="completed",
                submitter_user_id=102,
                create_time=datetime(2026, 6, 4, 10, 0, 0),
            ),
        ]
        for record in analysis_records:
            db.merge(record)

        registrations = [
            EventRegistration(
                id=1001,
                event_id=1001,
                lead_id=1001,
                visitor_name="王同学家长",
                visitor_phone="13900001001",
                registration_status="attended",
                create_time=datetime(2026, 6, 4, 19, 0, 0),
            ),
            EventRegistration(
                id=1002,
                event_id=1001,
                lead_id=1002,
                visitor_name="李同学家长",
                visitor_phone="13900001002",
                registration_status="registered",
                create_time=datetime(2026, 6, 4, 19, 5, 0),
            ),
        ]
        for registration in registrations:
            db.merge(registration)

        daily_reports = [
            EmployeeDailyReport(id=1001, employee_id=101, department_id=10, report_date=date(2026, 6, 1), raw_content="客户跟进 8 人，公开课邀约 3 人。", summary="客户跟进进展正常。", key_progress="完成公开课邀约。", risks="部分客户预算未确认。", tomorrow_plan="继续跟进预算信息。", report_status="submitted"),
            EmployeeDailyReport(id=1002, employee_id=102, department_id=10, report_date=date(2026, 6, 1), raw_content="处理投诉工单 2 条。", summary="投诉处理推进中。", key_progress="完成签证材料说明。", tomorrow_plan="回访家长满意度。", report_status="submitted"),
            EmployeeDailyReport(id=1003, employee_id=101, department_id=10, report_date=date(2026, 6, 2), raw_content="客户研判 2 条。", summary="客户质量较高。", key_progress="输出客户研判建议。", risks="一名客户预算不确定。", tomorrow_plan="安排深度咨询。", report_status="archived"),
            EmployeeDailyReport(id=1004, employee_id=102, department_id=10, report_date=date(2026, 6, 2), raw_content="草稿日报。", report_status="draft"),
            EmployeeDailyReport(id=1005, employee_id=103, department_id=20, report_date=date(2026, 6, 2), raw_content="其他部门日报。", report_status="submitted"),
            EmployeeDailyReport(id=1006, employee_id=101, department_id=10, report_date=date(2026, 6, 3), raw_content="逻辑删除日报。", report_status="submitted", risks="不应统计", is_delete=1),
        ]
        for daily_report in daily_reports:
            db.merge(daily_report)

        psych_profiles = [
            StudentPsychProfile(id=101, student_id=101, latest_emotion_tag="焦虑", emotion_score=42, risk_level="high", last_interaction_time=datetime(2026, 6, 2, 12, 0, 0), emotion_summary="申请节点临近，焦虑明显。"),
            StudentPsychProfile(id=102, student_id=102, latest_emotion_tag="稳定", emotion_score=76, risk_level="low", last_interaction_time=datetime(2026, 6, 3, 12, 0, 0), emotion_summary="学习和沟通状态稳定。"),
            StudentPsychProfile(id=103, student_id=103, latest_emotion_tag="低落", emotion_score=35, risk_level="medium", last_interaction_time=datetime(2026, 6, 4, 12, 0, 0), emotion_summary="其他部门学生，不应进入部门 10 统计。"),
        ]
        for profile in psych_profiles:
            db.merge(profile)

        psych_alerts = [
            StudentPsychAlert(id=1001, alert_no="FULL-ALERT-1001", student_id=101, trigger_reason="连续两次情绪分低于 45。", risk_level="high", status="pending", teacher_employee_id=102, create_time=datetime(2026, 6, 2, 13, 0, 0)),
            StudentPsychAlert(id=1002, alert_no="FULL-ALERT-1002", student_id=102, trigger_reason="阶段性压力升高。", risk_level="medium", status="resolved", teacher_employee_id=102, handle_result="已完成老师回访。", create_time=datetime(2026, 6, 5, 13, 0, 0)),
            StudentPsychAlert(id=1003, alert_no="FULL-ALERT-1003", student_id=101, trigger_reason="逻辑删除预警。", risk_level="critical", status="processing", teacher_employee_id=102, is_delete=1, create_time=datetime(2026, 6, 6, 13, 0, 0)),
        ]
        for alert in psych_alerts:
            db.merge(alert)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_full_report_data()
    print("report full acceptance seed data ready")
