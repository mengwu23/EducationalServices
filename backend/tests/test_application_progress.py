"""
Comprehensive test for Application Progress Tracking.
"""
import sys, os, traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

DATABASE_URL = 'mysql+pymysql://root:123456@localhost:3306/education_service_ai'
Session = sessionmaker(bind=create_engine(DATABASE_URL, pool_size=5))

passed = 0; failed = 0

def run_test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f'  [PASS] {name}')
    except Exception as e:
        failed += 1
        print(f'  [FAIL] {name} -- {e}')
        traceback.print_exc()

print('=' * 60)
print('  Application Progress Tracking - Full Test')
print('=' * 60)

from backend.app.services.application_progress_service import ApplicationProgressService
from backend.app.schemas.application_progress_schema import (
    ProgressCreateRequest, ProgressUpdateRequest, PROGRESS_STAGES, PROGRESS_STATUSES,
)

# ── Scene 1: Essay Review ──
print('\n[Scene 1] Essay Review')

def t1_1():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        r = svc.create_progress(ProgressCreateRequest(
            student_id=2, progress_stage='essay', progress_status='processing',
            progress_desc='Personal statement draft submitted, awaiting advisor review',
            school_name='New York University', target_country='USA',
            handler_employee_id=1,
            expected_finish_time=datetime.now() + timedelta(days=10),
        ))
        assert r.progress_stage == 'essay'
        assert r.progress_stage_label == '文书审核'
        assert r.student_name is not None and r.handler_name is not None
        print(f'      Created: {r.student_name} - {r.progress_stage_label} - {r.progress_status_label}')
        print(f'      School: {r.school_name}, Handler: {r.handler_name}')
    finally: db.rollback(); db.close()

def t1_2():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        items, total = svc.list_my_progress(student_user_id=12, progress_stage='essay', page=1, page_size=20)
        essay = [i for i in items if i.progress_stage == 'essay']
        print(f'      Student 12 has {len(essay)} essay record(s)')
        for i in essay:
            print(f'        - [{i.progress_status_label}] {i.progress_desc or "(no desc)"}')
    finally: db.rollback(); db.close()

def t1_3():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        items, _ = svc.list_my_progress(student_user_id=12, progress_stage='essay', page=1, page_size=20)
        essay = [i for i in items if i.progress_stage == 'essay' and i.progress_status != 'completed']
        if essay:
            r = svc.update_progress(essay[0].id, ProgressUpdateRequest(
                progress_status='completed',
                progress_desc='Personal statement approved by advisor',
            ))
            assert r.progress_status == 'completed'
            print(f'      Updated: {r.progress_stage_label} -> {r.progress_status_label}')
        else:
            print(f'      No in-progress essay to update, skip')
    finally: db.rollback(); db.close()

run_test('1.1 Create essay progress', t1_1)
run_test('1.2 Student queries essay progress', t1_2)
run_test('1.3 Update essay to completed', t1_3)

# ── Scene 2: School Application ──
print('\n[Scene 2] School Application')

def t2_1():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        r = svc.create_progress(ProgressCreateRequest(
            student_id=1, progress_stage='school_apply', progress_status='processing',
            progress_desc='Submitted to Harvard, Yale, Stanford - awaiting responses',
            school_name='Harvard University', target_country='USA',
            handler_employee_id=2,
            expected_finish_time=datetime.now() + timedelta(days=30),
        ))
        assert r.progress_stage_label == '院校申请'
        print(f'      Created: {r.student_name} - {r.progress_stage_label}')
        print(f'      Target: {r.school_name}, {r.target_country}')
    finally: db.rollback(); db.close()

def t2_2():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        items, total = svc.list_progress(progress_stage='school_apply', page=1, page_size=20)
        print(f'      School application records total: {total}')
        for i in items[:3]:
            print(f'        - {i.student_name}: {i.school_name} ({i.progress_status_label})')
    finally: db.rollback(); db.close()

