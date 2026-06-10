# 教育服务系统团队交付指南

本文档面向教育服务系统开发团队，用于统一项目目标、分层架构、目录规划、数据库约定、接口边界、Dify 协作方式、前端页面、测试验收和本地启动流程。

需求来源：[../superpowers/specs/2026-06-09-education-service-system-prd-design.md](../superpowers/specs/2026-06-09-education-service-system-prd-design.md)。

当前阶段只交付团队文档，不创建实际代码目录。本文中出现的 `backend/`、`frontend/`、`dify/`、`scripts/` 均为后续开发阶段的规划结构。

## 1. 项目概览

教育服务系统是一套面向教育/留学服务机构的智能服务平台，用于支持访客咨询、客户研判、员工内部业务处理、学生自助服务和管理报告生成。

系统采用 FastAPI + Vue + MySQL + SQLAlchemy，并通过 Dify 提供 Agent 编排、RAG 问答、自然语言操作解析和报告草稿生成能力。

### 用户角色

- 管理员：维护系统配置、知识库、报告、角色权限和全量业务数据。
- 员工：处理客户、客服、日报、学生业务、投诉、请假和报告。
- 学生：提交请假、投诉建议，查询成绩、考务、申请进度，使用学生助手。
- 访客：通过客服 Agent 咨询公司、业务、留学政策、课程项目和活动报名。

### 五大业务模块

- 客户研判：上传客户资料，基于用户画像规则生成匹配结论草稿。
- 客服 Agent：处理访客咨询、FAQ、课程项目推荐和活动报名。
- 企业智能助手：支持员工通过自然语言查询和操作内部业务数据。
- 学生智能助手：支持学生请假、投诉、情绪记录、考务查询和生活支持。
- 智能报告：生成客户经营、日报、心理健康、投诉处理等报告草稿。

### 核心约束

- 前端不直接调用 Dify，只调用 FastAPI。
- Dify 不直连 MySQL，不执行任意 SQL。
- 所有 AI 输出先生成草稿，人工确认后生效。
- 删除、批量修改、关键状态变更必须二次确认。
- 所有写操作、确认操作、报告发布和客服对外回复必须记录日志。

## 2. 项目架构示意图

Vue 是统一前端，不拆独立 AI 前端应用。Agent 聊天组件只是业务页面内组件，和表单、列表、详情组件同级。所有前端组件统一通过 `frontend/api/*` 调用 FastAPI。

后端由 Business Service 统一编排业务流程。`DifyClient` 只负责调用 Dify，不写草稿、不碰 DAO。`DraftService` 只管理草稿生命周期，不调用 Dify。Dify 如需查询数据或创建草稿，只能通过 FastAPI 的 AI Tools 白名单接口回调。

```mermaid
flowchart LR
  Admin["管理员"]
  Employee["员工"]
  Student["学生"]
  Visitor["访客"]

  subgraph FE["统一 Vue 前端"]
    Pages["角色页面 / 业务页面"]
    BizComponents["普通业务组件\n表单 / 列表 / 详情"]
    AgentComponents["Agent 聊天组件\n客服 / 企业助手 / 学生助手"]
    FrontApi["前端 API Client\nfrontend/api/*"]
  end

  subgraph API["FastAPI 后端"]
    Controller["Controllers 路由层"]
    BizService["Business Services 业务编排"]
    DraftService["DraftService 草稿生命周期"]
    DifyClient["DifyClient 调用适配器"]
    DAO["DAO 数据访问"]
    AiToolController["AI Tool Controller"]
    AiTools["AI Tools 白名单工具"]
  end

  subgraph DATA["数据层"]
    Model["Models / Schemas"]
    DB[("MySQL 数据库")]
    DraftTable[("Draft 草稿表")]
    AuditLog[("AuditLog 操作日志")]
  end

  subgraph AI["Dify 平台"]
    Dify["Dify 工作流"]
    KB[("知识库 / Prompt")]
  end

  Admin --> Pages
  Employee --> Pages
  Student --> Pages
  Visitor --> Pages

  Pages --> BizComponents
  Pages --> AgentComponents
  BizComponents --> FrontApi
  AgentComponents --> FrontApi
  FrontApi --> Controller

  Controller --> BizService
  BizService --> DraftService
  BizService --> DifyClient
  BizService --> DAO

  DraftService --> DraftTable
  DraftService --> AuditLog
  DraftService --> DAO

  DAO --> Model
  Model --> DB

  DifyClient --> Dify
  Dify --> KB
  Dify --> DifyClient

  Dify --> AiToolController
  AiToolController --> AiTools
  AiTools --> BizService
  AiTools --> DraftService
  AiTools --> DAO

  BizService --> AuditLog
```

