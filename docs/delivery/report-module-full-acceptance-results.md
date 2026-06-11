# ???????????

## ??????

- **????**?2026-06-11
- **???**?MySQL 8 (`education_service_ai_test`)
- **????**?Mock ??
- **pytest ??**?57 passed, 0 skipped, 0 failed

## ??????

| ?? | ??? | ?? |
|------|--------|------|
| crm_lead | 44 | ???? |
| customer_analysis_record | 21 | ???? |
| event_registration | 13 | ???? |
| student_feedback_ticket | 22 | ???? |
| employee_daily_report | 20 | ???? |
| student_psych_profile | 6 | ???? |
| student_psych_alert | 10 | ???? |

---

### ???? - ??????

**POST /api/v1/reports/generate-draft**

**???**
```json
{
  "report_type": "complaint_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "trace_id": "report-test-complaint_weekly",
  "department_id": 10
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 259,
    "draft_no": "DR-20260611113521-ae0ec180",
    "status": "pending_confirm",
    "content_json": {
      "risks": [
        "待处理工单 1 件未闭环，存在客户满意度下降和服务升级风险"
      ],
      "title": "投诉处理周报（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周期共收到 5 件投诉，已解决 1 件（解决率 20.0%），处理中 3 件，待处理 1 件。整体投诉量处于可控范围，待处理工单需优先跟进，避免积压升级。",
      "sections": [
        {
          "content": "本周期投诉工单总量为 5 件，覆盖待处理、处理中、已解决三种状态。相较前序周期如有数据变化需逐项分析原因。",
          "heading": "整体概况",
          "metrics": [
            {
              "name": "投诉总量",
              "value": 5
            }
          ]
        },
        {
          "content": "已解决 1 件（20.0%），处理中 3 件，待处理 1 件。各状态分布较为均衡，处理节奏正常。",
          "heading": "工单状态与处理进展",
          "metrics": [
            {
              "name": "已解决",
              "value": 1
            },
            {
              "name": "处理中",
              "value": 3
            },
            {
              "name": "待处理",
              "value": 1
            },
            {
              "name": "解决率",
              "value": "20.0%"
            }
          ]
        },
        {
          "content": "当前待处理工单 1 件，如超 48 小时无更新存在客户投诉升级风险，建议优先分配处理人并设定处理时限。",
          "heading": "风险预警",
          "metrics": []
        },
        {
          "content": "建议加强工单分派机制，确保每件投诉在 24 小时内匹配处理人；定期复盘高频投诉类别，制定专项 SOP 减少同类问题重复发生；建立满意度回访机制，对已解决工单进行 48 小时内回访确认。",
          "heading": "改善建议",
          "metrics": []
        }
      ],
      "report_type": "complaint_weekly",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "report_type": "complaint_weekly",
        "department_id": 10,
        "status_counts": {
          "pending": 1,
          "resolved": 1,
          "processing": 3
        },
        "total_tickets": 5,
        "category_counts": {
          "签证办理": 1,
          "院校申请": 1,
          "专业能力投诉": 1,
          "办理时效投诉": 1,
          "服务态度投诉": 1
        },
        "ticket_type_counts": {
          "咨询": 1,
          "投诉": 4
        },
        "avg_processing_hours": 17.0
      },
      "source_refs": [
        "数据来源：student_feedback_ticket 投诉工单表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendations": [
        "建议优先处理待处理工单，确保 48 小时内首次响应",
        "对高频投诉类别进行专项分析，制定预防性 SOP",
        "建立工单处理时效看板，透明化团队服务效率"
      ]
    },
    "trace_id": "report-test-complaint_weekly"
  },
  "trace_id": "report-test-complaint_weekly"
}
```


### ???? - ??????????

**POST /api/v1/reports/generate-draft**

**???**
```json
{
  "report_type": "customer_operation",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "trace_id": "report-test-customer_operation",
  "department_id": 10,
  "owner_user_id": 102
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 260,
    "draft_no": "DR-20260611113521-d7d5585e",
    "status": "pending_confirm",
    "content_json": {
      "risks": [
        "已流失 1 条线索（主要来自 异业合作 渠道），建议重点复盘该渠道线索质量和跟进流程"
      ],
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": 102
      },
      "summary": "本周期新增线索 8 条，完成客户研判 4 条，活动报名 1 人次。线索研判覆盖率 50.0%，成交 5 单。存在 1 条流失线索需关注归因",
      "sections": [
        {
          "content": "本周期新增客户线索 8 条。线索来源渠道分布：活动引流(1条)、官网(2条)、异业合作(2条)、展会获客(1条)、广告投放(1条)、转介绍(1条)。线索当前所处阶段：新线索(3条)、已成交(5条)、已分析(5条)、已谈判(7条)、已联系(2条)、已流失(1条)。建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。",
          "heading": "意向客户 - 线索获取与渠道分布",
          "metrics": [
            {
              "name": "新增线索",
              "value": 8
            },
            {
              "name": "渠道-活动引流",
              "value": 1
            },
            {
              "name": "渠道-官网",
              "value": 2
            },
            {
              "name": "渠道-异业合作",
              "value": 2
            },
            {
              "name": "渠道-展会获客",
              "value": 1
            },
            {
              "name": "渠道-广告投放",
              "value": 1
            },
            {
              "name": "渠道-转介绍",
              "value": 1
            }
          ]
        },
        {
          "content": "完成客户研判 4 条，研判覆盖率 50.0%。研判等级分布：高意向(2条)、中意向(2条)。高意向客户 2 条，是近期转化重点跟进对象。研判覆盖率正常。 从\"线索\"到\"研判\"的转化漏斗目前为 8 → 4。",
          "heading": "意向客户 - 研判转化漏斗",
          "metrics": [
            {
              "name": "研判数",
              "value": 4
            },
            {
              "name": "研判覆盖率",
              "value": "50.0%"
            },
            {
              "name": "研判-高意向",
              "value": 2
            },
            {
              "name": "研判-中意向",
              "value": 2
            },
            {
              "name": "上周研判数",
              "value": 1
            }
          ]
        },
        {
          "content": "本周期成交客户 5 单，线索到成交转化率 62.5%。从研判分布来看，高意向(2条)、中意向(2条)，高意向客户是成交主力来源。研判等级为高意向的客户应纳入优先跟进序列，加速转化。",
          "heading": "成交客户 - 转化路径与高价值特征",
          "metrics": [
            {
              "name": "成交客户数",
              "value": 5
            },
            {
              "name": "线索→成交转化率",
              "value": "62.5%"
            }
          ]
        },
        {
          "content": "活动报名总计 1 人次，其中已报名 0 人次、已转化 1 人次。活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，活动转化效果良好。",
          "heading": "活动参与与转化跟踪",
          "metrics": [
            {
              "name": "活动报名总人次",
              "value": 1
            },
            {
              "name": "活动-已转化",
              "value": 1
            }
          ]
        },
        {
          "content": "本周期流失线索 1 条，占线索总量的 11.1%。当前处于\"废弃/已关单\"状态的线索 1 条，建议逐条复盘流失原因（如价格、竞品、需求不匹配），沉淀流失特征模型",
          "heading": "
```


