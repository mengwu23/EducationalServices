from collections.abc import Generator
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import (
    CrmLead,
    CustomerAnalysisRecord,
    EmployeeProfile,
    EventRegistration,
    StudentFeedbackTicket,
    StudentProfile,
    SysDepartment,
    SysUser,
)


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
            SysUser(id=1, username="admin", role="admin"),
            SysUser(id=2, username="employee", role="employee"),
            SysUser(id=3, username="student", role="student"),
            SysDepartment(id=1, name="咨询一部"),
            EmployeeProfile(id=1, user_id=2, department_id=1, name="张老师"),
            StudentProfile(id=1, user_id=3, advisor_employee_id=1, name="李同学"),
        ]
    )
    db.flush()
    db.add_all(
        [
            StudentFeedbackTicket(
                id=1,
                student_id=1,
                handler_employee_id=1,
                category="service",
                status="open",
                content="宿舍维修慢",
                create_time=datetime(2026, 6, 2, 10, 0, 0),
            ),
            StudentFeedbackTicket(
                id=2,
                student_id=1,
                handler_employee_id=1,
                category="course",
                status="closed",
                content="课程时间冲突",
                create_time=datetime(2026, 6, 3, 10, 0, 0),
            ),
            CrmLead(
                id=1,
                name="王家长",
                status="new",
                source="event",
                owner_user_id=2,
                department_id=1,
                create_time=datetime(2026, 6, 2, 9, 0, 0),
            ),
            CustomerAnalysisRecord(
                id=1,
                lead_id=1,
                result_level="high",
                created_by=2,
                create_time=datetime(2026, 6, 3, 9, 0, 0),
            ),
            EventRegistration(
                id=1,
                lead_id=1,
                event_id=100,
                status="registered",
                register_date=date(2026, 6, 4),
            ),
        ]
    )
    db.commit()
