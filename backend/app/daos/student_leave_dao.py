"""
请假审批模块 — 数据访问层（DAO）
====================================

DAO 层的职责：
    只封装 SQLAlchemy 查询和写入操作，不写任何业务判断逻辑。
    所有业务规则（状态校验、权限校验）都在 Service 层处理。

返回说明：
    查询方法返回 SQLAlchemy ORM 对象，由 Service 层转换为 Pydantic 模型。
    分页查询返回 (items, total_count) 元组。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.app.common.enums import LeaveStatus
from backend.app.common.pagination import PageQuery
from backend.app.models.student_leave_request import StudentLeaveRequest


class StudentLeaveDao:
    """请假数据访问类

    所有方法通过构造时传入的 db Session 执行操作。
    事务由 Service 层统一管理，DAO 层不提交/回滚事务。
    """

    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------------------------
    # 单条查询
    # ----------------------------------------------------------

    def get_by_id(self, leave_id: int) -> Optional[StudentLeaveRequest]:
        """根据主键 ID 查询请假记录

        Args:
            leave_id: 请假申请 ID

        Returns:
            匹配的请假 ORM 对象，不存在则返回 None
        """
        return self.db.query(StudentLeaveRequest).filter(
            StudentLeaveRequest.id == leave_id
        ).first()

    def get_by_request_no(self, request_no: str) -> Optional[StudentLeaveRequest]:
        """根据请假单号查询

        request_no 在数据库中有唯一约束，只会返回 0 或 1 条。

        Args:
            request_no: 请假单号（如 "LV20260610001"）

        Returns:
            匹配的请假 ORM 对象，不存在则返回 None
        """
        return self.db.query(StudentLeaveRequest).filter(
            StudentLeaveRequest.request_no == request_no
        ).first()

    # ----------------------------------------------------------
    # 写入操作
    # ----------------------------------------------------------

    def create(self, **kwargs) -> StudentLeaveRequest:
        """创建请假记录

        接收关键字参数，直接映射到 StudentLeaveRequest 的字段。
        由 Service 层负责组装参数（含 request_no、student_id 等）。

        Args:
            **kwargs: 字段键值对，如 create(student_id=1, leave_type="sick", ...)

        Returns:
            已创建但尚未提交的 ORM 对象（Service 层负责 commit）
        """
        leave = StudentLeaveRequest(**kwargs)
        self.db.add(leave)
        # flush 后 leave.id 会被自动赋值，但事务还需 Service 层 commit
        self.db.flush()
        return leave

    def update(
        self,
        leave_id: int,
        **kwargs,
    ) -> Optional[StudentLeaveRequest]:
        """更新请假记录的指定字段

        只更新传入的字段，未传入的字段保持不变。
        常用于更新状态、审批信息等。

        Args:
            leave_id: 要更新的请假申请 ID
            **kwargs: 要更新的字段键值对，如 update_status(status="approved")

        Returns:
            更新后的 ORM 对象，不存在则返回 None

        使用示例：
            dao.update(leave_id=1, status="approved", approver_employee_id=2)
        """
        leave = self.get_by_id(leave_id)
        if leave is None:
            return None

        for field, value in kwargs.items():
            setattr(leave, field, value)

        self.db.flush()
        return leave

    # ----------------------------------------------------------
    # 列表查询（带分页）
    # ----------------------------------------------------------

    def list_by_student(
        self,
        student_id: int,
        query: PageQuery,
        status: Optional[LeaveStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[list[StudentLeaveRequest], int]:
        """查询某学生的请假列表（分页 + 可选筛选）

        Args:
            student_id: 学生 ID（必填，用于权限过滤）
            query: 分页参数（page, page_size）
            status: 按状态筛选（可选）
            date_from: 开始时间范围起始（可选，按 create_time）
            date_to: 开始时间范围结束（可选，按 create_time）

        Returns:
            (当前页数据列表, 符合条件的总记录数)
        """
        # 构建基础查询条件
        filters = [StudentLeaveRequest.student_id == student_id]

        if status is not None:
            filters.append(StudentLeaveRequest.status == status.value)
        if date_from is not None:
            filters.append(StudentLeaveRequest.create_time >= date_from)
        if date_to is not None:
            filters.append(StudentLeaveRequest.create_time <= date_to)

        return self._paginated_query(filters, query)

    def list_all_pending(
        self,
        query: PageQuery,
    ) -> tuple[list[StudentLeaveRequest], int]:
        """查询所有待审批的请假列表（分页）

        员工端的"待审批"入口，显示所有 status=pending 的记录。
        审批后 approver_employee_id 才被赋值，所以待审批时不按员工筛选。

        Args:
            query: 分页参数

        Returns:
            (当前页数据列表, 符合条件的总记录数)
        """
        filters = [StudentLeaveRequest.status == LeaveStatus.PENDING.value]
        return self._paginated_query(filters, query)

    def list_approval_history(
        self,
        employee_id: int,
        query: PageQuery,
        status: Optional[LeaveStatus] = None,
    ) -> tuple[list[StudentLeaveRequest], int]:
        """查询某员工审批过的请假历史（分页 + 可选状态筛选）

        用于员工查看自己处理过的审批记录（已通过/已驳回）。
        只有 approver_employee_id 等于当前员工 ID 的记录才会被查到。

        Args:
            employee_id: 员工 ID（employee_profile.id）
            query: 分页参数
            status: 按状态筛选（可选，如 approved / rejected）

        Returns:
            (当前页数据列表, 符合条件的总记录数)
        """
        filters = [StudentLeaveRequest.approver_employee_id == employee_id]

        if status is not None:
            filters.append(StudentLeaveRequest.status == status.value)

        return self._paginated_query(filters, query)

    # ----------------------------------------------------------
    # 计数查询
    # ----------------------------------------------------------

    def count_pending(self) -> int:
        """统计所有待审批的请假数量

        员工首页角标显示待处理数量。

        Returns:
            待审批数量
        """
        return self.db.query(StudentLeaveRequest).filter(
            StudentLeaveRequest.status == LeaveStatus.PENDING.value,
        ).count()

    # ----------------------------------------------------------
    # 私有方法
    # ----------------------------------------------------------

    def _paginated_query(
        self,
        filters: list,
        query: PageQuery,
    ) -> tuple[list[StudentLeaveRequest], int]:
        """执行分页查询的通用方法

        组装 filter → order_by → offset/limit → count，避免每个方法重复写。

        Args:
            filters: SQLAlchemy 过滤条件列表
            query: 分页参数

        Returns:
            (当前页数据, 总记录数)
        """
        # 构建查询对象
        q = self.db.query(StudentLeaveRequest).filter(*filters)

        # 先取总数，再取分页数据（顺序重要：count 不受 offset/limit 影响）
        total = q.count()

        # 按创建时间倒序排列，最新的在前
        items = q.order_by(
            desc(StudentLeaveRequest.create_time)
        ).offset(
            (query.page - 1) * query.page_size
        ).limit(
            query.page_size
        ).all()

        return items, total
