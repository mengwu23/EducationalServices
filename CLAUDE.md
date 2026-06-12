# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```powershell
# 启动后端
cd backend && python app/main.py
# 或
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# 运行测试
cd backend && python -m pytest -q          # 全部
cd backend && python -m pytest tests/unit  # 单元测试
cd backend && python -m pytest tests/integration  # 集成测试

# 数据库迁移
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "描述"

# API 文档（开发时）
# http://localhost:8000/docs
```

## 架构概览

**整体分层**：Vue 前端 → FastAPI 控制器 → 业务服务层 → DAO 层 → MySQL

**后端分层**（`backend/app/`）：

- `controllers/` — HTTP 路由处理，`ApiResponse` 封装，角色鉴权
- `services/` — 核心业务逻辑，Dify AI 调用，草稿确认工作流
- `daos/` — SQLAlchemy 查询，不含业务逻辑
- `models/` — ORM 实体（22张表），软删除（`is_deleted`/`deleted_at`），审计字段
- `schemas/` — Pydantic 请求/响应模型
- `common/` — `ApiResponse`、自定义异常、枚举常量
- `core/` — `config.py`（Pydantic BaseSettings 读取 `.env`），`security.py`（角色鉴权）
- `integrations/dify_client.py` — Dify API 客户端，支持 Mock 模式

## 关键设计

### Dify Mock 模式
本地开发时 `.env` 设置 `DIFY_MOCK_ENABLED=true`，跳过真实 Dify 调用，使用预定义模板响应。生产环境设为 `false`。

### 报告草稿工作流
`/api/v1/reports/generate-draft` → AI 生成存入 `AiDraft`（status: pending）→ 用户确认/拒绝 → 确认后写入 `AiReport`（status: published）→ 可导出 Word/PDF。所有操作写 `AuditLog`。

### 鉴权方式
通过请求头传递：`X-User-Id`、`X-User-Role`（默认 admin/1）。`require_roles()` 在服务层做角色校验。Dify 回调接口通过 `AI_TOOLS_SECRET` 验证。

### 统一响应格式
```json
{ "code": 0, "message": "success", "data": {}, "trace_id": "uuid" }
```
`code` 非 0 为业务错误。

## 数据库

- **驱动**：`mysql+pymysql`，配置在 `.env` 的 `DATABASE_URL`
- **迁移**：Alembic，版本文件在 `backend/alembic/versions/`
- **测试**：pytest 用 SQLite in-memory（`conftest.py` 中配置），无需额外清理

## 环境变量（`.env.example`）

关键变量：
- `DIFY_MOCK_ENABLED` — 本地设 `true`
- `AI_TOOLS_SECRET` — Dify 回调鉴权
- `NL2SQL_LLM_API_KEY` / `NL2SQL_LLM_MODEL` — DeepSeek，用于 NL2SQL 功能
- `REPORT_EXPORT_DIR` — Word/PDF 导出目录

## 前端现状

`frontend/src/` 已有路由、store、类型定义骨架，但实现尚未完成，主要开发集中在后端。

## 文档位置

- 项目规格：`docs/delivery/team-delivery-guide.md`
- PRD：`docs/superpowers/specs/2026-06-09-education-service-system-prd-design.md`
- 验收报告：`docs/delivery/report-module-full-acceptance-results.md`
