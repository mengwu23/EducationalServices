from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session, aliased

from backend.app.common.enums import ReportType
from backend.app.models.academic_event import AcademicEvent
from backend.app.models.audit_log import AiToolCallLog, AuditLog
from backend.app.models.crm_lead import CrmLead
from backend.app.models.customer_analysis_record import CustomerAnalysisRecord
from backend.app.models.draft import AiDraft
from backend.app.models.employee_daily_report import EmployeeDailyReport
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.event_registration import EventRegistration
from backend.app.models.report import AiReport, ReportExportRecord
from backend.app.models.student_feedback_ticket import StudentFeedbackTicket
from backend.app.models.student_profile import StudentProfile
from backend.app.models.student_psych_alert import StudentPsychAlert
from backend.app.models.student_psych_profile import StudentPsychProfile
from backend.app.models.sys_department import SysDepartment


class ReportDAO:
    def __init__(self, db: Session):
        self.db = db

    def query_report_source_data(
        self,
        report_type: str,
        date_start: date,
        date_end: date,
        department_id: int | None = None,
        owner_user_id: int | None = None,
    ) -> dict[str, Any]:
        if report_type == ReportType.COMPLAINT_WEEKLY:
            return self._query_complaint_weekly(date_start, date_end, department_id)
        if report_type == ReportType.CUSTOMER_OPERATION:
            return self._query_customer_operation(date_start, date_end, department_id, owner_user_id)
        if report_type == ReportType.EMPLOYEE_DAILY_SUMMARY:
            return self._query_employee_daily_summary(date_start, department_id)
        if report_type == ReportType.EMPLOYEE_WEEKLY_SUMMARY:
            return self._query_employee_weekly_summary(date_start, date_end, department_id)
        if report_type == ReportType.STUDENT_PSYCH_WEEKLY:
            return self._query_student_psych_weekly(date_start, date_end, department_id)
        raise ValueError(f"不支持的报告类型：{report_type}")

    def _query_complaint_weekly(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        stmt = (
            select(StudentFeedbackTicket.status, func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
            )
            .group_by(StudentFeedbackTicket.status)
        )
        if department_id is not None:
            stmt = stmt.where(EmployeeProfile.department_id == department_id, EmployeeProfile.is_delete == 0)
        rows = self.db.execute(stmt).all()
        status_counts = {status: count for status, count in rows}
        total = sum(status_counts.values())
        category_rows = self.db.execute(
            select(StudentFeedbackTicket.category, func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
            .group_by(StudentFeedbackTicket.category)
        ).all()
        category_counts = {cat or "未分类": count for cat, count in category_rows}
        type_rows = self.db.execute(
            select(StudentFeedbackTicket.ticket_type, func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
            .group_by(StudentFeedbackTicket.ticket_type)
        ).all()
        ticket_type_counts = {tt or "未分类": count for tt, count in type_rows}
        time_rows = self.db.execute(
            select(StudentFeedbackTicket.create_time, StudentFeedbackTicket.close_time)
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.close_time.is_not(None),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
        ).all()
        hours_list = [
            (close - create).total_seconds() / 3600
            for create, close in time_rows
        ]
        avg_hours = round(sum(hours_list) / len(hours_list), 1) if hours_list else None

        # 满意度均分
        dept_filter_sat = [
            EmployeeProfile.department_id == department_id,
            EmployeeProfile.is_delete == 0,
        ] if department_id is not None else []
        sat_stmt = (
            select(func.avg(StudentFeedbackTicket.satisfaction_score))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
                StudentFeedbackTicket.satisfaction_score.is_not(None),
                *dept_filter_sat,
            )
        )
        sat_val = self.db.scalar(sat_stmt)
        satisfaction_avg = round(float(sat_val), 1) if sat_val is not None else None

        # 优先级分布
        priority_rows = self.db.execute(
            select(StudentFeedbackTicket.priority_level, func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(date_start, date_end),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
            .group_by(StudentFeedbackTicket.priority_level)
        ).all()
        priority_counts = {p or "未设置": c for p, c in priority_rows}

        # 同环比
        period_days = (date_end - date_start).days or 7
        prev_start = date_start - timedelta(days=period_days)
        prev_end = date_end - timedelta(days=period_days)
        prev_count_stmt = (
            select(func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                func.date(StudentFeedbackTicket.create_time).between(prev_start, prev_end),
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
        )
        prev_week_total = self.db.scalar(prev_count_stmt) or 0
        wow_delta_pct = round((total - prev_week_total) / prev_week_total * 100, 1) if prev_week_total > 0 else (100 if total > 0 else 0)
        wow_trend_label = "上升" if wow_delta_pct > 5 else ("下降" if wow_delta_pct < -5 else "持平")

        # 超期工单（>48h 未闭环）
        deadline = datetime.now() - timedelta(hours=48)
        overdue_stmt = (
            select(func.count(StudentFeedbackTicket.id))
            .outerjoin(EmployeeProfile, StudentFeedbackTicket.handler_employee_id == EmployeeProfile.id)
            .where(
                StudentFeedbackTicket.status.in_(["pending", "processing"]),
                StudentFeedbackTicket.create_time < deadline,
                StudentFeedbackTicket.is_delete == 0,
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0 if department_id is not None else text('1=1'),
            )
        )
        overdue_ticket_count = self.db.scalar(overdue_stmt) or 0

        # 投诉分类中文映射
        CATEGORY_MAP = {
            "course": "教学课程", "service": "服务顾问",
            "visa": "签证办理", "school": "院校申请",
            "life": "生活服务", "finance": "财务费用",
        }
        category_cn_counts = {CATEGORY_MAP.get(k, k): v for k, v in category_counts.items()}

        return {
            "report_type": ReportType.COMPLAINT_WEEKLY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_tickets": total,
            "status_counts": status_counts,
            "category_counts": category_counts,
            "category_cn_counts": category_cn_counts,
            "ticket_type_counts": ticket_type_counts,
            "avg_processing_hours": round(float(avg_hours), 1) if avg_hours else None,
            "satisfaction_avg": satisfaction_avg,
            "priority_counts": priority_counts,
            "prev_week_total": prev_week_total,
            "wow_delta_pct": wow_delta_pct,
            "wow_trend_label": wow_trend_label,
            "overdue_ticket_count": overdue_ticket_count,
        }

    def _query_customer_operation(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
        owner_user_id: int | None,
    ) -> dict[str, Any]:
        from datetime import timedelta

        employee_filters = []
        if department_id is not None:
            employee_filters.append(EmployeeProfile.department_id == department_id)
        if owner_user_id is not None:
            employee_filters.append(EmployeeProfile.user_id == owner_user_id)
        employee_filters.append(EmployeeProfile.is_delete == 0)

        lead_stmt = (
            select(func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(func.date(CrmLead.create_time).between(date_start, date_end), CrmLead.is_delete == 0, *employee_filters)
        )
        analysis_stmt = (
            select(func.count(CustomerAnalysisRecord.id))
            .join(CrmLead, CustomerAnalysisRecord.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(CustomerAnalysisRecord.create_time).between(date_start, date_end),
                CustomerAnalysisRecord.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
        )
        registration_stmt = (
            select(func.count(EventRegistration.id))
            .join(CrmLead, EventRegistration.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(EventRegistration.create_time).between(date_start, date_end),
                EventRegistration.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
        )


        source_rows = self.db.execute(
            select(CrmLead.source_channel, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(func.date(CrmLead.create_time).between(date_start, date_end), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.source_channel)
        ).all()
        lead_source_breakdown = {s if s is not None else "未知渠道": c for s, c in source_rows}

        status_rows = self.db.execute(
            select(CrmLead.status, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.status)
        ).all()
        lead_status_breakdown = {s if s is not None else "未知状态": c for s, c in status_rows}

        result_rows = self.db.execute(
            select(CustomerAnalysisRecord.match_level, func.count(CustomerAnalysisRecord.id))
            .join(CrmLead, CustomerAnalysisRecord.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(CustomerAnalysisRecord.create_time).between(date_start, date_end),
                CustomerAnalysisRecord.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
            .group_by(CustomerAnalysisRecord.match_level)
        ).all()
        analysis_result_breakdown = {r if r is not None else "未分级": c for r, c in result_rows}

        event_status_rows = self.db.execute(
            select(EventRegistration.registration_status, func.count(EventRegistration.id))
            .join(CrmLead, EventRegistration.lead_id == CrmLead.id)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(
                func.date(EventRegistration.create_time).between(date_start, date_end),
                EventRegistration.is_delete == 0,
                CrmLead.is_delete == 0,
                *employee_filters,
            )
            .group_by(EventRegistration.registration_status)
        ).all()
        event_registration_breakdown = {s if s is not None else "未知状态": c for s, c in event_status_rows}

        new_leads = self.db.scalar(lead_stmt) or 0
        analysis_records = self.db.scalar(analysis_stmt) or 0
        event_regs = self.db.scalar(registration_stmt) or 0

        # === 同环比数据：上周同期 ===
        period_days = (date_end - date_start).days or 7
        prev_start = date_start - timedelta(days=period_days)
        prev_end = date_end - timedelta(days=period_days)
        prev_lead_stmt = (
            select(func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(func.date(CrmLead.create_time).between(prev_start, prev_end), CrmLead.is_delete == 0, *employee_filters)
        )
        prev_leads = self.db.scalar(prev_lead_stmt) or 0
        prev_analysis = self.db.scalar(analysis_stmt.where(func.date(CustomerAnalysisRecord.create_time).between(prev_start, prev_end))) or 0
        prev_events = self.db.scalar(registration_stmt.where(func.date(EventRegistration.create_time).between(prev_start, prev_end))) or 0
        lead_delta_pct = round((new_leads - prev_leads) / prev_leads * 100, 1) if prev_leads > 0 else (100 if new_leads > 0 else 0)
        trend_label = "上升" if lead_delta_pct > 5 else ("下降" if lead_delta_pct < -5 else "持平")

        # === 流失归因：按渠道和阶段细分 ===
        lost_statuses = ["lost", "invalid"]
        churn_source_rows = self.db.execute(
            select(CrmLead.source_channel, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(CrmLead.status.in_(lost_statuses), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.source_channel)
        ).all()
        churn_source_breakdown = {s or "未归类": c for s, c in churn_source_rows}

        churn_stage_rows = self.db.execute(
            select(CrmLead.status, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(CrmLead.status.in_(lost_statuses), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.status)
        ).all()
        churn_stage_breakdown = {s or "未归类": c for s, c in churn_stage_rows}

        # 客群深度画像：四维 GROUP BY
        portrait_breakdown: dict[str, dict[str, int]] = {}
        for field_attr, field_key in [
            (CrmLead.target_country, "target_country_counts"),
            (CrmLead.target_program, "target_program_counts"),
            (CrmLead.budget_range, "budget_range_counts"),
            (CrmLead.education_level, "education_level_counts"),
        ]:
            pb_rows = self.db.execute(
                select(field_attr, func.count(CrmLead.id))
                .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
                .where(func.date(CrmLead.create_time).between(date_start, date_end), CrmLead.is_delete == 0, *employee_filters)
                .group_by(field_attr)
            ).all()
            portrait_breakdown[field_key] = {v if v else "未填写": c for v, c in pb_rows}

        # 客群多维组合聚类：按 (意向国家 + 意向项目 + 预算区间) 组合分组，
        # 输出"美国+计算机硕士+50-80万（3人）"这样的真聚类客群，取 Top-N。
        cluster_rows = self.db.execute(
            select(
                CrmLead.target_country,
                CrmLead.target_program,
                CrmLead.budget_range,
                func.count(CrmLead.id),
            )
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(func.date(CrmLead.create_time).between(date_start, date_end), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.target_country, CrmLead.target_program, CrmLead.budget_range)
            .order_by(func.count(CrmLead.id).desc())
        ).all()
        cluster_breakdown = [
            {
                "target_country": country or "未填写",
                "target_program": program or "未填写",
                "budget_range": budget or "未填写",
                "count": count,
                "label": f"{country or '未填写'}+{program or '未填写'}+{budget or '未填写'}",
            }
            for country, program, budget, count in cluster_rows
            if count > 0
        ][:5]

        # 流失归因
        lost_reason_rows = self.db.execute(
            select(CrmLead.lost_reason, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(CrmLead.status.in_(lost_statuses), CrmLead.is_delete == 0, *employee_filters)
            .group_by(CrmLead.lost_reason)
        ).all()
        lost_reason_counts = {r if r else "未填写归因": c for r, c in lost_reason_rows}

        # === 成交客户专项：按 signed_time 落在周期内统计 ===
        signed_filters = [
            CrmLead.status == "signed",
            CrmLead.signed_time.is_not(None),
            func.date(CrmLead.signed_time).between(date_start, date_end),
            CrmLead.is_delete == 0,
            *employee_filters,
        ]
        signed_count = self.db.scalar(
            select(func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(*signed_filters)
        ) or 0

        # 成交客户高价值特征：渠道来源分布
        signed_source_rows = self.db.execute(
            select(CrmLead.source_channel, func.count(CrmLead.id))
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(*signed_filters)
            .group_by(CrmLead.source_channel)
        ).all()
        signed_source_breakdown = {s if s is not None else "未知渠道": c for s, c in signed_source_rows}

        # 平均转化周期（线索创建 → 签约，天）
        signed_time_rows = self.db.execute(
            select(CrmLead.create_time, CrmLead.signed_time)
            .join(EmployeeProfile, CrmLead.owner_employee_id == EmployeeProfile.id)
            .where(*signed_filters)
        ).all()
        cycle_days_list = [
            (signed - created).total_seconds() / 86400
            for created, signed in signed_time_rows
            if created and signed
        ]
        avg_conversion_days = round(sum(cycle_days_list) / len(cycle_days_list), 1) if cycle_days_list else None
        signed_conversion_rate = round(signed_count / new_leads * 100, 1) if new_leads > 0 else 0

        return {
            "report_type": ReportType.CUSTOMER_OPERATION,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "owner_user_id": owner_user_id,
            "new_leads": new_leads,
            "analysis_records": analysis_records,
            "event_registrations": event_regs,
            "lead_source_breakdown": lead_source_breakdown,
            "lead_status_breakdown": lead_status_breakdown,
            "analysis_result_breakdown": analysis_result_breakdown,
            "event_registration_breakdown": event_registration_breakdown,
            "prev_period": {
                "date_start": str(prev_start),
                "date_end": str(prev_end),
                "leads": prev_leads,
                "analysis": prev_analysis,
                "events": prev_events,
            },
            "lead_trend": {"delta_pct": lead_delta_pct, "label": trend_label},
            "churn_source_breakdown": churn_source_breakdown,
            "churn_stage_breakdown": churn_stage_breakdown,
            "portrait_breakdown": portrait_breakdown,
            "cluster_breakdown": cluster_breakdown,
            "lost_reason_counts": lost_reason_counts,
            "signed_count": signed_count,
            "signed_source_breakdown": signed_source_breakdown,
            "avg_conversion_days": avg_conversion_days,
            "signed_conversion_rate": signed_conversion_rate,
        }

    def _query_employee_daily_summary(
        self,
        report_date: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        filters = [
            EmployeeDailyReport.report_date == report_date,
            EmployeeDailyReport.is_delete == 0,
        ]
        if department_id is not None:
            filters.append(EmployeeDailyReport.department_id == department_id)

        status_counts = self._count_employee_daily_status(filters)

        progress_rows = self.db.execute(
            select(EmployeeDailyReport.summary, EmployeeDailyReport.key_progress, EmployeeProfile.employee_name)
            .join(EmployeeProfile, EmployeeDailyReport.employee_id == EmployeeProfile.id, isouter=True)
            .where(*filters, or_(EmployeeDailyReport.summary.is_not(None), EmployeeDailyReport.key_progress.is_not(None)))
            .limit(5)
        ).all()
        key_progress_items = [
            {"emp": row.employee_name or "", "text": (row.key_progress or row.summary or "")[:120]}
            for row in progress_rows if (row.key_progress or row.summary or "").strip()
        ]

        risk_rows = self.db.execute(
            select(EmployeeDailyReport.risks, EmployeeProfile.employee_name)
            .join(EmployeeProfile, EmployeeDailyReport.employee_id == EmployeeProfile.id, isouter=True)
            .where(*filters, EmployeeDailyReport.risks.is_not(None), EmployeeDailyReport.risks != "")
            .limit(5)
        ).all()
        risk_items = [
            {"emp": row.employee_name or "", "text": (row.risks or "")[:120]}
            for row in risk_rows
        ]

        sub_list_rows = self.db.execute(
            select(EmployeeProfile.employee_name, EmployeeDailyReport.report_status,
                   EmployeeDailyReport.risks, EmployeeDailyReport.tomorrow_plan)
            .join(EmployeeDailyReport, EmployeeProfile.id == EmployeeDailyReport.employee_id, isouter=True)
            .where(
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0,
            )
            .limit(20)
        ).all()
        dept_emp_count = len(sub_list_rows)
        submission_rate = f"{round(sum(status_counts.values()) / dept_emp_count * 100, 1)}%" if dept_emp_count > 0 else "N/A"

        return {
            "report_type": ReportType.EMPLOYEE_DAILY_SUMMARY,
            "date_start": str(report_date),
            "date_end": str(report_date),
            "department_id": department_id,
            "total_reports": sum(status_counts.values()),
            "status_counts": status_counts,
            "submitted_reports": status_counts.get("submitted", 0),
            "draft_reports": status_counts.get("draft", 0),
            "archived_reports": status_counts.get("archived", 0),
            "risk_reports": self._count_employee_daily_text_field(filters, EmployeeDailyReport.risks),
            "tomorrow_plan_reports": self._count_employee_daily_text_field(filters, EmployeeDailyReport.tomorrow_plan),
            "key_progress_items": key_progress_items,
            "risk_items": risk_items,
            "submission_rate": submission_rate,
            "employee_submission_list": [dict(r._mapping) for r in sub_list_rows[:10]],
        }

    def _query_employee_weekly_summary(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        filters = [
            EmployeeDailyReport.report_date.between(date_start, date_end),
            EmployeeDailyReport.is_delete == 0,
        ]
        if department_id is not None:
            filters.append(EmployeeDailyReport.department_id == department_id)

        trend_rows = self.db.execute(
            select(EmployeeDailyReport.report_date, func.count(EmployeeDailyReport.id))
            .where(*filters)
            .group_by(EmployeeDailyReport.report_date)
            .order_by(EmployeeDailyReport.report_date)
        ).all()

        total = self.db.scalar(select(func.count(EmployeeDailyReport.id)).where(*filters)) or 0
        distinct = self.db.scalar(
            select(func.count(func.distinct(EmployeeDailyReport.employee_id))).where(*filters)
        ) or 0
        trend = {str(report_date): count for report_date, count in trend_rows}
        risk_count = self._count_employee_daily_text_field(filters, EmployeeDailyReport.risks)

        dept_emp_count = self.db.scalar(
            select(func.count(EmployeeProfile.id))
            .where(
                EmployeeProfile.department_id == department_id if department_id is not None else text('1=1'),
                EmployeeProfile.is_delete == 0,
            )
        ) or 1
        week_days = max(len(trend), 1)
        week_submission_rate = f"{round(total / (dept_emp_count * week_days) * 100, 1)}%" if dept_emp_count > 0 else "N/A"

        risk_text_rows = self.db.execute(
            select(EmployeeDailyReport.risks)
            .where(*filters, EmployeeDailyReport.risks.is_not(None), EmployeeDailyReport.risks != "")
            .limit(30)
        ).all()
        risk_keywords: dict[str, int] = {}
        for (rtext,) in risk_text_rows:
            for kw in ["客户", "签约", "投诉", "进度", "沟通", "时间", "资料", "审核", "跟进", "压力"]:
                if kw in (rtext or ""):
                    risk_keywords[kw] = risk_keywords.get(kw, 0) + 1
        top_risk_themes = sorted(risk_keywords.items(), key=lambda x: x[1], reverse=True)[:5]

        trend_dates = sorted(trend.keys())
        peak_day = max(trend, key=trend.get) if trend else None
        valley_day = min(trend, key=trend.get) if trend else None

        return {
            "report_type": ReportType.EMPLOYEE_WEEKLY_SUMMARY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_reports": total,
            "distinct_employees": distinct,
            "status_counts": self._count_employee_daily_status(filters),
            "daily_trend": trend,
            "risk_reports": risk_count,
            "week_submission_rate": week_submission_rate,
            "top_risk_themes": top_risk_themes,
            "peak_submission_day": peak_day,
            "valley_submission_day": valley_day,
        }

    def _count_employee_daily_status(self, filters: list[Any]) -> dict[str, int]:
        rows = self.db.execute(
            select(EmployeeDailyReport.report_status, func.count(EmployeeDailyReport.id))
            .where(*filters)
            .group_by(EmployeeDailyReport.report_status)
        ).all()
        return {status: count for status, count in rows}

    def _count_employee_daily_text_field(self, filters: list[Any], field) -> int:
        return (
            self.db.scalar(
                select(func.count(EmployeeDailyReport.id)).where(
                    *filters,
                    field.is_not(None),
                    field != "",
                )
            )
            or 0
        )

    def _query_student_psych_weekly(
        self,
        date_start: date,
        date_end: date,
        department_id: int | None,
    ) -> dict[str, Any]:
        profile_stmt = (
            select(StudentPsychProfile.risk_level, func.count(StudentPsychProfile.id))
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
            )
            .group_by(StudentPsychProfile.risk_level)
        )
        profile_stmt = self._apply_student_department_filter(profile_stmt, department_id)
        risk_level_counts = {level: count for level, count in self.db.execute(profile_stmt).all()}

        emotion_stmt = (
            select(StudentPsychProfile.latest_emotion_tag, func.count(StudentPsychProfile.id))
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                StudentPsychProfile.latest_emotion_tag.is_not(None),
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
            )
            .group_by(StudentPsychProfile.latest_emotion_tag)
        )
        emotion_stmt = self._apply_student_department_filter(emotion_stmt, department_id)
        emotion_tag_counts = {tag: count for tag, count in self.db.execute(emotion_stmt).all()}

        avg_stmt = (
            select(func.avg(StudentPsychProfile.emotion_score))
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                StudentPsychProfile.emotion_score.is_not(None),
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
            )
        )
        avg_stmt = self._apply_student_department_filter(avg_stmt, department_id)
        average_score = self.db.scalar(avg_stmt)

        alert_status_stmt = (
            select(StudentPsychAlert.status, func.count(StudentPsychAlert.id))
            .join(StudentProfile, StudentPsychAlert.student_id == StudentProfile.id)
            .where(
                StudentPsychAlert.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychAlert.create_time).between(date_start, date_end),
            )
            .group_by(StudentPsychAlert.status)
        )
        alert_status_stmt = self._apply_student_department_filter(alert_status_stmt, department_id)
        alert_status_counts = {status: count for status, count in self.db.execute(alert_status_stmt).all()}

        alert_risk_stmt = (
            select(StudentPsychAlert.risk_level, func.count(StudentPsychAlert.id))
            .join(StudentProfile, StudentPsychAlert.student_id == StudentProfile.id)
            .where(
                StudentPsychAlert.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychAlert.create_time).between(date_start, date_end),
            )
            .group_by(StudentPsychAlert.risk_level)
        )
        alert_risk_stmt = self._apply_student_department_filter(alert_risk_stmt, department_id)
        alert_risk_level_counts = {level: count for level, count in self.db.execute(alert_risk_stmt).all()}

        # 每日互动趋势
        trend_stmt = (
            select(func.date(StudentPsychProfile.last_interaction_time), func.count(StudentPsychProfile.id))
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
            )
            .group_by(func.date(StudentPsychProfile.last_interaction_time))
            .order_by(func.date(StudentPsychProfile.last_interaction_time))
        )
        trend_stmt = self._apply_student_department_filter(trend_stmt, department_id)
        interaction_trend = {str(d): c for d, c in self.db.execute(trend_stmt).all()}

        # 高风险情绪摘要样本（最多5条，高风险优先）
        from sqlalchemy import case as sa_case
        sample_stmt = (
            select(StudentPsychProfile.student_id, StudentPsychProfile.emotion_summary)
            .join(StudentProfile, StudentPsychProfile.student_id == StudentProfile.id)
            .where(
                StudentPsychProfile.is_delete == 0,
                StudentProfile.is_delete == 0,
                func.date(StudentPsychProfile.last_interaction_time).between(date_start, date_end),
                StudentPsychProfile.emotion_summary.is_not(None),
                StudentPsychProfile.emotion_summary != "",
            )
            .order_by(
                sa_case(
                    (StudentPsychProfile.risk_level == "critical", 0),
                    (StudentPsychProfile.risk_level == "high", 1),
                    else_=2,
                )
            )
            .limit(5)
        )
        sample_stmt = self._apply_student_department_filter(sample_stmt, department_id)
        emotion_summary_samples = [
            {"student_id": sid, "summary": (s or "")[:200]}
            for sid, s in self.db.execute(sample_stmt).all()
        ]

        period_hint = self._derive_period_hint(date_start, date_end)

        return {
            "report_type": ReportType.STUDENT_PSYCH_WEEKLY,
            "date_start": str(date_start),
            "date_end": str(date_end),
            "department_id": department_id,
            "total_profiles": sum(risk_level_counts.values()),
            "risk_level_counts": risk_level_counts,
            "emotion_tag_counts": emotion_tag_counts,
            "average_emotion_score": round(float(average_score), 2) if average_score is not None else None,
            "total_alerts": sum(alert_status_counts.values()),
            "alert_status_counts": alert_status_counts,
            "alert_risk_level_counts": alert_risk_level_counts,
            "interaction_trend": interaction_trend,
            "emotion_summary_samples": emotion_summary_samples,
            "period_hint": period_hint,
        }

    def _derive_period_hint(self, date_start: date, date_end: date) -> str | None:
        """根据真实学业日历（academic_event）派生当前周期的留学阶段背景。

        优先读取周期内的公共学业事件（student_id 为空，如考试周/论文DDL/课程截止），
        识别落在统计周期内的真实节点。无匹配事件时返回 None，
        由报告渲染层回退到按月近似判断。
        """
        event_rows = self.db.execute(
            select(AcademicEvent.event_type, func.count(AcademicEvent.id))
            .where(
                AcademicEvent.student_id.is_(None),
                AcademicEvent.is_delete == 0,
                AcademicEvent.status == "active",
                func.date(AcademicEvent.deadline_time).between(date_start, date_end),
            )
            .group_by(AcademicEvent.event_type)
        ).all()
        if not event_rows:
            return None

        type_counts = {etype: cnt for etype, cnt in event_rows}
        exam_cnt = type_counts.get("exam", 0)
        paper_cnt = type_counts.get("paper_deadline", 0)
        course_cnt = type_counts.get("course_deadline", 0)

        if exam_cnt > 0:
            return f"当前周期内有 {exam_cnt} 场考试安排，处于考试季高压期，学业焦虑风险显著上升"
        if paper_cnt > 0 or course_cnt > 0:
            ddl_total = paper_cnt + course_cnt
            return f"当前周期内有 {ddl_total} 项论文/课程截止节点，处于作业冲刺期，时间管理压力较大"
        return "当前周期内有学业事项节点，建议结合学业节奏关注学生情绪波动"

    def _apply_student_department_filter(self, stmt, department_id: int | None):
        if department_id is None:
            return stmt
        Counselor = aliased(EmployeeProfile)
        Teacher = aliased(EmployeeProfile)
        return (
            stmt.outerjoin(Counselor, StudentProfile.counselor_employee_id == Counselor.id)
            .outerjoin(Teacher, StudentProfile.teacher_employee_id == Teacher.id)
            .where(
                or_(
                    and_(Counselor.department_id == department_id, Counselor.is_delete == 0),
                    and_(Teacher.department_id == department_id, Teacher.is_delete == 0),
                )
            )
        )

    def add_draft(self, draft: AiDraft) -> AiDraft:
        self.db.add(draft)
        self.db.flush()
        return draft

    def get_draft(self, draft_id: int) -> AiDraft | None:
        stmt = select(AiDraft).where(AiDraft.id == draft_id, AiDraft.is_deleted.is_(False))
        return self.db.scalar(stmt)

    def list_report_drafts(self) -> list[AiDraft]:
        stmt = (
            select(AiDraft)
            .where(AiDraft.biz_module == "report", AiDraft.is_deleted.is_(False))
            .order_by(AiDraft.create_time.desc())
        )
        return list(self.db.scalars(stmt).all())

    def add_report(self, report: AiReport) -> AiReport:
        self.db.add(report)
        self.db.flush()
        return report

    def get_report(self, report_id: int) -> AiReport | None:
        stmt = select(AiReport).where(AiReport.id == report_id, AiReport.is_deleted.is_(False))
        return self.db.scalar(stmt)

    def list_reports(self) -> list[AiReport]:
        stmt = select(AiReport).where(AiReport.is_deleted.is_(False)).order_by(AiReport.create_time.desc())
        return list(self.db.scalars(stmt).all())

    def add_export_record(self, record: ReportExportRecord) -> ReportExportRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def get_export_record(self, export_id: int) -> ReportExportRecord | None:
        stmt = select(ReportExportRecord).where(
            ReportExportRecord.id == export_id,
            ReportExportRecord.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def list_export_records(self, report_id: int) -> list[ReportExportRecord]:
        stmt = (
            select(ReportExportRecord)
            .where(ReportExportRecord.report_id == report_id, ReportExportRecord.is_deleted.is_(False))
            .order_by(ReportExportRecord.create_time.desc())
        )
        return list(self.db.scalars(stmt).all())

    def add_audit_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.flush()
        return log

    def add_tool_call_log(self, log: AiToolCallLog) -> AiToolCallLog:
        self.db.add(log)
        self.db.flush()
        return log