### ???? - ?????????

**POST /api/v1/reports/generate-draft**

**???**
```json
{
  "report_type": "employee_daily_summary",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "trace_id": "report-test-employee_daily_summary",
  "department_id": 10
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 261,
    "draft_no": "DR-20260611113521-5e1791b3",
    "status": "pending_confirm",
    "content_json": {
      "risks": [
        "全员已提交，暂无执行风险"
      ],
      "title": "员工日报汇总报告（2026-06-01）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本日共汇总日报 2 份，已提交 2 份（提交率 100.0%），草稿 0 份，归档 0 份。存在风险摘要的日报占比偏高，需重点关注",
      "sections": [
        {
          "content": "本日日报提交率 100.0%，其中已提交 2 份、草稿 0 份、已归档 0 份。全员已提交。",
          "heading": "日报提交概览",
          "metrics": [
            {
              "name": "总日报数",
              "value": 2
            },
            {
              "name": "已提交",
              "value": 2
            },
            {
              "name": "草稿",
              "value": 0
            },
            {
              "name": "已归档",
              "value": 0
            }
          ]
        },
        {
          "content": "含风险摘要的日报 2 份，填报明日计划 2 份。风险摘要集中出现，建议汇总分析风险类型并制定应对方案",
          "heading": "工作进展与潜在风险",
          "metrics": [
            {
              "name": "风险摘要日报",
              "value": 2
            },
            {
              "name": "明日计划日报",
              "value": 2
            }
          ]
        },
        {
          "content": "推动未提交和草稿状态日报在当日完成补交；对风险摘要日报进行专题复盘，提炼共性问题；强化明日计划填报要求，提升团队工作的可预见性。",
          "heading": "管理建议",
          "metrics": []
        }
      ],
      "report_type": "employee_daily_summary",
      "source_data": {
        "date_end": "2026-06-01",
        "date_start": "2026-06-01",
        "risk_items": [
          {
            "emp": "Full Employee A",
            "text": "人手不足"
          },
          {
            "emp": "Full Employee B",
            "text": "材料补充中"
          }
        ],
        "report_type": "employee_daily_summary",
        "risk_reports": 2,
        "department_id": 10,
        "draft_reports": 0,
        "status_counts": {
          "submitted": 2
        },
        "total_reports": 2,
        "submission_rate": "10.0%",
        "archived_reports": 0,
        "submitted_reports": 2,
        "key_progress_items": [
          {
            "emp": "Full Employee A",
            "text": "完成院校匹配方案"
          },
          {
            "emp": "Full Employee B",
            "text": "跟进高意向客户3组"
          }
        ],
        "tomorrow_plan_reports": 2,
        "employee_submission_list": [
          {
            "risks": "人手不足",
            "employee_name": "Full Employee A",
            "report_status": "submitted",
            "tomorrow_plan": "预约面谈4组"
          },
          {
            "risks": "材料补充中",
            "employee_name": "Full Employee A",
            "report_status": "draft",
            "tomorrow_plan": "跟进签证进度"
          },
          {
            "risks": "人手不足",
            "employee_name": "Full Employee A",
            "report_status": "submitted",
           
```


### ???? - ?????????

**POST /api/v1/reports/generate-draft**

**???**
```json
{
  "report_type": "employee_weekly_summary",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "trace_id": "report-test-employee_weekly_summary",
  "department_id": 10
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 262,
    "draft_no": "DR-20260611113521-a850078c",
    "status": "pending_confirm",
    "content_json": {
      "risks": [
        "暂无重大管理风险"
      ],
      "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周共汇总日报 10 份，涉及 2 名员工。平均每人提交 5.0份。含风险摘要日报占比偏高",
      "sections": [
        {
          "content": "本周共 2 人提交日报，总量 10 份。逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。",
          "heading": "周度提交趋势",
          "metrics": [
            {
              "name": "总日报数",
              "value": 10
            },
            {
              "name": "提交员工数",
              "value": 2
            }
          ]
        },
        {
          "content": "逐日提交量变化如下。' + ('工作日提交量高于周末，符合正常规律。' if len(daily_trend) >= 3 else '数据周期较短，建议积累更多数据做趋势分析。')",
          "heading": "每日提交趋势",
          "metrics": [
            {
              "name": "2026-06-01",
              "value": 2
            },
            {
              "name": "2026-06-02",
              "value": 2
            },
            {
              "name": "2026-06-03",
              "value": 2
            },
            {
              "name": "2026-06-04",
              "value": 2
            },
            {
              "name": "2026-06-05",
              "value": 2
            }
          ]
        },
        {
          "content": "含风险摘要日报 7 份（占比 70.0%）。风险摘要占比较高，建议汇总分析风险类型分布",
          "heading": "工作质量与风险观察",
          "metrics": [
            {
              "name": "风险摘要日报",
              "value": 7
            },
            {
              "name": "风险摘要占比",
              "value": "70.0%"
            }
          ]
        },
        {
          "content": "针对提交量波动的日期了解原因，评估是否需要工作安排优化；定期汇总风险摘要日报，提炼共性问题和改进方向；推动部门内日报标准化，提升工作可量化程度。",
          "heading": "管理建议",
          "metrics": []
        }
      ],
      "report_type": "employee_weekly_summary",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "daily_trend": {
          "2026-06-01": 2,
          "2026-06-02": 2,
          "2026-06-03": 2,
          "2026-06-04": 2,
          "2026-06-05": 2
        },
        "report_type": "employee_weekly_summary",
        "risk_reports": 7,
        "department_id": 10,
        "status_counts": {
          "draft": 3,
          "submitted": 7
        },
        "total_reports": 10,
        "top_risk_themes": [],
        "distinct_employees": 2,
        "peak_submission_day": "2026-06-01",
        "week_submission_rate": "100.0%",
        "valley_submission_day": "2026-06-01"
      },
      "source_refs": [
        "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendations": [
        "推动全员日报提交，确保工作进展透明化",
        "汇总本周风险摘要，形成团队风险清单",
        "建立日报质量评分机制，提升填报内容质量"
      ]
    },
    "trace_i
```


