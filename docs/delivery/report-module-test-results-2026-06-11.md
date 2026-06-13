# 智能报告模块全量测试报告

**测试日期**：2026-06-11  
**测试环境**：Python 3.12.7 / pytest 9.0.3 / SQLite in-memory  
**测试结果**：54 passed / 0 failed / 0 error（耗时 3.37s）

---

## 测试范围

| 测试文件 | 类型 | 用例数 |
|---|---|---|
| `tests/unit/test_report_service.py` | 单元测试 | 17 |
| `tests/unit/test_report_dao.py` | 单元测试 | 6 |
| `tests/unit/test_report_export_service.py` | 单元测试 | 2 |
| `tests/unit/test_dify_client.py` | 单元测试 | 10 |
| `tests/integration/test_report_api.py` | 集成测试 | 19 |
| **合计** | | **54** |

---

## 一、单元测试 — ReportService（17 条）

### 1.1 草稿生成

#### test_admin_generate_complaint_weekly_draft

**输入**
```python
report_type = "complaint_weekly"
date_start = "2026-06-01"
date_end = "2026-06-07"
department_id = 1
user = CurrentUser(id=1, role="admin")
```
**输出**
```python
draft["status"] == "pending_confirm"
draft["content_json"]["title"].startswith("投诉处理周报")  # True
```
**结果**：PASSED

---

#### test_employee_generate_customer_operation_draft

**输入**
```python
report_type = "customer_operation"
date_start = "2026-06-01"
date_end = "2026-06-07"
department_id = 1
owner_user_id = 2
user = CurrentUser(id=2, role="employee")
```
**输出**
```python
draft["status"] == "pending_confirm"
draft["content_json"]["title"].startswith("全域客户经营分析报告")  # True
```
**结果**：PASSED

---

#### test_admin_generate_new_report_type_draft[employee_daily_summary]

**输入**
```python
report_type = "employee_daily_summary"
date_start = "2026-06-01"
date_end = "2026-06-07"
department_id = 1
user = CurrentUser(id=1, role="admin")
```
**输出**
```python
draft["status"] == "pending_confirm"
draft["content_json"]["report_type"] == "employee_daily_summary"
draft["content_json"]["source_data"]["report_type"] == "employee_daily_summary"
draft["content_json"]["sections"]  # 非空
```
**结果**：PASSED

---

#### test_admin_generate_new_report_type_draft[employee_weekly_summary]

**输入**
```python
report_type = "employee_weekly_summary"
date_start = "2026-06-01"
date_end = "2026-06-07"
department_id = 1
user = CurrentUser(id=1, role="admin")
```
**输出**
```python
draft["status"] == "pending_confirm"
draft["content_json"]["report_type"] == "employee_weekly_summary"
draft["content_json"]["sections"]  # 非空
```
**结果**：PASSED

---

#### test_admin_generate_new_report_type_draft[student_psych_weekly]

**输入**
```python
report_type = "student_psych_weekly"
date_start = "2026-06-01"
date_end = "2026-06-07"
department_id = 1
user = CurrentUser(id=1, role="admin")
```
**输出**
```python
draft["status"] == "pending_confirm"
draft["content_json"]["report_type"] == "student_psych_weekly"
draft["content_json"]["sections"]  # 非空
```
**结果**：PASSED

---

#### test_employee_generate_new_report_type_draft[employee_daily_summary / employee_weekly_summary / student_psych_weekly]

**输入**：同上三种 report_type，user = CurrentUser(id=2, role="employee")

**输出**
```python
draft["status"] == "pending_confirm"
draft["content_json"]["report_type"] == report_type  # 各自匹配
```
**结果**：PASSED × 3

---

### 1.2 草稿确认

#### test_admin_confirm_draft_creates_ai_report

**输入**：先生成 complaint_weekly 草稿，再 confirm_draft(draft_id, admin)

**输出**
```python
report["title"].startswith("投诉处理周报")  # True
report["status"] == "confirmed"
report["source_draft_id"] == draft["id"]
```
**结果**：PASSED

---

#### test_admin_confirm_new_report_type_draft_creates_ai_report[employee_daily_summary / employee_weekly_summary / student_psych_weekly]

**输入**：生成各类型草稿后 confirm

