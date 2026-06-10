from enum import Enum


class AcademicEventType(str, Enum):
    PAPER_DEADLINE = "paper_deadline"
    EXAM = "exam"
    COURSE_DEADLINE = "course_deadline"
    OTHER = "other"


class AcademicEventStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FeedbackTicketType(str, Enum):
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    CONSULT = "consult"


class FeedbackPriorityLevel(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    SEVERE = "severe"


class FeedbackTicketStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"



class LeaveType(str, Enum):
    """请假类型

    对应 student_leave_request.leave_type 字段
    学生请假时必填
    """
    SICK = "sick"          # 病假
    PERSONAL = "personal"  # 事假
    OTHER = "other"        # 其他


class LeaveStatus(str, Enum):
    """请假审批状态

    对应 student_leave_request.status 字段
    状态流转规则由 student_leave_service 控制

    流转关系：
        学生提交 → pending（待审批）
                       ↓
              ┌── 员工审批 ──┐
              ↓              ↓
          approved       rejected
         （已通过）      （已驳回）

        pending 状态下，学生可取消 → cancelled（已取消）
    """
    PENDING = "pending"        # 待审批
    APPROVED = "approved"      # 已通过
    REJECTED = "rejected"      # 已驳回
    CANCELLED = "cancelled"    # 已取消


class UserType(str, Enum):
    """用户类型

    对应 sys_user.user_type 字段
    请假审批模块中用于校验：
    - 学生角色才允许提交请假
    - 员工角色才允许审批请假
    """
    EMPLOYEE = "employee"  # 员工
    STUDENT = "student"    # 学生
    CUSTOMER = "customer"  # 访客
    ADMIN = "admin"        # 管理员


# ============================================================
# 心理关怀模块枚举
# ============================================================

class PsychRiskLevel(str, Enum):
    """心理风险等级

    对应 student_psych_profile.risk_level 和 student_psych_alert.risk_level 字段
    用于标识学生当前心理风险状态

    等级说明：
        low      — 低风险，正常状态，常规关注
        medium   — 中风险，需要关注，建议定期沟通
        high     — 高风险，需要介入，建议老师跟进
        critical — 危急，需要立即干预

    AI 聊天时识别到高风险或危急等级，自动触发预警创建。
    """
    LOW = "low"                # 低风险
    MEDIUM = "medium"          # 中风险
    HIGH = "high"              # 高风险
    CRITICAL = "critical"      # 危急


class PsychAlertStatus(str, Enum):
    """心理预警处理状态

    对应 student_psych_alert.status 字段
    状态流转由 psych_service 控制

    流转关系：
        pending（未处理）
            │  老师点击"开始跟进"
            ▼
        processing（跟进中）
            │  老师填写处理结果后点击"解除"
            ▼
        resolved（已解除）
            │  老师点击"关闭"
            ▼
        closed（已关闭）

        注：AI 自动创建预警时初始状态为 pending
    """
    PENDING = "pending"            # 未处理
    PROCESSING = "processing"      # 跟进中
    RESOLVED = "resolved"          # 已解除
    CLOSED = "closed"
