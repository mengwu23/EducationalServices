# 报告模块全链路验收结果

本文档由 `backend/scripts/run_report_full_acceptance.py` 自动生成，记录报告模块后端全链路测试的完整接口输入输出。

敏感信息处理：MySQL 密码、Dify Key、AI Tools Secret 不写入本文档；二进制文件只记录大小、哈希和文件头摘要。

## 测试数据摘要

- 统计周期：`2026-06-01` 至 `2026-06-07`
- 主测部门：`10`，跨部门对照部门：`20`
- 主测管理员用户：`101`，主测员工用户：`102`，主测学生用户：`105`
- 覆盖数据：投诉工单、客户线索、客户研判、活动报名、员工日报、学生心理画像、学生心理预警
- 过滤验证：包含跨部门数据和 `is_delete=1` 逻辑删除数据
- 验收流程：AI Tool 聚合、生成草稿、确认草稿、发布报告、Word/PDF 导出和下载

## mock 阶段

- 执行时间：`2026-06-11 10:42:05`
- 后端地址：`http://127.0.0.1:18000`
- 数据库：`mysql+pymysql://127.0.0.1:3306/education_service_ai_test`
- AI Tools Secret：`已配置`


### 投诉处理周报 - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "mock-complaint_weekly",
    "conversation_id": "mock-complaint_weekly-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "466",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "complaint_weekly",
        "date_start": "2026-06-01",
        "date_end": "2026-06-07",
        "department_id": 10,
        "total_tickets": 3,
        "status_counts": {
          "pending": 1,
          "processing": 1,
          "resolved": 1
        },
        "category_counts": {
          "教学": 1,
          "服务": 1,
          "签证": 1
        },
        "ticket_type_counts": {
          "complaint": 3
        },
        "avg_processing_hours": 29.8
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "mock-complaint_weekly"
  }
}
```

### 投诉处理周报 - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "mock-complaint_weekly"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2447",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 183,
      "draft_no": "DR-20260611104205-0c4559cf",
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
        "summary": "本周期共收到 3 件投诉，已解决 1 件（解决率 33.3%），处理中 1 件，待处理 1 件。整体投诉量处于可控范围，待处理工单需优先跟进，避免积压升级。",
        "sections": [
          {
            "content": "本周期投诉工单总量为 3 件，覆盖待处理、处理中、已解决三种状态。相较前序周期如有数据变化需逐项分析原因。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "投诉总量",
                "value": 3
              }
            ]
          },
          {
            "content": "已解决 1 件（33.3%），处理中 1 件，待处理 1 件。待处理占比偏高，需关注是否有工单未及时分配处理人",
            "heading": "工单状态与处理进展",
            "metrics": [
              {
                "name": "已解决",
                "value": 1
              },
              {
                "name": "处理中",
                "value": 1
              },
              {
                "name": "待处理",
                "value": 1
              },
              {
                "name": "解决率",
                "value": "33.3%"
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
            "processing": 1
          },
          "total_tickets": 3,
          "category_counts": {
            "教学": 1,
            "服务": 1,
            "签证": 1
          },
          "ticket_type_counts": {
            "complaint": 3
          },
          "avg_processing_hours": 29.8
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
      "trace_id": "mock-complaint_weekly"
    },
    "trace_id": "mock-complaint_weekly"
  }
}
```

