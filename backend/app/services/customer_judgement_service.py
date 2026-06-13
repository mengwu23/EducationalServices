from datetime import datetime
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.app.common.exceptions import NotFoundError, ReportGenerationError
from backend.app.core.config import Settings, get_settings
from backend.app.core.security import CurrentUser, require_roles
from backend.app.daos.customer_judgement_dao import CustomerJudgementDAO
from backend.app.integrations.dify_client import DifyClient
from backend.app.models.customer_analysis_record import CustomerAnalysisRecord
from backend.app.schemas.customer_judgement_schema import (
    CustomerJudgementRequest,
    JudgementListRequest,
)
from backend.app.services.audit_log_service import AuditLogService


class CustomerJudgementService:
    """客户画像研判业务逻辑层。"""

    def __init__(
        self,
        db: Session,
        dify_client: DifyClient | None = None,
        settings: Settings | None = None,
    ):
        self.db = db
        self.settings = settings or get_settings()
        self.dao = CustomerJudgementDAO(db)
        self.audit_service = AuditLogService(db)
        self.dify_client = dify_client or DifyClient(self.settings)

    # ------------------------------------------------------------------
    # 核心研判
    # ------------------------------------------------------------------

    def analyze_customer(
        self,
        request: CustomerJudgementRequest,
        user: CurrentUser,
        files: list[UploadFile] | None = None,
    ) -> dict[str, Any]:
        """提交客户信息进行智能画像研判，支持可选的附件上传。"""
        require_roles(user, {"admin", "manager", "employee"})
        trace_id = f"cj-{uuid4().hex[:12]}"
        analysis_no = self.dao.generate_analysis_no()

        # 处理文件上传：先上传到 Dify 获取 file_id
        file_ids: list[str] = []
        file_names: list[str] = []
        if files:
            for f in files:
                if f.filename:
                    content = f.file.read()
                    if not content:
                        continue
                    upload_result = self.dify_client.upload_file(
                        file_path=f.filename,
                        file_content=content,
                        mime_type=f.content_type or "application/octet-stream",
                    )
                    file_ids.append(upload_result.get("id", ""))
                    file_names.append(f.filename)

        source_type = "text"
        if file_names:
            source_type = "pdf简历" if any(n.lower().endswith(".pdf") for n in file_names) else "excel表格" if any(n.lower().endswith((".xls", ".xlsx")) for n in file_names) else "text"

        record = CustomerAnalysisRecord(
            analysis_no=analysis_no,
            source_type=source_type,
            source_file_name=", ".join(file_names) if file_names else None,
            raw_content=request.text,
            target_product=request.target_product,
            lead_id=None,
            status="pending",
            submitter_user_id=None,
        )

        try:
            self.dao.add(record)
            result = self.dify_client.call_customer_judgement(
                customer_info_text=request.text,
                sys_query=request.sys_query,
                trace_id=trace_id,
                file_ids=file_ids if file_ids else None,
            )

            # 判断是否批量结果（JSON数组）
            if isinstance(result, list) and len(result) > 0:
                # 批量：为每位客户创建独立记录
                records_detail = []
                first_record_id = record.id

                for i, item in enumerate(result):
                    batch_no = f"{analysis_no}-{item.get('customer_index', i + 1):02d}"
                    batch_record = CustomerAnalysisRecord(
                        analysis_no=batch_no,
                        source_type=source_type,
                        source_file_name=", ".join(file_names) if file_names else None,
                        raw_content=request.text,
                        target_product=request.target_product,
                        lead_id=None,
                        status="completed",
                        submitter_user_id=None,
                        is_target_customer=1 if item.get("is_target_customer") else 0,
                        match_score=item.get("overall_match_score"),
                        match_level=item.get("overall_match_level"),
                        reason_summary=item.get("executive_summary") or item.get("reason_summary"),
                        suggestion=item.get("suggestion"),
                    )
                    self.dao.add(batch_record)
                    self.audit_service.record(
                        user,
                        action_type="customer_judge",
                        biz_object_type="customer_analysis_record",
                        biz_object_id=batch_record.id,
                        trace_id=trace_id,
                        after_json={
                            "analysis_no": batch_no,
                            "batch": True,
                            "customer_name": item.get("customer_name", ""),
                            "match_score": batch_record.match_score,
                            "match_level": batch_record.match_level,
                        },
                    )
                    records_detail.append(self._record_to_detail(batch_record))

                # 删除初始的空 pending 记录
                self.db.delete(record)
                self.db.commit()

                # 返回批量结果
                return {
                    "batch": True,
                    "total_customers": len(result),
                    "records": records_detail,
                }
            else:
                # 单客户：原有逻辑
                item = result if isinstance(result, dict) else result[0] if isinstance(result, list) else result

                record.is_target_customer = 1 if item.get("is_target_customer") else 0
                record.match_score = item.get("overall_match_score")
                record.match_level = item.get("overall_match_level")
                record.reason_summary = item.get("executive_summary") or item.get("reason_summary")
                record.suggestion = item.get("suggestion")
                record.status = "completed"

                self.dao.update(record)
                self.audit_service.record(
                    user,
                    action_type="customer_judge",
                    biz_object_type="customer_analysis_record",
                    biz_object_id=record.id,
                    trace_id=trace_id,
                    after_json={
                        "analysis_no": analysis_no,
                        "status": "completed",
                        "match_score": record.match_score,
                        "match_level": record.match_level,
                    },
                )
                self.db.commit()
                self.db.refresh(record)
                return self._record_to_detail(record)

        except Exception as exc:
            self.db.rollback()
            record.status = "failed"
            record.reason_summary = f"研判失败：{exc}"
            self.dao.update(record)
            self.audit_service.record(
                user,
                action_type="customer_judge",
                biz_object_type="customer_analysis_record",
                biz_object_id=record.id,
                trace_id=trace_id,
                result="fail",
                error_message=str(exc),
            )
            self.db.commit()
            raise ReportGenerationError(f"客户画像研判失败：{exc}") from exc

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def get_analysis_record(self, record_id: int, user: CurrentUser) -> dict[str, Any]:
        """获取单条研判记录详情。"""
        require_roles(user, {"admin", "manager", "employee"})
        record = self.dao.get_by_id(record_id)
        if not record:
            raise NotFoundError("研判记录不存在")
        return self._record_to_detail(record)

    def list_analysis_records(self, request: JudgementListRequest, user: CurrentUser) -> dict[str, Any]:
        """分页查询研判记录列表。"""
        require_roles(user, {"admin", "manager", "employee"})
        rows, total = self.dao.list_records(
            page=request.page,
            page_size=request.page_size,
            status=request.status,
            lead_id=request.lead_id,
            match_level=request.match_level,
            date_start=request.date_start,
            date_end=request.date_end,
        )
        items = [self._record_to_item(row) for row in rows]
        return {
            "total": total,
            "page": request.page,
            "page_size": request.page_size,
            "items": items,
        }

    # ------------------------------------------------------------------
    # 序列化辅助
    # ------------------------------------------------------------------

    def _record_to_item(self, record: CustomerAnalysisRecord) -> dict[str, Any]:
        """将 ORM 记录转为列表项字典。"""
        return {
            "id": record.id,
            "analysis_no": record.analysis_no,
            "source_type": record.source_type,
            "source_file_name": record.source_file_name,
            "target_product": record.target_product,
            "lead_id": record.lead_id,
            "is_target_customer": record.is_target_customer,
            "match_score": float(record.match_score) if record.match_score is not None else None,
            "match_level": record.match_level,
            "reason_summary": record.reason_summary,
            "suggestion": record.suggestion,
            "status": record.status,
            "submitter_user_id": record.submitter_user_id,
            "create_time": record.create_time.isoformat() if record.create_time else None,
            "update_time": record.update_time.isoformat() if record.update_time else None,
        }

    def _record_to_detail(self, record: CustomerAnalysisRecord) -> dict[str, Any]:
        """将 ORM 记录转为详情字典。"""
        detail = self._record_to_item(record)
        detail["raw_content"] = record.raw_content
        detail["executive_summary"] = record.reason_summary
        detail["ai_result"] = {
            "is_target_customer": bool(record.is_target_customer) if record.is_target_customer is not None else None,
            "overall_match_score": float(record.match_score) if record.match_score is not None else None,
            "overall_match_level": record.match_level,
            "executive_summary": record.reason_summary,
            "reason_summary": record.reason_summary,
            "suggestion": record.suggestion,
        }
        return detail