**输出**
```python
report["report_type"] == report_type
report["status"] == "confirmed"
report["source_draft_id"] == draft["id"]
```
**结果**：PASSED × 3

---

### 1.3 权限控制

#### test_employee_cannot_publish_report

**输入**：admin 生成并确认草稿后，employee 尝试发布

**输出**
```python
HTTPException.status_code == 403
```
**结果**：PASSED

---

### 1.4 异常处理

#### test_dify_failure_creates_failed_draft_and_audit_log

**输入**：注入 FailingDifyClient（抛出 `RuntimeError("Dify 模拟失败")`），生成草稿

**输出**
```python
# 抛出 ReportGenerationError
AiDraft.status == "generation_failed"
AiDraft.content_json["error_message"] == "Dify 模拟失败"
AuditLog.result == "fail"
AuditLog.error_message == "Dify 模拟失败"
```
**结果**：PASSED

---

#### test_export_failure_writes_record_and_audit_log

**输入**：monkeypatch 替换 export_service.export 为抛出 `RuntimeError("模板导出失败")`，对已发布报告执行 PDF 导出

**输出**
```python
HTTPException.status_code == 500
ReportExportRecord.status == "fail"
ReportExportRecord.error_message 包含 "模板导出失败"
AuditLog(action_type="export", result="fail").error_message 包含 "模板导出失败"
```
**结果**：PASSED

---

### 1.5 导出

#### test_export_word_creates_file_and_record

**输入**：admin 完成生成→确认→发布→导出 word 全流程，export_dir 为临时目录

**输出**
```python
export["status"] == "success"
Path(export["file_path"]).exists()  # True
```
**结果**：PASSED

---

### 1.6 模型字段校验

#### test_report_related_models_have_update_time_and_soft_delete_defaults

**输入**：完整走一遍生成→确认→发布→导出→AI Tool 查询流程

**输出**：AiDraft、AiReport、AuditLog、ReportExportRecord、AiToolCallLog 五张表记录均满足：
```python
model.update_time is not None
model.is_deleted is False
```
**结果**：PASSED

---

## 二、单元测试 — ReportDAO（6 条）

### test_query_complaint_weekly_by_date_and_department

**输入**
```python
report_type = "complaint_weekly"
date_start = date(2026, 6, 1)
date_end = date(2026, 6, 7)
department_id = 1
# 种子数据：ticket FB001(open)、FB002(closed)，均属学生1(部门1)
```
**输出**
```python
result["total_tickets"] == 2
result["status_counts"] == {"closed": 1, "open": 1}
```
**结果**：PASSED

---

### test_query_customer_operation_by_owner

**输入**
```python
report_type = "customer_operation"
date_start = date(2026, 6, 1)
date_end = date(2026, 6, 7)
department_id = 1
owner_user_id = 2
# 种子数据：lead LEAD001(员工1负责)、analysis AN001、registration 1条
```
**输出**
```python
result["new_leads"] == 1
result["analysis_records"] == 1
result["event_registrations"] == 1
```
**结果**：PASSED

---

### test_query_employee_daily_summary_by_single_date_and_department

**输入**
```python
report_type = "employee_daily_summary"
date_start = date_end = date(2026, 6, 2)
department_id = 1
# 种子数据：日报1(submitted,有risk,有plan)、日报2(draft,无risk,有plan)
# 日报4属部门2(排除)、日报5(is_delete=1，排除)
```
**输出**
```python
result["total_reports"] == 2
result["status_counts"] == {"draft": 1, "submitted": 1}
result["submitted_reports"] == 1
result["draft_reports"] == 1
result["archived_reports"] == 0
result["risk_reports"] == 1
result["tomorrow_plan_reports"] == 2
```
**结果**：PASSED

---

### test_query_employee_weekly_summary_by_date_range_and_department

**输入**
```python
report_type = "employee_weekly_summary"
date_start = date(2026, 6, 1)
date_end = date(2026, 6, 7)
department_id = 1
# 种子数据：日报1(6-2,submitted)、日报2(6-2,draft)、日报3(6-3,archived)
# 日报5(is_delete=1，排除)
```
**输出**
```python
result["total_reports"] == 3
result["distinct_employees"] == 2
result["status_counts"] == {"archived": 1, "draft": 1, "submitted": 1}
result["daily_trend"] == {"2026-06-02": 2, "2026-06-03": 1}
result["risk_reports"] == 2
```
**结果**：PASSED

