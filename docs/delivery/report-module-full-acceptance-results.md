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

- 执行时间：`2026-06-11 10:28:08`
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
      "id": 163,
      "draft_no": "DR-20260611102808-93c7773f",
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
  "url": "/api/v1/reports/drafts/163/confirm",
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
      "id": 108,
      "report_no": "RP-20260611102808-11af4d7f",
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
      "source_draft_id": 163,
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
  "url": "/api/v1/reports/108/publish",
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
      "id": 108,
      "report_no": "RP-20260611102808-11af4d7f",
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
      "source_draft_id": 163,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:09"
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
  "url": "/api/v1/reports/108/exports",
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
      "id": 213,
      "report_id": 108,
      "export_type": "word",
      "file_name": "RP-20260611102808-11af4d7f.docx",
      "file_path": "storage\\reports\\RP-20260611102808-11af4d7f.docx",
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
  "url": "/api/v1/reports/exports/213/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102808-11af4d7f.docx\"",
    "content-length": "37569"
  },
  "binary": {
    "size_bytes": 37569,
    "sha256": "3670634e8f3fda164d2f752244adb69e4bfa4cf9e984571c3f9306854fd7a79a",
    "first_16_bytes_hex": "504b03041400000008008453cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/108/exports",
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
      "id": 214,
      "report_id": 108,
      "export_type": "pdf",
      "file_name": "RP-20260611102808-11af4d7f.pdf",
      "file_path": "storage\\reports\\RP-20260611102808-11af4d7f.pdf",
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
  "url": "/api/v1/reports/exports/214/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102808-11af4d7f.pdf\"",
    "content-length": "5245"
  },
  "binary": {
    "size_bytes": 5245,
    "sha256": "195343c1c4b870f0d2bbb3239bc533b30083c1d743a2381d7e36e2187653ca4f",
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
    "content-length": "568",
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
        }
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
    "content-length": "2379",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 164,
      "draft_no": "DR-20260611102809-0e433f30",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "暂无重大经营风险"
        ],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条，完成客户研判 2 条，活动报名 2 人次。整体获客和转化节奏正常。",
        "sections": [
          {
            "content": "本周期新增客户线索 2 条。建议对比上周同口径数据，判断线索增长趋势和各类渠道的线索质量。",
            "heading": "线索获取概览",
            "metrics": [
              {
                "name": "新增线索",
                "value": 2
              }
            ]
          },
          {
            "content": "完成客户研判 2 条，研判覆盖率 100.0%。研判进度正常，可进一步关注研判质量",
            "heading": "客户研判与转化",
            "metrics": [
              {
                "name": "研判记录",
                "value": 2
              },
              {
                "name": "研判覆盖率",
                "value": "100.0%"
              }
            ]
          },
          {
            "content": "活动报名 2 人次。活动参与客户是潜在高意向群体，建议跟进活动参与后的转化动作，评估活动获客 ROI。",
            "heading": "活动报名参与",
            "metrics": [
              {
                "name": "活动报名人次",
                "value": 2
              }
            ]
          },
          {
            "content": "建议建立线索分级机制，优先跟进高意向线索；定期复盘研判转化漏斗，定位各环节流失原因；将活动报名客户纳入专项跟进序列，提升活动线索转化率。",
            "heading": "经营建议",
            "metrics": []
          }
        ],
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
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
          }
        },
        "source_refs": [
          "数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
          "对活动报名客户建立 48 小时回访机制，推动转化",
          "建立线索分级标准，按意向度匹配跟进强度"
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
  "url": "/api/v1/reports/drafts/164/confirm",
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
    "content-length": "2573",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 109,
      "report_no": "RP-20260611102809-6cb0399a",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "暂无重大经营风险"
        ],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条，完成客户研判 2 条，活动报名 2 人次。整体获客和转化节奏正常。",
        "sections": [
          {
            "content": "本周期新增客户线索 2 条。建议对比上周同口径数据，判断线索增长趋势和各类渠道的线索质量。",
            "heading": "线索获取概览",
            "metrics": [
              {
                "name": "新增线索",
                "value": 2
              }
            ]
          },
          {
            "content": "完成客户研判 2 条，研判覆盖率 100.0%。研判进度正常，可进一步关注研判质量",
            "heading": "客户研判与转化",
            "metrics": [
              {
                "name": "研判记录",
                "value": 2
              },
              {
                "name": "研判覆盖率",
                "value": "100.0%"
              }
            ]
          },
          {
            "content": "活动报名 2 人次。活动参与客户是潜在高意向群体，建议跟进活动参与后的转化动作，评估活动获客 ROI。",
            "heading": "活动报名参与",
            "metrics": [
              {
                "name": "活动报名人次",
                "value": 2
              }
            ]
          },
          {
            "content": "建议建立线索分级机制，优先跟进高意向线索；定期复盘研判转化漏斗，定位各环节流失原因；将活动报名客户纳入专项跟进序列，提升活动线索转化率。",
            "heading": "经营建议",
            "metrics": []
          }
        ],
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
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
          }
        },
        "source_refs": [
          "数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
          "对活动报名客户建立 48 小时回访机制，推动转化",
          "建立线索分级标准，按意向度匹配跟进强度"
        ]
      },
      "source_draft_id": 164,
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
  "url": "/api/v1/reports/109/publish",
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
    "content-length": "2589",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 109,
      "report_no": "RP-20260611102809-6cb0399a",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "暂无重大经营风险"
        ],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条，完成客户研判 2 条，活动报名 2 人次。整体获客和转化节奏正常。",
        "sections": [
          {
            "content": "本周期新增客户线索 2 条。建议对比上周同口径数据，判断线索增长趋势和各类渠道的线索质量。",
            "heading": "线索获取概览",
            "metrics": [
              {
                "name": "新增线索",
                "value": 2
              }
            ]
          },
          {
            "content": "完成客户研判 2 条，研判覆盖率 100.0%。研判进度正常，可进一步关注研判质量",
            "heading": "客户研判与转化",
            "metrics": [
              {
                "name": "研判记录",
                "value": 2
              },
              {
                "name": "研判覆盖率",
                "value": "100.0%"
              }
            ]
          },
          {
            "content": "活动报名 2 人次。活动参与客户是潜在高意向群体，建议跟进活动参与后的转化动作，评估活动获客 ROI。",
            "heading": "活动报名参与",
            "metrics": [
              {
                "name": "活动报名人次",
                "value": 2
              }
            ]
          },
          {
            "content": "建议建立线索分级机制，优先跟进高意向线索；定期复盘研判转化漏斗，定位各环节流失原因；将活动报名客户纳入专项跟进序列，提升活动线索转化率。",
            "heading": "经营建议",
            "metrics": []
          }
        ],
        "report_type": "customer_operation",
        "source_data": {
          "date_end": "2026-06-07",
          "new_leads": 2,
          "date_start": "2026-06-01",
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
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
          }
        },
        "source_refs": [
          "数据来源：crm_lead 线索表、customer_analysis_record 客户研判表、event_registration 活动报名表，统计口径：部门 10，日期 2026-06-01 至 2026-06-07"
        ],
        "recommendations": [
          "优先跟进未研判线索，缩短线索到首次接触的时间窗口",
          "对活动报名客户建立 48 小时回访机制，推动转化",
          "建立线索分级标准，按意向度匹配跟进强度"
        ]
      },
      "source_draft_id": 164,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:09"
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
  "url": "/api/v1/reports/109/exports",
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
      "id": 215,
      "report_id": 109,
      "export_type": "word",
      "file_name": "RP-20260611102809-6cb0399a.docx",
      "file_path": "storage\\reports\\RP-20260611102809-6cb0399a.docx",
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
  "url": "/api/v1/reports/exports/215/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102809-6cb0399a.docx\"",
    "content-length": "37494"
  },
  "binary": {
    "size_bytes": 37494,
    "sha256": "4878111bad48c8a047354e9e3f6129f1dc1e856e62386cca2cf20ebfcf497749",
    "first_16_bytes_hex": "504b03041400000008008453cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/109/exports",
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
      "id": 216,
      "report_id": 109,
      "export_type": "pdf",
      "file_name": "RP-20260611102809-6cb0399a.pdf",
      "file_path": "storage\\reports\\RP-20260611102809-6cb0399a.pdf",
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
  "url": "/api/v1/reports/exports/216/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102809-6cb0399a.pdf\"",
    "content-length": "5166"
  },
  "binary": {
    "size_bytes": 5166,
    "sha256": "e1127f90d9ec9ad429b22d7f3b7aaacffbf1b199751f64f4790c05d7941cbb29",
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
      "id": 165,
      "draft_no": "DR-20260611102809-870f03ec",
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
  "url": "/api/v1/reports/drafts/165/confirm",
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
      "id": 110,
      "report_no": "RP-20260611102809-4ae698cc",
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
      "source_draft_id": 165,
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
  "url": "/api/v1/reports/110/publish",
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
      "id": 110,
      "report_no": "RP-20260611102809-4ae698cc",
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
      "source_draft_id": 165,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:10"
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
  "url": "/api/v1/reports/110/exports",
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
      "id": 217,
      "report_id": 110,
      "export_type": "word",
      "file_name": "RP-20260611102809-4ae698cc.docx",
      "file_path": "storage\\reports\\RP-20260611102809-4ae698cc.docx",
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
  "url": "/api/v1/reports/exports/217/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102809-4ae698cc.docx\"",
    "content-length": "37398"
  },
  "binary": {
    "size_bytes": 37398,
    "sha256": "6acfa718cc27777dc26827803ce0d04a35abae66e31083b920ea51a918b1d6ff",
    "first_16_bytes_hex": "504b03041400000008008453cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/110/exports",
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
      "id": 218,
      "report_id": 110,
      "export_type": "pdf",
      "file_name": "RP-20260611102809-4ae698cc.pdf",
      "file_path": "storage\\reports\\RP-20260611102809-4ae698cc.pdf",
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
  "url": "/api/v1/reports/exports/218/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102809-4ae698cc.pdf\"",
    "content-length": "4948"
  },
  "binary": {
    "size_bytes": 4948,
    "sha256": "1aa0e804bc71ee013e3f626f20e9cd66da8b440e2fff2c180cc37a1ed5752629",
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
      "id": 166,
      "draft_no": "DR-20260611102809-012e1cdc",
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
  "url": "/api/v1/reports/drafts/166/confirm",
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
      "id": 111,
      "report_no": "RP-20260611102809-d7e5bdf3",
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
      "source_draft_id": 166,
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
  "url": "/api/v1/reports/111/publish",
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
      "id": 111,
      "report_no": "RP-20260611102809-d7e5bdf3",
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
      "source_draft_id": 166,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:10"
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
  "url": "/api/v1/reports/111/exports",
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
      "id": 219,
      "report_id": 111,
      "export_type": "word",
      "file_name": "RP-20260611102809-d7e5bdf3.docx",
      "file_path": "storage\\reports\\RP-20260611102809-d7e5bdf3.docx",
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
  "url": "/api/v1/reports/exports/219/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102809-d7e5bdf3.docx\"",
    "content-length": "37558"
  },
  "binary": {
    "size_bytes": 37558,
    "sha256": "cc214f99254173ec92b6931ce7d9cc7da9d9ec40cfd861a718cff75808c620cc",
    "first_16_bytes_hex": "504b03041400000008008553cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/111/exports",
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
      "id": 220,
      "report_id": 111,
      "export_type": "pdf",
      "file_name": "RP-20260611102809-d7e5bdf3.pdf",
      "file_path": "storage\\reports\\RP-20260611102809-d7e5bdf3.pdf",
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
  "url": "/api/v1/reports/exports/220/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102809-d7e5bdf3.pdf\"",
    "content-length": "5222"
  },
  "binary": {
    "size_bytes": 5222,
    "sha256": "1bc2a827b2bab292c7a1ce336a28b8ed3d7d3a37a57c87db4b750f93258ad157",
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
      "id": 167,
      "draft_no": "DR-20260611102810-43928259",
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
  "url": "/api/v1/reports/drafts/167/confirm",
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
      "id": 112,
      "report_no": "RP-20260611102810-a6820958",
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
      "source_draft_id": 167,
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
  "url": "/api/v1/reports/112/publish",
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
      "id": 112,
      "report_no": "RP-20260611102810-a6820958",
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
      "source_draft_id": 167,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:10"
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
  "url": "/api/v1/reports/112/exports",
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
      "id": 221,
      "report_id": 112,
      "export_type": "word",
      "file_name": "RP-20260611102810-a6820958.docx",
      "file_path": "storage\\reports\\RP-20260611102810-a6820958.docx",
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
  "url": "/api/v1/reports/exports/221/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102810-a6820958.docx\"",
    "content-length": "37687"
  },
  "binary": {
    "size_bytes": 37687,
    "sha256": "1bc10fe40655dfbb3985e855359ee8ec782a9c2cd5c8011d825ee9ce0dbb7d1d",
    "first_16_bytes_hex": "504b03041400000008008553cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/112/exports",
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
      "id": 222,
      "report_id": 112,
      "export_type": "pdf",
      "file_name": "RP-20260611102810-a6820958.pdf",
      "file_path": "storage\\reports\\RP-20260611102810-a6820958.pdf",
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
  "url": "/api/v1/reports/exports/222/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102810-a6820958.pdf\"",
    "content-length": "5736"
  },
  "binary": {
    "size_bytes": 5736,
    "sha256": "db17a1e7d1cfccdf6515d4bc733b637b399659ce9ab60850846b3661768504ea",
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
  "ai_draft": 167,
  "ai_report": 112,
  "report_export_record": 222,
  "audit_log": 835,
  "ai_tool_call_log": 173
}
```

### 阶段结论

- 结果：通过


## real-dify 阶段

- 执行时间：`2026-06-11 10:28:14`
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
    "content-length": "2335",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 168,
      "draft_no": "DR-20260611102827-7e7c217d",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "待处理投诉可能影响客户满意度，需及时跟进。"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共受理3件投诉，涉及教学、服务、签证各1件，平均处理时长为29.8小时。当前处理状态分布均匀，各有1件处于待处理、处理中和已解决。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共接到投诉工单3件，全部为投诉类型。工单处理状态分布：待处理1件、处理中1件、已解决1件。",
            "heading": "投诉总量概览",
            "metrics": [
              {
                "name": "投诉工单总数",
                "value": "3"
              },
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
              }
            ]
          },
          {
            "content": "投诉工单按类别分布：教学类1件、服务类1件、签证类1件。各类别投诉数量相同，需关注不同维度的服务痛点。",
            "heading": "投诉分类分析",
            "metrics": [
              {
                "name": "教学类投诉数",
                "value": "1"
              },
              {
                "name": "服务类投诉数",
                "value": "1"
              },
              {
                "name": "签证类投诉数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周投诉工单平均处理时长为29.8小时。当前仍有1件待处理、1件处理中，处理进度有待加快。",
            "heading": "处理时效与状态",
            "metrics": [
              {
                "name": "平均处理时长（小时）",
                "value": "29.8"
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
          "数据来源：query_report_source_data；投诉工单系统（按部门ID=10过滤），统计周期2026-06-01至2026-06-07。"
        ],
        "recommendations": [
          "优先处理待处理投诉工单，缩短处理周期。",
          "分析各类别投诉根因，制定针对性改进措施。"
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
  "url": "/api/v1/reports/drafts/168/confirm",
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
    "content-length": "2507",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 113,
      "report_no": "RP-20260611102827-63c71a42",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "待处理投诉可能影响客户满意度，需及时跟进。"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共受理3件投诉，涉及教学、服务、签证各1件，平均处理时长为29.8小时。当前处理状态分布均匀，各有1件处于待处理、处理中和已解决。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共接到投诉工单3件，全部为投诉类型。工单处理状态分布：待处理1件、处理中1件、已解决1件。",
            "heading": "投诉总量概览",
            "metrics": [
              {
                "name": "投诉工单总数",
                "value": "3"
              },
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
              }
            ]
          },
          {
            "content": "投诉工单按类别分布：教学类1件、服务类1件、签证类1件。各类别投诉数量相同，需关注不同维度的服务痛点。",
            "heading": "投诉分类分析",
            "metrics": [
              {
                "name": "教学类投诉数",
                "value": "1"
              },
              {
                "name": "服务类投诉数",
                "value": "1"
              },
              {
                "name": "签证类投诉数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周投诉工单平均处理时长为29.8小时。当前仍有1件待处理、1件处理中，处理进度有待加快。",
            "heading": "处理时效与状态",
            "metrics": [
              {
                "name": "平均处理时长（小时）",
                "value": "29.8"
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
          "数据来源：query_report_source_data；投诉工单系统（按部门ID=10过滤），统计周期2026-06-01至2026-06-07。"
        ],
        "recommendations": [
          "优先处理待处理投诉工单，缩短处理周期。",
          "分析各类别投诉根因，制定针对性改进措施。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 168,
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
  "url": "/api/v1/reports/113/publish",
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
    "content-length": "2523",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 113,
      "report_no": "RP-20260611102827-63c71a42",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "待处理投诉可能影响客户满意度，需及时跟进。"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共受理3件投诉，涉及教学、服务、签证各1件，平均处理时长为29.8小时。当前处理状态分布均匀，各有1件处于待处理、处理中和已解决。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共接到投诉工单3件，全部为投诉类型。工单处理状态分布：待处理1件、处理中1件、已解决1件。",
            "heading": "投诉总量概览",
            "metrics": [
              {
                "name": "投诉工单总数",
                "value": "3"
              },
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
              }
            ]
          },
          {
            "content": "投诉工单按类别分布：教学类1件、服务类1件、签证类1件。各类别投诉数量相同，需关注不同维度的服务痛点。",
            "heading": "投诉分类分析",
            "metrics": [
              {
                "name": "教学类投诉数",
                "value": "1"
              },
              {
                "name": "服务类投诉数",
                "value": "1"
              },
              {
                "name": "签证类投诉数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周投诉工单平均处理时长为29.8小时。当前仍有1件待处理、1件处理中，处理进度有待加快。",
            "heading": "处理时效与状态",
            "metrics": [
              {
                "name": "平均处理时长（小时）",
                "value": "29.8"
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
          "数据来源：query_report_source_data；投诉工单系统（按部门ID=10过滤），统计周期2026-06-01至2026-06-07。"
        ],
        "recommendations": [
          "优先处理待处理投诉工单，缩短处理周期。",
          "分析各类别投诉根因，制定针对性改进措施。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 168,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:28"
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
  "url": "/api/v1/reports/113/exports",
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
      "id": 223,
      "report_id": 113,
      "export_type": "word",
      "file_name": "RP-20260611102827-63c71a42.docx",
      "file_path": "storage\\reports\\RP-20260611102827-63c71a42.docx",
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
  "url": "/api/v1/reports/exports/223/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102827-63c71a42.docx\"",
    "content-length": "37381"
  },
  "binary": {
    "size_bytes": 37381,
    "sha256": "bbcc3da6e328b0462d938976045667ef335ffeb0945928e4481bfb54365bb2b8",
    "first_16_bytes_hex": "504b03041400000008008d53cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/113/exports",
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
      "id": 224,
      "report_id": 113,
      "export_type": "pdf",
      "file_name": "RP-20260611102827-63c71a42.pdf",
      "file_path": "storage\\reports\\RP-20260611102827-63c71a42.pdf",
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
  "url": "/api/v1/reports/exports/224/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102827-63c71a42.pdf\"",
    "content-length": "5087"
  },
  "binary": {
    "size_bytes": 5087,
    "sha256": "0bb0192a402c7d7fbe1f45dd8ab14506130f6bedde306532e8635286ca0f6267",
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
    "content-length": "573",
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
        }
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
    "content-length": "2984",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 169,
      "draft_no": "DR-20260611102842-3f231b34",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期（2026-06-01至2026-06-07）部门10、负责人102共新增2条线索，完成2次分析记录，并促成2次活动报名。线索来源以公开课和转介绍为主，线索状态以新线索和跟进中为主，分析结果中高潜与中等各1，活动报名中已参加与已注册各1。",
        "sections": [
          {
            "content": "本周期内，共新增2条线索，完成2次分析记录，活动报名2次。各项核心指标处于平稳状态。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "新增线索数",
                "value": "2"
              },
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "活动报名数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周期线索主要来源于公开课和转介绍，各占比50%。建议关注公开课渠道的持续效果以及转介绍机制的有效性。",
            "heading": "线索来源分布",
            "metrics": [
              {
                "name": "公开课",
                "value": "1"
              },
              {
                "name": "转介绍",
                "value": "1"
              }
            ]
          },
          {
            "content": "新线索与跟进中线索各1条，分布均衡，需及时安排跟进动作以推动转化。",
            "heading": "线索状态分布",
            "metrics": [
              {
                "name": "新线索",
                "value": "1"
              },
              {
                "name": "跟进中",
                "value": "1"
              }
            ]
          },
          {
            "content": "高潜客户与中等潜力客户各1位，需对高潜客户重点跟进，同时挖掘中等客户的提升空间。",
            "heading": "分析结果分布",
            "metrics": [
              {
                "name": "高潜",
                "value": "1"
              },
              {
                "name": "中等",
                "value": "1"
              }
            ]
          },
          {
            "content": "活动报名共2次，其中已参加1次，已注册1次，表明活动参与率较高，后续可继续鼓励注册用户实际到场。",
            "heading": "活动报名情况",
            "metrics": [
              {
                "name": "已参加",
                "value": "1"
              },
              {
                "name": "已注册",
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
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
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
          }
        },
        "source_refs": [
          "query_report_source_data（FastAPI AI Tool）",
          "数据表：客户经营数据表（线索表、分析记录表、活动报名表），口径：按部门10、负责人102、日期2026-06-01至2026-06-07筛选"
        ],
        "recommendations": [
          "建议加强对1条‘跟进中’线索的跟进频率，提升转化率。",
          "针对高潜客户，制定个性化跟进方案。",
          "继续跟踪公开课来源的线索转化效果，评估转介绍激励政策。"
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
  "url": "/api/v1/reports/drafts/169/confirm",
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
      "id": 114,
      "report_no": "RP-20260611102842-e2befc5a",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期（2026-06-01至2026-06-07）部门10、负责人102共新增2条线索，完成2次分析记录，并促成2次活动报名。线索来源以公开课和转介绍为主，线索状态以新线索和跟进中为主，分析结果中高潜与中等各1，活动报名中已参加与已注册各1。",
        "sections": [
          {
            "content": "本周期内，共新增2条线索，完成2次分析记录，活动报名2次。各项核心指标处于平稳状态。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "新增线索数",
                "value": "2"
              },
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "活动报名数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周期线索主要来源于公开课和转介绍，各占比50%。建议关注公开课渠道的持续效果以及转介绍机制的有效性。",
            "heading": "线索来源分布",
            "metrics": [
              {
                "name": "公开课",
                "value": "1"
              },
              {
                "name": "转介绍",
                "value": "1"
              }
            ]
          },
          {
            "content": "新线索与跟进中线索各1条，分布均衡，需及时安排跟进动作以推动转化。",
            "heading": "线索状态分布",
            "metrics": [
              {
                "name": "新线索",
                "value": "1"
              },
              {
                "name": "跟进中",
                "value": "1"
              }
            ]
          },
          {
            "content": "高潜客户与中等潜力客户各1位，需对高潜客户重点跟进，同时挖掘中等客户的提升空间。",
            "heading": "分析结果分布",
            "metrics": [
              {
                "name": "高潜",
                "value": "1"
              },
              {
                "name": "中等",
                "value": "1"
              }
            ]
          },
          {
            "content": "活动报名共2次，其中已参加1次，已注册1次，表明活动参与率较高，后续可继续鼓励注册用户实际到场。",
            "heading": "活动报名情况",
            "metrics": [
              {
                "name": "已参加",
                "value": "1"
              },
              {
                "name": "已注册",
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
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
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
          }
        },
        "source_refs": [
          "query_report_source_data（FastAPI AI Tool）",
          "数据表：客户经营数据表（线索表、分析记录表、活动报名表），口径：按部门10、负责人102、日期2026-06-01至2026-06-07筛选"
        ],
        "recommendations": [
          "建议加强对1条‘跟进中’线索的跟进频率，提升转化率。",
          "针对高潜客户，制定个性化跟进方案。",
          "继续跟踪公开课来源的线索转化效果，评估转介绍激励政策。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 169,
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
  "url": "/api/v1/reports/114/publish",
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
    "content-length": "3182",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 114,
      "report_no": "RP-20260611102842-e2befc5a",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期（2026-06-01至2026-06-07）部门10、负责人102共新增2条线索，完成2次分析记录，并促成2次活动报名。线索来源以公开课和转介绍为主，线索状态以新线索和跟进中为主，分析结果中高潜与中等各1，活动报名中已参加与已注册各1。",
        "sections": [
          {
            "content": "本周期内，共新增2条线索，完成2次分析记录，活动报名2次。各项核心指标处于平稳状态。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "新增线索数",
                "value": "2"
              },
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "活动报名数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周期线索主要来源于公开课和转介绍，各占比50%。建议关注公开课渠道的持续效果以及转介绍机制的有效性。",
            "heading": "线索来源分布",
            "metrics": [
              {
                "name": "公开课",
                "value": "1"
              },
              {
                "name": "转介绍",
                "value": "1"
              }
            ]
          },
          {
            "content": "新线索与跟进中线索各1条，分布均衡，需及时安排跟进动作以推动转化。",
            "heading": "线索状态分布",
            "metrics": [
              {
                "name": "新线索",
                "value": "1"
              },
              {
                "name": "跟进中",
                "value": "1"
              }
            ]
          },
          {
            "content": "高潜客户与中等潜力客户各1位，需对高潜客户重点跟进，同时挖掘中等客户的提升空间。",
            "heading": "分析结果分布",
            "metrics": [
              {
                "name": "高潜",
                "value": "1"
              },
              {
                "name": "中等",
                "value": "1"
              }
            ]
          },
          {
            "content": "活动报名共2次，其中已参加1次，已注册1次，表明活动参与率较高，后续可继续鼓励注册用户实际到场。",
            "heading": "活动报名情况",
            "metrics": [
              {
                "name": "已参加",
                "value": "1"
              },
              {
                "name": "已注册",
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
          "report_type": "customer_operation",
          "department_id": 10,
          "owner_user_id": 102,
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
          }
        },
        "source_refs": [
          "query_report_source_data（FastAPI AI Tool）",
          "数据表：客户经营数据表（线索表、分析记录表、活动报名表），口径：按部门10、负责人102、日期2026-06-01至2026-06-07筛选"
        ],
        "recommendations": [
          "建议加强对1条‘跟进中’线索的跟进频率，提升转化率。",
          "针对高潜客户，制定个性化跟进方案。",
          "继续跟踪公开课来源的线索转化效果，评估转介绍激励政策。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 169,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:43"
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
  "url": "/api/v1/reports/114/exports",
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
      "id": 225,
      "report_id": 114,
      "export_type": "word",
      "file_name": "RP-20260611102842-e2befc5a.docx",
      "file_path": "storage\\reports\\RP-20260611102842-e2befc5a.docx",
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
  "url": "/api/v1/reports/exports/225/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102842-e2befc5a.docx\"",
    "content-length": "37609"
  },
  "binary": {
    "size_bytes": 37609,
    "sha256": "e77e628881f12ea98df0d57be7291b81a2de75f985dfa9fb4f7045c2e51bea62",
    "first_16_bytes_hex": "504b03041400000008009553cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/114/exports",
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
      "id": 226,
      "report_id": 114,
      "export_type": "pdf",
      "file_name": "RP-20260611102842-e2befc5a.pdf",
      "file_path": "storage\\reports\\RP-20260611102842-e2befc5a.pdf",
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
  "url": "/api/v1/reports/exports/226/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102842-e2befc5a.pdf\"",
    "content-length": "5728"
  },
  "binary": {
    "size_bytes": 5728,
    "sha256": "7da8c5e07777924ad966c5d956471f54d49e516ad1e724959ab03d7dd7251444",
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
    "content-length": "3280",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 170,
      "draft_no": "DR-20260611102855-6166ee59",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "一名客户预算不确定。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026-06-02部门10共收到2份日报，提交率为40.0%，其中存档1份，草稿1份。发现1项风险事项，1份报告包含明日计划。",
        "sections": [
          {
            "content": "截止报告周期，部门10员工日报总计2份，已提交0份，草稿1份，存档1份，提交率为40.0%。有1份报告包含风险，1份报告包含明日计划。",
            "heading": "总体提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "2"
              },
              {
                "name": "已提交报告数",
                "value": "0"
              },
              {
                "name": "草稿报告数",
                "value": "1"
              },
              {
                "name": "存档报告数",
                "value": "1"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "含风险报告数",
                "value": "1"
              },
              {
                "name": "含明日计划报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "关键进展：Full Employee A 输出客户研判建议。风险：Full Employee A 报告一名客户预算不确定。",
            "heading": "关键进展与风险",
            "metrics": [
              {
                "name": "关键进展项",
                "value": "1项"
              },
              {
                "name": "风险项",
                "value": "1项"
              }
            ]
          },
          {
            "content": "Full Employee A 共3条记录（2条已提交，1条存档），其中2条包含风险信息（部分客户预算未确认、一名客户预算不确定），2条包含明日计划。Full Employee B 共2条记录（1条已提交，1条草稿），其中1条包含明日计划（回访家长满意度）。注意：数据中存在重复提交记录，请以存档状态为准。",
            "heading": "员工提交详情",
            "metrics": [
              {
                "name": "Full Employee A 提交记录数",
                "value": "3"
              },
              {
                "name": "Full Employee B 提交记录数",
                "value": "2"
              }
            ]
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
          "数据来源：员工日报表（department_id=10，日期2026-06-02）"
        ],
        "recommendations": [],
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
  "url": "/api/v1/reports/drafts/170/confirm",
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
    "content-length": "3439",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 115,
      "report_no": "RP-20260611102855-f427f339",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "一名客户预算不确定。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026-06-02部门10共收到2份日报，提交率为40.0%，其中存档1份，草稿1份。发现1项风险事项，1份报告包含明日计划。",
        "sections": [
          {
            "content": "截止报告周期，部门10员工日报总计2份，已提交0份，草稿1份，存档1份，提交率为40.0%。有1份报告包含风险，1份报告包含明日计划。",
            "heading": "总体提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "2"
              },
              {
                "name": "已提交报告数",
                "value": "0"
              },
              {
                "name": "草稿报告数",
                "value": "1"
              },
              {
                "name": "存档报告数",
                "value": "1"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "含风险报告数",
                "value": "1"
              },
              {
                "name": "含明日计划报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "关键进展：Full Employee A 输出客户研判建议。风险：Full Employee A 报告一名客户预算不确定。",
            "heading": "关键进展与风险",
            "metrics": [
              {
                "name": "关键进展项",
                "value": "1项"
              },
              {
                "name": "风险项",
                "value": "1项"
              }
            ]
          },
          {
            "content": "Full Employee A 共3条记录（2条已提交，1条存档），其中2条包含风险信息（部分客户预算未确认、一名客户预算不确定），2条包含明日计划。Full Employee B 共2条记录（1条已提交，1条草稿），其中1条包含明日计划（回访家长满意度）。注意：数据中存在重复提交记录，请以存档状态为准。",
            "heading": "员工提交详情",
            "metrics": [
              {
                "name": "Full Employee A 提交记录数",
                "value": "3"
              },
              {
                "name": "Full Employee B 提交记录数",
                "value": "2"
              }
            ]
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
          "数据来源：员工日报表（department_id=10，日期2026-06-02）"
        ],
        "recommendations": [],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 170,
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
  "url": "/api/v1/reports/115/publish",
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
    "content-length": "3455",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 115,
      "report_no": "RP-20260611102855-f427f339",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "published",
      "content_json": {
        "risks": [
          "一名客户预算不确定。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026-06-02部门10共收到2份日报，提交率为40.0%，其中存档1份，草稿1份。发现1项风险事项，1份报告包含明日计划。",
        "sections": [
          {
            "content": "截止报告周期，部门10员工日报总计2份，已提交0份，草稿1份，存档1份，提交率为40.0%。有1份报告包含风险，1份报告包含明日计划。",
            "heading": "总体提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "2"
              },
              {
                "name": "已提交报告数",
                "value": "0"
              },
              {
                "name": "草稿报告数",
                "value": "1"
              },
              {
                "name": "存档报告数",
                "value": "1"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "含风险报告数",
                "value": "1"
              },
              {
                "name": "含明日计划报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "关键进展：Full Employee A 输出客户研判建议。风险：Full Employee A 报告一名客户预算不确定。",
            "heading": "关键进展与风险",
            "metrics": [
              {
                "name": "关键进展项",
                "value": "1项"
              },
              {
                "name": "风险项",
                "value": "1项"
              }
            ]
          },
          {
            "content": "Full Employee A 共3条记录（2条已提交，1条存档），其中2条包含风险信息（部分客户预算未确认、一名客户预算不确定），2条包含明日计划。Full Employee B 共2条记录（1条已提交，1条草稿），其中1条包含明日计划（回访家长满意度）。注意：数据中存在重复提交记录，请以存档状态为准。",
            "heading": "员工提交详情",
            "metrics": [
              {
                "name": "Full Employee A 提交记录数",
                "value": "3"
              },
              {
                "name": "Full Employee B 提交记录数",
                "value": "2"
              }
            ]
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
          "数据来源：员工日报表（department_id=10，日期2026-06-02）"
        ],
        "recommendations": [],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 170,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:28:56"
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
  "url": "/api/v1/reports/115/exports",
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
      "id": 227,
      "report_id": 115,
      "export_type": "word",
      "file_name": "RP-20260611102855-f427f339.docx",
      "file_path": "storage\\reports\\RP-20260611102855-f427f339.docx",
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
  "url": "/api/v1/reports/exports/227/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102855-f427f339.docx\"",
    "content-length": "37352"
  },
  "binary": {
    "size_bytes": 37352,
    "sha256": "9529e2d6c07caf918f28a7aa04d1b275bee5473729df541c00f14a363d9e52be",
    "first_16_bytes_hex": "504b03041400000008009b53cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/115/exports",
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
      "id": 228,
      "report_id": 115,
      "export_type": "pdf",
      "file_name": "RP-20260611102855-f427f339.pdf",
      "file_path": "storage\\reports\\RP-20260611102855-f427f339.pdf",
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
  "url": "/api/v1/reports/exports/228/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102855-f427f339.pdf\"",
    "content-length": "5268"
  },
  "binary": {
    "size_bytes": 5268,
    "sha256": "fa964cde62b9ee556f8116147be8d85659744eaa8c4585add6ded9cfd18c69dc",
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
    "content-length": "3022",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 171,
      "draft_no": "DR-20260611102911-39bd19c9",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在2份风险报告，但系统未归类风险主题，可能遗漏重要风险信息，需人工逐一审核。",
          "提交高峰与低谷均为同一天，报告节奏过于集中，可能影响日常监控的及时性。"
        ],
        "title": "员工日报汇总报告（周）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共提交4份日报，涉及2名员工，周提交率达100.0%，但存在2份风险报告，需关注后续处理。提交高峰与低谷均为6月1日，整体提交节奏集中。",
        "sections": [
          {
            "content": "本周部门10共收到4份员工日报，由2名员工提交，全员提交率达到100.0%。提交高峰出现在2026-06-01，当日提交2份，同日也是提交低谷，说明提交高度集中在该日期。每日趋势显示6月1日和6月2日各有2份提交，其余日期无报告。",
            "heading": "整体提交概况",
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
            "content": "从报告状态分布来看，已提交2份，已归档1份，草稿1份，说明大部分报告处于最终或半最终态。风险报告数量为2份，但未识别出明确的风险主题，需要人工核查风险内容并启动跟进流程。",
            "heading": "报告状态与风险分析",
            "metrics": [
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
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "风险主题数",
                "value": "0"
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
          "工具：query_report_source_data",
          "数据表：员工日报汇总表（部门10，日期范围2026-06-01至2026-06-07）",
          "口径说明：周提交率=实际提交员工数/应提交员工数×100%，风险报告指标记为异常或含风险标记的报告。"
        ],
        "recommendations": [
          "建议部门负责人组织对2份风险报告进行逐条分析，补充风险主题并制定应对措施。",
          "鼓励员工在周内分散提交日报，避免全部集中在周一，以提升信息覆盖的均匀性。",
          "对留存为草稿的1份报告，提醒相关员工及时完成提交。"
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
  "url": "/api/v1/reports/drafts/171/confirm",
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
    "content-length": "3173",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 116,
      "report_no": "RP-20260611102911-a7df91e9",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在2份风险报告，但系统未归类风险主题，可能遗漏重要风险信息，需人工逐一审核。",
          "提交高峰与低谷均为同一天，报告节奏过于集中，可能影响日常监控的及时性。"
        ],
        "title": "员工日报汇总报告（周）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共提交4份日报，涉及2名员工，周提交率达100.0%，但存在2份风险报告，需关注后续处理。提交高峰与低谷均为6月1日，整体提交节奏集中。",
        "sections": [
          {
            "content": "本周部门10共收到4份员工日报，由2名员工提交，全员提交率达到100.0%。提交高峰出现在2026-06-01，当日提交2份，同日也是提交低谷，说明提交高度集中在该日期。每日趋势显示6月1日和6月2日各有2份提交，其余日期无报告。",
            "heading": "整体提交概况",
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
            "content": "从报告状态分布来看，已提交2份，已归档1份，草稿1份，说明大部分报告处于最终或半最终态。风险报告数量为2份，但未识别出明确的风险主题，需要人工核查风险内容并启动跟进流程。",
            "heading": "报告状态与风险分析",
            "metrics": [
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
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "风险主题数",
                "value": "0"
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
          "工具：query_report_source_data",
          "数据表：员工日报汇总表（部门10，日期范围2026-06-01至2026-06-07）",
          "口径说明：周提交率=实际提交员工数/应提交员工数×100%，风险报告指标记为异常或含风险标记的报告。"
        ],
        "recommendations": [
          "建议部门负责人组织对2份风险报告进行逐条分析，补充风险主题并制定应对措施。",
          "鼓励员工在周内分散提交日报，避免全部集中在周一，以提升信息覆盖的均匀性。",
          "对留存为草稿的1份报告，提醒相关员工及时完成提交。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 171,
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
  "url": "/api/v1/reports/116/publish",
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
    "content-length": "3189",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 116,
      "report_no": "RP-20260611102911-a7df91e9",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周）",
      "status": "published",
      "content_json": {
        "risks": [
          "存在2份风险报告，但系统未归类风险主题，可能遗漏重要风险信息，需人工逐一审核。",
          "提交高峰与低谷均为同一天，报告节奏过于集中，可能影响日常监控的及时性。"
        ],
        "title": "员工日报汇总报告（周）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共提交4份日报，涉及2名员工，周提交率达100.0%，但存在2份风险报告，需关注后续处理。提交高峰与低谷均为6月1日，整体提交节奏集中。",
        "sections": [
          {
            "content": "本周部门10共收到4份员工日报，由2名员工提交，全员提交率达到100.0%。提交高峰出现在2026-06-01，当日提交2份，同日也是提交低谷，说明提交高度集中在该日期。每日趋势显示6月1日和6月2日各有2份提交，其余日期无报告。",
            "heading": "整体提交概况",
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
            "content": "从报告状态分布来看，已提交2份，已归档1份，草稿1份，说明大部分报告处于最终或半最终态。风险报告数量为2份，但未识别出明确的风险主题，需要人工核查风险内容并启动跟进流程。",
            "heading": "报告状态与风险分析",
            "metrics": [
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
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "风险主题数",
                "value": "0"
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
          "工具：query_report_source_data",
          "数据表：员工日报汇总表（部门10，日期范围2026-06-01至2026-06-07）",
          "口径说明：周提交率=实际提交员工数/应提交员工数×100%，风险报告指标记为异常或含风险标记的报告。"
        ],
        "recommendations": [
          "建议部门负责人组织对2份风险报告进行逐条分析，补充风险主题并制定应对措施。",
          "鼓励员工在周内分散提交日报，避免全部集中在周一，以提升信息覆盖的均匀性。",
          "对留存为草稿的1份报告，提醒相关员工及时完成提交。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 171,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:29:11"
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
  "url": "/api/v1/reports/116/exports",
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
      "id": 229,
      "report_id": 116,
      "export_type": "word",
      "file_name": "RP-20260611102911-a7df91e9.docx",
      "file_path": "storage\\reports\\RP-20260611102911-a7df91e9.docx",
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
  "url": "/api/v1/reports/exports/229/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102911-a7df91e9.docx\"",
    "content-length": "37734"
  },
  "binary": {
    "size_bytes": 37734,
    "sha256": "fe704de5327620964d186d32922f9bad51b9f4eec24ea2df7f298f0a82a605d8",
    "first_16_bytes_hex": "504b0304140000000800a553cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/116/exports",
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
      "id": 230,
      "report_id": 116,
      "export_type": "pdf",
      "file_name": "RP-20260611102911-a7df91e9.pdf",
      "file_path": "storage\\reports\\RP-20260611102911-a7df91e9.pdf",
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
  "url": "/api/v1/reports/exports/230/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102911-a7df91e9.pdf\"",
    "content-length": "4925"
  },
  "binary": {
    "size_bytes": 4925,
    "sha256": "245b57f0d07bd296529d3a816eef6fde1400b3b053f525b236919bb0ea7633bf",
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
    "content-length": "2779",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 172,
      "draft_no": "DR-20260611102921-2fd0792f",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在1名高风险学生，且仍有1条预警处于待处理状态，可能导致学生心理问题恶化或突发事件。"
        ],
        "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共监测2名学生档案，其中高风险1人、低风险1人；平均情绪得分59.0；累计产生2条预警，1条待处理、1条已处理。",
        "sections": [
          {
            "content": "本周共纳入2份学生心理健康档案。风险等级分布为：高风险1人（占比50%），低风险1人（占比50%）。情绪标签分布为：焦虑1人，稳定1人。全体学生平均情绪得分为59.0分，处于中等偏低水平，需关注情绪状态偏弱的学生。",
            "heading": "心理健康概况",
            "metrics": [
              {
                "name": "总档案数",
                "value": 2
              },
              {
                "name": "高风险人数",
                "value": 1
              },
              {
                "name": "低风险人数",
                "value": 1
              },
              {
                "name": "焦虑人数",
                "value": 1
              },
              {
                "name": "稳定人数",
                "value": 1
              },
              {
                "name": "平均情绪得分",
                "value": 59.0
              }
            ]
          },
          {
            "content": "本周共产生2条心理健康预警。按预警状态统计：待处理1条，已处理1条。按风险等级统计：高风险预警1条，中风险预警1条。待处理的预警需及时跟进，尤其关注高风险预警对应的学生。",
            "heading": "预警事件分析",
            "metrics": [
              {
                "name": "总预警数",
                "value": 2
              },
              {
                "name": "待处理预警数",
                "value": 1
              },
              {
                "name": "已处理预警数",
                "value": 1
              },
              {
                "name": "高风险预警数",
                "value": 1
              },
              {
                "name": "中风险预警数",
                "value": 1
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
          "数据来源于 query_report_source_data 工具，使用的数据表为学生心理档案表及预警记录表。",
          "口径说明：风险等级、情绪标签由系统根据标准模型自动生成，平均情绪得分为所有档案情绪分数均值。"
        ],
        "recommendations": [
          "建议心理辅导老师优先约谈高风险学生，进行一对一评估与干预。",
          "对编号待处理的预警尽快分配责任人并明确处理时限。",
          "持续监测情绪得分偏低的学生，必要时调整辅导计划。"
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
  "url": "/api/v1/reports/drafts/172/confirm",
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
    "content-length": "2953",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 117,
      "report_no": "RP-20260611102921-b972e870",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在1名高风险学生，且仍有1条预警处于待处理状态，可能导致学生心理问题恶化或突发事件。"
        ],
        "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共监测2名学生档案，其中高风险1人、低风险1人；平均情绪得分59.0；累计产生2条预警，1条待处理、1条已处理。",
        "sections": [
          {
            "content": "本周共纳入2份学生心理健康档案。风险等级分布为：高风险1人（占比50%），低风险1人（占比50%）。情绪标签分布为：焦虑1人，稳定1人。全体学生平均情绪得分为59.0分，处于中等偏低水平，需关注情绪状态偏弱的学生。",
            "heading": "心理健康概况",
            "metrics": [
              {
                "name": "总档案数",
                "value": 2
              },
              {
                "name": "高风险人数",
                "value": 1
              },
              {
                "name": "低风险人数",
                "value": 1
              },
              {
                "name": "焦虑人数",
                "value": 1
              },
              {
                "name": "稳定人数",
                "value": 1
              },
              {
                "name": "平均情绪得分",
                "value": 59.0
              }
            ]
          },
          {
            "content": "本周共产生2条心理健康预警。按预警状态统计：待处理1条，已处理1条。按风险等级统计：高风险预警1条，中风险预警1条。待处理的预警需及时跟进，尤其关注高风险预警对应的学生。",
            "heading": "预警事件分析",
            "metrics": [
              {
                "name": "总预警数",
                "value": 2
              },
              {
                "name": "待处理预警数",
                "value": 1
              },
              {
                "name": "已处理预警数",
                "value": 1
              },
              {
                "name": "高风险预警数",
                "value": 1
              },
              {
                "name": "中风险预警数",
                "value": 1
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
          "数据来源于 query_report_source_data 工具，使用的数据表为学生心理档案表及预警记录表。",
          "口径说明：风险等级、情绪标签由系统根据标准模型自动生成，平均情绪得分为所有档案情绪分数均值。"
        ],
        "recommendations": [
          "建议心理辅导老师优先约谈高风险学生，进行一对一评估与干预。",
          "对编号待处理的预警尽快分配责任人并明确处理时限。",
          "持续监测情绪得分偏低的学生，必要时调整辅导计划。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 172,
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
  "url": "/api/v1/reports/117/publish",
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
    "content-length": "2969",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 117,
      "report_no": "RP-20260611102921-b972e870",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "存在1名高风险学生，且仍有1条预警处于待处理状态，可能导致学生心理问题恶化或突发事件。"
        ],
        "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共监测2名学生档案，其中高风险1人、低风险1人；平均情绪得分59.0；累计产生2条预警，1条待处理、1条已处理。",
        "sections": [
          {
            "content": "本周共纳入2份学生心理健康档案。风险等级分布为：高风险1人（占比50%），低风险1人（占比50%）。情绪标签分布为：焦虑1人，稳定1人。全体学生平均情绪得分为59.0分，处于中等偏低水平，需关注情绪状态偏弱的学生。",
            "heading": "心理健康概况",
            "metrics": [
              {
                "name": "总档案数",
                "value": 2
              },
              {
                "name": "高风险人数",
                "value": 1
              },
              {
                "name": "低风险人数",
                "value": 1
              },
              {
                "name": "焦虑人数",
                "value": 1
              },
              {
                "name": "稳定人数",
                "value": 1
              },
              {
                "name": "平均情绪得分",
                "value": 59.0
              }
            ]
          },
          {
            "content": "本周共产生2条心理健康预警。按预警状态统计：待处理1条，已处理1条。按风险等级统计：高风险预警1条，中风险预警1条。待处理的预警需及时跟进，尤其关注高风险预警对应的学生。",
            "heading": "预警事件分析",
            "metrics": [
              {
                "name": "总预警数",
                "value": 2
              },
              {
                "name": "待处理预警数",
                "value": 1
              },
              {
                "name": "已处理预警数",
                "value": 1
              },
              {
                "name": "高风险预警数",
                "value": 1
              },
              {
                "name": "中风险预警数",
                "value": 1
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
          "数据来源于 query_report_source_data 工具，使用的数据表为学生心理档案表及预警记录表。",
          "口径说明：风险等级、情绪标签由系统根据标准模型自动生成，平均情绪得分为所有档案情绪分数均值。"
        ],
        "recommendations": [
          "建议心理辅导老师优先约谈高风险学生，进行一对一评估与干预。",
          "对编号待处理的预警尽快分配责任人并明确处理时限。",
          "持续监测情绪得分偏低的学生，必要时调整辅导计划。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 172,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:29:21"
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
  "url": "/api/v1/reports/117/exports",
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
      "id": 231,
      "report_id": 117,
      "export_type": "word",
      "file_name": "RP-20260611102921-b972e870.docx",
      "file_path": "storage\\reports\\RP-20260611102921-b972e870.docx",
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
  "url": "/api/v1/reports/exports/231/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102921-b972e870.docx\"",
    "content-length": "37598"
  },
  "binary": {
    "size_bytes": 37598,
    "sha256": "e8d23990fd55aa0dce215ab353c50bc9ba1fd1a9e958b753de20fa10ca0f874c",
    "first_16_bytes_hex": "504b0304140000000800aa53cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/117/exports",
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
      "id": 232,
      "report_id": 117,
      "export_type": "pdf",
      "file_name": "RP-20260611102921-b972e870.pdf",
      "file_path": "storage\\reports\\RP-20260611102921-b972e870.pdf",
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
  "url": "/api/v1/reports/exports/232/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611102921-b972e870.pdf\"",
    "content-length": "5005"
  },
  "binary": {
    "size_bytes": 5005,
    "sha256": "82ad186b8eca1ba1a32a2655d262ffbc69817a8bf4a5aacfbf99513c5c80fd1e",
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
  "ai_draft": 172,
  "ai_report": 117,
  "report_export_record": 232,
  "audit_log": 870,
  "ai_tool_call_log": 183
}
```

### 阶段结论

- 结果：通过

