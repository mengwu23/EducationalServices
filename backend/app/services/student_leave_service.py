"""
请假审批模块 — 业务逻辑层（Service）
========================================

Service 层是请假审批模块的核心编排者，负责：

1. 业务规则校验（状态机、角色权限、数据一致性）
2. 跨 DAO 的数据组装（如查询关联的学生姓名、审批人姓名）
3. 请求单号生成
4. 事务提交（commit）

调用关系：
    Controller → StudentLeaveService → StudentLeaveDao
                                   → StudentProfile（查学生姓名）
                                   → EmployeeProfile + SysUser（查审批人姓名）

注意：所有写操作完成后调用 self.db.commit()，异常由 Controller 层统一捕获回滚。
"""

import random
import string
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.common.enums import LeaveStatus, UserType
from app.common.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    StateConflictException,
)
from app.common.pagination import PageQuery
from app.daos.student_leave_dao import StudentLeaveDao
from app.models.employee_profile import EmployeeProfile
from app.models.student_profile import StudentProfile
from app.models.student_leave_request import StudentLeaveRequest
from app.models.sys_user import SysUser
from app.schemas.student_leave_schema import (
    LeaveCreateRequest,
    LeaveListQuery,
    LeaveResponse,
)


class StudentLeaveService:
    """请假审批业务服务

    每个方法接收当前登录用户的 sys_user.id 和 user_type，
    通过这两个参数进行权限鉴别和关联数据查询。

    Attributes:
        db: SQLAlchemy 数据库会话
        dao: 请假数据访问对象
    """

    def __init__(self, db: Session):
        self.db = db
        self.dao = StudentLeaveDao(db)

    # ============================================================
    # 公开方法 — 对应 Controller 的每个 API
    # ============================================================

    def create_leave(
        self,
        current_user_id: int,
        current_user_type: str,
        data: LeaveCreateRequest,
    ) -> LeaveResponse:
        """学生提交请假申请

        完整流程：
            1. 校验当前用户是学生角色
            2. 查找 sys_user_id 对应的学生档案（student_profile）
            3. 生成唯一请假单号
            4. 调用 DAO 创建记录
            5. 提交事务
            6. 返回含学生姓名的完整响应

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type（必须为 student）
            data: 前端提交的请假请求体（leave_type, reason, start_time, end_time）

        Returns:
            创建成功的请假完整信息（含 student_name）

        Raises:
            PermissionDeniedException: 非学生角色不能提交请假
            NotFoundException: 学生档案不存在
        """
        # --- 第 1 步：校验角色 ---
        if current_user_type != UserType.STUDENT.value:
            raise PermissionDeniedException("只有学生才能提交请假申请")

        # --- 第 2 步：查找学生档案 ---
        student = self._get_student_by_user_id(current_user_id)
        if student is None:
            raise NotFoundException("未找到学生档案，请确认账号已关联学生身份", code=40401)

        # --- 第 3 步：生成请求单号 ---
        request_no = self._generate_request_no()

        # --- 第 4 步：调用 DAO 创建记录 ---
        leave = self.dao.create(
            request_no=request_no,
            student_id=student.id,
            leave_type=data.leave_type.value,
            reason=data.reason,
            start_time=data.start_time,
            end_time=data.end_time,
            status=LeaveStatus.PENDING.value,
        )

        # --- 第 5 步：提交事务 ---
        self.db.commit()

        # --- 第 6 步：构建并返回响应 ---
        return self._build_leave_response(leave, student_name=student.student_name)

    def approve_leave(
        self,
        current_user_id: int,
        current_user_type: str,
        leave_id: int,
    ) -> LeaveResponse:
        """员工审批通过请假申请

        完整流程：
            1. 校验当前用户是员工角色
            2. 查找员工档案（employee_profile）
            3. 查找请假记录，校验存在
            4. 校验请假状态为 pending（待审批）
            5. 更新状态为 approved，记录审批人、审批时间
            6. 提交事务
            7. 返回更新后的请假信息

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type（必须为 employee）
            leave_id: 请假申请 ID

        Returns:
            审批通过后的请假完整信息

        Raises:
            PermissionDeniedException: 非员工角色不能审批
            NotFoundException: 员工档案不存在 或 请假申请不存在
            StateConflictException: 请假状态不是 pending，无法审批通过
        """
        # --- 第 1 步：校验角色 ---
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能审批请假")

        # --- 第 2 步：查找员工档案 ---
        employee = self._get_employee_by_user_id(current_user_id)
        if employee is None:
            raise NotFoundException("未找到员工档案，请确认账号已关联员工身份", code=40402)

        # --- 第 3 步：查找请假记录 ---
        leave = self.dao.get_by_id(leave_id)
        if leave is None:
            raise NotFoundException("请假申请不存在", code=40400)

        # --- 第 4 步：校验状态 ---
        if leave.status != LeaveStatus.PENDING.value:
            raise StateConflictException(
                f"当前状态为「{leave.status}」，仅待审批（pending）状态的请假才能审批通过"
            )

        # --- 第 5 步：更新状态 ---
        leave = self.dao.update(
            leave_id=leave_id,
            status=LeaveStatus.APPROVED.value,
            approver_employee_id=employee.id,
            approval_comment=None,  # 审批通过不需要意见
            approve_time=datetime.now(),
        )

        # --- 第 6 步：提交事务 ---
        self.db.commit()

        # --- 第 7 步：构建响应 ---
        return self._build_leave_response(
            leave,
            student_name=self._get_student_name_by_id(leave.student_id),
            employee_id=employee.id,
        )

    def reject_leave(
        self,
        current_user_id: int,
        current_user_type: str,
        leave_id: int,
        comment: Optional[str] = None,
    ) -> LeaveResponse:
        """员工驳回请假申请

        流程与 approve 类似，但状态改为 rejected，并可附加驳回原因。

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type（必须为 employee）
            leave_id: 请假申请 ID
            comment: 驳回原因（可选，但建议填写方便学生了解）

        Returns:
            驳回后的请假完整信息

        Raises:
            PermissionDeniedException: 非员工角色不能审批
            NotFoundException: 员工档案不存在 或 请假申请不存在
            StateConflictException: 请假状态不是 pending，无法驳回
        """
        # --- 第 1~4 步：与 approve 相同的校验逻辑 ---
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能审批请假")

        employee = self._get_employee_by_user_id(current_user_id)
        if employee is None:
            raise NotFoundException("未找到员工档案，请确认账号已关联员工身份", code=40402)

        leave = self.dao.get_by_id(leave_id)
        if leave is None:
            raise NotFoundException("请假申请不存在", code=40400)

        if leave.status != LeaveStatus.PENDING.value:
            raise StateConflictException(
                f"当前状态为「{leave.status}」，仅待审批（pending）状态的请假才能驳回"
            )

        # --- 第 5 步：更新状态为 rejected ---
        leave = self.dao.update(
            leave_id=leave_id,
            status=LeaveStatus.REJECTED.value,
            approver_employee_id=employee.id,
            approval_comment=comment,
            approve_time=datetime.now(),
        )

        self.db.commit()

        return self._build_leave_response(
            leave,
            student_name=self._get_student_name_by_id(leave.student_id),
            employee_id=employee.id,
        )

    def cancel_leave(
        self,
        current_user_id: int,
        current_user_type: str,
        leave_id: int,
    ) -> LeaveResponse:
        """学生取消请假申请

        只有请假本人（学生）且在 pending 状态下才能取消。

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            leave_id: 请假申请 ID

        Returns:
            取消后的请假完整信息

        Raises:
            NotFoundException: 请假申请不存在
            PermissionDeniedException: 不是本人操作
            StateConflictException: 状态不是 pending，无法取消
        """
        # --- 第 1 步：查找请假记录 ---
        leave = self.dao.get_by_id(leave_id)
        if leave is None:
            raise NotFoundException("请假申请不存在", code=40400)

        # --- 第 2 步：校验是本人（学生才能取消自己的请假） ---
        if current_user_type == UserType.STUDENT.value:
            student = self._get_student_by_user_id(current_user_id)
            if student is None or leave.student_id != student.id:
                raise PermissionDeniedException("只能取消自己的请假申请")
        elif current_user_type == UserType.ADMIN.value:
            # 管理员可以取消任何请假
            pass
        else:
            raise PermissionDeniedException("只有学生或管理员才能取消请假")

        # --- 第 3 步：校验状态 ---
        if leave.status != LeaveStatus.PENDING.value:
            raise StateConflictException(
                f"当前状态为「{leave.status}」，仅待审批（pending）状态的请假才能取消"
            )

        # --- 第 4 步：更新状态 ---
        leave = self.dao.update(
            leave_id=leave_id,
            status=LeaveStatus.CANCELLED.value,
        )

        self.db.commit()

        return self._build_leave_response(
            leave,
            student_name=self._get_student_name_by_id(leave.student_id),
        )

    def get_leave_detail(
        self,
        current_user_id: int,
        current_user_type: str,
        leave_id: int,
    ) -> LeaveResponse:
        """查询请假详情

        权限规则：
            - 学生：只能查自己的请假
            - 员工：只能查自己审批过的请假
            - 管理员：可查任意请假

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            leave_id: 请假申请 ID

        Returns:
            含完整关联信息的请假详情
        """
        leave = self.dao.get_by_id(leave_id)
        if leave is None:
            raise NotFoundException("请假申请不存在", code=40400)

        # --- 权限校验 ---
        self._check_leave_read_permission(leave, current_user_id, current_user_type)

        # --- 查询关联名称 ---
        student_name = self._get_student_name_by_id(leave.student_id)

        return self._build_leave_response(leave, student_name=student_name)

    def list_my_leaves(
        self,
        current_user_id: int,
        current_user_type: str,
        query: LeaveListQuery,
    ):
        """查询当前学生的请假列表（分页 + 筛选）

        从 JWT 中获取当前用户信息，自动转换 user_id → student_id。

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            query: 分页 + 筛选参数（status, date_from, date_to）

        Returns:
            (当前页 LeaveResponse 列表, 总记录数)
        """
        if current_user_type != UserType.STUDENT.value:
            raise PermissionDeniedException("只有学生才能查看自己的请假列表")

        student = self._get_student_by_user_id(current_user_id)
        if student is None:
            raise NotFoundException("未找到学生档案", code=40401)

        items, total = self.dao.list_by_student(
            student_id=student.id,
            query=query,
            status=query.status,
            date_from=query.date_from,
            date_to=query.date_to,
        )

        # 为每条记录填充学生姓名
        results = [
            self._build_leave_response(item, student_name=student.student_name)
            for item in items
        ]

        return results, total

    def list_all_pending(
        self,
        current_user_type: str,
        query: PageQuery,
    ):
        """查询所有待审批的请假列表（员工端）

        Args:
            current_user_type: 当前登录用户的 user_type（必须为 employee/admin）
            query: 分页参数

        Returns:
            (当前页 LeaveResponse 列表, 总记录数)
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能查看待审批列表")

        items, total = self.dao.list_all_pending(query)

        # 为每条待审批记录填充学生姓名
        results = [
            self._build_leave_response(
                item,
                student_name=self._get_student_name_by_id(item.student_id),
            )
            for item in items
        ]

        return results, total

    def list_approval_history(
        self,
        current_user_id: int,
        current_user_type: str,
        query: PageQuery,
    ):
        """查询当前员工的审批历史（已通过 / 已驳回）

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            query: 分页参数

        Returns:
            (当前页 LeaveResponse 列表, 总记录数)
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能查看审批历史")

        employee = self._get_employee_by_user_id(current_user_id)
        if employee is None:
            raise NotFoundException("未找到员工档案", code=40402)

        items, total = self.dao.list_approval_history(
            employee_id=employee.id,
            query=query,
        )

        results = [
            self._build_leave_response(
                item,
                student_name=self._get_student_name_by_id(item.student_id),
                employee_id=employee.id,
            )
            for item in items
        ]

        return results, total

    def count_pending(self, current_user_type: str) -> int:
        """统计当前待审批的请假总数（员工首页角标用）

        Args:
            current_user_type: 当前登录用户的 user_type

        Returns:
            待审批总数
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            return 0
        return self.dao.count_pending()

    # ============================================================
    # 私有辅助方法
    # ============================================================

    def _build_leave_response(
        self,
        leave: StudentLeaveRequest,
        student_name: Optional[str] = None,
        employee_id: Optional[int] = None,
    ) -> LeaveResponse:
        """将 ORM 对象转换为 LeaveResponse

        同时填充 student_name 和 approver_name 等关联字段。

        Args:
            leave: SQLAlchemy ORM 对象
            student_name: 学生姓名（可选，由调用方传入避免重复查询）
            employee_id: 当前员工 ID（可选，用于判断是否需要查审批人姓名）

        Returns:
            可直接序列化返回的 LeaveResponse
        """
        # 先通过 from_attributes 自动转换 ORM 字段
        response = LeaveResponse.model_validate(leave)

        # 填充学生姓名
        if student_name:
            response.student_name = student_name

        # 填充审批人姓名（如果有审批人）
        if leave.approver_employee_id:
            approver_name = self._get_employee_name_by_id(leave.approver_employee_id)
            response.approver_name = approver_name

        return response

    def _check_leave_read_permission(
        self,
        leave: StudentLeaveRequest,
        current_user_id: int,
        current_user_type: str,
    ):
        """校验当前用户是否有权限查看这条请假记录

        规则：
            - 管理员：全部可见
            - 学生：只能看自己的
            - 员工：只能看自己审批过的

        Args:
            leave: 请假 ORM 对象
            current_user_id: 当前用户 sys_user.id
            current_user_type: 当前用户角色

        Raises:
            PermissionDeniedException: 无权限查看
        """
        if current_user_type == UserType.ADMIN.value:
            return  # 管理员全部可见

        if current_user_type == UserType.STUDENT.value:
            student = self._get_student_by_user_id(current_user_id)
            if student and leave.student_id == student.id:
                return  # 本人，通过

        if current_user_type == UserType.EMPLOYEE.value:
            employee = self._get_employee_by_user_id(current_user_id)
            if employee and leave.approver_employee_id == employee.id:
                return  # 审批人，通过

        raise PermissionDeniedException("无权查看此请假记录")

    # ----------------------------------------------------------
    # 关联数据查询
    # ----------------------------------------------------------

    def _get_student_by_user_id(self, user_id: int) -> Optional[StudentProfile]:
        """根据 sys_user.id 查找对应的学生档案

        student_profile.user_id 关联 sys_user.id。
        一个用户账号最多对应一个学生档案（数据库有唯一约束）。
        """
        return self.db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id
        ).first()

    def _get_employee_by_user_id(self, user_id: int) -> Optional[EmployeeProfile]:
        """根据 sys_user.id 查找对应的员工档案

        employee_profile.user_id 关联 sys_user.id。
        一个用户账号最多对应一个员工档案。
        """
        return self.db.query(EmployeeProfile).filter(
            EmployeeProfile.user_id == user_id
        ).first()

    def _get_student_name_by_id(self, student_id: int) -> Optional[str]:
        """根据 student_profile.id 查询学生姓名"""
        student = self.db.query(StudentProfile).filter(
            StudentProfile.id == student_id
        ).first()
        return student.student_name if student else None

    def _get_employee_name_by_id(self, employee_id: int) -> Optional[str]:
        """根据 employee_profile.id 查询员工真实姓名

        员工姓名存在 sys_user.real_name 中，需要联表：
            employee_profile.id → employee_profile.user_id → sys_user.id → sys_user.real_name
        """
        emp = self.db.query(EmployeeProfile).filter(
            EmployeeProfile.id == employee_id
        ).first()
        if emp is None:
            return None

        user = self.db.query(SysUser).filter(
            SysUser.id == emp.user_id
        ).first()
        return user.real_name if user else None

    # ----------------------------------------------------------
    # 工具方法
    # ----------------------------------------------------------

    @staticmethod
    def _generate_request_no() -> str:
        """生成请假单号

        格式：LV + 年月日时分秒 + 3位随机数字
        示例：LV202606101530123

        采用秒级时间戳 + 随机数，保证单号唯一性。
        3位随机数字提供 1000 种组合，同一秒内冲突概率极低。
        """
        now = datetime.now()
        time_part = now.strftime("%Y%m%d%H%M%S")  # 202606101530
        rand_part = ''.join(random.choices(string.digits, k=3))  # 123
        return f"LV{time_part}{rand_part}"
