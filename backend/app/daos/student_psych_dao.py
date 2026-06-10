"""
心理关怀模块 — 数据访问层（DAO）
====================================

操作两张表：
    - student_psych_profile — 心理画像（每人一条）
    - student_psych_alert   — 心理预警（一人多条）

查询方法返回 SQLAlchemy ORM 对象，由 Service 层转换为 Pydantic 模型。
分页查询返回 (items, total_count) 元组。

注意：所有查询默认过滤 is_delete=0（未删除）。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.common.enums import PsychAlertStatus, PsychRiskLevel
from app.common.pagination import PageQuery
from app.models.student_psych_alert import StudentPsychAlert
from app.models.student_psych_profile import StudentPsychProfile


class StudentPsychDao:
    """心理关怀数据访问类

    构造时传入 db Session，所有方法通过该 Session 执行操作。
    事务由 Service 层统一管理，DAO 层只做 flush 不做 commit。
    """

    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------------------------
    # 心理画像 — 查询
    # ----------------------------------------------------------

    def get_profile_by_student_id(self, student_id: int) -> Optional[StudentPsychProfile]:
        """按学生 ID 查询心理画像

        每个学生只有一条心理画像（数据库有 student_id 唯一约束）。

        Args:
            student_id: 学生 ID

        Returns:
            心理画像 ORM 对象，不存在则返回 None
        """
        return self.db.query(StudentPsychProfile).filter(
            StudentPsychProfile.student_id == student_id,
            StudentPsychProfile.is_delete == 0,
        ).first()

    def get_profile_by_id(self, profile_id: int) -> Optional[StudentPsychProfile]:
        """按主键 ID 查询心理画像

        Args:
            profile_id: 心理画像 ID

        Returns:
            心理画像 ORM 对象，不存在则返回 None
        """
        return self.db.query(StudentPsychProfile).filter(
            StudentPsychProfile.id == profile_id,
            StudentPsychProfile.is_delete == 0,
        ).first()

    def list_profiles(
        self,
        query: PageQuery,
        risk_level: Optional[PsychRiskLevel] = None,
    ) -> tuple[list[StudentPsychProfile], int]:
        """分页查询所有学生心理画像（按风险等级筛选）

        用于员工端查看学生心理状态概览，了解整体风险分布。

        Args:
            query: 分页参数
            risk_level: 按风险等级筛选（可选），如只查高风险学生

        Returns:
            (当前页画像列表, 符合条件的总记录数)
        """
        filters = [StudentPsychProfile.is_delete == 0]

        if risk_level is not None:
            filters.append(StudentPsychProfile.risk_level == risk_level.value)

        return self._paginated_query(StudentPsychProfile, filters, query)

    # ----------------------------------------------------------
    # 心理画像 — 写入
    # ----------------------------------------------------------

    def update_profile(
        self,
        student_id: int,
        **kwargs,
    ) -> Optional[StudentPsychProfile]:
        """更新学生心理画像

        根据 student_id 查找并更新指定字段。
        AI 检测到情绪变化时调用此方法更新情绪标签和分数。

        Args:
            student_id: 学生 ID
            **kwargs: 要更新的字段，如：
                - latest_emotion_tag: 最新情绪标签
                - emotion_score: 情绪分值
                - risk_level: 风险等级
                - emotion_summary: 情绪摘要
                - last_interaction_time: 最近交互时间

        Returns:
            更新后的 ORM 对象，学生不存在则返回 None
        """
        profile = self.get_profile_by_student_id(student_id)
        if profile is None:
            return None

        for field, value in kwargs.items():
            setattr(profile, field, value)

        self.db.flush()
        return profile

    # ----------------------------------------------------------
    # 心理预警 — 查询
    # ----------------------------------------------------------

    def get_alert_by_id(self, alert_id: int) -> Optional[StudentPsychAlert]:
        """按主键 ID 查询预警记录

        Args:
            alert_id: 预警 ID

        Returns:
            预警 ORM 对象，不存在则返回 None
        """
        return self.db.query(StudentPsychAlert).filter(
            StudentPsychAlert.id == alert_id,
            StudentPsychAlert.is_delete == 0,
        ).first()

    def get_alert_by_no(self, alert_no: str) -> Optional[StudentPsychAlert]:
        """按预警编号查询

        alert_no 在数据库中有唯一约束。

        Args:
            alert_no: 预警编号，如 "PA2026001"

        Returns:
            预警 ORM 对象，不存在则返回 None
        """
        return self.db.query(StudentPsychAlert).filter(
            StudentPsychAlert.alert_no == alert_no,
            StudentPsychAlert.is_delete == 0,
        ).first()

    def list_alerts_by_student(
        self,
        student_id: int,
        query: PageQuery,
        status: Optional[PsychAlertStatus] = None,
    ) -> tuple[list[StudentPsychAlert], int]:
        """查询某学生的预警记录（分页 + 可选状态筛选）

        学生端查看自己的预警历史。

        Args:
            student_id: 学生 ID
            query: 分页参数
            status: 按状态筛选（可选）

        Returns:
            (当前页预警列表, 总记录数)
        """
        filters = [
            StudentPsychAlert.student_id == student_id,
            StudentPsychAlert.is_delete == 0,
        ]

        if status is not None:
            filters.append(StudentPsychAlert.status == status.value)

        return self._paginated_query(StudentPsychAlert, filters, query)

    def list_pending_alerts(
        self,
        query: PageQuery,
    ) -> tuple[list[StudentPsychAlert], int]:
        """查询所有待处理和跟进中的预警

        员工端的"待处理预警"入口，显示 status=pending 和 status=processing 的记录。

        Args:
            query: 分页参数

        Returns:
            (当前页预警列表, 总记录数)
        """
        filters = [
            StudentPsychAlert.status.in_([
                PsychAlertStatus.PENDING.value,
                PsychAlertStatus.PROCESSING.value,
            ]),
            StudentPsychAlert.is_delete == 0,
        ]

        return self._paginated_query(StudentPsychAlert, filters, query)

    def list_processed_alerts(
        self,
        employee_id: int,
        query: PageQuery,
        status: Optional[PsychAlertStatus] = None,
    ) -> tuple[list[StudentPsychAlert], int]:
        """查询某员工处理过的预警历史

        用于员工端查看自己跟进/解除/关闭过的预警。

        Args:
            employee_id: 员工 ID（employee_profile.id）
            query: 分页参数
            status: 按状态筛选（可选）

        Returns:
            (当前页预警列表, 总记录数)
        """
        filters = [
            StudentPsychAlert.teacher_employee_id == employee_id,
            StudentPsychAlert.is_delete == 0,
        ]

        if status is not None:
            filters.append(StudentPsychAlert.status == status.value)

        return self._paginated_query(StudentPsychAlert, filters, query)

    def count_pending_alerts(self) -> int:
        """统计待处理的预警数量（未处理 + 跟进中）

        员工首页角标显示待处理数量。

        Returns:
            待处理预警总数
        """
        return self.db.query(StudentPsychAlert).filter(
            StudentPsychAlert.status.in_([
                PsychAlertStatus.PENDING.value,
                PsychAlertStatus.PROCESSING.value,
            ]),
            StudentPsychAlert.is_delete == 0,
        ).count()

    # ----------------------------------------------------------
    # 心理预警 — 写入
    # ----------------------------------------------------------

    def create_alert(self, **kwargs) -> StudentPsychAlert:
        """创建预警记录

        人工或 AI 检测到高风险时调用。
        由 Service 层负责组装参数（含 alert_no、student_id 等）。

        Args:
            **kwargs: 字段键值对，如：
                - alert_no: 预警编号
                - student_id: 学生 ID
                - trigger_reason: 触发原因
                - risk_level: 风险等级
                - status: 状态（默认 pending）

        Returns:
            已创建但尚未提交的 ORM 对象（Service 层负责 commit）
        """
        alert = StudentPsychAlert(**kwargs)
        self.db.add(alert)
        self.db.flush()
        return alert

    def update_alert(
        self,
        alert_id: int,
        **kwargs,
    ) -> Optional[StudentPsychAlert]:
        """更新预警的指定字段

        只更新传入的字段，未传入的字段保持不变。
        用于状态变更、填写处理结果、记录跟进老师等。

        Args:
            alert_id: 要更新的预警 ID
            **kwargs: 要更新的字段键值对，如：
                - status: 处理状态
                - teacher_employee_id: 跟进老师
                - handle_result: 处理结果
                - close_time: 关闭时间

        Returns:
            更新后的 ORM 对象，不存在则返回 None
        """
        alert = self.get_alert_by_id(alert_id)
        if alert is None:
            return None

        for field, value in kwargs.items():
            setattr(alert, field, value)

        self.db.flush()
        return alert

    # ----------------------------------------------------------
    # 私有方法
    # ----------------------------------------------------------

    def _paginated_query(
        self,
        model,
        filters: list,
        query: PageQuery,
    ) -> tuple[list, int]:
        """执行分页查询的通用方法

        Args:
            model: SQLAlchemy Model 类
            filters: 过滤条件列表
            query: 分页参数

        Returns:
            (当前页数据, 总记录数)
        """
        q = self.db.query(model).filter(*filters)

        total = q.count()

        items = q.order_by(
            desc(model.create_time)
        ).offset(
            (query.page - 1) * query.page_size
        ).limit(
            query.page_size
        ).all()

        return items, total