---

### test_query_student_psych_weekly_by_department

**输入**
```python
report_type = "student_psych_weekly"
date_start = date(2026, 6, 1)
date_end = date(2026, 6, 7)
department_id = 1
# 种子数据：心理画像2条(高风险+中风险)，第3条is_delete=1排除
# 预警2条(pending+resolved)，第3条is_delete=1排除
```
**输出**
```python
result["total_profiles"] == 2
result["risk_level_counts"] == {"high": 1, "medium": 1}
result["emotion_tag_counts"] == {"anxious": 1, "stable": 1}
result["average_emotion_score"] == 55  # (40+70)/2
result["total_alerts"] == 2
result["alert_status_counts"] == {"pending": 1, "resolved": 1}
result["alert_risk_level_counts"] == {"high": 1, "medium": 1}
```
**结果**：PASSED

---

### test_dao_filters_soft_deleted_drafts_reports_and_exports

**输入**：手动插入已删除草稿(is_deleted=True)、已删除报告、已删除导出记录，和对应的有效记录

**输出**
```python
dao.get_draft(deleted_draft.id) is None
deleted_draft.id not in [d.id for d in dao.list_report_drafts()]
dao.get_report(deleted_report.id) is None
deleted_report.id not in [r.id for r in dao.list_reports()]
deleted_export.id not in [e.id for e in dao.list_export_records(active_report.id)]
```
**结果**：PASSED

---

## 三、单元测试 — ReportExportService（2 条）

### test_export_word_uses_report_template

**输入**
```python
report = AiReport(
    report_no="RP-TEMPLATE",
    report_type="complaint_weekly",
    title="投诉处理周报",
    content_json={
        "title": "投诉处理周报",
        "summary": "本周投诉处理整体平稳。",
        "sections": [{"heading": "投诉概览", "content": "本周共处理投诉 2 条。",
                      "metrics": [{"name": "open", "value": 1}, {"name": "closed", "value": 1}]}],
        "risks": ["仍有未关闭投诉需要跟进"],
        "recommendations": ["下周优先关闭超时工单"],
        "source_refs": ["student_feedback_ticket"],
    },
    ...
)
export_type = ExportType.WORD
```
**输出**
```python
file_name == "RP-TEMPLATE.docx"
Path(file_path).exists()  # True
# Word 文档内容包含：
"投诉处理周报" in text
"本周投诉处理整体平稳。" in text
"投诉概览" in text
"open：1" in text
"仍有未关闭投诉需要跟进" in text
```
**结果**：PASSED

---

### test_export_pdf_uses_report_template

**输入**：同上，export_type = ExportType.PDF

**输出**
```python
file_name == "RP-TEMPLATE.pdf"
Path(file_path).exists()  # True
Path(file_path).read_bytes().startswith(b"%PDF")  # True
```
**结果**：PASSED

---

## 四、单元测试 — DifyClient（10 条）

### test_real_dify_parses_report_object

**输入**：Dify 返回 `outputs.report` 为 dict 对象
```json
{"data": {"outputs": {"report": {"title": "真实Dify报告", "summary": "摘要", "sections": [...]}}}}
```
**输出**
```python
draft["title"] == "真实Dify报告"
draft["risks"] == []
draft["recommendations"] == []
draft["source_refs"] == []
# 请求头携带 Authorization: Bearer test-key
# inputs.source_data 和 inputs.filters 均为 JSON 字符串
```
**结果**：PASSED

---

### test_real_dify_parses_report_json_string

**输入**：`outputs.report` 为 JSON 字符串

**输出**
```python
draft["title"] == "JSON字符串报告"
draft["sections"][0]["heading"] == "趋势"
```
**结果**：PASSED

---

### test_real_dify_parses_text_json_string

**输入**：`outputs.text` 为 JSON 字符串（无 report 字段）

**输出**
```python
draft["title"] == "Text字段报告"
```
**结果**：PASSED

---

### test_real_dify_parses_think_prefixed_json

**输入**：`outputs.report` 为 `<think>内部推理内容</think>{"title": "思考模式报告", ...}`