### ???? - ????????

**POST /api/v1/reports/generate-draft**

**???**
```json
{
  "report_type": "student_psych_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "trace_id": "report-test-student_psych_weekly",
  "department_id": 10
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 263,
    "draft_no": "DR-20260611113521-4106b2ab",
    "status": "pending_confirm",
    "content_json": {
      "risks": [
        "暂无高危预警",
        "整体平均情绪分 68.0，低于健康阈值"
      ],
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周纳入心理画像 2 份，平均情绪分 68.0，触发预警 2 条。整体心理健康处于关注区间，需介入高风险个案",
      "sections": [
        {
          "content": "本周共 2 名学生完成心理画像评估，整体平均情绪分 68.0。平均情绪分偏低，需关注学生群体的整体心理健康趋势建议结合留学周期（当前处于学期中段，课业压力可能上升）进行综合研判。",
          "heading": "整体心理态势",
          "metrics": [
            {
              "name": "心理画像数",
              "value": 2
            },
            {
              "name": "平均情绪分",
              "value": "68.0 (满分 100)"
            }
          ]
        },
        {
          "content": "高风险管理：0 人，中等风险：1 人，低风险：1 人。无高风险学生，继续保持常规关注。",
          "heading": "风险分层分析",
          "metrics": [
            {
              "name": "高风险",
              "value": 0
            },
            {
              "name": "中风险",
              "value": 1
            },
            {
              "name": "低风险",
              "value": 1
            }
          ]
        },
        {
          "content": "本周主要情绪标签分布：稳定(1)、焦虑(1)。焦虑标签占比突出，可能与近期考试或学业压力相关",
          "heading": "情绪标签与趋势",
          "metrics": [
            {
              "name": "稳定",
              "value": 1
            },
            {
              "name": "焦虑",
              "value": 1
            }
          ]
        },
        {
          "content": "预警总量 2 条，已处理 0 条，待处理 0 条。预警全部闭环处理。建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。",
          "heading": "预警处理与关怀建议",
          "metrics": [
            {
              "name": "预警总量",
              "value": 2
            },
            {
              "name": "已处理",
              "value": 0
            },
            {
              "name": "待处理",
              "value": 0
            }
          ]
        }
      ],
      "report_type": "student_psych_weekly",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "report_type": "student_psych_weekly",
        "total_alerts": 2,
        "department_id": 10,
        "total_profiles": 2,
        "risk_level_counts": {
          "low": 1,
          "medium": 1
        },
        "emotion_tag_counts": {
          "焦虑": 1,
          "稳定": 1
        },
        "alert_status_counts": {
          "processing": 2
        },
        "average_emotion_score": 68.0,
        "alert_risk_level_counts": {
          "low": 1,
          "medium": 1
        }
      },
      "source_refs": [
        "数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendations": [
        "对高风险学生启动 48 小时内深度访谈",
        "组织本学期中段心理健康主题分享活动",
        "建立心理健康预警回访机制，
```


### ???? - complaint_weekly

