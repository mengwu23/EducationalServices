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

- 执行时间：`2026-06-10 22:39:32`
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
      "id": 133,
      "draft_no": "DR-20260610223932-4100817c",
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
  "url": "/api/v1/reports/drafts/133/confirm",
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
      "id": 78,
      "report_no": "RP-20260610223932-410073b1",
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
      "source_draft_id": 133,
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
  "url": "/api/v1/reports/78/publish",
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
      "id": 78,
      "report_no": "RP-20260610223932-410073b1",
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
      "source_draft_id": 133,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:39:33"
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
  "url": "/api/v1/reports/78/exports",
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
      "id": 153,
      "report_id": 78,
      "export_type": "word",
      "file_name": "RP-20260610223932-410073b1.docx",
      "file_path": "storage\\reports\\RP-20260610223932-410073b1.docx",
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
  "url": "/api/v1/reports/exports/153/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223932-410073b1.docx\"",
    "content-length": "36909"
  },
  "binary": {
    "size_bytes": 36909,
    "sha256": "3daeecf96eb51d40da0234acddbcf7f6f25e288e511346a82e917eef0697df72",
    "first_16_bytes_hex": "504b0304140000000800f0b4ca5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/78/exports",
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
      "id": 154,
      "report_id": 78,
      "export_type": "pdf",
      "file_name": "RP-20260610223932-410073b1.pdf",
      "file_path": "storage\\reports\\RP-20260610223932-410073b1.pdf",
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
  "url": "/api/v1/reports/exports/154/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223932-410073b1.pdf\"",
    "content-length": "3480"
  },
  "binary": {
    "size_bytes": 3480,
    "sha256": "d8e7a3bef91c97c442f88a1900b9ad47a2789cb0dcfda63a2159279c26d27ff4",
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
      "id": 134,
      "draft_no": "DR-20260610223932-a81a61e9",
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
  "url": "/api/v1/reports/drafts/134/confirm",
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
      "id": 79,
      "report_no": "RP-20260610223933-e7a15b3d",
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
      "source_draft_id": 134,
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
  "url": "/api/v1/reports/79/publish",
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
      "id": 79,
      "report_no": "RP-20260610223933-e7a15b3d",
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
      "source_draft_id": 134,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:39:33"
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
  "url": "/api/v1/reports/79/exports",
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
      "id": 155,
      "report_id": 79,
      "export_type": "word",
      "file_name": "RP-20260610223933-e7a15b3d.docx",
      "file_path": "storage\\reports\\RP-20260610223933-e7a15b3d.docx",
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
  "url": "/api/v1/reports/exports/155/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223933-e7a15b3d.docx\"",
    "content-length": "36951"
  },
  "binary": {
    "size_bytes": 36951,
    "sha256": "c87d5b382e78dda7cad4db894c14fc7dbcb673b28baf4b8ff341396dc5754115",
    "first_16_bytes_hex": "504b0304140000000800f0b4ca5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/79/exports",
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
      "id": 156,
      "report_id": 79,
      "export_type": "pdf",
      "file_name": "RP-20260610223933-e7a15b3d.pdf",
      "file_path": "storage\\reports\\RP-20260610223933-e7a15b3d.pdf",
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
  "url": "/api/v1/reports/exports/156/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223933-e7a15b3d.pdf\"",
    "content-length": "3509"
  },
  "binary": {
    "size_bytes": 3509,
    "sha256": "203675b0ad234dbcfa26d6bd408743932b38681591d2442dfb2ee605a222ebeb",
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
      "id": 135,
      "draft_no": "DR-20260610223933-8f3abc83",
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
  "url": "/api/v1/reports/drafts/135/confirm",
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
      "id": 80,
      "report_no": "RP-20260610223933-ce2d2867",
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
      "source_draft_id": 135,
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
  "url": "/api/v1/reports/80/publish",
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
      "id": 80,
      "report_no": "RP-20260610223933-ce2d2867",
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
      "source_draft_id": 135,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:39:33"
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
  "url": "/api/v1/reports/80/exports",
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
      "id": 157,
      "report_id": 80,
      "export_type": "word",
      "file_name": "RP-20260610223933-ce2d2867.docx",
      "file_path": "storage\\reports\\RP-20260610223933-ce2d2867.docx",
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
  "url": "/api/v1/reports/exports/157/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223933-ce2d2867.docx\"",
    "content-length": "36966"
  },
  "binary": {
    "size_bytes": 36966,
    "sha256": "4d15a80e7c51987e2b3557dbd9c0283b43f08ab32655a3bb74e1fe805bc4ea34",
    "first_16_bytes_hex": "504b0304140000000800f0b4ca5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/80/exports",
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
      "id": 158,
      "report_id": 80,
      "export_type": "pdf",
      "file_name": "RP-20260610223933-ce2d2867.pdf",
      "file_path": "storage\\reports\\RP-20260610223933-ce2d2867.pdf",
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
  "url": "/api/v1/reports/exports/158/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223933-ce2d2867.pdf\"",
    "content-length": "3711"
  },
  "binary": {
    "size_bytes": 3711,
    "sha256": "8e457e9f6505c09f10d63f6dbab7334e6c8863efdc0b6c5f6399c1f9e08f99bf",
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
      "id": 136,
      "draft_no": "DR-20260610223933-57f8ad19",
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
  "url": "/api/v1/reports/drafts/136/confirm",
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
      "id": 81,
      "report_no": "RP-20260610223933-ad3841d6",
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
      "source_draft_id": 136,
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
  "url": "/api/v1/reports/81/publish",
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
      "id": 81,
      "report_no": "RP-20260610223933-ad3841d6",
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
      "source_draft_id": 136,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:39:34"
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
  "url": "/api/v1/reports/81/exports",
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
      "id": 159,
      "report_id": 81,
      "export_type": "word",
      "file_name": "RP-20260610223933-ad3841d6.docx",
      "file_path": "storage\\reports\\RP-20260610223933-ad3841d6.docx",
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
  "url": "/api/v1/reports/exports/159/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223933-ad3841d6.docx\"",
    "content-length": "37001"
  },
  "binary": {
    "size_bytes": 37001,
    "sha256": "b95a80b4e47b09062f600b3eb695c187467151768f7aae8869b1709e8155c1b9",
    "first_16_bytes_hex": "504b0304140000000800f0b4ca5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/81/exports",
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
      "id": 160,
      "report_id": 81,
      "export_type": "pdf",
      "file_name": "RP-20260610223933-ad3841d6.pdf",
      "file_path": "storage\\reports\\RP-20260610223933-ad3841d6.pdf",
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
  "url": "/api/v1/reports/exports/160/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223933-ad3841d6.pdf\"",
    "content-length": "3784"
  },
  "binary": {
    "size_bytes": 3784,
    "sha256": "cc9da0bfc694ff63e90c619f0685262a2904eae6e4803718a61ca8ad77145553",
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
      "id": 137,
      "draft_no": "DR-20260610223933-c75e2deb",
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
  "url": "/api/v1/reports/drafts/137/confirm",
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
      "id": 82,
      "report_no": "RP-20260610223934-928611a0",
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
      "source_draft_id": 137,
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
  "url": "/api/v1/reports/82/publish",
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
      "id": 82,
      "report_no": "RP-20260610223934-928611a0",
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
      "source_draft_id": 137,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:39:34"
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
  "url": "/api/v1/reports/82/exports",
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
      "id": 161,
      "report_id": 82,
      "export_type": "word",
      "file_name": "RP-20260610223934-928611a0.docx",
      "file_path": "storage\\reports\\RP-20260610223934-928611a0.docx",
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
  "url": "/api/v1/reports/exports/161/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223934-928611a0.docx\"",
    "content-length": "37046"
  },
  "binary": {
    "size_bytes": 37046,
    "sha256": "e954ff3ff43d460f807b601e37802a674bdd576fcde3b3de3722ee9a952a069b",
    "first_16_bytes_hex": "504b0304140000000800f1b4ca5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/82/exports",
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
      "id": 162,
      "report_id": 82,
      "export_type": "pdf",
      "file_name": "RP-20260610223934-928611a0.pdf",
      "file_path": "storage\\reports\\RP-20260610223934-928611a0.pdf",
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
  "url": "/api/v1/reports/exports/162/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223934-928611a0.pdf\"",
    "content-length": "3864"
  },
  "binary": {
    "size_bytes": 3864,
    "sha256": "17c29adf65cfd50104db0330da8db2044dac884ba53a762a3a1692240ab2ff58",
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
  "ai_draft": 137,
  "ai_report": 82,
  "report_export_record": 162,
  "audit_log": 625,
  "ai_tool_call_log": 128
}
```

### 阶段结论

- 结果：通过


## real-dify 阶段

- 执行时间：`2026-06-10 22:39:38`
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
    "content-length": "1756",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 138,
      "draft_no": "DR-20260610223950-a40056e0",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共收到投诉工单3件，其中待处理1件、处理中1件、已解决1件。",
        "sections": [
          {
            "content": "本周投诉工单总计3件，各状态分布均匀。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总工单数",
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
            "content": "待处理、处理中、已解决各占三分之一，需关注待处理工单的及时响应与处理中工单的推进。",
            "heading": "工单状态分布",
            "metrics": [
              {
                "name": "待处理占比",
                "value": "33.33%"
              },
              {
                "name": "处理中占比",
                "value": "33.33%"
              },
              {
                "name": "已解决占比",
                "value": "33.33%"
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
          "数据来源：query_report_source_data，投诉工单表（complaint_tickets），口径说明：工单状态按系统定义（pending=待处理，processing=处理中，resolved=已解决）。"
        ],
        "recommendations": [
          "建议优先处理待处理的1件工单，避免超时；同时跟进处理中的工单，确保按时结案。"
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
  "url": "/api/v1/reports/drafts/138/confirm",
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
    "content-length": "1927",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 83,
      "report_no": "RP-20260610223950-d9c4b6db",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共收到投诉工单3件，其中待处理1件、处理中1件、已解决1件。",
        "sections": [
          {
            "content": "本周投诉工单总计3件，各状态分布均匀。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总工单数",
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
            "content": "待处理、处理中、已解决各占三分之一，需关注待处理工单的及时响应与处理中工单的推进。",
            "heading": "工单状态分布",
            "metrics": [
              {
                "name": "待处理占比",
                "value": "33.33%"
              },
              {
                "name": "处理中占比",
                "value": "33.33%"
              },
              {
                "name": "已解决占比",
                "value": "33.33%"
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
          "数据来源：query_report_source_data，投诉工单表（complaint_tickets），口径说明：工单状态按系统定义（pending=待处理，processing=处理中，resolved=已解决）。"
        ],
        "recommendations": [
          "建议优先处理待处理的1件工单，避免超时；同时跟进处理中的工单，确保按时结案。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 138,
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
  "url": "/api/v1/reports/83/publish",
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
    "content-length": "1943",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 83,
      "report_no": "RP-20260610223950-d9c4b6db",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共收到投诉工单3件，其中待处理1件、处理中1件、已解决1件。",
        "sections": [
          {
            "content": "本周投诉工单总计3件，各状态分布均匀。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总工单数",
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
            "content": "待处理、处理中、已解决各占三分之一，需关注待处理工单的及时响应与处理中工单的推进。",
            "heading": "工单状态分布",
            "metrics": [
              {
                "name": "待处理占比",
                "value": "33.33%"
              },
              {
                "name": "处理中占比",
                "value": "33.33%"
              },
              {
                "name": "已解决占比",
                "value": "33.33%"
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
          "数据来源：query_report_source_data，投诉工单表（complaint_tickets），口径说明：工单状态按系统定义（pending=待处理，processing=处理中，resolved=已解决）。"
        ],
        "recommendations": [
          "建议优先处理待处理的1件工单，避免超时；同时跟进处理中的工单，确保按时结案。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 138,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:39:51"
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
  "url": "/api/v1/reports/83/exports",
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
      "id": 163,
      "report_id": 83,
      "export_type": "word",
      "file_name": "RP-20260610223950-d9c4b6db.docx",
      "file_path": "storage\\reports\\RP-20260610223950-d9c4b6db.docx",
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
  "url": "/api/v1/reports/exports/163/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223950-d9c4b6db.docx\"",
    "content-length": "37181"
  },
  "binary": {
    "size_bytes": 37181,
    "sha256": "eedaef407d9cccccc951750e9999e3b62a04c4ff8a6c3b8753dc8d5d1f6b413b",
    "first_16_bytes_hex": "504b0304140000000800f9b4ca5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/83/exports",
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
      "id": 164,
      "report_id": 83,
      "export_type": "pdf",
      "file_name": "RP-20260610223950-d9c4b6db.pdf",
      "file_path": "storage\\reports\\RP-20260610223950-d9c4b6db.pdf",
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
  "url": "/api/v1/reports/exports/164/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610223950-d9c4b6db.pdf\"",
    "content-length": "4030"
  },
  "binary": {
    "size_bytes": 4030,
    "sha256": "825b57b1d3a916347f41d2170e4fd3ef1d5aa9c9700caa197d8c156de709dd8c",
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
    "content-length": "1798",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 139,
      "draft_no": "DR-20260610224000-39d7b7a1",
      "status": "pending_confirm",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期部门10负责人102共新增线索2条，完成客户分析2次，活动报名2次。整体运营指标偏低，需加强各环节推进。",
        "sections": [
          {
            "content": "本周期新增线索2条，客户分析记录2次，表明对现有客户进行了跟进分析，但线索量有限，转化效率待提升。",
            "heading": "客户获取与转化",
            "metrics": [
              {
                "name": "新增线索",
                "value": "2"
              },
              {
                "name": "客户分析记录",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周期活动报名2次，参与度较低，需加强活动推广力度和吸引力。",
            "heading": "活动运营",
            "metrics": [
              {
                "name": "活动报名次数",
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
          "数据来源：query_report_source_data 接口",
          "口径说明：新增线索来自 customer_leads 表，客户分析来自 customer_analysis 表，活动报名来自 event_registrations 表，统计周期2026-06-01至2026-06-07，部门ID=10，负责人ID=102"
        ],
        "recommendations": [
          "建议加大线索获取投入，拓展获客渠道",
          "提高客户分析频率，深入挖掘客户需求",
          "策划更多高吸引力活动，提升报名参与率"
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
  "url": "/api/v1/reports/drafts/139/confirm",
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
    "content-length": "1979",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 84,
      "report_no": "RP-20260610224000-a9d5fb85",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 ~ 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期部门10负责人102共新增线索2条，完成客户分析2次，活动报名2次。整体运营指标偏低，需加强各环节推进。",
        "sections": [
          {
            "content": "本周期新增线索2条，客户分析记录2次，表明对现有客户进行了跟进分析，但线索量有限，转化效率待提升。",
            "heading": "客户获取与转化",
            "metrics": [
              {
                "name": "新增线索",
                "value": "2"
              },
              {
                "name": "客户分析记录",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周期活动报名2次，参与度较低，需加强活动推广力度和吸引力。",
            "heading": "活动运营",
            "metrics": [
              {
                "name": "活动报名次数",
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
          "数据来源：query_report_source_data 接口",
          "口径说明：新增线索来自 customer_leads 表，客户分析来自 customer_analysis 表，活动报名来自 event_registrations 表，统计周期2026-06-01至2026-06-07，部门ID=10，负责人ID=102"
        ],
        "recommendations": [
          "建议加大线索获取投入，拓展获客渠道",
          "提高客户分析频率，深入挖掘客户需求",
          "策划更多高吸引力活动，提升报名参与率"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 139,
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
  "url": "/api/v1/reports/84/publish",
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
    "content-length": "1995",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 84,
      "report_no": "RP-20260610224000-a9d5fb85",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01 ~ 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [],
        "title": "全域客户经营分析报告（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期部门10负责人102共新增线索2条，完成客户分析2次，活动报名2次。整体运营指标偏低，需加强各环节推进。",
        "sections": [
          {
            "content": "本周期新增线索2条，客户分析记录2次，表明对现有客户进行了跟进分析，但线索量有限，转化效率待提升。",
            "heading": "客户获取与转化",
            "metrics": [
              {
                "name": "新增线索",
                "value": "2"
              },
              {
                "name": "客户分析记录",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周期活动报名2次，参与度较低，需加强活动推广力度和吸引力。",
            "heading": "活动运营",
            "metrics": [
              {
                "name": "活动报名次数",
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
          "数据来源：query_report_source_data 接口",
          "口径说明：新增线索来自 customer_leads 表，客户分析来自 customer_analysis 表，活动报名来自 event_registrations 表，统计周期2026-06-01至2026-06-07，部门ID=10，负责人ID=102"
        ],
        "recommendations": [
          "建议加大线索获取投入，拓展获客渠道",
          "提高客户分析频率，深入挖掘客户需求",
          "策划更多高吸引力活动，提升报名参与率"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 139,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:40:01"
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
  "url": "/api/v1/reports/84/exports",
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
      "id": 165,
      "report_id": 84,
      "export_type": "word",
      "file_name": "RP-20260610224000-a9d5fb85.docx",
      "file_path": "storage\\reports\\RP-20260610224000-a9d5fb85.docx",
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
  "url": "/api/v1/reports/exports/165/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224000-a9d5fb85.docx\"",
    "content-length": "37289"
  },
  "binary": {
    "size_bytes": 37289,
    "sha256": "770b2151b060c5a5d2ccd54ab662381f6a27c70a2c2e50b8996578753f84d69e",
    "first_16_bytes_hex": "504b030414000000080000b5ca5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/84/exports",
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
      "id": 166,
      "report_id": 84,
      "export_type": "pdf",
      "file_name": "RP-20260610224000-a9d5fb85.pdf",
      "file_path": "storage\\reports\\RP-20260610224000-a9d5fb85.pdf",
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
  "url": "/api/v1/reports/exports/166/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224000-a9d5fb85.pdf\"",
    "content-length": "3959"
  },
  "binary": {
    "size_bytes": 3959,
    "sha256": "95fe0d26546dd589f412c5b03f05de73959aa4911504b98b1c0fb4f33deaa993",
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
    "content-length": "1922",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 140,
      "draft_no": "DR-20260610224007-fbb3e6d9",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在1份含风险提示的日报，需进一步确认具体内容及应对措施。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月2日，部门10共提交2份员工日报，其中草稿1份，归档1份。存在1份含风险提示的日报，并有1份包含明日计划。",
        "sections": [
          {
            "content": "截至当日，部门10共收到2份员工日报。已提交0份，草稿1份，归档1份。提交率为0%。",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "总日报数",
                "value": "2"
              },
              {
                "name": "已提交日报",
                "value": "0"
              },
              {
                "name": "草稿日报",
                "value": "1"
              },
              {
                "name": "归档日报",
                "value": "1"
              }
            ]
          },
          {
            "content": "所有日报中，有1份标记了风险内容，1份包含明日工作计划。建议关注风险日报的后续处理。",
            "heading": "风险与计划情况",
            "metrics": [
              {
                "name": "含风险日报数",
                "value": "1"
              },
              {
                "name": "含明日计划日报数",
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
          "query_report_source_data 表：employee_daily_summary，口径：统计当日部门10所有状态日报，不含删除数据。"
        ],
        "recommendations": [
          "建议部门负责人审阅风险日报并跟进处理方案。",
          "鼓励员工提前提交日报以避免草稿滞留。"
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
  "url": "/api/v1/reports/drafts/140/confirm",
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
    "content-length": "2080",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 85,
      "report_no": "RP-20260610224007-71f9db43",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在1份含风险提示的日报，需进一步确认具体内容及应对措施。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月2日，部门10共提交2份员工日报，其中草稿1份，归档1份。存在1份含风险提示的日报，并有1份包含明日计划。",
        "sections": [
          {
            "content": "截至当日，部门10共收到2份员工日报。已提交0份，草稿1份，归档1份。提交率为0%。",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "总日报数",
                "value": "2"
              },
              {
                "name": "已提交日报",
                "value": "0"
              },
              {
                "name": "草稿日报",
                "value": "1"
              },
              {
                "name": "归档日报",
                "value": "1"
              }
            ]
          },
          {
            "content": "所有日报中，有1份标记了风险内容，1份包含明日工作计划。建议关注风险日报的后续处理。",
            "heading": "风险与计划情况",
            "metrics": [
              {
                "name": "含风险日报数",
                "value": "1"
              },
              {
                "name": "含明日计划日报数",
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
          "query_report_source_data 表：employee_daily_summary，口径：统计当日部门10所有状态日报，不含删除数据。"
        ],
        "recommendations": [
          "建议部门负责人审阅风险日报并跟进处理方案。",
          "鼓励员工提前提交日报以避免草稿滞留。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 140,
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
  "url": "/api/v1/reports/85/publish",
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
    "content-length": "2096",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 85,
      "report_no": "RP-20260610224007-71f9db43",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "published",
      "content_json": {
        "risks": [
          "存在1份含风险提示的日报，需进一步确认具体内容及应对措施。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月2日，部门10共提交2份员工日报，其中草稿1份，归档1份。存在1份含风险提示的日报，并有1份包含明日计划。",
        "sections": [
          {
            "content": "截至当日，部门10共收到2份员工日报。已提交0份，草稿1份，归档1份。提交率为0%。",
            "heading": "日报提交概览",
            "metrics": [
              {
                "name": "总日报数",
                "value": "2"
              },
              {
                "name": "已提交日报",
                "value": "0"
              },
              {
                "name": "草稿日报",
                "value": "1"
              },
              {
                "name": "归档日报",
                "value": "1"
              }
            ]
          },
          {
            "content": "所有日报中，有1份标记了风险内容，1份包含明日工作计划。建议关注风险日报的后续处理。",
            "heading": "风险与计划情况",
            "metrics": [
              {
                "name": "含风险日报数",
                "value": "1"
              },
              {
                "name": "含明日计划日报数",
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
          "query_report_source_data 表：employee_daily_summary，口径：统计当日部门10所有状态日报，不含删除数据。"
        ],
        "recommendations": [
          "建议部门负责人审阅风险日报并跟进处理方案。",
          "鼓励员工提前提交日报以避免草稿滞留。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 140,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:40:07"
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
  "url": "/api/v1/reports/85/exports",
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
      "id": 167,
      "report_id": 85,
      "export_type": "word",
      "file_name": "RP-20260610224007-71f9db43.docx",
      "file_path": "storage\\reports\\RP-20260610224007-71f9db43.docx",
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
  "url": "/api/v1/reports/exports/167/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224007-71f9db43.docx\"",
    "content-length": "37269"
  },
  "binary": {
    "size_bytes": 37269,
    "sha256": "7ef045e1c5251728684ca762b54de2fafe3c4e6a896b9d5b9e46f9a43a797720",
    "first_16_bytes_hex": "504b030414000000080003b5ca5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/85/exports",
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
      "id": 168,
      "report_id": 85,
      "export_type": "pdf",
      "file_name": "RP-20260610224007-71f9db43.pdf",
      "file_path": "storage\\reports\\RP-20260610224007-71f9db43.pdf",
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
  "url": "/api/v1/reports/exports/168/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224007-71f9db43.pdf\"",
    "content-length": "4165"
  },
  "binary": {
    "size_bytes": 4165,
    "sha256": "89108613f1e8ab775d1ba89b1b3be7750d1167e6bdc287d4898c7d5c9f550ab6",
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
    "content-length": "2672",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 141,
      "draft_no": "DR-20260610224020-746aad22",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本周共有2份风险报告，占比50%，需重点关注并跟进处理。"
        ],
        "title": "员工日报汇总报告（周报）- 2026-06-01至2026-06-07",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共收集员工日报4份，由2名员工提交。其中已提交2份，已归档1份，草稿1份。风险报告2份。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门ID=10共有2名员工提交了4份日报，总提交率为2/2（全员提交）。",
            "heading": "总体情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
              }
            ]
          },
          {
            "content": "在4份日报中，已提交状态2份，已归档状态1份，草稿状态1份。其中已提交和已归档的合计3份，代表了已完成填报的报告。",
            "heading": "报告提交状态",
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
              }
            ]
          },
          {
            "content": "本周仅有2026-06-01和2026-06-02两日有提交记录，各提交2份。后续日期未出现提交行为，请关注员工是否按规定每日填报。",
            "heading": "每日提交趋势",
            "metrics": [
              {
                "name": "2026-06-01提交数",
                "value": "2"
              },
              {
                "name": "2026-06-02提交数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周共有2份日报被标记为风险报告，占报告总数的50%。请相关部门及时处理风险事项。",
            "heading": "风险报告情况",
            "metrics": [
              {
                "name": "风险报告数",
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
          "数据来源：query_report_source_data 工具，数据表为员工日报汇总表（department_id=10）。",
          "统计口径：报告周期2026-06-01至2026-06-07，不含未提交日期的默认值。",
          "状态计数基于最终提交状态，不含临时保存记录。"
        ],
        "recommendations": [
          "建议督促员工在每日规定时间内完成日报填报，避免集中某几天提交。",
          "对于草稿状态的1份报告，提醒员工尽快提交或归档。",
          "针对风险报告中的具体事项，建议相关责任人限期反馈处理进展。"
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
  "url": "/api/v1/reports/drafts/141/confirm",
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
    "content-length": "2850",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 86,
      "report_no": "RP-20260610224020-e262de8d",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周报）- 2026-06-01至2026-06-07",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本周共有2份风险报告，占比50%，需重点关注并跟进处理。"
        ],
        "title": "员工日报汇总报告（周报）- 2026-06-01至2026-06-07",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共收集员工日报4份，由2名员工提交。其中已提交2份，已归档1份，草稿1份。风险报告2份。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门ID=10共有2名员工提交了4份日报，总提交率为2/2（全员提交）。",
            "heading": "总体情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
              }
            ]
          },
          {
            "content": "在4份日报中，已提交状态2份，已归档状态1份，草稿状态1份。其中已提交和已归档的合计3份，代表了已完成填报的报告。",
            "heading": "报告提交状态",
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
              }
            ]
          },
          {
            "content": "本周仅有2026-06-01和2026-06-02两日有提交记录，各提交2份。后续日期未出现提交行为，请关注员工是否按规定每日填报。",
            "heading": "每日提交趋势",
            "metrics": [
              {
                "name": "2026-06-01提交数",
                "value": "2"
              },
              {
                "name": "2026-06-02提交数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周共有2份日报被标记为风险报告，占报告总数的50%。请相关部门及时处理风险事项。",
            "heading": "风险报告情况",
            "metrics": [
              {
                "name": "风险报告数",
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
          "数据来源：query_report_source_data 工具，数据表为员工日报汇总表（department_id=10）。",
          "统计口径：报告周期2026-06-01至2026-06-07，不含未提交日期的默认值。",
          "状态计数基于最终提交状态，不含临时保存记录。"
        ],
        "recommendations": [
          "建议督促员工在每日规定时间内完成日报填报，避免集中某几天提交。",
          "对于草稿状态的1份报告，提醒员工尽快提交或归档。",
          "针对风险报告中的具体事项，建议相关责任人限期反馈处理进展。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 141,
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
  "url": "/api/v1/reports/86/publish",
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
    "content-length": "2866",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 86,
      "report_no": "RP-20260610224020-e262de8d",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周报）- 2026-06-01至2026-06-07",
      "status": "published",
      "content_json": {
        "risks": [
          "本周共有2份风险报告，占比50%，需重点关注并跟进处理。"
        ],
        "title": "员工日报汇总报告（周报）- 2026-06-01至2026-06-07",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共收集员工日报4份，由2名员工提交。其中已提交2份，已归档1份，草稿1份。风险报告2份。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门ID=10共有2名员工提交了4份日报，总提交率为2/2（全员提交）。",
            "heading": "总体情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "提交员工数",
                "value": "2"
              }
            ]
          },
          {
            "content": "在4份日报中，已提交状态2份，已归档状态1份，草稿状态1份。其中已提交和已归档的合计3份，代表了已完成填报的报告。",
            "heading": "报告提交状态",
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
              }
            ]
          },
          {
            "content": "本周仅有2026-06-01和2026-06-02两日有提交记录，各提交2份。后续日期未出现提交行为，请关注员工是否按规定每日填报。",
            "heading": "每日提交趋势",
            "metrics": [
              {
                "name": "2026-06-01提交数",
                "value": "2"
              },
              {
                "name": "2026-06-02提交数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周共有2份日报被标记为风险报告，占报告总数的50%。请相关部门及时处理风险事项。",
            "heading": "风险报告情况",
            "metrics": [
              {
                "name": "风险报告数",
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
          "数据来源：query_report_source_data 工具，数据表为员工日报汇总表（department_id=10）。",
          "统计口径：报告周期2026-06-01至2026-06-07，不含未提交日期的默认值。",
          "状态计数基于最终提交状态，不含临时保存记录。"
        ],
        "recommendations": [
          "建议督促员工在每日规定时间内完成日报填报，避免集中某几天提交。",
          "对于草稿状态的1份报告，提醒员工尽快提交或归档。",
          "针对风险报告中的具体事项，建议相关责任人限期反馈处理进展。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 141,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:40:20"
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
  "url": "/api/v1/reports/86/exports",
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
      "id": 169,
      "report_id": 86,
      "export_type": "word",
      "file_name": "RP-20260610224020-e262de8d.docx",
      "file_path": "storage\\reports\\RP-20260610224020-e262de8d.docx",
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
  "url": "/api/v1/reports/exports/169/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224020-e262de8d.docx\"",
    "content-length": "37556"
  },
  "binary": {
    "size_bytes": 37556,
    "sha256": "d8102daf905110540c79935056b7cb07c997b5b69303fb0bc29c5380c65d3f81",
    "first_16_bytes_hex": "504b03041400000008000ab5ca5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/86/exports",
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
      "id": 170,
      "report_id": 86,
      "export_type": "pdf",
      "file_name": "RP-20260610224020-e262de8d.pdf",
      "file_path": "storage\\reports\\RP-20260610224020-e262de8d.pdf",
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
  "url": "/api/v1/reports/exports/170/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224020-e262de8d.pdf\"",
    "content-length": "5495"
  },
  "binary": {
    "size_bytes": 5495,
    "sha256": "014b9b64bd062519711e7aa8359bc3e2ae72682d018249a6e69d2c5c178e0613",
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
    "content-length": "2686",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 142,
      "draft_no": "DR-20260610224032-15702d9f",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在1条高风险的待处理预警，可能涉及学生心理危机，需立即关注。",
          "平均情绪评分59.0分，低于正常区间，整体学生心理状态需引起重视。"
        ],
        "title": "学生心理健康周报 (2026-06-01 至 2026-06-07)",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期共有2份学生心理档案，其中高风险1人、低风险1人；平均情绪评分59.0分，整体情绪偏低；共产生2条预警，其中1条待处理、1条已解决。",
        "sections": [
          {
            "content": "本周期共覆盖2份学生心理档案，风险等级分布为高风险1人、低风险1人；情绪标签分布为焦虑1人、稳定1人；平均情绪评分为59.0分，处于较低水平，需关注学生整体情绪状态。",
            "heading": "心理档案概况",
            "metrics": [
              {
                "name": "总档案数",
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
                "name": "焦虑标签人数",
                "value": "1"
              },
              {
                "name": "稳定标签人数",
                "value": "1"
              },
              {
                "name": "平均情绪评分",
                "value": "59.0"
              }
            ]
          },
          {
            "content": "本周期共产生2条预警，按状态统计：待处理1条、已解决1条；按风险等级统计：高风险1条、中风险1条。目前仍有待处理的预警，需及时跟进。",
            "heading": "预警与处理情况",
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
          "数据来源：query_report_source_data（学生心理档案表、预警表）",
          "统计口径：部门ID=10，时间范围2026-06-01至2026-06-07"
        ],
        "recommendations": [
          "立即安排心理辅导老师或班主任对接高风险预警学生，启动干预流程。",
          "对低风险学生也应进行日常关怀，防止情绪恶化。",
          "建议下周期继续跟踪预警处理进展，并关注情绪评分变化趋势。"
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
  "url": "/api/v1/reports/drafts/142/confirm",
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
    "content-length": "2858",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 87,
      "report_no": "RP-20260610224032-789df1e9",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报 (2026-06-01 至 2026-06-07)",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在1条高风险的待处理预警，可能涉及学生心理危机，需立即关注。",
          "平均情绪评分59.0分，低于正常区间，整体学生心理状态需引起重视。"
        ],
        "title": "学生心理健康周报 (2026-06-01 至 2026-06-07)",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期共有2份学生心理档案，其中高风险1人、低风险1人；平均情绪评分59.0分，整体情绪偏低；共产生2条预警，其中1条待处理、1条已解决。",
        "sections": [
          {
            "content": "本周期共覆盖2份学生心理档案，风险等级分布为高风险1人、低风险1人；情绪标签分布为焦虑1人、稳定1人；平均情绪评分为59.0分，处于较低水平，需关注学生整体情绪状态。",
            "heading": "心理档案概况",
            "metrics": [
              {
                "name": "总档案数",
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
                "name": "焦虑标签人数",
                "value": "1"
              },
              {
                "name": "稳定标签人数",
                "value": "1"
              },
              {
                "name": "平均情绪评分",
                "value": "59.0"
              }
            ]
          },
          {
            "content": "本周期共产生2条预警，按状态统计：待处理1条、已解决1条；按风险等级统计：高风险1条、中风险1条。目前仍有待处理的预警，需及时跟进。",
            "heading": "预警与处理情况",
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
          "数据来源：query_report_source_data（学生心理档案表、预警表）",
          "统计口径：部门ID=10，时间范围2026-06-01至2026-06-07"
        ],
        "recommendations": [
          "立即安排心理辅导老师或班主任对接高风险预警学生，启动干预流程。",
          "对低风险学生也应进行日常关怀，防止情绪恶化。",
          "建议下周期继续跟踪预警处理进展，并关注情绪评分变化趋势。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 142,
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
  "url": "/api/v1/reports/87/publish",
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
    "content-length": "2874",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 87,
      "report_no": "RP-20260610224032-789df1e9",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报 (2026-06-01 至 2026-06-07)",
      "status": "published",
      "content_json": {
        "risks": [
          "存在1条高风险的待处理预警，可能涉及学生心理危机，需立即关注。",
          "平均情绪评分59.0分，低于正常区间，整体学生心理状态需引起重视。"
        ],
        "title": "学生心理健康周报 (2026-06-01 至 2026-06-07)",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周期共有2份学生心理档案，其中高风险1人、低风险1人；平均情绪评分59.0分，整体情绪偏低；共产生2条预警，其中1条待处理、1条已解决。",
        "sections": [
          {
            "content": "本周期共覆盖2份学生心理档案，风险等级分布为高风险1人、低风险1人；情绪标签分布为焦虑1人、稳定1人；平均情绪评分为59.0分，处于较低水平，需关注学生整体情绪状态。",
            "heading": "心理档案概况",
            "metrics": [
              {
                "name": "总档案数",
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
                "name": "焦虑标签人数",
                "value": "1"
              },
              {
                "name": "稳定标签人数",
                "value": "1"
              },
              {
                "name": "平均情绪评分",
                "value": "59.0"
              }
            ]
          },
          {
            "content": "本周期共产生2条预警，按状态统计：待处理1条、已解决1条；按风险等级统计：高风险1条、中风险1条。目前仍有待处理的预警，需及时跟进。",
            "heading": "预警与处理情况",
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
          "数据来源：query_report_source_data（学生心理档案表、预警表）",
          "统计口径：部门ID=10，时间范围2026-06-01至2026-06-07"
        ],
        "recommendations": [
          "立即安排心理辅导老师或班主任对接高风险预警学生，启动干预流程。",
          "对低风险学生也应进行日常关怀，防止情绪恶化。",
          "建议下周期继续跟踪预警处理进展，并关注情绪评分变化趋势。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 142,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-10T22:40:32"
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
  "url": "/api/v1/reports/87/exports",
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
      "id": 171,
      "report_id": 87,
      "export_type": "word",
      "file_name": "RP-20260610224032-789df1e9.docx",
      "file_path": "storage\\reports\\RP-20260610224032-789df1e9.docx",
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
  "url": "/api/v1/reports/exports/171/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224032-789df1e9.docx\"",
    "content-length": "37508"
  },
  "binary": {
    "size_bytes": 37508,
    "sha256": "829f98c5548a8ed78f9d69a4c03c5a19c568e0f4e5916aac18176625c9926e57",
    "first_16_bytes_hex": "504b030414000000080010b5ca5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/87/exports",
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
      "id": 172,
      "report_id": 87,
      "export_type": "pdf",
      "file_name": "RP-20260610224032-789df1e9.pdf",
      "file_path": "storage\\reports\\RP-20260610224032-789df1e9.pdf",
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
  "url": "/api/v1/reports/exports/172/download",
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
    "content-disposition": "attachment; filename=\"RP-20260610224032-789df1e9.pdf\"",
    "content-length": "5031"
  },
  "binary": {
    "size_bytes": 5031,
    "sha256": "4b65d95f3496940c55b4d729d57c2ec324725df4239a31555987bd86b2738453",
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
  "ai_draft": 142,
  "ai_report": 87,
  "report_export_record": 172,
  "audit_log": 660,
  "ai_tool_call_log": 138
}
```

### 阶段结论

- 结果：通过

