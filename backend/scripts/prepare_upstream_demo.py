"""本轮四方案的上游展示数据准备脚本（一次性）。

在已有 rich demo 数据基础上，补齐本轮新增方案所需的上游数据：
- 方案D：插入 academic_event 公共学业事件（考试周），使 period_hint 走真实日历
- 方案A：对周期内工单调真实 DeepSeek 分类器，写回 category(英文键) + content_summary 根因
- 方案C：对周期内心理画像 emotion_summary 文本调真实 DeepSeek 识别器，
         写回 latest_emotion_tag（含 cultural_conflict）/emotion_score/risk_level

用法（项目根目录，.env 已配 NL2SQL_LLM_API_KEY）：
    python -m backend.scripts.prepare_upstream_demo
幂等：academic_event 先按 title 去重；AI 打标可重复执行（覆盖写回）。
"""

from datetime import date, datetime

from sqlalchemy import select

from backend.app.database import get_session_factory
from backend.app.models.academic_event import AcademicEvent
from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
from backend.app.models.student_psych_profile import StudentPsychProfile
from backend.app.services.emotion_recognition_service import EmotionRecognitionService
from backend.app.services.ticket_classifier_service import TicketClassifierService

PERIOD_START = date(2026, 6, 1)
PERIOD_END = date(2026, 6, 7)

# 方案D：公共学业事件（student_id 为空），落在统计周期内
ACADEMIC_EVENTS = [
    ("exam", "2026春季学期期中考试周", datetime(2026, 6, 3, 9, 0)),
    ("exam", "雅思/托福语言冲刺考试", datetime(2026, 6, 5, 14, 0)),
    ("paper_deadline", "学期论文提交截止", datetime(2026, 6, 6, 23, 0)),
]


def seed_academic_events(db) -> int:
    """插入公共学业事件（按 title 去重）。"""
    existing = set(db.scalars(select(AcademicEvent.title)).all())
    added = 0
    for event_type, title, deadline in ACADEMIC_EVENTS:
        if title in existing:
            continue
        db.add(AcademicEvent(
            student_id=None, event_type=event_type, title=title,
            event_desc="留学周期公共节点（展示用）", deadline_time=deadline,
            status="active",
        ))
        added += 1
    db.flush()
    return added


def tag_tickets(db, classifier: TicketClassifierService) -> int:
    """对周期内工单做 AI 分类 + 根因打标（覆盖写回）。"""
    tickets = db.scalars(
        select(StudentFeedbackTicket).where(
            StudentFeedbackTicket.is_delete == 0,
        )
    ).all()
    tagged = 0
    for t in tickets:
        if not (PERIOD_START <= t.create_time.date() <= PERIOD_END):
            continue
        result = classifier.classify(t.title, t.detail)
        if not result:
            continue
        t.category = result["category"]
        if result.get("content_summary"):
            t.content_summary = result["content_summary"]
        tagged += 1
        print(f"  工单 {t.id}: category={t.category} | 根因={t.content_summary}")
    db.flush()
    return tagged


def tag_psych(db, recognizer: EmotionRecognitionService) -> int:
    """对周期内心理画像的 emotion_summary 文本做 AI 情绪识别（覆盖写回）。"""
    profiles = db.scalars(
        select(StudentPsychProfile).where(
            StudentPsychProfile.is_delete == 0,
            StudentPsychProfile.emotion_summary.is_not(None),
        )
    ).all()
    tagged = 0
    for p in profiles:
        if p.last_interaction_time is None:
            continue
        if not (PERIOD_START <= p.last_interaction_time.date() <= PERIOD_END):
            continue
        result = recognizer.recognize(p.emotion_summary)
        if not result:
            continue
        p.latest_emotion_tag = result["emotion_tag"]
        if result.get("emotion_score") is not None:
            p.emotion_score = result["emotion_score"]
        p.risk_level = result["risk_level"]
        tagged += 1
        print(f"  画像 {p.id}(stu {p.student_id}): tag={p.latest_emotion_tag} "
              f"score={p.emotion_score} risk={p.risk_level}")
    db.flush()
    return tagged


def main() -> None:
    classifier = TicketClassifierService()
    recognizer = EmotionRecognitionService()
    if not classifier.is_available():
        raise SystemExit("未配置 NL2SQL_LLM_API_KEY，无法真跑 AI 打标")

    db = get_session_factory()()
    try:
        n_events = seed_academic_events(db)
        print(f"方案D：新增 {n_events} 条公共学业事件")
        print("方案A：工单 AI 分类 + 根因打标")
        n_tickets = tag_tickets(db, classifier)
        print("方案C：心理画像 AI 情绪识别")
        n_psych = tag_psych(db, recognizer)
        db.commit()
        print(f"\n完成：events+{n_events} tickets打标 {n_tickets} 画像打标 {n_psych}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