**POST /api/v1/reports/drafts/259/confirm**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 168,
    "report_no": "RP-20260611113521-9c220481",
    "report_type": "complaint_weekly",
    "title": "投诉处理周报（2026-06-01 至 2026-06-07）",
    "status": "confirmed",
    "content_json": {
      "risks": [
        "待处理工单 1 件未闭环，存在客户满意度下降和服务升级风险"
      ],
      "title": "投诉处理周报（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周期共收到 5 件投诉，已解决 1 件（解决率 20.0%），处理中 3 件，待处理 1 件。整体投诉量处于可控范围，待处理工单需优先跟进，避免积压升级。",
      "sections": [
        {
          "content": "本周期投诉工单总量为 5 件，覆盖待处理、处理中、已解决三种状态。相较前序周期如有数据变化需逐项分析原因。",
          "heading": "整体概况",
          "metrics": [
            {
              "name": "投诉总量",
              "value": 5
            }
          ]
        },
        {
          "content": "已解决 1 件（20.0%），处理中 3 件，待处理 1 件。各状态分布较为均衡，处理节奏正常。",
          "heading": "工单状态与处理进展",
          "metrics": [
            {
              "name": "已解决",
              "value": 1
            },
            {
              "name": "处理中",
              "value": 3
            },
            {
              "name": "待处理",
              "value": 1
            },
            {
              "name": "解决率",
              "value": "20.0%"
            }
          ]
        },
        {
          "content": "当前待处理工单 1 件，如超 48 小时无更新存在客户投诉升级风险，建议优先分配处理人并设定处理时限。",
          "heading": "风险预警",
          "metrics": []
        },
        {
          "content": "建议加强工单分派机制，确保每件投诉在 24 小时内匹配处理人；定期复盘高频投诉类别，制定专项 SOP 减少同类问题重复发生；建立满意度回访机制，对已解决工单进行 48 小时内回访确认。",
          "heading": "改善建议",
          "metrics": []
        }
      ],
      "report_type": "complaint_weekly",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "report_type": "complaint_weekly",
        "department_id": 10,
        "status_counts": {
          "pending": 1,
          "resolved": 1,
          "processing": 3
        },
        "total_tickets": 5,
        "category_counts": {
          "签证办理": 1,
          "院校申请": 1,
          "专业能力投诉": 1,
          "办理时效投诉": 1,
          "服务态度投诉": 1
        },
        "ticket_type_counts": {
          "咨询": 1,
          "投诉": 4
        },
        "avg_processing_hours": 17.0
      },
      "source_refs": [
        "数据来源：student_feedback_ticket 投诉工单表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendations": [
        "建议优先处理待处理工单，确保 48 小时内首次响应",
        "对高频投诉类别进行专项分析，制定预防性 SOP",
        "建立工单处理时效看板，透明化团队服务效率"
      ]
    },
    "source_draft_id": 259,
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "created_by": 101,
    "published_by": null,
    "published_time": null
  },
  "trace_id": null
}
```


### ???? - customer_operation

**POST /api/v1/reports/drafts/260/confirm**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 169,
    "report_no": "RP-20260611113522-55fb5703",
    "report_type": "customer_operation",
    "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
    "status": "confirmed",
    "content_json": {
      "risks": [
        "已流失 1 条线索（主要来自 异业合作 渠道），建议重点复盘该渠道线索质量和跟进流程"
      ],
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": 102
      },
      "summary": "本周期新增线索 8 条，完成客户研判 4 条，活动报名 1 人次。线索研判覆盖率 50.0%，成交 5 单。存在 1 条流失线索需关注归因",
      "sections": [
        {
          "content": "本周期新增客户线索 8 条。线索来源渠道分布：活动引流(1条)、官网(2条)、异业合作(2条)、展会获客(1条)、广告投放(1条)、转介绍(1条)。线索当前所处阶段：新线索(3条)、已成交(5条)、已分析(5条)、已谈判(7条)、已联系(2条)、已流失(1条)。建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。",
          "heading": "意向客户 - 线索获取与渠道分布",
          "metrics": [
            {
              "name": "新增线索",
              "value": 8
            },
            {
              "name": "渠道-活动引流",
              "value": 1
            },
            {
              "name": "渠道-官网",
              "value": 2
            },
            {
              "name": "渠道-异业合作",
              "value": 2
            },
            {
              "name": "渠道-展会获客",
              "value": 1
            },
            {
              "name": "渠道-广告投放",
              "value": 1
            },
            {
              "name": "渠道-转介绍",
              "value": 1
            }
          ]
        },
        {
          "content": "完成客户研判 4 条，研判覆盖率 50.0%。研判等级分布：高意向(2条)、中意向(2条)。高意向客户 2 条，是近期转化重点跟进对象。研判覆盖率正常。 从\"线索\"到\"研判\"的转化漏斗目前为 8 → 4。",
          "heading": "意向客户 - 研判转化漏斗",
          "metrics": [
            {
              "name": "研判数",
              "value": 4
            },
            {
              "name": "研判覆盖率",
              "value": "50.0%"
            },
            {
              "name": "研判-高意向",
              "value": 2
            },
            {
              "name": "研判-中意向",
              "value": 2
            },
            {
              "name": "上周研判数",
              "value": 1
            }
          ]
        },
        {
          "content": "本周期成交客户 5 单，线索到成交转化率 62.5%。从研判分布来看，高意向(2条)、中意向(2条)，高意向客户是成交主力来源。研判等级为高意向的客户应纳入优先跟进序列，加速转化。",
          "heading": "成交客户 - 转化路径与高价值特征",
          "metrics": [
            {
              "name": "成交客户数",
              "value": 5
            },
            {
              "name": "线索→成交转化率",
              "value": "62.5%"
            }
          ]
        },
        {
          "content": "活动报名总计 1 人次，其中已报名 0 人次、已转化 1 人次。活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，活动转化效果良好。",
          "heading": "活动参与与转化跟踪",
          "metrics": [
            {
              "name": "活动报名总人次",
              "value": 1
            },
            {
              "name": "活动-已转化",
              "value": 1
            }
          ]
        },
        {
          "content": "本周期流失线索 1 条，占线索总量的 
```


### ???? - employee_daily_summary

