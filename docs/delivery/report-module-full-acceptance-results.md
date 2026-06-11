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

- 执行时间：`2026-06-11 10:34:51`
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
      "id": 173,
      "draft_no": "DR-20260611103451-f74adfb2",
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
  "url": "/api/v1/reports/drafts/173/confirm",
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
      "id": 118,
      "report_no": "RP-20260611103451-95cff7e9",
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
      "source_draft_id": 173,
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
  "url": "/api/v1/reports/118/publish",
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
      "id": 118,
      "report_no": "RP-20260611103451-95cff7e9",
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
      "source_draft_id": 173,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:34:52"
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
  "url": "/api/v1/reports/118/exports",
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
      "id": 233,
      "report_id": 118,
      "export_type": "word",
      "file_name": "RP-20260611103451-95cff7e9.docx",
      "file_path": "storage\\reports\\RP-20260611103451-95cff7e9.docx",
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
  "url": "/api/v1/reports/exports/233/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103451-95cff7e9.docx\"",
    "content-length": "37569"
  },
  "binary": {
    "size_bytes": 37569,
    "sha256": "c12b8be7131ea85abd52c1c4288846a54937fbb7a30607479df9a618fb99b925",
    "first_16_bytes_hex": "504b03041400000008005954cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/118/exports",
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
      "id": 234,
      "report_id": 118,
      "export_type": "pdf",
      "file_name": "RP-20260611103451-95cff7e9.pdf",
      "file_path": "storage\\reports\\RP-20260611103451-95cff7e9.pdf",
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
  "url": "/api/v1/reports/exports/234/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103451-95cff7e9.pdf\"",
    "content-length": "5245"
  },
  "binary": {
    "size_bytes": 5245,
    "sha256": "5392fd54a151b2812bc0cb3ce711e999f3e758380f042d124c4ce16765692654",
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
    "content-length": "4613",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 174,
      "draft_no": "DR-20260611103451-9bb04656",
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
  "url": "/api/v1/reports/drafts/174/confirm",
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
    "content-length": "4807",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 119,
      "report_no": "RP-20260611103451-8e1f537b",
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
          "建立线索分级标准，按意向度匹配跟进强度",
          "每周复盘流失线索共性特征，沉淀流失预防 SOP",
          "将高意向客户纳入重点跟进看板，确保闭环管理"
        ]
      },
      "source_draft_id": 174,
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
  "url": "/api/v1/reports/119/publish",
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
    "content-length": "4823",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 119,
      "report_no": "RP-20260611103451-8e1f537b",
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
          "建立线索分级标准，按意向度匹配跟进强度",
          "每周复盘流失线索共性特征，沉淀流失预防 SOP",
          "将高意向客户纳入重点跟进看板，确保闭环管理"
        ]
      },
      "source_draft_id": 174,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:34:52"
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
  "url": "/api/v1/reports/119/exports",
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
      "id": 235,
      "report_id": 119,
      "export_type": "word",
      "file_name": "RP-20260611103451-8e1f537b.docx",
      "file_path": "storage\\reports\\RP-20260611103451-8e1f537b.docx",
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
  "url": "/api/v1/reports/exports/235/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103451-8e1f537b.docx\"",
    "content-length": "38390"
  },
  "binary": {
    "size_bytes": 38390,
    "sha256": "4d28a5c5df20298b6f0a20325c0ea4eeed2f35a1c7316dddb94257a4601ce3b5",
    "first_16_bytes_hex": "504b03041400000008005954cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/119/exports",
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
      "id": 236,
      "report_id": 119,
      "export_type": "pdf",
      "file_name": "RP-20260611103451-8e1f537b.pdf",
      "file_path": "storage\\reports\\RP-20260611103451-8e1f537b.pdf",
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
  "url": "/api/v1/reports/exports/236/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103451-8e1f537b.pdf\"",
    "content-length": "7105"
  },
  "binary": {
    "size_bytes": 7105,
    "sha256": "1215809c45d0dce62238fb6703ec57076afb456c50621f42000010edf7da78d6",
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
      "id": 175,
      "draft_no": "DR-20260611103452-efffacb3",
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
  "url": "/api/v1/reports/drafts/175/confirm",
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
      "id": 120,
      "report_no": "RP-20260611103452-b7554df8",
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
      "source_draft_id": 175,
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
  "url": "/api/v1/reports/120/publish",
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
      "id": 120,
      "report_no": "RP-20260611103452-b7554df8",
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
      "source_draft_id": 175,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:34:52"
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
  "url": "/api/v1/reports/120/exports",
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
      "id": 237,
      "report_id": 120,
      "export_type": "word",
      "file_name": "RP-20260611103452-b7554df8.docx",
      "file_path": "storage\\reports\\RP-20260611103452-b7554df8.docx",
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
  "url": "/api/v1/reports/exports/237/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103452-b7554df8.docx\"",
    "content-length": "37398"
  },
  "binary": {
    "size_bytes": 37398,
    "sha256": "808ae78f8d04a414df87d33a815eeada1f9845abb4fd4b47df2e0338d6e35cc4",
    "first_16_bytes_hex": "504b03041400000008005a54cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/120/exports",
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
      "id": 238,
      "report_id": 120,
      "export_type": "pdf",
      "file_name": "RP-20260611103452-b7554df8.pdf",
      "file_path": "storage\\reports\\RP-20260611103452-b7554df8.pdf",
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
  "url": "/api/v1/reports/exports/238/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103452-b7554df8.pdf\"",
    "content-length": "4948"
  },
  "binary": {
    "size_bytes": 4948,
    "sha256": "a597bdc36acde5cf9651089c9555c418aeec7df66bbd23596425e1b7af99087b",
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
      "id": 176,
      "draft_no": "DR-20260611103452-a6f80e86",
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
  "url": "/api/v1/reports/drafts/176/confirm",
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
      "id": 121,
      "report_no": "RP-20260611103452-742a328b",
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
      "source_draft_id": 176,
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
  "url": "/api/v1/reports/121/publish",
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
      "id": 121,
      "report_no": "RP-20260611103452-742a328b",
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
      "source_draft_id": 176,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:34:53"
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
  "url": "/api/v1/reports/121/exports",
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
      "id": 239,
      "report_id": 121,
      "export_type": "word",
      "file_name": "RP-20260611103452-742a328b.docx",
      "file_path": "storage\\reports\\RP-20260611103452-742a328b.docx",
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
  "url": "/api/v1/reports/exports/239/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103452-742a328b.docx\"",
    "content-length": "37558"
  },
  "binary": {
    "size_bytes": 37558,
    "sha256": "21b995deb23ad44742530715e785c85889dd68d806361fe6264193ef439df9d4",
    "first_16_bytes_hex": "504b03041400000008005a54cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/121/exports",
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
      "id": 240,
      "report_id": 121,
      "export_type": "pdf",
      "file_name": "RP-20260611103452-742a328b.pdf",
      "file_path": "storage\\reports\\RP-20260611103452-742a328b.pdf",
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
  "url": "/api/v1/reports/exports/240/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103452-742a328b.pdf\"",
    "content-length": "5222"
  },
  "binary": {
    "size_bytes": 5222,
    "sha256": "e341efc2472f4a042e0685f5817719e896b19ee0d7e81db175ffd6b5e64c2229",
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
      "id": 177,
      "draft_no": "DR-20260611103452-b49a28c6",
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
  "url": "/api/v1/reports/drafts/177/confirm",
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
      "id": 122,
      "report_no": "RP-20260611103452-40ea7224",
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
      "source_draft_id": 177,
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
  "url": "/api/v1/reports/122/publish",
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
      "id": 122,
      "report_no": "RP-20260611103452-40ea7224",
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
      "source_draft_id": 177,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:34:53"
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
  "url": "/api/v1/reports/122/exports",
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
      "id": 241,
      "report_id": 122,
      "export_type": "word",
      "file_name": "RP-20260611103452-40ea7224.docx",
      "file_path": "storage\\reports\\RP-20260611103452-40ea7224.docx",
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
  "url": "/api/v1/reports/exports/241/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103452-40ea7224.docx\"",
    "content-length": "37687"
  },
  "binary": {
    "size_bytes": 37687,
    "sha256": "a17c9bbd517b20c39e6a78691b55f2717429e3ef73b6d77c531880700fdc0233",
    "first_16_bytes_hex": "504b03041400000008005a54cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/122/exports",
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
      "id": 242,
      "report_id": 122,
      "export_type": "pdf",
      "file_name": "RP-20260611103452-40ea7224.pdf",
      "file_path": "storage\\reports\\RP-20260611103452-40ea7224.pdf",
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
  "url": "/api/v1/reports/exports/242/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103452-40ea7224.pdf\"",
    "content-length": "5736"
  },
  "binary": {
    "size_bytes": 5736,
    "sha256": "7d978e0e4c9d41d120be3983372395dc6e023ad2b5597fbc0495338b790c7feb",
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
  "ai_draft": 177,
  "ai_report": 122,
  "report_export_record": 242,
  "audit_log": 905,
  "ai_tool_call_log": 188
}
```

### 阶段结论

- 结果：通过


## real-dify 阶段

- 执行时间：`2026-06-11 10:34:57`
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
    "content-length": "2100",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 178,
      "draft_no": "DR-20260611103508-ff5dbd01",
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
        "summary": "本周（2026-06-01至2026-06-07）部门10共受理3张投诉工单，状态分布均匀（待处理、处理中、已解决各1张），平均处理时长为29.8小时。",
        "sections": [
          {
            "content": "本期共收到投诉工单3张，其中待处理1张、处理中1张、已解决1张，无重复或遗漏。平均处理时长为29.8小时，需关注时效性。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "工单总量",
                "value": 3
              },
              {
                "name": "待处理工单数",
                "value": 1
              },
              {
                "name": "处理中工单数",
                "value": 1
              },
              {
                "name": "已解决工单数",
                "value": 1
              },
              {
                "name": "平均处理时长(小时)",
                "value": 29.8
              }
            ]
          },
          {
            "content": "投诉工单按类别分为教学、服务、签证各1张，工单类型均为'投诉'，无其他类型。",
            "heading": "分类分布",
            "metrics": [
              {
                "name": "教学类工单数",
                "value": 1
              },
              {
                "name": "服务类工单数",
                "value": 1
              },
              {
                "name": "签证类工单数",
                "value": 1
              },
              {
                "name": "投诉工单数",
                "value": 3
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
          "数据来源：query_report_source_data；数据表：complaint_weekly；口径说明：时间范围2026-06-01至2026-06-07，部门ID=10，负责人不限。"
        ],
        "recommendations": [
          "建议对平均处理时长29.8小时进行深入分析，优化流程以缩短处理周期。",
          "可考虑对工单分类标签进行细化，便于后续统计与改进。"
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
  "url": "/api/v1/reports/drafts/178/confirm",
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
    "content-length": "2272",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 123,
      "report_no": "RP-20260611103508-ebacc475",
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
        "summary": "本周（2026-06-01至2026-06-07）部门10共受理3张投诉工单，状态分布均匀（待处理、处理中、已解决各1张），平均处理时长为29.8小时。",
        "sections": [
          {
            "content": "本期共收到投诉工单3张，其中待处理1张、处理中1张、已解决1张，无重复或遗漏。平均处理时长为29.8小时，需关注时效性。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "工单总量",
                "value": 3
              },
              {
                "name": "待处理工单数",
                "value": 1
              },
              {
                "name": "处理中工单数",
                "value": 1
              },
              {
                "name": "已解决工单数",
                "value": 1
              },
              {
                "name": "平均处理时长(小时)",
                "value": 29.8
              }
            ]
          },
          {
            "content": "投诉工单按类别分为教学、服务、签证各1张，工单类型均为'投诉'，无其他类型。",
            "heading": "分类分布",
            "metrics": [
              {
                "name": "教学类工单数",
                "value": 1
              },
              {
                "name": "服务类工单数",
                "value": 1
              },
              {
                "name": "签证类工单数",
                "value": 1
              },
              {
                "name": "投诉工单数",
                "value": 3
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
          "数据来源：query_report_source_data；数据表：complaint_weekly；口径说明：时间范围2026-06-01至2026-06-07，部门ID=10，负责人不限。"
        ],
        "recommendations": [
          "建议对平均处理时长29.8小时进行深入分析，优化流程以缩短处理周期。",
          "可考虑对工单分类标签进行细化，便于后续统计与改进。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 178,
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
  "url": "/api/v1/reports/123/publish",
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
    "content-length": "2288",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 123,
      "report_no": "RP-20260611103508-ebacc475",
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
        "summary": "本周（2026-06-01至2026-06-07）部门10共受理3张投诉工单，状态分布均匀（待处理、处理中、已解决各1张），平均处理时长为29.8小时。",
        "sections": [
          {
            "content": "本期共收到投诉工单3张，其中待处理1张、处理中1张、已解决1张，无重复或遗漏。平均处理时长为29.8小时，需关注时效性。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "工单总量",
                "value": 3
              },
              {
                "name": "待处理工单数",
                "value": 1
              },
              {
                "name": "处理中工单数",
                "value": 1
              },
              {
                "name": "已解决工单数",
                "value": 1
              },
              {
                "name": "平均处理时长(小时)",
                "value": 29.8
              }
            ]
          },
          {
            "content": "投诉工单按类别分为教学、服务、签证各1张，工单类型均为'投诉'，无其他类型。",
            "heading": "分类分布",
            "metrics": [
              {
                "name": "教学类工单数",
                "value": 1
              },
              {
                "name": "服务类工单数",
                "value": 1
              },
              {
                "name": "签证类工单数",
                "value": 1
              },
              {
                "name": "投诉工单数",
                "value": 3
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
          "数据来源：query_report_source_data；数据表：complaint_weekly；口径说明：时间范围2026-06-01至2026-06-07，部门ID=10，负责人不限。"
        ],
        "recommendations": [
          "建议对平均处理时长29.8小时进行深入分析，优化流程以缩短处理周期。",
          "可考虑对工单分类标签进行细化，便于后续统计与改进。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 178,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:35:08"
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
  "url": "/api/v1/reports/123/exports",
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
      "id": 243,
      "report_id": 123,
      "export_type": "word",
      "file_name": "RP-20260611103508-ebacc475.docx",
      "file_path": "storage\\reports\\RP-20260611103508-ebacc475.docx",
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
  "url": "/api/v1/reports/exports/243/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103508-ebacc475.docx\"",
    "content-length": "37317"
  },
  "binary": {
    "size_bytes": 37317,
    "sha256": "bd9abbf4e52449cbf3f200dca9f392062fb63dc5d9223d2a0cc7e721e525a231",
    "first_16_bytes_hex": "504b03041400000008006454cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/123/exports",
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
      "id": 244,
      "report_id": 123,
      "export_type": "pdf",
      "file_name": "RP-20260611103508-ebacc475.pdf",
      "file_path": "storage\\reports\\RP-20260611103508-ebacc475.pdf",
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
  "url": "/api/v1/reports/exports/244/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103508-ebacc475.pdf\"",
    "content-length": "4116"
  },
  "binary": {
    "size_bytes": 4116,
    "sha256": "1e42d2335318eb6ee578478f97b302da5e48f3c7db7273ddbb4f2eb5a3ee1e63",
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
    "content-length": "2651",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 179,
      "draft_no": "DR-20260611103523-52df8788",
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
        "summary": "本周负责人ID 102新增线索2条，完成分析记录2条，活动报名2人，线索来源以公开课和转介绍为主，分析结果高意向与中等意向各1人。",
        "sections": [
          {
            "content": "本周新增线索共2条，其中公开课来源1条，转介绍来源1条；线索状态分布为：新线索1条，跟进中1条。建议持续跟进转介绍渠道，提升线索转化。",
            "heading": "线索概况",
            "metrics": [
              {
                "name": "新增线索",
                "value": "2"
              },
              {
                "name": "线索来源-公开课",
                "value": "1"
              },
              {
                "name": "线索来源-转介绍",
                "value": "1"
              },
              {
                "name": "线索状态-新",
                "value": "1"
              },
              {
                "name": "线索状态-跟进中",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周共完成分析记录2条，其中高意向分析结果1条，中等意向分析结果1条；活动报名共2人，实际参与1人，已注册未参与1人。建议对高意向客户优先安排深度跟进，同时关注未到场报名者的后续激活。",
            "heading": "分析记录与活动报名",
            "metrics": [
              {
                "name": "分析记录",
                "value": "2"
              },
              {
                "name": "分析结果-高意向",
                "value": "1"
              },
              {
                "name": "分析结果-中等意向",
                "value": "1"
              },
              {
                "name": "活动报名",
                "value": "2"
              },
              {
                "name": "活动报名-已参加",
                "value": "1"
              },
              {
                "name": "活动报名-已注册",
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
          "query_report_source_data",
          "客户经营分析数据表（口径说明：new_leads统计新增线索数，analysis_records统计分析记录数，event_registrations统计活动报名人数，来源及状态分解均为实际录入数据）"
        ],
        "recommendations": [
          "加强转介绍线索的获取激励，增加来源多样性",
          "对高意向分析结果客户尽快安排跟进，缩短转化周期",
          "对已注册未参加活动的客户进行回访，了解原因并重新激活"
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
  "url": "/api/v1/reports/drafts/179/confirm",
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
    "content-length": "2833",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 124,
      "report_no": "RP-20260611103523-26799337",
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
        "summary": "本周负责人ID 102新增线索2条，完成分析记录2条，活动报名2人，线索来源以公开课和转介绍为主，分析结果高意向与中等意向各1人。",
        "sections": [
          {
            "content": "本周新增线索共2条，其中公开课来源1条，转介绍来源1条；线索状态分布为：新线索1条，跟进中1条。建议持续跟进转介绍渠道，提升线索转化。",
            "heading": "线索概况",
            "metrics": [
              {
                "name": "新增线索",
                "value": "2"
              },
              {
                "name": "线索来源-公开课",
                "value": "1"
              },
              {
                "name": "线索来源-转介绍",
                "value": "1"
              },
              {
                "name": "线索状态-新",
                "value": "1"
              },
              {
                "name": "线索状态-跟进中",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周共完成分析记录2条，其中高意向分析结果1条，中等意向分析结果1条；活动报名共2人，实际参与1人，已注册未参与1人。建议对高意向客户优先安排深度跟进，同时关注未到场报名者的后续激活。",
            "heading": "分析记录与活动报名",
            "metrics": [
              {
                "name": "分析记录",
                "value": "2"
              },
              {
                "name": "分析结果-高意向",
                "value": "1"
              },
              {
                "name": "分析结果-中等意向",
                "value": "1"
              },
              {
                "name": "活动报名",
                "value": "2"
              },
              {
                "name": "活动报名-已参加",
                "value": "1"
              },
              {
                "name": "活动报名-已注册",
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
          "query_report_source_data",
          "客户经营分析数据表（口径说明：new_leads统计新增线索数，analysis_records统计分析记录数，event_registrations统计活动报名人数，来源及状态分解均为实际录入数据）"
        ],
        "recommendations": [
          "加强转介绍线索的获取激励，增加来源多样性",
          "对高意向分析结果客户尽快安排跟进，缩短转化周期",
          "对已注册未参加活动的客户进行回访，了解原因并重新激活"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 179,
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
  "url": "/api/v1/reports/124/publish",
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
    "content-length": "2849",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 124,
      "report_no": "RP-20260611103523-26799337",
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
        "summary": "本周负责人ID 102新增线索2条，完成分析记录2条，活动报名2人，线索来源以公开课和转介绍为主，分析结果高意向与中等意向各1人。",
        "sections": [
          {
            "content": "本周新增线索共2条，其中公开课来源1条，转介绍来源1条；线索状态分布为：新线索1条，跟进中1条。建议持续跟进转介绍渠道，提升线索转化。",
            "heading": "线索概况",
            "metrics": [
              {
                "name": "新增线索",
                "value": "2"
              },
              {
                "name": "线索来源-公开课",
                "value": "1"
              },
              {
                "name": "线索来源-转介绍",
                "value": "1"
              },
              {
                "name": "线索状态-新",
                "value": "1"
              },
              {
                "name": "线索状态-跟进中",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周共完成分析记录2条，其中高意向分析结果1条，中等意向分析结果1条；活动报名共2人，实际参与1人，已注册未参与1人。建议对高意向客户优先安排深度跟进，同时关注未到场报名者的后续激活。",
            "heading": "分析记录与活动报名",
            "metrics": [
              {
                "name": "分析记录",
                "value": "2"
              },
              {
                "name": "分析结果-高意向",
                "value": "1"
              },
              {
                "name": "分析结果-中等意向",
                "value": "1"
              },
              {
                "name": "活动报名",
                "value": "2"
              },
              {
                "name": "活动报名-已参加",
                "value": "1"
              },
              {
                "name": "活动报名-已注册",
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
          "query_report_source_data",
          "客户经营分析数据表（口径说明：new_leads统计新增线索数，analysis_records统计分析记录数，event_registrations统计活动报名人数，来源及状态分解均为实际录入数据）"
        ],
        "recommendations": [
          "加强转介绍线索的获取激励，增加来源多样性",
          "对高意向分析结果客户尽快安排跟进，缩短转化周期",
          "对已注册未参加活动的客户进行回访，了解原因并重新激活"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 179,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:35:24"
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
  "url": "/api/v1/reports/124/exports",
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
      "id": 245,
      "report_id": 124,
      "export_type": "word",
      "file_name": "RP-20260611103523-26799337.docx",
      "file_path": "storage\\reports\\RP-20260611103523-26799337.docx",
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
  "url": "/api/v1/reports/exports/245/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103523-26799337.docx\"",
    "content-length": "37462"
  },
  "binary": {
    "size_bytes": 37462,
    "sha256": "2f2ad4d8257614a40a3ccc359c69a84a575353187f3195f84d5faf8ce5f7251c",
    "first_16_bytes_hex": "504b03041400000008006b54cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/124/exports",
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
      "id": 246,
      "report_id": 124,
      "export_type": "pdf",
      "file_name": "RP-20260611103523-26799337.pdf",
      "file_path": "storage\\reports\\RP-20260611103523-26799337.pdf",
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
  "url": "/api/v1/reports/exports/246/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103523-26799337.pdf\"",
    "content-length": "4891"
  },
  "binary": {
    "size_bytes": 4891,
    "sha256": "84f9a48769301b1b6f2a61a3f7efaff53a265d19d6057bc03e8d8a2dd930a419",
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
    "content-length": "3737",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 180,
      "draft_no": "DR-20260611103543-5d13aabd",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "一名客户预算不确定（Full Employee A反馈），可能影响项目进度。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日部门10共有2份日报，提交率40.0%。其中草稿1份，已归档1份；含风险报告1份，明日计划报告1份。关键进展为“输出客户研判建议”，主要风险为“一名客户预算不确定”。",
        "sections": [
          {
            "content": "截至报告周期，部门10在2026年6月2日共收到日报2份。按状态分布：草稿1份（50.0%），已归档1份（50.0%），无处于已提交状态的日报。提交率为40.0%（按系统口径计算）。涉及员工2人（Full Employee A、Full Employee B）。本日风险报告1份，含明日计划内容的报告1份。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总报表数",
                "value": "2"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "草稿数",
                "value": "1"
              },
              {
                "name": "已归档数",
                "value": "1"
              },
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本日关键进展：Full Employee A 输出客户研判建议。风险方面：Full Employee A 反馈一名客户预算不确定，可能影响后续推进。请相关同事关注并制定应对策略。",
            "heading": "关键进展与风险",
            "metrics": [
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
            "content": "员工提交清单共5条记录（含重复状态），去重后涉及2名员工：Full Employee A 有3条记录（状态：submitted、archived、submitted），Full Employee B 有2条记录（状态：submitted、draft）。需注意系统统计的已提交状态日报数为0，可能与清单存在口径差异。",
            "heading": "员工提交详情",
            "metrics": [
              {
                "name": "提交清单记录数",
                "value": "5"
              },
              {
                "name": "涉及员工数",
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
          "数据来源于 query_report_source_data 工具，数据表：employee_daily_summary（部门10，日期2026-06-02）。提交率口径为系统定义。"
        ],
        "recommendations": [
          "建议部门负责人跟进客户预算确认情况，及时调整策略。",
          "关注员工日报提交状态一致性，确保统计口径与实际清单吻合。"
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
  "url": "/api/v1/reports/drafts/180/confirm",
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
    "content-length": "3896",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 125,
      "report_no": "RP-20260611103543-7be698d8",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "一名客户预算不确定（Full Employee A反馈），可能影响项目进度。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日部门10共有2份日报，提交率40.0%。其中草稿1份，已归档1份；含风险报告1份，明日计划报告1份。关键进展为“输出客户研判建议”，主要风险为“一名客户预算不确定”。",
        "sections": [
          {
            "content": "截至报告周期，部门10在2026年6月2日共收到日报2份。按状态分布：草稿1份（50.0%），已归档1份（50.0%），无处于已提交状态的日报。提交率为40.0%（按系统口径计算）。涉及员工2人（Full Employee A、Full Employee B）。本日风险报告1份，含明日计划内容的报告1份。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总报表数",
                "value": "2"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "草稿数",
                "value": "1"
              },
              {
                "name": "已归档数",
                "value": "1"
              },
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本日关键进展：Full Employee A 输出客户研判建议。风险方面：Full Employee A 反馈一名客户预算不确定，可能影响后续推进。请相关同事关注并制定应对策略。",
            "heading": "关键进展与风险",
            "metrics": [
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
            "content": "员工提交清单共5条记录（含重复状态），去重后涉及2名员工：Full Employee A 有3条记录（状态：submitted、archived、submitted），Full Employee B 有2条记录（状态：submitted、draft）。需注意系统统计的已提交状态日报数为0，可能与清单存在口径差异。",
            "heading": "员工提交详情",
            "metrics": [
              {
                "name": "提交清单记录数",
                "value": "5"
              },
              {
                "name": "涉及员工数",
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
          "数据来源于 query_report_source_data 工具，数据表：employee_daily_summary（部门10，日期2026-06-02）。提交率口径为系统定义。"
        ],
        "recommendations": [
          "建议部门负责人跟进客户预算确认情况，及时调整策略。",
          "关注员工日报提交状态一致性，确保统计口径与实际清单吻合。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 180,
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
  "url": "/api/v1/reports/125/publish",
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
    "content-length": "3912",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 125,
      "report_no": "RP-20260611103543-7be698d8",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "published",
      "content_json": {
        "risks": [
          "一名客户预算不确定（Full Employee A反馈），可能影响项目进度。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本日部门10共有2份日报，提交率40.0%。其中草稿1份，已归档1份；含风险报告1份，明日计划报告1份。关键进展为“输出客户研判建议”，主要风险为“一名客户预算不确定”。",
        "sections": [
          {
            "content": "截至报告周期，部门10在2026年6月2日共收到日报2份。按状态分布：草稿1份（50.0%），已归档1份（50.0%），无处于已提交状态的日报。提交率为40.0%（按系统口径计算）。涉及员工2人（Full Employee A、Full Employee B）。本日风险报告1份，含明日计划内容的报告1份。",
            "heading": "总体概况",
            "metrics": [
              {
                "name": "总报表数",
                "value": "2"
              },
              {
                "name": "提交率",
                "value": "40.0%"
              },
              {
                "name": "草稿数",
                "value": "1"
              },
              {
                "name": "已归档数",
                "value": "1"
              },
              {
                "name": "风险报告数",
                "value": "1"
              },
              {
                "name": "明日计划报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本日关键进展：Full Employee A 输出客户研判建议。风险方面：Full Employee A 反馈一名客户预算不确定，可能影响后续推进。请相关同事关注并制定应对策略。",
            "heading": "关键进展与风险",
            "metrics": [
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
            "content": "员工提交清单共5条记录（含重复状态），去重后涉及2名员工：Full Employee A 有3条记录（状态：submitted、archived、submitted），Full Employee B 有2条记录（状态：submitted、draft）。需注意系统统计的已提交状态日报数为0，可能与清单存在口径差异。",
            "heading": "员工提交详情",
            "metrics": [
              {
                "name": "提交清单记录数",
                "value": "5"
              },
              {
                "name": "涉及员工数",
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
          "数据来源于 query_report_source_data 工具，数据表：employee_daily_summary（部门10，日期2026-06-02）。提交率口径为系统定义。"
        ],
        "recommendations": [
          "建议部门负责人跟进客户预算确认情况，及时调整策略。",
          "关注员工日报提交状态一致性，确保统计口径与实际清单吻合。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 180,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:35:43"
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
  "url": "/api/v1/reports/125/exports",
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
      "id": 247,
      "report_id": 125,
      "export_type": "word",
      "file_name": "RP-20260611103543-7be698d8.docx",
      "file_path": "storage\\reports\\RP-20260611103543-7be698d8.docx",
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
  "url": "/api/v1/reports/exports/247/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103543-7be698d8.docx\"",
    "content-length": "37646"
  },
  "binary": {
    "size_bytes": 37646,
    "sha256": "dba62715c5ba74500f93ba90b5eff22de980bf22ae2bac89f98c489f341e1adf",
    "first_16_bytes_hex": "504b03041400000008007554cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/125/exports",
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
      "id": 248,
      "report_id": 125,
      "export_type": "pdf",
      "file_name": "RP-20260611103543-7be698d8.pdf",
      "file_path": "storage\\reports\\RP-20260611103543-7be698d8.pdf",
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
  "url": "/api/v1/reports/exports/248/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103543-7be698d8.pdf\"",
    "content-length": "5252"
  },
  "binary": {
    "size_bytes": 5252,
    "sha256": "82eb5c414ab5eccd7e981846579f9b6e9121cbe104b704df8224f665649f0bc1",
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
    "content-length": "2181",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 181,
      "draft_no": "DR-20260611103549-b89922a1",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本周有2篇风险报告，但未发现明确风险主题，需进一步人工核查。"
        ],
        "title": "员工日报汇总报告（周报）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共有4篇日报提交，涉及2名员工，周提交率100%。提交日主要集中在6月1日和2日，各2篇。存在2篇风险报告，需关注。",
        "sections": [
          {
            "content": "本周部门10共收到4篇日报，由2名员工提交。其中已提交2篇，已归档1篇，草稿1篇。周提交率达到100%，表明所有员工均按时提交。",
            "heading": "总体提交概览",
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
              }
            ]
          },
          {
            "content": "提交高峰与低谷均在6月1日（2篇），6月2日也有2篇提交。本周共有2篇风险报告，但暂无明确风险主题，建议后续关注风险报告详情。",
            "heading": "提交趋势与风险",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "高峰提交日",
                "value": "2026-06-01"
              },
              {
                "name": "低谷提交日",
                "value": "2026-06-01"
              },
              {
                "name": "每日提交趋势",
                "value": "2026-06-01:2, 2026-06-02:2"
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
          "query_report_source_data 接口",
          "员工日报表 employee_daily_reports"
        ],
        "recommendations": [
          "建议对风险报告内容进行逐篇复核，及时干预潜在问题。"
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
  "url": "/api/v1/reports/drafts/181/confirm",
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
    "content-length": "2335",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 126,
      "report_no": "RP-20260611103549-a6c5415e",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周报）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本周有2篇风险报告，但未发现明确风险主题，需进一步人工核查。"
        ],
        "title": "员工日报汇总报告（周报）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共有4篇日报提交，涉及2名员工，周提交率100%。提交日主要集中在6月1日和2日，各2篇。存在2篇风险报告，需关注。",
        "sections": [
          {
            "content": "本周部门10共收到4篇日报，由2名员工提交。其中已提交2篇，已归档1篇，草稿1篇。周提交率达到100%，表明所有员工均按时提交。",
            "heading": "总体提交概览",
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
              }
            ]
          },
          {
            "content": "提交高峰与低谷均在6月1日（2篇），6月2日也有2篇提交。本周共有2篇风险报告，但暂无明确风险主题，建议后续关注风险报告详情。",
            "heading": "提交趋势与风险",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "高峰提交日",
                "value": "2026-06-01"
              },
              {
                "name": "低谷提交日",
                "value": "2026-06-01"
              },
              {
                "name": "每日提交趋势",
                "value": "2026-06-01:2, 2026-06-02:2"
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
          "query_report_source_data 接口",
          "员工日报表 employee_daily_reports"
        ],
        "recommendations": [
          "建议对风险报告内容进行逐篇复核，及时干预潜在问题。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 181,
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
  "url": "/api/v1/reports/126/publish",
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
    "content-length": "2351",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 126,
      "report_no": "RP-20260611103549-a6c5415e",
      "report_type": "employee_weekly_summary",
      "title": "员工日报汇总报告（周报）",
      "status": "published",
      "content_json": {
        "risks": [
          "本周有2篇风险报告，但未发现明确风险主题，需进一步人工核查。"
        ],
        "title": "员工日报汇总报告（周报）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周（2026-06-01至2026-06-07）部门10共有4篇日报提交，涉及2名员工，周提交率100%。提交日主要集中在6月1日和2日，各2篇。存在2篇风险报告，需关注。",
        "sections": [
          {
            "content": "本周部门10共收到4篇日报，由2名员工提交。其中已提交2篇，已归档1篇，草稿1篇。周提交率达到100%，表明所有员工均按时提交。",
            "heading": "总体提交概览",
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
              }
            ]
          },
          {
            "content": "提交高峰与低谷均在6月1日（2篇），6月2日也有2篇提交。本周共有2篇风险报告，但暂无明确风险主题，建议后续关注风险报告详情。",
            "heading": "提交趋势与风险",
            "metrics": [
              {
                "name": "风险报告数",
                "value": "2"
              },
              {
                "name": "高峰提交日",
                "value": "2026-06-01"
              },
              {
                "name": "低谷提交日",
                "value": "2026-06-01"
              },
              {
                "name": "每日提交趋势",
                "value": "2026-06-01:2, 2026-06-02:2"
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
          "query_report_source_data 接口",
          "员工日报表 employee_daily_reports"
        ],
        "recommendations": [
          "建议对风险报告内容进行逐篇复核，及时干预潜在问题。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 181,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:35:50"
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
  "url": "/api/v1/reports/126/exports",
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
      "id": 249,
      "report_id": 126,
      "export_type": "word",
      "file_name": "RP-20260611103549-a6c5415e.docx",
      "file_path": "storage\\reports\\RP-20260611103549-a6c5415e.docx",
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
  "url": "/api/v1/reports/exports/249/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103549-a6c5415e.docx\"",
    "content-length": "37320"
  },
  "binary": {
    "size_bytes": 37320,
    "sha256": "82e1c828bc5372ac6e9bb3ea7273ca37592898f1ed1c785ff0fe44d5f25a02cb",
    "first_16_bytes_hex": "504b03041400000008007854cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/126/exports",
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
      "id": 250,
      "report_id": 126,
      "export_type": "pdf",
      "file_name": "RP-20260611103549-a6c5415e.pdf",
      "file_path": "storage\\reports\\RP-20260611103549-a6c5415e.pdf",
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
  "url": "/api/v1/reports/exports/250/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103549-a6c5415e.pdf\"",
    "content-length": "4178"
  },
  "binary": {
    "size_bytes": 4178,
    "sha256": "8e080b7c77b75575d1bf8bf7f3df228417d9a230aa6fd09e56115a82008c45a9",
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
    "content-length": "3279",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 182,
      "draft_no": "DR-20260611103603-e2906543",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "现有样本仅2人，样本量小，结论代表性有限。",
          "平均情绪得分仅59.0，低于60分基准，整体情绪状况需关注。",
          "存在1条待处理的高风险预警，若不及时干预可能导致情况恶化。"
        ],
        "title": "学生心理健康周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共有2名学生心理健康档案，平均情绪得分59.0，处于偏低水平。高风险学生1名，低风险学生1名；共产生2条预警，其中1条待处理，1条已解决，预警风险等级涵盖高与中等。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共维护学生心理健康档案2人，覆盖高风险与低风险各1人。情绪得分均值59.0，提示整体情绪状态偏弱。共记录2条预警，预警处理完成率为50%（已解决1条）。",
            "heading": "总体概况",
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
                "name": "总预警数",
                "value": "2"
              }
            ]
          },
          {
            "content": "风险等级分布为：高风险1人，低风险1人，无中等风险记录。高风险人员需重点关注其心理状态变化，低风险人员仍需保持观察。",
            "heading": "风险等级分布",
            "metrics": [
              {
                "name": "高风险人数",
                "value": "1"
              },
              {
                "name": "低风险人数",
                "value": "1"
              }
            ]
          },
          {
            "content": "情绪标签统计显示：焦虑1人，稳定1人。焦虑标签对应情绪得分偏低，可能与高风险关联；稳定标签对应低风险人员。",
            "heading": "情绪标签分布",
            "metrics": [
              {
                "name": "焦虑",
                "value": "1"
              },
              {
                "name": "稳定",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周预警处理状态：待处理1条，已解决1条。预警风险等级：高风险预警1条，中等风险预警1条。待处理的高风险预警需尽快干预。",
            "heading": "预警状态与风险等级",
            "metrics": [
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
                "name": "中等风险预警数",
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
          "query_report_source_data 接口，数据源为 student_psych_daily_profile 与 student_psych_alert 表，统计周期2026-06-01至2026-06-07，部门ID=10。"
        ],
        "recommendations": [
          "立即安排心理辅导老师对高风险学生进行一对一访谈，明确干预方案。",
          "对低风险学生开展定期回访，防止风险升级。",
          "加快待处理预警的核实与处置，确保在下一周期前完成。",
          "考虑扩大心理健康档案覆盖范围，提高监测的全面性。"
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
  "url": "/api/v1/reports/drafts/182/confirm",
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
    "content-length": "3453",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 127,
      "report_no": "RP-20260611103603-d1a31500",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "现有样本仅2人，样本量小，结论代表性有限。",
          "平均情绪得分仅59.0，低于60分基准，整体情绪状况需关注。",
          "存在1条待处理的高风险预警，若不及时干预可能导致情况恶化。"
        ],
        "title": "学生心理健康周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共有2名学生心理健康档案，平均情绪得分59.0，处于偏低水平。高风险学生1名，低风险学生1名；共产生2条预警，其中1条待处理，1条已解决，预警风险等级涵盖高与中等。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共维护学生心理健康档案2人，覆盖高风险与低风险各1人。情绪得分均值59.0，提示整体情绪状态偏弱。共记录2条预警，预警处理完成率为50%（已解决1条）。",
            "heading": "总体概况",
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
                "name": "总预警数",
                "value": "2"
              }
            ]
          },
          {
            "content": "风险等级分布为：高风险1人，低风险1人，无中等风险记录。高风险人员需重点关注其心理状态变化，低风险人员仍需保持观察。",
            "heading": "风险等级分布",
            "metrics": [
              {
                "name": "高风险人数",
                "value": "1"
              },
              {
                "name": "低风险人数",
                "value": "1"
              }
            ]
          },
          {
            "content": "情绪标签统计显示：焦虑1人，稳定1人。焦虑标签对应情绪得分偏低，可能与高风险关联；稳定标签对应低风险人员。",
            "heading": "情绪标签分布",
            "metrics": [
              {
                "name": "焦虑",
                "value": "1"
              },
              {
                "name": "稳定",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周预警处理状态：待处理1条，已解决1条。预警风险等级：高风险预警1条，中等风险预警1条。待处理的高风险预警需尽快干预。",
            "heading": "预警状态与风险等级",
            "metrics": [
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
                "name": "中等风险预警数",
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
          "query_report_source_data 接口，数据源为 student_psych_daily_profile 与 student_psych_alert 表，统计周期2026-06-01至2026-06-07，部门ID=10。"
        ],
        "recommendations": [
          "立即安排心理辅导老师对高风险学生进行一对一访谈，明确干预方案。",
          "对低风险学生开展定期回访，防止风险升级。",
          "加快待处理预警的核实与处置，确保在下一周期前完成。",
          "考虑扩大心理健康档案覆盖范围，提高监测的全面性。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 182,
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
  "url": "/api/v1/reports/127/publish",
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
    "content-length": "3469",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 127,
      "report_no": "RP-20260611103603-d1a31500",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "现有样本仅2人，样本量小，结论代表性有限。",
          "平均情绪得分仅59.0，低于60分基准，整体情绪状况需关注。",
          "存在1条待处理的高风险预警，若不及时干预可能导致情况恶化。"
        ],
        "title": "学生心理健康周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周部门10共有2名学生心理健康档案，平均情绪得分59.0，处于偏低水平。高风险学生1名，低风险学生1名；共产生2条预警，其中1条待处理，1条已解决，预警风险等级涵盖高与中等。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共维护学生心理健康档案2人，覆盖高风险与低风险各1人。情绪得分均值59.0，提示整体情绪状态偏弱。共记录2条预警，预警处理完成率为50%（已解决1条）。",
            "heading": "总体概况",
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
                "name": "总预警数",
                "value": "2"
              }
            ]
          },
          {
            "content": "风险等级分布为：高风险1人，低风险1人，无中等风险记录。高风险人员需重点关注其心理状态变化，低风险人员仍需保持观察。",
            "heading": "风险等级分布",
            "metrics": [
              {
                "name": "高风险人数",
                "value": "1"
              },
              {
                "name": "低风险人数",
                "value": "1"
              }
            ]
          },
          {
            "content": "情绪标签统计显示：焦虑1人，稳定1人。焦虑标签对应情绪得分偏低，可能与高风险关联；稳定标签对应低风险人员。",
            "heading": "情绪标签分布",
            "metrics": [
              {
                "name": "焦虑",
                "value": "1"
              },
              {
                "name": "稳定",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周预警处理状态：待处理1条，已解决1条。预警风险等级：高风险预警1条，中等风险预警1条。待处理的高风险预警需尽快干预。",
            "heading": "预警状态与风险等级",
            "metrics": [
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
                "name": "中等风险预警数",
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
          "query_report_source_data 接口，数据源为 student_psych_daily_profile 与 student_psych_alert 表，统计周期2026-06-01至2026-06-07，部门ID=10。"
        ],
        "recommendations": [
          "立即安排心理辅导老师对高风险学生进行一对一访谈，明确干预方案。",
          "对低风险学生开展定期回访，防止风险升级。",
          "加快待处理预警的核实与处置，确保在下一周期前完成。",
          "考虑扩大心理健康档案覆盖范围，提高监测的全面性。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 182,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:36:03"
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
  "url": "/api/v1/reports/127/exports",
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
      "id": 251,
      "report_id": 127,
      "export_type": "word",
      "file_name": "RP-20260611103603-d1a31500.docx",
      "file_path": "storage\\reports\\RP-20260611103603-d1a31500.docx",
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
  "url": "/api/v1/reports/exports/251/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103603-d1a31500.docx\"",
    "content-length": "37764"
  },
  "binary": {
    "size_bytes": 37764,
    "sha256": "378796637d04234de8f6fa69a5471529ada5849841c5a0abedc53e07608923a9",
    "first_16_bytes_hex": "504b03041400000008008154cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/127/exports",
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
      "id": 252,
      "report_id": 127,
      "export_type": "pdf",
      "file_name": "RP-20260611103603-d1a31500.pdf",
      "file_path": "storage\\reports\\RP-20260611103603-d1a31500.pdf",
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
  "url": "/api/v1/reports/exports/252/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611103603-d1a31500.pdf\"",
    "content-length": "5669"
  },
  "binary": {
    "size_bytes": 5669,
    "sha256": "b7bd819512043d544801e1d560a6f1ebb660bbd1d7e3347272d9d17c4b17c541",
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
  "ai_draft": 182,
  "ai_report": 127,
  "report_export_record": 252,
  "audit_log": 940,
  "ai_tool_call_log": 198
}
```

### 阶段结论

- 结果：通过