## 3. MVC 与后端分层

### MVC 对应关系

- Model：`models/` 中的 SQLAlchemy ORM，以及 `schemas/` 中的 Pydantic 请求/响应模型。
- View：前端 `views/`、`layouts/`、`components/`。
- Controller：后端 `controllers/` 中的 FastAPI 路由。

FastAPI 不强制 MVC，但本项目通过技术分层目录实现 MVC 协作边界。

### 后端分层职责

- `controllers/`：接收前端请求和 Dify 工具回调请求，负责路由、参数接收、响应返回。
- `services/`：业务编排、权限后的业务规则、AI 草稿确认、二次确认和状态流转。
- `daos/`：DAO 数据访问层，只封装 SQLAlchemy 查询和写入，不写业务判断。
- `models/`：定义 SQLAlchemy ORM 模型。
- `schemas/`：定义 Pydantic 请求模型、响应模型和内部数据结构。
- `ai_tools/`：封装给 Dify 调用的白名单工具，不暴露原始 DAO。
- `integrations/`：封装外部平台客户端，当前主要是 Dify API Client。
- `common/`：放枚举、异常、统一响应、分页等跨层公共对象。
- `core/`：放配置、安全、日志等基础设施。
- `db/`：放数据库连接、会话、Base 和迁移相关入口。

### 调用方向

推荐调用方向：

```text
controller -> service
service -> dao
service -> draft_service
service -> dify_client
service -> common
dao -> model/db
ai_tools -> service / draft_service / dao
controller -> schema
```

禁止调用方向：

```text
controller -> dao
dao -> service
dao -> controller
model -> service
dify_client -> dao
dify_client -> draft_service
draft_service -> dify_client
frontend -> dify
dify -> mysql
dify -> dao
```

## 4. DifyClient、DraftService 与 AI Tools 协调关系

### 标准 AI 业务流程

```text
前端业务页面
  -> FastAPI Controller
  -> Business Service
  -> DraftService 创建草稿壳，状态=生成中
  -> DifyClient 调用 Dify
  -> Dify 按需调用 FastAPI AI Tools
  -> DifyClient 返回结果
  -> Business Service 校验和结构化结果
  -> DraftService 更新草稿，状态=待确认或生成失败
  -> 前端在当前业务页面展示草稿
```

### 各层边界

- `Business Service` 是一次 AI 业务流程的编排者。
- `DifyClient` 只做 Dify 请求、响应解析、异常、超时和 `trace_id` 传递。
- `DifyClient` 不直接调用 DAO，不直接写草稿表。
- `DraftService` 统一管理草稿状态、确认、驳回、二次确认和草稿日志。
- `DraftService` 不调用 DifyClient。
- 业务 Service 决定 Dify 结果属于哪种草稿，例如客服回复草稿、报告草稿、客户研判草稿、业务操作草稿。
- 前端的草稿确认入口嵌入各业务页面，不把 AI 草稿确认做成独立业务模块。

### AI Tools 调用流程

```text
Dify 工作流
  -> POST /api/v1/ai-tools/{tool_name}
  -> AI Tool Controller
  -> AI Tools
  -> Service / DraftService / DAO
  -> 返回受控结果给 Dify
```

AI Tools 分两类：

- 查询工具：可以通过 Service 或 DAO 查询受限数据摘要，返回给 Dify。
- 写入工具：不能直接写正式业务表，只能通过 DraftService 创建草稿或待二次确认操作。

AI Tools 禁止提供通用 SQL 执行能力，禁止让 Dify 传入任意 SQL。

## 5. 文件夹结构规划

本节只描述未来代码目录规划。当前文档阶段不创建实际代码骨架。

