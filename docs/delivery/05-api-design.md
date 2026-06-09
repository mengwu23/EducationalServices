# 05 API 设计约定

## 统一前缀

后端 API 统一使用 `/api/v1` 前缀。

接口分组：

```text
/api/v1/auth/*
/api/v1/customer-judgements/*
/api/v1/service-agent/*
/api/v1/enterprise-assistant/*
/api/v1/student-assistant/*
/api/v1/reports/*
/api/v1/drafts/*
/api/v1/audit-logs/*
```

## 分层要求

- Controller 负责声明路由、解析请求和返回响应。
- Controller 不直接调用 Repository。
- Service 负责业务编排和状态流转。
- Repository 负责数据库访问。
- Dify 调用统一通过 `integrations/dify_client.py`。

## 统一响应格式

建议响应结构：

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "trace_id": "request-trace-id"
}
```

错误响应结构：

```json
{
  "code": 40001,
  "message": "参数不完整",
  "data": null,
  "trace_id": "request-trace-id"
}
```

## 草稿确认接口

所有 AI 输出都进入草稿确认流程。建议统一接口：

```text
POST /api/v1/drafts
GET /api/v1/drafts
GET /api/v1/drafts/{draft_id}
POST /api/v1/drafts/{draft_id}/confirm
POST /api/v1/drafts/{draft_id}/reject
```

删除、批量修改、关键状态变更需要额外二次确认：

```text
POST /api/v1/drafts/{draft_id}/second-confirm
```

## 接口命名规则

- 资源名使用复数。
- URL 使用短横线命名。
- 请求体和响应体字段使用 snake_case。
- 前端 TypeScript 类型可使用 camelCase，但 API 层需要处理字段转换或保持一致。

## 权限与日志

- 所有写接口必须校验角色权限。
- 所有确认、发布、删除和批量修改接口必须写操作日志。
- 查询接口需要按角色限制数据范围。