### 投诉处理周报 - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/183/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2631",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 128,
      "report_no": "RP-20260611104205-267d7184",
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
        "summary": "本周期共收到 3 件投诉，已解决 1 件（解决率 33.3%），处理中 1 件，待处理 1 件。整体投诉量处于可控范围，待处理工单需优先跟进，避免积压升级。",
        "sections": [
          {
            "content": "本周期投诉工单总量为 3 件，覆盖待处理、处理中、已解决三种状态。相较前序周期如有数据变化需逐项分析原因。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "投诉总量",
                "value": 3
              }
            ]
          },
          {
            "content": "已解决 1 件（33.3%），处理中 1 件，待处理 1 件。待处理占比偏高，需关注是否有工单未及时分配处理人",
            "heading": "工单状态与处理进展",
            "metrics": [
              {
                "name": "已解决",
                "value": 1
              },
              {
                "name": "处理中",
                "value": 1
              },
              {
                "name": "待处理",
                "value": 1
              },
              {
                "name": "解决率",
                "value": "33.3%"
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
            "processing": 1
          },
          "total_tickets": 3,
          "category_counts": {
            "教学": 1,
            "服务": 1,
            "签证": 1
          },
          "ticket_type_counts": {
            "complaint": 3
          },
          "avg_processing_hours": 29.8
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
      "source_draft_id": 183,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/128/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2647",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 128,
      "report_no": "RP-20260611104205-267d7184",
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
        "summary": "本周期共收到 3 件投诉，已解决 1 件（解决率 33.3%），处理中 1 件，待处理 1 件。整体投诉量处于可控范围，待处理工单需优先跟进，避免积压升级。",
        "sections": [
          {
            "content": "本周期投诉工单总量为 3 件，覆盖待处理、处理中、已解决三种状态。相较前序周期如有数据变化需逐项分析原因。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "投诉总量",
                "value": 3
              }
            ]
          },
          {
            "content": "已解决 1 件（33.3%），处理中 1 件，待处理 1 件。待处理占比偏高，需关注是否有工单未及时分配处理人",
            "heading": "工单状态与处理进展",
            "metrics": [
              {
                "name": "已解决",
                "value": 1
              },
              {
                "name": "处理中",
                "value": 1
              },
              {
                "name": "待处理",
                "value": 1
              },
              {
                "name": "解决率",
                "value": "33.3%"
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
            "processing": 1
          },
          "total_tickets": 3,
          "category_counts": {
            "教学": 1,
            "服务": 1,
            "签证": 1
          },
          "ticket_type_counts": {
            "complaint": 3
          },
          "avg_processing_hours": 29.8
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
      "source_draft_id": 183,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:06"
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/128/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 253,
      "report_id": 128,
      "export_type": "word",
      "file_name": "RP-20260611104205-267d7184.docx",
      "file_path": "storage\\reports\\RP-20260611104205-267d7184.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/253/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104205-267d7184.docx\"",
    "content-length": "37569"
  },
  "binary": {
    "size_bytes": 37569,
    "sha256": "df4d5c08a829de9a66829c294fde71a33f2be097450f55b490641d213f7f33ba",
    "first_16_bytes_hex": "504b03041400000008004255cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/128/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 254,
      "report_id": 128,
      "export_type": "pdf",
      "file_name": "RP-20260611104205-267d7184.pdf",
      "file_path": "storage\\reports\\RP-20260611104205-267d7184.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/254/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104205-267d7184.pdf\"",
    "content-length": "5245"
  },
  "binary": {
    "size_bytes": 5245,
    "sha256": "c76031f7676829cffcbfab3874cd8c046d4763fae7b3fd5a9d6fa15bc4490f10",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 客户经营分析报告 - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "customer_operation",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "owner_user_id": 102,
    "trace_id": "mock-customer_operation",
    "conversation_id": "mock-customer_operation-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "773",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "customer_operation",
        "date_start": "2026-06-01",
        "date_end": "2026-06-07",
        "department_id": 10,
        "owner_user_id": 102,
        "new_leads": 2,
        "analysis_records": 2,
        "event_registrations": 2,
        "lead_source_breakdown": {
          "公开课": 1,
          "转介绍": 1
        },
        "lead_status_breakdown": {
          "new": 1,
          "following": 1
        },
        "analysis_result_breakdown": {
          "high": 1,
          "medium": 1
        },
        "event_registration_breakdown": {
          "attended": 1,
          "registered": 1
        },
        "prev_period": {
          "date_start": "2026-05-26",
          "date_end": "2026-06-01",
          "leads": 1,
          "analysis": 0,
          "events": 0
        },
        "lead_trend": {
          "delta_pct": 100.0,
          "label": "上升"
        },
        "churn_source_breakdown": {},
        "churn_stage_breakdown": {}
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "mock-customer_operation"
  }
}
```

### 客户经营分析报告 - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "customer_operation",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "owner_user_id": 102,
    "trace_id": "mock-customer_operation"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "4818",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 184,
      "draft_no": "DR-20260611104206-81937cb8",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本周期零成交，线索到签约的转化链路存在阻断，需紧急排查瓶颈环节"
        ],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条，完成客户研判 2 条，活动报名 2 人次。线索研判覆盖率 100.0%，暂无已成交客户。",
        "sections": [
          {
            "content": "本周期新增客户线索 2 条。线索来源渠道分布：公开课(1条)、转介绍(1条)。线索当前所处阶段：new(1条)、following(1条)。建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。",
            "heading": "意向客户 - 线索获取与渠道分布",
            "metrics": [
              {
                "name": "新增线索",
                "value": 2
              },
              {
                "name": "渠道-公开课",
                "value": 1
              },
              {
                "name": "渠道-转介绍",
                "value": 1
              }
            ]
          },
          {
            "content": "完成客户研判 2 条，研判覆盖率 100.0%。研判等级分布：high(1条)、medium(1条)。高意向客户 1 条，是近期转化重点跟进对象。研判覆盖率正常。 从\"线索\"到\"研判\"的转化漏斗目前为 2 → 2。",
            "heading": "意向客户 - 研判转化漏斗",
            "metrics": [
              {
                "name": "研判数",
                "value": 2
              },
              {
                "name": "研判覆盖率",
                "value": "100.0%"
              },
              {
                "name": "研判-high",
                "value": 1
              },
              {
                "name": "研判-medium",
                "value": 1
              }
            ]
          },
          {
            "content": "本周期成交客户 0 单，线索到成交转化率 0.0%。从研判分布来看，high(1条)、medium(1条)，高意向客户是成交主力来源。研判等级为高意向的客户应纳入优先跟进序列，加速转化。暂无成交客户，建议复盘从研判到签约环节的转化障碍",
            "heading": "成交客户 - 转化路径与高价值特征",
            "metrics": [
              {
                "name": "成交客户数",
                "value": 0
              },
              {
                "name": "线索→成交转化率",
                "value": "0.0%"
              }
            ]
          },
          {
            "content": "活动报名总计 2 人次，其中已报名 1 人次、已转化 0 人次。活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，将活动报名 → 研判 → 签约的转化链打通。",
            "heading": "活动参与与转化跟踪",
            "metrics": [
              {
                "name": "活动报名总人次",
                "value": 2
              },
              {
                "name": "活动-attended",
                "value": 1
              },
              {
                "name": "活动-registered",
                "value": 1
              }
            ]
          },
          {
            "content": "本周期流失线索 0 条，占线索总量的 0.0%。当前处于\"废弃/已关单\"状态的线索 0 条，暂无流失线索，客户留存状况良好。",
            "heading": "流失客户 - 归因分析与预警",
            "metrics": [
              {
                "name": "流失线索数",
                "value": 0
              },
              {
                "name": "流失占比",
                "value": "0.0%"
              }
            ]
          },
          {
            "content": "基于本周期数据，线索来源以 公开课 为主（占比 50.0%）。研判后高意向客群占比 50.0%。当前客群画像：以活动引流和转介绍为主要获客方式，高意向客户特征集中在研判结果为\"高意向\"的群体。建议后续补充客户行业、规模、预算等维度数据，进一步提升画像精准度。",
            "heading": "客群特征与画像提炼",
            "metrics": []
          },
          {
            "content": "建议建立线索分级机制，优先跟进高意向线索；定期复盘研判转化漏斗，定位各环节流失原因；将活动报名客户纳入专项跟进序列，提升活动线索转化率；建立流失预警模型，对长期无互动线索自动标记并推送挽回策略；按月/周输出客户经营健康度看板，支撑全链路决策闭环。",
            "heading": "全链路经营建议",
            "metrics": []
          }
        ],
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "lead_trend": {
            "label": "上升",
            "delta_pct": 100.0
          },
          "prev_period": {
            "leads": 1,
            "events": 0,
            "analysis": 0,
            "date_end": "2026-06-01",
            "date_start": "2026-05-26"
          },
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
          "analysis_records": 2,
          "event_registrations": 2,
          "churn_stage_breakdown": {},
          "lead_source_breakdown": {
            "公开课": 1,
            "转介绍": 1
          },
          "lead_status_breakdown": {
            "new": 1,
            "following": 1
          },
          "churn_source_breakdown": {},
          "analysis_result_breakdown": {
            "high": 1,
            "medium": 1
          },
          "event_registration_breakdown": {
            "attended": 1,
            "registered": 1
          }
        },
        "source_refs": [
          "数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
          "对活动报名客户建立 48 小时回访机制，推动转化",
          "建立线索分级标准，按意向度匹配跟进强度",
          "每周复盘流失线索共性特征，沉淀流失预防 SOP",
          "将高意向客户纳入重点跟进看板，确保闭环管理"
        ]
      },
      "trace_id": "mock-customer_operation"
    },
    "trace_id": "mock-customer_operation"
  }
}
```

### 客户经营分析报告 - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/184/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "5012",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 129,
      "report_no": "RP-20260611104206-24322e6c",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本周期零成交，线索到签约的转化链路存在阻断，需紧急排查瓶颈环节"
        ],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条，完成客户研判 2 条，活动报名 2 人次。线索研判覆盖率 100.0%，暂无已成交客户。",
        "sections": [
          {
            "content": "本周期新增客户线索 2 条。线索来源渠道分布：公开课(1条)、转介绍(1条)。线索当前所处阶段：new(1条)、following(1条)。建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。",
            "heading": "意向客户 - 线索获取与渠道分布",
            "metrics": [
              {
                "name": "新增线索",
                "value": 2
              },
              {
                "name": "渠道-公开课",
                "value": 1
              },
              {
                "name": "渠道-转介绍",
                "value": 1
              }
            ]
          },
          {
            "content": "完成客户研判 2 条，研判覆盖率 100.0%。研判等级分布：high(1条)、medium(1条)。高意向客户 1 条，是近期转化重点跟进对象。研判覆盖率正常。 从\"线索\"到\"研判\"的转化漏斗目前为 2 → 2。",
            "heading": "意向客户 - 研判转化漏斗",
            "metrics": [
              {
                "name": "研判数",
                "value": 2
              },
              {
                "name": "研判覆盖率",
                "value": "100.0%"
              },
              {
                "name": "研判-high",
                "value": 1
              },
              {
                "name": "研判-medium",
                "value": 1
              }
            ]
          },
          {
            "content": "本周期成交客户 0 单，线索到成交转化率 0.0%。从研判分布来看，high(1条)、medium(1条)，高意向客户是成交主力来源。研判等级为高意向的客户应纳入优先跟进序列，加速转化。暂无成交客户，建议复盘从研判到签约环节的转化障碍",
            "heading": "成交客户 - 转化路径与高价值特征",
            "metrics": [
              {
                "name": "成交客户数",
                "value": 0
              },
              {
                "name": "线索→成交转化率",
                "value": "0.0%"
              }
            ]
          },
          {
            "content": "活动报名总计 2 人次，其中已报名 1 人次、已转化 0 人次。活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，将活动报名 → 研判 → 签约的转化链打通。",
            "heading": "活动参与与转化跟踪",
            "metrics": [
              {
                "name": "活动报名总人次",
                "value": 2
              },
              {
                "name": "活动-attended",
                "value": 1
              },
              {
                "name": "活动-registered",
                "value": 1
              }
            ]
          },
          {
            "content": "本周期流失线索 0 条，占线索总量的 0.0%。当前处于\"废弃/已关单\"状态的线索 0 条，暂无流失线索，客户留存状况良好。",
            "heading": "流失客户 - 归因分析与预警",
            "metrics": [
              {
                "name": "流失线索数",
                "value": 0
              },
              {
                "name": "流失占比",
                "value": "0.0%"
              }
            ]
          },
          {
            "content": "基于本周期数据，线索来源以 公开课 为主（占比 50.0%）。研判后高意向客群占比 50.0%。当前客群画像：以活动引流和转介绍为主要获客方式，高意向客户特征集中在研判结果为\"高意向\"的群体。建议后续补充客户行业、规模、预算等维度数据，进一步提升画像精准度。",
            "heading": "客群特征与画像提炼",
            "metrics": []
          },
          {
            "content": "建议建立线索分级机制，优先跟进高意向线索；定期复盘研判转化漏斗，定位各环节流失原因；将活动报名客户纳入专项跟进序列，提升活动线索转化率；建立流失预警模型，对长期无互动线索自动标记并推送挽回策略；按月/周输出客户经营健康度看板，支撑全链路决策闭环。",
            "heading": "全链路经营建议",
            "metrics": []
          }
        ],
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "lead_trend": {
            "label": "上升",
            "delta_pct": 100.0
          },
          "prev_period": {
            "leads": 1,
            "events": 0,
            "analysis": 0,
            "date_end": "2026-06-01",
            "date_start": "2026-05-26"
          },
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
          "analysis_records": 2,
          "event_registrations": 2,
          "churn_stage_breakdown": {},
          "lead_source_breakdown": {
            "公开课": 1,
            "转介绍": 1
          },
          "lead_status_breakdown": {
            "new": 1,
            "following": 1
          },
          "churn_source_breakdown": {},
          "analysis_result_breakdown": {
            "high": 1,
            "medium": 1
          },
          "event_registration_breakdown": {
            "attended": 1,
            "registered": 1
          }
        },
        "source_refs": [
          "数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
          "对活动报名客户建立 48 小时回访机制，推动转化",
          "建立线索分级标准，按意向度匹配跟进强度",
          "每周复盘流失线索共性特征，沉淀流失预防 SOP",
          "将高意向客户纳入重点跟进看板，确保闭环管理"
        ]
      },
      "source_draft_id": 184,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/129/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "5028",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 129,
      "report_no": "RP-20260611104206-24322e6c",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "本周期零成交，线索到签约的转化链路存在阻断，需紧急排查瓶颈环节"
        ],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条，完成客户研判 2 条，活动报名 2 人次。线索研判覆盖率 100.0%，暂无已成交客户。",
        "sections": [
          {
            "content": "本周期新增客户线索 2 条。线索来源渠道分布：公开课(1条)、转介绍(1条)。线索当前所处阶段：new(1条)、following(1条)。建议对比上周同期数据判断各渠道线索质量变化趋势，对高量低质渠道做定向优化。",
            "heading": "意向客户 - 线索获取与渠道分布",
            "metrics": [
              {
                "name": "新增线索",
                "value": 2
              },
              {
                "name": "渠道-公开课",
                "value": 1
              },
              {
                "name": "渠道-转介绍",
                "value": 1
              }
            ]
          },
          {
            "content": "完成客户研判 2 条，研判覆盖率 100.0%。研判等级分布：high(1条)、medium(1条)。高意向客户 1 条，是近期转化重点跟进对象。研判覆盖率正常。 从\"线索\"到\"研判\"的转化漏斗目前为 2 → 2。",
            "heading": "意向客户 - 研判转化漏斗",
            "metrics": [
              {
                "name": "研判数",
                "value": 2
              },
              {
                "name": "研判覆盖率",
                "value": "100.0%"
              },
              {
                "name": "研判-high",
                "value": 1
              },
              {
                "name": "研判-medium",
                "value": 1
              }
            ]
          },
          {
            "content": "本周期成交客户 0 单，线索到成交转化率 0.0%。从研判分布来看，high(1条)、medium(1条)，高意向客户是成交主力来源。研判等级为高意向的客户应纳入优先跟进序列，加速转化。暂无成交客户，建议复盘从研判到签约环节的转化障碍",
            "heading": "成交客户 - 转化路径与高价值特征",
            "metrics": [
              {
                "name": "成交客户数",
                "value": 0
              },
              {
                "name": "线索→成交转化率",
                "value": "0.0%"
              }
            ]
          },
          {
            "content": "活动报名总计 2 人次，其中已报名 1 人次、已转化 0 人次。活动报名客户是潜在高意向客群，建议建立活动客户专项跟进池，将活动报名 → 研判 → 签约的转化链打通。",
            "heading": "活动参与与转化跟踪",
            "metrics": [
              {
                "name": "活动报名总人次",
                "value": 2
              },
              {
                "name": "活动-attended",
                "value": 1
              },
              {
                "name": "活动-registered",
                "value": 1
              }
            ]
          },
          {
            "content": "本周期流失线索 0 条，占线索总量的 0.0%。当前处于\"废弃/已关单\"状态的线索 0 条，暂无流失线索，客户留存状况良好。",
            "heading": "流失客户 - 归因分析与预警",
            "metrics": [
              {
                "name": "流失线索数",
                "value": 0
              },
              {
                "name": "流失占比",
                "value": "0.0%"
              }
            ]
          },
          {
            "content": "基于本周期数据，线索来源以 公开课 为主（占比 50.0%）。研判后高意向客群占比 50.0%。当前客群画像：以活动引流和转介绍为主要获客方式，高意向客户特征集中在研判结果为\"高意向\"的群体。建议后续补充客户行业、规模、预算等维度数据，进一步提升画像精准度。",
            "heading": "客群特征与画像提炼",
            "metrics": []
          },
          {
            "content": "建议建立线索分级机制，优先跟进高意向线索；定期复盘研判转化漏斗，定位各环节流失原因；将活动报名客户纳入专项跟进序列，提升活动线索转化率；建立流失预警模型，对长期无互动线索自动标记并推送挽回策略；按月/周输出客户经营健康度看板，支撑全链路决策闭环。",
            "heading": "全链路经营建议",
            "metrics": []
          }
        ],
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "lead_trend": {
            "label": "上升",
            "delta_pct": 100.0
          },
          "prev_period": {
            "leads": 1,
            "events": 0,
            "analysis": 0,
            "date_end": "2026-06-01",
            "date_start": "2026-05-26"
          },
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
          "analysis_records": 2,
          "event_registrations": 2,
          "churn_stage_breakdown": {},
          "lead_source_breakdown": {
            "公开课": 1,
            "转介绍": 1
          },
          "lead_status_breakdown": {
            "new": 1,
            "following": 1
          },
          "churn_source_breakdown": {},
          "analysis_result_breakdown": {
            "high": 1,
            "medium": 1
          },
          "event_registration_breakdown": {
            "attended": 1,
            "registered": 1
          }
        },
        "source_refs": [
          "数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
          "对活动报名客户建立 48 小时回访机制，推动转化",
          "建立线索分级标准，按意向度匹配跟进强度",
          "每周复盘流失线索共性特征，沉淀流失预防 SOP",
          "将高意向客户纳入重点跟进看板，确保闭环管理"
        ]
      },
      "source_draft_id": 184,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:06"
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/129/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 255,
      "report_id": 129,
      "export_type": "word",
      "file_name": "RP-20260611104206-24322e6c.docx",
      "file_path": "storage\\reports\\RP-20260611104206-24322e6c.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/255/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104206-24322e6c.docx\"",
    "content-length": "38390"
  },
  "binary": {
    "size_bytes": 38390,
    "sha256": "1296686cb9b4d3faa37d6699167deb25589f430639f707cb5a5ffa1e7183c702",
    "first_16_bytes_hex": "504b03041400000008004355cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/129/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 256,
      "report_id": 129,
      "export_type": "pdf",
      "file_name": "RP-20260611104206-24322e6c.pdf",
      "file_path": "storage\\reports\\RP-20260611104206-24322e6c.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/256/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104206-24322e6c.pdf\"",
    "content-length": "7105"
  },
  "binary": {
    "size_bytes": 7105,
    "sha256": "d9450769324e8694c3454db8720b691615d8e8cc4bf130a41c05da25cc2e46a1",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 员工日报汇总报告（日） - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_daily_summary",
    "date_start": "2026-06-02",
    "date_end": "2026-06-02",
    "department_id": 10,
    "trace_id": "mock-employee_daily_summary",
    "conversation_id": "mock-employee_daily_summary-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "1286",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "employee_daily_summary",
        "date_start": "2026-06-02",
        "date_end": "2026-06-02",
        "department_id": 10,
        "total_reports": 2,
        "status_counts": {
          "archived": 1,
          "draft": 1
        },
        "submitted_reports": 0,
        "draft_reports": 1,
        "archived_reports": 1,
        "risk_reports": 1,
        "tomorrow_plan_reports": 1,
        "key_progress_items": [
          {
            "emp": "Full Employee A",
            "text": "输出客户研判建议。"
          }
        ],
        "risk_items": [
          {
            "emp": "Full Employee A",
            "text": "一名客户预算不确定。"
          }
        ],
        "submission_rate": "40.0%",
        "employee_submission_list": [
          {
            "employee_name": "Full Employee A",
            "report_status": "submitted",
            "risks": "部分客户预算未确认。",
            "tomorrow_plan": "继续跟进预算信息。"
          },
          {
            "employee_name": "Full Employee A",
            "report_status": "archived",
            "risks": "一名客户预算不确定。",
            "tomorrow_plan": "安排深度咨询。"
          },
          {
            "employee_name": "Full Employee A",
            "report_status": "submitted",
            "risks": "不应统计",
            "tomorrow_plan": null
          },
          {
            "employee_name": "Full Employee B",
            "report_status": "submitted",
            "risks": null,
            "tomorrow_plan": "回访家长满意度。"
          },
          {
            "employee_name": "Full Employee B",
            "report_status": "draft",
            "risks": null,
            "tomorrow_plan": null
          }
        ]
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "mock-employee_daily_summary"
  }
}
```

### 员工日报汇总报告（日） - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_daily_summary",
    "date_start": "2026-06-02",
    "date_end": "2026-06-02",
    "department_id": 10,
    "trace_id": "mock-employee_daily_summary"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2981",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 185,
      "draft_no": "DR-20260611104206-020c2341",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "日报提交率 0.0%，2 份未提交，工作透明度存在风险"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日共汇总日报 2 份，已提交 0 份（提交率 0.0%），草稿 1 份，归档 1 份。存在风险摘要的日报占比偏高，需重点关注",
        "sections": [
          {
            "content": "本日日报提交率 0.0%，其中已提交 0 份、草稿 1 份、已归档 1 份。存在未提交或草稿状态的日报，建议了解原因并推动补交",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "总日报数",
                "value": 2
              },
              {
                "name": "已提交",
                "value": 0
              },
              {
                "name": "草稿",
                "value": 1
              },
              {
                "name": "已归档",
                "value": 1
              }
            ]
          },
          {
            "content": "含风险摘要的日报 1 份，填报明日计划 1 份。风险摘要集中出现，建议汇总分析风险类型并制定应对方案",
            "heading": "工作进展与潜在风险",
            "metrics": [
              {
                "name": "风险摘要日报",
                "value": 1
              },
              {
                "name": "明日计划日报",
                "value": 1
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
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "risk_items": [
            {
              "emp": "Full Employee A",
              "text": "一名客户预算不确定。"
            }
          ],
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "submission_rate": "40.0%",
          "archived_reports": 1,
          "submitted_reports": 0,
          "key_progress_items": [
            {
              "emp": "Full Employee A",
              "text": "输出客户研判建议。"
            }
          ],
          "tomorrow_plan_reports": 1,
          "employee_submission_list": [
            {
              "risks": "部分客户预算未确认。",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": "继续跟进预算信息。"
            },
            {
              "risks": "一名客户预算不确定。",
              "employee_name": "Full Employee A",
              "report_status": "archived",
              "tomorrow_plan": "安排深度咨询。"
            },
            {
              "risks": "不应统计",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": null
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "submitted",
              "tomorrow_plan": "回访家长满意度。"
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "draft",
              "tomorrow_plan": null
            }
          ]
        },
        "source_refs": [
          "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-02"
        ],
        "recommendations": [
          "建立日报提交截止时间提醒，确保当日日清日结",
          "对风险摘要日报进行集中分析，制定应对方案",
          "将明日计划填报纳入日报考核标准"
        ]
      },
      "trace_id": "mock-employee_daily_summary"
    },
    "trace_id": "mock-employee_daily_summary"
  }
}
```

