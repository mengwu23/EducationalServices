"""报告 DAO 上游增强字段单元测试（方案 B 组合聚类 / 方案 D 学期日历）。

使用独立的内存 SQLite 会话，构造针对性数据，不依赖共享 conftest seed。
"""

from datetime import date, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.common.enums import ReportType
from backend.app.daos.report_dao import ReportDAO
from backend.app.database import Base
import backend.app.models  # noqa: F401  注册全部 ORM 表
from backend.app.models.academic_event import AcademicEvent
from backend.app.models.crm_lead import CrmLead
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.student_profile import StudentProfile
from backend.app.models.student_psych_profile import StudentPsychProfile


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(
        EmployeeProfile(
            id=1, user_id=2, department_id=1,
            employee_no="E1", employee_name="顾问", role_code="service",
        )
    )
    db.flush()
    yield db
    db.close()
    Base.metadata.drop_all(engine)


def _add_lead(db, lead_id, country, program, budget):
    db.add(
        CrmLead(
            id=lead_id, lead_no=f"L{lead_id}", customer_name=f"客户{lead_id}",
            status="new", owner_employee_id=1,
            target_country=country, target_program=program, budget_range=budget,
            create_time=datetime(2026, 6, 2),
        )
    )


def test_cluster_breakdown_groups_by_combined_dimensions(session):
    # 两条"美国+计算机硕士+50-80万"，一条"英国+商科+20-30万"
    _add_lead(session, 1, "美国", "计算机硕士", "50-80万")
    _add_lead(session, 2, "美国", "计算机硕士", "50-80万")
    _add_lead(session, 3, "英国", "商科", "20-30万")
    session.commit()

    result = ReportDAO(session).query_report_source_data(
        ReportType.CUSTOMER_OPERATION, date(2026, 6, 1), date(2026, 6, 7), 1, None
    )
    clusters = result["cluster_breakdown"]
    assert clusters, "应返回组合聚类客群"
    # 按人数降序，最高频组合在首位
    top = clusters[0]
    assert top["count"] == 2
    assert top["target_country"] == "美国"
    assert top["target_program"] == "计算机硕士"
    assert top["budget_range"] == "50-80万"
    assert top["label"] == "美国+计算机硕士+50-80万"


def test_cluster_breakdown_caps_at_five(session):
    for i in range(1, 9):
        _add_lead(session, i, f"国家{i}", f"项目{i}", f"预算{i}")
    session.commit()
    result = ReportDAO(session).query_report_source_data(
        ReportType.CUSTOMER_OPERATION, date(2026, 6, 1), date(2026, 6, 7), 1, None
    )
    assert len(result["cluster_breakdown"]) <= 5


def test_period_hint_from_exam_events(session):
    db = session
    db.add_all([
        StudentProfile(
            id=1, user_id=3, counselor_employee_id=1, teacher_employee_id=1,
            student_no="S1", student_name="学生1",
        ),
        StudentPsychProfile(
            id=1, student_id=1, latest_emotion_tag="anxious", emotion_score=40,
            risk_level="high", last_interaction_time=datetime(2026, 6, 2),
        ),
        AcademicEvent(
            id=1, student_id=None, event_type="exam", title="期中考试周",
            deadline_time=datetime(2026, 6, 4), status="active",
        ),
        AcademicEvent(
            id=2, student_id=None, event_type="exam", title="期末考试",
            deadline_time=datetime(2026, 6, 5), status="active",
        ),
    ])
    db.commit()
    result = ReportDAO(db).query_report_source_data(
        ReportType.STUDENT_PSYCH_WEEKLY, date(2026, 6, 1), date(2026, 6, 7), 1, None
    )
    assert result["period_hint"] is not None
    assert "考试" in result["period_hint"]


def test_period_hint_from_deadline_events(session):
    db = session
    db.add_all([
        StudentProfile(
            id=1, user_id=3, counselor_employee_id=1, teacher_employee_id=1,
            student_no="S1", student_name="学生1",
        ),
        StudentPsychProfile(
            id=1, student_id=1, latest_emotion_tag="stressed", emotion_score=45,
            risk_level="medium", last_interaction_time=datetime(2026, 6, 2),
        ),
        AcademicEvent(
            id=1, student_id=None, event_type="paper_deadline", title="论文截止",
            deadline_time=datetime(2026, 6, 4), status="active",
        ),
    ])
    db.commit()
    result = ReportDAO(db).query_report_source_data(
        ReportType.STUDENT_PSYCH_WEEKLY, date(2026, 6, 1), date(2026, 6, 7), 1, None
    )
    assert result["period_hint"] is not None
    assert "截止" in result["period_hint"] or "冲刺" in result["period_hint"]


def test_period_hint_none_without_events(session):
    db = session
    db.add_all([
        StudentProfile(
            id=1, user_id=3, counselor_employee_id=1, teacher_employee_id=1,
            student_no="S1", student_name="学生1",
        ),
        StudentPsychProfile(
            id=1, student_id=1, latest_emotion_tag="stable", emotion_score=70,
            risk_level="low", last_interaction_time=datetime(2026, 6, 2),
        ),
    ])
    db.commit()
    result = ReportDAO(db).query_report_source_data(
        ReportType.STUDENT_PSYCH_WEEKLY, date(2026, 6, 1), date(2026, 6, 7), 1, None
    )
    # 无学业事件时回退给渲染层（DAO 返回 None）
    assert result["period_hint"] is None


def test_period_hint_ignores_student_specific_events(session):
    """仅统计公共事件（student_id 为空），个人事件不参与周期判断。"""
    db = session
    db.add_all([
        StudentProfile(
            id=1, user_id=3, counselor_employee_id=1, teacher_employee_id=1,
            student_no="S1", student_name="学生1",
        ),
        StudentPsychProfile(
            id=1, student_id=1, latest_emotion_tag="stable", emotion_score=70,
            risk_level="low", last_interaction_time=datetime(2026, 6, 2),
        ),
        AcademicEvent(
            id=1, student_id=1, event_type="exam", title="个人补考",
            deadline_time=datetime(2026, 6, 4), status="active",
        ),
    ])
    db.commit()
    result = ReportDAO(db).query_report_source_data(
        ReportType.STUDENT_PSYCH_WEEKLY, date(2026, 6, 1), date(2026, 6, 7), 1, None
    )
    assert result["period_hint"] is None