### 后端目录

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      logging.py
    db/
      session.py
      base.py
    common/
      enums.py
      exceptions.py
      responses.py
      pagination.py
    controllers/
      auth_controller.py
      customer_judgement_controller.py
      service_agent_controller.py
      enterprise_assistant_controller.py
      student_assistant_controller.py
      report_controller.py
      draft_controller.py
      audit_log_controller.py
      ai_tool_controller.py
    services/
      auth_service.py
      customer_judgement_service.py
      service_agent_service.py
      enterprise_assistant_service.py
      student_assistant_service.py
      report_service.py
      draft_service.py
      audit_log_service.py
    daos/
      user_dao.py
      customer_judgement_dao.py
      service_agent_dao.py
      enterprise_assistant_dao.py
      student_assistant_dao.py
      report_dao.py
      draft_dao.py
      audit_log_dao.py
    models/
      user.py
      customer_judgement.py
      service_agent.py
      enterprise_assistant.py
      student_assistant.py
      report.py
      draft.py
      audit_log.py
    schemas/
      auth_schema.py
      customer_judgement_schema.py
      service_agent_schema.py
      enterprise_assistant_schema.py
      student_assistant_schema.py
      report_schema.py
      draft_schema.py
      audit_log_schema.py
      ai_tool_schema.py
    ai_tools/
      registry.py
      customer_judgement_tools.py
      service_agent_tools.py
      enterprise_assistant_tools.py
      student_assistant_tools.py
      report_tools.py
    integrations/
      dify_client.py
    scripts/
      create_admin.py
  alembic/
  tests/
    unit/
    integration/
    e2e/
  requirements.txt
  .env.example
  start_backend.ps1
```

### 前端目录

```text
frontend/
  src/
    main.ts
    App.vue
    router/
      index.ts
    api/
      request.ts
      auth.ts
      customerJudgement.ts
      serviceAgent.ts
      enterpriseAssistant.ts
      studentAssistant.ts
      reports.ts
      drafts.ts
      auditLogs.ts
    stores/
      authStore.ts
      draftStore.ts
    layouts/
      AdminLayout.vue
      EmployeeLayout.vue
      StudentLayout.vue
      VisitorLayout.vue
    views/
      admin/
      employee/
      student/
      visitor/
    components/
      common/
      forms/
      tables/
      chat/
      reports/
    types/
      auth.ts
      customerJudgement.ts
      serviceAgent.ts
      enterpriseAssistant.ts
      studentAssistant.ts
      reports.ts
      drafts.ts
    utils/
  package.json
  .env.example
  start_frontend.ps1
```

### Dify 与脚本目录

```text
dify/
  workflows/
    customer_judgement.yml
    service_agent.yml
    enterprise_assistant.yml
    student_assistant.yml
    reports.yml
  prompts/
  knowledge-base/
  README.md

scripts/
  start_all.ps1
  init_mysql.sql
