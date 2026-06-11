"""方案 A / C 服务层集成测试：工单 AI 打标 与 学生情绪打卡。

使用独立内存会话（仅播种必要 FK 行，工单/画像走自增主键），
通过注入假分类器/识别器验证 AI 打标写回逻辑。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.common.enums import UserType
from backend.app.common.exceptions import PermissionDeniedException, ValidationErrorException
from backend.app.database import Base
import backend.app.models  # noqa: F401  注册全部 ORM 表
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.student_profile import StudentProfile
from backend.app.models.sys_user import SysUser
from backend.app.schemas.student_feedback_ticket_schema import StudentFeedbackTicketCreate
from backend.app.services.emotion_recognition_service import EmotionRecognitionService
from backend.app.services.student_feedback_ticket_service import StudentFeedbackTicketService
from backend.app.services.student_psych_service import StudentPsychService
from backend.app.services.ticket_classifier_service import TicketClassifierService


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add_all([
        SysUser(id=2, username="emp", real_name="员工", user_type="employee"),
        SysUser(id=3, username="stu", real_name="学生", user_type="student"),
        EmployeeProfile(
            id=1, user_id=2, department_id=1,
            employee_no="E1", employee_name="员工", role_code="service",
        ),
        StudentProfile(
            id=1, user_id=3, counselor_employee_id=1, teacher_employee_id=1,
            student_no="S1", student_name="学生",
        ),
    ])
    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(engine)


class FakeLlm:
    def __init__(self, available=True, result=None):
        self._available = available
        self._result = result or {}

    def is_available(self):
        return self._available

    def complete_json(self, *a, **k):
        return self._result


# ----------------------- 方案 A：工单 AI 打标 -----------------------

def test_create_ticket_keeps_manual_category_but_fills_summary(session, monkeypatch):
    """人工已填 category 时不覆盖，但补全空的 content_summary（根因）。"""
    fake = TicketClassifierService(
        FakeLlm(result={"category": "visa", "root_cause": "签证流程复杂"})
    )
    monkeypatch.setattr(
        "backend.app.services.student_feedback_ticket_service.TicketClassifierService",
        lambda: fake,
    )
    payload = StudentFeedbackTicketCreate(
        student_id=1, category="course", title="课程问题", detail="老师讲得太快跟不上"
    )
    ticket = StudentFeedbackTicketService.create_ticket(session, payload)
    assert ticket.category == "course"  # 人工值保留
    assert ticket.content_summary == "签证流程复杂"  # 根因补全


def test_create_ticket_autofills_category_when_empty(session, monkeypatch):
    fake = TicketClassifierService(
        FakeLlm(result={"category": "visa", "root_cause": "材料缺失"})
    )
    monkeypatch.setattr(
        "backend.app.services.student_feedback_ticket_service.TicketClassifierService",
        lambda: fake,
    )
    payload = StudentFeedbackTicketCreate(
        student_id=1, title="签证求助", detail="签证迟迟办不下来"
    )
    ticket = StudentFeedbackTicketService.create_ticket(session, payload)
    assert ticket.category == "visa"
    assert ticket.content_summary == "材料缺失"


def test_create_ticket_unaffected_when_llm_unavailable(session, monkeypatch):
    fake = TicketClassifierService(FakeLlm(available=False))
    monkeypatch.setattr(
        "backend.app.services.student_feedback_ticket_service.TicketClassifierService",
        lambda: fake,
    )
    payload = StudentFeedbackTicketCreate(
        student_id=1, title="建议", detail="希望增加自习室"
    )
    ticket = StudentFeedbackTicketService.create_ticket(session, payload)
    assert ticket.id is not None
    assert ticket.content_summary is None


def test_classify_ticket_force_overrides_category(session, monkeypatch):
    monkeypatch.setattr(
        "backend.app.services.student_feedback_ticket_service.TicketClassifierService",
        lambda: TicketClassifierService(FakeLlm(available=False)),
    )
    payload = StudentFeedbackTicketCreate(
        student_id=1, category="course", title="签证", detail="签证问题"
    )
    ticket = StudentFeedbackTicketService.create_ticket(session, payload)
    assert ticket.category == "course"

    # 独立重做打标，强制覆盖
    fake = TicketClassifierService(
        FakeLlm(result={"category": "visa", "root_cause": "签证延误"})
    )
    updated = StudentFeedbackTicketService.classify_ticket(session, ticket.id, fake)
    assert updated.category == "visa"
    assert updated.content_summary == "签证延误"


# ----------------------- 方案 C：学生情绪打卡 -----------------------

def test_emotion_checkin_updates_profile_via_ai(session):
    recognizer = EmotionRecognitionService(
        FakeLlm(result={
            "emotion_tag": "cultural_conflict",
            "emotion_score": 35,
            "summary": "海外文化适应困难，感到孤立",
        })
    )
    service = StudentPsychService(session)
    result = service.emotion_checkin(
        current_user_id=3,
        current_user_type=UserType.STUDENT.value,
        content="周围都是外国同学，上课也听不太懂，很难融入",
        recognizer=recognizer,
    )
    assert result.latest_emotion_tag == "cultural_conflict"
    assert result.emotion_score == 35
    assert result.risk_level == "high"


def test_emotion_checkin_rejects_non_student(session):
    recognizer = EmotionRecognitionService(FakeLlm(result={"emotion_tag": "stable"}))
    service = StudentPsychService(session)
    with pytest.raises(PermissionDeniedException):
        service.emotion_checkin(
            current_user_id=2,
            current_user_type=UserType.EMPLOYEE.value,
            content="x",
            recognizer=recognizer,
        )


def test_emotion_checkin_errors_when_ai_unavailable(session):
    recognizer = EmotionRecognitionService(FakeLlm(available=False))
    service = StudentPsychService(session)
    with pytest.raises(ValidationErrorException):
        service.emotion_checkin(
            current_user_id=3,
            current_user_type=UserType.STUDENT.value,
            content="今天心情不好",
            recognizer=recognizer,
        )