### 员工日报汇总报告（日） - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/185/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3150",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 130,
      "report_no": "RP-20260611104206-dbfbfd21",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "日报提交率 0.0%，2 份未提交，工作透明度存在风险"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日共汇总日报 2 份，已提交 0 份（提交率 0.0%），草稿 1 份，归档 1 份。存在风险摘要的日报占比偏高，需重点关注",
        "sections": [
          {
            "content": "本日日报提交率 0.0%，其中已提交 0 份、草稿 1 份、已归档 1 份。存在未提交或草稿状态的日报，建议了解原因并推动补交",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "总日报数",
                "value": 2
              },
              {
                "name": "已提交",
                "value": 0
              },
              {
                "name": "草稿",
                "value": 1
              },
              {
                "name": "已归档",
                "value": 1
              }
            ]
          },
          {
            "content": "含风险摘要的日报 1 份，填报明日计划 1 份。风险摘要集中出现，建议汇总分析风险类型并制定应对方案",
            "heading": "工作进展与潜在风险",
            "metrics": [
              {
                "name": "风险摘要日报",
                "value": 1
              },
              {
                "name": "明日计划日报",
                "value": 1
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
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "risk_items": [
            {
              "emp": "Full Employee A",
              "text": "一名客户预算不确定。"
            }
          ],
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "submission_rate": "40.0%",
          "archived_reports": 1,
          "submitted_reports": 0,
          "key_progress_items": [
            {
              "emp": "Full Employee A",
              "text": "输出客户研判建议。"
            }
          ],
          "tomorrow_plan_reports": 1,
          "employee_submission_list": [
            {
              "risks": "部分客户预算未确认。",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": "继续跟进预算信息。"
            },
            {
              "risks": "一名客户预算不确定。",
              "employee_name": "Full Employee A",
              "report_status": "archived",
              "tomorrow_plan": "安排深度咨询。"
            },
            {
              "risks": "不应统计",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": null
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "submitted",
              "tomorrow_plan": "回访家长满意度。"
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "draft",
              "tomorrow_plan": null
            }
          ]
        },
        "source_refs": [
          "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-02"
        ],
        "recommendations": [
          "建立日报提交截止时间提醒，确保当日日清日结",
          "对风险摘要日报进行集中分析，制定应对方案",
          "将明日计划填报纳入日报考核标准"
        ]
      },
      "source_draft_id": 185,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/130/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3166",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 130,
      "report_no": "RP-20260611104206-dbfbfd21",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "published",
      "content_json": {
        "risks": [
          "日报提交率 0.0%，2 份未提交，工作透明度存在风险"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日共汇总日报 2 份，已提交 0 份（提交率 0.0%），草稿 1 份，归档 1 份。存在风险摘要的日报占比偏高，需重点关注",
        "sections": [
          {
            "content": "本日日报提交率 0.0%，其中已提交 0 份、草稿 1 份、已归档 1 份。存在未提交或草稿状态的日报，建议了解原因并推动补交",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "总日报数",
                "value": 2
              },
              {
                "name": "已提交",
                "value": 0
              },
              {
                "name": "草稿",
                "value": 1
              },
              {
                "name": "已归档",
                "value": 1
              }
            ]
          },
          {
            "content": "含风险摘要的日报 1 份，填报明日计划 1 份。风险摘要集中出现，建议汇总分析风险类型并制定应对方案",
            "heading": "工作进展与潜在风险",
            "metrics": [
              {
                "name": "风险摘要日报",
                "value": 1
              },
              {
                "name": "明日计划日报",
                "value": 1
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
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "risk_items": [
            {
              "emp": "Full Employee A",
              "text": "一名客户预算不确定。"
            }
          ],
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "submission_rate": "40.0%",
          "archived_reports": 1,
          "submitted_reports": 0,
          "key_progress_items": [
            {
              "emp": "Full Employee A",
              "text": "输出客户研判建议。"
            }
          ],
          "tomorrow_plan_reports": 1,
          "employee_submission_list": [
            {
              "risks": "部分客户预算未确认。",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": "继续跟进预算信息。"
            },
            {
              "risks": "一名客户预算不确定。",
              "employee_name": "Full Employee A",
              "report_status": "archived",
              "tomorrow_plan": "安排深度咨询。"
            },
            {
              "risks": "不应统计",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": null
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "submitted",
              "tomorrow_plan": "回访家长满意度。"
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "draft",
              "tomorrow_plan": null
            }
          ]
        },
        "source_refs": [
          "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-02"
        ],
        "recommendations": [
          "建立日报提交截止时间提醒，确保当日日清日结",
          "对风险摘要日报进行集中分析，制定应对方案",
          "将明日计划填报纳入日报考核标准"
        ]
      },
      "source_draft_id": 185,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:07"
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/130/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 257,
      "report_id": 130,
      "export_type": "word",
      "file_name": "RP-20260611104206-dbfbfd21.docx",
      "file_path": "storage\\reports\\RP-20260611104206-dbfbfd21.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/257/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104206-dbfbfd21.docx\"",
    "content-length": "37398"
  },
  "binary": {
    "size_bytes": 37398,
    "sha256": "ea592f3ddf0dbc5e939f070a5c844a8a63d41245f8db95bdd3104324252f5db2",
    "first_16_bytes_hex": "504b03041400000008004355cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/130/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 258,
      "report_id": 130,
      "export_type": "pdf",
      "file_name": "RP-20260611104206-dbfbfd21.pdf",
      "file_path": "storage\\reports\\RP-20260611104206-dbfbfd21.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/258/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104206-dbfbfd21.pdf\"",
    "content-length": "4948"
  },
  "binary": {
    "size_bytes": 4948,
    "sha256": "e2e9729fa4f7d444d1d65155bca46466309025ad5eb51852d4e09f0583da9783",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 员工日报汇总报告（周） - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_weekly_summary",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "mock-employee_weekly_summary",
    "conversation_id": "mock-employee_weekly_summary-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "570",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "employee_weekly_summary",
        "date_start": "2026-06-01",
        "date_end": "2026-06-07",
        "department_id": 10,
        "total_reports": 4,
        "distinct_employees": 2,
        "status_counts": {
          "submitted": 2,
          "archived": 1,
          "draft": 1
        },
        "daily_trend": {
          "2026-06-01": 2,
          "2026-06-02": 2
        },
        "risk_reports": 2,
        "week_submission_rate": "100.0%",
        "top_risk_themes": [],
        "peak_submission_day": "2026-06-01",
        "valley_submission_day": "2026-06-01"
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "mock-employee_weekly_summary"
  }
}
```

### 员工日报汇总报告（周） - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_weekly_summary",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "mock-employee_weekly_summary"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2527",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 186,
      "draft_no": "DR-20260611104206-e42fab1b",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "日报覆盖率偏低（2 人提交），部分员工工作情况不可见"
        ],
        "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共汇总日报 4 份，涉及 2 名员工。日报覆盖率偏低，需关注未提交员工份。含风险摘要日报占比偏高",
        "sections": [
          {
            "content": "本周共 2 人提交日报，总量 4 份。逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。",
            "heading": "周度提交趋势",
            "metrics": [
              {
                "name": "总日报数",
                "value": 4
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
              }
            ]
          },
          {
            "content": "含风险摘要日报 2 份（占比 50.0%）。风险摘要占比较高，建议汇总分析风险类型分布",
            "heading": "工作质量与风险观察",
            "metrics": [
              {
                "name": "风险摘要日报",
                "value": 2
              },
              {
                "name": "风险摘要占比",
                "value": "50.0%"
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
            "2026-06-02": 2
          },
          "report_type": "employee_weekly_summary",
          "risk_reports": 2,
          "department_id": 10,
          "status_counts": {
            "draft": 1,
            "archived": 1,
            "submitted": 2
          },
          "total_reports": 4,
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
      "trace_id": "mock-employee_weekly_summary"
    },
    "trace_id": "mock-employee_weekly_summary"
  }
}
```

### 员工日报汇总报告（周） - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/186/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2710",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 131,
      "report_no": "RP-20260611104206-859a544a",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "日报覆盖率偏低（2 人提交），部分员工工作情况不可见"
        ],
        "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共汇总日报 4 份，涉及 2 名员工。日报覆盖率偏低，需关注未提交员工份。含风险摘要日报占比偏高",
        "sections": [
          {
            "content": "本周共 2 人提交日报，总量 4 份。逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。",
            "heading": "周度提交趋势",
            "metrics": [
              {
                "name": "总日报数",
                "value": 4
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
              }
            ]
          },
          {
            "content": "含风险摘要日报 2 份（占比 50.0%）。风险摘要占比较高，建议汇总分析风险类型分布",
            "heading": "工作质量与风险观察",
            "metrics": [
              {
                "name": "风险摘要日报",
                "value": 2
              },
              {
                "name": "风险摘要占比",
                "value": "50.0%"
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
            "2026-06-02": 2
          },
          "report_type": "employee_weekly_summary",
          "risk_reports": 2,
          "department_id": 10,
          "status_counts": {
            "draft": 1,
            "archived": 1,
            "submitted": 2
          },
          "total_reports": 4,
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
      "source_draft_id": 186,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/131/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2726",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 131,
      "report_no": "RP-20260611104206-859a544a",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "日报覆盖率偏低（2 人提交），部分员工工作情况不可见"
        ],
        "title": "员工日报汇总报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共汇总日报 4 份，涉及 2 名员工。日报覆盖率偏低，需关注未提交员工份。含风险摘要日报占比偏高",
        "sections": [
          {
            "content": "本周共 2 人提交日报，总量 4 份。逐日提交量如下。建议观察提交量是否存在工作日前后波动，分析提交规律。",
            "heading": "周度提交趋势",
            "metrics": [
              {
                "name": "总日报数",
                "value": 4
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
              }
            ]
          },
          {
            "content": "含风险摘要日报 2 份（占比 50.0%）。风险摘要占比较高，建议汇总分析风险类型分布",
            "heading": "工作质量与风险观察",
            "metrics": [
              {
                "name": "风险摘要日报",
                "value": 2
              },
              {
                "name": "风险摘要占比",
                "value": "50.0%"
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
            "2026-06-02": 2
          },
          "report_type": "employee_weekly_summary",
          "risk_reports": 2,
          "department_id": 10,
          "status_counts": {
            "draft": 1,
            "archived": 1,
            "submitted": 2
          },
          "total_reports": 4,
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
      "source_draft_id": 186,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:07"
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/131/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 259,
      "report_id": 131,
      "export_type": "word",
      "file_name": "RP-20260611104206-859a544a.docx",
      "file_path": "storage\\reports\\RP-20260611104206-859a544a.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/259/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104206-859a544a.docx\"",
    "content-length": "37558"
  },
  "binary": {
    "size_bytes": 37558,
    "sha256": "8e50e602e06d2569744895014f2018f79349e18d0f265a3a747c9b309845873f",
    "first_16_bytes_hex": "504b03041400000008004355cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/131/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 260,
      "report_id": 131,
      "export_type": "pdf",
      "file_name": "RP-20260611104206-859a544a.pdf",
      "file_path": "storage\\reports\\RP-20260611104206-859a544a.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/260/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104206-859a544a.pdf\"",
    "content-length": "5222"
  },
  "binary": {
    "size_bytes": 5222,
    "sha256": "bdbc25733bf506991163c8d385dcb3bc3cfb5e307a10223aaf74d0bd90c1990e",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 学生心理健康周报 - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "student_psych_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "mock-student_psych_weekly",
    "conversation_id": "mock-student_psych_weekly-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "526",
    "content-type": "application/json"
  },
  "json": {
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
          "high": 1,
          "low": 1
        },
        "emotion_tag_counts": {
          "焦虑": 1,
          "稳定": 1
        },
        "average_emotion_score": 59.0,
        "total_alerts": 2,
        "alert_status_counts": {
          "pending": 1,
          "resolved": 1
        },
        "alert_risk_level_counts": {
          "high": 1,
          "medium": 1
        }
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "mock-student_psych_weekly"
  }
}
```

### 学生心理健康周报 - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "student_psych_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "mock-student_psych_weekly"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2870",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 187,
      "draft_no": "DR-20260611104207-9175fa6f",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在 1 名高风险学生需紧急干预",
          "整体平均情绪分 59.0，低于健康阈值",
          "尚有 1 条预警待处理"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周纳入心理画像 2 份，平均情绪分 59.0，触发预警 2 条。整体心理健康处于关注区间，需介入高风险个案",
        "sections": [
          {
            "content": "本周共 2 名学生完成心理画像评估，整体平均情绪分 59.0。平均情绪分偏低，需关注学生群体的整体心理健康趋势建议结合留学周期（当前处于学期中段，课业压力可能上升）进行综合研判。",
            "heading": "整体心理态势",
            "metrics": [
              {
                "name": "心理画像数",
                "value": 2
              },
              {
                "name": "平均情绪分",
                "value": "59.0 (满分 100)"
              }
            ]
          },
          {
            "content": "高风险管理：1 人，中等风险：0 人，低风险：1 人。存在高风险学生，建议立即启动深度访谈和心理干预方案",
            "heading": "风险分层分析",
            "metrics": [
              {
                "name": "高风险",
                "value": 1
              },
              {
                "name": "中风险",
                "value": 0
              },
              {
                "name": "低风险",
                "value": 1
              }
            ]
          },
          {
            "content": "本周主要情绪标签分布：焦虑(1)、稳定(1)。焦虑标签占比突出，可能与近期考试或学业压力相关",
            "heading": "情绪标签与趋势",
            "metrics": [
              {
                "name": "焦虑",
                "value": 1
              },
              {
                "name": "稳定",
                "value": 1
              }
            ]
          },
          {
            "content": "预警总量 2 条，已处理 1 条，待处理 1 条。存在未处理预警，需立即跟进高风险学生建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。",
            "heading": "预警处理与关怀建议",
            "metrics": [
              {
                "name": "预警总量",
                "value": 2
              },
              {
                "name": "已处理",
                "value": 1
              },
              {
                "name": "待处理",
                "value": 1
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
            "high": 1
          },
          "emotion_tag_counts": {
            "焦虑": 1,
            "稳定": 1
          },
          "alert_status_counts": {
            "pending": 1,
            "resolved": 1
          },
          "average_emotion_score": 59.0,
          "alert_risk_level_counts": {
            "high": 1,
            "medium": 1
          }
        },
        "source_refs": [
          "数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "对高风险学生启动 48 小时内深度访谈",
          "组织本学期中段心理健康主题分享活动",
          "建立心理健康预警回访机制，确保干预闭环",
          "针对焦虑标签突出的学生，协调学业支持资源"
        ]
      },
      "trace_id": "mock-student_psych_weekly"
    },
    "trace_id": "mock-student_psych_weekly"
  }
}
```

### 学生心理健康周报 - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/187/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3056",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 132,
      "report_no": "RP-20260611104207-594f5d33",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在 1 名高风险学生需紧急干预",
          "整体平均情绪分 59.0，低于健康阈值",
          "尚有 1 条预警待处理"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周纳入心理画像 2 份，平均情绪分 59.0，触发预警 2 条。整体心理健康处于关注区间，需介入高风险个案",
        "sections": [
          {
            "content": "本周共 2 名学生完成心理画像评估，整体平均情绪分 59.0。平均情绪分偏低，需关注学生群体的整体心理健康趋势建议结合留学周期（当前处于学期中段，课业压力可能上升）进行综合研判。",
            "heading": "整体心理态势",
            "metrics": [
              {
                "name": "心理画像数",
                "value": 2
              },
              {
                "name": "平均情绪分",
                "value": "59.0 (满分 100)"
              }
            ]
          },
          {
            "content": "高风险管理：1 人，中等风险：0 人，低风险：1 人。存在高风险学生，建议立即启动深度访谈和心理干预方案",
            "heading": "风险分层分析",
            "metrics": [
              {
                "name": "高风险",
                "value": 1
              },
              {
                "name": "中风险",
                "value": 0
              },
              {
                "name": "低风险",
                "value": 1
              }
            ]
          },
          {
            "content": "本周主要情绪标签分布：焦虑(1)、稳定(1)。焦虑标签占比突出，可能与近期考试或学业压力相关",
            "heading": "情绪标签与趋势",
            "metrics": [
              {
                "name": "焦虑",
                "value": 1
              },
              {
                "name": "稳定",
                "value": 1
              }
            ]
          },
          {
            "content": "预警总量 2 条，已处理 1 条，待处理 1 条。存在未处理预警，需立即跟进高风险学生建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。",
            "heading": "预警处理与关怀建议",
            "metrics": [
              {
                "name": "预警总量",
                "value": 2
              },
              {
                "name": "已处理",
                "value": 1
              },
              {
                "name": "待处理",
                "value": 1
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
            "high": 1
          },
          "emotion_tag_counts": {
            "焦虑": 1,
            "稳定": 1
          },
          "alert_status_counts": {
            "pending": 1,
            "resolved": 1
          },
          "average_emotion_score": 59.0,
          "alert_risk_level_counts": {
            "high": 1,
            "medium": 1
          }
        },
        "source_refs": [
          "数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "对高风险学生启动 48 小时内深度访谈",
          "组织本学期中段心理健康主题分享活动",
          "建立心理健康预警回访机制，确保干预闭环",
          "针对焦虑标签突出的学生，协调学业支持资源"
        ]
      },
      "source_draft_id": 187,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/132/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3072",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 132,
      "report_no": "RP-20260611104207-594f5d33",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "存在 1 名高风险学生需紧急干预",
          "整体平均情绪分 59.0，低于健康阈值",
          "尚有 1 条预警待处理"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周纳入心理画像 2 份，平均情绪分 59.0，触发预警 2 条。整体心理健康处于关注区间，需介入高风险个案",
        "sections": [
          {
            "content": "本周共 2 名学生完成心理画像评估，整体平均情绪分 59.0。平均情绪分偏低，需关注学生群体的整体心理健康趋势建议结合留学周期（当前处于学期中段，课业压力可能上升）进行综合研判。",
            "heading": "整体心理态势",
            "metrics": [
              {
                "name": "心理画像数",
                "value": 2
              },
              {
                "name": "平均情绪分",
                "value": "59.0 (满分 100)"
              }
            ]
          },
          {
            "content": "高风险管理：1 人，中等风险：0 人，低风险：1 人。存在高风险学生，建议立即启动深度访谈和心理干预方案",
            "heading": "风险分层分析",
            "metrics": [
              {
                "name": "高风险",
                "value": 1
              },
              {
                "name": "中风险",
                "value": 0
              },
              {
                "name": "低风险",
                "value": 1
              }
            ]
          },
          {
            "content": "本周主要情绪标签分布：焦虑(1)、稳定(1)。焦虑标签占比突出，可能与近期考试或学业压力相关",
            "heading": "情绪标签与趋势",
            "metrics": [
              {
                "name": "焦虑",
                "value": 1
              },
              {
                "name": "稳定",
                "value": 1
              }
            ]
          },
          {
            "content": "预警总量 2 条，已处理 1 条，待处理 1 条。存在未处理预警，需立即跟进高风险学生建议针对高风险学生，安排一对一心理咨询或导师面谈；定期组织留学适应分享活动；建立心理健康预警回访机制。",
            "heading": "预警处理与关怀建议",
            "metrics": [
              {
                "name": "预警总量",
                "value": 2
              },
              {
                "name": "已处理",
                "value": 1
              },
              {
                "name": "待处理",
                "value": 1
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
            "high": 1
          },
          "emotion_tag_counts": {
            "焦虑": 1,
            "稳定": 1
          },
          "alert_status_counts": {
            "pending": 1,
            "resolved": 1
          },
          "average_emotion_score": 59.0,
          "alert_risk_level_counts": {
            "high": 1,
            "medium": 1
          }
        },
        "source_refs": [
          "数据来源：student_psych_profile 心理画像表、student_psych_alert 心理预警表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "对高风险学生启动 48 小时内深度访谈",
          "组织本学期中段心理健康主题分享活动",
          "建立心理健康预警回访机制，确保干预闭环",
          "针对焦虑标签突出的学生，协调学业支持资源"
        ]
      },
      "source_draft_id": 187,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:07"
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/132/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 261,
      "report_id": 132,
      "export_type": "word",
      "file_name": "RP-20260611104207-594f5d33.docx",
      "file_path": "storage\\reports\\RP-20260611104207-594f5d33.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/261/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104207-594f5d33.docx\"",
    "content-length": "37687"
  },
  "binary": {
    "size_bytes": 37687,
    "sha256": "978b76b0ba1e69fe0bc3ff2b17b81981f889612e82e27e928ee333a3546b6ed0",
    "first_16_bytes_hex": "504b03041400000008004355cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/132/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 262,
      "report_id": 132,
      "export_type": "pdf",
      "file_name": "RP-20260611104207-594f5d33.pdf",
      "file_path": "storage\\reports\\RP-20260611104207-594f5d33.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/262/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104207-594f5d33.pdf\"",
    "content-length": "5736"
  },
  "binary": {
    "size_bytes": 5736,
    "sha256": "d44ed981fbc00747a395722e2c96e4d360f04069e8d082600580d0e71e849128",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

## 权限与安全补充场景


### 学生访问报告生成接口应被拒绝

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "105",
    "X-User-Role": "student",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "acceptance-mock-complaint-weekly"
  }
}
```
响应：
```json
{
  "status_code": 403,
  "headers": {
    "content-length": "46",
    "content-type": "application/json"
  },
  "json": {
    "detail": "当前角色无权访问该接口"
  }
}
```

### 员工发布不存在报告应被拒绝

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/99999999/publish",
  "headers": {
    "X-User-Id": "102",
    "X-User-Role": "employee",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 403,
  "headers": {
    "content-length": "46",
    "content-type": "application/json"
  },
  "json": {
    "detail": "当前角色无权访问该接口"
  }
}
```

### AI Tools Secret 错误应被拒绝

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "acceptance-mock-complaint-weekly",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 401,
  "headers": {
    "content-length": "40",
    "content-type": "application/json"
  },
  "json": {
    "detail": "AI Tools 调用密钥无效"
  }
}
```

### 数据库落表统计

```json
{
  "ai_draft": 187,
  "ai_report": 132,
  "report_export_record": 262,
  "audit_log": 975,
  "ai_tool_call_log": 203
}
```

### 阶段结论

- 结果：通过


## real-dify 阶段

- 执行时间：`2026-06-11 10:42:11`
- 后端地址：`http://127.0.0.1:18000`
- 数据库：`mysql+pymysql://127.0.0.1:3306/education_service_ai_test`
- AI Tools Secret：`已配置`


### 投诉处理周报 - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "real-dify-complaint_weekly",
    "conversation_id": "real-dify-complaint_weekly-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "471",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "complaint_weekly",
        "date_start": "2026-06-01",
        "date_end": "2026-06-07",
        "department_id": 10,
        "total_tickets": 3,
        "status_counts": {
          "pending": 1,
          "processing": 1,
          "resolved": 1
        },
        "category_counts": {
          "教学": 1,
          "服务": 1,
          "签证": 1
        },
        "ticket_type_counts": {
          "complaint": 3
        },
        "avg_processing_hours": 29.8
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "real-dify-complaint_weekly"
  }
}
```

### 投诉处理周报 - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "real-dify-complaint_weekly"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2436",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 188,
      "draft_no": "DR-20260611104227-270c2570",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "仍有1件工单处于待处理状态，可能影响客户满意度",
          "平均处理时长29.8小时，接近或超过部门目标值，存在积压风险"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共受理投诉工单3件，涉及教学、服务、签证三类；平均处理时长29.8小时，截至周末，待处理、处理中、已解决各1件。",
        "sections": [
          {
            "content": "本周部门10累计受理投诉工单3件，均为投诉类型。从处理状态看，待处理工单1件，处理中1件，已解决1件，解决率33.3%。平均处理时长为29.8小时，高于常规水平，需关注处理效率。",
            "heading": "工单总体情况",
            "metrics": [
              {
                "name": "总工单数",
                "value": "3"
              },
              {
                "name": "平均处理时长（小时）",
                "value": "29.8"
              }
            ]
          },
          {
            "content": "按投诉类别统计：教学类1件、服务类1件、签证类1件，各占三分之一。三类工单均有待处理或处理中状态，需分类跟进。",
            "heading": "工单分类详情",
            "metrics": [
              {
                "name": "待处理工单数",
                "value": "1"
              },
              {
                "name": "处理中工单数",
                "value": "1"
              },
              {
                "name": "已解决工单数",
                "value": "1"
              },
              {
                "name": "教学类工单数",
                "value": "1"
              },
              {
                "name": "服务类工单数",
                "value": "1"
              },
              {
                "name": "签证类工单数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "complaint_weekly",
        "source_data": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "report_type": "complaint_weekly",
          "department_id": 10,
          "status_counts": {
            "pending": 1,
            "resolved": 1,
            "processing": 1
          },
          "total_tickets": 3,
          "category_counts": {
            "教学": 1,
            "服务": 1,
            "签证": 1
          },
          "ticket_type_counts": {
            "complaint": 3
          },
          "avg_processing_hours": 29.8
        },
        "source_refs": [
          "数据来源：query_report_source_data 工具，基于投诉工单业务表（complaints），口径：统计日期2026-06-01至2026-06-07，部门ID=10"
        ],
        "recommendations": [
          "优先处理待处理工单，明确责任人和完成时限",
          "分析平均处理时长偏长的原因，优化工单流转环节",
          "加强跨部门协作，确保教学、服务、签证类投诉均能快速响应"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "trace_id": "real-dify-complaint_weekly"
    },
    "trace_id": "real-dify-complaint_weekly"
  }
}
```