```

### 命名规则

- 后端按技术分层建目录，不创建 `app/modules/`。
- 业务模块通过文件名前缀区分。
- Python 文件使用小写蛇形命名。
- 前端 API 和类型文件使用业务名区分。
- 报告模块后端文件统一使用 `report`，前端文件可使用 `reports`。

## 6. 数据库设计约定

数据库使用 MySQL，ORM 使用 SQLAlchemy，迁移使用 Alembic。

数据库设计目标是先支撑第一版业务闭环，同时保证 AI 草稿确认、AI Tools 调用和操作审计有稳定落点。CRM、教务、申请进度等数据先在本系统内维护。

### 表结构来源

业务基础表来自 `C:/Users/14470/xwechat_files/wxid_awv937a0yzpz22_5200/msg/file/2026-06/项目sql.txt`。该 SQL 文件策略是先建基础必需表，把复杂日志、AI 审计和细粒度分析表放到后续扩展。

本开发文档在这 18 张基础业务表上补充 3 张 AI 公共能力表：

- `ai_draft`：支撑 DraftService 草稿生命周期。
- `audit_log`：支撑确认、驳回、二次确认、正式写入、发布和导出审计。
- `ai_tool_call_log`：支撑 Dify 调用 AI Tools 的工具级审计。

### 第一阶段必建表清单

第一阶段共 21 张表：18 张基础业务表 + 3 张 AI 公共能力表。

组织与账号：

- `sys_department`
- `sys_user`
- `employee_profile`
- `student_profile`

客户与销售：

- `crm_lead`
- `customer_analysis_record`

员工业务：

- `employee_daily_report`

学生业务：

- `student_score`
- `student_leave_request`
- `student_feedback_ticket`
- `student_psych_profile`
- `student_psych_alert`
- `academic_event`
- `student_application_progress`

客服与内容：

- `course_project`
- `event_lecture`
- `event_registration`
- `faq_qa`

AI 公共能力：

- `ai_draft`
- `audit_log`
- `ai_tool_call_log`

### 表结构摘要

| 表名 | 所属模块 | 用途 | 关键关联 |
| --- | --- | --- | --- |
| `sys_department` | 组织与账号 | 部门组织架构、部门汇总、组织查询 | 自关联 `parent_id` |
| `sys_user` | 组织与账号 | 统一账号、身份识别、权限基础 | 被员工、学生、审计表引用 |
| `employee_profile` | 组织与账号 | 员工档案、岗位角色、部门归属 | `sys_user`、`sys_department` |
| `student_profile` | 组织与账号 | 学生基础档案和学生业务主对象 | `sys_user`、员工顾问 |
| `crm_lead` | 客户与销售 | 意向客户、销售漏斗、客户状态 | 负责员工、活动报名、客户研判 |
| `customer_analysis_record` | 客户研判 | 客户资料、AI 研判结果、匹配依据 | `crm_lead`、员工、学生 |
| `employee_daily_report` | 企业智能助手 | 员工日报、AI 摘要、日报汇总 | 员工、部门 |
| `student_score` | 学生业务 | 学生成绩录入与查询 | 学生、录入员工 |
| `student_leave_request` | 学生业务 | 请假申请、员工审批、结果查询 | 学生、审批员工 |
| `student_feedback_ticket` | 学生业务 | 投诉建议、售后反馈、跟进处理 | 学生、处理员工 |
| `student_psych_profile` | 学生业务 | 学生心理画像、最新情绪状态 | 学生、更新员工 |
| `student_psych_alert` | 学生业务 | 心理风险预警、老师跟进 | 学生、跟进老师 |
| `course_project` | 客服与内容 | 课程项目、推荐匹配、增值服务 | 客服 Agent、学生助手 |
| `event_lecture` | 客服与内容 | 活动讲座、时间地点、名额状态 | 活动报名 |
| `event_registration` | 客服与内容 | 活动报名闭环、报名状态统计 | 活动、意向客户 |
| `faq_qa` | 客服与内容 | FAQ、制度问答、海外生活问答 | 客服 Agent、学生助手 |
| `academic_event` | 学生业务 | 论文 DDL、考试、课程截止提醒 | 学生 |
| `student_application_progress` | 学生业务 | 文书、院校申请、签证等进度查询 | 学生、负责员工 |
| `ai_draft` | AI 公共能力 | AI 输出草稿、待确认操作、二次确认 | 用户、业务对象 |
| `audit_log` | AI 公共能力 | 操作审计、确认审计、发布审计 | 用户、草稿、业务对象 |
| `ai_tool_call_log` | AI 公共能力 | Dify 调用 AI Tools 的工具审计 | 草稿、会话、链路 |

### 三张 AI 公共表 SQL

以下 3 张表是对 `项目sql.txt` 的第一阶段补充，用来让数据库设计与 `DraftService`、`DifyClient`、`AI Tools` 架构保持一致。

```sql
CREATE TABLE IF NOT EXISTS ai_draft (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'AI草稿ID',
    draft_no VARCHAR(50) NOT NULL COMMENT '草稿编号',
    draft_type VARCHAR(50) NOT NULL COMMENT '草稿类型：customer_analysis/customer_reply/activity_signup/business_operation/complaint_summary/emotion_record/report',
    biz_module VARCHAR(50) NOT NULL COMMENT '业务模块：customer_judgement/service_agent/enterprise_assistant/student_assistant/report',
    biz_object_type VARCHAR(80) DEFAULT NULL COMMENT '关联业务对象类型',
    biz_object_id BIGINT DEFAULT NULL COMMENT '关联业务对象ID',
    status VARCHAR(30) NOT NULL DEFAULT 'generating' COMMENT '草稿状态：generating生成中/pending_confirm待确认/confirmed已确认/rejected已驳回/generation_failed生成失败/pending_second_confirm待二次确认',
    content_json JSON NOT NULL COMMENT '草稿内容JSON',
    source_trace_id VARCHAR(100) DEFAULT NULL COMMENT '来源链路ID',
    created_by BIGINT DEFAULT NULL COMMENT '创建人用户ID',
    confirmed_by BIGINT DEFAULT NULL COMMENT '确认人用户ID',
    confirmed_time DATETIME DEFAULT NULL COMMENT '确认时间',
    reject_reason VARCHAR(500) DEFAULT NULL COMMENT '驳回原因',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_ai_draft_no (draft_no),
    KEY idx_ai_draft_type (draft_type),
    KEY idx_ai_draft_module (biz_module),
    KEY idx_ai_draft_object (biz_object_type, biz_object_id),
    KEY idx_ai_draft_status (status),
    KEY idx_ai_draft_created_by (created_by),
    KEY idx_ai_draft_confirmed_by (confirmed_by),
    CONSTRAINT fk_ai_draft_created_by FOREIGN KEY (created_by) REFERENCES sys_user(id),
    CONSTRAINT fk_ai_draft_confirmed_by FOREIGN KEY (confirmed_by) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI草稿公共表';

CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '审计日志ID',
    operator_user_id BIGINT DEFAULT NULL COMMENT '操作人用户ID',
    operator_role VARCHAR(50) DEFAULT NULL COMMENT '操作人角色',
    action_type VARCHAR(80) NOT NULL COMMENT '操作类型：create/update/delete/confirm/reject/second_confirm/publish/export/tool_call',
    biz_module VARCHAR(50) NOT NULL COMMENT '业务模块',
    biz_object_type VARCHAR(80) DEFAULT NULL COMMENT '业务对象类型',
    biz_object_id BIGINT DEFAULT NULL COMMENT '业务对象ID',
    before_json JSON DEFAULT NULL COMMENT '操作前数据摘要',
    after_json JSON DEFAULT NULL COMMENT '操作后数据摘要',
    draft_id BIGINT DEFAULT NULL COMMENT '关联AI草稿ID',
    trace_id VARCHAR(100) DEFAULT NULL COMMENT '链路追踪ID',
    result VARCHAR(30) NOT NULL DEFAULT 'success' COMMENT '执行结果：success成功/fail失败',
    error_message VARCHAR(1000) DEFAULT NULL COMMENT '失败原因',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    KEY idx_audit_operator (operator_user_id),
    KEY idx_audit_action_type (action_type),
    KEY idx_audit_module_object (biz_module, biz_object_type, biz_object_id),
    KEY idx_audit_draft_id (draft_id),
    KEY idx_audit_trace_id (trace_id),
    KEY idx_audit_create_time (create_time),
    CONSTRAINT fk_audit_operator FOREIGN KEY (operator_user_id) REFERENCES sys_user(id),
    CONSTRAINT fk_audit_draft FOREIGN KEY (draft_id) REFERENCES ai_draft(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统操作审计日志表';

CREATE TABLE IF NOT EXISTS ai_tool_call_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'AI工具调用日志ID',
    tool_name VARCHAR(100) NOT NULL COMMENT '工具名称',
    caller VARCHAR(50) NOT NULL DEFAULT 'dify' COMMENT '调用方：dify/other',
    conversation_id VARCHAR(100) DEFAULT NULL COMMENT 'Dify会话ID',
    trace_id VARCHAR(100) DEFAULT NULL COMMENT '链路追踪ID',
    arguments_summary JSON DEFAULT NULL COMMENT '调用参数摘要',
    result_summary JSON DEFAULT NULL COMMENT '调用结果摘要',
    draft_id BIGINT DEFAULT NULL COMMENT '关联AI草稿ID',
    status VARCHAR(30) NOT NULL DEFAULT 'success' COMMENT '调用状态：success成功/fail失败',
    error_message VARCHAR(1000) DEFAULT NULL COMMENT '失败原因',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    KEY idx_tool_call_tool_name (tool_name),
    KEY idx_tool_call_caller (caller),
    KEY idx_tool_call_conversation (conversation_id),
    KEY idx_tool_call_trace_id (trace_id),
    KEY idx_tool_call_draft_id (draft_id),
    KEY idx_tool_call_create_time (create_time),
    CONSTRAINT fk_tool_call_draft FOREIGN KEY (draft_id) REFERENCES ai_draft(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI工具调用日志表';
```

### 数据库与 AI 架构对应关系

- `DraftService` 只操作 `ai_draft` 和必要业务确认动作。
- `DifyClient` 不直接操作任何表。
- `AI Tools` 查询类工具可读取业务表摘要。
- `AI Tools` 写入类工具只能创建 `ai_draft` 或待二次确认操作，不能直接写正式业务状态。
- 所有 AI Tools 调用必须写入 `ai_tool_call_log`。
- 所有确认、驳回、二次确认、正式写入、报告发布必须写入 `audit_log`。

### 第二阶段扩展表

以下表来自 `项目sql.txt` 的后续扩展规划，第一阶段不要求建表：

- `crm_lead_followup`：客户跟进明细表。
- `student_feedback_log`：投诉/反馈处理日志表。
- `ai_conversation_session`：AI 会话记录表。
- `ai_conversation_message`：AI 会话消息表。
- `knowledge_document`：知识库文档表。
- `knowledge_chunk`：知识库切片表。
- `todo_task`：主动待办表。
- `notification_message`：通知消息表。
- `ai_report`：智能报告历史表。
- `crm_contract`：签约合同表。
- `service_product`：服务产品表。
- `customer_profile_rule`：客户画像规则表。
- `student_emotion_record`：学生情绪明细记录表。
- `student_upgrade_intent`：学生增值转化意向表。

### 状态枚举

AI 草稿状态：

- 待生成
- 生成中
- 待确认
- 已确认
- 已驳回
- 生成失败

业务操作状态：

- 草稿
- 待二次确认
- 已执行
- 执行失败
- 已撤销

报告状态：

- 待生成
- 草稿
- 已发布
- 导出中
- 导出失败

工单状态：

- 待确认
- 待处理
- 处理中
- 已解决
- 已关闭

请假状态：

- 待审批
- 已通过
- 已拒绝
- 已取消

### 迁移约定

- 每次新增或修改表结构必须生成 Alembic 迁移。
- 迁移文件名称需要包含业务模块和变更说明。
- 禁止直接在生产数据库手工改表。
- 开发成员提交涉及模型变更的代码时，必须同时提交迁移文件和数据结构说明。

## 7. API 设计约定

后端 API 统一使用 `/api/v1` 前缀。

### 接口分组

```text
/api/v1/auth/*
/api/v1/customer-judgements/*
/api/v1/service-agent/*
/api/v1/enterprise-assistant/*
/api/v1/student-assistant/*
/api/v1/reports/*
/api/v1/drafts/*
/api/v1/audit-logs/*
/api/v1/ai-tools/*
```

### 前端调用 FastAPI 的 Agent 业务接口

```text
POST /api/v1/service-agent/messages
POST /api/v1/enterprise-assistant/messages
POST /api/v1/student-assistant/messages
POST /api/v1/reports/generate-draft
POST /api/v1/customer-judgements/generate-draft
```

### Dify 调用 FastAPI 的 AI Tools 接口

```text
GET  /api/v1/ai-tools
POST /api/v1/ai-tools/{tool_name}
GET  /api/v1/ai-tools/logs
```

AI Tool 调用响应建议：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "tool_name": "query_activity_list",
    "result": [],
    "draft_id": null,
    "requires_confirmation": false
  },
  "trace_id": "request-trace-id"
}
```

### 草稿确认接口

草稿确认是公共能力，入口嵌入业务页面中。

```text
POST /api/v1/drafts
GET /api/v1/drafts
GET /api/v1/drafts/{draft_id}
POST /api/v1/drafts/{draft_id}/confirm
POST /api/v1/drafts/{draft_id}/reject
POST /api/v1/drafts/{draft_id}/second-confirm
```

### 统一响应格式

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

### 接口命名规则

- 资源名使用复数。
- URL 使用短横线命名。
- 请求体和响应体字段使用 snake_case。
- 前端 TypeScript 类型可使用 camelCase，但 API 层需要处理字段转换或保持一致。
- 所有写接口必须校验角色权限。
- 所有确认、发布、删除和批量修改接口必须写操作日志。

## 8. Dify 工作流协作说明

Dify 负责 AI 编排，不负责正式业务写入。

### Dify 主要能力

- 客户资料解析和画像规则匹配。
- 客服 Agent 多意图识别和 RAG 问答。
- 活动报名信息抽取。
- 企业助手自然语言查询和操作解析。
- 学生助手投诉摘要、情绪识别、生活知识问答。
- 智能报告草稿生成。

### Dify 与后端边界

后端负责：

- 权限校验。
- 业务数据读取和写入。
- 草稿创建、确认、驳回和二次确认。
- 操作日志。
- Dify 调用参数组织。
- AI Tools 白名单工具暴露。

Dify 返回：

- 结构化草稿内容。
- 引用来源。
- 置信度或风险标记。
- 需要补充的信息。

Dify 不直接：

- 修改数据库。
- 发布报告。
- 对外发送客服回复。
- 执行删除或批量修改。
- 改变请假、投诉、客户等正式状态。
- 调用原始 DAO。

### AI Tool 示例

- `query_activity_list`：查询可报名活动列表。
- `create_activity_signup_draft`：创建活动报名草稿。
- `query_student_progress`：查询学生申请进度。
- `create_complaint_summary_draft`：创建投诉摘要草稿。
- `query_customer_judgement_record`：查询客户研判记录摘要。
- `create_business_operation_draft`：创建自然语言业务操作草稿。
- `query_report_source_data`：查询报告生成所需聚合数据摘要。

### 工作流清单

建议维护以下 Dify 工作流导出文件：

- `customer_judgement.yml`
- `service_agent.yml`
- `enterprise_assistant.yml`
- `student_assistant.yml`
- `reports.yml`

当前阶段只在文档中规划这些文件，开发阶段再创建实际目录和工作流文件。

### Prompt 与知识库管理

Prompt 需要按模块管理，并记录版本。每次调整 Prompt，需要说明影响范围和验证结果。

知识库资料包括：

- 公司信息。
- 公司业务。
- 留学政策。
- FAQ。
- 海外生活指南。
- 升学项目资料。

知识库更新后，需要至少验证一个典型问题能正确命中来源。

## 9. 前端页面规划

### 前端角色入口

- 管理员入口：系统管理、知识库、报告、日志和全量业务数据。
- 员工入口：客户、客服、企业助手、学生业务和报告。
- 学生入口：学生助手、请假、投诉、查询和生活支持。
- 访客入口：客服 Agent 咨询和活动报名。

### 管理员页面

- 管理员首页
- 用户与角色管理页
- 知识库资料管理页
- 活动管理页
- 课程项目管理页
- 报告中心
- 操作日志页
- AI 草稿管理页

### 员工页面

- 员工首页
- 客户研判上传页
- 客户研判记录页
- 客服会话记录页
- 活动报名列表页
- 企业助手聊天页
- 意向客户管理页
- 员工日报页
- 请假审批页
- 投诉反馈处理页
- 学生成绩管理页
- 报告查看页

### 学生页面

- 学生首页
- 学生助手聊天页
- 请假申请页
- 请假记录页
- 投诉建议页
- 成绩查询页
- 考务查询页
- 申请进度查询页
- 生活支持问答页
- 增值项目推荐页

### 访客页面

- 访客客服聊天入口
- 活动查询与报名入口

### 前端分层

- `views/`：页面级组件。
- `layouts/`：角色布局。
- `components/`：通用组件、表单、表格、聊天、报告组件。
- `api/`：后端接口封装。
- `stores/`：登录态、草稿状态等全局状态。
- `types/`：接口和页面数据类型。
- `router/`：路由和角色访问控制。

### 页面验收标准

- 页面能按角色访问。
- 页面能展示草稿、确认、驳回和二次确认状态。
- 业务列表支持基础查询和详情查看。
- 表单提交失败时有明确错误提示。
- AI 生成内容必须有确认入口。

## 10. 测试与验收

### 测试类型

单元测试：

- 重点覆盖 `services/`。
- 验证草稿确认、二次确认、状态流转、权限后的业务规则。

集成测试：

- 覆盖 Controller 到 Service 到 DAO 到 MySQL。
- 验证接口请求、响应、数据库写入和异常返回。

Dify 联调测试：

- 验证客户研判、客服回复、自然语言操作、学生助手和报告草稿。
- 检查 Dify 返回内容是否能被后端结构化处理。
- 检查 Dify 调用 AI Tools 时不会绕过业务规则。

前端测试：

- 验证角色入口、页面路由、接口调用、草稿确认入口、日志页、报告页。

端到端验收：

- 验证真实业务链路是否能完整跑通。

### 核心验收场景

- 访客咨询活动并提交报名信息，员工确认后写入活动报名表。
- 员工上传客户资料，系统生成客户研判草稿，员工确认后归档。
- 员工输入自然语言删除指令，系统生成操作草稿并要求二次确认，确认后执行并记录日志。
- 学生提交请假申请，员工端审批，学生端查看审批结果。
- 学生提交投诉，系统生成工单摘要草稿，员工确认后进入投诉工单。
- 管理员生成投诉处理周报草稿，编辑确认后发布正式版本并导出。

### 验收原则

- 没有草稿确认入口的 AI 输出不能验收通过。
- 没有操作日志的写操作不能验收通过。
- 删除、批量修改、关键状态变更没有二次确认不能验收通过。
- Dify 返回失败时，页面和接口都要有明确错误提示。
- 各角色不能访问未授权页面和数据。
- Dify 不能直连数据库或执行任意 SQL。

## 11. 本地启动规划

本节描述未来开发阶段的本地启动方式。当前阶段只写文档，不创建启动脚本和代码目录。

项目采用本地脚本启动，不使用 Docker Compose 或 Kubernetes。

规划脚本：

- `backend/start_backend.ps1`
- `frontend/start_frontend.ps1`
- `scripts/start_all.ps1`
- `scripts/init_mysql.sql`

### 后端启动规划

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

后端 `.env.example` 应包含：

```text
APP_ENV=local
DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/education_service
DIFY_API_BASE_URL=http://127.0.0.1:5001
DIFY_API_KEY=replace_with_local_key
JWT_SECRET_KEY=replace_with_local_secret
```

### 前端启动规划

```powershell
cd frontend
npm install
npm run dev
```

前端 `.env.example` 应包含：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### 本地联调检查

- 后端健康检查接口可访问。
- 前端能访问登录页。
- 前端接口地址指向本地后端。
- 后端能连接 MySQL。
- 后端能调用 Dify 测试接口。
- Dify 能调用 FastAPI AI Tools 测试接口。
- 草稿确认接口能创建和查询测试草稿。

## 12. 交付检查清单

### 文档检查

- [ ] README 能指向 PRD 和团队交付文档。
- [ ] 项目概览说明了目标、角色、模块和边界。
- [ ] 架构图体现统一 Vue 前端、FastAPI、Dify、DAO、DraftService 和 AI Tools 的关系。
- [ ] MVC 分层说明清楚 Controller、Service、DAO、Model、Schema 的职责。
- [ ] 文件夹结构按技术分层，而不是按业务模块目录拆分。
- [ ] 数据库文档包含核心表、公共模型、状态枚举和迁移约定。
- [ ] API 文档包含 `/api/v1` 分组、响应格式、草稿确认接口和 AI Tools 接口。
- [ ] Dify 文档说明了工作流、Prompt、知识库、AI Tools 和后端边界。
- [ ] 前端文档列出管理员、员工、学生、访客四类入口。
- [ ] 测试文档覆盖单元、集成、Dify 联调、前端和端到端验收。
- [ ] 本地启动文档说明脚本、环境变量和联调检查。

### 开发前检查

- [ ] 团队已确认技术栈：FastAPI + Vue + MySQL + SQLAlchemy。
- [ ] 团队已确认前端只调用 FastAPI，不直接调用 Dify。
- [ ] 团队已确认 Dify 只生成草稿或调用白名单工具，不直接写正式业务数据。
- [ ] 团队已确认所有 AI 输出需要人工确认后生效。
- [ ] 团队已确认删除、批量修改、关键状态变更需要二次确认。
- [ ] 团队已确认后端目录按技术分层组织。
- [ ] 团队已确认本地脚本启动方式。

### 模块交付检查

- [ ] 客户研判模块能上传资料、生成草稿、确认归档。
- [ ] 客服 Agent 能生成回复草稿并完成活动报名确认。
- [ ] 企业智能助手能查询业务数据并生成写操作草稿。
- [ ] 学生智能助手能完成请假、投诉、查询和情绪记录。
- [ ] 智能报告能生成五类报告草稿并确认发布。

### 最终验收检查

- [ ] 端到端验收场景全部通过。
- [ ] 写操作均有操作日志。
- [ ] AI 草稿均有确认或驳回记录。
- [ ] 高风险操作均有二次确认记录。
- [ ] Dify AI Tools 调用均有工具日志。
- [ ] 文档、接口、页面和测试结果一致。