**输出**
```python
draft["title"] == "思考模式报告"
```
**结果**：PASSED

---

### test_real_dify_parses_markdown_fenced_json

**输入**：`outputs.report` 为 ` ```json\n{...}\n``` ` 格式

**输出**
```python
draft["title"] == "代码块报告"
```
**结果**：PASSED

---

### test_real_dify_extracts_embedded_json_object

**输入**：`outputs.report` 为 `"前缀说明 {...} 后缀说明"` 混合文本

**输出**
```python
draft["title"] == "嵌入JSON报告"
```
**结果**：PASSED

---

### test_real_dify_rejects_failed_tool_call

**输入**：`outputs.report` 包含 `tool_call_success: false`

**输出**
```python
RuntimeError("Dify AI Tool 调用失败")  # 抛出
```
**结果**：PASSED

---

### test_real_dify_rejects_non_200_tool_status

**输入**：`outputs.report` 包含 `tool_call_success: true` 但 `tool_status_code: "401"`

**输出**
```python
RuntimeError("Dify AI Tool 调用失败")  # 抛出
```
**结果**：PASSED

---

### test_real_dify_rejects_failure_content_without_status_flag

**输入**：`outputs.report` 虽然 `tool_status_code: 200`，但 summary/sections 内容描述的是工具调用错误（HTTP 422）

**输出**
```python
RuntimeError("模型输出包含工具失败")  # 抛出
```
**结果**：PASSED

---

### test_real_dify_invalid_json_raises_clear_error

**输入**：`outputs.report` 为 `"{not-json"`

**输出**
```python
RuntimeError("Dify 返回内容无法解析")  # 抛出
```
**结果**：PASSED

---

### test_real_dify_missing_title_raises_clear_error

**输入**：`outputs.report` 为 `{"summary": "缺少标题"}`（无 title 字段）

**输出**
```python
RuntimeError("Dify 返回内容无法解析")  # 抛出
```
**结果**：PASSED

---

### test_real_dify_without_api_key_raises_clear_error

**输入**：`dify_mock_enabled=False`，`dify_api_key=""`（空字符串）

**输出**
```python
RuntimeError("未配置 Dify API Key")  # 抛出
```
**结果**：PASSED

---

## 五、集成测试 — Report API（19 条）

### 5.1 完整业务流程

#### test_generate_draft_api_supports_five_report_types

**输入**：以 admin 身份分别请求五类报告类型
```http
POST /api/v1/reports/generate-draft
X-User-Id: 1  X-User-Role: admin
{"report_type": "<各类型>", "date_start": "2026-06-01", "date_end": "2026-06-07", "department_id": 1}
```
**输出**（每种类型）
```json
{"code": 0, "data": {"content_json": {"report_type": "<各类型>"}}}
HTTP 200
```
**结果**：PASSED（5 种类型全部通过）

---

#### test_generate_confirm_publish_export_word_flow

**输入**：完整走一遍四步流程（admin）
```
POST /generate-draft → POST /drafts/{id}/confirm → POST /{id}/publish → POST /{id}/exports
```
**输出**
```python
# 生成草稿
HTTP 200, draft_id 非空
# 确认草稿
HTTP 200, report_id 非空
# 发布报告
HTTP 200, data["status"] == "published"
# 导出 Word
HTTP 200, data["status"] == "success"
```
**结果**：PASSED

---

### 5.2 文件下载

#### test_download_word_export_file

**输入**：完成导出后下载
```http
GET /api/v1/reports/exports/{id}/download
X-User-Id: 1  X-User-Role: admin
```
**输出**
```python
HTTP 200
response.content.startswith(b"PK")  # True（Word 文件头）
content-type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
AuditLog(action_type="download_export").result == "success"
```
**结果**：PASSED

---

#### test_download_pdf_export_file

**输入**：导出 PDF 后下载

**输出**
```python
HTTP 200
response.content.startswith(b"%PDF")  # True
content-type: application/pdf
```
**结果**：PASSED

---

#### test_employee_can_download_own_export_record

**输入**：employee(id=2) 下载自己创建的报告导出记录
```http
GET /api/v1/reports/exports/{id}/download
X-User-Id: 2  X-User-Role: employee
```
**输出**
```python
HTTP 200
response.content == b"PK employee report"
```
**结果**：PASSED

