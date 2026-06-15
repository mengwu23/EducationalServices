"""
Comprehensive test script for all 4 features:
1. Student Leave Approval
2. Psychological Care
3. Academic Events
4. Student Feedback Tickets

Tests against the real database (education_service_ai).
"""
import sys
import os
import traceback

# Setup path — add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = 'mysql+pymysql://root:123456@localhost:3306/education_service_ai'
engine = create_engine(DATABASE_URL, pool_size=5)
Session = sessionmaker(bind=engine)

passed = 0
failed = 0
results = []


def run_test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        results.append(f"  [PASS] {name}")
        print(f"  [PASS] {name}")
    except Exception as e:
        failed += 1
        results.append(f"  [FAIL] {name} -- {e}")
        print(f"  [FAIL] {name} -- {e}")
        traceback.print_exc()


# =====================================================
# Module 1: Student Leave Approval
# =====================================================

def test_student_leave():
    from backend.app.services.student_leave_service import StudentLeaveService
    from backend.app.schemas.student_leave_schema import LeaveCreateRequest, LeaveListQuery
    from backend.app.common.enums import LeaveType, LeaveStatus, UserType
    from backend.app.common.pagination import PageQuery
    from backend.app.common.exceptions import (
        NotFoundException, PermissionDeniedException, StateConflictException
    )
    from backend.app.models.student_leave_request import StudentLeaveRequest
    from backend.app.daos.student_leave_dao import StudentLeaveDao

    # 1.1: Student submits leave
    def t1_1():
        db = Session()
        try:
            service = StudentLeaveService(db)
            data = LeaveCreateRequest(
                leave_type=LeaveType.SICK,
                reason="Test leave - cold/fever",
                start_time=datetime.now() + timedelta(days=1),
                end_time=datetime.now() + timedelta(days=1, hours=8),
            )
            result = service.create_leave(
                current_user_id=11, current_user_type=UserType.STUDENT.value, data=data,
            )
            assert result.request_no.startswith("LV"), f"Expected LV prefix: {result.request_no}"
            assert result.status == LeaveStatus.PENDING.value
            assert result.student_name is not None
            print(f"      Created: {result.request_no}, student={result.student_name}")
        finally:
            db.rollback(); db.close()

    # 1.2: Non-student cannot submit
    def t1_2():
        db = Session()
        try:
            service = StudentLeaveService(db)
            data = LeaveCreateRequest(
                leave_type=LeaveType.SICK, reason="Test",
                start_time=datetime.now() + timedelta(days=1),
                end_time=datetime.now() + timedelta(days=1, hours=8),
            )
            try:
                service.create_leave(current_user_id=1, current_user_type=UserType.EMPLOYEE.value, data=data)
                assert False, "Should have raised PermissionDeniedException"
            except PermissionDeniedException as e:
                assert "only student" in str(e.message).lower() or "只有学生" in str(e.message)
        finally:
            db.rollback(); db.close()

    # 1.3: Student views own leaves
    def t1_3():
        db = Session()
        try:
            service = StudentLeaveService(db)
            query = LeaveListQuery(page=1, page_size=10)
            items, total = service.list_my_leaves(
                current_user_id=11, current_user_type=UserType.STUDENT.value, query=query,
            )
            assert total >= 0
            print(f"      Student 11 has {total} leave record(s)")
        finally:
            db.rollback(); db.close()

    # 1.4: Employee views pending list
    def t1_4():
        db = Session()
        try:
            service = StudentLeaveService(db)
            query = PageQuery(page=1, page_size=10)
            items, total = service.list_all_pending(
                current_user_type=UserType.EMPLOYEE.value, query=query,
            )
            assert total >= 0
            print(f"      Pending leaves: {total}")
        finally:
            db.rollback(); db.close()

    # 1.5: Employee approves leave
    def t1_5():
        db = Session()
        try:
            service = StudentLeaveService(db)
            pending = db.query(StudentLeaveRequest).filter(
                StudentLeaveRequest.status == LeaveStatus.PENDING.value
            ).first()
            if pending:
                result = service.approve_leave(
                    current_user_id=1, current_user_type=UserType.EMPLOYEE.value, leave_id=pending.id,
                )
                assert result.status == LeaveStatus.APPROVED.value
                print(f"      Approved: ID={pending.id}, approver={result.approver_name}")
            else:
                print(f"      No pending leave to approve, skip")
        finally:
            db.rollback(); db.close()

    # 1.6: Employee rejects leave
    def t1_6():
        db = Session()
        try:
            service = StudentLeaveService(db)
            pending = db.query(StudentLeaveRequest).filter(
                StudentLeaveRequest.status == LeaveStatus.PENDING.value
            ).first()
            if pending:
                result = service.reject_leave(
                    current_user_id=1, current_user_type=UserType.EMPLOYEE.value,
                    leave_id=pending.id, comment="Insufficient reason",
                )
                assert result.status == LeaveStatus.REJECTED.value
                assert result.approval_comment == "Insufficient reason"
                print(f"      Rejected: ID={pending.id}, comment={result.approval_comment}")
            else:
                print(f"      No pending leave to reject, skip")
        finally:
            db.rollback(); db.close()

    # 1.7: Cannot re-approve already-approved leave
    def t1_7():
        db = Session()
        try:
            service = StudentLeaveService(db)
            approved = db.query(StudentLeaveRequest).filter(
                StudentLeaveRequest.status == LeaveStatus.APPROVED.value
            ).first()
            if approved:
                try:
                    service.approve_leave(
                        current_user_id=1, current_user_type=UserType.EMPLOYEE.value, leave_id=approved.id,
                    )
                    assert False, "Should have raised StateConflictException"
                except StateConflictException as e:
                    assert "pending" in str(e.message).lower() or "待审批" in str(e.message)
                    print(f"      Correctly rejected re-approval: {e.message[:50]}")
            else:
                print(f"      No approved leave to test, skip")
        finally:
            db.rollback(); db.close()

    # 1.8: Student cancels own leave
    def t1_8():
        db = Session()
        try:
            service = StudentLeaveService(db)
            pending = db.query(StudentLeaveRequest).filter(
                StudentLeaveRequest.status == LeaveStatus.PENDING.value,
                StudentLeaveRequest.student_id == 1,
            ).first()
            if pending:
                result = service.cancel_leave(
                    current_user_id=11, current_user_type=UserType.STUDENT.value, leave_id=pending.id,
                )
                assert result.status == LeaveStatus.CANCELLED.value
                print(f"      Cancelled: ID={pending.id}")
            else:
                print(f"      No own pending leave, skip")
        finally:
            db.rollback(); db.close()

    # 1.9: Get leave detail
    def t1_9():
        db = Session()
        try:
            service = StudentLeaveService(db)
            result = service.get_leave_detail(
                current_user_id=1, current_user_type=UserType.ADMIN.value, leave_id=1,
            )
            assert result.id == 1
            assert result.student_name is not None
            print(f"      Detail: #{result.request_no}, student={result.student_name}, status={result.status}")
        finally:
            db.rollback(); db.close()

    # 1.10: Count pending
    def t1_10():
        db = Session()
        try:
            service = StudentLeaveService(db)
            count = service.count_pending(current_user_type=UserType.EMPLOYEE.value)
            assert count >= 0
            print(f"      Pending count: {count}")
        finally:
            db.rollback(); db.close()

    # 1.11: Employee approval history
    def t1_11():
        db = Session()
        try:
            service = StudentLeaveService(db)
            query = PageQuery(page=1, page_size=10)
            items, total = service.list_approval_history(
                current_user_id=1, current_user_type=UserType.EMPLOYEE.value, query=query,
            )
            assert total >= 0
            print(f"      Approval history: {total} record(s)")
        finally:
            db.rollback(); db.close()

    # 1.12: Non-employee cannot view pending
    def t1_12():
        db = Session()
        try:
            service = StudentLeaveService(db)
            query = PageQuery(page=1, page_size=10)
            try:
                service.list_all_pending(current_user_type=UserType.STUDENT.value, query=query)
                assert False, "Should have raised PermissionDeniedException"
            except PermissionDeniedException as e:
                assert "only employee" in str(e.message).lower() or "只有员工" in str(e.message)
        finally:
            db.rollback(); db.close()

    tests = [t1_1, t1_2, t1_3, t1_4, t1_5, t1_6, t1_7, t1_8, t1_9, t1_10, t1_11, t1_12]
    for i, t in enumerate(tests):
        name = f"1.{i+1} {t.__doc__ or t.__name__}"
        run_test(name, t)


