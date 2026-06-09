# 团队交付文档总览

本目录是教育服务系统的团队交付文档入口，面向产品、前端、后端、Dify 工作流、测试和项目管理成员。

需求来源见：[../superpowers/specs/2026-06-09-education-service-system-prd-design.md](../superpowers/specs/2026-06-09-education-service-system-prd-design.md)。

## 建议阅读顺序

1. [01-project-overview.md](01-project-overview.md)：先理解项目目标、角色、模块和交付边界。
2. [02-architecture-mvc-layering.md](02-architecture-mvc-layering.md)：理解 MVC 和后端分层职责。
3. [03-folder-structure.md](03-folder-structure.md)：查看未来代码目录规划。
4. [04-database-design.md](04-database-design.md)：统一数据表、状态枚举和迁移约定。
5. [05-api-design.md](05-api-design.md)：统一接口分组、请求响应和草稿确认接口。
6. [06-dify-workflows.md](06-dify-workflows.md)：明确 Dify 与自研后端的边界。
7. [07-frontend-pages.md](07-frontend-pages.md)：查看四类角色入口和页面清单。
8. [08-test-acceptance.md](08-test-acceptance.md)：确认测试类型和验收场景。
9. [09-local-startup.md](09-local-startup.md)：了解未来本地启动方式。
10. [10-delivery-checklist.md](10-delivery-checklist.md)：交付前逐项检查。

## 当前交付范围

本次只交付团队文档，不创建实际代码目录。文档中的 `backend/`、`frontend/`、`dify/`、`scripts/` 均为后续开发阶段的规划结构。

## 协作原则

- 文档以开发团队可执行为目标，不写成客户方案。
- 后端按技术分层组织，不按业务模块创建 `modules/` 目录。
- 业务模块通过文件名前缀区分，例如 `customer_judgement_controller.py`。
- Dify 负责 AI 编排和草稿生成，自研后端负责业务事实、权限、确认和日志。
- 所有 AI 输出默认先进入草稿确认流程。