---

### 5.3 权限控制

#### test_employee_cannot_download_other_report_export

**输入**：admin 创建的导出记录，employee(id=2) 尝试下载

**输出**
```python
HTTP 403
```
**结果**：PASSED

---

#### test_student_cannot_download_export

**输入**：student(id=3) 尝试下载任意导出记录

**输出**
```python
HTTP 403
```
**结果**：PASSED

---

#### test_employee_cannot_publish_report_api

**输入**：employee 对已确认报告执行发布
```http
POST /api/v1/reports/{id}/publish
X-User-Id: 2  X-User-Role: employee
```
**输出**
```python
HTTP 403
```
**结果**：PASSED

---

#### test_student_cannot_generate_report_api

**输入**：student 尝试生成报告草稿

**输出**
```python
HTTP 403
```
**结果**：PASSED

---

### 5.4 异常与边界

#### test_download_failed_export_record_returns_error

**输入**：将导出记录状态手动改为 fail 后尝试下载

**输出**
```python
HTTP 400
```
**结果**：PASSED

---

#### test_download_missing_file_returns_not_found_and_audit_log

**输入**：删除实际文件后尝试下载

**输出**
```python
HTTP 404
AuditLog(action_type="download_export").result == "fail"
```
**结果**：PASSED

---

#### test_download_export_path_outside_export_dir_returns_forbidden

**输入**：将导出记录 file_path 篡改为导出目录外的路径

**输出**
```python
HTTP 403
```
**结果**：PASSED

---

#### test_missing_date_range_returns_validation_error

**输入**：请求体缺少 date_start / date_end 字段

**输出**
```python
HTTP 422
```
**结果**：PASSED

---

### 5.5 AI Tools 接口

#### test_ai_tool_query_report_source_data_writes_log

**输入**
```http
POST /api/v1/ai-tools/query_report_source_data
{"report_type": "customer_operation", "date_start": "2026-06-01", "date_end": "2026-06-07",
 "department_id": 1, "owner_user_id": 2, "conversation_id": "conv-1", "trace_id": "trace-1"}
```
**输出**
```python
HTTP 200
data["tool_name"] == "query_report_source_data"
data["result"]["new_leads"] == 1
AiToolCallLog(tool_name="query_report_source_data").trace_id == "trace-1"
```
**结果**：PASSED

---

#### test_ai_tool_query_report_source_data_supports_new_report_type

**输入**：report_type = "student_psych_weekly"

**输出**
```python
HTTP 200
result["total_profiles"] == 2
result["total_alerts"] == 2
```
**结果**：PASSED

---

#### test_ai_tool_query_report_source_data_accepts_blank_optional_ids

**输入**：department_id 和 owner_user_id 传空字符串 `""`

**输出**
```python
HTTP 200
result["department_id"] is None
AiToolCallLog.arguments_summary["department_id"] is None
AiToolCallLog.arguments_summary["owner_user_id"] is None
AiToolCallLog.caller == "dify"
```
**结果**：PASSED

---

#### test_ai_tool_secret_is_required_when_configured

**输入**：设置环境变量 `AI_TOOLS_SECRET=test-ai-tool-secret`，分三种情况：
1. 不带 secret 请求 `GET /api/v1/ai-tools`
2. 携带错误 secret 请求
3. 携带正确 secret 请求

**输出**
```python
# 情况1
HTTP 401
# 情况2
HTTP 401
# 情况3
HTTP 200
result["total_tickets"] == 2
```
**结果**：PASSED

---

## 汇总

| 模块 | 覆盖能力 | 用例数 | 通过 |
|---|---|---|---|
| ReportService | 五类报告生成、草稿确认、权限控制、Dify 失败降级、导出失败审计、模型字段 | 17 | 17 |
| ReportDAO | 五类报告数据聚合、软删除过滤 | 6 | 6 |
| ReportExportService | Word/PDF 模板渲染 | 2 | 2 |
| DifyClient | 6 种响应格式解析、3 种工具失败检测、缺少 API Key | 10 | 10 |
| Report API（集成） | 完整四步流程、文件下载、权限拦截、路径安全、AI Tools 鉴权 | 19 | 19 |
| **合计** | | **54** | **54** |

**所有测试通过，无跳过，无失败。**
