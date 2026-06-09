# 03 文件夹结构规划

本文件只描述未来代码目录规划。当前文档阶段不创建实际代码骨架。

## 后端目录

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
    services/
      auth_service.py
      customer_judgement_service.py
      service_agent_service.py
      enterprise_assistant_service.py
      student_assistant_service.py
      report_service.py
      draft_service.py
      audit_log_service.py
    repositories/
      user_repository.py
      customer_judgement_repository.py
      service_agent_repository.py
      enterprise_assistant_repository.py
      student_assistant_repository.py
      report_repository.py
      draft_repository.py
      audit_log_repository.py
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

## 前端目录

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

## Dify 与脚本目录

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

## 命名规则

- 后端按技术分层建目录，不创建 `app/modules/`。
- 业务模块通过文件名前缀区分。
- Python 文件使用小写蛇形命名。
- 前端 API 和类型文件使用业务名区分。
- 报告模块后端文件统一使用 `report`，前端文件可使用 `reports`。
