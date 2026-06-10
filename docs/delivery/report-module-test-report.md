# 报告模块全量测试报告

## 1. 测试结论

本次对报告模块 DAO、Service、API、AI Tool 自动化用例执行全量测试，覆盖五类报告的源数据聚合、草稿生成、草稿确认、报告发布、报告导出、权限控制、参数校验、Dify 失败处理和 AI Tool 调用日志。

测试结果：30 个用例全部通过。

```text
30 passed in 1.81s
```

## 2. 测试命令

执行目录：

```text
D:\code_progarm\Education_Service_System\backend
```

执行命令：

```powershell
python -m pytest tests/unit/test_report_dao.py tests/unit/test_report_service.py tests/integration/test_report_api.py -q
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

## 4. 覆盖报告类型

| 报告 | `report_type` |
| --- | --- |
| 投诉处理周报 | `complaint_weekly` |
| 全域客户经营分析报告 | `customer_operation` |
| 员工日报汇总报告（日） | `employee_daily_summary` |
| 员工日报汇总报告（周） | `employee_weekly_summary` |
| 学生心理健康周报 | `student_psych_weekly` |

## 5. 测试输入数据

| 类型 | 输入 |
| --- | --- |
| 管理员 | `id=1`, `username=admin`, `user_type=admin` |
| 员工 | `id=2`, `username=employee`, `user_type=employee` |
| 学生 | `id=3`, `username=student`, `user_type=student` |
| 部门 | `id=1`, `department_name=咨询一部` |
| 投诉工单 | 2 条有效数据，状态分别为 `open`、`closed` |
| 客户经营数据 | 1 条线索、1 条研判记录、1 条活动报名 |
| 员工日报 | 3 条部门内有效数据，覆盖 `submitted`、`draft`、`archived`；另有跨部门和逻辑删除数据用于过滤验证 |
| 学生心理画像 | 2 条部门内有效画像；另有逻辑删除画像用于过滤验证 |
| 学生心理预警 | 2 条部门内有效预警；另有逻辑删除预警用于过滤验证 |

公共请求参数：

| 参数 | 输入 |
| --- | --- |
| 开始日期 | `2026-06-01` |
| 结束日期 | `2026-06-07` |
| 部门 ID | `1` |
| 负责人用户 ID | `2` |

## 6. 用例结果

| 范围 | 用例 | 结果 |
| --- | --- | --- |
| DAO | 投诉周报按日期和部门聚合 | 通过 |
| DAO | 客户经营按负责人聚合 | 通过 |
| DAO | 员工日报（日）按单日和部门聚合 | 通过 |
| DAO | 员工日报（周）按日期范围和部门聚合 | 通过 |
| DAO | 学生心理健康周报按部门聚合 | 通过 |
| DAO | 草稿、报告、导出记录逻辑删除过滤 | 通过 |
| Service | 管理员生成投诉周报草稿 | 通过 |
| Service | 报告相关模型 `update_time` 和 `is_deleted` 默认值 | 通过 |
| Service | 员工生成客户经营分析报告草稿 | 通过 |
| Service | 管理员生成三类新增报告草稿 | 通过 |
| Service | 员工生成三类新增报告草稿 | 通过 |
| Service | 管理员确认三类新增报告草稿生成正式报告 | 通过 |
| Service | 员工不能发布报告 | 通过 |
| Service | 管理员确认草稿生成 `AiReport` | 通过 |
| Service | Dify 失败时生成失败草稿和审计日志 | 通过 |
| Service | Word 导出生成文件和导出记录 | 通过 |
| Service | PDF 转换失败写入失败导出记录和审计日志 | 通过 |
| API | `generate-draft` 支持五类报告 | 通过 |
| API | 生成、确认、发布、Word 导出完整流程 | 通过 |
| API | 员工不能通过 API 发布报告 | 通过 |
| API | 学生不能通过 API 生成报告草稿 | 通过 |
| API | 缺少日期范围返回校验错误 | 通过 |
| AI Tool | 查询客户经营数据并写入工具调用日志 | 通过 |
| AI Tool | 查询学生心理健康周报数据 | 通过 |

## 7. 关键输出示例

### 员工日报（日）DAO 输出

```json
{
  "report_type": "employee_daily_summary",
  "date_start": "2026-06-02",
  "date_end": "2026-06-02",
  "department_id": 1,
  "total_reports": 2,
  "status_counts": {
    "draft": 1,
    "submitted": 1
  },
  "submitted_reports": 1,
  "draft_reports": 1,
  "archived_reports": 0,
  "risk_reports": 1,
  "tomorrow_plan_reports": 2
}
```

### 员工日报（周）DAO 输出

```json
{
  "report_type": "employee_weekly_summary",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1,
  "total_reports": 3,
  "distinct_employees": 2,
  "status_counts": {
    "archived": 1,
    "draft": 1,
    "submitted": 1
  },
  "daily_trend": {
    "2026-06-02": 2,
    "2026-06-03": 1
  },
  "risk_reports": 2
}
```

### 学生心理健康周报 DAO 输出

```json
{
  "report_type": "student_psych_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1,
  "total_profiles": 2,
  "risk_level_counts": {
    "high": 1,
    "medium": 1
  },
  "emotion_tag_counts": {
    "anxious": 1,
    "stable": 1
  },
  "average_emotion_score": 55.0,
  "total_alerts": 2,
  "alert_status_counts": {
    "pending": 1,
    "resolved": 1
  },
  "alert_risk_level_counts": {
    "high": 1,
    "medium": 1
  }
}
```

## 8. 实际 pytest 输出

```text
..............................                                           [100%]
30 passed in 1.81s
```

## 9. 结论

报告模块当前自动化测试已覆盖五类报告的核心后端闭环：数据聚合、Dify/Mock 草稿生成、人工确认、正式报告发布、导出和审计记录。新增报告类型继续复用统一 API、统一 `DraftService`、统一 `DifyClient` 和统一 AI Tool 入口，不新增数据库表或迁移。
