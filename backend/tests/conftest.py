from collections.abc import Generator
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.db.session import get_db
from app.main import create_app
from app.models import (
    CrmLead,
    CustomerAnalysisRecord,
    EmployeeProfile,
    EventLecture,
    EventRegistration,
    StudentFeedbackTicket,
    StudentProfile,
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
            SysDepartment(id=1, department_name="咨询一部"),
            EmployeeProfile(
                id=1,
                user_id=2,
                department_id=1,
                employee_no="EMP001",
                employee_name="张老师",
                role_code="service",
            ),
            StudentProfile(
                id=1,
                user_id=3,
                counselor_employee_id=1,
                student_no="STU001",
                student_name="李同学",
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
        ]
    )
    db.commit()