### 投诉处理周报 - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/188/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2608",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 133,
      "report_no": "RP-20260611104227-7a749768",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "仍有1件工单处于待处理状态，可能影响客户满意度",
          "平均处理时长29.8小时，接近或超过部门目标值，存在积压风险"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共受理投诉工单3件，涉及教学、服务、签证三类；平均处理时长29.8小时，截至周末，待处理、处理中、已解决各1件。",
        "sections": [
          {
            "content": "本周部门10累计受理投诉工单3件，均为投诉类型。从处理状态看，待处理工单1件，处理中1件，已解决1件，解决率33.3%。平均处理时长为29.8小时，高于常规水平，需关注处理效率。",
            "heading": "工单总体情况",
            "metrics": [
              {
                "name": "总工单数",
                "value": "3"
              },
              {
                "name": "平均处理时长（小时）",
                "value": "29.8"
              }
            ]
          },
          {
            "content": "按投诉类别统计：教学类1件、服务类1件、签证类1件，各占三分之一。三类工单均有待处理或处理中状态，需分类跟进。",
            "heading": "工单分类详情",
            "metrics": [
              {
                "name": "待处理工单数",
                "value": "1"
              },
              {
                "name": "处理中工单数",
                "value": "1"
              },
              {
                "name": "已解决工单数",
                "value": "1"
              },
              {
                "name": "教学类工单数",
                "value": "1"
              },
              {
                "name": "服务类工单数",
                "value": "1"
              },
              {
                "name": "签证类工单数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "complaint_weekly",
        "source_data": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "report_type": "complaint_weekly",
          "department_id": 10,
          "status_counts": {
            "pending": 1,
            "resolved": 1,
            "processing": 1
          },
          "total_tickets": 3,
          "category_counts": {
            "教学": 1,
            "服务": 1,
            "签证": 1
          },
          "ticket_type_counts": {
            "complaint": 3
          },
          "avg_processing_hours": 29.8
        },
        "source_refs": [
          "数据来源：query_report_source_data 工具，基于投诉工单业务表（complaints），口径：统计日期2026-06-01至2026-06-07，部门ID=10"
        ],
        "recommendations": [
          "优先处理待处理工单，明确责任人和完成时限",
          "分析平均处理时长偏长的原因，优化工单流转环节",
          "加强跨部门协作，确保教学、服务、签证类投诉均能快速响应"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 188,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/133/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2624",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 133,
      "report_no": "RP-20260611104227-7a749768",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "仍有1件工单处于待处理状态，可能影响客户满意度",
          "平均处理时长29.8小时，接近或超过部门目标值，存在积压风险"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共受理投诉工单3件，涉及教学、服务、签证三类；平均处理时长29.8小时，截至周末，待处理、处理中、已解决各1件。",
        "sections": [
          {
            "content": "本周部门10累计受理投诉工单3件，均为投诉类型。从处理状态看，待处理工单1件，处理中1件，已解决1件，解决率33.3%。平均处理时长为29.8小时，高于常规水平，需关注处理效率。",
            "heading": "工单总体情况",
            "metrics": [
              {
                "name": "总工单数",
                "value": "3"
              },
              {
                "name": "平均处理时长（小时）",
                "value": "29.8"
              }
            ]
          },
          {
            "content": "按投诉类别统计：教学类1件、服务类1件、签证类1件，各占三分之一。三类工单均有待处理或处理中状态，需分类跟进。",
            "heading": "工单分类详情",
            "metrics": [
              {
                "name": "待处理工单数",
                "value": "1"
              },
              {
                "name": "处理中工单数",
                "value": "1"
              },
              {
                "name": "已解决工单数",
                "value": "1"
              },
              {
                "name": "教学类工单数",
                "value": "1"
              },
              {
                "name": "服务类工单数",
                "value": "1"
              },
              {
                "name": "签证类工单数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "complaint_weekly",
        "source_data": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "report_type": "complaint_weekly",
          "department_id": 10,
          "status_counts": {
            "pending": 1,
            "resolved": 1,
            "processing": 1
          },
          "total_tickets": 3,
          "category_counts": {
            "教学": 1,
            "服务": 1,
            "签证": 1
          },
          "ticket_type_counts": {
            "complaint": 3
          },
          "avg_processing_hours": 29.8
        },
        "source_refs": [
          "数据来源：query_report_source_data 工具，基于投诉工单业务表（complaints），口径：统计日期2026-06-01至2026-06-07，部门ID=10"
        ],
        "recommendations": [
          "优先处理待处理工单，明确责任人和完成时限",
          "分析平均处理时长偏长的原因，优化工单流转环节",
          "加强跨部门协作，确保教学、服务、签证类投诉均能快速响应"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 188,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:28"
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/133/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 263,
      "report_id": 133,
      "export_type": "word",
      "file_name": "RP-20260611104227-7a749768.docx",
      "file_path": "storage\\reports\\RP-20260611104227-7a749768.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/263/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104227-7a749768.docx\"",
    "content-length": "37482"
  },
  "binary": {
    "size_bytes": 37482,
    "sha256": "5285644dc03c43cc2c4f436b07dca61f05c6fe4ff7f279e9fb0e7557fdbe39ec",
    "first_16_bytes_hex": "504b03041400000008004d55cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/133/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 264,
      "report_id": 133,
      "export_type": "pdf",
      "file_name": "RP-20260611104227-7a749768.pdf",
      "file_path": "storage\\reports\\RP-20260611104227-7a749768.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 投诉处理周报 - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/264/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104227-7a749768.pdf\"",
    "content-length": "4994"
  },
  "binary": {
    "size_bytes": 4994,
    "sha256": "28bd3d3e7af734b32dfd9c92bdde02806e0c0742a30b1dd74e8211262a86f3e2",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 客户经营分析报告 - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "customer_operation",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "owner_user_id": 102,
    "trace_id": "real-dify-customer_operation",
    "conversation_id": "real-dify-customer_operation-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "778",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "customer_operation",
        "date_start": "2026-06-01",
        "date_end": "2026-06-07",
        "department_id": 10,
        "owner_user_id": 102,
        "new_leads": 2,
        "analysis_records": 2,
        "event_registrations": 2,
        "lead_source_breakdown": {
          "公开课": 1,
          "转介绍": 1
        },
        "lead_status_breakdown": {
          "new": 1,
          "following": 1
        },
        "analysis_result_breakdown": {
          "high": 1,
          "medium": 1
        },
        "event_registration_breakdown": {
          "attended": 1,
          "registered": 1
        },
        "prev_period": {
          "date_start": "2026-05-26",
          "date_end": "2026-06-01",
          "leads": 1,
          "analysis": 0,
          "events": 0
        },
        "lead_trend": {
          "delta_pct": 100.0,
          "label": "上升"
        },
        "churn_source_breakdown": {},
        "churn_stage_breakdown": {}
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "real-dify-customer_operation"
  }
}
```

### 客户经营分析报告 - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "customer_operation",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "owner_user_id": 102,
    "trace_id": "real-dify-customer_operation"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2880",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 189,
      "draft_no": "DR-20260611104240-9749b532",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本周流失来源和流失阶段数据均为空，尚未记录客户流失信息，建议建立流失监控机制。"
        ],
        "title": "6月第一周客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周新线索2条，环比上升100%；完成客户分析2次，活动参与2次，经营活跃度较上周明显提升。",
        "sections": [
          {
            "content": "本周新增线索2条，全部来源于公开课和转介绍各1条。线索状态分布为：新线索1条，跟进中1条。与上一周期（5月最后一周，1条线索）相比，线索数量增长100%。",
            "heading": "线索获取情况",
            "metrics": [
              {
                "name": "新线索数",
                "value": "2"
              },
              {
                "name": "线索趋势变化百分比",
                "value": "100.0%"
              },
              {
                "name": "线索趋势标签",
                "value": "上升"
              },
              {
                "name": "公开课来源线索数",
                "value": "1"
              },
              {
                "name": "转介绍来源线索数",
                "value": "1"
              },
              {
                "name": "新线索状态数",
                "value": "1"
              },
              {
                "name": "跟进中线索状态数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周完成客户分析记录2次，其中高意向1次、中等意向1次。活动注册2次，实际参加1次，注册未参加1次。上一周期无分析与活动记录，本周实现了从无到有的突破。",
            "heading": "客户分析与活动转化",
            "metrics": [
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "高意向分析数",
                "value": "1"
              },
              {
                "name": "中等意向分析数",
                "value": "1"
              },
              {
                "name": "活动注册数",
                "value": "2"
              },
              {
                "name": "实际参加活动数",
                "value": "1"
              },
              {
                "name": "注册未参加活动数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "lead_trend": {
            "label": "上升",
            "delta_pct": 100.0
          },
          "prev_period": {
            "leads": 1,
            "events": 0,
            "analysis": 0,
            "date_end": "2026-06-01",
            "date_start": "2026-05-26"
          },
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
          "analysis_records": 2,
          "event_registrations": 2,
          "churn_stage_breakdown": {},
          "lead_source_breakdown": {
            "公开课": 1,
            "转介绍": 1
          },
          "lead_status_breakdown": {
            "new": 1,
            "following": 1
          },
          "churn_source_breakdown": {},
          "analysis_result_breakdown": {
            "high": 1,
            "medium": 1
          },
          "event_registration_breakdown": {
            "attended": 1,
            "registered": 1
          }
        },
        "source_refs": [
          "数据来源于 query_report_source_data，口径：部门ID=10、负责人ID=102，日期范围2026-06-01至2026-06-07。",
          "对比周期为2026-05-26至2026-06-01。"
        ],
        "recommendations": [
          "建议对跟进中线索加大沟通力度，推动转化为意向客户。",
          "活动参与率50%，可通过回访提高下一轮活动到会率。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "trace_id": "real-dify-customer_operation"
    },
    "trace_id": "real-dify-customer_operation"
  }
}
```

### 客户经营分析报告 - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/189/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3069",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 134,
      "report_no": "RP-20260611104240-00fd7d92",
      "report_type": "customer_operation",
      "title": "6月第一周客户经营分析报告（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本周流失来源和流失阶段数据均为空，尚未记录客户流失信息，建议建立流失监控机制。"
        ],
        "title": "6月第一周客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周新线索2条，环比上升100%；完成客户分析2次，活动参与2次，经营活跃度较上周明显提升。",
        "sections": [
          {
            "content": "本周新增线索2条，全部来源于公开课和转介绍各1条。线索状态分布为：新线索1条，跟进中1条。与上一周期（5月最后一周，1条线索）相比，线索数量增长100%。",
            "heading": "线索获取情况",
            "metrics": [
              {
                "name": "新线索数",
                "value": "2"
              },
              {
                "name": "线索趋势变化百分比",
                "value": "100.0%"
              },
              {
                "name": "线索趋势标签",
                "value": "上升"
              },
              {
                "name": "公开课来源线索数",
                "value": "1"
              },
              {
                "name": "转介绍来源线索数",
                "value": "1"
              },
              {
                "name": "新线索状态数",
                "value": "1"
              },
              {
                "name": "跟进中线索状态数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周完成客户分析记录2次，其中高意向1次、中等意向1次。活动注册2次，实际参加1次，注册未参加1次。上一周期无分析与活动记录，本周实现了从无到有的突破。",
            "heading": "客户分析与活动转化",
            "metrics": [
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "高意向分析数",
                "value": "1"
              },
              {
                "name": "中等意向分析数",
                "value": "1"
              },
              {
                "name": "活动注册数",
                "value": "2"
              },
              {
                "name": "实际参加活动数",
                "value": "1"
              },
              {
                "name": "注册未参加活动数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "lead_trend": {
            "label": "上升",
            "delta_pct": 100.0
          },
          "prev_period": {
            "leads": 1,
            "events": 0,
            "analysis": 0,
            "date_end": "2026-06-01",
            "date_start": "2026-05-26"
          },
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
          "analysis_records": 2,
          "event_registrations": 2,
          "churn_stage_breakdown": {},
          "lead_source_breakdown": {
            "公开课": 1,
            "转介绍": 1
          },
          "lead_status_breakdown": {
            "new": 1,
            "following": 1
          },
          "churn_source_breakdown": {},
          "analysis_result_breakdown": {
            "high": 1,
            "medium": 1
          },
          "event_registration_breakdown": {
            "attended": 1,
            "registered": 1
          }
        },
        "source_refs": [
          "数据来源于 query_report_source_data，口径：部门ID=10、负责人ID=102，日期范围2026-06-01至2026-06-07。",
          "对比周期为2026-05-26至2026-06-01。"
        ],
        "recommendations": [
          "建议对跟进中线索加大沟通力度，推动转化为意向客户。",
          "活动参与率50%，可通过回访提高下一轮活动到会率。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 189,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/134/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3085",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 134,
      "report_no": "RP-20260611104240-00fd7d92",
      "report_type": "customer_operation",
      "title": "6月第一周客户经营分析报告（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "本周流失来源和流失阶段数据均为空，尚未记录客户流失信息，建议建立流失监控机制。"
        ],
        "title": "6月第一周客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周新线索2条，环比上升100%；完成客户分析2次，活动参与2次，经营活跃度较上周明显提升。",
        "sections": [
          {
            "content": "本周新增线索2条，全部来源于公开课和转介绍各1条。线索状态分布为：新线索1条，跟进中1条。与上一周期（5月最后一周，1条线索）相比，线索数量增长100%。",
            "heading": "线索获取情况",
            "metrics": [
              {
                "name": "新线索数",
                "value": "2"
              },
              {
                "name": "线索趋势变化百分比",
                "value": "100.0%"
              },
              {
                "name": "线索趋势标签",
                "value": "上升"
              },
              {
                "name": "公开课来源线索数",
                "value": "1"
              },
              {
                "name": "转介绍来源线索数",
                "value": "1"
              },
              {
                "name": "新线索状态数",
                "value": "1"
              },
              {
                "name": "跟进中线索状态数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周完成客户分析记录2次，其中高意向1次、中等意向1次。活动注册2次，实际参加1次，注册未参加1次。上一周期无分析与活动记录，本周实现了从无到有的突破。",
            "heading": "客户分析与活动转化",
            "metrics": [
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "高意向分析数",
                "value": "1"
              },
              {
                "name": "中等意向分析数",
                "value": "1"
              },
              {
                "name": "活动注册数",
                "value": "2"
              },
              {
                "name": "实际参加活动数",
                "value": "1"
              },
              {
                "name": "注册未参加活动数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "lead_trend": {
            "label": "上升",
            "delta_pct": 100.0
          },
          "prev_period": {
            "leads": 1,
            "events": 0,
            "analysis": 0,
            "date_end": "2026-06-01",
            "date_start": "2026-05-26"
          },
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
          "analysis_records": 2,
          "event_registrations": 2,
          "churn_stage_breakdown": {},
          "lead_source_breakdown": {
            "公开课": 1,
            "转介绍": 1
          },
          "lead_status_breakdown": {
            "new": 1,
            "following": 1
          },
          "churn_source_breakdown": {},
          "analysis_result_breakdown": {
            "high": 1,
            "medium": 1
          },
          "event_registration_breakdown": {
            "attended": 1,
            "registered": 1
          }
        },
        "source_refs": [
          "数据来源于 query_report_source_data，口径：部门ID=10、负责人ID=102，日期范围2026-06-01至2026-06-07。",
          "对比周期为2026-05-26至2026-06-01。"
        ],
        "recommendations": [
          "建议对跟进中线索加大沟通力度，推动转化为意向客户。",
          "活动参与率50%，可通过回访提高下一轮活动到会率。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 189,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:40"
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/134/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 265,
      "report_id": 134,
      "export_type": "word",
      "file_name": "RP-20260611104240-00fd7d92.docx",
      "file_path": "storage\\reports\\RP-20260611104240-00fd7d92.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/265/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104240-00fd7d92.docx\"",
    "content-length": "37517"
  },
  "binary": {
    "size_bytes": 37517,
    "sha256": "b8336119031c4ed31c1bbcbc54b8ce9191df27ff463ce5f9c35c5589c1fde43a",
    "first_16_bytes_hex": "504b03041400000008005455cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/134/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 266,
      "report_id": 134,
      "export_type": "pdf",
      "file_name": "RP-20260611104240-00fd7d92.pdf",
      "file_path": "storage\\reports\\RP-20260611104240-00fd7d92.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 客户经营分析报告 - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/266/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104240-00fd7d92.pdf\"",
    "content-length": "5061"
  },
  "binary": {
    "size_bytes": 5061,
    "sha256": "3a43952d4905d3bdef6bdadd3bbd580b00e17b165462641a82287e22bd2ff081",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 员工日报汇总报告（日） - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_daily_summary",
    "date_start": "2026-06-02",
    "date_end": "2026-06-02",
    "department_id": 10,
    "trace_id": "real-dify-employee_daily_summary",
    "conversation_id": "real-dify-employee_daily_summary-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "1291",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "employee_daily_summary",
        "date_start": "2026-06-02",
        "date_end": "2026-06-02",
        "department_id": 10,
        "total_reports": 2,
        "status_counts": {
          "archived": 1,
          "draft": 1
        },
        "submitted_reports": 0,
        "draft_reports": 1,
        "archived_reports": 1,
        "risk_reports": 1,
        "tomorrow_plan_reports": 1,
        "key_progress_items": [
          {
            "emp": "Full Employee A",
            "text": "输出客户研判建议。"
          }
        ],
        "risk_items": [
          {
            "emp": "Full Employee A",
            "text": "一名客户预算不确定。"
          }
        ],
        "submission_rate": "40.0%",
        "employee_submission_list": [
          {
            "employee_name": "Full Employee A",
            "report_status": "submitted",
            "risks": "部分客户预算未确认。",
            "tomorrow_plan": "继续跟进预算信息。"
          },
          {
            "employee_name": "Full Employee A",
            "report_status": "archived",
            "risks": "一名客户预算不确定。",
            "tomorrow_plan": "安排深度咨询。"
          },
          {
            "employee_name": "Full Employee A",
            "report_status": "submitted",
            "risks": "不应统计",
            "tomorrow_plan": null
          },
          {
            "employee_name": "Full Employee B",
            "report_status": "submitted",
            "risks": null,
            "tomorrow_plan": "回访家长满意度。"
          },
          {
            "employee_name": "Full Employee B",
            "report_status": "draft",
            "risks": null,
            "tomorrow_plan": null
          }
        ]
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "real-dify-employee_daily_summary"
  }
}
```

### 员工日报汇总报告（日） - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_daily_summary",
    "date_start": "2026-06-02",
    "date_end": "2026-06-02",
    "department_id": 10,
    "trace_id": "real-dify-employee_daily_summary"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3424",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 190,
      "draft_no": "DR-20260611104257-1d1b3978",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "Full Employee A报告一名客户预算不确定，需关注后续跟进；Full Employee A另一条报告反映部分客户预算未确认。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "部门10在2026年6月2日共有2份日报记录，提交率为40.0%，其中包含1个风险报告和1个明日计划报告。",
        "sections": [
          {
            "content": "本日共统计2份员工日报，其中已归档1份，草稿1份。提交率为40.0%。已提交报告0份，草稿报告1份，已归档报告1份。",
            "heading": "整体提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "2"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "已归档报告数",
                "value": "1"
              },
              {
                "name": "草稿报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "关键工作进展：Full Employee A报告了“输出客户研判建议”。风险报告：Full Employee A提及“一名客户预算不确定”。另外，有1份报告包含了明日计划。",
            "heading": "工作进展与风险",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              },
              {
                "name": "关键进展项数",
                "value": "1"
              },
              {
                "name": "风险项数",
                "value": "1"
              }
            ]
          },
          {
            "content": "Full Employee A共提交3条记录：1条已归档（风险：一名客户预算不确定，明日计划：安排深度咨询），2条已提交（其中一条风险：部分客户预算未确认，明日计划：继续跟进预算信息；另一条风险：不应统计，无明日计划）。Full Employee B共提交2条记录：1条已提交（无风险，明日计划：回访家长满意度），1条草稿（无风险，无明日计划）。",
            "heading": "员工提交明细",
            "metrics": []
          }
        ],
        "tool_error": "",
        "report_type": "employee_daily_summary",
        "source_data": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "risk_items": [
            {
              "emp": "Full Employee A",
              "text": "一名客户预算不确定。"
            }
          ],
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "submission_rate": "40.0%",
          "archived_reports": 1,
          "submitted_reports": 0,
          "key_progress_items": [
            {
              "emp": "Full Employee A",
              "text": "输出客户研判建议。"
            }
          ],
          "tomorrow_plan_reports": 1,
          "employee_submission_list": [
            {
              "risks": "部分客户预算未确认。",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": "继续跟进预算信息。"
            },
            {
              "risks": "一名客户预算不确定。",
              "employee_name": "Full Employee A",
              "report_status": "archived",
              "tomorrow_plan": "安排深度咨询。"
            },
            {
              "risks": "不应统计",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": null
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "submitted",
              "tomorrow_plan": "回访家长满意度。"
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "draft",
              "tomorrow_plan": null
            }
          ]
        },
        "source_refs": [
          "query_report_source_data",
          "数据表：employee_daily_summary，日期2026-06-02，部门ID10"
        ],
        "recommendations": [
          "建议跟进风险报告中客户预算问题，督促相关人员完善明日计划。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "trace_id": "real-dify-employee_daily_summary"
    },
    "trace_id": "real-dify-employee_daily_summary"
  }
}
```

### 员工日报汇总报告（日） - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/190/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3583",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 135,
      "report_no": "RP-20260611104257-a30e5a3b",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "Full Employee A报告一名客户预算不确定，需关注后续跟进；Full Employee A另一条报告反映部分客户预算未确认。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "部门10在2026年6月2日共有2份日报记录，提交率为40.0%，其中包含1个风险报告和1个明日计划报告。",
        "sections": [
          {
            "content": "本日共统计2份员工日报，其中已归档1份，草稿1份。提交率为40.0%。已提交报告0份，草稿报告1份，已归档报告1份。",
            "heading": "整体提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "2"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "已归档报告数",
                "value": "1"
              },
              {
                "name": "草稿报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "关键工作进展：Full Employee A报告了“输出客户研判建议”。风险报告：Full Employee A提及“一名客户预算不确定”。另外，有1份报告包含了明日计划。",
            "heading": "工作进展与风险",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              },
              {
                "name": "关键进展项数",
                "value": "1"
              },
              {
                "name": "风险项数",
                "value": "1"
              }
            ]
          },
          {
            "content": "Full Employee A共提交3条记录：1条已归档（风险：一名客户预算不确定，明日计划：安排深度咨询），2条已提交（其中一条风险：部分客户预算未确认，明日计划：继续跟进预算信息；另一条风险：不应统计，无明日计划）。Full Employee B共提交2条记录：1条已提交（无风险，明日计划：回访家长满意度），1条草稿（无风险，无明日计划）。",
            "heading": "员工提交明细",
            "metrics": []
          }
        ],
        "tool_error": "",
        "report_type": "employee_daily_summary",
        "source_data": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "risk_items": [
            {
              "emp": "Full Employee A",
              "text": "一名客户预算不确定。"
            }
          ],
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "submission_rate": "40.0%",
          "archived_reports": 1,
          "submitted_reports": 0,
          "key_progress_items": [
            {
              "emp": "Full Employee A",
              "text": "输出客户研判建议。"
            }
          ],
          "tomorrow_plan_reports": 1,
          "employee_submission_list": [
            {
              "risks": "部分客户预算未确认。",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": "继续跟进预算信息。"
            },
            {
              "risks": "一名客户预算不确定。",
              "employee_name": "Full Employee A",
              "report_status": "archived",
              "tomorrow_plan": "安排深度咨询。"
            },
            {
              "risks": "不应统计",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": null
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "submitted",
              "tomorrow_plan": "回访家长满意度。"
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "draft",
              "tomorrow_plan": null
            }
          ]
        },
        "source_refs": [
          "query_report_source_data",
          "数据表：employee_daily_summary，日期2026-06-02，部门ID10"
        ],
        "recommendations": [
          "建议跟进风险报告中客户预算问题，督促相关人员完善明日计划。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 190,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/135/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3599",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 135,
      "report_no": "RP-20260611104257-a30e5a3b",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "published",
      "content_json": {
        "risks": [
          "Full Employee A报告一名客户预算不确定，需关注后续跟进；Full Employee A另一条报告反映部分客户预算未确认。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "部门10在2026年6月2日共有2份日报记录，提交率为40.0%，其中包含1个风险报告和1个明日计划报告。",
        "sections": [
          {
            "content": "本日共统计2份员工日报，其中已归档1份，草稿1份。提交率为40.0%。已提交报告0份，草稿报告1份，已归档报告1份。",
            "heading": "整体提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "2"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "已归档报告数",
                "value": "1"
              },
              {
                "name": "草稿报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "关键工作进展：Full Employee A报告了“输出客户研判建议”。风险报告：Full Employee A提及“一名客户预算不确定”。另外，有1份报告包含了明日计划。",
            "heading": "工作进展与风险",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              },
              {
                "name": "关键进展项数",
                "value": "1"
              },
              {
                "name": "风险项数",
                "value": "1"
              }
            ]
          },
          {
            "content": "Full Employee A共提交3条记录：1条已归档（风险：一名客户预算不确定，明日计划：安排深度咨询），2条已提交（其中一条风险：部分客户预算未确认，明日计划：继续跟进预算信息；另一条风险：不应统计，无明日计划）。Full Employee B共提交2条记录：1条已提交（无风险，明日计划：回访家长满意度），1条草稿（无风险，无明日计划）。",
            "heading": "员工提交明细",
            "metrics": []
          }
        ],
        "tool_error": "",
        "report_type": "employee_daily_summary",
        "source_data": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "risk_items": [
            {
              "emp": "Full Employee A",
              "text": "一名客户预算不确定。"
            }
          ],
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "submission_rate": "40.0%",
          "archived_reports": 1,
          "submitted_reports": 0,
          "key_progress_items": [
            {
              "emp": "Full Employee A",
              "text": "输出客户研判建议。"
            }
          ],
          "tomorrow_plan_reports": 1,
          "employee_submission_list": [
            {
              "risks": "部分客户预算未确认。",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": "继续跟进预算信息。"
            },
            {
              "risks": "一名客户预算不确定。",
              "employee_name": "Full Employee A",
              "report_status": "archived",
              "tomorrow_plan": "安排深度咨询。"
            },
            {
              "risks": "不应统计",
              "employee_name": "Full Employee A",
              "report_status": "submitted",
              "tomorrow_plan": null
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "submitted",
              "tomorrow_plan": "回访家长满意度。"
            },
            {
              "risks": null,
              "employee_name": "Full Employee B",
              "report_status": "draft",
              "tomorrow_plan": null
            }
          ]
        },
        "source_refs": [
          "query_report_source_data",
          "数据表：employee_daily_summary，日期2026-06-02，部门ID10"
        ],
        "recommendations": [
          "建议跟进风险报告中客户预算问题，督促相关人员完善明日计划。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 190,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:42:58"
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/135/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 267,
      "report_id": 135,
      "export_type": "word",
      "file_name": "RP-20260611104257-a30e5a3b.docx",
      "file_path": "storage\\reports\\RP-20260611104257-a30e5a3b.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/267/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104257-a30e5a3b.docx\"",
    "content-length": "37472"
  },
  "binary": {
    "size_bytes": 37472,
    "sha256": "bd075dd27edb9b75c710e648470adbe9dbb31eaaefb01411273faf91d1c91bf3",
    "first_16_bytes_hex": "504b03041400000008005d55cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/135/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 268,
      "report_id": 135,
      "export_type": "pdf",
      "file_name": "RP-20260611104257-a30e5a3b.pdf",
      "file_path": "storage\\reports\\RP-20260611104257-a30e5a3b.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（日） - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/268/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104257-a30e5a3b.pdf\"",
    "content-length": "5088"
  },
  "binary": {
    "size_bytes": 5088,
    "sha256": "64325f8f2eb1b4c07d7ea389b8f50c09f57257420ea7506174b7a4a70ad82e70",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 员工日报汇总报告（周） - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_weekly_summary",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "real-dify-employee_weekly_summary",
    "conversation_id": "real-dify-employee_weekly_summary-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "575",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "tool_name": "query_report_source_data",
      "result": {
        "report_type": "employee_weekly_summary",
        "date_start": "2026-06-01",
        "date_end": "2026-06-07",
        "department_id": 10,
        "total_reports": 4,
        "distinct_employees": 2,
        "status_counts": {
          "submitted": 2,
          "archived": 1,
          "draft": 1
        },
        "daily_trend": {
          "2026-06-01": 2,
          "2026-06-02": 2
        },
        "risk_reports": 2,
        "week_submission_rate": "100.0%",
        "top_risk_themes": [],
        "peak_submission_day": "2026-06-01",
        "valley_submission_day": "2026-06-01"
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "real-dify-employee_weekly_summary"
  }
}
```

### 员工日报汇总报告（周） - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "employee_weekly_summary",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "real-dify-employee_weekly_summary"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2654",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 191,
      "draft_no": "DR-20260611104310-cde8fe4f",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "员工日报汇总报告（周）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月1日至6月7日期间，部门10共有2名员工提交了4份日报，周提交率100%，其中已提交2份、已归档1份、草稿1份。本周共标记2份风险报告，但未集中出现特定风险主题。",
        "sections": [
          {
            "content": "本周共收到4份日报，由2名不同员工提交，周提交率达100%。从状态分布看：已提交2份，已归档1份，草稿1份。提交高峰与低谷日均出现在2026年6月1日（当日提交2份），次日6月2日同样提交2份。整体提交节奏集中在前两天，后续无新增提交。",
            "heading": "提交概览",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
              },
              {
                "name": "周提交率",
                "value": "100.0%"
              },
              {
                "name": "已提交",
                "value": "2"
              },
              {
                "name": "已归档",
                "value": "1"
              },
              {
                "name": "草稿",
                "value": "1"
              },
              {
                "name": "提交高峰日",
                "value": "2026-06-01"
              },
              {
                "name": "提交低谷日",
                "value": "2026-06-01"
              }
            ]
          },
          {
            "content": "本周共识别出2份风险报告，但经分析未发现集中的风险主题（top_risk_themes为空）。建议各部门负责人结合具体报告内容确认风险详情，以便采取针对性措施。",
            "heading": "风险情况",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "主要风险主题",
                "value": "无"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "employee_weekly_summary",
        "source_data": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "daily_trend": {
            "2026-06-01": 2,
            "2026-06-02": 2
          },
          "report_type": "employee_weekly_summary",
          "risk_reports": 2,
          "department_id": 10,
          "status_counts": {
            "draft": 1,
            "archived": 1,
            "submitted": 2
          },
          "total_reports": 4,
          "top_risk_themes": [],
          "distinct_employees": 2,
          "peak_submission_day": "2026-06-01",
          "week_submission_rate": "100.0%",
          "valley_submission_day": "2026-06-01"
        },
        "source_refs": [
          "数据来源：query_report_source_data，基于员工日报表统计，数据表：employee_daily_report",
          "口径说明：周提交率 = 实际提交员工数 / 应提交员工数 × 100%；风险报告为员工自行标记或系统自动识别的风险内容。"
        ],
        "recommendations": [
          "请部门负责人查阅2份风险报告的具体内容，及时跟进处理。",
          "考虑提醒员工在每日提交截止前完成草稿状态的报告，确保提交率持续达标。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "trace_id": "real-dify-employee_weekly_summary"
    },
    "trace_id": "real-dify-employee_weekly_summary"
  }
}
```

### 员工日报汇总报告（周） - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/191/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2805",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 136,
      "report_no": "RP-20260611104310-5383eb7f",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周）",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "员工日报汇总报告（周）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月1日至6月7日期间，部门10共有2名员工提交了4份日报，周提交率100%，其中已提交2份、已归档1份、草稿1份。本周共标记2份风险报告，但未集中出现特定风险主题。",
        "sections": [
          {
            "content": "本周共收到4份日报，由2名不同员工提交，周提交率达100%。从状态分布看：已提交2份，已归档1份，草稿1份。提交高峰与低谷日均出现在2026年6月1日（当日提交2份），次日6月2日同样提交2份。整体提交节奏集中在前两天，后续无新增提交。",
            "heading": "提交概览",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
              },
              {
                "name": "周提交率",
                "value": "100.0%"
              },
              {
                "name": "已提交",
                "value": "2"
              },
              {
                "name": "已归档",
                "value": "1"
              },
              {
                "name": "草稿",
                "value": "1"
              },
              {
                "name": "提交高峰日",
                "value": "2026-06-01"
              },
              {
                "name": "提交低谷日",
                "value": "2026-06-01"
              }
            ]
          },
          {
            "content": "本周共识别出2份风险报告，但经分析未发现集中的风险主题（top_risk_themes为空）。建议各部门负责人结合具体报告内容确认风险详情，以便采取针对性措施。",
            "heading": "风险情况",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "主要风险主题",
                "value": "无"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "employee_weekly_summary",
        "source_data": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "daily_trend": {
            "2026-06-01": 2,
            "2026-06-02": 2
          },
          "report_type": "employee_weekly_summary",
          "risk_reports": 2,
          "department_id": 10,
          "status_counts": {
            "draft": 1,
            "archived": 1,
            "submitted": 2
          },
          "total_reports": 4,
          "top_risk_themes": [],
          "distinct_employees": 2,
          "peak_submission_day": "2026-06-01",
          "week_submission_rate": "100.0%",
          "valley_submission_day": "2026-06-01"
        },
        "source_refs": [
          "数据来源：query_report_source_data，基于员工日报表统计，数据表：employee_daily_report",
          "口径说明：周提交率 = 实际提交员工数 / 应提交员工数 × 100%；风险报告为员工自行标记或系统自动识别的风险内容。"
        ],
        "recommendations": [
          "请部门负责人查阅2份风险报告的具体内容，及时跟进处理。",
          "考虑提醒员工在每日提交截止前完成草稿状态的报告，确保提交率持续达标。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 191,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/136/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2821",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 136,
      "report_no": "RP-20260611104310-5383eb7f",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周）",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "员工日报汇总报告（周）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月1日至6月7日期间，部门10共有2名员工提交了4份日报，周提交率100%，其中已提交2份、已归档1份、草稿1份。本周共标记2份风险报告，但未集中出现特定风险主题。",
        "sections": [
          {
            "content": "本周共收到4份日报，由2名不同员工提交，周提交率达100%。从状态分布看：已提交2份，已归档1份，草稿1份。提交高峰与低谷日均出现在2026年6月1日（当日提交2份），次日6月2日同样提交2份。整体提交节奏集中在前两天，后续无新增提交。",
            "heading": "提交概览",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
              },
              {
                "name": "周提交率",
                "value": "100.0%"
              },
              {
                "name": "已提交",
                "value": "2"
              },
              {
                "name": "已归档",
                "value": "1"
              },
              {
                "name": "草稿",
                "value": "1"
              },
              {
                "name": "提交高峰日",
                "value": "2026-06-01"
              },
              {
                "name": "提交低谷日",
                "value": "2026-06-01"
              }
            ]
          },
          {
            "content": "本周共识别出2份风险报告，但经分析未发现集中的风险主题（top_risk_themes为空）。建议各部门负责人结合具体报告内容确认风险详情，以便采取针对性措施。",
            "heading": "风险情况",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "主要风险主题",
                "value": "无"
              }
            ]
          }
        ],
        "tool_error": "",
        "report_type": "employee_weekly_summary",
        "source_data": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "daily_trend": {
            "2026-06-01": 2,
            "2026-06-02": 2
          },
          "report_type": "employee_weekly_summary",
          "risk_reports": 2,
          "department_id": 10,
          "status_counts": {
            "draft": 1,
            "archived": 1,
            "submitted": 2
          },
          "total_reports": 4,
          "top_risk_themes": [],
          "distinct_employees": 2,
          "peak_submission_day": "2026-06-01",
          "week_submission_rate": "100.0%",
          "valley_submission_day": "2026-06-01"
        },
        "source_refs": [
          "数据来源：query_report_source_data，基于员工日报表统计，数据表：employee_daily_report",
          "口径说明：周提交率 = 实际提交员工数 / 应提交员工数 × 100%；风险报告为员工自行标记或系统自动识别的风险内容。"
        ],
        "recommendations": [
          "请部门负责人查阅2份风险报告的具体内容，及时跟进处理。",
          "考虑提醒员工在每日提交截止前完成草稿状态的报告，确保提交率持续达标。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 191,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:43:10"
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/136/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 269,
      "report_id": 136,
      "export_type": "word",
      "file_name": "RP-20260611104310-5383eb7f.docx",
      "file_path": "storage\\reports\\RP-20260611104310-5383eb7f.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/269/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104310-5383eb7f.docx\"",
    "content-length": "37563"
  },
  "binary": {
    "size_bytes": 37563,
    "sha256": "155b08444bc0a800f907209fcdfa0f53380984143b6db34fbe1cd379d7f7a4ed",
    "first_16_bytes_hex": "504b03041400000008006555cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/136/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 270,
      "report_id": 136,
      "export_type": "pdf",
      "file_name": "RP-20260611104310-5383eb7f.pdf",
      "file_path": "storage\\reports\\RP-20260611104310-5383eb7f.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 员工日报汇总报告（周） - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/270/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104310-5383eb7f.pdf\"",
    "content-length": "4767"
  },
  "binary": {
    "size_bytes": 4767,
    "sha256": "6975439add669ded440da8bb799cf9125a2df5b01e2a6c8f85295b2dfd0e55a1",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

### 学生心理健康周报 - AI Tool 聚合数据

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "student_psych_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "real-dify-student_psych_weekly",
    "conversation_id": "real-dify-student_psych_weekly-conversation",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "531",
    "content-type": "application/json"
  },
  "json": {
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
          "high": 1,
          "low": 1
        },
        "emotion_tag_counts": {
          "焦虑": 1,
          "稳定": 1
        },
        "average_emotion_score": 59.0,
        "total_alerts": 2,
        "alert_status_counts": {
          "pending": 1,
          "resolved": 1
        },
        "alert_risk_level_counts": {
          "high": 1,
          "medium": 1
        }
      },
      "draft_id": null,
      "requires_confirmation": false
    },
    "trace_id": "real-dify-student_psych_weekly"
  }
}
```

### 学生心理健康周报 - 生成草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "student_psych_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "real-dify-student_psych_weekly"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2822",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 192,
      "draft_no": "DR-20260611104320-2e57ab8d",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在1名高风险学生，平均情绪评分59.0偏低，且对应1条高等级预警尚未处理，可能产生心理危机。"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共监测学生心理档案2份，其中高风险1人、低风险1人；平均情绪评分为59.0，情绪标签以“焦虑”和“稳定”为主；产生预警2条，其中1条待处理、1条已解决，预警风险等级涵盖高、中两级。整体心理健康状况需重点关注高风险个案。",
        "sections": [
          {
            "content": "本周部门内共维护学生心理档案2份，风险等级分布为高风险1人、低风险1人。情绪标签统计显示，“焦虑”1人、“稳定”1人，平均情绪评分为59.0，处于中等偏低水平。需持续关注高风险学生的情绪状态并提供干预。",
            "heading": "一、整体心理健康概况",
            "metrics": [
              {
                "name": "档案总数",
                "value": "2"
              },
              {
                "name": "高风险人数",
                "value": "1"
              },
              {
                "name": "低风险人数",
                "value": "1"
              },
              {
                "name": "平均情绪评分",
                "value": "59.0"
              }
            ]
          },
          {
            "content": "本周共产生预警2条，按处理状态分：待处理1条、已解决1条；按风险等级分：高预警1条、中预警1条。已解决的预警表明处置流程有效，但仍有一条高等级预警待处理，需尽快安排心理辅导。",
            "heading": "二、预警事件分析",
            "metrics": [
              {
                "name": "预警总数",
                "value": "2"
              },
              {
                "name": "待处理预警",
                "value": "1"
              },
              {
                "name": "已解决预警",
                "value": "1"
              },
              {
                "name": "高等级预警",
                "value": "1"
              },
              {
                "name": "中等级预警",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
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
            "high": 1
          },
          "emotion_tag_counts": {
            "焦虑": 1,
            "稳定": 1
          },
          "alert_status_counts": {
            "pending": 1,
            "resolved": 1
          },
          "average_emotion_score": 59.0,
          "alert_risk_level_counts": {
            "high": 1,
            "medium": 1
          }
        },
        "source_refs": [
          "数据来源于 query_report_source_data 接口，口径基于学生心理档案表（student_psych_profile）及预警事件表（student_psych_alert），部门ID=10，时间范围2026-06-01至2026-06-07。"
        ],
        "recommendations": [
          "立即对高风险学生开展一对一心理评估与干预，尽早处理待处理的高等级预警。",
          "加强日常情绪监测，关注焦虑情绪学生的心理健康状态，必要时增加辅导频次。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "trace_id": "real-dify-student_psych_weekly"
    },
    "trace_id": "real-dify-student_psych_weekly"
  }
}
```

