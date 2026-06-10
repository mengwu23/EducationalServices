# Dify 工作流联调说明

本目录存放教育服务系统的 Dify 工作流草案和联调说明。当前已补充智能报告工作流：

- `workflows/reports.yml`：智能报告生成工作流导入草案，已在本地 Dify `1.14.2` 验证可创建应用。

当前工作流节点顺序：

```text
Start -> Parse Report Filters -> Query Report Source Data -> Generate Report JSON -> End
```

其中 `Parse Report Filters` 用于把后端传入的 `filters` JSON 拆成 AI Tool 需要的顶层字段，`Query Report Source Data` 是必须执行的 FastAPI HTTP Tool 调用。

## 1. 边界说明

Dify 负责 AI 编排和报告草稿内容生成，FastAPI 负责业务事实、权限、数据库访问、草稿落库、报告发布、导出和审计日志。

Dify 不能：

- 直连 MySQL。
- 执行任意 SQL。
- 写正式业务表。
- 发布报告。
- 修改草稿状态。

Dify 可以：

- 接收 FastAPI 传入的报告生成参数。
- 调用 FastAPI AI Tools 白名单接口查询受控聚合数据。
- 根据工具返回数据生成结构化报告草稿。

## 2. 报告工作流输入

FastAPI 调用 Dify `/v1/workflows/run` 时传入：

```json
{
  "inputs": {
    "report_type": "complaint_weekly",
    "source_data": "{}",
    "filters": "{\"date_start\":\"2026-06-01\",\"date_end\":\"2026-06-07\",\"department_id\":1,\"owner_user_id\":null}",
    "trace_id": "report-trace-id"
  },
  "response_mode": "blocking",
  "user": "education-service-backend"
}
```

说明：

- `source_data` 和 `filters` 在 Dify Start 节点里按 `paragraph` 接收，推荐后端传 JSON 字符串。
- 如果后端直接传 JSON 对象，`Parse Report Filters` 节点也保留了对象兼容逻辑，但真实联调时以当前 Dify 版本实际校验为准。
- `filters` 至少包含：

```json
{
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1,
  "owner_user_id": null
}
```

`report_type` 允许值：

| 报告 | report_type |
| --- | --- |
| 投诉处理周报 | `complaint_weekly` |
| 全域客户经营分析报告 | `customer_operation` |
| 员工日报汇总报告（日） | `employee_daily_summary` |
| 员工日报汇总报告（周） | `employee_weekly_summary` |
| 学生心理健康周报 | `student_psych_weekly` |

## 3. 必须调用的 AI Tool

报告工作流每次运行都必须调用 FastAPI AI Tool：

```text
POST /api/v1/ai-tools/query_report_source_data
```

推荐 Dify HTTP Tool URL：

```text
{{#env.AI_TOOLS_BASE_URL#}}/api/v1/ai-tools/query_report_source_data
```

HTTP Tool 请求体由 `Parse Report Filters` 节点输出拼装：

```json
{
  "report_type": "complaint_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1,
  "owner_user_id": null,
  "caller": "dify",
  "conversation_id": "dify-conversation-id",
  "trace_id": "report-trace-id"
}
```

