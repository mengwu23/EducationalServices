"""学生智能助手 — 公共 DAO。"""

from sqlalchemy.orm import Session
from backend.app.models.faq_qa import FaqQa


class StudentAssistantDao:

    @staticmethod
    def search_life_faq(db: Session, keyword: str, limit: int = 10):
        q = db.query(FaqQa).filter(
            FaqQa.is_delete == 0, FaqQa.status == "enabled",
        ).filter(
            (FaqQa.question.like(f"%{keyword}%")) |
            (FaqQa.answer.like(f"%{keyword}%")) |
            (FaqQa.keywords.like(f"%{keyword}%")) |
            (FaqQa.category.like(f"%{keyword}%"))
        )
        total = q.count()
        items = q.order_by(FaqQa.sort_order).limit(limit).all()
        return items, total
