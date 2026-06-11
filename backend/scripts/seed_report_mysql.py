"""写入智能报告 MySQL 联调最小数据集。"""

from datetime import date, datetime

from app.db.session import SessionLocal
from app.models import (
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


def seed_report_data() -> None:
    db = SessionLocal()
    try:
        db.merge(SysDepartment(id=1, department_name="Consulting Department"))
        db.merge(SysDepartment(id=2, department_name="Other Department"))
        db.merge(SysUser(id=1, username="admin", real_name="Admin", user_type="admin"))
        db.merge(SysUser(id=2, username="employee", real_name="Employee One", user_type="employee"))
        db.merge(SysUser(id=3, username="student", real_name="Student One", user_type="student"))
        db.merge(SysUser(id=4, username="employee2", real_name="Employee Two", user_type="employee"))
        db.merge(SysUser(id=5, username="student2", real_name="Student Two", user_type="student"))
        db.merge(SysUser(id=6, username="employee3", real_name="Employee Three", user_type="employee"))
        db.merge(SysUser(id=7, username="student3", real_name="Student Three", user_type="student"))
        db.flush()

        db.merge(
            EmployeeProfile(
                id=1,
                user_id=2,
                department_id=1,
                employee_no="EMP001",
                employee_name="Employee One",
                role_code="service",
            )
        )
        db.merge(
            EmployeeProfile(
                id=2,
                user_id=4,
                department_id=1,
                employee_no="EMP002",
                employee_name="Employee Two",
                role_code="teacher",
            )
        )
        db.merge(
            EmployeeProfile(
                id=3,
                user_id=6,
                department_id=2,
                employee_no="EMP003",
                employee_name="Employee Three",
                role_code="service",
            )
        )
        db.flush()

        db.merge(
            StudentProfile(
                id=1,
                user_id=3,
                counselor_employee_id=1,
                teacher_employee_id=1,
                student_no="STU001",
                student_name="Student One",
            )
        )
        db.merge(
            StudentProfile(
                id=2,
                user_id=5,
                counselor_employee_id=2,
                teacher_employee_id=2,
                student_no="STU002",
                student_name="Student Two",
            )
        )
        db.merge(
            StudentProfile(
                id=3,
                user_id=7,
                counselor_employee_id=1,
                teacher_employee_id=1,
                student_no="STU003",
                student_name="Student Three",
            )
        )
        db.merge(
            EventLecture(
                id=100,
                event_no="EVT001",
                event_name="Study Abroad Consulting Lecture",
                event_type="offline",
                start_time=datetime(2026, 6, 4, 9, 0, 0),
            )
        )
        db.flush()

        db.merge(
            StudentFeedbackTicket(
                id=1,
                ticket_no="FB001",
                student_id=1,
                handler_employee_id=1,
                category="service",
                title="Dorm repair",
                detail="Dorm repair request",
                status="open",
                create_time=datetime(2026, 6, 2, 10, 0, 0),
            )
        )
        db.merge(
            StudentFeedbackTicket(
                id=2,
                ticket_no="FB002",
                student_id=1,
                handler_employee_id=1,
                category="course",
                title="Course schedule conflict",
                detail="Course schedule conflict",
                status="closed",
                create_time=datetime(2026, 6, 3, 10, 0, 0),
            )
        )
        db.merge(
            CrmLead(
                id=1,
                lead_no="LEAD001",
                customer_name="Parent Wang",
                status="new",
                source_channel="event",
                owner_employee_id=1,
                create_time=datetime(2026, 6, 2, 9, 0, 0),
            )
        )
        db.flush()

        db.merge(
            CustomerAnalysisRecord(
                id=1,
                analysis_no="AN001",
                source_type="manual",
                lead_id=1,
                create_time=datetime(2026, 6, 3, 9, 0, 0),
            )
        )
        db.merge(
            EventRegistration(
                id=1,
                lead_id=1,
                event_id=100,
                visitor_name="Parent Wang",
                visitor_phone="13800000000",
                registration_status="registered",
                create_time=datetime(2026, 6, 4, 9, 0, 0),
            )
        )
        db.merge(
            EmployeeDailyReport(
                id=1,
                employee_id=1,
                department_id=1,
                report_date=date(2026, 6, 2),
                raw_content="daily report 1",
                summary="summary 1",
                key_progress="progress 1",
                risks="risk 1",
                tomorrow_plan="plan 1",
                report_status="submitted",
            )
        )
        db.merge(
            EmployeeDailyReport(
                id=2,
                employee_id=2,
                department_id=1,
                report_date=date(2026, 6, 2),
                raw_content="daily report 2",
                summary="summary 2",
                key_progress="progress 2",
                tomorrow_plan="plan 2",
                report_status="draft",
            )
        )
        db.merge(
            EmployeeDailyReport(
                id=3,
                employee_id=1,
                department_id=1,
                report_date=date(2026, 6, 3),
                raw_content="daily report 3",
                summary="summary 3",
                key_progress="progress 3",
                risks="risk 3",
                report_status="archived",
            )
        )
        db.merge(
            EmployeeDailyReport(
                id=4,
                employee_id=3,
                department_id=2,
                report_date=date(2026, 6, 2),
                raw_content="other department daily report",
                report_status="submitted",
            )
        )
        db.merge(
            EmployeeDailyReport(
                id=5,
                employee_id=2,
                department_id=1,
                report_date=date(2026, 6, 3),
                raw_content="deleted daily report",
                risks="deleted risk",
                report_status="submitted",
                is_delete=1,
            )
        )
        db.merge(
            StudentPsychProfile(
                id=1,
                student_id=1,
                latest_emotion_tag="anxious",
                emotion_score=40,
                risk_level="high",
                last_interaction_time=datetime(2026, 6, 2, 9, 0, 0),
                emotion_summary="needs attention",
            )
        )
        db.merge(
            StudentPsychProfile(
                id=2,
                student_id=2,
                latest_emotion_tag="stable",
                emotion_score=70,
                risk_level="medium",
                last_interaction_time=datetime(2026, 6, 3, 9, 0, 0),
                emotion_summary="stable",
            )
        )
        db.merge(
            StudentPsychProfile(
                id=3,
                student_id=3,
                latest_emotion_tag="critical",
                emotion_score=10,
                risk_level="critical",
                last_interaction_time=datetime(2026, 6, 4, 9, 0, 0),
                emotion_summary="deleted profile",
                is_delete=1,
            )
        )
        db.merge(
            StudentPsychAlert(
                id=1,
                alert_no="ALERT001",
                student_id=1,
                trigger_reason="risk high",
                risk_level="high",
                status="pending",
                teacher_employee_id=1,
                create_time=datetime(2026, 6, 2, 10, 0, 0),
            )
        )
        db.merge(
            StudentPsychAlert(
                id=2,
                alert_no="ALERT002",
                student_id=2,
                trigger_reason="risk medium",
                risk_level="medium",
                status="resolved",
                teacher_employee_id=2,
                create_time=datetime(2026, 6, 4, 10, 0, 0),
            )
        )
        db.merge(
            StudentPsychAlert(
                id=3,
                alert_no="ALERT003",
                student_id=1,
                trigger_reason="deleted alert",
                risk_level="critical",
                status="processing",
                teacher_employee_id=1,
                create_time=datetime(2026, 6, 5, 10, 0, 0),
                is_delete=1,
            )
        )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_report_data()
    print("report mysql seed data ready")
