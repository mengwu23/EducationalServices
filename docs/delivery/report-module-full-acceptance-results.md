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

- 执行时间：`2026-06-10 21:36:58`
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
    "content-length": "348",
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
        }
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
    "content-length": "963",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 43,
      "draft_no": "DR-20260610213658-60b2e6c3",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "投诉处理周报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期共处理投诉 3 条。",
        "sections": [
          {
            "content": "按状态统计本周期投诉处理进展，供管理员复盘服务响应。",
            "heading": "投诉概览",
            "metrics": [
              {
                "name": "pending",
                "value": 1
              },
              {
                "name": "processing",
                "value": 1
              },
              {
                "name": "resolved",
                "value": 1
              }
            ]
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
          "total_tickets": 3
        },
        "source_refs": [
          "complaint_weekly"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
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
  "url": "/api/v1/reports/drafts/43/confirm",
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
    "content-length": "1115",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 18,
      "report_no": "RP-20260610213658-59a47b4d",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "投诉处理周报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期共处理投诉 3 条。",
        "sections": [
          {
            "content": "按状态统计本周期投诉处理进展，供管理员复盘服务响应。",
            "heading": "投诉概览",
            "metrics": [
              {
                "name": "pending",
                "value": 1
              },
              {
                "name": "processing",
                "value": 1
              },
              {
                "name": "resolved",
                "value": 1
              }
            ]
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
          "total_tickets": 3
        },
        "source_refs": [
          "complaint_weekly"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 43,
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
  "url": "/api/v1/reports/18/publish",
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
    "content-length": "1131",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 18,
      "report_no": "RP-20260610213658-59a47b4d",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "投诉处理周报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期共处理投诉 3 条。",
        "sections": [
          {
            "content": "按状态统计本周期投诉处理进展，供管理员复盘服务响应。",
            "heading": "投诉概览",
            "metrics": [
              {
                "name": "pending",
                "value": 1
              },
              {
                "name": "processing",
                "value": 1
              },
              {
                "name": "resolved",
                "value": 1
              }
            ]
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
          "total_tickets": 3
        },
        "source_refs": [
          "complaint_weekly"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 43,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T21:36:59"
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
  "url": "/api/v1/reports/18/exports",
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
    "content-length": "249",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 33,
      "report_id": 18,
      "export_type": "word",
      "file_name": "RP-20260610213658-59a47b4d.docx",
      "file_path": "storage\\reports\\RP-20260610213658-59a47b4d.docx",
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
  "url": "/api/v1/reports/exports/33/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213658-59a47b4d.docx\"",
    "content-length": "36909"
  },
  "binary": {
    "size_bytes": 36909,
    "sha256": "38b2564627ae0fc22326e0e2b96ba727051e68e6fb8536848935a7cb8bab9027",
    "first_16_bytes_hex": "504b03041400000008009dacca5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/18/exports",
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
    "content-length": "246",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 34,
      "report_id": 18,
      "export_type": "pdf",
      "file_name": "RP-20260610213658-59a47b4d.pdf",
      "file_path": "storage\\reports\\RP-20260610213658-59a47b4d.pdf",
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
  "url": "/api/v1/reports/exports/34/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213658-59a47b4d.pdf\"",
    "content-length": "3480"
  },
  "binary": {
    "size_bytes": 3480,
    "sha256": "9601214b88847e24e7e90be237ab57b6083d108c6e957501039cfd2dc90aacf4",
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
    "content-length": "355",
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
        "event_registrations": 2
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
    "content-length": "1000",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 44,
      "draft_no": "DR-20260610213659-078dec51",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "客户经营分析报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条。",
        "sections": [
          {
            "content": "汇总线索、客户研判和活动报名数据，辅助判断经营质量。",
            "heading": "客户转化概览",
            "metrics": [
              {
                "name": "new_leads",
                "value": 2
              },
              {
                "name": "analysis_records",
                "value": 2
              },
              {
                "name": "event_registrations",
                "value": 2
              }
            ]
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
          "event_registrations": 2
        },
        "source_refs": [
          "customer_operation"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
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
  "url": "/api/v1/reports/drafts/44/confirm",
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
    "content-length": "1153",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 19,
      "report_no": "RP-20260610213659-1c5ab60f",
      "report_type": "customer_operation",
      "title": "客户经营分析报",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "客户经营分析报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条。",
        "sections": [
          {
            "content": "汇总线索、客户研判和活动报名数据，辅助判断经营质量。",
            "heading": "客户转化概览",
            "metrics": [
              {
                "name": "new_leads",
                "value": 2
              },
              {
                "name": "analysis_records",
                "value": 2
              },
              {
                "name": "event_registrations",
                "value": 2
              }
            ]
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
          "event_registrations": 2
        },
        "source_refs": [
          "customer_operation"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 44,
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
  "url": "/api/v1/reports/19/publish",
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
    "content-length": "1169",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 19,
      "report_no": "RP-20260610213659-1c5ab60f",
      "report_type": "customer_operation",
      "title": "客户经营分析报",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "客户经营分析报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期新增线索 2 条。",
        "sections": [
          {
            "content": "汇总线索、客户研判和活动报名数据，辅助判断经营质量。",
            "heading": "客户转化概览",
            "metrics": [
              {
                "name": "new_leads",
                "value": 2
              },
              {
                "name": "analysis_records",
                "value": 2
              },
              {
                "name": "event_registrations",
                "value": 2
              }
            ]
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
          "event_registrations": 2
        },
        "source_refs": [
          "customer_operation"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 44,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T21:36:59"
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
  "url": "/api/v1/reports/19/exports",
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
    "content-length": "249",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 35,
      "report_id": 19,
      "export_type": "word",
      "file_name": "RP-20260610213659-1c5ab60f.docx",
      "file_path": "storage\\reports\\RP-20260610213659-1c5ab60f.docx",
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
  "url": "/api/v1/reports/exports/35/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213659-1c5ab60f.docx\"",
    "content-length": "36951"
  },
  "binary": {
    "size_bytes": 36951,
    "sha256": "1ddd9327fc49dd0d977cb5aeb2bc2a7082bc812bdf51285f2bc82987ff8bbdcd",
    "first_16_bytes_hex": "504b03041400000008009dacca5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/19/exports",
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
    "content-length": "246",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 36,
      "report_id": 19,
      "export_type": "pdf",
      "file_name": "RP-20260610213659-1c5ab60f.pdf",
      "file_path": "storage\\reports\\RP-20260610213659-1c5ab60f.pdf",
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
  "url": "/api/v1/reports/exports/36/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213659-1c5ab60f.pdf\"",
    "content-length": "3509"
  },
  "binary": {
    "size_bytes": 3509,
    "sha256": "4d19dae6e65b28ba0a2f0f8bd5b607bb0076adc11cf1830b38e85535ea05e9ec",
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
    "content-length": "447",
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
        "tomorrow_plan_reports": 1
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
    "content-length": "1228",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 45,
      "draft_no": "DR-20260610213659-8f14b70d",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "员工日报汇总报告（日）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日共汇总日报 2 份。",
        "sections": [
          {
            "content": "按单日统计员工日报提交、草稿、归档和风险摘要情况。",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "total_reports",
                "value": 2
              },
              {
                "name": "submitted_reports",
                "value": 0
              },
              {
                "name": "draft_reports",
                "value": 1
              },
              {
                "name": "archived_reports",
                "value": 1
              },
              {
                "name": "risk_reports",
                "value": 1
              },
              {
                "name": "tomorrow_plan_reports",
                "value": 1
              }
            ]
          }
        ],
        "report_type": "employee_daily_summary",
        "source_data": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "archived_reports": 1,
          "submitted_reports": 0,
          "tomorrow_plan_reports": 1
        },
        "source_refs": [
          "employee_daily_summary"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
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
  "url": "/api/v1/reports/drafts/45/confirm",
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
    "content-length": "1389",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 20,
      "report_no": "RP-20260610213659-ffe4b9a1",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（日）",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "员工日报汇总报告（日）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日共汇总日报 2 份。",
        "sections": [
          {
            "content": "按单日统计员工日报提交、草稿、归档和风险摘要情况。",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "total_reports",
                "value": 2
              },
              {
                "name": "submitted_reports",
                "value": 0
              },
              {
                "name": "draft_reports",
                "value": 1
              },
              {
                "name": "archived_reports",
                "value": 1
              },
              {
                "name": "risk_reports",
                "value": 1
              },
              {
                "name": "tomorrow_plan_reports",
                "value": 1
              }
            ]
          }
        ],
        "report_type": "employee_daily_summary",
        "source_data": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "archived_reports": 1,
          "submitted_reports": 0,
          "tomorrow_plan_reports": 1
        },
        "source_refs": [
          "employee_daily_summary"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 45,
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
  "url": "/api/v1/reports/20/publish",
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
    "content-length": "1405",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 20,
      "report_no": "RP-20260610213659-ffe4b9a1",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（日）",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "员工日报汇总报告（日）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日共汇总日报 2 份。",
        "sections": [
          {
            "content": "按单日统计员工日报提交、草稿、归档和风险摘要情况。",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "total_reports",
                "value": 2
              },
              {
                "name": "submitted_reports",
                "value": 0
              },
              {
                "name": "draft_reports",
                "value": 1
              },
              {
                "name": "archived_reports",
                "value": 1
              },
              {
                "name": "risk_reports",
                "value": 1
              },
              {
                "name": "tomorrow_plan_reports",
                "value": 1
              }
            ]
          }
        ],
        "report_type": "employee_daily_summary",
        "source_data": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "report_type": "employee_daily_summary",
          "risk_reports": 1,
          "department_id": 10,
          "draft_reports": 1,
          "status_counts": {
            "draft": 1,
            "archived": 1
          },
          "total_reports": 2,
          "archived_reports": 1,
          "submitted_reports": 0,
          "tomorrow_plan_reports": 1
        },
        "source_refs": [
          "employee_daily_summary"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 45,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T21:37:00"
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
  "url": "/api/v1/reports/20/exports",
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
    "content-length": "249",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 37,
      "report_id": 20,
      "export_type": "word",
      "file_name": "RP-20260610213659-ffe4b9a1.docx",
      "file_path": "storage\\reports\\RP-20260610213659-ffe4b9a1.docx",
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
  "url": "/api/v1/reports/exports/37/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213659-ffe4b9a1.docx\"",
    "content-length": "36966"
  },
  "binary": {
    "size_bytes": 36966,
    "sha256": "38339332133ca5263c5f3aa323eb8bdb8e0dfdef10bd2522b9f2726f25ca2615",
    "first_16_bytes_hex": "504b03041400000008009dacca5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/20/exports",
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
    "content-length": "246",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 38,
      "report_id": 20,
      "export_type": "pdf",
      "file_name": "RP-20260610213659-ffe4b9a1.pdf",
      "file_path": "storage\\reports\\RP-20260610213659-ffe4b9a1.pdf",
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
  "url": "/api/v1/reports/exports/38/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213659-ffe4b9a1.pdf\"",
    "content-length": "3711"
  },
  "binary": {
    "size_bytes": 3711,
    "sha256": "cb2fb140770cfc41e9b175078db639e9fb33641d5ed30e40243d8b0cf4b2fb4a",
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
    "content-length": "445",
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
        "risk_reports": 2
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
    "content-length": "1290",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 46,
      "draft_no": "DR-20260610213659-fc45d234",
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
        "summary": "本周共汇总日报 4 份。",
        "sections": [
          {
            "content": "按周统计日报总量、提交员工数、每日趋势和风险摘要数量。",
            "heading": "周度日报趋势",
            "metrics": [
              {
                "name": "total_reports",
                "value": 4
              },
              {
                "name": "distinct_employees",
                "value": 2
              },
              {
                "name": "risk_reports",
                "value": 2
              }
            ]
          },
          {
            "content": "展示本周期内各日期日报提交数量。",
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
          "distinct_employees": 2
        },
        "source_refs": [
          "employee_weekly_summary"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
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
  "url": "/api/v1/reports/drafts/46/confirm",
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
    "content-length": "1450",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 21,
      "report_no": "RP-20260610213659-9b1dbbc5",
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
        "summary": "本周共汇总日报 4 份。",
        "sections": [
          {
            "content": "按周统计日报总量、提交员工数、每日趋势和风险摘要数量。",
            "heading": "周度日报趋势",
            "metrics": [
              {
                "name": "total_reports",
                "value": 4
              },
              {
                "name": "distinct_employees",
                "value": 2
              },
              {
                "name": "risk_reports",
                "value": 2
              }
            ]
          },
          {
            "content": "展示本周期内各日期日报提交数量。",
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
          "distinct_employees": 2
        },
        "source_refs": [
          "employee_weekly_summary"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 46,
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
  "url": "/api/v1/reports/21/publish",
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
    "content-length": "1466",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 21,
      "report_no": "RP-20260610213659-9b1dbbc5",
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
        "summary": "本周共汇总日报 4 份。",
        "sections": [
          {
            "content": "按周统计日报总量、提交员工数、每日趋势和风险摘要数量。",
            "heading": "周度日报趋势",
            "metrics": [
              {
                "name": "total_reports",
                "value": 4
              },
              {
                "name": "distinct_employees",
                "value": 2
              },
              {
                "name": "risk_reports",
                "value": 2
              }
            ]
          },
          {
            "content": "展示本周期内各日期日报提交数量。",
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
          "distinct_employees": 2
        },
        "source_refs": [
          "employee_weekly_summary"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 46,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T21:37:00"
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
  "url": "/api/v1/reports/21/exports",
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
    "content-length": "249",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 39,
      "report_id": 21,
      "export_type": "word",
      "file_name": "RP-20260610213659-9b1dbbc5.docx",
      "file_path": "storage\\reports\\RP-20260610213659-9b1dbbc5.docx",
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
  "url": "/api/v1/reports/exports/39/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213659-9b1dbbc5.docx\"",
    "content-length": "37001"
  },
  "binary": {
    "size_bytes": 37001,
    "sha256": "ff1bfd32e66fe0bcd7cdaeaa1d441df079b205e67ecdaa2a6c7c9b26cba40b73",
    "first_16_bytes_hex": "504b0304140000000800a0acca5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/21/exports",
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
    "content-length": "246",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 40,
      "report_id": 21,
      "export_type": "pdf",
      "file_name": "RP-20260610213659-9b1dbbc5.pdf",
      "file_path": "storage\\reports\\RP-20260610213659-9b1dbbc5.pdf",
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
  "url": "/api/v1/reports/exports/40/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213659-9b1dbbc5.pdf\"",
    "content-length": "3784"
  },
  "binary": {
    "size_bytes": 3784,
    "sha256": "9c27d8c2db1647110db2767aa3396ccd23d60bb76fc3fe46d9d4fe110a768afe",
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
    "content-length": "1418",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 47,
      "draft_no": "DR-20260610213700-5b5d496c",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "学生心理健康周报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周纳入心理画像 2 份，预警 2 条。",
        "sections": [
          {
            "content": "按风险等级、情绪标签和平均情绪分观察学生心理健康趋势。",
            "heading": "心理风险概览",
            "metrics": [
              {
                "name": "high",
                "value": 1
              },
              {
                "name": "low",
                "value": 1
              },
              {
                "name": "average_emotion_score",
                "value": 59.0
              },
              {
                "name": "total_alerts",
                "value": 2
              }
            ]
          },
          {
            "content": "按预警状态和预警风险等级统计本周期心理健康跟进情况。",
            "heading": "预警处理概览",
            "metrics": [
              {
                "name": "pending",
                "value": 1
              },
              {
                "name": "resolved",
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
          "student_psych_weekly"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
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
  "url": "/api/v1/reports/drafts/47/confirm",
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
    "content-length": "1572",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 22,
      "report_no": "RP-20260610213700-962b1fb3",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "学生心理健康周报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周纳入心理画像 2 份，预警 2 条。",
        "sections": [
          {
            "content": "按风险等级、情绪标签和平均情绪分观察学生心理健康趋势。",
            "heading": "心理风险概览",
            "metrics": [
              {
                "name": "high",
                "value": 1
              },
              {
                "name": "low",
                "value": 1
              },
              {
                "name": "average_emotion_score",
                "value": 59.0
              },
              {
                "name": "total_alerts",
                "value": 2
              }
            ]
          },
          {
            "content": "按预警状态和预警风险等级统计本周期心理健康跟进情况。",
            "heading": "预警处理概览",
            "metrics": [
              {
                "name": "pending",
                "value": 1
              },
              {
                "name": "resolved",
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
          "student_psych_weekly"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 47,
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
  "url": "/api/v1/reports/22/publish",
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
    "content-length": "1588",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 22,
      "report_no": "RP-20260610213700-962b1fb3",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "学生心理健康周报",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周纳入心理画像 2 份，预警 2 条。",
        "sections": [
          {
            "content": "按风险等级、情绪标签和平均情绪分观察学生心理健康趋势。",
            "heading": "心理风险概览",
            "metrics": [
              {
                "name": "high",
                "value": 1
              },
              {
                "name": "low",
                "value": 1
              },
              {
                "name": "average_emotion_score",
                "value": 59.0
              },
              {
                "name": "total_alerts",
                "value": 2
              }
            ]
          },
          {
            "content": "按预警状态和预警风险等级统计本周期心理健康跟进情况。",
            "heading": "预警处理概览",
            "metrics": [
              {
                "name": "pending",
                "value": 1
              },
              {
                "name": "resolved",
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
          "student_psych_weekly"
        ],
        "recommendations": [
          "请结合业务负责人反馈复核 AI 报告草稿。"
        ]
      },
      "source_draft_id": 47,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T21:37:00"
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
  "url": "/api/v1/reports/22/exports",
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
    "content-length": "249",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 41,
      "report_id": 22,
      "export_type": "word",
      "file_name": "RP-20260610213700-962b1fb3.docx",
      "file_path": "storage\\reports\\RP-20260610213700-962b1fb3.docx",
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
  "url": "/api/v1/reports/exports/41/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213700-962b1fb3.docx\"",
    "content-length": "37046"
  },
  "binary": {
    "size_bytes": 37046,
    "sha256": "fba0c4db04cc5e6fb21f46c2de2e11b439fabdd3d78730dfbd29a384fe0a62a4",
    "first_16_bytes_hex": "504b0304140000000800a0acca5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/22/exports",
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
    "content-length": "246",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 42,
      "report_id": 22,
      "export_type": "pdf",
      "file_name": "RP-20260610213700-962b1fb3.pdf",
      "file_path": "storage\\reports\\RP-20260610213700-962b1fb3.pdf",
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
  "url": "/api/v1/reports/exports/42/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610213700-962b1fb3.pdf\"",
    "content-length": "3864"
  },
  "binary": {
    "size_bytes": 3864,
    "sha256": "4b9c844f8892adae764bf967f8231816f3660b8f10ec478f7845bcf12d03bf4c",
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
  "ai_draft": 47,
  "ai_report": 22,
  "report_export_record": 42,
  "audit_log": 175,
  "ai_tool_call_log": 37
}
```

### 阶段结论

- 结果：通过


## real-dify 阶段

- 执行时间：`2026-06-10 21:37:04`
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
    "content-length": "353",
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
        }
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
  "status_code": 502,
  "headers": {
    "content-length": "84",
    "content-type": "application/json"
  },
  "json": {
    "detail": "报告草稿生成失败：Dify 返回内容无法解析为报告草稿"
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
    "content-length": "360",
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
        "event_registrations": 2
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
  "status_code": 502,
  "headers": {
    "content-length": "84",
    "content-type": "application/json"
  },
  "json": {
    "detail": "报告草稿生成失败：Dify 返回内容无法解析为报告草稿"
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
    "content-length": "452",
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
        "tomorrow_plan_reports": 1
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
  "status_code": 502,
  "headers": {
    "content-length": "84",
    "content-type": "application/json"
  },
  "json": {
    "detail": "报告草稿生成失败：Dify 返回内容无法解析为报告草稿"
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
    "content-length": "450",
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
        "risk_reports": 2
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
  "status_code": 502,
  "headers": {
    "content-length": "84",
    "content-type": "application/json"
  },
  "json": {
    "detail": "报告草稿生成失败：Dify 返回内容无法解析为报告草稿"
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
  "status_code": 502,
  "headers": {
    "content-length": "84",
    "content-type": "application/json"
  },
  "json": {
    "detail": "报告草稿生成失败：Dify 返回内容无法解析为报告草稿"
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
  "ai_draft": 52,
  "ai_report": 22,
  "report_export_record": 42,
  "audit_log": 180,
  "ai_tool_call_log": 42
}
```

### 阶段结论

- 结果：失败，失败步骤数 `5`
- 投诉处理周报 - 生成草稿 返回状态码 502，期望 [200]
- 客户经营分析报告 - 生成草稿 返回状态码 502，期望 [200]
- 员工日报汇总报告（日） - 生成草稿 返回状态码 502，期望 [200]
- 员工日报汇总报告（周） - 生成草稿 返回状态码 502，期望 [200]
- 学生心理健康周报 - 生成草稿 返回状态码 502，期望 [200]

