# 智能报告模块五类报告测试报告

**测试时间**：2026-06-12  
**测试方式**：启动后端 `backend/app/main.py`，通过 `/api/v1/reports/generate-draft` 逐类生成报告草稿正文。  
**输出文件**：`docs/delivery/report-five-types-generated-2026-06-12.md`

## 测试范围

本次覆盖五类智能报告：

| 序号 | 报告名称 | report_type | 结果 |
|---|---|---|---|
| 1 | 投诉处理周报 | `complaint_weekly` | 生成成功 |
| 2 | 全域客户经营分析报告 | `customer_operation` | 生成成功 |
| 3 | 员工日报智能汇总报告（日） | `employee_daily_summary` | 生成成功 |
| 4 | 员工日报智能汇总报告（周） | `employee_weekly_summary` | 生成成功 |
| 5 | 学生心理健康周报 | `student_psych_weekly` | 生成成功 |

## 输出校验

- Markdown 文件已生成：`docs/delivery/report-five-types-generated-2026-06-12.md`
- 文件大小：约 18 KB
- 文件包含 5 个报告章节
- 未发现 `生成失败` 标记

## 执行命令

```bash
python -m backend.scripts.generate_reports_md docs\delivery\report-five-types-generated-2026-06-12.md
```

生成结果：

```text
投诉处理周报：完成
全域客户经营分析报告：完成
员工日报智能汇总报告（日）：完成
员工日报智能汇总报告（周）：完成
学生心理健康周报：完成
```

## 自动化验证

```bash
python -m pytest backend\tests\integration\test_report_api.py::test_generate_draft_api_supports_five_report_types -q
```

结果：

```text
1 passed
```

```bash
python -m pytest backend\tests\integration\test_report_api_mysql.py::test_mysql_five_report_types_generate_drafts -q
```

结果：

```text
1 skipped
```

跳过原因：当前环境未设置 `MYSQL_TEST_DATABASE_URL`，该专项测试未执行。

## 结论

智能报告模块五类报告正文均已通过真实后端接口生成，并保存为 Markdown 文件。核心五类报告生成 API 自动化用例通过。
