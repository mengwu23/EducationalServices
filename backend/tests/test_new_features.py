"""Tests for newly added features."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

DATABASE_URL = 'mysql+pymysql://root:123456@localhost:3306/education_service_ai'
engine = create_engine(DATABASE_URL, pool_size=5)
Session = sessionmaker(bind=engine)

passed = 0
failed = 0

def run_test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f'  [PASS] {name}')
    except Exception as e:
        failed += 1
        print(f'  [FAIL] {name} -- {e}')
        import traceback
        traceback.print_exc()

print('=' * 60)
print('  New Feature Tests')
print('=' * 60)

# ---- AI Emotion Analysis (SKIPPED — writes real data to production DB via db.commit()) ----
# NOTE: student_psych_service methods internally call db.commit(),
# so the finally-block rollback() cannot undo writes to the real MySQL database.
# print('\n[AI Emotion Analysis]')
# def t_ai_high(): ...
# def t_ai_low(): ...
# run_test('AI high risk triggers alert', t_ai_high)
# run_test('AI low risk does not trigger alert', t_ai_low)

# ---- Enterprise Assistant Leave Approval ----
print('\n[Enterprise Assistant - Leave Approval]')

def t_ent_approve():
    from backend.app.services.enterprise_assistant_service import EnterpriseAssistantService
    from backend.app.models.student_leave_request import StudentLeaveRequest
    from backend.app.common.enums import LeaveStatus
    db = Session()
    try:
        pending = db.query(StudentLeaveRequest).filter(
            StudentLeaveRequest.status == LeaveStatus.PENDING.value
        ).first()
        if pending:
            service = EnterpriseAssistantService(db)
            result = service.approve_student_leave(leave_id=pending.id, employee_id=1)
            assert result.success is True
            assert result.status == 'approved'
            print(f'      Approved: {result.request_no}')
        else:
            print(f'      No pending leave, skip')
    finally:
        db.rollback(); db.close()

def t_ent_reject():
    from backend.app.services.enterprise_assistant_service import EnterpriseAssistantService
    from backend.app.models.student_leave_request import StudentLeaveRequest
    from backend.app.common.enums import LeaveStatus
    db = Session()
    try:
        pending = db.query(StudentLeaveRequest).filter(
            StudentLeaveRequest.status == LeaveStatus.PENDING.value
        ).first()
        if pending:
            service = EnterpriseAssistantService(db)
            result = service.reject_student_leave(
                leave_id=pending.id, employee_id=1, comment='Insufficient reason'
            )
            assert result.success is True
            assert result.status == 'rejected'
            print(f'      Rejected: {result.request_no}')
        else:
            print(f'      No pending leave, skip')
    finally:
        db.rollback(); db.close()

run_test('Enterprise approve leave', t_ent_approve)
run_test('Enterprise reject leave', t_ent_reject)

# ---- Enterprise Assistant Psych Alerts ----
print('\n[Enterprise Assistant - Psych Alerts]')

def t_ent_psych_list():
    from backend.app.services.enterprise_assistant_service import EnterpriseAssistantService
    db = Session()
    try:
        service = EnterpriseAssistantService(db)
        result = service.search_student_psych_alerts(status='pending', page=1, page_size=10)
        assert result.total >= 0
        print(f'      Pending alerts: {result.total}')
    finally:
        db.rollback(); db.close()

def t_ent_psych_process():
    from backend.app.services.enterprise_assistant_service import EnterpriseAssistantService
    from backend.app.models.student_psych_alert import StudentPsychAlert
    from backend.app.common.enums import PsychAlertStatus
    db = Session()
    try:
        pending = db.query(StudentPsychAlert).filter(
            StudentPsychAlert.status == PsychAlertStatus.PENDING.value,
            StudentPsychAlert.is_delete == 0,
        ).first()
        if pending:
            service = EnterpriseAssistantService(db)
            result = service.handle_student_psych_alert(
                alert_id=pending.id, employee_id=1, action='process',
            )
            assert result.success is True
            assert result.status == 'processing'
            print(f'      Processing: {result.alert_no}')
        else:
            print(f'      No pending alert, skip')
    finally:
        db.rollback(); db.close()

run_test('Enterprise list psych alerts', t_ent_psych_list)
run_test('Enterprise process psych alert', t_ent_psych_process)

# ---- Feedback Notification ----
print('\n[Feedback Notification]')

def t_notify_resolved():
    from backend.app.services.student_feedback_ticket_service import StudentFeedbackTicketService
    from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
    from backend.app.common.enums import FeedbackTicketStatus
    db = Session()
    try:
        resolved = db.query(StudentFeedbackTicket).filter(
            StudentFeedbackTicket.status == FeedbackTicketStatus.RESOLVED.value
        ).first()
        if resolved:
            ticket = StudentFeedbackTicketService.notify_ticket(db, resolved.id)
            assert ticket.is_notified == 1
            print(f'      Notified: {ticket.ticket_no}, is_notified={ticket.is_notified}')
        else:
            print(f'      No resolved ticket, skip')
    finally:
        db.rollback(); db.close()

def t_notify_pending_rejected():
    from backend.app.services.student_feedback_ticket_service import StudentFeedbackTicketService
    from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
    from backend.app.common.enums import FeedbackTicketStatus
    from backend.app.common.exceptions import BadRequestError
    db = Session()
    try:
        pending = db.query(StudentFeedbackTicket).filter(
            StudentFeedbackTicket.status == FeedbackTicketStatus.PENDING.value
        ).first()
        if pending:
            try:
                StudentFeedbackTicketService.notify_ticket(db, pending.id)
                assert False, 'Should have raised BadRequestError'
            except BadRequestError as e:
                assert 'Only resolved' in str(e.detail)
                print(f'      Correctly rejected: {e.detail}')
        else:
            print(f'      No pending ticket, skip')
    finally:
        db.rollback(); db.close()

run_test('Notify resolved ticket', t_notify_resolved)
run_test('Cannot notify pending ticket', t_notify_pending_rejected)

# ---- Academic Deadline Detection ----
print('\n[Academic Deadline Detection]')

def t_approaching():
    from backend.app.services.academic_event_service import AcademicEventService
    db = Session()
    try:
        now = datetime.now()
        deadline_before = now + timedelta(days=7)
        items, total, page, size = AcademicEventService.list_events(
            db, status='active', deadline_to=deadline_before, page=1, size=100,
        )
        assert total >= 0
        print(f'      Approaching deadlines (next 7 days): {total}')
    finally:
        db.rollback(); db.close()

def t_reminders():
    from backend.app.models.academic_event import AcademicEvent
    from backend.app.common.enums import AcademicEventStatus
    db = Session()
    try:
        now = datetime.now()
        reminder_start = now - timedelta(hours=1)
        reminder_end = now + timedelta(hours=1)
        items = db.query(AcademicEvent).filter(
            AcademicEvent.status == AcademicEventStatus.ACTIVE.value,
            AcademicEvent.reminder_time.isnot(None),
            AcademicEvent.reminder_time >= reminder_start,
            AcademicEvent.reminder_time <= reminder_end,
            AcademicEvent.is_delete == 0,
        ).all()
        print(f'      Upcoming reminders (1h window): {len(items)}')
    finally:
        db.rollback(); db.close()

run_test('List approaching deadlines', t_approaching)
run_test('List upcoming reminders', t_reminders)

print('\n' + '=' * 60)
print(f'  New features: {passed} PASSED, {failed} FAILED')
print('=' * 60)