**POST /api/v1/reports/drafts/261/confirm**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 170,
    "report_no": "RP-20260611113522-5b85b956",
    "report_type": "employee_daily_summary",
    "title": "员工日报汇总报告（2026-06-01）",
    "status": "confirmed",
    "content_json": {
      "risks": [
        "全员已提交，暂无执行风险"
      ],
      "title": "员工日报汇总报告（2026-06-01）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本日共汇总日报 2 份，已提交 2 份（提交率 100.0%），草稿 0 份，归档 0 份。存在风险摘要的日报占比偏高，需重点关注",
      "sections": [
        {
          "content": "本日日报提交率 100.0%，其中已提交 2 份、草稿 0 份、已归档 0 份。全员已提交。",
          "heading": "日报提交概览",
          "metrics": [
            {
              "name": "总日报数",
              "value": 2
            },
            {
              "name": "已提交",
              "value": 2
            },
            {
              "name": "草稿",
              "value": 0
            },
            {
              "name": "已归档",
              "value": 0
            }
          ]
        },
        {
          "content": "含风险摘要的日报 2 份，填报明日计划 2 份。风险摘要集中出现，建议汇总分析风险类型并制定应对方案",
          "heading": "工作进展与潜在风险",
          "metrics": [
            {
              "name": "风险摘要日报",
              "value": 2
            },
            {
              "name": "明日计划日报",
              "value": 2
            }
          ]
        },
        {
          "content": "推动未提交和草稿状态日报在当日完成补交；对风险摘要日报进行专题复盘，提炼共性问题；强化明日计划填报要求，提升团队工作的可预见性。",
          "heading": "管理建议",
          "metrics": []
        }
      ],
      "report_type": "employee_daily_summary",
      "source_data": {
        "date_end": "2026-06-01",
        "date_start": "2026-06-01",
        "risk_items": [
          {
            "emp": "Full Employee A",
            "text": "人手不足"
          },
          {
            "emp": "Full Employee B",
            "text": "材料补充中"
          }
        ],
        "report_type": "employee_daily_summary",
        "risk_reports": 2,
        "department_id": 10,
        "draft_reports": 0,
        "status_counts": {
          "submitted": 2
        },
        "total_reports": 2,
        "submission_rate": "10.0%",
        "archived_reports": 0,
        "submitted_reports": 2,
        "key_progress_items": [
          {
            "emp": "Full Employee A",
            "text": "完成院校匹配方案"
          },
          {
            "emp": "Full Employee B",
            "text": "跟进高意向客户3组"
          }
        ],
        "tomorrow_plan_reports": 2,
        "employee_submission_list": [
          {
            "risks": "人手不足",
            "employee_name": "Full Employee A",
            "report_status": "submitted",
            "tomorrow_plan": "预约面谈4组"
          },
          {
            "risks": "材料补充中",
            "employee_name": "Full Employee A",
            "report_status": "draft",
            "tomorrow_plan": "跟进签证进度"
          },
          {
            "risks": "人手不足",
            "employee_na
```


### ???? - employee_weekly_summary

**POST /api/v1/reports/drafts/262/confirm**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 171,
    "report_no": "RP-20260611113522-813f1c42",
    "report_type": "employee_weekly_summary",
    "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
    "status": "confirmed",
    "content_json": {
      "risks": [
        "暂无重大管理风险"
      ],
      "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周共汇总日报 10 份，涉及 2 名员工。平均每人提交 5.0份。含风险摘要日报占比偏高",
      "sections": [
        {
          "content": "本周共 2 人提交日报，总量 10 份。逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。",
          "heading": "周度提交趋势",
          "metrics": [
            {
              "name": "总日报数",
              "value": 10
            },
            {
              "name": "提交员工数",
              "value": 2
            }
          ]
        },
        {
          "content": "逐日提交量变化如下。' + ('工作日提交量高于周末，符合正常规律。' if len(daily_trend) >= 3 else '数据周期较短，建议积累更多数据做趋势分析。')",
          "heading": "每日提交趋势",
          "metrics": [
            {
              "name": "2026-06-01",
              "value": 2
            },
            {
              "name": "2026-06-02",
              "value": 2
            },
            {
              "name": "2026-06-03",
              "value": 2
            },
            {
              "name": "2026-06-04",
              "value": 2
            },
            {
              "name": "2026-06-05",
              "value": 2
            }
          ]
        },
        {
          "content": "含风险摘要日报 7 份（占比 70.0%）。风险摘要占比较高，建议汇总分析风险类型分布",
          "heading": "工作质量与风险观察",
          "metrics": [
            {
              "name": "风险摘要日报",
              "value": 7
            },
            {
              "name": "风险摘要占比",
              "value": "70.0%"
            }
          ]
        },
        {
          "content": "针对提交量波动的日期了解原因，评估是否需要工作安排优化；定期汇总风险摘要日报，提炼共性问题和改进方向；推动部门内日报标准化，提升工作可量化程度。",
          "heading": "管理建议",
          "metrics": []
        }
      ],
      "report_type": "employee_weekly_summary",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "daily_trend": {
          "2026-06-01": 2,
          "2026-06-02": 2,
          "2026-06-03": 2,
          "2026-06-04": 2,
          "2026-06-05": 2
        },
        "report_type": "employee_weekly_summary",
        "risk_reports": 7,
        "department_id": 10,
        "status_counts": {
          "draft": 3,
          "submitted": 7
        },
        "total_reports": 10,
        "top_risk_themes": [],
        "distinct_employees": 2,
        "peak_submission_day": "2026-06-01",
        "week_submission_rate": "100.0%",
        "valley_submission_day": "2026-06-01"
      },
      "source_refs": [
        "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendations": [
        "推动全员日报提交，确保工作进展透
```


### ???? - student_psych_weekly

**POST /api/v1/reports/drafts/263/confirm**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 172,
    "report_no": "RP-20260611113522-c50fb477",
    "report_type": "student_psych_weekly",
    "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
    "status": "confirmed",
    "content_json": {
      "risks": [
        "暂无高危预警",
        "整体平均情绪分 68.0，低于健康阈值"
      ],
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周纳入心理画像 2 份，平均情绪分 68.0，触发预警 2 条。整体心理健康处于关注区间，需介入高风险个案",
      "sections": [
        {
          "content": "本周共 2 名学生完成心理画像评估，整体平均情绪分 68.0。平均情绪分偏低，需关注学生群体的整体心理健康趋势建议结合留学周期（当前处于学期中段，课业压力可能上升）进行综合研判。",
          "heading": "整体心理态势",
          "metrics": [
            {
              "name": "心理画像数",
              "value": 2
            },
            {
              "name": "平均情绪分",
              "value": "68.0 (满分 100)"
            }
          ]
        },
        {
          "content": "高风险管理：0 人，中等风险：1 人，低风险：1 人。无高风险学生，继续保持常规关注。",
          "heading": "风险分层分析",
          "metrics": [
            {
              "name": "高风险",
              "value": 0
            },
            {
              "name": "中风险",
              "value": 1
            },
            {
              "name": "低风险",
              "value": 1
            }
          ]
        },
        {
          "content": "本周主要情绪标签分布：稳定(1)、焦虑(1)。焦虑标签占比突出，可能与近期考试或学业压力相关",
          "heading": "情绪标签与趋势",
          "metrics": [
            {
              "name": "稳定",
              "value": 1
            },
            {
              "name": "焦虑",
              "value": 1
            }
          ]
        },
        {
          "content": "预警总量 2 条，已处理 0 条，待处理 0 条。预警全部闭环处理。建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。",
          "heading": "预警处理与关怀建议",
          "metrics": [
            {
              "name": "预警总量",
              "value": 2
            },
            {
              "name": "已处理",
              "value": 0
            },
            {
              "name": "待处理",
              "value": 0
            }
          ]
        }
      ],
      "report_type": "student_psych_weekly",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "report_type": "student_psych_weekly",
        "total_alerts": 2,
        "department_id": 10,
        "total_profiles": 2,
        "risk_level_counts": {
          "low": 1,
          "medium": 1
        },
        "emotion_tag_counts": {
          "焦虑": 1,
          "稳定": 1
        },
        "alert_status_counts": {
          "processing": 2
        },
        "average_emotion_score": 68.0,
        "alert_risk_level_counts": {
          "low": 1,
          "medium": 1
        }
      },
      "source_refs": [
        "数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendation
```


### ???? - complaint_weekly

**POST /api/v1/reports/168/publish**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 168,
    "report_no": "RP-20260611113521-9c220481",
    "report_type": "complaint_weekly",
    "title": "投诉处理周报（2026-06-01 至 2026-06-07）",
    "status": "published",
    "content_json": {
      "risks": [
        "待处理工单 1 件未闭环，存在客户满意度下降和服务升级风险"
      ],
      "title": "投诉处理周报（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周期共收到 5 件投诉，已解决 1 件（解决率 20.0%），处理中 3 件，待处理 1 件。整体投诉量处于可控范围，待处理工单需优先跟进，避免积压升级。",
      "sections": [
        {
          "content": "本周期投诉工单总量为 5 件，覆盖待处理、处理中、已解决三种状态。相较前序周期如有数据变化需逐项分析原因。",
          "heading": "整体概况",
          "metrics": [
            {
              "name": "投诉总量",
              "value": 5
            }
          ]
        },
        {
          "content": "已解决 1 件（20.0%），处理中 3 件，待处理 1 件。各状态分布较为均衡，处理节奏正常。",
          "heading": "工单状态与处理进展",
          "metrics": [
            {
              "name": "已解决",
              "value": 1
            },
            {
              "name": "处理中",
              "value": 3
            },
            {
              "name": "待处理",
              "value": 1
            },
            {
              "name": "解决率",
              "value": "20.0%"
            }
          ]
        },
        {
          "content": "当前待处理工单 1 件，如超 48 小时无更新存在客户投诉升级风险，建议优先分配处理人并设定处理时限。",
          "heading": "风险预警",
          "metrics": []
        },
        {
          "content": "建议加强工单分派机制，确保每件投诉在 24 小时内匹配处理人；定期复盘高频投诉类别，制定专项 SOP 减少同类问题重复发生；建立满意度回访机制，对已解决工单进行 48 小时内回访确认。",
          "heading": "改善建议",
          "metrics": []
        }
      ],
      "report_type": "complaint_weekly",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "report_type": "complaint_weekly",
        "department_id": 10,
        "status_counts": {
          "pending": 1,
          "resolved": 1,
          "processing": 3
        },
        "total_tickets": 5,
        "category_counts": {
          "签证办理": 1,
          "院校申请": 1,
          "专业能力投诉": 1,
          "办理时效投诉": 1,
          "服务态度投诉": 1
        },
        "ticket_type_counts": {
          "咨询": 1,
          "投诉": 4
        },
        "avg_processing_hours": 17.0
      },
      "source_refs": [
        "数据来源：student_feedback_ticket 投诉工单表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendations": [
        "建议优先处理待处理工单，确保 48 小时内首次响应",
        "对高频投诉类别进行专项分析，制定预防性 SOP",
        "建立工单处理时效看板，透明化团队服务效率"
      ]
    },
    "source_draft_id": 259,
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "created_by": 101,
    "published_by": 101,
    "published_time": "2026-06-11T11:35:22"
  },
  "trace_id": null
}
```


### ???? - customer_operation

**POST /api/v1/reports/169/publish**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 169,
    "report_no": "RP-20260611113522-55fb5703",
    "report_type": "customer_operation",
    "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
    "status": "published",
    "content_json": {
      "risks": [
        "已流失 1 条线索（主要来自 异业合作 渠道），建议重点复盘该渠道线索质量和跟进流程"
      ],
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": 102
      },
      "summary": "本周期新增线索 8 条，完成客户研判 4 条，活动报名 1 人次。线索研判覆盖率 50.0%，成交 5 单。存在 1 条流失线索需关注归因",
      "sections": [
        {
          "content": "本周期新增客户线索 8 条。线索来源渠道分布：活动引流(1条)、官网(2条)、异业合作(2条)、展会获客(1条)、广告投放(1条)、转介绍(1条)。线索当前所处阶段：新线索(3条)、已成交(5条)、已分析(5条)、已谈判(7条)、已联系(2条)、已流失(1条)。建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。",
          "heading": "意向客户 - 线索获取与渠道分布",
          "metrics": [
            {
              "name": "新增线索",
              "value": 8
            },
            {
              "name": "渠道-活动引流",
              "value": 1
            },
            {
              "name": "渠道-官网",
              "value": 2
            },
            {
              "name": "渠道-异业合作",
              "value": 2
            },
            {
              "name": "渠道-展会获客",
              "value": 1
            },
            {
              "name": "渠道-广告投放",
              "value": 1
            },
            {
              "name": "渠道-转介绍",
              "value": 1
            }
          ]
        },
        {
          "content": "完成客户研判 4 条，研判覆盖率 50.0%。研判等级分布：高意向(2条)、中意向(2条)。高意向客户 2 条，是近期转化重点跟进对象。研判覆盖率正常。 从\"线索\"到\"研判\"的转化漏斗目前为 8 → 4。",
          "heading": "意向客户 - 研判转化漏斗",
          "metrics": [
            {
              "name": "研判数",
              "value": 4
            },
            {
              "name": "研判覆盖率",
              "value": "50.0%"
            },
            {
              "name": "研判-高意向",
              "value": 2
            },
            {
              "name": "研判-中意向",
              "value": 2
            },
            {
              "name": "上周研判数",
              "value": 1
            }
          ]
        },
        {
          "content": "本周期成交客户 5 单，线索到成交转化率 62.5%。从研判分布来看，高意向(2条)、中意向(2条)，高意向客户是成交主力来源。研判等级为高意向的客户应纳入优先跟进序列，加速转化。",
          "heading": "成交客户 - 转化路径与高价值特征",
          "metrics": [
            {
              "name": "成交客户数",
              "value": 5
            },
            {
              "name": "线索→成交转化率",
              "value": "62.5%"
            }
          ]
        },
        {
          "content": "活动报名总计 1 人次，其中已报名 0 人次、已转化 1 人次。活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，活动转化效果良好。",
          "heading": "活动参与与转化跟踪",
          "metrics": [
            {
              "name": "活动报名总人次",
              "value": 1
            },
            {
              "name": "活动-已转化",
              "value": 1
            }
          ]
        },
        {
          "content": "本周期流失线索 1 条，占线索总量的 
```


### ???? - employee_daily_summary

**POST /api/v1/reports/170/publish**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 170,
    "report_no": "RP-20260611113522-5b85b956",
    "report_type": "employee_daily_summary",
    "title": "员工日报汇总报告（2026-06-01）",
    "status": "published",
    "content_json": {
      "risks": [
        "全员已提交，暂无执行风险"
      ],
      "title": "员工日报汇总报告（2026-06-01）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本日共汇总日报 2 份，已提交 2 份（提交率 100.0%），草稿 0 份，归档 0 份。存在风险摘要的日报占比偏高，需重点关注",
      "sections": [
        {
          "content": "本日日报提交率 100.0%，其中已提交 2 份、草稿 0 份、已归档 0 份。全员已提交。",
          "heading": "日报提交概览",
          "metrics": [
            {
              "name": "总日报数",
              "value": 2
            },
            {
              "name": "已提交",
              "value": 2
            },
            {
              "name": "草稿",
              "value": 0
            },
            {
              "name": "已归档",
              "value": 0
            }
          ]
        },
        {
          "content": "含风险摘要的日报 2 份，填报明日计划 2 份。风险摘要集中出现，建议汇总分析风险类型并制定应对方案",
          "heading": "工作进展与潜在风险",
          "metrics": [
            {
              "name": "风险摘要日报",
              "value": 2
            },
            {
              "name": "明日计划日报",
              "value": 2
            }
          ]
        },
        {
          "content": "推动未提交和草稿状态日报在当日完成补交；对风险摘要日报进行专题复盘，提炼共性问题；强化明日计划填报要求，提升团队工作的可预见性。",
          "heading": "管理建议",
          "metrics": []
        }
      ],
      "report_type": "employee_daily_summary",
      "source_data": {
        "date_end": "2026-06-01",
        "date_start": "2026-06-01",
        "risk_items": [
          {
            "emp": "Full Employee A",
            "text": "人手不足"
          },
          {
            "emp": "Full Employee B",
            "text": "材料补充中"
          }
        ],
        "report_type": "employee_daily_summary",
        "risk_reports": 2,
        "department_id": 10,
        "draft_reports": 0,
        "status_counts": {
          "submitted": 2
        },
        "total_reports": 2,
        "submission_rate": "10.0%",
        "archived_reports": 0,
        "submitted_reports": 2,
        "key_progress_items": [
          {
            "emp": "Full Employee A",
            "text": "完成院校匹配方案"
          },
          {
            "emp": "Full Employee B",
            "text": "跟进高意向客户3组"
          }
        ],
        "tomorrow_plan_reports": 2,
        "employee_submission_list": [
          {
            "risks": "人手不足",
            "employee_name": "Full Employee A",
            "report_status": "submitted",
            "tomorrow_plan": "预约面谈4组"
          },
          {
            "risks": "材料补充中",
            "employee_name": "Full Employee A",
            "report_status": "draft",
            "tomorrow_plan": "跟进签证进度"
          },
          {
            "risks": "人手不足",
            "employee_na
```


### ???? - employee_weekly_summary

**POST /api/v1/reports/171/publish**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 171,
    "report_no": "RP-20260611113522-813f1c42",
    "report_type": "employee_weekly_summary",
    "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
    "status": "published",
    "content_json": {
      "risks": [
        "暂无重大管理风险"
      ],
      "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周共汇总日报 10 份，涉及 2 名员工。平均每人提交 5.0份。含风险摘要日报占比偏高",
      "sections": [
        {
          "content": "本周共 2 人提交日报，总量 10 份。逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。",
          "heading": "周度提交趋势",
          "metrics": [
            {
              "name": "总日报数",
              "value": 10
            },
            {
              "name": "提交员工数",
              "value": 2
            }
          ]
        },
        {
          "content": "逐日提交量变化如下。' + ('工作日提交量高于周末，符合正常规律。' if len(daily_trend) >= 3 else '数据周期较短，建议积累更多数据做趋势分析。')",
          "heading": "每日提交趋势",
          "metrics": [
            {
              "name": "2026-06-01",
              "value": 2
            },
            {
              "name": "2026-06-02",
              "value": 2
            },
            {
              "name": "2026-06-03",
              "value": 2
            },
            {
              "name": "2026-06-04",
              "value": 2
            },
            {
              "name": "2026-06-05",
              "value": 2
            }
          ]
        },
        {
          "content": "含风险摘要日报 7 份（占比 70.0%）。风险摘要占比较高，建议汇总分析风险类型分布",
          "heading": "工作质量与风险观察",
          "metrics": [
            {
              "name": "风险摘要日报",
              "value": 7
            },
            {
              "name": "风险摘要占比",
              "value": "70.0%"
            }
          ]
        },
        {
          "content": "针对提交量波动的日期了解原因，评估是否需要工作安排优化；定期汇总风险摘要日报，提炼共性问题和改进方向；推动部门内日报标准化，提升工作可量化程度。",
          "heading": "管理建议",
          "metrics": []
        }
      ],
      "report_type": "employee_weekly_summary",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "daily_trend": {
          "2026-06-01": 2,
          "2026-06-02": 2,
          "2026-06-03": 2,
          "2026-06-04": 2,
          "2026-06-05": 2
        },
        "report_type": "employee_weekly_summary",
        "risk_reports": 7,
        "department_id": 10,
        "status_counts": {
          "draft": 3,
          "submitted": 7
        },
        "total_reports": 10,
        "top_risk_themes": [],
        "distinct_employees": 2,
        "peak_submission_day": "2026-06-01",
        "week_submission_rate": "100.0%",
        "valley_submission_day": "2026-06-01"
      },
      "source_refs": [
        "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendations": [
        "推动全员日报提交，确保工作进展透
```


### ???? - student_psych_weekly

**POST /api/v1/reports/172/publish**

**???**
```json
{}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 172,
    "report_no": "RP-20260611113522-c50fb477",
    "report_type": "student_psych_weekly",
    "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
    "status": "published",
    "content_json": {
      "risks": [
        "暂无高危预警",
        "整体平均情绪分 68.0，低于健康阈值"
      ],
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "filters": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "department_id": 10,
        "owner_user_id": null
      },
      "summary": "本周纳入心理画像 2 份，平均情绪分 68.0，触发预警 2 条。整体心理健康处于关注区间，需介入高风险个案",
      "sections": [
        {
          "content": "本周共 2 名学生完成心理画像评估，整体平均情绪分 68.0。平均情绪分偏低，需关注学生群体的整体心理健康趋势建议结合留学周期（当前处于学期中段，课业压力可能上升）进行综合研判。",
          "heading": "整体心理态势",
          "metrics": [
            {
              "name": "心理画像数",
              "value": 2
            },
            {
              "name": "平均情绪分",
              "value": "68.0 (满分 100)"
            }
          ]
        },
        {
          "content": "高风险管理：0 人，中等风险：1 人，低风险：1 人。无高风险学生，继续保持常规关注。",
          "heading": "风险分层分析",
          "metrics": [
            {
              "name": "高风险",
              "value": 0
            },
            {
              "name": "中风险",
              "value": 1
            },
            {
              "name": "低风险",
              "value": 1
            }
          ]
        },
        {
          "content": "本周主要情绪标签分布：稳定(1)、焦虑(1)。焦虑标签占比突出，可能与近期考试或学业压力相关",
          "heading": "情绪标签与趋势",
          "metrics": [
            {
              "name": "稳定",
              "value": 1
            },
            {
              "name": "焦虑",
              "value": 1
            }
          ]
        },
        {
          "content": "预警总量 2 条，已处理 0 条，待处理 0 条。预警全部闭环处理。建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。",
          "heading": "预警处理与关怀建议",
          "metrics": [
            {
              "name": "预警总量",
              "value": 2
            },
            {
              "name": "已处理",
              "value": 0
            },
            {
              "name": "待处理",
              "value": 0
            }
          ]
        }
      ],
      "report_type": "student_psych_weekly",
      "source_data": {
        "date_end": "2026-06-07",
        "date_start": "2026-06-01",
        "report_type": "student_psych_weekly",
        "total_alerts": 2,
        "department_id": 10,
        "total_profiles": 2,
        "risk_level_counts": {
          "low": 1,
          "medium": 1
        },
        "emotion_tag_counts": {
          "焦虑": 1,
          "稳定": 1
        },
        "alert_status_counts": {
          "processing": 2
        },
        "average_emotion_score": 68.0,
        "alert_risk_level_counts": {
          "low": 1,
          "medium": 1
        }
      },
      "source_refs": [
        "数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
      ],
      "recommendation
```


### ??WORD - ??????

**POST /api/v1/reports/168/exports**

**???**
```json
{
  "export_type": "word"
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 327,
    "report_id": 168,
    "export_type": "word",
    "file_name": "RP-20260611113521-9c220481.docx",
    "file_path": "storage\\reports\\RP-20260611113521-9c220481.docx",
    "status": "success",
    "error_message": null
  },
  "trace_id": null
}
```


### ??PDF - ??????

**POST /api/v1/reports/168/exports**

**???**
```json
{
  "export_type": "pdf"
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 328,
    "report_id": 168,
    "export_type": "pdf",
    "file_name": "RP-20260611113521-9c220481.pdf",
    "file_path": "storage\\reports\\RP-20260611113521-9c220481.pdf",
    "status": "success",
    "error_message": null
  },
  "trace_id": null
}
```


### ??WORD - ??????

**GET /api/v1/reports/exports/327/download**

**??????** 200

- ?????37565 bytes
- ????16????`504b03041400000008006b5ccb5cad52`


### ??PDF - ??????

**GET /api/v1/reports/exports/328/download**

**??????** 200

- ?????5247 bytes
- ????16????`255044462d312e340a25938c8b9e2052`


### AI Tools ??????

**POST /api/v1/ai-tools/query_report_source_data**

**???**
```json
{
  "report_type": "complaint_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 10,
  "conversation_id": "test-conv",
  "trace_id": "test-trace"
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "tool_name": "query_report_source_data",
    "result": {
      "report_type": "complaint_weekly",
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "total_tickets": 5,
      "status_counts": {
        "resolved": 1,
        "processing": 3,
        "pending": 1
      },
      "category_counts": {
        "专业能力投诉": 1,
        "院校申请": 1,
        "办理时效投诉": 1,
        "服务态度投诉": 1,
        "签证办理": 1
      },
      "ticket_type_counts": {
        "投诉": 4,
        "咨询": 1
      },
      "avg_processing_hours": 17.0
    },
    "draft_id": null,
    "requires_confirmation": false
  },
  "trace_id": "test-trace"
}
```


### AI Tools ??????

**POST /api/v1/ai-tools/query_report_source_data**

**???**
```json
{
  "report_type": "student_psych_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 10
}
```

**??????** 200

**????**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "tool_name": "query_report_source_data",
    "result": {
      "report_type": "student_psych_weekly",
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "total_profiles": 2,
      "risk_level_counts": {
        "low": 1,
        "medium": 1
      },
      "emotion_tag_counts": {
        "稳定": 1,
        "焦虑": 1
      },
      "average_emotion_score": 68.0,
      "total_alerts": 2,
      "alert_status_counts": {
        "processing": 2
      },
      "alert_risk_level_counts": {
        "low": 1,
        "medium": 1
      }
    },
    "draft_id": null,
    "requires_confirmation": false
  },
  "trace_id": null
}
```


### ???? - ???????????

**POST /api/v1/reports/generate-draft**

**???**
```json
{
  "report_type": "complaint_weekly"
}
```

**??????** 403

**????**
```json
{
  "detail": "当前角色无权访问该接口"
}
```


### ???? - ???????????

**POST /api/v1/reports/168/publish**

**???**
```json
{}
```

**??????** 403

**????**
```json
{
  "detail": "当前角色无权访问该接口"
}
```