响应格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "tool_name": "query_report_source_data",
    "result": {
      "report_type": "complaint_weekly",
      "date_start": "2026-06-01",
      "date_end": "2026-06-07",
      "department_id": 1,
      "total_tickets": 2,
      "status_counts": {
        "open": 1,
        "closed": 1
      }
    },
    "draft_id": null,
    "requires_confirmation": false
  },
  "trace_id": "report-trace-id"
}
```

生成报告时以 `data.result` 为准。后端传给 Dify 的 `source_data` 只作为初始上下文，不作为最终数据口径。

## 4. 报告输出契约

Dify 工作流最终输出变量名必须是：

```text
report
```

后端 `DifyClient` 支持以下返回形式：

- `outputs.report` 是 JSON 对象。
- `outputs.report` 是 JSON 字符串。
- `outputs.text` 或 `outputs.result` 是 JSON 字符串。

推荐输出：

```json
{
  "title": "投诉处理周报",
  "summary": "本周期投诉处理整体平稳。",
  "sections": [
    {
      "heading": "投诉概览",
      "content": "本周期共处理投诉 2 条，其中 open 1 条，closed 1 条。",
      "metrics": [
        {"name": "total_tickets", "value": 2},
        {"name": "open", "value": 1},
        {"name": "closed", "value": 1}
      ]
    }
  ],
  "risks": [],
  "recommendations": ["持续跟进未关闭投诉。"],
  "source_refs": ["query_report_source_data", "student_feedback_ticket"]
}
```

输出要求：

- 只输出 JSON，不输出 Markdown 代码块。
- `title` 必填。
- `sections` 至少包含 2 个章节。
- `metrics` 必须来自 AI Tool 返回数据。
- 不能编造没有数据支撑的指标。
- 不能包含 SQL 或数据库写入动作。

## 5. Prompt 模板要点

系统 Prompt 应包含以下约束：

```text
你是教育服务系统的智能报告生成助手。
你只能基于 FastAPI AI Tool 返回的受控聚合数据生成报告草稿。
你不能直接连接数据库，不能输出 SQL，不能发布报告，不能写入任何业务表。
你不能编造指标。无法从工具数据判断的信息，必须写入 risks 或 recommendations。
你必须只输出一个 JSON 对象，不要输出 Markdown，不要输出代码块，不要输出解释性前后缀。
```

用户 Prompt 应提供：

- `report_type`
- 后端初始 `source_data`
- 后端筛选条件 `filters`
- FastAPI AI Tool 返回结果

## 6. 导入和联调步骤

1. 在 Dify 控制台创建 Workflow App。
2. 导入或参考 `workflows/reports.yml` 配置工作流。
3. 配置 Dify 环境变量：

```text
AI_TOOLS_BASE_URL=http://host.docker.internal:8000
```

如果 Dify 和 FastAPI 都运行在宿主机上，也可以改为 `http://127.0.0.1:8000`。如果 Dify 运行在 Docker 容器内，通常使用 `host.docker.internal` 访问宿主机 FastAPI。

4. 在后端 `.env` 中配置：

```text
DIFY_API_BASE_URL=http://127.0.0.1:5001
DIFY_API_KEY=你的 Dify App API Key
DIFY_MOCK_ENABLED=false
```

5. 启动 FastAPI 后端。
6. 调用后端报告接口：

```text
POST /api/v1/reports/generate-draft
```

7. 检查结果：

- Dify 工作流执行成功。
- `Parse Report Filters` 节点能从 `filters` 中拆出 `date_start`、`date_end`、`department_id`、`owner_user_id`。
- Dify 工作流调用了 `query_report_source_data`。
- 后端 `ai_tool_call_log` 有工具调用记录。
- 后端 `ai_draft` 生成报告草稿。
- 草稿 `content_json` 包含 `title`、`summary`、`sections`。

8. 模型配置：

- `reports.yml` 默认使用本地 Dify 已安装的 `langgenius/deepseek/deepseek` / `deepseek-chat`。
- 如果团队环境使用 OpenAI 或其他供应商，在 Dify 画布中打开 `Generate Report JSON` 节点切换模型即可。

## 7. 五类报告最小测试输入

投诉处理周报：

```json
{
  "report_type": "complaint_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1
}
```

客户经营分析报告：

```json
{
  "report_type": "customer_operation",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1,
  "owner_user_id": 2
}
```

员工日报汇总报告（日）：

```json
{
  "report_type": "employee_daily_summary",
  "date_start": "2026-06-02",
  "date_end": "2026-06-02",
  "department_id": 1
}
```

员工日报汇总报告（周）：

```json
{
  "report_type": "employee_weekly_summary",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1
}
```

学生心理健康周报：

```json
{
  "report_type": "student_psych_weekly",
  "date_start": "2026-06-01",
  "date_end": "2026-06-07",
  "department_id": 1
}
```

## 8. 常见问题

如果 Dify 返回后端解析失败，检查：

- 最终输出变量是否命名为 `report`。
- `report` 是否是 JSON 对象或 JSON 字符串。
- JSON 是否包含 `title`。
- 是否输出了 Markdown 代码块。

如果 AI Tool 调用失败，检查：

- `AI_TOOLS_BASE_URL` 是否能从 Dify 运行环境访问。
- FastAPI 后端是否启动。
- 请求路径是否为 `/api/v1/ai-tools/query_report_source_data`。
- 请求体是否包含 `report_type`、`date_start`、`date_end`。
- `filters` 是否是合法 JSON，且能被 `Parse Report Filters` 节点解析。

如果报告内容指标不对，检查：

- Dify 是否实际使用了 `data.result`。
- Prompt 是否要求以 AI Tool 返回数据为准。
- Dify 是否编造了工具结果里不存在的指标。
