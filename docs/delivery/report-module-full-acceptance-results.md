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

- 执行时间：`2026-06-11 10:10:31`
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
    "content-length": "2329",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 153,
      "draft_no": "DR-20260611101032-6a69b546",
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
          "total_tickets": 3
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
  "url": "/api/v1/reports/drafts/153/confirm",
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
    "content-length": "2512",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 98,
      "report_no": "RP-20260611101032-4f94ae9c",
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
          "total_tickets": 3
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
      "source_draft_id": 153,
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
  "url": "/api/v1/reports/98/publish",
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
    "content-length": "2528",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 98,
      "report_no": "RP-20260611101032-4f94ae9c",
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
          "total_tickets": 3
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
      "source_draft_id": 153,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:10:32"
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
  "url": "/api/v1/reports/98/exports",
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
      "id": 193,
      "report_id": 98,
      "export_type": "word",
      "file_name": "RP-20260611101032-4f94ae9c.docx",
      "file_path": "storage\\reports\\RP-20260611101032-4f94ae9c.docx",
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
  "url": "/api/v1/reports/exports/193/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101032-4f94ae9c.docx\"",
    "content-length": "37569"
  },
  "binary": {
    "size_bytes": 37569,
    "sha256": "cb7a152313013d0033f9375c2c61bfffd74714315674ded9070c5991225416ee",
    "first_16_bytes_hex": "504b03041400000008005051cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/98/exports",
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
      "id": 194,
      "report_id": 98,
      "export_type": "pdf",
      "file_name": "RP-20260611101032-4f94ae9c.pdf",
      "file_path": "storage\\reports\\RP-20260611101032-4f94ae9c.pdf",
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
  "url": "/api/v1/reports/exports/194/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101032-4f94ae9c.pdf\"",
    "content-length": "5245"
  },
  "binary": {
    "size_bytes": 5245,
    "sha256": "3d50dc8416ddac39b4013d54992efd315b1339d86b0ff2f1e667a1fdbe001a01",
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
    "content-length": "2166",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 154,
      "draft_no": "DR-20260611101032-03d10c14",
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
          "event_registrations": 2
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
  "url": "/api/v1/reports/drafts/154/confirm",
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
    "content-length": "2359",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 99,
      "report_no": "RP-20260611101032-ab67cc60",
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
          "event_registrations": 2
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
      "source_draft_id": 154,
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
  "url": "/api/v1/reports/99/publish",
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
    "content-length": "2375",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 99,
      "report_no": "RP-20260611101032-ab67cc60",
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
          "event_registrations": 2
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
      "source_draft_id": 154,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:10:33"
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
  "url": "/api/v1/reports/99/exports",
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
      "id": 195,
      "report_id": 99,
      "export_type": "word",
      "file_name": "RP-20260611101032-ab67cc60.docx",
      "file_path": "storage\\reports\\RP-20260611101032-ab67cc60.docx",
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
  "url": "/api/v1/reports/exports/195/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101032-ab67cc60.docx\"",
    "content-length": "37494"
  },
  "binary": {
    "size_bytes": 37494,
    "sha256": "c8956f5e5a5f5a06474adfe7762b35f2fcf69637ed97498af58dc499f22e2609",
    "first_16_bytes_hex": "504b03041400000008005051cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/99/exports",
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
      "id": 196,
      "report_id": 99,
      "export_type": "pdf",
      "file_name": "RP-20260611101032-ab67cc60.pdf",
      "file_path": "storage\\reports\\RP-20260611101032-ab67cc60.pdf",
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
  "url": "/api/v1/reports/exports/196/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101032-ab67cc60.pdf\"",
    "content-length": "5166"
  },
  "binary": {
    "size_bytes": 5166,
    "sha256": "53489004e3e3264b93a095183413313a2eabd66dd7f92a47d86344c84c6ba722",
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
    "content-length": "2142",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 155,
      "draft_no": "DR-20260611101032-30a3bc63",
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
  "url": "/api/v1/reports/drafts/155/confirm",
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
    "content-length": "2311",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 100,
      "report_no": "RP-20260611101032-0f3a5214",
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
          "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-02"
        ],
        "recommendations": [
          "建立日报提交截止时间提醒，确保当日日清日结",
          "对风险摘要日报进行集中分析，制定应对方案",
          "将明日计划填报纳入日报考核标准"
        ]
      },
      "source_draft_id": 155,
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
  "url": "/api/v1/reports/100/publish",
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
    "content-length": "2327",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 100,
      "report_no": "RP-20260611101032-0f3a5214",
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
          "数据来源：employee_daily_report 员工日报表，统计口径：部门 10，日期 2026-06-02"
        ],
        "recommendations": [
          "建立日报提交截止时间提醒，确保当日日清日结",
          "对风险摘要日报进行集中分析，制定应对方案",
          "将明日计划填报纳入日报考核标准"
        ]
      },
      "source_draft_id": 155,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:10:33"
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
  "url": "/api/v1/reports/100/exports",
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
      "id": 197,
      "report_id": 100,
      "export_type": "word",
      "file_name": "RP-20260611101032-0f3a5214.docx",
      "file_path": "storage\\reports\\RP-20260611101032-0f3a5214.docx",
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
  "url": "/api/v1/reports/exports/197/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101032-0f3a5214.docx\"",
    "content-length": "37398"
  },
  "binary": {
    "size_bytes": 37398,
    "sha256": "6fb52d43d900e87798bbde1634939a11787bfe46b6020b1dd59dca54326ca250",
    "first_16_bytes_hex": "504b03041400000008005051cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/100/exports",
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
      "id": 198,
      "report_id": 100,
      "export_type": "pdf",
      "file_name": "RP-20260611101032-0f3a5214.pdf",
      "file_path": "storage\\reports\\RP-20260611101032-0f3a5214.pdf",
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
  "url": "/api/v1/reports/exports/198/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101032-0f3a5214.pdf\"",
    "content-length": "4948"
  },
  "binary": {
    "size_bytes": 4948,
    "sha256": "060d6ceccc3316cc47a7ff5a2974aab229a80a41bf20568344f5a940ad701595",
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
    "content-length": "2402",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 156,
      "draft_no": "DR-20260611101033-0e1b731a",
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
          "distinct_employees": 2
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
  "url": "/api/v1/reports/drafts/156/confirm",
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
    "content-length": "2585",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 101,
      "report_no": "RP-20260611101033-06929190",
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
          "distinct_employees": 2
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
      "source_draft_id": 156,
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
  "url": "/api/v1/reports/101/publish",
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
    "content-length": "2601",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 101,
      "report_no": "RP-20260611101033-06929190",
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
          "distinct_employees": 2
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
      "source_draft_id": 156,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:10:33"
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
  "url": "/api/v1/reports/101/exports",
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
      "id": 199,
      "report_id": 101,
      "export_type": "word",
      "file_name": "RP-20260611101033-06929190.docx",
      "file_path": "storage\\reports\\RP-20260611101033-06929190.docx",
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
  "url": "/api/v1/reports/exports/199/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101033-06929190.docx\"",
    "content-length": "37558"
  },
  "binary": {
    "size_bytes": 37558,
    "sha256": "18d1184a655dda8f4678b386c4c6c01a61c5b3f5ac41a6a475c3a633cef9cb80",
    "first_16_bytes_hex": "504b03041400000008005051cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/101/exports",
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
      "id": 200,
      "report_id": 101,
      "export_type": "pdf",
      "file_name": "RP-20260611101033-06929190.pdf",
      "file_path": "storage\\reports\\RP-20260611101033-06929190.pdf",
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
  "url": "/api/v1/reports/exports/200/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101033-06929190.pdf\"",
    "content-length": "5222"
  },
  "binary": {
    "size_bytes": 5222,
    "sha256": "a1215efad3a467a05448bd9b3475f2690858794a5d1f4e985208db9e047d2174",
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
      "id": 157,
      "draft_no": "DR-20260611101033-da2ac464",
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
  "url": "/api/v1/reports/drafts/157/confirm",
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
      "id": 102,
      "report_no": "RP-20260611101033-763b1595",
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
      "source_draft_id": 157,
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
  "url": "/api/v1/reports/102/publish",
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
      "id": 102,
      "report_no": "RP-20260611101033-763b1595",
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
      "source_draft_id": 157,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:10:34"
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
  "url": "/api/v1/reports/102/exports",
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
      "id": 201,
      "report_id": 102,
      "export_type": "word",
      "file_name": "RP-20260611101033-763b1595.docx",
      "file_path": "storage\\reports\\RP-20260611101033-763b1595.docx",
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
  "url": "/api/v1/reports/exports/201/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101033-763b1595.docx\"",
    "content-length": "37687"
  },
  "binary": {
    "size_bytes": 37687,
    "sha256": "18ffc68ec68dec8226055c8b76a33f5cdca02003efe233994c6bff9602db465f",
    "first_16_bytes_hex": "504b03041400000008005051cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/102/exports",
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
      "id": 202,
      "report_id": 102,
      "export_type": "pdf",
      "file_name": "RP-20260611101033-763b1595.pdf",
      "file_path": "storage\\reports\\RP-20260611101033-763b1595.pdf",
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
  "url": "/api/v1/reports/exports/202/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101033-763b1595.pdf\"",
    "content-length": "5736"
  },
  "binary": {
    "size_bytes": 5736,
    "sha256": "0c71d59bb77b65d3ba9c834c7fd0d5f2b0c1447517433d2fe7fa469796c4a151",
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
  "ai_draft": 157,
  "ai_report": 102,
  "report_export_record": 202,
  "audit_log": 765,
  "ai_tool_call_log": 158
}
```

### 阶段结论

- 结果：通过


## real-dify 阶段

- 执行时间：`2026-06-11 10:10:37`
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
    "content-length": "1660",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 158,
      "draft_no": "DR-20260611101055-cd38dee0",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本周仍有1件投诉处于待处理状态，需关注超时未处理风险。"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共受理3件投诉，其中1件待处理、1件处理中、1件已解决。",
        "sections": [
          {
            "content": "本周投诉总量为3件。按状态分布：待处理1件（33.3%），处理中1件（33.3%），已解决1件（33.3%）。",
            "heading": "投诉总量与状态分布",
            "metrics": [
              {
                "name": "总投诉量",
                "value": "3"
              },
              {
                "name": "待处理数",
                "value": "1"
              },
              {
                "name": "处理中数",
                "value": "1"
              },
              {
                "name": "已解决数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周期投诉集中在部门ID为10的部门。",
            "heading": "部门投诉情况",
            "metrics": [
              {
                "name": "部门ID",
                "value": "10"
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
          "数据表：complaint_weekly（投诉处理周报）",
          "口径：date_start=2026-06-01, date_end=2026-06-07, department_id=10"
        ],
        "recommendations": [
          "建议加快待处理投诉的分配与处理，避免积压。",
          "持续跟踪处理中投诉的进展，确保按时解决。"
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
  "url": "/api/v1/reports/drafts/158/confirm",
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
    "content-length": "1832",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 103,
      "report_no": "RP-20260611101055-0c40c030",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本周仍有1件投诉处于待处理状态，需关注超时未处理风险。"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共受理3件投诉，其中1件待处理、1件处理中、1件已解决。",
        "sections": [
          {
            "content": "本周投诉总量为3件。按状态分布：待处理1件（33.3%），处理中1件（33.3%），已解决1件（33.3%）。",
            "heading": "投诉总量与状态分布",
            "metrics": [
              {
                "name": "总投诉量",
                "value": "3"
              },
              {
                "name": "待处理数",
                "value": "1"
              },
              {
                "name": "处理中数",
                "value": "1"
              },
              {
                "name": "已解决数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周期投诉集中在部门ID为10的部门。",
            "heading": "部门投诉情况",
            "metrics": [
              {
                "name": "部门ID",
                "value": "10"
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
          "数据表：complaint_weekly（投诉处理周报）",
          "口径：date_start=2026-06-01, date_end=2026-06-07, department_id=10"
        ],
        "recommendations": [
          "建议加快待处理投诉的分配与处理，避免积压。",
          "持续跟踪处理中投诉的进展，确保按时解决。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 158,
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
  "url": "/api/v1/reports/103/publish",
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
    "content-length": "1848",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 103,
      "report_no": "RP-20260611101055-0c40c030",
      "report_type": "complaint_weekly",
      "title": "投诉处理周报（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "本周仍有1件投诉处于待处理状态，需关注超时未处理风险。"
        ],
        "title": "投诉处理周报（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共受理3件投诉，其中1件待处理、1件处理中、1件已解决。",
        "sections": [
          {
            "content": "本周投诉总量为3件。按状态分布：待处理1件（33.3%），处理中1件（33.3%），已解决1件（33.3%）。",
            "heading": "投诉总量与状态分布",
            "metrics": [
              {
                "name": "总投诉量",
                "value": "3"
              },
              {
                "name": "待处理数",
                "value": "1"
              },
              {
                "name": "处理中数",
                "value": "1"
              },
              {
                "name": "已解决数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本周期投诉集中在部门ID为10的部门。",
            "heading": "部门投诉情况",
            "metrics": [
              {
                "name": "部门ID",
                "value": "10"
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
          "数据表：complaint_weekly（投诉处理周报）",
          "口径：date_start=2026-06-01, date_end=2026-06-07, department_id=10"
        ],
        "recommendations": [
          "建议加快待处理投诉的分配与处理，避免积压。",
          "持续跟踪处理中投诉的进展，确保按时解决。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 158,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:10:56"
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
  "url": "/api/v1/reports/103/exports",
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
      "id": 203,
      "report_id": 103,
      "export_type": "word",
      "file_name": "RP-20260611101055-0c40c030.docx",
      "file_path": "storage\\reports\\RP-20260611101055-0c40c030.docx",
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
  "url": "/api/v1/reports/exports/203/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101055-0c40c030.docx\"",
    "content-length": "37193"
  },
  "binary": {
    "size_bytes": 37193,
    "sha256": "3a76713dcef8cfa64ec5087c5e25c5d11c50c485a752ec95106f4d853f4aded8",
    "first_16_bytes_hex": "504b03041400000008005b51cb5cad52"
  }
}
```