# =====================================================
# Module 2: Psychological Care
# =====================================================

def test_student_psych():
    from backend.app.services.student_psych_service import StudentPsychService
    from backend.app.schemas.student_psych_schema import (
        PsychAlertCreateRequest, PsychAlertListQuery,
        PsychProfileListQuery, EmotionUpdateRequest,
    )
    from backend.app.common.enums import PsychRiskLevel, PsychAlertStatus, UserType
    from backend.app.common.pagination import PageQuery
    from backend.app.common.exceptions import (
        NotFoundException, PermissionDeniedException, StateConflictException
    )
    from backend.app.models.student_psych_alert import StudentPsychAlert

    # 2.1: Student views own psych profile
    def t2_1():
        db = Session()
        try:
            service = StudentPsychService(db)
            try:
                result = service.get_my_profile(
                    current_user_id=11, current_user_type=UserType.STUDENT.value,
                )
                assert result.student_name is not None
                print(f"      Profile: {result.student_name}, risk={result.risk_level}")
            except NotFoundException as e:
                print(f"      Skip (no profile): {e.message}")
        finally:
            db.rollback(); db.close()

    # 2.2: Non-student cannot view profile
    def t2_2():
        db = Session()
        try:
            service = StudentPsychService(db)
            try:
                service.get_my_profile(current_user_id=1, current_user_type=UserType.EMPLOYEE.value)
                assert False, "Should have raised PermissionDeniedException"
            except PermissionDeniedException as e:
                assert "只有学生" in str(e.message) or "only student" in str(e.message).lower()
        finally:
            db.rollback(); db.close()

    # 2.3: Student views own alerts
    def t2_3():
        db = Session()
        try:
            service = StudentPsychService(db)
            query = PsychAlertListQuery(page=1, page_size=10)
            items, total = service.list_my_alerts(
                current_user_id=11, current_user_type=UserType.STUDENT.value, query=query,
            )
            assert total >= 0
            print(f"      Alerts: {total} record(s)")
        finally:
            db.rollback(); db.close()

    # 2.4: Employee views all profiles
    def t2_4():
        db = Session()
        try:
            service = StudentPsychService(db)
            query = PsychProfileListQuery(page=1, page_size=10)
            items, total = service.list_all_profiles(
                current_user_type=UserType.EMPLOYEE.value, query=query,
            )
            assert total >= 0
            print(f"      All profiles: {total}")
        finally:
            db.rollback(); db.close()

    # 2.5: Create alert (SKIPPED — writes real data to production DB via db.commit())
    # NOTE: student_psych_service.create_alert() internally calls db.commit(),
    # so the finally-block rollback() cannot undo it. Use a test DB or savepoint.
    # def t2_5():
    #     db = Session()
    #     try:
    #         service = StudentPsychService(db)
    #         data = PsychAlertCreateRequest(
    #             student_id=1, trigger_reason="Test alert - student low mood", risk_level=PsychRiskLevel.HIGH,
    #         )
    #         result = service.create_alert(
    #             current_user_id=1, current_user_type=UserType.EMPLOYEE.value, data=data,
    #         )
    #         assert result.alert_no.startswith("PA")
    #         assert result.status == PsychAlertStatus.PENDING.value
    #         print(f"      Created: {result.alert_no}, risk={result.risk_level}")
    #     finally:
    #         db.rollback(); db.close()

    # 2.6: View pending alerts
    def t2_6():
        db = Session()
        try:
            service = StudentPsychService(db)
            query = PageQuery(page=1, page_size=10)
            items, total = service.list_pending_alerts(
                current_user_type=UserType.EMPLOYEE.value, query=query,
            )
            assert total >= 0
            print(f"      Pending alerts: {total}")
        finally:
            db.rollback(); db.close()

    # 2.7: Count pending alerts
    def t2_7():
        db = Session()
        try:
            service = StudentPsychService(db)
            count = service.count_pending_alerts(current_user_type=UserType.EMPLOYEE.value)
            assert count >= 0
            print(f"      Pending count: {count}")
        finally:
            db.rollback(); db.close()

    # 2.8: Process alert (start handling)
    def t2_8():
        db = Session()
        try:
            service = StudentPsychService(db)
            pending = db.query(StudentPsychAlert).filter(
                StudentPsychAlert.status == PsychAlertStatus.PENDING.value,
                StudentPsychAlert.is_delete == 0,
            ).first()
            if pending:
                result = service.process_alert(
                    current_user_id=1, current_user_type=UserType.EMPLOYEE.value, alert_id=pending.id,
                )
                assert result.status == PsychAlertStatus.PROCESSING.value
                print(f"      Processing: ID={pending.id}")
            else:
                print(f"      No pending alert, skip")
        finally:
            db.rollback(); db.close()

    # 2.9: Resolve alert
    def t2_9():
        db = Session()
        try:
            service = StudentPsychService(db)
            processing = db.query(StudentPsychAlert).filter(
                StudentPsychAlert.status == PsychAlertStatus.PROCESSING.value,
                StudentPsychAlert.is_delete == 0,
            ).first()
            if processing:
                result = service.resolve_alert(
                    current_user_id=1, current_user_type=UserType.EMPLOYEE.value,
                    alert_id=processing.id, handle_result="Counseling completed, student improved",
                )
                assert result.status == PsychAlertStatus.RESOLVED.value
                print(f"      Resolved: ID={processing.id}")
            else:
                print(f"      No processing alert, skip")
        finally:
            db.rollback(); db.close()

    # 2.10: Close alert
    def t2_10():
        db = Session()
        try:
            service = StudentPsychService(db)
            resolved = db.query(StudentPsychAlert).filter(
                StudentPsychAlert.status == PsychAlertStatus.RESOLVED.value,
                StudentPsychAlert.is_delete == 0,
            ).first()
            if resolved:
                result = service.close_alert(
                    current_user_id=1, current_user_type=UserType.EMPLOYEE.value, alert_id=resolved.id,
                )
                assert result.status == PsychAlertStatus.CLOSED.value
                assert result.close_time is not None
                print(f"      Closed: ID={resolved.id}")
            else:
                print(f"      No resolved alert, skip")
        finally:
            db.rollback(); db.close()

    # 2.11: Update emotion
    def t2_11():
        db = Session()
        try:
            service = StudentPsychService(db)
            data = EmotionUpdateRequest(
                emotion_tag="Test-Anxiety", emotion_score=45,
                risk_level=PsychRiskLevel.MEDIUM, summary="Test emotion summary",
            )
            result = service.update_emotion(
                current_user_id=1, current_user_type=UserType.EMPLOYEE.value,
                student_id=1, data=data,
            )
            assert result.emotion_score == 45
            print(f"      Updated: tag={result.latest_emotion_tag}, score={result.emotion_score}")
        finally:
            db.rollback(); db.close()

    # 2.12: Cannot close pending alert directly
    def t2_12():
        db = Session()
        try:
            service = StudentPsychService(db)
            pending = db.query(StudentPsychAlert).filter(
                StudentPsychAlert.status == PsychAlertStatus.PENDING.value,
                StudentPsychAlert.is_delete == 0,
            ).first()
            if pending:
                try:
                    service.close_alert(
                        current_user_id=1, current_user_type=UserType.EMPLOYEE.value, alert_id=pending.id,
                    )
                    assert False, "Should have raised StateConflictException"
                except StateConflictException as e:
                    assert "resolved" in str(e.message).lower() or "已解除" in str(e.message)
                    print(f"      Correctly rejected: {e.message[:50]}")
            else:
                print(f"      No pending alert, skip")
        finally:
            db.rollback(); db.close()

    tests = [t2_1, t2_2, t2_3, t2_4, t2_6, t2_7, t2_8, t2_9, t2_10, t2_11, t2_12]  # t2_5 skipped: writes real DB data
    for i, t in enumerate(tests):
        name = f"2.{i+1} {t.__doc__ or t.__name__}"
        run_test(name, t)


