# 02 MVC 与分层架构

## 总体架构

系统采用前后端分离架构：

- 前端：Vue，负责页面、路由、状态管理、接口调用和用户交互。
- 后端：FastAPI，负责 API、业务编排、权限、数据访问、草稿确认和日志。
- 数据库：MySQL，负责结构化业务数据。
- ORM：SQLAlchemy，负责模型定义和数据访问。
- AI 编排：Dify，负责意图识别、RAG、自然语言解析和报告草稿生成。

## MVC 对应关系

- Model：`models/` 中的 SQLAlchemy ORM，以及 `schemas/` 中的 Pydantic 请求/响应模型。
- View：前端 `views/`、`layouts/`、`components/`。
- Controller：后端 `controllers/` 中的 FastAPI 路由。

FastAPI 不强制 MVC，但本项目用分层目录实现 MVC 协作边界。

## 后端分层职责

- `controllers/`：只负责路由、参数接收、响应返回，不直接访问数据库。
- `services/`：负责业务编排、权限后的业务规则、AI 草稿确认、二次确认和状态流转。
- `repositories/`：只封装 SQLAlchemy 数据访问，不写业务判断。
- `models/`：定义 SQLAlchemy ORM 模型。
- `schemas/`：定义 Pydantic 请求模型、响应模型和内部数据结构。
- `integrations/`：封装外部系统调用，当前主要是 Dify。
- `common/`：放枚举、异常、统一响应、分页等跨层公共对象。
- `core/`：放配置、安全、日志等基础设施。
- `db/`：放数据库连接、会话、Base 和迁移相关入口。

## 调用方向

推荐调用方向：

```text
controller -> service -> repository -> model/db
service -> integration
service -> common
controller -> schema
```

禁止调用方向：

```text
controller -> repository
repository -> service
repository -> controller
model -> service
integration -> controller
```

## Dify 边界

Dify 只生成草稿或解析结果，不直接修改正式业务数据。所有正式写入都必须通过后端 service 层完成权限校验、确认和日志记录。