run_test('2.1 Create school application progress', t2_1)
run_test('2.2 Filter by school_apply stage', t2_2)

# ── Scene 3: Visa Processing ──
print('\n[Scene 3] Visa Processing')

def t3_1():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        r = svc.create_progress(ProgressCreateRequest(
            student_id=1, progress_stage='visa', progress_status='pending',
            progress_desc='I-20 received, preparing DS-160 and booking interview',
            school_name='Harvard University', target_country='USA',
            handler_employee_id=3,
            expected_finish_time=datetime.now() + timedelta(days=45),
        ))
        assert r.progress_stage_label == '签证办理'
        print(f'      Created: {r.student_name} - {r.progress_stage_label} - {r.progress_status_label}')
    finally: db.rollback(); db.close()

def t3_2():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        items, _ = svc.list_my_progress(student_user_id=11, progress_stage='visa', page=1, page_size=20)
        visa_items = [i for i in items if i.progress_stage == 'visa' and i.progress_status == 'pending']
        if visa_items:
            r = svc.update_progress(visa_items[0].id, ProgressUpdateRequest(
                progress_status='blocked',
                progress_desc='Visa interview delayed - embassy backlog',
            ))
            assert r.progress_status == 'blocked'
            assert r.progress_status_label == '受阻'
            print(f'      Blocked: {r.progress_desc}')
        else:
            print(f'      No pending visa to block, skip')
    finally: db.rollback(); db.close()

def t3_3():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        count = svc.count_blocked()
        print(f'      Blocked progress count: {count}')
    finally: db.rollback(); db.close()

run_test('3.1 Create visa progress', t3_1)
run_test('3.2 Block visa (受阻)', t3_2)
run_test('3.3 Count blocked', t3_3)

# ── Scene 4: Offer ──
print('\n[Scene 4] Offer')

def t4_1():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        r = svc.create_progress(ProgressCreateRequest(
            student_id=3, progress_stage='offer', progress_status='completed',
            progress_desc='Received unconditional offer from MIT',
            school_name='MIT', program_name='Computer Science PhD', target_country='USA',
        ))
        assert r.progress_stage_label == '录取通知'
        assert r.progress_status_label == '已完成'
        print(f'      Created: {r.student_name} - {r.school_name} {r.program_name}')
        print(f'      Status: {r.progress_status_label}')
    finally: db.rollback(); db.close()

def t4_2():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        timeline = svc.get_timeline(student_user_id=13)
        assert timeline.student_name is not None
        print(f'      {timeline.student_name} timeline: {len(timeline.stages)} stages')
        print(f'      Summary: {timeline.summary}')
        for s in timeline.stages:
            status_icon = '[DONE]' if s.status == 'completed' else ('[BLOCK]' if s.status == 'blocked' else '[PROG]')
            print(f'        {status_icon} {s.stage_label}: {s.status_label}')
    finally: db.rollback(); db.close()

run_test('4.1 Create offer progress', t4_1)
run_test('4.2 Student timeline overview', t4_2)

# ── Cross-cutting ──
print('\n[Cross-cutting]')

def t5_1():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        items, total = svc.list_progress(page=1, page_size=100)
        stages = {}
        for i in items:
            s = i.progress_stage
            stages[s] = stages.get(s, 0) + 1
        print(f'      Total: {total} records')
        for s, c in sorted(stages.items()):
            print(f'        {PROGRESS_STAGES.get(s, s)}: {c}')
    finally: db.rollback(); db.close()

def t5_2():
    ref = ApplicationProgressService.get_stages_reference()
    assert len(ref.stages) == 5 and len(ref.statuses) == 4
    print(f'      Stages: {list(ref.stages.values())}')
    print(f'      Statuses: {list(ref.statuses.values())}')