### 投诉处理周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/103/exports",
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
      "id": 204,
      "report_id": 103,
      "export_type": "pdf",
      "file_name": "RP-20260611101055-0c40c030.pdf",
      "file_path": "storage\\reports\\RP-20260611101055-0c40c030.pdf",
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
  "url": "/api/v1/reports/exports/204/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101055-0c40c030.pdf\"",
    "content-length": "4260"
  },
  "binary": {
    "size_bytes": 4260,
    "sha256": "8175002f6288e34cf0dc842f40dfdc5977e6706b2c08c3e36abdf0a96b2c6733",
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
    "content-length": "1935",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 159,
      "draft_no": "DR-20260611101103-99c81581",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "整体客户运营指标数值较低，可能存在客户基数不足或渠道效率不高的问题。"
        ],
        "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期内，部门10下负责人102共计新增潜客2个，完成分析记录2条，活动报名2次。整体运营数据处于起步阶段，需加强各环节转化。",
        "sections": [
          {
            "content": "本周期共新增潜客2个，表明客户引流活动处于初期或小规模阶段。建议持续拓展获客渠道，提升新客数量。",
            "heading": "客户获取分析",
            "metrics": [
              {
                "name": "新增潜客数",
                "value": "2"
              }
            ]
          },
          {
            "content": "分析记录和活动报名均为2次，与潜客数量持平。说明客户初步互动后，后续跟进及转化动作较为同步，但总量较低，需提升整体客户活跃度。",
            "heading": "客户分析与活动参与",
            "metrics": [
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "活动报名数",
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
          "数据来源于 FastAPI AI Tool 的 query_report_source_data，取自客户运营相关业务表（new_leads、analysis_records、event_registrations）。"
        ],
        "recommendations": [
          "建议加大获客投入，如增加线上推广或线下活动。",
          "针对已产生的潜客和分析记录，加快跟进转化节奏，提高活动报名参与率。"
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
  "url": "/api/v1/reports/drafts/159/confirm",
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
    "content-length": "2117",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 104,
      "report_no": "RP-20260611101103-8499b0ac",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "整体客户运营指标数值较低，可能存在客户基数不足或渠道效率不高的问题。"
        ],
        "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期内，部门10下负责人102共计新增潜客2个，完成分析记录2条，活动报名2次。整体运营数据处于起步阶段，需加强各环节转化。",
        "sections": [
          {
            "content": "本周期共新增潜客2个，表明客户引流活动处于初期或小规模阶段。建议持续拓展获客渠道，提升新客数量。",
            "heading": "客户获取分析",
            "metrics": [
              {
                "name": "新增潜客数",
                "value": "2"
              }
            ]
          },
          {
            "content": "分析记录和活动报名均为2次，与潜客数量持平。说明客户初步互动后，后续跟进及转化动作较为同步，但总量较低，需提升整体客户活跃度。",
            "heading": "客户分析与活动参与",
            "metrics": [
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "活动报名数",
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
          "数据来源于 FastAPI AI Tool 的 query_report_source_data，取自客户运营相关业务表（new_leads、analysis_records、event_registrations）。"
        ],
        "recommendations": [
          "建议加大获客投入，如增加线上推广或线下活动。",
          "针对已产生的潜客和分析记录，加快跟进转化节奏，提高活动报名参与率。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 159,
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
  "url": "/api/v1/reports/104/publish",
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
    "content-length": "2133",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 104,
      "report_no": "RP-20260611101103-8499b0ac",
      "report_type": "customer_operation",
      "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "整体客户运营指标数值较低，可能存在客户基数不足或渠道效率不高的问题。"
        ],
        "title": "全域客户经营分析报告（2026-06-01至2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": 102
        },
        "summary": "本周期内，部门10下负责人102共计新增潜客2个，完成分析记录2条，活动报名2次。整体运营数据处于起步阶段，需加强各环节转化。",
        "sections": [
          {
            "content": "本周期共新增潜客2个，表明客户引流活动处于初期或小规模阶段。建议持续拓展获客渠道，提升新客数量。",
            "heading": "客户获取分析",
            "metrics": [
              {
                "name": "新增潜客数",
                "value": "2"
              }
            ]
          },
          {
            "content": "分析记录和活动报名均为2次，与潜客数量持平。说明客户初步互动后，后续跟进及转化动作较为同步，但总量较低，需提升整体客户活跃度。",
            "heading": "客户分析与活动参与",
            "metrics": [
              {
                "name": "分析记录数",
                "value": "2"
              },
              {
                "name": "活动报名数",
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
          "数据来源于 FastAPI AI Tool 的 query_report_source_data，取自客户运营相关业务表（new_leads、analysis_records、event_registrations）。"
        ],
        "recommendations": [
          "建议加大获客投入，如增加线上推广或线下活动。",
          "针对已产生的潜客和分析记录，加快跟进转化节奏，提高活动报名参与率。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 159,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:11:04"
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
  "url": "/api/v1/reports/104/exports",
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
      "id": 205,
      "report_id": 104,
      "export_type": "word",
      "file_name": "RP-20260611101103-8499b0ac.docx",
      "file_path": "storage\\reports\\RP-20260611101103-8499b0ac.docx",
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
  "url": "/api/v1/reports/exports/205/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101103-8499b0ac.docx\"",
    "content-length": "37433"
  },
  "binary": {
    "size_bytes": 37433,
    "sha256": "bc6c6801c46623c4b4f1eb70d75f1ccc2446aabbd5b7868face2992a690b2899",
    "first_16_bytes_hex": "504b03041400000008006151cb5cad52"
  }
}
```

### 客户经营分析报告 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/104/exports",
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
      "id": 206,
      "report_id": 104,
      "export_type": "pdf",
      "file_name": "RP-20260611101103-8499b0ac.pdf",
      "file_path": "storage\\reports\\RP-20260611101103-8499b0ac.pdf",
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
  "url": "/api/v1/reports/exports/206/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101103-8499b0ac.pdf\"",
    "content-length": "4107"
  },
  "binary": {
    "size_bytes": 4107,
    "sha256": "5779c61d1a7a3428acf413dc0c6ca3c69705a0b460036b62a9dce94d2aae8496",
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
    "content-length": "2124",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 160,
      "draft_no": "DR-20260611101111-fdd41ef2",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本日有1份员工日报标记为风险报告，需关注相关员工或事项，及时跟进处理。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月2日，部门ID为10的部门共有2份员工日报，其中草稿1份、归档1份，无已提交报告。涉及风险报告1份，明日计划报告1份。",
        "sections": [
          {
            "content": "本日共收到2份员工日报，全部未提交至审核流程。其中1份为草稿状态，1份为归档状态。无已提交或已完成的报告。",
            "heading": "报告提交概览",
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
                "name": "归档报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本日收集的报告中有1份标注了风险，占比50%。同时，有1份报告包含了明日工作计划，表明部分员工已提前规划次日任务。",
            "heading": "内容与风险分析",
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
          "query_report_source_data 返回 employee_daily_summary 表",
          "数据口径：统计2026-06-02当天部门ID=10的员工日报，不含按负责人筛选（owner_user_id=null）"
        ],
        "recommendations": [
          "建议督促草稿状态的报告（1份）尽快提交，以提高报告完成率。",
          "可针对风险报告内容组织相关团队进行复盘或支持。"
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
  "url": "/api/v1/reports/drafts/160/confirm",
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
    "content-length": "2283",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 105,
      "report_no": "RP-20260611101111-ee088109",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本日有1份员工日报标记为风险报告，需关注相关员工或事项，及时跟进处理。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月2日，部门ID为10的部门共有2份员工日报，其中草稿1份、归档1份，无已提交报告。涉及风险报告1份，明日计划报告1份。",
        "sections": [
          {
            "content": "本日共收到2份员工日报，全部未提交至审核流程。其中1份为草稿状态，1份为归档状态。无已提交或已完成的报告。",
            "heading": "报告提交概览",
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
                "name": "归档报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本日收集的报告中有1份标注了风险，占比50%。同时，有1份报告包含了明日工作计划，表明部分员工已提前规划次日任务。",
            "heading": "内容与风险分析",
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
          "query_report_source_data 返回 employee_daily_summary 表",
          "数据口径：统计2026-06-02当天部门ID=10的员工日报，不含按负责人筛选（owner_user_id=null）"
        ],
        "recommendations": [
          "建议督促草稿状态的报告（1份）尽快提交，以提高报告完成率。",
          "可针对风险报告内容组织相关团队进行复盘或支持。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 160,
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
  "url": "/api/v1/reports/105/publish",
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
    "content-length": "2299",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 105,
      "report_no": "RP-20260611101111-ee088109",
      "report_type": "employee_daily_summary",
      "title": "员工日报汇总报告（2026-06-02）",
      "status": "published",
      "content_json": {
        "risks": [
          "本日有1份员工日报标记为风险报告，需关注相关员工或事项，及时跟进处理。"
        ],
        "title": "员工日报汇总报告（2026-06-02）",
        "filters": {
          "date_end": "2026-06-02",
          "date_start": "2026-06-02",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "2026年6月2日，部门ID为10的部门共有2份员工日报，其中草稿1份、归档1份，无已提交报告。涉及风险报告1份，明日计划报告1份。",
        "sections": [
          {
            "content": "本日共收到2份员工日报，全部未提交至审核流程。其中1份为草稿状态，1份为归档状态。无已提交或已完成的报告。",
            "heading": "报告提交概览",
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
                "name": "归档报告数",
                "value": "1"
              }
            ]
          },
          {
            "content": "本日收集的报告中有1份标注了风险，占比50%。同时，有1份报告包含了明日工作计划，表明部分员工已提前规划次日任务。",
            "heading": "内容与风险分析",
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
          "query_report_source_data 返回 employee_daily_summary 表",
          "数据口径：统计2026-06-02当天部门ID=10的员工日报，不含按负责人筛选（owner_user_id=null）"
        ],
        "recommendations": [
          "建议督促草稿状态的报告（1份）尽快提交，以提高报告完成率。",
          "可针对风险报告内容组织相关团队进行复盘或支持。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 160,
      "date_start": "2026-06-02",
      "date_end": "2026-06-02",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:11:11"
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
  "url": "/api/v1/reports/105/exports",
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
      "id": 207,
      "report_id": 105,
      "export_type": "word",
      "file_name": "RP-20260611101111-ee088109.docx",
      "file_path": "storage\\reports\\RP-20260611101111-ee088109.docx",
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
  "url": "/api/v1/reports/exports/207/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101111-ee088109.docx\"",
    "content-length": "37405"
  },
  "binary": {
    "size_bytes": 37405,
    "sha256": "df9424b1163cfd6c41cb9b71e09d9401e7e08a0d073e4ec107a2942be30b4132",
    "first_16_bytes_hex": "504b03041400000008006551cb5cad52"
  }
}
```

### 员工日报汇总报告（日） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/105/exports",
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
      "id": 208,
      "report_id": 105,
      "export_type": "pdf",
      "file_name": "RP-20260611101111-ee088109.pdf",
      "file_path": "storage\\reports\\RP-20260611101111-ee088109.pdf",
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
  "url": "/api/v1/reports/exports/208/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101111-ee088109.pdf\"",
    "content-length": "4215"
  },
  "binary": {
    "size_bytes": 4215,
    "sha256": "46c18675033c2755c9181ac2f29c267bc4becebba8bf6cb202c5a114ccece6be",
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
    "content-length": "2068",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 161,
      "draft_no": "DR-20260611101118-25715ebc",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "本周有2条风险报告，需关注具体风险内容并推动闭环处理。"
        ],
        "title": "员工日报周汇总报告（2026-06-01 至 2026-06-07）部门10",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共收到4份员工日报，涉及2名员工。完成提交2份，归档1份，草稿1份。风险报告2条，需关注。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共有4份员工日报，由2名员工提交。其中2份已提交，1份已归档，1份为草稿。报告提交集中在6月1日和2日，每天各2份。",
            "heading": "报告提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "不同员工数",
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
              },
              {
                "name": "6月1日报告数",
                "value": "2"
              },
              {
                "name": "6月2日报告数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周共标记2条风险报告，占报告总数的50%。建议相关员工及时补充风险详情并跟进处理。",
            "heading": "风险报告",
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
          "query_report_source_data 返回：employee_weekly_summary 周报数据",
          "数据表/口径：员工日报表，按日期范围2026-06-01至2026-06-07、部门ID=10汇总"
        ],
        "recommendations": [
          "请提醒有草稿状态的员工提交日报；跟进风险报告的详细描述与处理进展。"
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
  "url": "/api/v1/reports/drafts/161/confirm",
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
    "content-length": "2252",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 106,
      "report_no": "RP-20260611101118-da03b371",
      "report_type": "employee_weekly_summary",
      "title": "员工日报周汇总报告（2026-06-01 至 2026-06-07）部门10",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "本周有2条风险报告，需关注具体风险内容并推动闭环处理。"
        ],
        "title": "员工日报周汇总报告（2026-06-01 至 2026-06-07）部门10",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共收到4份员工日报，涉及2名员工。完成提交2份，归档1份，草稿1份。风险报告2条，需关注。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共有4份员工日报，由2名员工提交。其中2份已提交，1份已归档，1份为草稿。报告提交集中在6月1日和2日，每天各2份。",
            "heading": "报告提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "不同员工数",
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
              },
              {
                "name": "6月1日报告数",
                "value": "2"
              },
              {
                "name": "6月2日报告数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周共标记2条风险报告，占报告总数的50%。建议相关员工及时补充风险详情并跟进处理。",
            "heading": "风险报告",
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
          "query_report_source_data 返回：employee_weekly_summary 周报数据",
          "数据表/口径：员工日报表，按日期范围2026-06-01至2026-06-07、部门ID=10汇总"
        ],
        "recommendations": [
          "请提醒有草稿状态的员工提交日报；跟进风险报告的详细描述与处理进展。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 161,
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
  "url": "/api/v1/reports/106/publish",
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
    "content-length": "2268",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 106,
      "report_no": "RP-20260611101118-da03b371",
      "report_type": "employee_weekly_summary",
      "title": "员工日报周汇总报告（2026-06-01 至 2026-06-07）部门10",
      "status": "published",
      "content_json": {
        "risks": [
          "本周有2条风险报告，需关注具体风险内容并推动闭环处理。"
        ],
        "title": "员工日报周汇总报告（2026-06-01 至 2026-06-07）部门10",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共收到4份员工日报，涉及2名员工。完成提交2份，归档1份，草稿1份。风险报告2条，需关注。",
        "sections": [
          {
            "content": "本周（2026-06-01至2026-06-07）部门10共有4份员工日报，由2名员工提交。其中2份已提交，1份已归档，1份为草稿。报告提交集中在6月1日和2日，每天各2份。",
            "heading": "报告提交情况",
            "metrics": [
              {
                "name": "总报告数",
                "value": "4"
              },
              {
                "name": "不同员工数",
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
              },
              {
                "name": "6月1日报告数",
                "value": "2"
              },
              {
                "name": "6月2日报告数",
                "value": "2"
              }
            ]
          },
          {
            "content": "本周共标记2条风险报告，占报告总数的50%。建议相关员工及时补充风险详情并跟进处理。",
            "heading": "风险报告",
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
          "query_report_source_data 返回：employee_weekly_summary 周报数据",
          "数据表/口径：员工日报表，按日期范围2026-06-01至2026-06-07、部门ID=10汇总"
        ],
        "recommendations": [
          "请提醒有草稿状态的员工提交日报；跟进风险报告的详细描述与处理进展。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 161,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:11:19"
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
  "url": "/api/v1/reports/106/exports",
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
      "id": 209,
      "report_id": 106,
      "export_type": "word",
      "file_name": "RP-20260611101118-da03b371.docx",
      "file_path": "storage\\reports\\RP-20260611101118-da03b371.docx",
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
  "url": "/api/v1/reports/exports/209/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101118-da03b371.docx\"",
    "content-length": "37308"
  },
  "binary": {
    "size_bytes": 37308,
    "sha256": "61c30dfa7b0c77778875e752412a1f94eb3f8839916b2004a51aca80fde00c50",
    "first_16_bytes_hex": "504b03041400000008006951cb5cad52"
  }
}
```

### 员工日报汇总报告（周） - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/106/exports",
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
      "id": 210,
      "report_id": 106,
      "export_type": "pdf",
      "file_name": "RP-20260611101118-da03b371.pdf",
      "file_path": "storage\\reports\\RP-20260611101118-da03b371.pdf",
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
  "url": "/api/v1/reports/exports/210/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101118-da03b371.pdf\"",
    "content-length": "5019"
  },
  "binary": {
    "size_bytes": 5019,
    "sha256": "0b226c735d0005af94c9d625bfc9111472b38723b240aa19429fd5bbbd62c845",
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
    "content-length": "2465",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 162,
      "draft_no": "DR-20260611101129-4abdfaff",
      "status": "pending_confirm",
      "content_json": {
        "risks": [
          "存在1名高风险学生，且仍有1条高风险预警待处理，如不及时干预可能影响其他学生或引发更严重的心理危机。"
        ],
        "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共监测2名学生，高风险、低风险各1人；平均情绪得分59.0；产生2条预警（1条待处理，1条已处理），其中高风险预警1条、中风险1条。",
        "sections": [
          {
            "content": "本周期内共纳入2份学生心理档案，部门ID为10。风险等级分布为：高风险1人，低风险1人，无中等风险学生。整体需关注高风险个体的心理状态。",
            "heading": "总体概况",
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
              }
            ]
          },
          {
            "content": "学生情绪标签分布为：焦虑1人，稳定1人。平均情绪得分为59.0，处于中等偏下水平。本周共产生2条预警，其中待处理1条、已处理1条；预警风险等级分布为：高1条、中1条。",
            "heading": "情绪与预警分析",
            "metrics": [
              {
                "name": "平均情绪得分",
                "value": "59.0"
              },
              {
                "name": "总预警数",
                "value": "2"
              },
              {
                "name": "待处理预警数",
                "value": "1"
              },
              {
                "name": "已处理预警数",
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
          "query_report_source_data - student_psych_weekly (department_id=10, 2026-06-01~2026-06-07)"
        ],
        "recommendations": [
          "建议优先处理待处理的高风险预警，安排心理老师跟进评估。",
          "对低风险学生可开展常规心理辅导，巩固稳定状态。",
          "建议部门加强情绪焦虑学生的日常关注与沟通。"
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
  "url": "/api/v1/reports/drafts/162/confirm",
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
    "content-length": "2639",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 107,
      "report_no": "RP-20260611101129-01170074",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
      "status": "confirmed",
      "content_json": {
        "risks": [
          "存在1名高风险学生，且仍有1条高风险预警待处理，如不及时干预可能影响其他学生或引发更严重的心理危机。"
        ],
        "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共监测2名学生，高风险、低风险各1人；平均情绪得分59.0；产生2条预警（1条待处理，1条已处理），其中高风险预警1条、中风险1条。",
        "sections": [
          {
            "content": "本周期内共纳入2份学生心理档案，部门ID为10。风险等级分布为：高风险1人，低风险1人，无中等风险学生。整体需关注高风险个体的心理状态。",
            "heading": "总体概况",
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
              }
            ]
          },
          {
            "content": "学生情绪标签分布为：焦虑1人，稳定1人。平均情绪得分为59.0，处于中等偏下水平。本周共产生2条预警，其中待处理1条、已处理1条；预警风险等级分布为：高1条、中1条。",
            "heading": "情绪与预警分析",
            "metrics": [
              {
                "name": "平均情绪得分",
                "value": "59.0"
              },
              {
                "name": "总预警数",
                "value": "2"
              },
              {
                "name": "待处理预警数",
                "value": "1"
              },
              {
                "name": "已处理预警数",
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
          "query_report_source_data - student_psych_weekly (department_id=10, 2026-06-01~2026-06-07)"
        ],
        "recommendations": [
          "建议优先处理待处理的高风险预警，安排心理老师跟进评估。",
          "对低风险学生可开展常规心理辅导，巩固稳定状态。",
          "建议部门加强情绪焦虑学生的日常关注与沟通。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 162,
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
  "url": "/api/v1/reports/107/publish",
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
    "content-length": "2655",
    "content-type": "application/json"
  },
  "json": {
    "code": 0,
    "message": "success",
    "data": {
      "id": 107,
      "report_no": "RP-20260611101129-01170074",
      "report_type": "student_psych_weekly",
      "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
      "status": "published",
      "content_json": {
        "risks": [
          "存在1名高风险学生，且仍有1条高风险预警待处理，如不及时干预可能影响其他学生或引发更严重的心理危机。"
        ],
        "title": "学生心理健康周报（2026-06-01 ~ 2026-06-07）",
        "filters": {
          "date_end": "2026-06-07",
          "date_start": "2026-06-01",
          "department_id": 10,
          "owner_user_id": null
        },
        "summary": "本周共监测2名学生，高风险、低风险各1人；平均情绪得分59.0；产生2条预警（1条待处理，1条已处理），其中高风险预警1条、中风险1条。",
        "sections": [
          {
            "content": "本周期内共纳入2份学生心理档案，部门ID为10。风险等级分布为：高风险1人，低风险1人，无中等风险学生。整体需关注高风险个体的心理状态。",
            "heading": "总体概况",
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
              }
            ]
          },
          {
            "content": "学生情绪标签分布为：焦虑1人，稳定1人。平均情绪得分为59.0，处于中等偏下水平。本周共产生2条预警，其中待处理1条、已处理1条；预警风险等级分布为：高1条、中1条。",
            "heading": "情绪与预警分析",
            "metrics": [
              {
                "name": "平均情绪得分",
                "value": "59.0"
              },
              {
                "name": "总预警数",
                "value": "2"
              },
              {
                "name": "待处理预警数",
                "value": "1"
              },
              {
                "name": "已处理预警数",
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
          "query_report_source_data - student_psych_weekly (department_id=10, 2026-06-01~2026-06-07)"
        ],
        "recommendations": [
          "建议优先处理待处理的高风险预警，安排心理老师跟进评估。",
          "对低风险学生可开展常规心理辅导，巩固稳定状态。",
          "建议部门加强情绪焦虑学生的日常关注与沟通。"
        ],
        "tool_status_code": 200,
        "tool_call_success": true
      },
      "source_draft_id": 162,
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 10,
      "created_by": 101,
      "published_by": 101,
      "published_time": "2026-06-11T10:11:29"
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
  "url": "/api/v1/reports/107/exports",
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
      "id": 211,
      "report_id": 107,
      "export_type": "word",
      "file_name": "RP-20260611101129-01170074.docx",
      "file_path": "storage\\reports\\RP-20260611101129-01170074.docx",
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
  "url": "/api/v1/reports/exports/211/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101129-01170074.docx\"",
    "content-length": "37469"
  },
  "binary": {
    "size_bytes": 37469,
    "sha256": "4bcc1b963055b45a113fb3eed845c2fb2c694fad4fb8b8b7e51027101e182fab",
    "first_16_bytes_hex": "504b03041400000008006e51cb5cad52"
  }
}
```

### 学生心理健康周报 - 导出 PDF

请求：
```json
{
  "method": "POST",
  "url": "/api/v1/reports/107/exports",
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
      "id": 212,
      "report_id": 107,
      "export_type": "pdf",
      "file_name": "RP-20260611101129-01170074.pdf",
      "file_path": "storage\\reports\\RP-20260611101129-01170074.pdf",
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
  "url": "/api/v1/reports/exports/212/download",
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
    "content-disposition": "attachment; filename=\"RP-20260611101129-01170074.pdf\"",
    "content-length": "5020"
  },
  "binary": {
    "size_bytes": 5020,
    "sha256": "83cb71a3557fb4a77c09d816c89a8d8663ff16ca3a91bb2294069d235a810e2c",
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
  "ai_draft": 162,
  "ai_report": 107,
  "report_export_record": 212,
  "audit_log": 800,
  "ai_tool_call_log": 168
}
```

### 阶段结论

- 结果：通过

