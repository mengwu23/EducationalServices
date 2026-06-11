from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.customer_analysis_record import CustomerAnalysisRecord


class CustomerJudgementDAO:
    """客户画像研判记录数据访问层。"""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # 单条查询
    # ------------------------------------------------------------------

    def get_by_id(self, record_id: int) -> CustomerAnalysisRecord | None:
        stmt = select(CustomerAnalysisRecord).where(
            CustomerAnalysisRecord.id == record_id,
            CustomerAnalysisRecord.is_delete == 0,
        )
        return self.db.scalar(stmt)

    def get_by_analysis_no(self, analysis_no: str) -> CustomerAnalysisRecord | None:
        stmt = select(CustomerAnalysisRecord).where(
            CustomerAnalysisRecord.analysis_no == analysis_no,
            CustomerAnalysisRecord.is_delete == 0,
        )
        return self.db.scalar(stmt)

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def add(self, record: CustomerAnalysisRecord) -> CustomerAnalysisRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def update(self, record: CustomerAnalysisRecord) -> CustomerAnalysisRecord:
        self.db.flush()
        return record

    # ------------------------------------------------------------------
    # 列表查询
    # ------------------------------------------------------------------

    def list_records(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        lead_id: int | None = None,
        match_level: str | None = None,
        date_start: date | None = None,
        date_end: date | None = None,
    ) -> tuple[list[CustomerAnalysisRecord], int]:
        stmt = select(CustomerAnalysisRecord).where(CustomerAnalysisRecord.is_delete == 0)

        if status:
            stmt = stmt.where(CustomerAnalysisRecord.status == status)
        if lead_id is not None:
            stmt = stmt.where(CustomerAnalysisRecord.lead_id == lead_id)
        if match_level:
            stmt = stmt.where(CustomerAnalysisRecord.match_level == match_level)
        if date_start:
            stmt = stmt.where(func.date(CustomerAnalysisRecord.create_time) >= date_start)
        if date_end:
            stmt = stmt.where(func.date(CustomerAnalysisRecord.create_time) <= date_end)

        # 总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        # 分页
        stmt = stmt.order_by(CustomerAnalysisRecord.create_time.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = list(self.db.scalars(stmt).all())

        return rows, total

    # ------------------------------------------------------------------
    # 编号生成
    # ------------------------------------------------------------------

    def generate_analysis_no(self) -> str:
        year = date.today().year
        count_stmt = select(func.count(CustomerAnalysisRecord.id)).where(
            func.year(CustomerAnalysisRecord.create_time) == year,
        )
        year_count = self.db.scalar(count_stmt) or 0
        next_seq = year_count + 1
        return f"CA{year}{next_seq:03d}"
