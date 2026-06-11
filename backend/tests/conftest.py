from collections.abc import Generator
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.db.session import get_db
from backend.app.main import create_app
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


@compiles(LONGTEXT, "sqlite")
def compile_longtext_for_sqlite(_type, compiler, **kw):
    return "TEXT"


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = TestingSessionLocal()
    seed_report_data(db)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def seed_report_data(db: Session) -> None:
    db.add_all(
        [
            SysUser(id=1, username="admin", real_name="管理员", user_type="admin"),
            SysUser(id=2, username="employee", real_name="张老师", user_type="employee"),
            SysUser(id=3, username="student", real_name="李同学", user_type="student"),
            SysUser(id=4, username="employee2", real_name="employee2", user_type="employee"),
            SysUser(id=5, username="student2", real_name="student2", user_type="student"),
            SysUser(id=6, username="employee3", real_name="employee3", user_type="employee"),
            SysUser(id=7, username="student3", real_name="student3", user_type="student"),
            SysDepartment(id=1, department_name="咨询一部"),
            SysDepartment(id=2, department_name="Other Department"),
            EmployeeProfile(
                id=1,
                user_id=2,
                department_id=1,
                employee_no="EMP001",
                employee_name="张老师",
                role_code="service",
            ),
            EmployeeProfile(
                id=2,
                user_id=4,
                department_id=1,
                employee_no="EMP002",
                employee_name="employee2",
                role_code="teacher",
            ),
            EmployeeProfile(
                id=3,
                user_id=6,
                department_id=2,
                employee_no="EMP003",
                employee_name="employee3",
                role_code="service",
            ),
            StudentProfile(
                id=1,
                user_id=3,
                counselor_employee_id=1,
                teacher_employee_id=1,
                student_no="STU001",
                student_name="李同学",
            ),
            StudentProfile(
                id=2,
                user_id=5,
                counselor_employee_id=2,
                teacher_employee_id=2,
                student_no="STU002",
                student_name="student2",
            ),
            StudentProfile(
                id=3,
                user_id=7,
                counselor_employee_id=1,
                teacher_employee_id=1,
                student_no="STU003",
                student_name="student3",
            ),
            EventLecture(
                id=100,
                event_no="EVT001",
                event_name="留学咨询讲座",
                event_type="offline",
                start_time=datetime(2026, 6, 4, 9, 0, 0),
            ),
        ]
    )
    db.flush()
    db.add_all(
        [
            StudentFeedbackTicket(
                id=1,
                ticket_no="FB001",
                student_id=1,
                handler_employee_id=1,
                category="service",
                title="宿舍维修",
                detail="宿舍维修慢",
                status="open",
                create_time=datetime(2026, 6, 2, 10, 0, 0),
            ),
            StudentFeedbackTicket(
                id=2,
                ticket_no="FB002",
                student_id=1,
                handler_employee_id=1,
                category="course",
                title="课程时间冲突",
                detail="课程时间冲突",
                status="closed",
                create_time=datetime(2026, 6, 3, 10, 0, 0),
            ),
            CrmLead(
                id=1,
                lead_no="LEAD001",
                customer_name="王家长",
                status="new",
                source_channel="event",
                owner_employee_id=1,
                create_time=datetime(2026, 6, 2, 9, 0, 0),
            ),
            CustomerAnalysisRecord(
                id=1,
                analysis_no="AN001",
                source_type="manual",
                lead_id=1,
                create_time=datetime(2026, 6, 3, 9, 0, 0),
            ),
            EventRegistration(
                id=1,
                lead_id=1,
                event_id=100,
                visitor_name="王家长",
                visitor_phone="13800000000",
                registration_status="registered",
                create_time=datetime(2026, 6, 4, 9, 0, 0),
            ),
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
            ),
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
            ),
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
            ),
            EmployeeDailyReport(
                id=4,
                employee_id=3,
                department_id=2,
                report_date=date(2026, 6, 2),
                raw_content="other department daily report",
                report_status="submitted",
            ),
            EmployeeDailyReport(
                id=5,
                employee_id=2,
                department_id=1,
                report_date=date(2026, 6, 3),
                raw_content="deleted daily report",
                risks="deleted risk",
                report_status="submitted",
                is_delete=1,
            ),
            StudentPsychProfile(
                id=1,
                student_id=1,
                latest_emotion_tag="anxious",
                emotion_score=40,
                risk_level="high",
                last_interaction_time=datetime(2026, 6, 2, 9, 0, 0),
                emotion_summary="needs attention",
            ),
            StudentPsychProfile(
                id=2,
                student_id=2,
                latest_emotion_tag="stable",
                emotion_score=70,
                risk_level="medium",
                last_interaction_time=datetime(2026, 6, 3, 9, 0, 0),
                emotion_summary="stable",
            ),
            StudentPsychProfile(
                id=3,
                student_id=3,
                latest_emotion_tag="critical",
                emotion_score=10,
                risk_level="critical",
                last_interaction_time=datetime(2026, 6, 4, 9, 0, 0),
                emotion_summary="deleted profile",
                is_delete=1,
            ),
            StudentPsychAlert(
                id=1,
                alert_no="ALERT001",
                student_id=1,
                trigger_reason="risk high",
                risk_level="high",
                status="pending",
                teacher_employee_id=1,
                create_time=datetime(2026, 6, 2, 10, 0, 0),
            ),
            StudentPsychAlert(
                id=2,
                alert_no="ALERT002",
                student_id=2,
                trigger_reason="risk medium",
                risk_level="medium",
                status="resolved",
                teacher_employee_id=2,
                create_time=datetime(2026, 6, 4, 10, 0, 0),
            ),
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
            ),
        ]
    )
    db.commit()