def t5_3():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        try:
            svc.create_progress(ProgressCreateRequest(
                student_id=1, progress_stage='gre_exam', progress_status='processing',
            ))
            assert False, 'should have raised'
        except Exception as e:
            assert 'Invalid stage' in str(e)
            print(f'      Rejected invalid stage: gre_exam')
    finally: db.rollback(); db.close()

def t5_4():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        try:
            svc.create_progress(ProgressCreateRequest(
                student_id=1, progress_stage='essay', progress_status='unknown',
            ))
            assert False, 'should have raised'
        except Exception as e:
            assert 'Invalid status' in str(e)
            print(f'      Rejected invalid status: unknown')
    finally: db.rollback(); db.close()

def t5_5():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        try:
            svc.get_progress(99999)
            assert False, 'should have raised'
        except Exception as e:
            assert 'not found' in str(e).lower()
            print(f'      Rejected non-existent ID: 99999')
    finally: db.rollback(); db.close()

def t5_6():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        from backend.app.models.crm_lead import CrmLead
        lead = db.query(CrmLead).filter(CrmLead.is_delete == 0).first()
        if lead:
            result = svc.sync_from_crm('crm_lead', lead.lead_no)
            assert result['sync_direction'] == 'to_local'
            assert result['progress'].crm_sync_status == 'synced'
            print(f'      CRM synced from lead: {lead.lead_no}')
        else:
            print(f'      No CRM lead to sync, skip')
    finally: db.rollback(); db.close()

def t5_7():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        try:
            svc.list_my_progress(student_user_id=99999, page=1, page_size=20)
            assert False, 'should have raised'
        except Exception as e:
            assert 'not found' in str(e).lower()
            print(f'      Rejected non-existent user: 99999')
    finally: db.rollback(); db.close()

def t5_8():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        items, total = svc.list_progress(handler_employee_id=6, page=1, page_size=20)
        print(f'      Handler 6: {total} record(s)')
        for i in items[:3]:
            print(f'        - {i.student_name}: {i.progress_stage_label} ({i.progress_status_label})')
    finally: db.rollback(); db.close()

def t5_9():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        p1, t1 = svc.list_progress(page=1, page_size=5)
        p2, t2 = svc.list_progress(page=2, page_size=5)
        assert t1 == t2
        assert len(p1) <= 5 and len(p2) <= 5
        print(f'      Page1: {len(p1)} items, Page2: {len(p2)} items, Total: {t1}')
    finally: db.rollback(); db.close()

def t5_10():
    db = Session()
    try:
        svc = ApplicationProgressService(db)
        timeline = svc.get_timeline(student_user_id=11)
        print(f'      {timeline.student_name} full progress:')
        covered = set()
        for s in timeline.stages:
            covered.add(s.stage)
            eta = s.expected_finish_time.strftime('%Y-%m-%d') if s.expected_finish_time else 'N/A'
            print(f'        [{s.status_label}] {s.stage_label}: {s.desc or "N/A"}')
            print(f'           School: {s.school_name or "N/A"}, ETA: {eta}')
        missing = set(PROGRESS_STAGES.keys()) - covered - {'other'}
        if missing:
            labels = [PROGRESS_STAGES[ms] for ms in missing]
            print(f'      Not yet started: {labels}')
        else:
            print(f'      All major stages covered!')
    finally: db.rollback(); db.close()

run_test('5.1 List all with stage distribution', t5_1)
run_test('5.2 Stages reference data', t5_2)
run_test('5.3 Reject invalid stage', t5_3)
run_test('5.4 Reject invalid status', t5_4)
run_test('5.5 Reject non-existent ID', t5_5)
run_test('5.6 CRM sync reservation', t5_6)
run_test('5.7 Reject non-existent user', t5_7)
run_test('5.8 Filter by handler', t5_8)
run_test('5.9 Pagination', t5_9)
run_test('5.10 Full student timeline', t5_10)

print('\n' + '=' * 60)
print(f'  Results: {passed} PASSED, {failed} FAILED')
print('=' * 60)
