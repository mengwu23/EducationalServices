# 团队交付文档入口

本目录是教育服务系统的团队交付文档入口，面向产品、前端、后端、Dify 工作流、测试和项目管理成员。

需求来源见：[../superpowers/specs/2026-06-09-education-service-system-prd-design.md](../superpowers/specs/2026-06-09-education-service-system-prd-design.md)。

## 主文档

请优先阅读：[team-delivery-guide.md](team-delivery-guide.md)。

原 `01` 到 `10` 的分拆内容已经合并到这份主文档中，便于团队成员按一份材料统一理解项目交付要求。

## 主文档内容

- 项目概览
- 项目架构示意图
- MVC 与后端分层
- DifyClient、DraftService 与 AI Tools 协调关系
- 文件夹结构规划
- 数据库设计约定
- API 设计约定
- Dify 工作流协作说明
- 前端页面规划
- 测试与验收
- 本地启动规划
- 交付检查清单

## 当前交付范围

本目录只交付团队文档，不创建实际代码目录。文档中的 `backend/`、`frontend/`、`dify/`、`scripts/` 均为后续开发阶段的规划结构。

## 关键协作原则

- 文档以开发团队可执行为目标，不写成客户方案。
- 后端按技术分层组织，不按业务模块创建 `modules/` 目录。
- 业务模块通过文件名前缀区分，例如 `customer_judgement_controller.py`。
- 前端统一调用 FastAPI，不直接调用 Dify。
- Dify 负责 AI 编排，FastAPI 负责业务事实、权限、确认和日志。
- Dify 如需数据库能力，只能调用 FastAPI AI Tools 白名单接口。
- 所有 AI 输出默认先进入草稿确认流程。
