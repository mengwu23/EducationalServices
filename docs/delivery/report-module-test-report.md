# 报告模块全量测试报告

## 1. 测试结论

本次对报告模块现有 DAO、Service、API、AI Tool 自动化用例执行全量测试，覆盖报告源数据聚合、草稿生成、草稿确认、报告发布、报告导出、权限控制、参数校验、Dify 失败处理和 AI Tool 调用日志。

测试结果：14 个用例全部通过。

```text
14 passed in 0.84s
```

## 2. 测试命令

执行目录：

```text
D:\code_progarm\Education_Service_System\backend
```

执行命令：

```powershell
python -m pytest tests/unit/test_report_dao.py tests/unit/test_report_service.py tests/integration/test_report_api.py -vv
```

## 3. 测试环境

- 测试框架：pytest 9.0.3
- Python：3.12.7
- 数据库：SQLite 内存库
- ORM Base：`app.database.Base`
- Web 测试客户端：FastAPI `TestClient`
- Dify：默认 mock；失败场景使用 `FailingDifyClient`
- PDF 导出失败场景：通过空 `report_pdf_converter_path` 模拟转换器不可用
- MySQL 方言兼容：测试中将 MySQL `LONGTEXT` 在 SQLite 下编译为 `TEXT`

## 4. 测试输入数据

### 用户和组织

| 类型 | 输入 |
| --- | --- |
| 管理员 | `id=1`, `username=admin`, `user_type=admin` |
| 员工 | `id=2`, `username=employee`, `user_type=employee` |
| 学生 | `id=3`, `username=student`, `user_type=student` |
| 部门 | `id=1`, `department_name=咨询一部` |
| 员工档案 | `id=1`, `user_id=2`, `department_id=1`, `role_code=service` |
| 学生档案 | `id=1`, `user_id=3`, `counselor_employee_id=1` |

### 业务数据

| 类型 | 输入 |
| --- | --- |
| 投诉工单 1 | `ticket_no=FB001`, `status=open`, `category=service`, `create_time=2026-06-02 10:00:00` |
| 投诉工单 2 | `ticket_no=FB002`, `status=closed`, `category=course`, `create_time=2026-06-03 10:00:00` |
| 客户线索 | `lead_no=LEAD001`, `status=new`, `source_channel=event`, `owner_employee_id=1`, `create_time=2026-06-02 09:00:00` |
| 客户研判记录 | `analysis_no=AN001`, `source_type=manual`, `lead_id=1`, `create_time=2026-06-03 09:00:00` |
| 活动讲座 | `event_no=EVT001`, `event_type=offline`, `start_time=2026-06-04 09:00:00` |
| 活动报名 | `lead_id=1`, `event_id=100`, `registration_status=registered`, `create_time=2026-06-04 09:00:00` |

### 公共请求参数

| 参数 | 输入 |
| --- | --- |
| 投诉周报类型 | `complaint_weekly` |
| 客户经营类型 | `customer_operation` |
| 开始日期 | `2026-06-01` |
| 结束日期 | `2026-06-07` |
| 部门 ID | `1` |
| 负责人用户 ID | `2` |

## 5. 用例结果

