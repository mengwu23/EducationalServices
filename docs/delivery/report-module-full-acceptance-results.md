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

- 执行时间：`2026-06-11 09:27:46`
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
    "content-length": "964",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 143,
      "draft_no": "DR-20260611092747-d8a9d758",
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
  "url": "/api/v1/reports/drafts/143/confirm",
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
    "content-length": "1116",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 88,
      "report_no": "RP-20260611092747-8c4270f2",
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
      "source_draft_id": 143,
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
  "url": "/api/v1/reports/88/publish",
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
    "content-length": "1132",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 88,
      "report_no": "RP-20260611092747-8c4270f2",
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
      "source_draft_id": 143,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:27:47"
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
  "url": "/api/v1/reports/88/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 173,
      "report_id": 88,
      "export_type": "word",
      "file_name": "RP-20260611092747-8c4270f2.docx",
      "file_path": "storage\\reports\\RP-20260611092747-8c4270f2.docx",
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
  "url": "/api/v1/reports/exports/173/download",
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
    "content-length": "36909",
    "content-disposition": "attachment; filename=\"RP-20260611092747-8c4270f2.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 36909,
    "sha256": "6d542348e49b0e20f4b0ae3bc19ce745dd47eecb302532a6072cbbca22fcb136",
    "first_16_bytes_hex": "504b0304140000000800774bcb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/88/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 174,
      "report_id": 88,
      "export_type": "pdf",
      "file_name": "RP-20260611092747-8c4270f2.pdf",
      "file_path": "storage\\reports\\RP-20260611092747-8c4270f2.pdf",
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
  "url": "/api/v1/reports/exports/174/download",
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
    "content-length": "3480",
    "content-disposition": "attachment; filename=\"RP-20260611092747-8c4270f2.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 3480,
    "sha256": "71b4288342650e69491c555c08fffdf7e884f08ebc2beff33befc021fc729fa9",
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
    "content-length": "1001",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 144,
      "draft_no": "DR-20260611092747-c16b6e28",
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
  "url": "/api/v1/reports/drafts/144/confirm",
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
    "content-length": "1154",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 89,
      "report_no": "RP-20260611092747-770d97a6",
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
      "source_draft_id": 144,
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
  "url": "/api/v1/reports/89/publish",
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
    "content-length": "1170",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 89,
      "report_no": "RP-20260611092747-770d97a6",
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
      "source_draft_id": 144,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:27:48"
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
  "url": "/api/v1/reports/89/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 175,
      "report_id": 89,
      "export_type": "word",
      "file_name": "RP-20260611092747-770d97a6.docx",
      "file_path": "storage\\reports\\RP-20260611092747-770d97a6.docx",
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
  "url": "/api/v1/reports/exports/175/download",
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
    "content-length": "36951",
    "content-disposition": "attachment; filename=\"RP-20260611092747-770d97a6.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 36951,
    "sha256": "8bf9ec1430a278ee905c1ef28e17a989d04f6cff7db0170a6df493bc4bfa37f0",
    "first_16_bytes_hex": "504b0304140000000800784bcb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/89/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 176,
      "report_id": 89,
      "export_type": "pdf",
      "file_name": "RP-20260611092747-770d97a6.pdf",
      "file_path": "storage\\reports\\RP-20260611092747-770d97a6.pdf",
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
  "url": "/api/v1/reports/exports/176/download",
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
    "content-length": "3509",
    "content-disposition": "attachment; filename=\"RP-20260611092747-770d97a6.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 3509,
    "sha256": "e8ddd6642cdd2ee9d0666354f91c6029bfe9dfb71308bfadc79990aafc01b2ce",
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
    "content-length": "1229",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 145,
      "draft_no": "DR-20260611092748-2a4d4ff8",
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
  "url": "/api/v1/reports/drafts/145/confirm",
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
    "content-length": "1390",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 90,
      "report_no": "RP-20260611092748-5843eae0",
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
      "source_draft_id": 145,
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
  "url": "/api/v1/reports/90/publish",
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
    "content-length": "1406",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 90,
      "report_no": "RP-20260611092748-5843eae0",
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
      "source_draft_id": 145,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:27:48"
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
  "url": "/api/v1/reports/90/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 177,
      "report_id": 90,
      "export_type": "word",
      "file_name": "RP-20260611092748-5843eae0.docx",
      "file_path": "storage\\reports\\RP-20260611092748-5843eae0.docx",
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
  "url": "/api/v1/reports/exports/177/download",
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
    "content-length": "36966",
    "content-disposition": "attachment; filename=\"RP-20260611092748-5843eae0.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 36966,
    "sha256": "cad7133700a70b9b28d24661bec555f6e4b01c00a2440309aec47adc1c0617c6",
    "first_16_bytes_hex": "504b0304140000000800784bcb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/90/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 178,
      "report_id": 90,
      "export_type": "pdf",
      "file_name": "RP-20260611092748-5843eae0.pdf",
      "file_path": "storage\\reports\\RP-20260611092748-5843eae0.pdf",
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
  "url": "/api/v1/reports/exports/178/download",
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
    "content-length": "3711",
    "content-disposition": "attachment; filename=\"RP-20260611092748-5843eae0.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 3711,
    "sha256": "fd1c379aee942f4288dceac06977008ecdd0daaf8357b39ee07b302bb2cb48b2",
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
    "content-length": "1291",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 146,
      "draft_no": "DR-20260611092748-6c30d6f4",
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
  "url": "/api/v1/reports/drafts/146/confirm",
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
    "content-length": "1451",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 91,
      "report_no": "RP-20260611092748-43e8e368",
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
      "source_draft_id": 146,
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
  "url": "/api/v1/reports/91/publish",
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
    "content-length": "1467",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 91,
      "report_no": "RP-20260611092748-43e8e368",
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
      "source_draft_id": 146,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:27:49"
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
  "url": "/api/v1/reports/91/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 179,
      "report_id": 91,
      "export_type": "word",
      "file_name": "RP-20260611092748-43e8e368.docx",
      "file_path": "storage\\reports\\RP-20260611092748-43e8e368.docx",
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
  "url": "/api/v1/reports/exports/179/download",
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
    "content-length": "37001",
    "content-disposition": "attachment; filename=\"RP-20260611092748-43e8e368.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 37001,
    "sha256": "82e55f0f7118a788d69e6396c505227dce1ad42451f0d9f50982c8c0f1ebf7ca",
    "first_16_bytes_hex": "504b0304140000000800784bcb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/91/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 180,
      "report_id": 91,
      "export_type": "pdf",
      "file_name": "RP-20260611092748-43e8e368.pdf",
      "file_path": "storage\\reports\\RP-20260611092748-43e8e368.pdf",
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
  "url": "/api/v1/reports/exports/180/download",
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
    "content-length": "3784",
    "content-disposition": "attachment; filename=\"RP-20260611092748-43e8e368.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 3784,
    "sha256": "48e76c06e2f738a0fcb661ce33b84ca095bd06f3b710d9bce7ecc50727047de5",
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
    "content-length": "1419",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 147,
      "draft_no": "DR-20260611092749-5ee81a30",
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
  "url": "/api/v1/reports/drafts/147/confirm",
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
    "content-length": "1573",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 92,
      "report_no": "RP-20260611092749-410c73b4",
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
      "source_draft_id": 147,
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
  "url": "/api/v1/reports/92/publish",
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
    "content-length": "1589",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 92,
      "report_no": "RP-20260611092749-410c73b4",
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
      "source_draft_id": 147,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:27:49"
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
  "url": "/api/v1/reports/92/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 181,
      "report_id": 92,
      "export_type": "word",
      "file_name": "RP-20260611092749-410c73b4.docx",
      "file_path": "storage\\reports\\RP-20260611092749-410c73b4.docx",
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
  "url": "/api/v1/reports/exports/181/download",
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
    "content-length": "37046",
    "content-disposition": "attachment; filename=\"RP-20260611092749-410c73b4.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 37046,
    "sha256": "9d07d755686d317b4372b536798daec278d0bf3ef8c3e06d3fde8ee79a5aba83",
    "first_16_bytes_hex": "504b0304140000000800784bcb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/92/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 182,
      "report_id": 92,
      "export_type": "pdf",
      "file_name": "RP-20260611092749-410c73b4.pdf",
      "file_path": "storage\\reports\\RP-20260611092749-410c73b4.pdf",
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
  "url": "/api/v1/reports/exports/182/download",
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
    "content-length": "3864",
    "content-disposition": "attachment; filename=\"RP-20260611092749-410c73b4.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 3864,
    "sha256": "dd430549eaa1a17fdbcf8801a9cdbede920d5448b48707ff9fc067daa40d61a0",
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
  "ai_draft": 147,
  "ai_report": 92,
  "report_export_record": 182,
  "audit_log": 695,
  "ai_tool_call_log": 143
}
```

### 阶段结论

- 结果：通过


## real-dify 阶段

- 执行时间：`2026-06-11 09:27:53`
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
  "status_code": 200,
  "headers": {
    "content-length": "1910",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 148,
      "draft_no": "DR-20260611092806-2b9facad",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "待处理与处理中工单各占1件，需持续关注处理时效，避免转为超期工单。"
        ],
        "title": "投诉处理周报（部门10）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月1日至6月7日，部门10共收到投诉工单3件，其中待处理1件、处理中1件、已解决1件，整体处理进度正常。",
        "sections": [
          {
            "content": "本周部门10投诉工单总量为3件，覆盖待处理、处理中及已解决三个状态，工单流转情况清晰，暂无积压异常。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "投诉工单总数",
                "value": "3"
              },
              {
                "name": "待处理",
                "value": "1"
              },
              {
                "name": "处理中",
                "value": "1"
              },
              {
                "name": "已解决",
                "value": "1"
              }
            ]
          },
          {
            "content": "按状态统计，待处理工单1件（占比33.3%），处理中工单1件（占比33.3%），已解决工单1件（占比33.3%），各状态分布均衡。",
            "heading": "工单状态分布",
            "metrics": [
              {
                "name": "待处理占比",
                "value": "33.3%"
              },
              {
                "name": "处理中占比",
                "value": "33.3%"
              },
              {
                "name": "已解决占比",
                "value": "33.3%"
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
          "total_tickets": 3
        },
        "source_refs": [
          "query_report_source_data",
          "数据表：complaint_tickets，口径：按工单状态统计部门10的投诉工单数量，时间范围2026-06-01至2026-06-07"
        ],
        "recommendations": [
          "建议优先处理待办工单，并跟进处理中工单的进展，确保本周内全部闭环。"
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
  "url": "/api/v1/reports/drafts/148/confirm",
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
    "content-length": "2066",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 93,
      "report_no": "RP-20260611092806-1b9c56b3",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（部门10）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "待处理与处理中工单各占1件，需持续关注处理时效，避免转为超期工单。"
        ],
        "title": "投诉处理周报（部门10）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月1日至6月7日，部门10共收到投诉工单3件，其中待处理1件、处理中1件、已解决1件，整体处理进度正常。",
        "sections": [
          {
            "content": "本周部门10投诉工单总量为3件，覆盖待处理、处理中及已解决三个状态，工单流转情况清晰，暂无积压异常。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "投诉工单总数",
                "value": "3"
              },
              {
                "name": "待处理",
                "value": "1"
              },
              {
                "name": "处理中",
                "value": "1"
              },
              {
                "name": "已解决",
                "value": "1"
              }
            ]
          },
          {
            "content": "按状态统计，待处理工单1件（占比33.3%），处理中工单1件（占比33.3%），已解决工单1件（占比33.3%），各状态分布均衡。",
            "heading": "工单状态分布",
            "metrics": [
              {
                "name": "待处理占比",
                "value": "33.3%"
              },
              {
                "name": "处理中占比",
                "value": "33.3%"
              },
              {
                "name": "已解决占比",
                "value": "33.3%"
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
          "total_tickets": 3
        },
        "source_refs": [
          "query_report_source_data",
          "数据表：complaint_tickets，口径：按工单状态统计部门10的投诉工单数量，时间范围2026-06-01至2026-06-07"
        ],
        "recommendations": [
          "建议优先处理待办工单，并跟进处理中工单的进展，确保本周内全部闭环。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 148,
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
  "url": "/api/v1/reports/93/publish",
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
    "content-length": "2082",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 93,
      "report_no": "RP-20260611092806-1b9c56b3",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（部门10）",
      "status": "published",
      "content_json": {
        "risks": [
          "待处理与处理中工单各占1件，需持续关注处理时效，避免转为超期工单。"
        ],
        "title": "投诉处理周报（部门10）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月1日至6月7日，部门10共收到投诉工单3件，其中待处理1件、处理中1件、已解决1件，整体处理进度正常。",
        "sections": [
          {
            "content": "本周部门10投诉工单总量为3件，覆盖待处理、处理中及已解决三个状态，工单流转情况清晰，暂无积压异常。",
            "heading": "整体概况",
            "metrics": [
              {
                "name": "投诉工单总数",
                "value": "3"
              },
              {
                "name": "待处理",
                "value": "1"
              },
              {
                "name": "处理中",
                "value": "1"
              },
              {
                "name": "已解决",
                "value": "1"
              }
            ]
          },
          {
            "content": "按状态统计，待处理工单1件（占比33.3%），处理中工单1件（占比33.3%），已解决工单1件（占比33.3%），各状态分布均衡。",
            "heading": "工单状态分布",
            "metrics": [
              {
                "name": "待处理占比",
                "value": "33.3%"
              },
              {
                "name": "处理中占比",
                "value": "33.3%"
              },
              {
                "name": "已解决占比",
                "value": "33.3%"
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
          "total_tickets": 3
        },
        "source_refs": [
          "query_report_source_data",
          "数据表：complaint_tickets，口径：按工单状态统计部门10的投诉工单数量，时间范围2026-06-01至2026-06-07"
        ],
        "recommendations": [
          "建议优先处理待办工单，并跟进处理中工单的进展，确保本周内全部闭环。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 148,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:28:07"
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
  "url": "/api/v1/reports/93/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 183,
      "report_id": 93,
      "export_type": "word",
      "file_name": "RP-20260611092806-1b9c56b3.docx",
      "file_path": "storage\\reports\\RP-20260611092806-1b9c56b3.docx",
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
  "url": "/api/v1/reports/exports/183/download",
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
    "content-length": "37293",
    "content-disposition": "attachment; filename=\"RP-20260611092806-1b9c56b3.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 37293,
    "sha256": "8eeaa94899d9f60caaecaa6faa6d8a631456fdb41778c251df4ee865185a1d6d",
    "first_16_bytes_hex": "504b0304140000000800834bcb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/93/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 184,
      "report_id": 93,
      "export_type": "pdf",
      "file_name": "RP-20260611092806-1b9c56b3.pdf",
      "file_path": "storage\\reports\\RP-20260611092806-1b9c56b3.pdf",
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
  "url": "/api/v1/reports/exports/184/download",
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
    "content-length": "4129",
    "content-disposition": "attachment; filename=\"RP-20260611092806-1b9c56b3.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 4129,
    "sha256": "914fc21610d2f8412ff022074d58c038574b78192db7458bae7d105ba7689d2c",
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
  "status_code": 200,
  "headers": {
    "content-length": "1711",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 149,
      "draft_no": "DR-20260611092813-ef94c69b",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周新线索2条，客户分析记录2条，活动报名2次，整体运营数据规模较小，需关注增长策略。",
        "sections": [
          {
            "content": "本周共获取新线索2条，主要集中在部门10，由负责人102跟进。线索量偏低，需加强多渠道引流。",
            "heading": "新线索获取情况",
            "metrics": [
              {
                "name": "new_leads",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周完成客户分析记录2条，客户分析工作持续推进；同时活动报名2次，线下/线上活动参与度尚需提升。",
            "heading": "客户分析与活动参与",
            "metrics": [
              {
                "name": "analysis_records",
                "value": "2"
              },
              {
                "name": "event_registrations",
                "value": "2"
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
          "event_registrations": 2
        },
        "source_refs": [
          "数据来源：query_report_source_data，口径说明：customer_operation 数据表（部门10，负责人102，日期2026-06-01至2026-06-07）"
        ],
        "recommendations": [
          "建议加大线索获取投入，拓展推广渠道（如社交媒体、合作方推荐）",
          "针对当前线索量不足，可考虑优化客户画像，提升转化率"
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
  "url": "/api/v1/reports/drafts/149/confirm",
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
    "content-length": "1894",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 94,
      "report_no": "RP-20260611092813-d3003e5f",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周新线索2条，客户分析记录2条，活动报名2次，整体运营数据规模较小，需关注增长策略。",
        "sections": [
          {
            "content": "本周共获取新线索2条，主要集中在部门10，由负责人102跟进。线索量偏低，需加强多渠道引流。",
            "heading": "新线索获取情况",
            "metrics": [
              {
                "name": "new_leads",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周完成客户分析记录2条，客户分析工作持续推进；同时活动报名2次，线下/线上活动参与度尚需提升。",
            "heading": "客户分析与活动参与",
            "metrics": [
              {
                "name": "analysis_records",
                "value": "2"
              },
              {
                "name": "event_registrations",
                "value": "2"
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
          "event_registrations": 2
        },
        "source_refs": [
          "数据来源：query_report_source_data，口径说明：customer_operation 数据表（部门10，负责人102，日期2026-06-01至2026-06-07）"
        ],
        "recommendations": [
          "建议加大线索获取投入，拓展推广渠道（如社交媒体、合作方推荐）",
          "针对当前线索量不足，可考虑优化客户画像，提升转化率"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 149,
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
  "url": "/api/v1/reports/94/publish",
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
    "content-length": "1910",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 94,
      "report_no": "RP-20260611092813-d3003e5f",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周新线索2条，客户分析记录2条，活动报名2次，整体运营数据规模较小，需关注增长策略。",
        "sections": [
          {
            "content": "本周共获取新线索2条，主要集中在部门10，由负责人102跟进。线索量偏低，需加强多渠道引流。",
            "heading": "新线索获取情况",
            "metrics": [
              {
                "name": "new_leads",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周完成客户分析记录2条，客户分析工作持续推进；同时活动报名2次，线下/线上活动参与度尚需提升。",
            "heading": "客户分析与活动参与",
            "metrics": [
              {
                "name": "analysis_records",
                "value": "2"
              },
              {
                "name": "event_registrations",
                "value": "2"
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
          "event_registrations": 2
        },
        "source_refs": [
          "数据来源：query_report_source_data，口径说明：customer_operation 数据表（部门10，负责人102，日期2026-06-01至2026-06-07）"
        ],
        "recommendations": [
          "建议加大线索获取投入，拓展推广渠道（如社交媒体、合作方推荐）",
          "针对当前线索量不足，可考虑优化客户画像，提升转化率"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 149,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:28:14"
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
  "url": "/api/v1/reports/94/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 185,
      "report_id": 94,
      "export_type": "word",
      "file_name": "RP-20260611092813-d3003e5f.docx",
      "file_path": "storage\\reports\\RP-20260611092813-d3003e5f.docx",
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
  "url": "/api/v1/reports/exports/185/download",
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
    "content-length": "37285",
    "content-disposition": "attachment; filename=\"RP-20260611092813-d3003e5f.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 37285,
    "sha256": "6aa9fddebdeb204599db84e3667f9e093aa6f705f5fd5e9e25254b305c25e48f",
    "first_16_bytes_hex": "504b0304140000000800864bcb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/94/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 186,
      "report_id": 94,
      "export_type": "pdf",
      "file_name": "RP-20260611092813-d3003e5f.pdf",
      "file_path": "storage\\reports\\RP-20260611092813-d3003e5f.pdf",
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
  "url": "/api/v1/reports/exports/186/download",
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
    "content-length": "3983",
    "content-disposition": "attachment; filename=\"RP-20260611092813-d3003e5f.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 3983,
    "sha256": "4eac7d879b41ecce46cab94451e0866aa1dcc0270e2321702056a25865bc170e",
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
  "status_code": 200,
  "headers": {
    "content-length": "1902",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 150,
      "draft_no": "DR-20260611092822-71ffd10e",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在1份风险报告，需及时关注和处理。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期（2026-06-02）部门10共提交2份日报，其中已归档1份，草稿1份。包含1份风险报告，1份明日计划报告。",
        "sections": [
          {
            "content": "截至2026年6月2日，部门10共有2份日报记录，其中已归档1份，草稿状态1份，无已提交报告。草稿报告需尽快完成提交。",
            "heading": "总体情况",
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
                "name": "已归档报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本期包含1份风险报告和1份明日计划报告，表明员工已识别潜在问题并有明日工作安排，但需关注风险报告的具体跟进与落实。",
            "heading": "风险与明日计划",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
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
          "query_report_source_data",
          "员工日报表（employee_daily_summary）"
        ],
        "recommendations": [
          "督促草稿报告尽快提交归档。",
          "对风险报告内容进行确认，必要时启动风险应对措施。"
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
  "url": "/api/v1/reports/drafts/150/confirm",
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
    "content-length": "2060",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 95,
      "report_no": "RP-20260611092822-13276a5c",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在1份风险报告，需及时关注和处理。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期（2026-06-02）部门10共提交2份日报，其中已归档1份，草稿1份。包含1份风险报告，1份明日计划报告。",
        "sections": [
          {
            "content": "截至2026年6月2日，部门10共有2份日报记录，其中已归档1份，草稿状态1份，无已提交报告。草稿报告需尽快完成提交。",
            "heading": "总体情况",
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
                "name": "已归档报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本期包含1份风险报告和1份明日计划报告，表明员工已识别潜在问题并有明日工作安排，但需关注风险报告的具体跟进与落实。",
            "heading": "风险与明日计划",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
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
          "query_report_source_data",
          "员工日报表（employee_daily_summary）"
        ],
        "recommendations": [
          "督促草稿报告尽快提交归档。",
          "对风险报告内容进行确认，必要时启动风险应对措施。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 150,
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
  "url": "/api/v1/reports/95/publish",
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
    "content-length": "2076",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 95,
      "report_no": "RP-20260611092822-13276a5c",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "published",
      "content_json": {
        "risks": [
          "存在1份风险报告，需及时关注和处理。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期（2026-06-02）部门10共提交2份日报，其中已归档1份，草稿1份。包含1份风险报告，1份明日计划报告。",
        "sections": [
          {
            "content": "截至2026年6月2日，部门10共有2份日报记录，其中已归档1份，草稿状态1份，无已提交报告。草稿报告需尽快完成提交。",
            "heading": "总体情况",
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
                "name": "已归档报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本期包含1份风险报告和1份明日计划报告，表明员工已识别潜在问题并有明日工作安排，但需关注风险报告的具体跟进与落实。",
            "heading": "风险与明日计划",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              }
            ]
          }
        ],
        "tool_error": "",
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
          "query_report_source_data",
          "员工日报表（employee_daily_summary）"
        ],
        "recommendations": [
          "督促草稿报告尽快提交归档。",
          "对风险报告内容进行确认，必要时启动风险应对措施。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 150,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:28:23"
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
  "url": "/api/v1/reports/95/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 187,
      "report_id": 95,
      "export_type": "word",
      "file_name": "RP-20260611092822-13276a5c.docx",
      "file_path": "storage\\reports\\RP-20260611092822-13276a5c.docx",
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
  "url": "/api/v1/reports/exports/187/download",
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
    "content-length": "37229",
    "content-disposition": "attachment; filename=\"RP-20260611092822-13276a5c.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 37229,
    "sha256": "cdb86fbef51eb25e1e93585eae8bcc8bc754454614291f95efed2260ee80372f",
    "first_16_bytes_hex": "504b03041400000008008b4bcb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/95/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 188,
      "report_id": 95,
      "export_type": "pdf",
      "file_name": "RP-20260611092822-13276a5c.pdf",
      "file_path": "storage\\reports\\RP-20260611092822-13276a5c.pdf",
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
  "url": "/api/v1/reports/exports/188/download",
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
    "content-length": "4126",
    "content-disposition": "attachment; filename=\"RP-20260611092822-13276a5c.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 4126,
    "sha256": "38093d7e240df047748cc38fc0c04c5a7ba824cd3bf800152ab53edabcaba93b",
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
  "status_code": 200,
  "headers": {
    "content-length": "2165",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 151,
      "draft_no": "DR-20260611092832-bc5d681c",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本周存在2份风险报告，占总提交数的50%，需及时跟进处理。"
        ],
        "title": "员工日报周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）共收到4份员工日报，涉及2名员工。其中2份已提交、1份归档、1份草稿。风险报告2份，需重点关注。",
        "sections": [
          {
            "content": "本周期内部门ID为10的员工共提交了4份日报，参与员工2人。日报状态分布为：已提交2份、已归档1份、草稿1份。每日提交趋势显示6月1日和6月2日各有2份日报提交。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总提交数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
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
              }
            ]
          },
          {
            "content": "本周存在2份风险报告，占提交总量的50%。每日提交量集中在周一（6月1日）和周二（6月2日），后续无新增提交。建议关注风险报告的后续处理。",
            "heading": "风险报告与趋势",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "2026-06-01提交数",
                "value": "2"
              },
              {
                "name": "2026-06-02提交数",
                "value": "2"
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
          "distinct_employees": 2
        },
        "source_refs": [
          "query_report_source_data：employee_daily_reports 表，筛选部门ID=10，日期范围2026-06-01至2026-06-07，不按负责人筛选。"
        ],
        "recommendations": [
          "建议对风险报告逐条复盘，记录解决方案。",
          "鼓励未提交日报的员工按时完成提交。"
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
  "url": "/api/v1/reports/drafts/151/confirm",
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
    "content-length": "2329",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 96,
      "report_no": "RP-20260611092832-5fe7d66f",
      "report_type": "employee_weekly_summary",
      "title": "员工日报周报（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本周存在2份风险报告，占总提交数的50%，需及时跟进处理。"
        ],
        "title": "员工日报周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）共收到4份员工日报，涉及2名员工。其中2份已提交、1份归档、1份草稿。风险报告2份，需重点关注。",
        "sections": [
          {
            "content": "本周期内部门ID为10的员工共提交了4份日报，参与员工2人。日报状态分布为：已提交2份、已归档1份、草稿1份。每日提交趋势显示6月1日和6月2日各有2份日报提交。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总提交数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
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
              }
            ]
          },
          {
            "content": "本周存在2份风险报告，占提交总量的50%。每日提交量集中在周一（6月1日）和周二（6月2日），后续无新增提交。建议关注风险报告的后续处理。",
            "heading": "风险报告与趋势",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "2026-06-01提交数",
                "value": "2"
              },
              {
                "name": "2026-06-02提交数",
                "value": "2"
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
          "distinct_employees": 2
        },
        "source_refs": [
          "query_report_source_data：employee_daily_reports 表，筛选部门ID=10，日期范围2026-06-01至2026-06-07，不按负责人筛选。"
        ],
        "recommendations": [
          "建议对风险报告逐条复盘，记录解决方案。",
          "鼓励未提交日报的员工按时完成提交。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 151,
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
  "url": "/api/v1/reports/96/publish",
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
    "content-length": "2345",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 96,
      "report_no": "RP-20260611092832-5fe7d66f",
      "report_type": "employee_weekly_summary",
      "title": "员工日报周报（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "本周存在2份风险报告，占总提交数的50%，需及时跟进处理。"
        ],
        "title": "员工日报周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）共收到4份员工日报，涉及2名员工。其中2份已提交、1份归档、1份草稿。风险报告2份，需重点关注。",
        "sections": [
          {
            "content": "本周期内部门ID为10的员工共提交了4份日报，参与员工2人。日报状态分布为：已提交2份、已归档1份、草稿1份。每日提交趋势显示6月1日和6月2日各有2份日报提交。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总提交数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
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
              }
            ]
          },
          {
            "content": "本周存在2份风险报告，占提交总量的50%。每日提交量集中在周一（6月1日）和周二（6月2日），后续无新增提交。建议关注风险报告的后续处理。",
            "heading": "风险报告与趋势",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "2026-06-01提交数",
                "value": "2"
              },
              {
                "name": "2026-06-02提交数",
                "value": "2"
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
          "distinct_employees": 2
        },
        "source_refs": [
          "query_report_source_data：employee_daily_reports 表，筛选部门ID=10，日期范围2026-06-01至2026-06-07，不按负责人筛选。"
        ],
        "recommendations": [
          "建议对风险报告逐条复盘，记录解决方案。",
          "鼓励未提交日报的员工按时完成提交。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 151,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:28:33"
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
  "url": "/api/v1/reports/96/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 189,
      "report_id": 96,
      "export_type": "word",
      "file_name": "RP-20260611092832-5fe7d66f.docx",
      "file_path": "storage\\reports\\RP-20260611092832-5fe7d66f.docx",
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
  "url": "/api/v1/reports/exports/189/download",
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
    "content-length": "37350",
    "content-disposition": "attachment; filename=\"RP-20260611092832-5fe7d66f.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 37350,
    "sha256": "b9719aa3b35aa2a144f3c1348d986ab1cd83a785b6663d4536aa9ca709526df6",
    "first_16_bytes_hex": "504b0304140000000800904bcb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/96/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 190,
      "report_id": 96,
      "export_type": "pdf",
      "file_name": "RP-20260611092832-5fe7d66f.pdf",
      "file_path": "storage\\reports\\RP-20260611092832-5fe7d66f.pdf",
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
  "url": "/api/v1/reports/exports/190/download",
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
    "content-length": "4883",
    "content-disposition": "attachment; filename=\"RP-20260611092832-5fe7d66f.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 4883,
    "sha256": "4cc041547c1d5c359def9c6a36b3dc8c3dfc9bd19307ffdb92dd9d8289eae0e7",
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
    "content-length": "2578",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 152,
      "draft_no": "DR-20260611092841-06eac985",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "平均情绪得分59.0偏低，可能存在普遍情绪困扰",
          "1条高风险预警尚未处理，需尽快安排心理干预"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共采集2份学生心理档案，平均情绪得分为59.0，整体情绪状态偏低。共产生2条预警，其中高风险预警1条，中风险1条，待处理预警1条，需重点关注。",
        "sections": [
          {
            "content": "本周部门10共有2份学生心理档案，风险等级分布为高风险1人、低风险1人。情绪标签分布为焦虑1人、稳定1人。平均情绪得分为59.0，处于偏低水平，需持续关注学生情绪状态。",
            "heading": "心理档案概况",
            "metrics": [
              {
                "name": "总档案数",
                "value": "2"
              },
              {
                "name": "平均情绪得分",
                "value": "59.0"
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
                "name": "焦虑标签人数",
                "value": "1"
              },
              {
                "name": "稳定标签人数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周共产生2条预警，其中1条为高风险，1条为中风险。预警状态方面，1条待处理，1条已解决。待处理高风险预警需尽快跟进干预，避免风险升级。",
            "heading": "预警分析",
            "metrics": [
              {
                "name": "总预警数",
                "value": "2"
              },
              {
                "name": "待处理预警数",
                "value": "1"
              },
              {
                "name": "已解决预警数",
                "value": "1"
              },
              {
                "name": "高风险预警数",
                "value": "1"
              },
              {
                "name": "中风险预警数",
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
          "数据来源：query_report_source_data",
          "数据表：学生心理档案表、预警表",
          "口径说明：风险等级、情绪标签、预警统计均基于所选时段和部门"
        ],
        "recommendations": [
          "对高风险学生安排一对一心理辅导",
          "开展情绪管理团体活动，提升整体情绪水平",
          "定期追踪待处理预警状态，确保闭环"
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
  "url": "/api/v1/reports/drafts/152/confirm",
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
    "content-length": "2753",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 97,
      "report_no": "RP-20260611092841-540a0fc6",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "平均情绪得分59.0偏低，可能存在普遍情绪困扰",
          "1条高风险预警尚未处理，需尽快安排心理干预"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共采集2份学生心理档案，平均情绪得分为59.0，整体情绪状态偏低。共产生2条预警，其中高风险预警1条，中风险1条，待处理预警1条，需重点关注。",
        "sections": [
          {
            "content": "本周部门10共有2份学生心理档案，风险等级分布为高风险1人、低风险1人。情绪标签分布为焦虑1人、稳定1人。平均情绪得分为59.0，处于偏低水平，需持续关注学生情绪状态。",
            "heading": "心理档案概况",
            "metrics": [
              {
                "name": "总档案数",
                "value": "2"
              },
              {
                "name": "平均情绪得分",
                "value": "59.0"
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
                "name": "焦虑标签人数",
                "value": "1"
              },
              {
                "name": "稳定标签人数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周共产生2条预警，其中1条为高风险，1条为中风险。预警状态方面，1条待处理，1条已解决。待处理高风险预警需尽快跟进干预，避免风险升级。",
            "heading": "预警分析",
            "metrics": [
              {
                "name": "总预警数",
                "value": "2"
              },
              {
                "name": "待处理预警数",
                "value": "1"
              },
              {
                "name": "已解决预警数",
                "value": "1"
              },
              {
                "name": "高风险预警数",
                "value": "1"
              },
              {
                "name": "中风险预警数",
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
          "数据来源：query_report_source_data",
          "数据表：学生心理档案表、预警表",
          "口径说明：风险等级、情绪标签、预警统计均基于所选时段和部门"
        ],
        "recommendations": [
          "对高风险学生安排一对一心理辅导",
          "开展情绪管理团体活动，提升整体情绪水平",
          "定期追踪待处理预警状态，确保闭环"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 152,
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
  "url": "/api/v1/reports/97/publish",
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
    "content-length": "2769",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 97,
      "report_no": "RP-20260611092841-540a0fc6",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "平均情绪得分59.0偏低，可能存在普遍情绪困扰",
          "1条高风险预警尚未处理，需尽快安排心理干预"
        ],
        "title": "学生心理健康周报（2026-06-01 至 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共采集2份学生心理档案，平均情绪得分为59.0，整体情绪状态偏低。共产生2条预警，其中高风险预警1条，中风险1条，待处理预警1条，需重点关注。",
        "sections": [
          {
            "content": "本周部门10共有2份学生心理档案，风险等级分布为高风险1人、低风险1人。情绪标签分布为焦虑1人、稳定1人。平均情绪得分为59.0，处于偏低水平，需持续关注学生情绪状态。",
            "heading": "心理档案概况",
            "metrics": [
              {
                "name": "总档案数",
                "value": "2"
              },
              {
                "name": "平均情绪得分",
                "value": "59.0"
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
                "name": "焦虑标签人数",
                "value": "1"
              },
              {
                "name": "稳定标签人数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周共产生2条预警，其中1条为高风险，1条为中风险。预警状态方面，1条待处理，1条已解决。待处理高风险预警需尽快跟进干预，避免风险升级。",
            "heading": "预警分析",
            "metrics": [
              {
                "name": "总预警数",
                "value": "2"
              },
              {
                "name": "待处理预警数",
                "value": "1"
              },
              {
                "name": "已解决预警数",
                "value": "1"
              },
              {
                "name": "高风险预警数",
                "value": "1"
              },
              {
                "name": "中风险预警数",
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
          "数据来源：query_report_source_data",
          "数据表：学生心理档案表、预警表",
          "口径说明：风险等级、情绪标签、预警统计均基于所选时段和部门"
        ],
        "recommendations": [
          "对高风险学生安排一对一心理辅导",
          "开展情绪管理团体活动，提升整体情绪水平",
          "定期追踪待处理预警状态，确保闭环"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 152,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T09:28:42"
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
  "url": "/api/v1/reports/97/exports",
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
    "content-length": "250",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 191,
      "report_id": 97,
      "export_type": "word",
      "file_name": "RP-20260611092841-540a0fc6.docx",
      "file_path": "storage\\reports\\RP-20260611092841-540a0fc6.docx",
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
  "url": "/api/v1/reports/exports/191/download",
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
    "content-length": "37454",
    "content-disposition": "attachment; filename=\"RP-20260611092841-540a0fc6.docx\"",
    "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "binary": {
    "size_bytes": 37454,
    "sha256": "2bd7a7f6f0fd0778886576103a5e26105bf43b395f761853b3c056257b17826a",
    "first_16_bytes_hex": "504b0304140000000800944bcb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/97/exports",
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
    "content-length": "247",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 192,
      "report_id": 97,
      "export_type": "pdf",
      "file_name": "RP-20260611092841-540a0fc6.pdf",
      "file_path": "storage\\reports\\RP-20260611092841-540a0fc6.pdf",
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
  "url": "/api/v1/reports/exports/192/download",
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
    "content-length": "4988",
    "content-disposition": "attachment; filename=\"RP-20260611092841-540a0fc6.pdf\"",
    "content-type": "application/pdf"
  },
  "binary": {
    "size_bytes": 4988,
    "sha256": "2e907e804898d72262edd0cf8ad379990aad392c1c5fd1fec6d41f10a5a6050f",
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
  "ai_draft": 152,
  "ai_report": 97,
  "report_export_record": 192,
  "audit_log": 730,
  "ai_tool_call_log": 153
}
```

### 阶段结论

- 结果：通过