# =====================================================
# Module 3: Academic Events
# =====================================================

def test_academic_event():
    from backend.app.services.academic_event_service import AcademicEventService
    from backend.app.schemas.academic_event_schema import AcademicEventCreate, AcademicEventUpdate
    from backend.app.common.enums import AcademicEventType, AcademicEventStatus
    from backend.app.common.exceptions import NotFoundError, BadRequestError
    from backend.app.models.academic_event import AcademicEvent

    # 3.1: Create academic event
    def t3_1():
        db = Session()
        try:
            data = AcademicEventCreate(
                student_id=1, event_type=AcademicEventType.EXAM,
                title="Test Exam Event", event_desc="Test exam description",
                course_name="Test Course",
                deadline_time=datetime.now() + timedelta(days=14),
            )
            event = AcademicEventService.create_event(db, data)
            assert event.title == "Test Exam Event"
            assert event.status == AcademicEventStatus.ACTIVE.value
            print(f"      Created: ID={event.id}, type={event.event_type}")
        finally:
            db.rollback(); db.close()

    # 3.2: Create public event (no student_id)
    def t3_2():
        db = Session()
        try:
            data = AcademicEventCreate(
                student_id=None, event_type=AcademicEventType.OTHER,
                title="Test Public Event", deadline_time=datetime.now() + timedelta(days=30),
            )
            event = AcademicEventService.create_event(db, data)
            assert event.student_id is None
            print(f"      Public event: ID={event.id}, student_id=None")
        finally:
            db.rollback(); db.close()

    # 3.3: List events
    def t3_3():
        db = Session()
        try:
            items, total, page, size = AcademicEventService.list_events(db, student_id=1, page=1, size=10)
            assert total >= 0
            print(f"      Student 1 events: {total}")
        finally:
            db.rollback(); db.close()

    # 3.4: Filter by type
    def t3_4():
        db = Session()
        try:
            items, total, page, size = AcademicEventService.list_events(db, event_type="exam", page=1, size=10)
            assert total >= 0
            print(f"      Exam events: {total}")
        finally:
            db.rollback(); db.close()

    # 3.5: Keyword search
    def t3_5():
        db = Session()
        try:
            items, total, page, size = AcademicEventService.list_events(db, keyword="paper", page=1, size=10)
            assert total >= 0
            print(f"      Keyword 'paper': {total} result(s)")
        finally:
            db.rollback(); db.close()

    # 3.6: Get detail
    def t3_6():
        db = Session()
        try:
            event = AcademicEventService.get_event(db, 1)
            assert event.id == 1
            print(f"      Detail: ID={event.id}, title={event.title}")
        finally:
            db.rollback(); db.close()

    # 3.7: Get non-existent event
    def t3_7():
        db = Session()
        try:
            try:
                AcademicEventService.get_event(db, 99999)
                assert False, "Should have raised NotFoundError"
            except NotFoundError as e:
                assert "not found" in str(e.detail).lower()
        finally:
            db.rollback(); db.close()

    # 3.8: Update event
    def t3_8():
        db = Session()
        try:
            data = AcademicEventUpdate(title="Updated Title")
            event = AcademicEventService.update_event(db, 1, data)
            assert event.title == "Updated Title"
            print(f"      Updated: ID={event.id}, new title={event.title}")
        finally:
            db.rollback(); db.close()

    # 3.9: Complete event
    def t3_9():
        db = Session()
        try:
            active = db.query(AcademicEvent).filter(
                AcademicEvent.status == AcademicEventStatus.ACTIVE.value
            ).first()
            if active:
                event = AcademicEventService.complete_event(db, active.id)
                assert event.status == AcademicEventStatus.COMPLETED.value
                print(f"      Completed: ID={event.id}")
            else:
                print(f"      No active event, skip")
        finally:
            db.rollback(); db.close()

    # 3.10: Cancel event
    def t3_10():
        db = Session()
        try:
            active = db.query(AcademicEvent).filter(
                AcademicEvent.status == AcademicEventStatus.ACTIVE.value
            ).first()
            if active:
                event = AcademicEventService.cancel_event(db, active.id)
                assert event.status == AcademicEventStatus.CANCELLED.value
                print(f"      Cancelled: ID={event.id}")
            else:
                print(f"      No active event, skip")
        finally:
            db.rollback(); db.close()

    # 3.11: Cannot complete completed event
    def t3_11():
        db = Session()
        try:
            completed = db.query(AcademicEvent).filter(
                AcademicEvent.status == AcademicEventStatus.COMPLETED.value
            ).first()
            if completed:
                try:
                    AcademicEventService.complete_event(db, completed.id)
                    assert False, "Should have raised BadRequestError"
                except BadRequestError as e:
                    assert "completed" in str(e.detail).lower()
                    print(f"      Correctly rejected: {e.detail}")
            else:
                print(f"      No completed event, skip")
        finally:
            db.rollback(); db.close()

    # 3.12: Cannot cancel already-cancelled event
    def t3_12():
        db = Session()
        try:
            cancelled = db.query(AcademicEvent).filter(
                AcademicEvent.status == AcademicEventStatus.CANCELLED.value
            ).first()
            if cancelled:
                try:
                    AcademicEventService.cancel_event(db, cancelled.id)
                    assert False, "Should have raised BadRequestError"
                except BadRequestError as e:
                    assert "already cancelled" in str(e.detail).lower()
                    print(f"      Correctly rejected: {e.detail}")
            else:
                # Create and cancel to test
                data = AcademicEventCreate(
                    student_id=1, event_type=AcademicEventType.OTHER,
                    title="To Cancel", deadline_time=datetime.now() + timedelta(days=7),
                )
                event = AcademicEventService.create_event(db, data)
                AcademicEventService.cancel_event(db, event.id)
                try:
                    AcademicEventService.cancel_event(db, event.id)
                    assert False, "Should have raised BadRequestError"
                except BadRequestError as e:
                    assert "already cancelled" in str(e.detail).lower()
                    print(f"      Correctly rejected double cancel: {e.detail}")
        finally:
            db.rollback(); db.close()

    tests = [t3_1, t3_2, t3_3, t3_4, t3_5, t3_6, t3_7, t3_8, t3_9, t3_10, t3_11, t3_12]
    for i, t in enumerate(tests):
        name = f"3.{i+1} {t.__doc__ or t.__name__}"
        run_test(name, t)


