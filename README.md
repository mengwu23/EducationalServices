# 教育服务系统

本仓库用于教育/留学服务机构智能服务系统的需求、交付文档和后续代码实现。

当前已完成：

- 产品需求设计：[docs/superpowers/specs/2026-06-09-education-service-system-prd-design.md](docs/superpowers/specs/2026-06-09-education-service-system-prd-design.md)
- 团队交付文档：[docs/delivery/README.md](docs/delivery/README.md)
- 智能报告后端第一版：报告草稿生成、确认、发布、Word/PDF 导出接口、审计日志和 AI Tools 日志。

## 项目技术方向

- 后端：FastAPI + SQLAlchemy
- 前端：Vue
- 数据库：MySQL
- AI 编排：Dify
- 架构：MVC + 分层设计
- 启动方式：本地脚本启动

## 团队协作说明

交付文档面向开发团队成员，主要用于统一项目目标、分层目录、接口约定、Dify 协作方式、测试验收和本地启动流程。

当前已进入后端开发阶段，已创建 `backend/` 并优先实现智能报告模块。`frontend/`、`dify/` 等目录后续按交付文档继续创建。

## 后端测试

```powershell
cd backend
python -m pytest -q
```