| 序号 | 用例 | 输入 | 预期输出 | 实际结果 |
| --- | --- | --- | --- | --- |
| 1 | `test_query_complaint_weekly_by_date_and_department` | 投诉周报，日期 `2026-06-01` 到 `2026-06-07`，部门 `1` | `total_tickets=2`，`status_counts={"closed": 1, "open": 1}` | 通过 |
| 2 | `test_query_customer_operation_by_owner` | 客户经营，日期 `2026-06-01` 到 `2026-06-07`，部门 `1`，负责人用户 `2` | `new_leads=1`，`analysis_records=1`，`event_registrations=1` | 通过 |
| 3 | `test_admin_generate_complaint_weekly_draft` | 管理员生成投诉周报草稿 | 草稿状态为 `pending_confirm`，标题为投诉处理周报 | 通过 |
| 4 | `test_employee_generate_customer_operation_draft` | 员工生成客户经营分析报告草稿 | 草稿状态为 `pending_confirm`，标题为客户经营分析报告 | 通过 |
| 5 | `test_employee_cannot_publish_report` | 员工发布已确认报告 | 返回 HTTP 403 | 通过 |
| 6 | `test_admin_confirm_draft_creates_ai_report` | 管理员确认草稿 | 生成 `AiReport`，状态为 `confirmed`，关联原草稿 ID | 通过 |
| 7 | `test_dify_failure_creates_failed_draft_and_audit_log` | Dify mock 抛出异常 | 生成失败草稿，记录失败审计日志，错误信息写入草稿和日志 | 通过 |
| 8 | `test_export_word_creates_file_and_record` | 已发布报告导出 Word | 导出状态为 `success`，本地文件存在 | 通过 |
| 9 | `test_export_pdf_failure_writes_record_and_audit_log` | PDF 转换器路径为空时导出 PDF | 返回 HTTP 500，写入失败导出记录和失败审计日志 | 通过 |
| 10 | `test_generate_confirm_publish_export_word_flow` | API 完整流程：生成草稿、确认、发布、Word 导出 | 各步骤 HTTP 200，发布状态为 `published`，导出状态为 `success` | 通过 |
| 11 | `test_employee_cannot_publish_report_api` | 员工通过 API 发布管理员报告 | 返回 HTTP 403 | 通过 |
| 12 | `test_student_cannot_generate_report_api` | 学生通过 API 生成报告草稿 | 返回 HTTP 403 | 通过 |
| 13 | `test_missing_date_range_returns_validation_error` | API 请求缺少日期范围 | 返回 HTTP 422 | 通过 |
| 14 | `test_ai_tool_query_report_source_data_writes_log` | AI Tool 查询客户经营数据，携带 `conversation_id` 和 `trace_id` | 返回工具名 `query_report_source_data`，结果 `new_leads=1`，写入工具调用日志 | 通过 |

## 6. 关键输出示例

### 投诉周报 DAO 输出

```json
{
  "report_type": "complaint_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1,
  "total_tickets": 2,
  "status_counts": {
    "closed": 1,
    "open": 1
  }
}
```

### 客户经营 DAO 输出

```json
{
  "report_type": "customer_operation",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1,
  "owner_user_id": 2,
  "new_leads": 1,
  "analysis_records": 1,
  "event_registrations": 1
}
```

### API 完整流程输出

| 步骤 | 接口 | 关键输出 |
| --- | --- | --- |
| 生成草稿 | `POST /api/v1/reports/generate-draft` | HTTP 200，返回草稿 `id` |
| 确认草稿 | `POST /api/v1/reports/drafts/{draft_id}/confirm` | HTTP 200，返回报告 `id` |
| 发布报告 | `POST /api/v1/reports/{report_id}/publish` | HTTP 200，`status=published` |
| Word 导出 | `POST /api/v1/reports/{report_id}/exports` | HTTP 200，`status=success` |

## 7. 实际 pytest 输出

```text
tests/unit/test_report_dao.py::test_query_complaint_weekly_by_date_and_department PASSED [  7%]
tests/unit/test_report_dao.py::test_query_customer_operation_by_owner PASSED [ 14%]
tests/unit/test_report_service.py::test_admin_generate_complaint_weekly_draft PASSED [ 21%]
tests/unit/test_report_service.py::test_employee_generate_customer_operation_draft PASSED [ 28%]
tests/unit/test_report_service.py::test_employee_cannot_publish_report PASSED [ 35%]
tests/unit/test_report_service.py::test_admin_confirm_draft_creates_ai_report PASSED [ 42%]
tests/unit/test_report_service.py::test_dify_failure_creates_failed_draft_and_audit_log PASSED [ 50%]
tests/unit/test_report_service.py::test_export_word_creates_file_and_record PASSED [ 57%]
tests/unit/test_report_service.py::test_export_pdf_failure_writes_record_and_audit_log PASSED [ 64%]
tests/integration/test_report_api.py::test_generate_confirm_publish_export_word_flow PASSED [ 71%]
tests/integration/test_report_api.py::test_employee_cannot_publish_report_api PASSED [ 78%]
tests/integration/test_report_api.py::test_student_cannot_generate_report_api PASSED [ 85%]
tests/integration/test_report_api.py::test_missing_date_range_returns_validation_error PASSED [ 92%]
tests/integration/test_report_api.py::test_ai_tool_query_report_source_data_writes_log PASSED [100%]

============================= 14 passed in 0.84s ==============================
```

## 8. 结论

报告模块现有自动化测试已覆盖核心链路和关键异常分支，当前测试结果满足交付验证要求。后续如新增日报、心理健康、学生服务等报告类型，需要同步补充对应 DAO 聚合用例、Service 流程用例和 API 集成用例。