# =====================================================
# Module 4: Student Feedback Tickets
# =====================================================

def test_student_feedback():
    from backend.app.services.student_feedback_ticket_service import StudentFeedbackTicketService
    from backend.app.schemas.student_feedback_ticket_schema import (
        StudentFeedbackTicketCreate, StudentFeedbackTicketUpdate,
        FeedbackAssignRequest, FeedbackResolveRequest, FeedbackCloseRequest,
    )
    from backend.app.common.enums import (
        FeedbackTicketType, FeedbackPriorityLevel, FeedbackTicketStatus,
    )
    from backend.app.common.exceptions import NotFoundError, BadRequestError
    from backend.app.models.student_feedback_ticket import StudentFeedbackTicket

    # 4.1: Create ticket
    def t4_1():
        db = Session()
        try:
            data = StudentFeedbackTicketCreate(
                student_id=1, ticket_type=FeedbackTicketType.COMPLAINT,
                category="Teaching", title="Test Complaint",
                detail="Test complaint content about teaching quality",
                priority_level=FeedbackPriorityLevel.NORMAL,
            )
            ticket = StudentFeedbackTicketService.create_ticket(db, data)
            assert ticket.ticket_no.startswith("FB")
            assert ticket.status == FeedbackTicketStatus.PENDING.value
            print(f"      Created: {ticket.ticket_no}, status={ticket.status}")
        finally:
            db.rollback(); db.close()

    # 4.2: Create urgent ticket
    def t4_2():
        db = Session()
        try:
            data = StudentFeedbackTicketCreate(
                student_id=2, ticket_type=FeedbackTicketType.COMPLAINT,
                category="Service", title="Urgent Complaint",
                detail="Consultant attitude problem, needs immediate handling",
                priority_level=FeedbackPriorityLevel.URGENT,
            )
            ticket = StudentFeedbackTicketService.create_ticket(db, data)
            assert ticket.priority_level == FeedbackPriorityLevel.URGENT.value
            print(f"      Urgent: {ticket.ticket_no}, priority={ticket.priority_level}")
        finally:
            db.rollback(); db.close()

    # 4.3: List tickets
    def t4_3():
        db = Session()
        try:
            items, total, page, size = StudentFeedbackTicketService.list_tickets(db, page=1, size=10)
            assert total >= 0
            print(f"      Total tickets: {total}")
        finally:
            db.rollback(); db.close()

    # 4.4: Filter by student
    def t4_4():
        db = Session()
        try:
            items, total, page, size = StudentFeedbackTicketService.list_tickets(
                db, student_id=1, page=1, size=10,
            )
            assert total >= 0
            print(f"      Student 1 tickets: {total}")
        finally:
            db.rollback(); db.close()

    # 4.5: Get detail
    def t4_5():
        db = Session()
        try:
            ticket = StudentFeedbackTicketService.get_ticket(db, 1)
            assert ticket.id == 1
            print(f"      Detail: #{ticket.ticket_no}, title={ticket.title}")
        finally:
            db.rollback(); db.close()

    # 4.6: Update ticket
    def t4_6():
        db = Session()
        try:
            data = StudentFeedbackTicketUpdate(title="Updated Title", priority_level=FeedbackPriorityLevel.URGENT)
            ticket = StudentFeedbackTicketService.update_ticket(db, 1, data)
            assert ticket.title == "Updated Title"
            print(f"      Updated: {ticket.title}, priority={ticket.priority_level}")
        finally:
            db.rollback(); db.close()

    # 4.7: Assign ticket
    def t4_7():
        db = Session()
        try:
            pending = db.query(StudentFeedbackTicket).filter(
                StudentFeedbackTicket.status == FeedbackTicketStatus.PENDING.value
            ).first()
            if pending:
                data = FeedbackAssignRequest(handler_employee_id=1)
                ticket = StudentFeedbackTicketService.assign_ticket(db, pending.id, data)
                assert ticket.status == FeedbackTicketStatus.PROCESSING.value
                assert ticket.handler_employee_id == 1
                print(f"      Assigned: ID={pending.id}, handler={ticket.handler_employee_id}")
            else:
                print(f"      No pending ticket, skip")
        finally:
            db.rollback(); db.close()

    # 4.8: Resolve ticket
    def t4_8():
        db = Session()
        try:
            processing = db.query(StudentFeedbackTicket).filter(
                StudentFeedbackTicket.status == FeedbackTicketStatus.PROCESSING.value
            ).first()
            if processing:
                data = FeedbackResolveRequest(solution="Issue resolved properly", notify_student=True)
                ticket = StudentFeedbackTicketService.resolve_ticket(db, processing.id, data)
                assert ticket.status == FeedbackTicketStatus.RESOLVED.value
                print(f"      Resolved: ID={processing.id}")
            else:
                print(f"      No processing ticket, skip")
        finally:
            db.rollback(); db.close()

    # 4.9: Close ticket
    def t4_9():
        db = Session()
        try:
            resolved = db.query(StudentFeedbackTicket).filter(
                StudentFeedbackTicket.status == FeedbackTicketStatus.RESOLVED.value
            ).first()
            if resolved:
                data = FeedbackCloseRequest(satisfaction_score=4)
                ticket = StudentFeedbackTicketService.close_ticket(db, resolved.id, data)
                assert ticket.status == FeedbackTicketStatus.CLOSED.value
                assert ticket.satisfaction_score == 4
                assert ticket.close_time is not None
                print(f"      Closed: ID={resolved.id}, satisfaction={ticket.satisfaction_score}")
            else:
                print(f"      No resolved ticket, skip")
        finally:
            db.rollback(); db.close()

    # 4.10: Cannot close non-resolved ticket
    def t4_10():
        db = Session()
        try:
            pending = db.query(StudentFeedbackTicket).filter(
                StudentFeedbackTicket.status == FeedbackTicketStatus.PENDING.value
            ).first()
            if pending:
                data = FeedbackCloseRequest()
                try:
                    StudentFeedbackTicketService.close_ticket(db, pending.id, data)
                    assert False, "Should have raised BadRequestError"
                except BadRequestError as e:
                    assert "Only resolved" in str(e.detail)
                    print(f"      Correctly rejected: {e.detail}")
            else:
                print(f"      No pending ticket, skip")
        finally:
            db.rollback(); db.close()

    # 4.11: Get non-existent ticket
    def t4_11():
        db = Session()
        try:
            try:
                StudentFeedbackTicketService.get_ticket(db, 99999)
                assert False, "Should have raised NotFoundError"
            except NotFoundError as e:
                assert "not found" in str(e.detail).lower()
        finally:
            db.rollback(); db.close()

    # 4.12: Filter by status + category
    def t4_12():
        db = Session()
        try:
            items, total, page, size = StudentFeedbackTicketService.list_tickets(
                db, status="pending", category="Teaching", page=1, size=10,
            )
            assert total >= 0
            print(f"      Pending+Teaching: {total}")
        finally:
            db.rollback(); db.close()

    tests = [t4_1, t4_2, t4_3, t4_4, t4_5, t4_6, t4_7, t4_8, t4_9, t4_10, t4_11, t4_12]
    for i, t in enumerate(tests):
        name = f"4.{i+1} {t.__doc__ or t.__name__}"
        run_test(name, t)


# =====================================================
# Main runner
# =====================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Education Services - Full Feature Test")
    print("=" * 60)

    print("\n[Module 1] Student Leave Approval")
    print("-" * 50)
    test_student_leave()

    print("\n[Module 2] Psychological Care")
    print("-" * 50)
    test_student_psych()

    print("\n[Module 3] Academic Events")
    print("-" * 50)
    test_academic_event()

    print("\n[Module 4] Student Feedback Tickets")
    print("-" * 50)
    test_student_feedback()

    print("\n" + "=" * 60)
    print(f"  Results: {passed} PASSED, {failed} FAILED")
    print("=" * 60)

    if failed > 0:
        print("\nFailure details:")
        for r in results:
            if "FAIL" in r:
                print(r)
        sys.exit(1)
    else:
        print("\n[OK] All tests passed!")
        sys.exit(0)
