"""
心理关怀模块 — 业务逻辑层（Service）
========================================

Service 层是心理关怀模块的核心编排者，负责：

1. 业务规则校验（状态机、角色权限、数据一致性）
2. 跨 DAO 的数据组装（查询关联的学生姓名、老师姓名）
3. 预警编号生成
4. 事务提交（commit）

调用关系：
    Controller → StudentPsychService → StudentPsychDao
                                  → StudentProfile（查学生姓名）
                                  → EmployeeProfile + SysUser（查老师姓名）

AI 预留接口：
    - create_alert()   — 后续 Dify 检测到高风险时自动调用
    - update_emotion() — 后续 Dify 聊天时自动更新情绪状态
"""

import random
import string
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.common.enums import PsychAlertStatus, PsychRiskLevel, UserType
from backend.app.common.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    StateConflictException,
    ValidationErrorException,
)
from backend.app.common.pagination import PageQuery
from backend.app.daos.student_psych_dao import StudentPsychDao
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.student_profile import StudentProfile
from backend.app.models.sys_user import SysUser
from backend.app.models.student_psych_profile import StudentPsychProfile
from backend.app.schemas.student_psych_schema import (
    EmotionUpdateRequest,
    PsychAlertCreateRequest,
    PsychAlertResponse,
    PsychProfileResponse,
)