### 学生心理健康周报 - 确认草稿

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/drafts/192/confirm",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "2998",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 137,
      "report_no": "RP-20260611104320-315d059c",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在1名高风险学生，平均情绪评分59.0偏低，且对应1条高等级预警尚未处理，可能产生心理危机。"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共监测学生心理档案2份，其中高风险1人、低风险1人；平均情绪评分为59.0，情绪标签以“焦虑”和“稳定”为主；产生预警2条，其中1条待处理、1条已解决，预警风险等级涵盖高、中两级。整体心理健康状况需重点关注高风险个案。",
        "sections": [
          {
            "content": "本周部门内共维护学生心理档案2份，风险等级分布为高风险1人、低风险1人。情绪标签统计显示，“焦虑”1人、“稳定”1人，平均情绪评分为59.0，处于中等偏低水平。需持续关注高风险学生的情绪状态并提供干预。",
            "heading": "一、整体心理健康概况",
            "metrics": [
              {
                "name": "档案总数",
                "value": "2"
              },
              {
                "name": "高风险人数",
                "value": "1"
              },
              {
                "name": "低风险人数",
                "value": "1"
              },
              {
                "name": "平均情绪评分",
                "value": "59.0"
              }
            ]
          },
          {
            "content": "本周共产生预警2条，按处理状态分：待处理1条、已解决1条；按风险等级分：高预警1条、中预警1条。已解决的预警表明处置流程有效，但仍有一条高等级预警待处理，需尽快安排心理辅导。",
            "heading": "二、预警事件分析",
            "metrics": [
              {
                "name": "预警总数",
                "value": "2"
              },
              {
                "name": "待处理预警",
                "value": "1"
              },
              {
                "name": "已解决预警",
                "value": "1"
              },
              {
                "name": "高等级预警",
                "value": "1"
              },
              {
                "name": "中等级预警",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
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
            "high": 1
          },
          "emotion_tag_counts": {
            "焦虑": 1,
            "稳定": 1
          },
          "alert_status_counts": {
            "pending": 1,
            "resolved": 1
          },
          "average_emotion_score": 59.0,
          "alert_risk_level_counts": {
            "high": 1,
            "medium": 1
          }
        },
        "source_refs": [
          "数据来源于 query_report_source_data 接口，口径基于学生心理档案表（student_psych_profile）及预警事件表（student_psych_alert），部门ID=10，时间范围2026-06-01至2026-06-07。"
        ],
        "recommendations": [
          "立即对高风险学生开展一对一心理评估与干预，尽早处理待处理的高等级预警。",
          "加强日常情绪监测，关注焦虑情绪学生的心理健康状态，必要时增加辅导频次。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 192,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": null,
      "published_time": null
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 发布报告

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/137/publish",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "3014",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 137,
      "report_no": "RP-20260611104320-315d059c",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "存在1名高风险学生，平均情绪评分59.0偏低，且对应1条高等级预警尚未处理，可能产生心理危机。"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共监测学生心理档案2份，其中高风险1人、低风险1人；平均情绪评分为59.0，情绪标签以“焦虑”和“稳定”为主；产生预警2条，其中1条待处理、1条已解决，预警风险等级涵盖高、中两级。整体心理健康状况需重点关注高风险个案。",
        "sections": [
          {
            "content": "本周部门内共维护学生心理档案2份，风险等级分布为高风险1人、低风险1人。情绪标签统计显示，“焦虑”1人、“稳定”1人，平均情绪评分为59.0，处于中等偏低水平。需持续关注高风险学生的情绪状态并提供干预。",
            "heading": "一、整体心理健康概况",
            "metrics": [
              {
                "name": "档案总数",
                "value": "2"
              },
              {
                "name": "高风险人数",
                "value": "1"
              },
              {
                "name": "低风险人数",
                "value": "1"
              },
              {
                "name": "平均情绪评分",
                "value": "59.0"
              }
            ]
          },
          {
            "content": "本周共产生预警2条，按处理状态分：待处理1条、已解决1条；按风险等级分：高预警1条、中预警1条。已解决的预警表明处置流程有效，但仍有一条高等级预警待处理，需尽快安排心理辅导。",
            "heading": "二、预警事件分析",
            "metrics": [
              {
                "name": "预警总数",
                "value": "2"
              },
              {
                "name": "待处理预警",
                "value": "1"
              },
              {
                "name": "已解决预警",
                "value": "1"
              },
              {
                "name": "高等级预警",
                "value": "1"
              },
              {
                "name": "中等级预警",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
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
            "high": 1
          },
          "emotion_tag_counts": {
            "焦虑": 1,
            "稳定": 1
          },
          "alert_status_counts": {
            "pending": 1,
            "resolved": 1
          },
          "average_emotion_score": 59.0,
          "alert_risk_level_counts": {
            "high": 1,
            "medium": 1
          }
        },
        "source_refs": [
          "数据来源于 query_report_source_data 接口，口径基于学生心理档案表（student_psych_profile）及预警事件表（student_psych_alert），部门ID=10，时间范围2026-06-01至2026-06-07。"
        ],
        "recommendations": [
          "立即对高风险学生开展一对一心理评估与干预，尽早处理待处理的高等级预警。",
          "加强日常情绪监测，关注焦虑情绪学生的心理健康状态，必要时增加辅导频次。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 192,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:43:21"
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 导出 WORD

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/137/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "word"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "251",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 271,
      "report_id": 137,
      "export_type": "word",
      "file_name": "RP-20260611104320-315d059c.docx",
      "file_path": "storage\\reports\\RP-20260611104320-315d059c.docx",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 下载 WORD

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/271/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content-disposition": "attachment; filename=\"RP-20260611104320-315d059c.docx\"",
    "content-length": "37613"
  },
  "binary": {
    "size_bytes": 37613,
    "sha256": "a8989731e70c924fefaa4fc9d553b1a2b11403c91a382deee61bfc9d4dab0591",
    "first_16_bytes_hex": "504b03041400000008006a55cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/137/exports",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "export_type": "pdf"
  }
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-length": "248",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 272,
      "report_id": 137,
      "export_type": "pdf",
      "file_name": "RP-20260611104320-315d059c.pdf",
      "file_path": "storage\\reports\\RP-20260611104320-315d059c.pdf",
      "status": "success",
      "error_message": null
    },
    "trace_id": null
  }
}
```

### 学生心理健康周报 - 下载 PDF

请求：
```json
{
  "method": "GET",
  "url": "/api/v1/reports/exports/272/download",
  "headers": {
    "X-User-Id": "101",
    "X-User-Role": "admin",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/pdf",
    "content-disposition": "attachment; filename=\"RP-20260611104320-315d059c.pdf\"",
    "content-length": "5035"
  },
  "binary": {
    "size_bytes": 5035,
    "sha256": "9c9d2516df9740462676ede76552ba001a2f2654becb661333b6307c2fa293c7",
    "first_16_bytes_hex": "255044462d312e340a25938c8b9e2052"
  }
}
```

## 权限与安全补充场景


### 学生访问报告生成接口应被拒绝

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/generate-draft",
  "headers": {
    "X-User-Id": "105",
    "X-User-Role": "student",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "acceptance-mock-complaint-weekly"
  }
}
```
响应：
```json
{
  "status_code": 403,
  "headers": {
    "content-length": "46",
    "content-type": "application/json"
  },
  "json": {
    "detail": "当前角色无权访问该接口"
  }
}
```

### 员工发布不存在报告应被拒绝

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/99999999/publish",
  "headers": {
    "X-User-Id": "102",
    "X-User-Role": "employee",
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": null
}
```
响应：
```json
{
  "status_code": 403,
  "headers": {
    "content-length": "46",
    "content-type": "application/json"
  },
  "json": {
    "detail": "当前角色无权访问该接口"
  }
}
```

### AI Tools Secret 错误应被拒绝

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/ai-tools/query_report_source_data",
  "headers": {
    "X-AI-Tools-Secret": "<configured>"
  },
  "json": {
    "report_type": "complaint_weekly",
    "date_start": "2026-06-01",
    "date_end": "2026-06-07",
    "department_id": 10,
    "trace_id": "acceptance-mock-complaint-weekly",
    "caller": "other"
  }
}
```
响应：
```json
{
  "status_code": 401,
  "headers": {
    "content-length": "40",
    "content-type": "application/json"
  },
  "json": {
    "detail": "AI Tools 调用密钥无效"
  }
}
```

### 数据库落表统计

```json
{
  "ai_draft": 192,
  "ai_report": 137,
  "report_export_record": 272,
  "audit_log": 1010,
  "ai_tool_call_log": 213
}
```

### 阶段结论

- 结果：通过

