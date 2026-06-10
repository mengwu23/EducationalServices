"""集中导入所有 ORM 实体，确保 SQLAlchemy 元数据能注册全部表。"""

from .academic_event import AcademicEvent
from .course_project import CourseProject
from .crm_lead import CrmLead
from .customer_analysis_record import CustomerAnalysisRecord
from .employee_daily_report import EmployeeDailyReport
from .employee_profile import EmployeeProfile
from .event_lecture import EventLecture
from .event_registration import EventRegistration
from .faq_qa import FaqQa
from .student_application_progress import StudentApplicationProgress
from .student_feedback_ticket import StudentFeedbackTicket
from .student_leave_request import StudentLeaveRequest
from .student_profile import StudentProfile
from .student_psych_alert import StudentPsychAlert
from .student_psych_profile import StudentPsychProfile
from .student_score import StudentScore
from .sys_department import SysDepartment
from .sys_user import SysUser

__all__ = [
    "AcademicEvent",
    "CourseProject",
    "CrmLead",
    "CustomerAnalysisRecord",
    "EmployeeDailyReport",
    "EmployeeProfile",
    "EventLecture",
    "EventRegistration",
    "FaqQa",
    "StudentApplicationProgress",
    "StudentFeedbackTicket",
    "StudentLeaveRequest",
    "StudentProfile",
    "StudentPsychAlert",
    "StudentPsychProfile",
    "StudentScore",
    "SysDepartment",
    "SysUser",
]