class StudentPsychService:
    """心理关怀业务服务

    每个方法接收当前登录用户的 sys_user.id 和 user_type，
    通过这两个参数进行权限鉴别和关联数据查询。

    Attributes:
        db: SQLAlchemy 数据库会话
        dao: 心理关怀数据访问对象
    """

    def __init__(self, db: Session):
        self.db = db
        self.dao = StudentPsychDao(db)

    # ============================================================
    # 公开方法 — 查询类
    # ============================================================

    def get_my_profile(
        self,
        current_user_id: int,
        current_user_type: str,
    ) -> PsychProfileResponse:
        """学生查看自己的心理画像

        流程：
            1. 校验当前用户是学生
            2. 查找 student_profile 获取 student_id
            3. 查心理画像
            4. 返回含学生姓名的完整响应

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type（必须为 student）

        Returns:
            心理画像详情

        Raises:
            PermissionDeniedException: 非学生角色
            NotFoundException: 学生档案不存在 或 心理画像不存在
        """
        if current_user_type != UserType.STUDENT.value:
            raise PermissionDeniedException("只有学生才能查看自己的心理画像")

        student = self._get_student_by_user_id(current_user_id)
        if student is None:
            raise NotFoundException("未找到学生档案", code=40401)

        profile = self.dao.get_profile_by_student_id(student.id)
        if profile is None:
            raise NotFoundException("暂无心���画像数据", code=40403)

        return self._build_profile_response(profile, student_name=student.student_name)

    def list_my_alerts(
        self,
        current_user_id: int,
        current_user_type: str,
        query: "PsychAlertListQuery",
    ):
        """学生查看自己的预警记录（分页 + 状态筛选）

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type（必须为 student）
            query: 分页 + 状态筛选参数

        Returns:
            (当前页预警列表, 总记录数)
        """
        if current_user_type != UserType.STUDENT.value:
            raise PermissionDeniedException("只有学生才能查看自己的预警记录")

        student = self._get_student_by_user_id(current_user_id)
        if student is None:
            raise NotFoundException("未找到学生档案", code=40401)

        items, total = self.dao.list_alerts_by_student(
            student_id=student.id,
            query=query,
            status=query.status,
        )

        student_name = student.student_name
        results = [
            self._build_alert_response(item, student_name=student_name)
            for item in items
        ]

        return results, total

    def list_all_profiles(
        self,
        current_user_type: str,
        query: "PsychProfileListQuery",
    ):
        """员工查看所有学生的心理画像（分页 + 按风险等级筛选）

        Args:
            current_user_type: 当前登录用户的 user_type（必须为 employee/admin）
            query: 分页 + 风险等级筛选参数

        Returns:
            (当前页画像列表, 总记录数)
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能查看心理画像列表")

        items, total = self.dao.list_profiles(
            query=query,
            risk_level=query.risk_level,
        )

        # 为每条画像填充学生姓名
        results = [
            self._build_profile_response(
                item,
                student_name=self._get_student_name_by_id(item.student_id),
            )
            for item in items
        ]

        return results, total

    def list_pending_alerts(
        self,
        current_user_type: str,
        query: PageQuery,
    ):
        """员工查看所有待处理预警（分页）

        包含 status=pending 和 status=processing 的记录。

        Args:
            current_user_type: 当前登录用户的 user_type（必须为 employee/admin）
            query: 分页参数

        Returns:
            (当前页预警列表, 总记录数)
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能查看待处理预警")

        items, total = self.dao.list_pending_alerts(query)

        results = [
            self._build_alert_response(
                item,
                student_name=self._get_student_name_by_id(item.student_id),
                teacher_name=self._get_employee_name_by_id(item.teacher_employee_id) if item.teacher_employee_id else None,
            )
            for item in items
        ]

        return results, total

    def list_processed_alerts(
        self,
        current_user_id: int,
        current_user_type: str,
        query: PageQuery,
    ):
        """员工查看自己处理过的预警历史

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type（必须为 employee/admin）
            query: 分页参数

        Returns:
            (当前页预警列表, 总记录数)
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能查看处理历史")

        employee = self._get_employee_by_user_id(current_user_id)
        if employee is None:
            raise NotFoundException("未找到员工档案", code=40402)

        items, total = self.dao.list_processed_alerts(
            employee_id=employee.id,
            query=query,
        )

        results = [
            self._build_alert_response(
                item,
                student_name=self._get_student_name_by_id(item.student_id),
                employee_id=employee.id,
            )
            for item in items
        ]

        return results, total

    def count_pending_alerts(self, current_user_type: str) -> int:
        """统计待处理预警数量（员工首页角标用）

        Args:
            current_user_type: 当前登录用户的 user_type

        Returns:
            待处理预警总数（非员工角色返回 0）
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            return 0
        return self.dao.count_pending_alerts()

    # ============================================================
    # 公开方法 — 写入类
    # ============================================================

    def create_alert(
        self,
        current_user_id: int,
        current_user_type: str,
        data: PsychAlertCreateRequest,
    ) -> PsychAlertResponse:
        """创建预警（AI/人工共用）

        人工或 AI 检测到高风险时创建预警记录。
        后续 Dify 聊天模块识别到 high/critical 风险时自动调用此接口。

        流程：
            1. 校验角色（employee/admin，后续 AI 调用可放宽）
            2. 验证学生存在
            3. 生成预警编号
            4. 创建预警（初始状态 pending）
            5. 更新心理画像的风险等级
            6. 提交事务

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            data: 预警创建请求体

        Returns:
            创建成功的预警详情

        Raises:
            PermissionDeniedException: 非员工/管理员角色
            NotFoundException: 学生不存在
        """
        # 校验角色（后续 AI 接入时，可增加 AI 调用凭证）
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能创建预警")

        # 验证学生存在
        student = self.db.query(StudentProfile).filter(
            StudentProfile.id == data.student_id,
        ).first()
        if student is None:
            raise NotFoundException("学生不存在", code=40401)

        # 生成预警编号
        alert_no = self._generate_alert_no()

        # 创建预警
        alert = self.dao.create_alert(
            alert_no=alert_no,
            student_id=data.student_id,
            trigger_reason=data.trigger_reason,
            risk_level=data.risk_level.value,
            status=PsychAlertStatus.PENDING.value,
        )

        # 同步更新心理画像的风险等级（如果画像存在）
        self.dao.update_profile(
            student_id=data.student_id,
            risk_level=data.risk_level.value,
        )

        self.db.commit()

        return self._build_alert_response(
            alert,
            student_name=student.student_name,
        )

    def update_emotion(
        self,
        current_user_id: int,
        current_user_type: str,
        student_id: int,
        data: EmotionUpdateRequest,
    ) -> PsychProfileResponse:
        """更新学生情绪状态（AI 预留接口）

        后续 Dify 聊天时，AI 分析学生情绪后自动调用此接口更新心理画像。
        当前阶段仅供员工手动更新。

        流程：
            1. 校验角色（employee/admin，后续 AI 调用可放宽）
            2. 验证学生存在
            3. 查找或创建心理画像
            4. 更新指定字段
            5. 提交事务

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            student_id: 要更新的学生 ID
            data: 情绪更新数据

        Returns:
            更新后的心理画像
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能更新情绪状态")

        student = self.db.query(StudentProfile).filter(
            StudentProfile.id == student_id,
        ).first()
        if student is None:
            raise NotFoundException("学生不存在", code=40401)

        # 查找或创建心理画像
        profile = self.dao.get_profile_by_student_id(student_id)
        if profile is None:
            # 如果没有画像，创建一个新的
            from backend.app.models.student_psych_profile import StudentPsychProfile
            profile = StudentPsychProfile(
                student_id=student_id,
                risk_level=PsychRiskLevel.LOW.value,
            )
            self.db.add(profile)
            self.db.flush()

        # 组装要更新的字段（只更新有值的字段）
        update_kwargs = {}
        if data.emotion_tag is not None:
            update_kwargs["latest_emotion_tag"] = data.emotion_tag
        if data.emotion_score is not None:
            update_kwargs["emotion_score"] = data.emotion_score
        if data.risk_level is not None:
            update_kwargs["risk_level"] = data.risk_level.value
        if data.summary is not None:
            update_kwargs["emotion_summary"] = data.summary
        update_kwargs["last_interaction_time"] = datetime.now()

        # 更新画像
        self.dao.update_profile(student_id=student_id, **update_kwargs)
        self.db.commit()

        # 重新查询获取更新后的数据
        profile = self.dao.get_profile_by_student_id(student_id)
        return self._build_profile_response(profile, student_name=student.student_name)

    def process_alert(
        self,
        current_user_id: int,
        current_user_type: str,
        alert_id: int,
    ) -> PsychAlertResponse:
        """开始跟进预警

        老师点击"开始跟进"，标记自己为处理人，状态改为 processing。

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type（必须为 employee/admin）
            alert_id: 预警 ID

        Returns:
            更新后的预警详情

        Raises:
            NotFoundException: 预警不存在
            PermissionDeniedException: 非员工角色
            StateConflictException: 状态不是 pending
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能处理预警")

        employee = self._get_employee_by_user_id(current_user_id)
        if employee is None:
            raise NotFoundException("未找到员工档案", code=40402)

        alert = self.dao.get_alert_by_id(alert_id)
        if alert is None:
            raise NotFoundException("预警不存在", code=40404)

        if alert.status != PsychAlertStatus.PENDING.value:
            raise StateConflictException(
                f"当前状态为「{alert.status}」，仅未处理（pending）的预警才能开始跟进"
            )

        alert = self.dao.update_alert(
            alert_id=alert_id,
            status=PsychAlertStatus.PROCESSING.value,
            teacher_employee_id=employee.id,
        )

        self.db.commit()

        return self._build_alert_response(
            alert,
            student_name=self._get_student_name_by_id(alert.student_id),
            employee_id=employee.id,
        )

    def resolve_alert(
        self,
        current_user_id: int,
        current_user_type: str,
        alert_id: int,
        handle_result: Optional[str] = None,
    ) -> PsychAlertResponse:
        """解除预警

        老师填写处理结果后点击"解除"，状态改为 resolved。

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            alert_id: 预警 ID
            handle_result: 处理结果说明

        Returns:
            更新后的预警详情

        Raises:
            StateConflictException: 状态不是 processing
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能处理预警")

        alert = self.dao.get_alert_by_id(alert_id)
        if alert is None:
            raise NotFoundException("预警不存在", code=40404)

        if alert.status != PsychAlertStatus.PROCESSING.value:
            raise StateConflictException(
                f"当前状态为「{alert.status}」，仅跟进中（processing）的预警才能解除"
            )

        alert = self.dao.update_alert(
            alert_id=alert_id,
            status=PsychAlertStatus.RESOLVED.value,
            handle_result=handle_result,
        )

        self.db.commit()

        return self._build_alert_response(
            alert,
            student_name=self._get_student_name_by_id(alert.student_id),
        )

    def close_alert(
        self,
        current_user_id: int,
        current_user_type: str,
        alert_id: int,
    ) -> PsychAlertResponse:
        """关闭预警

        老师点击"关闭"，状态改为 closed，记录关闭时间。

        Args:
            current_user_id: 当前登录用户的 sys_user.id
            current_user_type: 当前登录用户的 user_type
            alert_id: 预警 ID

        Returns:
            更新后的预警详情

        Raises:
            StateConflictException: 状态不是 resolved
        """
        if current_user_type not in (UserType.EMPLOYEE.value, UserType.ADMIN.value):
            raise PermissionDeniedException("只有员工才能处理预警")

        alert = self.dao.get_alert_by_id(alert_id)
        if alert is None:
            raise NotFoundException("预警不存在", code=40404)

        if alert.status != PsychAlertStatus.RESOLVED.value:
            raise StateConflictException(
                f"当前状态为「{alert.status}」，仅已解除（resolved）的预警才能关闭"
            )

        alert = self.dao.update_alert(
            alert_id=alert_id,
            status=PsychAlertStatus.CLOSED.value,
            close_time=datetime.now(),
        )

        self.db.commit()

        return self._build_alert_response(
            alert,
            student_name=self._get_student_name_by_id(alert.student_id),
        )

    # ============================================================
    # 私有辅助方法
    # ============================================================

    def _build_profile_response(
        self,
        profile: "StudentPsychProfile",
        student_name: Optional[str] = None,
    ) -> PsychProfileResponse:
        """将 ORM 对象转换为 PsychProfileResponse

        Args:
            profile: 心理画像 ORM 对象
            student_name: 学生姓名（可选，由调用方传入避免重复查询）

        Returns:
            可直接序列化的 PsychProfileResponse
        """
        response = PsychProfileResponse.model_validate(profile)
        if student_name:
            response.student_name = student_name
        return response

    def _build_alert_response(
        self,
        alert: "StudentPsychAlert",
        student_name: Optional[str] = None,
        teacher_name: Optional[str] = None,
        employee_id: Optional[int] = None,
    ) -> PsychAlertResponse:
        """将 ORM 对象转换为 PsychAlertResponse

        Args:
            alert: 预警 ORM 对象
            student_name: 学生姓名
            teacher_name: 老师姓名（可选）
            employee_id: 当前员工 ID（可选，用于自动查询老师姓名）

        Returns:
            可直接序列化的 PsychAlertResponse
        """
        response = PsychAlertResponse.model_validate(alert)
        if student_name:
            response.student_name = student_name
        if teacher_name:
            response.teacher_name = teacher_name
        if employee_id and alert.teacher_employee_id:
            response.teacher_name = self._get_employee_name_by_id(alert.teacher_employee_id)
        return response

    # ----------------------------------------------------------
    # 关联数据查询
    # ----------------------------------------------------------

    def _get_student_by_user_id(self, user_id: int) -> Optional[StudentProfile]:
        """根据 sys_user.id 查找对应的学生档案"""
        return self.db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id
        ).first()

    def _get_employee_by_user_id(self, user_id: int) -> Optional[EmployeeProfile]:
        """根据 sys_user.id 查找对应的员工档案"""
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

        联表路径：employee_profile → sys_user → real_name
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
    def _generate_alert_no() -> str:
        """生成预警编号

        格式：PA + 年月日时分秒 + 3位随机数字
        示例：PA202606101530123

        采用秒级时间戳 + 随机数，保证编号唯一性。
        """
        now = datetime.now()
        time_part = now.strftime("%Y%m%d%H%M%S")
        rand_part = ''.join(random.choices(string.digits, k=3))
        return f"PA{time_part}{rand_part}"
