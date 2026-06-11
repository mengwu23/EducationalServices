import json
import re
import time
from typing import Any

import httpx

from backend.app.common.enums import ReportType
from backend.app.core.config import Settings, get_settings


class DifyClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def generate_report_draft(
        self,
        report_type: str,
        source_data: dict[str, Any],
        filters: dict[str, Any],
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        if self.settings.dify_mock_enabled:
            return self._mock_report_draft(report_type, source_data)
        return self._call_dify_report_workflow(report_type, source_data, filters, trace_id)

    def ask_onboarding_guide(
        self,
        question: str,
        category: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """调用新人入职指引 Dify Chat App，并返回模型回答和会话信息。"""
        if not self.settings.dify_onboarding_api_key:
            raise RuntimeError("未配置新人入职指引 Dify API Key")

        base_url = self.settings.dify_onboarding_api_base_url.rstrip("/")
        url = f"{base_url}/chat-messages" if base_url.endswith("/v1") else f"{base_url}/v1/chat-messages"
        payload = {
            "inputs": {},
            "query": question,
            "response_mode": "blocking",
            "user": "enterprise-onboarding-guide",
        }
        headers = {
            "Authorization": f"Bearer {self.settings.dify_onboarding_api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=60) as client:
            response = self._post_with_retry(client, url, payload, headers)
            response.raise_for_status()

        data = response.json()
        answer = data.get("answer")
        if not answer:
            raise RuntimeError("Dify 返回内容中缺少 answer 字段")
        return {
            "answer": self._strip_think_tags(answer),
            "conversation_id": data.get("conversation_id"),
            "message_id": data.get("message_id") or data.get("id"),
            "metadata": data.get("metadata") or {},
        }

    def _post_with_retry(
        self,
        client: httpx.Client,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:
        """Dify 或模型服务偶发 502/503/504 时重试，降低临时网关错误影响。"""
        retry_status_codes = {502, 503, 504}
        response: httpx.Response | None = None
        for attempt in range(4):
            response = client.post(url, json=payload, headers=headers)
            status_code = getattr(response, "status_code", 200)
            if status_code not in retry_status_codes:
                return response
            if attempt < 3:
                time.sleep(0.8 * (attempt + 1))
        if response is None:
            raise RuntimeError("Dify 请求未返回响应")
        return response

    def _strip_think_tags(self, answer: str) -> str:
        """清理部分推理模型返回的 <think>...</think> 内容，只把最终回答给前端。"""
        return re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()

    def _mock_report_draft(self, report_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        if report_type == ReportType.COMPLAINT_WEEKLY:
            total = source_data.get("total_tickets", 0)
            status_counts = source_data.get("status_counts", {})
            resolved = status_counts.get("resolved", 0)
            pending = status_counts.get("pending", 0)
            processing = status_counts.get("processing", 0)
            resolve_rate = f"{round(resolved / total * 100, 1) if total > 0 else 0}%"
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")
            satisfaction_avg = source_data.get("satisfaction_avg")
            priority_counts = source_data.get("priority_counts", {})
            prev_week_total = source_data.get("prev_week_total", 0)
            wow_delta_pct = source_data.get("wow_delta_pct", 0)
            wow_trend_label = source_data.get("wow_trend_label", "持平")
            overdue_ticket_count = source_data.get("overdue_ticket_count", 0)
            category_cn_counts = source_data.get("category_cn_counts", source_data.get("category_counts", {}))

            title = f"投诉处理周报（{date_start} 至 {date_end}）"
            summary = (
                f"本周期共收到 {total} 件投诉，已解决 {resolved} 件（解决率 {resolve_rate}），"
                f"处理中 {processing} 件，待处理 {pending} 件。"
                f"较上周期投诉量{wow_trend_label}（{wow_delta_pct:+.1f}%），"
                f"整体投诉量处于可控范围，{'待处理工单需优先跟进，避免积压升级' if pending > 0 else '工单流转正常'}。"
            )

            # 整体概况 metrics
            overview_metrics = [{"name": "投诉总量", "value": total}]
            if prev_week_total is not None:
                overview_metrics.append({"name": "上周同期", "value": prev_week_total})
            overview_metrics.append({"name": "周环比", "value": f"{wow_delta_pct:+.1f}%"})

            # 处理进展 metrics
            progress_metrics = [
                {"name": "已解决", "value": resolved},
                {"name": "处理中", "value": processing},
                {"name": "待处理", "value": pending},
                {"name": "解决率", "value": resolve_rate},
            ]
            sat_text = ""
            if satisfaction_avg is not None:
                progress_metrics.append({"name": "满意度均分", "value": f"{satisfaction_avg}/5"})
                sat_text = f"客户满意度均分 {satisfaction_avg}/5，{'满意度偏低，需关注服务质量' if satisfaction_avg < 3.5 else '满意度良好'}。"
            avg_hours = source_data.get("avg_processing_hours")
            hours_text = ""
            if avg_hours is not None:
                progress_metrics.append({"name": "平均处理时长(h)", "value": avg_hours})
                hours_text = f"已闭环工单平均处理时长 {avg_hours} 小时，{'处理时效偏慢，建议优化分派和处理流程' if avg_hours > 48 else '处理时效良好'}。"
            urgent_cnt = priority_counts.get("urgent", 0)
            severe_cnt = priority_counts.get("severe", 0)
            if priority_counts:
                for pname, pval in priority_counts.items():
                    progress_metrics.append({"name": f"优先级-{pname}", "value": pval})
            priority_text = (
                f"紧急工单 {urgent_cnt} 件、严重工单 {severe_cnt} 件，需优先处置。" if (urgent_cnt + severe_cnt) > 0 else ""
            )

            # 投诉分类 section
            top_category = max(category_cn_counts, key=category_cn_counts.get) if category_cn_counts else "未知"
            category_metrics = [{"name": k, "value": v} for k, v in category_cn_counts.items()]
            category_text = (
                "、".join(f"{k}（{v}件）" for k, v in sorted(category_cn_counts.items(), key=lambda x: x[1], reverse=True))
                if category_cn_counts else "暂无分类数据"
            )

            sections = [
                {
                    "heading": "整体概况",
                    "content": (
                        f"本周期投诉工单总量为 {total} 件，覆盖待处理、处理中、已解决三种状态。"
                        f"与上周同期 {prev_week_total} 件相比，投诉量{wow_trend_label}（{wow_delta_pct:+.1f}%）。"
                    ),
                    "metrics": overview_metrics,
                },
                {
                    "heading": "工单状态与处理进展",
                    "content": (
                        f"已解决 {resolved} 件（{resolve_rate}），处理中 {processing} 件，待处理 {pending} 件。"
                        f"{sat_text}{hours_text}{priority_text}"
                        f"{'待处理占比偏高，需关注是否有工单未及时分配处理人' if pending >= total * 0.3 else '各状态分布较为均衡，处理节奏正常。'}"
                    ),
                    "metrics": progress_metrics,
                },
                {
                    "heading": "投诉分类分布",
                    "content": (
                        f"本周投诉分类分布：{category_text}。"
                        f"最高频分类为「{top_category}」，建议针对该类别制定专项 SOP，减少同类投诉重复出现。"
                    ),
                    "metrics": category_metrics,
                },
                {
                    "heading": "风险预警",
                    "content": (
                        f"当前待处理工单 {pending} 件，{'如超 48 小时无更新存在客户投诉升级风险，建议优先分配处理人并设定处理时限' if pending > 0 else '暂无积压风险'}。"
                        f"{'超 48 小时未闭环工单 ' + str(overdue_ticket_count) + ' 件，需立即跟进' if overdue_ticket_count > 0 else ''}"
                    ),
                    "metrics": [{"name": "超期工单(>48h)", "value": overdue_ticket_count}],
                },
                {
                    "heading": "改善建议",
                    "content": (
                        "建议加强工单分派机制，确保每件投诉在 24 小时内匹配处理人；"
                        "定期复盘高频投诉类别，制定专项 SOP 减少同类问题重复发生；"
                        "建立满意度回访机制，对已解决工单进行 48 小时内回访确认。"
                    ),
                    "metrics": [],
                },
            ]
            risks = [
                f"待处理工单 {pending} 件未闭环，存在客户满意度下降和服务升级风险"
                if pending > 0
                else "本周工单全部闭环，暂无服务风险"
            ]
            if overdue_ticket_count > 0:
                risks.append(f"超 48 小时未闭环工单 {overdue_ticket_count} 件，客诉升级风险较高")
            recommendations = [
                "建议优先处理待处理工单，确保 48 小时内首次响应",
                "对高频投诉类别进行专项分析，制定预防性 SOP",
                "建立工单处理时效看板，透明化团队服务效率",
            ]
            source_refs = [
                f"数据来源：student_feedback_ticket 投诉工单表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.CUSTOMER_OPERATION:
            new_leads = source_data.get("new_leads", 0)
            analysis_records = source_data.get("analysis_records", 0)
            event_regs = source_data.get("event_registrations", 0)
            lead_source = source_data.get("lead_source_breakdown", {})
            lead_status = source_data.get("lead_status_breakdown", {})
            analysis_result = source_data.get("analysis_result_breakdown", {})
            event_reg = source_data.get("event_registration_breakdown", {})
            portrait_breakdown = source_data.get("portrait_breakdown", {})
            lost_reason_counts = source_data.get("lost_reason_counts", {})
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")
            prev = source_data.get("prev_period", {})
            lead_trend = source_data.get("lead_trend", {})
            churn_source = source_data.get("churn_source_breakdown", {})
            top_churn_source = max(churn_source, key=churn_source.get) if churn_source else "未归类"
            prev_leads = prev.get("leads", 0)
            delta_pct = lead_trend.get("delta_pct", 0)
            trend_label = lead_trend.get("label", "持平")
            prev_analysis = prev.get("analysis", 0)
            prev_events = prev.get("events", 0)

            source_text = "、".join(f"{k}({v}条)" for k, v in lead_source.items()) if lead_source else "暂无渠道数据"
            status_text = "、".join(f"{k}({v}条)" for k, v in lead_status.items()) if lead_status else "暂无阶段数据"
            result_text = "、".join(f"{k}({v}条)" for k, v in analysis_result.items()) if analysis_result else "暂无研判等级数据"
            title = f"全域客户经营分析报告（{date_start} 至 {date_end}）"

            lead_to_analysis = round(analysis_records / new_leads * 100, 1) if new_leads > 0 else 0
            # 成交数据优先用 DAO 成交专项字段，回退到状态分布（英文枚举 signed）
            signed_count = source_data.get("signed_count", lead_status.get("signed", 0))
            signed_source_breakdown = source_data.get("signed_source_breakdown", {})
            avg_conversion_days = source_data.get("avg_conversion_days")
            signed_conversion_rate = source_data.get("signed_conversion_rate",
                                                     round(signed_count / new_leads * 100, 1) if new_leads > 0 else 0)
            lost_count = lead_status.get("lost", 0) + lead_status.get("invalid", 0)
            high_intent = analysis_result.get("高意向", analysis_result.get("high", 0))
            active_event_regs = event_reg.get("已报名", event_reg.get("registered", 0))
            converted_event_regs = event_reg.get("已转化", event_reg.get("converted", event_reg.get("已参加", 0)))

            summary = (
                f"本周期新增线索 {new_leads} 条，完成客户研判 {analysis_records} 条，"
                f"活动报名 {event_regs} 人次。线索研判覆盖率 {lead_to_analysis}%，"
                f"{'成交 ' + str(signed_count) + ' 单' if signed_count > 0 else '暂无已成交客户'}。"
                f"{'存在 ' + str(lost_count) + ' 条流失线索需关注归因' if lost_count > 0 else ''}"
            )

            # 客群深度画像文字
            def _portrait_text(sub_dict: dict, top_n: int = 3) -> str:
                if not sub_dict or all(k == "未填写" for k in sub_dict):
                    return "该维度数据暂未完整填报，建议完善线索录入规范"
                top = sorted(sub_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
                return "、".join(f"{k}（{v}条）" for k, v in top)

            portrait_content_parts = []
            if portrait_breakdown.get("target_country_counts"):
                portrait_content_parts.append(f"意向国家：{_portrait_text(portrait_breakdown['target_country_counts'])}")
            if portrait_breakdown.get("target_program_counts"):
                portrait_content_parts.append(f"意向项目：{_portrait_text(portrait_breakdown['target_program_counts'])}")
            if portrait_breakdown.get("budget_range_counts"):
                portrait_content_parts.append(f"预算区间：{_portrait_text(portrait_breakdown['budget_range_counts'])}")
            if portrait_breakdown.get("education_level_counts"):
                portrait_content_parts.append(f"学历背景：{_portrait_text(portrait_breakdown['education_level_counts'])}")

            portrait_metrics = []
            for dim_key, dim_label in [
                ("target_country_counts", "意向国家"),
                ("target_program_counts", "意向项目"),
                ("budget_range_counts", "预算区间"),
                ("education_level_counts", "学历背景"),
            ]:
                for k, v in list((portrait_breakdown.get(dim_key) or {}).items())[:3]:
                    portrait_metrics.append({"name": f"{dim_label}-{k}", "value": v})

            # 流失归因文字
            top_lost_reasons = sorted(lost_reason_counts.items(), key=lambda x: x[1], reverse=True)[:3] if lost_reason_counts else []
            lost_reason_text = (
                "高频流失原因：" + "、".join(f"{r}（{c}条）" for r, c in top_lost_reasons)
                if top_lost_reasons else "暂无流失归因数据，建议完善流失原因记录。"
            )
            lost_reason_metrics = [{"name": r, "value": c} for r, c in top_lost_reasons]

            # 成交客户高价值特征文字
            signed_source_text = (
                "、".join(f"{k}（{v}单）" for k, v in sorted(signed_source_breakdown.items(), key=lambda x: x[1], reverse=True)[:3])
                if signed_source_breakdown else "暂无成交渠道数据"
            )
            cycle_text = f"平均转化周期 {avg_conversion_days} 天。" if avg_conversion_days is not None else ""

            sections = [
                {
                    "heading": "意向客户 - 线索获取与渠道分布",
                    "content": (
                        f"本周期新增客户线索 {new_leads} 条。线索来源渠道分布：{source_text}。"
                        f"线索当前所处阶段：{status_text}。"
                        "建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。"
                    ),
                    "metrics": [
                        {"name": "新增线索", "value": new_leads},
                        *[{"name": f"渠道-{k}", "value": v} for k, v in lead_source.items()],
                    ],
                },
                {
                    "heading": "意向客户 - 研判转化漏斗",
                    "content": (
                        f"完成客户研判 {analysis_records} 条，研判覆盖率 {lead_to_analysis}%。"
                        f"研判等级分布：{result_text}。"
                        f"高意向客户 {high_intent} 条，是近期转化重点跟进对象。"
                        f"{'研判覆盖率偏低，部分线索尚未进入研判阶段，存在流失风险' if lead_to_analysis < 50 else '研判覆盖率正常。'} "
                        f"从\"线索\"到\"研判\"的转化漏斗目前为 {new_leads} → {analysis_records}。"
                    ),
                    "metrics": [
                        {"name": "研判数", "value": analysis_records},
                        {"name": "研判覆盖率", "value": f"{lead_to_analysis}%"},
                        *[{"name": f"研判-{k}", "value": v} for k, v in analysis_result.items()],
                        {"name": "上周研判数", "value": prev_analysis},
                    ],
                },
                {
                    "heading": "成交客户 - 转化路径与高价值特征",
                    "content": (
                        f"本周期成交客户 {signed_count} 单"
                        f"{'，线索到成交转化率 ' + str(signed_conversion_rate) + '%' if new_leads > 0 else ''}。"
                        f"{cycle_text}"
                        f"{'成交客户渠道来源：' + signed_source_text + '，可据此判断高价值客户的获客渠道偏好。' if signed_count > 0 else ''}"
                        f"从研判分布来看，{result_text}，高意向客户是成交主力来源。"
                        f"{'研判等级为高意向的客户应纳入优先跟进序列，加速转化。' if high_intent > 0 else ''}"
                        f"{'暂无成交客户，建议复盘从研判到签约环节的转化障碍。' if signed_count == 0 else ''}"
                    ),
                    "metrics": [
                        {"name": "成交客户数", "value": signed_count},
                        {"name": "线索→成交转化率", "value": f"{signed_conversion_rate}%" if new_leads > 0 else "N/A"},
                        *([{"name": "平均转化周期(天)", "value": avg_conversion_days}] if avg_conversion_days is not None else []),
                        *[{"name": f"成交渠道-{k}", "value": v} for k, v in signed_source_breakdown.items()],
                    ],
                },
                {
                    "heading": "活动参与与转化跟踪",
                    "content": (
                        f"活动报名总计 {event_regs} 人次，"
                        f"其中已报名 {active_event_regs} 人次、已转化 {converted_event_regs} 人次。"
                        "活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，"
                        f"{'将活动报名 → 研判 → 签约的转化链打通' if converted_event_regs < active_event_regs else '活动转化效果良好'}。"
                    ),
                    "metrics": [
                        {"name": "活动报名总人次", "value": event_regs},
                        *[{"name": f"活动-{k}", "value": v} for k, v in event_reg.items()],
                    ],
                },
                {
                    "heading": "流失客户 - 归因分析与预警",
                    "content": (
                        f"本周期流失线索 {lost_count} 条，占线索总量的 "
                        f"{f'{round(lost_count / (new_leads + lost_count) * 100, 1)}%' if (new_leads + lost_count) > 0 else 'N/A'}。"
                        f"{lost_reason_text}"
                        f"{'建议逐条复盘流失原因，沉淀流失特征模型' if lost_count > 0 else '暂无流失线索，客户留存状况良好。'}"
                    ),
                    "metrics": [
                        {"name": "流失线索数", "value": lost_count},
                        {"name": "流失占比", "value": f"{round(lost_count / (new_leads + lost_count) * 100, 1)}%" if (new_leads + lost_count) > 0 else "0%"},
                        *lost_reason_metrics,
                    ],
                },
                {
                    "heading": "客群特征与画像提炼",
                    "content": (
                        f"基于本周期数据，线索来源以 {max(lead_source, key=lead_source.get) if lead_source else '未归类'} 为主"
                        f"（占比 {f'{round(max(lead_source.values()) / sum(lead_source.values()) * 100, 1)}%' if lead_source else 'N/A'}）。"
                        f"研判后高意向客群占比 {f'{round(high_intent / analysis_records * 100, 1)}%' if analysis_records > 0 else 'N/A'}。"
                        + (("深度画像：" + "；".join(portrait_content_parts) + "。") if portrait_content_parts else
                           "建议后续补充客户行业、规模、预算等维度数据，进一步提升画像精准度。")
                    ),
                    "metrics": portrait_metrics,
                },
                {
                    "heading": "全链路经营建议",
                    "content": (
                        "建议建立线索分级机制，优先跟进高意向线索；"
                        "定期复盘研判转化漏斗，定位各环节流失原因；"
                        "将活动报名客户纳入专项跟进序列，提升活动线索转化率；"
                        "建立流失预警模型，对长期无互动线索自动标记并推送挽回策略；"
                        "按月/周输出客户经营健康度看板，支撑全链路决策闭环。"
                    ),
                    "metrics": [],
                },
            ]
            risks = []
            if new_leads > 0 and analysis_records < new_leads * 0.5:
                risks.append(f"线索研判覆盖率仅 {lead_to_analysis}%，半数以上线索未进入研判，存在大量线索沉默流失风险")
            if lost_count > 0:
                risks.append(f"已流失 {lost_count} 条线索（主要来自 {top_churn_source} 渠道），建议重点复盘该渠道线索质量和跟进流程")
            if delta_pct < -20 and new_leads > 0:
                risks.append(f"线索量较上周下降 {abs(delta_pct)}%，获客能力出现明显下滑，建议排查渠道投放和营销活动效果")
            if signed_count == 0 and new_leads > 0:
                risks.append("本周期零成交，线索到签约的转化链路存在阻断，需紧急排查瓶颈环节")
            if not risks:
                risks = ["暂无重大经营风险，建议保持当前跟进节奏"]
            recommendations = [
                "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
                "对活动报名客户建立 48 小时回访机制，推动转化",
                "建立线索分级标准，按意向度匹配跟进强度",
                "每周复盘流失线索共性特征，沉淀流失预防 SOP",
                "将高意向客户纳入重点跟进看板，确保闭环管理",
            ]
            if lost_reason_counts.get("未填写归因", 0) > lost_count * 0.5 and lost_count > 0:
                recommendations.append("大量流失线索缺少归因记录，建议完善流失原因填报规范")
            source_refs = [
                f"数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.EMPLOYEE_DAILY_SUMMARY:
            total = source_data.get("total_reports", 0)
            submitted = source_data.get("submitted_reports", 0)
            draft = source_data.get("draft_reports", 0)
            archived = source_data.get("archived_reports", 0)
            risk_reports = source_data.get("risk_reports", 0)
            tomorrow_plan = source_data.get("tomorrow_plan_reports", 0)
            date_start = source_data.get("date_start", "")
            title = f"员工日报汇总报告（{date_start}）"
            summary = (
                f"本日共汇总日报 {total} 份，已提交 {submitted} 份（提交率 {f'{round(submitted / total * 100, 1)}%' if total > 0 else 'N/A'}），"
                f"草稿 {draft} 份，归档 {archived} 份。"
                f"{'存在风险摘要的日报占比偏高，需重点关注' if total > 0 and risk_reports / total > 0.3 else '整体工作执行平稳。'}"
            )
            sections = [
                {
                    "heading": "日报提交概览",
                    "content": (
                        f"本日日报提交率 {f'{round(submitted / total * 100, 1)}%' if total > 0 else 'N/A'}，"
                        f"其中已提交 {submitted} 份、草稿 {draft} 份、已归档 {archived} 份。"
                        f"{'存在未提交或草稿状态的日报，建议了解原因并推动补交' if total - submitted > 0 else '全员已提交。'}"
                    ),
                    "metrics": [
                        {"name": "总日报数", "value": total},
                        {"name": "已提交", "value": submitted},
                        {"name": "草稿", "value": draft},
                        {"name": "已归档", "value": archived},
                    ],
                },
                {
                    "heading": "工作进展与潜在风险",
                    "content": (
                        f"含风险摘要的日报 {risk_reports} 份，填报明日计划 {tomorrow_plan} 份。"
                        f"{'风险摘要集中出现，建议汇总分析风险类型并制定应对方案' if risk_reports > 0 else '暂无风险上报。'}"
                        f"{'明日计划填报率偏低，团队工作计划清晰度有待提升' if total > 0 and tomorrow_plan < total * 0.5 else ''}"
                    ),
                    "metrics": [
                        {"name": "风险摘要日报", "value": risk_reports},
                        {"name": "明日计划日报", "value": tomorrow_plan},
                    ],
                },
                {
                    "heading": "管理建议",
                    "content": (
                        "推动未提交和草稿状态日报在当日完成补交；"
                        "对风险摘要日报进行专题复盘，提炼共性问题；"
                        "强化明日计划填报要求，提升团队工作的可预见性。"
                    ),
                    "metrics": [],
                },
            ]
            risks = [
                f"日报提交率 {f'{round(submitted / total * 100, 1)}%' if total > 0 else 'N/A'}，"
                f"{total - submitted} 份未提交，工作透明度存在风险" if total > submitted else "全员已提交，暂无执行风险"
            ]
            recommendations = [
                "建立日报提交截止时间提醒，确保当日日清日结",
                "对风险摘要日报进行集中分析，制定应对方案",
                "将明日计划填报纳入日报考核标准",
            ]
            source_refs = [
                f"数据来源：employee_daily_report 员工日报表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.EMPLOYEE_WEEKLY_SUMMARY:
            total = source_data.get("total_reports", 0)
            distinct = source_data.get("distinct_employees", 0)
            risk_reports = source_data.get("risk_reports", 0)
            daily_trend = source_data.get("daily_trend", {})
            week_submission_rate = source_data.get("week_submission_rate", "N/A")
            top_risk_themes = source_data.get("top_risk_themes", [])
            peak_submission_day = source_data.get("peak_submission_day")
            valley_submission_day = source_data.get("valley_submission_day")
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")
            title = f"员工日报汇总报告（{date_start} 至 {date_end}）"
            summary = (
                f"本周共汇总日报 {total} 份，涉及 {distinct} 名员工。"
                f"{'日报覆盖率偏低，需关注未提交员工。' if distinct > 0 and total / distinct < 5 else ('平均每人提交 ' + str(round(total / distinct, 1)) + ' 份。' if distinct > 0 else '')}"
                f"{'含风险摘要日报占比偏高' if total > 0 and risk_reports / total > 0.3 else '整体工作执行正常。'}"
            )

            # 每日趋势 content（bug 修复：原为字符串字面量）
            daily_trend_content = (
                "逐日提交量变化如下。"
                + ("工作日提交量高于周末，符合正常规律。" if len(daily_trend) >= 3
                   else "数据周期较短，建议积累更多数据做趋势分析。")
            )
            if peak_submission_day and valley_submission_day:
                daily_trend_content += f"提交峰值日：{peak_submission_day}，提交低谷日：{valley_submission_day}。"

            daily_trend_metrics = [{"name": day, "value": count} for day, count in daily_trend.items()]
            if peak_submission_day:
                daily_trend_metrics.append({"name": "高峰日", "value": peak_submission_day})
            if valley_submission_day:
                daily_trend_metrics.append({"name": "低谷日", "value": valley_submission_day})

            # 风险主题
            risk_theme_text = ""
            risk_theme_metrics = []
            if top_risk_themes:
                theme_strs = "、".join(f"{kw}（{cnt}次）" for kw, cnt in top_risk_themes[:5])
                risk_theme_text = f"高频风险主题词：{theme_strs}，建议管理层重点关注。"
                risk_theme_metrics = [{"name": f"风险词-{kw}", "value": cnt} for kw, cnt in top_risk_themes[:5]]

            sections = [
                {
                    "heading": "周度提交趋势",
                    "content": (
                        f"本周共 {distinct} 人提交日报，总量 {total} 份，本周提交率 {week_submission_rate}。"
                        "逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。"
                    ),
                    "metrics": [
                        {"name": "总日报数", "value": total},
                        {"name": "提交员工数", "value": distinct},
                        {"name": "本周提交率", "value": week_submission_rate},
                    ],
                },
                {
                    "heading": "每日提交趋势",
                    "content": daily_trend_content,
                    "metrics": daily_trend_metrics,
                },
                {
                    "heading": "工作质量与风险观察",
                    "content": (
                        f"含风险摘要日报 {risk_reports} 份（占比 {f'{round(risk_reports / total * 100, 1)}%' if total > 0 else 'N/A'}）。"
                        f"{'风险摘要占比较高，建议汇总分析风险类型分布。' if total > 0 and risk_reports / total > 0.3 else '风险披露比例适中。'}"
                        + risk_theme_text
                    ),
                    "metrics": [
                        {"name": "风险摘要日报", "value": risk_reports},
                        {"name": "风险摘要占比", "value": f"{round(risk_reports / total * 100, 1)}%" if total > 0 else "N/A"},
                        *risk_theme_metrics,
                    ],
                },
                {
                    "heading": "管理建议",
                    "content": (
                        "针对提交量波动的日期了解原因，评估是否需要工作安排优化；"
                        "定期汇总风险摘要日报，提炼共性问题和改进方向；"
                        "推动部门内日报标准化，提升工作可量化程度。"
                    ),
                    "metrics": [],
                },
            ]
            risks = [
                f"日报覆盖率偏低（{distinct} 人提交），部分员工工作情况不可见" if distinct > 0 and total < distinct * 3 else "暂无重大管理风险"
            ]
            recommendations = [
                "推动全员日报提交，确保工作进展透明化",
                "汇总本周风险摘要，形成团队风险清单",
                "建立日报质量评分机制，提升填报内容质量",
            ]
            source_refs = [
                f"数据来源：employee_daily_report 员工日报表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        elif report_type == ReportType.STUDENT_PSYCH_WEEKLY:
            total_profiles = source_data.get("total_profiles", 0)
            total_alerts = source_data.get("total_alerts", 0)
            risk_level_counts = source_data.get("risk_level_counts", {})
            emotion_tag_counts = source_data.get("emotion_tag_counts", {})
            alert_status_counts = source_data.get("alert_status_counts", {})
            avg_score = source_data.get("average_emotion_score", 0)
            interaction_trend = source_data.get("interaction_trend", {})
            emotion_summary_samples = source_data.get("emotion_summary_samples", [])
            date_start = source_data.get("date_start", "")
            date_end = source_data.get("date_end", "")

            # 情绪标签中文映射
            EMOTION_TAG_MAP = {
                "anxious": "焦虑", "stable": "平稳", "depressed": "低落",
                "excited": "亢奋", "lonely": "孤独", "stressed": "压力大",
                "happy": "积极", "neutral": "平静",
            }
            emotion_tag_cn = {EMOTION_TAG_MAP.get(k, k): v for k, v in emotion_tag_counts.items()}
            anxious_cnt = emotion_tag_counts.get("anxious", 0)

            # 留学周期节点动态化
            try:
                month = int(date_start.split("-")[1])
            except (IndexError, ValueError):
                month = 0
            if month in (4, 5, 11, 12):
                period_hint = "当前处于考试季高压期，学业焦虑风险显著上升"
            elif month in (1, 7, 8):
                period_hint = "当前处于假期/学期衔接期，跨文化孤独感风险较高"
            else:
                period_hint = "当前处于常规学期阶段，持续关注高风险个案"

            # 情绪摘要样本（最多3条，脱敏）
            sample_text = ""
            if emotion_summary_samples:
                excerpts = [f"（摘录）{s['summary']}" for s in emotion_summary_samples[:3] if s.get("summary")]
                if excerpts:
                    sample_text = "典型情绪摘录：" + "；".join(excerpts) + "。"

            title = f"学生心理健康周报（{date_start} 至 {date_end}）"
            summary = (
                f"本周纳入心理画像 {total_profiles} 份，平均情绪分 {avg_score}，"
                f"触发预警 {total_alerts} 条。"
                f"{'整体心理健康处于关注区间，需介入高风险个案' if avg_score < 70 or risk_level_counts.get('high', 0) > 0 else '整体心理状态平稳。'}"
            )

            # 互动趋势文字
            interaction_text = ""
            if interaction_trend:
                peak_day = max(interaction_trend, key=interaction_trend.get)
                interaction_text = f"本周逐日心理互动记录：{'、'.join(f'{d}（{c}人次）' for d, c in interaction_trend.items())}。情绪互动峰值日为 {peak_day}。"

            sections = [
                {
                    "heading": "整体心理态势",
                    "content": (
                        f"本周共 {total_profiles} 名学生完成心理画像评估，整体平均情绪分 {avg_score}。"
                        f"{'平均情绪分偏低，需关注学生群体的整体心理健康趋势。' if avg_score < 70 else '情绪分处于正常区间，群体心理状态平稳。'}"
                        f"留学阶段背景：{period_hint}。"
                        + (sample_text if sample_text else "建议推动辅导员定期更新心理画像，以获取更丰富的个案支撑。")
                    ),
                    "metrics": [
                        {"name": "心理画像数", "value": total_profiles},
                        {"name": "平均情绪分", "value": f"{avg_score}（满分 100）"},
                    ],
                },
                {
                    "heading": "风险分层分析",
                    "content": (
                        f"高风险：{risk_level_counts.get('high', 0)} 人，中等风险：{risk_level_counts.get('medium', 0)} 人，"
                        f"低风险：{risk_level_counts.get('low', 0)} 人。"
                        f"{'存在高风险学生，建议立即启动深度访谈和心理干预方案' if risk_level_counts.get('high', 0) > 0 else '无高风险学生，继续保持常规关注。'}"
                    ),
                    "metrics": [
                        {"name": "高风险", "value": risk_level_counts.get("high", 0)},
                        {"name": "中风险", "value": risk_level_counts.get("medium", 0)},
                        {"name": "低风险", "value": risk_level_counts.get("low", 0)},
                    ],
                },
                {
                    "heading": "情绪标签与趋势",
                    "content": (
                        "本周主要情绪标签分布：" +
                        "、".join(f"{tag}({cnt})" for tag, cnt in emotion_tag_cn.items()) +
                        ("。" if emotion_tag_cn else "暂无情绪标签数据。") +
                        (f"焦虑标签占比突出，可能与近期考试或学业压力相关。" if anxious_cnt > 0 else "") +
                        interaction_text
                    ),
                    "metrics": [
                        {"name": tag, "value": cnt}
                        for tag, cnt in emotion_tag_cn.items()
                    ] + [{"name": f"互动-{d}", "value": c} for d, c in interaction_trend.items()],
                },
                {
                    "heading": "预警处理与关怀建议",
                    "content": (
                        f"预警总量 {total_alerts} 条，已处理 {alert_status_counts.get('resolved', 0)} 条，"
                        f"待处理 {alert_status_counts.get('pending', 0)} 条。"
                        f"{'存在未处理预警，需立即跟进高风险学生。' if alert_status_counts.get('pending', 0) > 0 else '预警全部闭环处理。'}"
                        "建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。"
                    ),
                    "metrics": [
                        {"name": "预警总量", "value": total_alerts},
                        {"name": "已处理", "value": alert_status_counts.get("resolved", 0)},
                        {"name": "待处理", "value": alert_status_counts.get("pending", 0)},
                    ],
                },
            ]
            risks = [
                f"存在 {risk_level_counts.get('high', 0)} 名高风险学生需紧急干预" if risk_level_counts.get('high', 0) > 0 else "暂无高危预警",
                f"整体平均情绪分 {avg_score}，低于健康阈值" if avg_score and avg_score < 70 else "",
                f"尚有 {alert_status_counts.get('pending', 0)} 条预警待处理" if alert_status_counts.get('pending', 0) > 0 else "",
            ]
            risks = [r for r in risks if r]
            recommendations = [
                "对高风险学生启动 48 小时内深度访谈",
                "组织本学期中段心理健康主题分享活动",
                "建立心理健康预警回访机制，确保干预闭环",
                f"针对{'焦虑' if anxious_cnt > 0 else '高风险'}标签突出的学生，协调学业支持资源",
            ]
            source_refs = [
                f"数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 {source_data.get('department_id')}，日期 {date_start} 至 {date_end}"
            ]
            return {
                "title": title,
                "summary": summary,
                "sections": sections,
                "risks": risks,
                "recommendations": recommendations,
                "source_refs": source_refs,
            }
        else:
            raise ValueError("不支持的报告类型")
        return {
            "title": title,
            "summary": summary,
            "sections": sections,
            "risks": [],
            "recommendations": ["请结合业务负责人反馈复核 AI 报告草稿。"],
            "source_refs": [source_data.get("report_type", report_type)],
        }

    def _call_dify_report_workflow(
        self,
        report_type: str,
        source_data: dict[str, Any],
        filters: dict[str, Any],
        trace_id: str | None,
    ) -> dict[str, Any]:
        if not self.settings.dify_api_key:
            raise RuntimeError("未配置 Dify API Key")
        url = f"{self.settings.dify_api_base_url.rstrip('/')}/v1/workflows/run"
        payload = {
            "inputs": {
                "report_type": report_type,
                "source_data": json.dumps(source_data, ensure_ascii=False),
                "filters": json.dumps(filters, ensure_ascii=False),
                "trace_id": trace_id,
            },
            "response_mode": "blocking",
            "user": "education-service-backend",
        }
        headers = {"Authorization": f"Bearer {self.settings.dify_api_key}"}
        with httpx.Client(timeout=60) as client:
            response = self._post_with_retry(client, url, payload, headers)
            response.raise_for_status()
        data = response.json()
        outputs = data.get("data", {}).get("outputs", {})
        draft = self._extract_report_output(outputs)
        return self._normalize_report_draft(draft)

    def _extract_report_output(self, outputs: Any) -> dict[str, Any]:
        if isinstance(outputs, dict):
            for key in ("report", "text", "result"):
                value = outputs.get(key)
                if value:
                    return self._coerce_report_dict(value)
            return self._coerce_report_dict(outputs)
        return self._coerce_report_dict(outputs)

    def _coerce_report_dict(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            for candidate in self._candidate_json_strings(value):
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict):
                    return parsed
        raise RuntimeError("Dify 返回内容无法解析为报告草稿")

    def _candidate_json_strings(self, text: str) -> list[str]:
        stripped = text.strip()
        without_think = re.sub(r"<think>.*?</think>", "", stripped, flags=re.IGNORECASE | re.DOTALL).strip()
        candidates = [stripped, without_think]

        fence_match = re.search(r"```(?:json)?\s*(.*?)```", without_think, flags=re.IGNORECASE | re.DOTALL)
        if fence_match:
            candidates.append(fence_match.group(1).strip())

        embedded_json = self._extract_first_json_object(without_think)
        if embedded_json:
            candidates.append(embedded_json)

        unique_candidates = []
        for candidate in candidates:
            if candidate and candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates

    def _extract_first_json_object(self, text: str) -> str | None:
        start = text.find("{")
        if start < 0:
            return None

        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        # 扫到末尾仍未闭合：JSON 被截断（如 LLM max_tokens 不足），尝试补全兜底
        if depth > 0:
            repaired = self._repair_truncated_json(text[start:])
            if repaired is not None:
                return repaired
        return None

    def _repair_truncated_json(self, fragment: str) -> str | None:
        """对截断的 JSON 片段做补全：回退到最后一个完整元素，按括号栈补闭合符。

        仅在补全结果能成功解析时返回，否则返回 None（不强行挽救残缺内容）。
        """
        # 逐步回退截断点：从最长到最短，尝试在每个可能的元素边界处补全
        for cut in self._truncation_cut_candidates(fragment):
            stack: list[str] = []
            in_string = False
            escaped = False
            for ch in cut:
                if in_string:
                    if escaped:
                        escaped = False
                    elif ch == "\\":
                        escaped = True
                    elif ch == '"':
                        in_string = False
                    continue
                if ch == '"':
                    in_string = True
                elif ch in "{[":
                    stack.append(ch)
                elif ch == "}" and stack and stack[-1] == "{":
                    stack.pop()
                elif ch == "]" and stack and stack[-1] == "[":
                    stack.pop()
            if in_string:
                continue  # 截断点落在字符串中途，换下一个候选
            closing = "".join("}" if b == "{" else "]" for b in reversed(stack))
            patched = cut + closing
            try:
                json.loads(patched)
                return patched
            except json.JSONDecodeError:
                continue
        return None

    def _truncation_cut_candidates(self, text: str) -> list[str]:
        """生成候选截断点：在每个完整元素边界（} 或 ]）后切断，去掉残缺尾部。"""
        base = text.rstrip().rstrip(",")
        candidates = [base]
        # 找所有 } 和 ] 的位置，从后往前作为候选切点
        for i in range(len(base) - 1, 0, -1):
            if base[i] in "}]":
                trimmed = base[: i + 1].rstrip().rstrip(",")
                if trimmed and trimmed not in candidates:
                    candidates.append(trimmed)
                if len(candidates) >= 8:  # 限制回退尝试次数
                    break
        return candidates

    def _normalize_report_draft(self, draft: dict[str, Any]) -> dict[str, Any]:
        self._raise_for_failed_tool_call(draft)
        self._raise_for_failure_content(draft)
        title = draft.get("title")
        if not isinstance(title, str) or not title.strip():
            raise RuntimeError("Dify 返回内容无法解析为报告草稿")
        sections = draft.get("sections", [])
        if not isinstance(sections, list):
            sections = []
        normalized_sections = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            metrics = section.get("metrics", [])
            normalized_sections.append(
                {
                    "heading": str(section.get("heading", "")),
                    "content": str(section.get("content", "")),
                    "metrics": metrics if isinstance(metrics, list) else [],
                }
            )
        return {
            **draft,
            "title": title.strip(),
            "summary": str(draft.get("summary", "")),
            "sections": normalized_sections,
            "risks": draft.get("risks") if isinstance(draft.get("risks"), list) else [],
            "recommendations": draft.get("recommendations")
            if isinstance(draft.get("recommendations"), list)
            else [],
            "source_refs": draft.get("source_refs") if isinstance(draft.get("source_refs"), list) else [],
        }

    def _raise_for_failed_tool_call(self, draft: dict[str, Any]) -> None:
        tool_call_success = draft.get("tool_call_success")
        tool_status_code = self._coerce_status_code(draft.get("tool_status_code"))

        success_is_false = tool_call_success is False or (
            isinstance(tool_call_success, str) and tool_call_success.strip().lower() in {"false", "0", "no"}
        )
        status_is_failed = tool_status_code is not None and tool_status_code != 200
        if success_is_false or status_is_failed:
            error = draft.get("tool_error") or draft.get("summary") or "Dify AI Tool 返回失败状态"
            raise RuntimeError(f"Dify AI Tool 调用失败：{error}")

    def _raise_for_failure_content(self, draft: dict[str, Any]) -> None:
        content = json.dumps(draft, ensure_ascii=False)
        failure_markers = (
            "HTTP 422",
            "HTTP 401",
            "HTTP 403",
            "FastAPI AI Tool返回",
            "FastAPI AI Tool 返回",
            "参数校验错误",
            "请求被拒绝",
            "query_report_source_data未成功执行",
            "query_report_source_data 未成功执行",
            "无可用数据表",
        )
        if any(marker in content for marker in failure_markers):
            raise RuntimeError("Dify AI Tool 调用失败：模型输出包含工具失败或参数校验错误内容")

    def _coerce_status_code(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
