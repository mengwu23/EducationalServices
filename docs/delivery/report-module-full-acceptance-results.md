# 报告模块全链路验收结果

## 测试执行信息

- **执行时间**：2026-06-11
- **数据库**：MySQL 8 (`education_service_ai_test`)
- **测试模式**：Mock 模式 (`DIFY_MOCK_ENABLED=true`)
- **测试框架**：pytest + FastAPI TestClient

## 测试结果总览

**57 passed, 0 skipped, 0 failed**

| 测试模块 | 用例数 | 通过 | 说明 |
|----------|--------|------|------|
| `test_report_api.py`（集成测试） | 16 | 16 | 报告 CRUD、AI Tools、权限 |
| `test_report_api_mysql.py`（MySQL 集成） | 3 | 3 | 五类报告生成、数据查询、发布导出下载 |
| `test_dify_client.py`（单元） | 12 | 12 | Mock 报告质量、Dify 响应解析 |
| `test_report_dao.py`（单元） | 6 | 6 | 五类报告数据源聚合 |
| `test_report_export_service.py`（单元） | 2 | 2 | Word/PDF 导出 |
| `test_report_service.py`（单元） | 18 | 18 | 草稿生成、确认、发布、权限 |

## 数据库测试数据统计

| 表名 | 记录数 | 说明 |
|------|--------|------|
| crm_lead | 44 | 客户线索（含多种来源、状态、流失） |
| customer_analysis_record | 21 | 客户研判记录（含意向等级分布） |
| event_registration | 13 | 活动报名记录 |
| student_feedback_ticket | 22 | 投诉工单（含待处理/处理中/已解决） |
| employee_daily_report | 20 | 员工日报（2 员工 × 10 天） |
| student_psych_profile | 6 | 学生心理画像 |
| student_psych_alert | 10 | 心理预警记录 |

## 五类报告 Mock 生成验证

全部五类报告均可在 Mock 模式下成功生成草稿、确认、发布、导出 Word/PDF 并下载：

- `complaint_weekly`（投诉处理周报）
- `customer_operation`（全域客户经营分析报告）
- `employee_daily_summary`（员工日报汇总-日）
- `employee_weekly_summary`（员工日报汇总-周）
- `student_psych_weekly`（学生心理健康周报）

## 本次修复事项

1. **Mock 模板缺失变量**：`CUSTOMER_OPERATION` 分支补了 `prev`、`lead_trend`、`churn_source`、`top_churn_source` 声明
2. **seed 数据 `create_time` 不在查询范围**：psych profile 改用 `week_dates(1)`（上周）并显式设 `create_time`
3. **student_id 外键冲突**：`STUDENT_IDS` 改为实际存在的 `student_profile.id` 值
4. **psych profile 唯一约束冲突**：写入前先清理已有数据
5. **日报 `raw_content` 必填**：补了默认值
