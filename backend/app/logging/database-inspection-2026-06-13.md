# ???????

- ?????2026-06-13 11:23:33
- ??????`mysql+pymysql://root:***@localhost:3306/education_service_ai`
- ????23
- ??????338
- ?????????? 5 ?????????

## ???
| ?? | ?? | ??? | ?? | ???? | ?? |
| --- | --- | --- | --- | --- | --- |
| academic_event | 33 | 12 | id | 0 | 学业考务事件表 |
| ai_draft | 15 | 16 | id | - | AI草稿公共表 |
| ai_report | 1 | 16 | id | - | - |
| alembic_version | 1 | 1 | version_num | - | - |
| audit_log | 33 | 16 | id | - | 系统操作审计日志表 |
| course_project | 10 | 12 | id | 0 | 课程与项目表 |
| crm_lead | 12 | 25 | id | 0 | 意向客户线索表 |
| customer_analysis_record | 22 | 17 | id | 0 | 客户研判记录表 |
| employee_daily_report | 10 | 13 | id | 0 | 员工日报表 |
| employee_profile | 10 | 11 | id | 0 | 员工档案表 |
| event_lecture | 10 | 16 | id | 0 | 活动与讲座表 |
| event_registration | 23 | 10 | id | 0 | 活动报名表 |
| faq_qa | 10 | 11 | id | 0 | FAQ标准问答表 |
| report_export_record | 1 | 11 | id | - | - |
| student_application_progress | 20 | 16 | id | 0 | 学生申请进度表 |
| student_feedback_ticket | 28 | 18 | id | 0 | 学生投诉与售后反馈工单表 |
| student_leave_request | 18 | 14 | id | 0 | 学生请假申请表 |
| student_profile | 11 | 16 | id | 0 | 学生档案表 |
| student_psych_alert | 20 | 12 | id | 0 | 学生心理预警表 |
| student_psych_profile | 10 | 10 | id | 0 | 学生心理健康画像表 |
| student_score | 10 | 12 | id | 0 | 学生成绩表 |
| sys_department | 10 | 10 | id | 0 | 部门组织架构表 |
| sys_user | 20 | 11 | id | 0 | 统一用户表 |

## ??????
- ??????????

## ??????
### `academic_event.event_type`
| ? | ?? |
| --- | --- |
| exam | 18 |
| other | 8 |
| paper_deadline | 5 |
| course_deadline | 2 |

### `academic_event.status`
| ? | ?? |
| --- | --- |
| active | 18 |
| completed | 8 |
| cancelled | 7 |

### `ai_draft.biz_object_type`
| ? | ?? |
| --- | --- |
| None | 15 |

### `ai_draft.draft_type`
| ? | ?? |
| --- | --- |
| report | 12 |
| business_operation | 3 |

### `ai_draft.status`
| ? | ?? |
| --- | --- |
| pending_confirm | 6 |
| confirmed | 4 |
| generation_failed | 3 |
| rejected | 2 |

### `ai_report.report_type`
| ? | ?? |
| --- | --- |
| customer_operation | 1 |

### `ai_report.status`
| ? | ?? |
| --- | --- |
| published | 1 |

### `audit_log.action_type`
| ? | ?? |
| --- | --- |
| customer_judge | 13 |
| generate_draft | 12 |
| create | 2 |
| reject | 2 |
| confirm | 1 |
| export | 1 |
| publish | 1 |
| update | 1 |

### `audit_log.biz_object_type`
| ? | ?? |
| --- | --- |
| ai_draft | 14 |
| customer_analysis_record | 13 |
| crm_lead | 3 |
| ai_report | 3 |

### `course_project.project_type`
| ? | ?? |
| --- | --- |
| application | 5 |
| background | 3 |
| language | 2 |

### `course_project.status`
| ? | ?? |
| --- | --- |
| enabled | 10 |

### `course_project.target_education_level`
| ? | ?? |
| --- | --- |
| 本科 | 7 |
| 高中/本科 | 2 |
| 硕士 | 1 |

### `crm_lead.education_level`
| ? | ?? |
| --- | --- |
| 本科 | 10 |
| 高中 | 1 |
| 硕士 | 1 |

### `crm_lead.status`
| ? | ?? |
| --- | --- |
| following | 6 |
| new | 3 |
| signed | 2 |
| lost | 1 |

### `customer_analysis_record.match_level`
| ? | ?? |
| --- | --- |
| high | 11 |
| medium | 7 |
| low | 4 |

### `customer_analysis_record.source_type`
| ? | ?? |
| --- | --- |
| text | 19 |
| manual | 1 |
| pdf | 1 |
| excel | 1 |

### `customer_analysis_record.status`
| ? | ?? |
| --- | --- |
| completed | 22 |

### `employee_daily_report.report_status`
| ? | ?? |
| --- | --- |
| submitted | 10 |

### `employee_profile.role_code`
| ? | ?? |
| --- | --- |
| teacher | 3 |
| manager | 2 |
| sales | 2 |
| service | 2 |
| admin | 1 |

### `employee_profile.status`
| ? | ?? |
| --- | --- |
| active | 10 |

### `event_lecture.event_type`
| ? | ?? |
| --- | --- |
| online | 6 |
| offline | 4 |

### `event_lecture.status`
| ? | ?? |
| --- | --- |
| open | 10 |

### `event_registration.registration_status`
| ? | ?? |
| --- | --- |
| registered | 21 |
| attended | 1 |
| cancelled | 1 |

### `faq_qa.module_scope`
| ? | ?? |
| --- | --- |
| enterprise_assistant | 4 |
| common | 2 |
| customer_service | 2 |
| student_assistant | 2 |

### `faq_qa.status`
| ? | ?? |
| --- | --- |
| enabled | 10 |

### `report_export_record.export_type`
| ? | ?? |
| --- | --- |
| word | 1 |

### `report_export_record.status`
| ? | ?? |
| --- | --- |
| success | 1 |

### `student_application_progress.crm_sync_status`
| ? | ?? |
| --- | --- |
| not_synced | 19 |
| synced | 1 |

### `student_application_progress.progress_status`
| ? | ?? |
| --- | --- |
| processing | 7 |
| completed | 6 |
| pending | 6 |
| blocked | 1 |

### `student_feedback_ticket.priority_level`
| ? | ?? |
| --- | --- |
| normal | 18 |
| urgent | 10 |

### `student_feedback_ticket.status`
| ? | ?? |
| --- | --- |
| pending | 14 |
| closed | 8 |
| processing | 3 |
| resolved | 3 |

### `student_feedback_ticket.ticket_type`
| ? | ?? |
| --- | --- |
| complaint | 20 |
| suggestion | 4 |
| consult | 4 |

### `student_leave_request.leave_type`
| ? | ?? |
| --- | --- |
| sick | 12 |
| personal | 4 |
| other | 2 |

### `student_leave_request.status`
| ? | ?? |
| --- | --- |
| approved | 12 |
| cancelled | 3 |
| rejected | 3 |

### `student_profile.status`
| ? | ?? |
| --- | --- |
| active | 11 |

### `student_psych_alert.risk_level`
| ? | ?? |
| --- | --- |
| high | 11 |
| medium | 9 |

### `student_psych_alert.status`
| ? | ?? |
| --- | --- |
| closed | 9 |
| processing | 8 |
| resolved | 3 |

### `student_psych_profile.risk_level`
| ? | ?? |
| --- | --- |
| low | 5 |
| medium | 3 |
| high | 2 |

### `student_score.exam_type`
| ? | ?? |
| --- | --- |
| daily | 7 |
| midterm | 1 |
| final | 1 |
| other | 1 |

### `sys_department.status`
| ? | ?? |
| --- | --- |
| enabled | 10 |

### `sys_user.status`
| ? | ?? |
| --- | --- |
| enabled | 20 |

### `sys_user.user_type`
| ? | ?? |
| --- | --- |
| employee | 10 |
| student | 10 |

## ????????
### `academic_event`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 学业考务事件ID |
| student_id | BIGINT | ? | - | 学生ID，为空表示公共事件 |
| event_type | VARCHAR(50) | ? | - | 事件类型：paper_deadline论文DDL/exam考试/course_deadline课程截止/other其他 |
| title | VARCHAR(300) | ? | - | 事件标题 |
| event_desc | TEXT | ? | - | 事件说明 |
| course_name | VARCHAR(200) | ? | - | 关联课程 |
| deadline_time | DATETIME | ? | - | 截止或考试时间 |
| reminder_time | DATETIME | ? | - | 提醒时间 |
| status | VARCHAR(30) | ? | 'active' | 状态：active有效/completed已完成/cancelled已取消 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | student_id | event_type | title | event_desc | course_name | deadline_time | reminder_time | status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | paper_deadline | updated title | 需提交个人陈述初稿给文案老师。 | 留学文书 | 2026-06-20 23:59:00 | 2026-06-18 09:00:00 | completed | 2026-06-10 12:03:21 | 2026-06-12 10:07:26 | 0 |
| 2 | 2 | exam | 托福模考 | 托福全真模考，需提前10分钟进入线上考场。 | 托福 | 2026-06-18 19:00:00 | 2026-06-18 12:00:00 | cancelled | 2026-06-10 12:03:21 | 2026-06-11 11:03:26 | 0 |
| 3 | 3 | course_deadline | 澳洲转学材料清单提交 | 提交成绩单、在读证明和课程描述。 | 申请材料 | 2026-06-22 18:00:00 | 2026-06-20 09:00:00 | completed | 2026-06-10 12:03:21 | 2026-06-11 11:04:24 | 0 |
| 4 | 4 | paper_deadline | 加拿大申请简历定稿 | 确认申请简历最终版本。 | 留学文书 | 2026-06-21 20:00:00 | 2026-06-19 10:00:00 | cancelled | 2026-06-10 12:03:21 | 2026-06-11 11:04:24 | 0 |
| 5 | 5 | exam | 雅思口语模拟考试 | 口语一对一模拟考试。 | 雅思 | 2026-06-16 15:00:00 | 2026-06-16 09:00:00 | completed | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `ai_draft`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | AI草稿ID |
| draft_no | VARCHAR(50) | ? | - | 草稿编号 |
| draft_type | VARCHAR(50) | ? | - | 草稿类型 |
| biz_module | VARCHAR(50) | ? | - | 业务模块 |
| biz_object_type | VARCHAR(80) | ? | - | 关联业务对象类型 |
| biz_object_id | BIGINT | ? | - | 关联业务对象ID |
| status | VARCHAR(30) | ? | 'generating' | 草稿状态 |
| content_json | JSON | ? | - | 草稿内容JSON |
| source_trace_id | VARCHAR(100) | ? | - | 来源链路ID |
| created_by | BIGINT | ? | - | 创建人用户ID |
| confirmed_by | BIGINT | ? | - | 确认人用户ID |
| confirmed_time | DATETIME | ? | - | 确认时间 |
| reject_reason | VARCHAR(500) | ? | - | 驳回原因 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | - |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | - |
| is_deleted | TINYINT | ? | '0' | - |

| id | draft_no | draft_type | biz_module | biz_object_type | biz_object_id | status | content_json | source_trace_id | created_by | confirmed_by | confirmed_time | reject_reason | create_time | update_time | is_deleted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 61 | OP-20260611214106-314aa5c3 | business_operation | enterprise_operation |  |  | confirmed | {"phone": "13777730001", "_intent": "create_lead", "budget_range": "31万", "current_grade": "大四", "customer_name": "欧阳全", "source_channel": "抖音", "target_coun... |  | 1 | 1 | 2026-06-11 21:41:48 |  | 2026-06-11 21:41:07 | 2026-06-11 21:41:48 | 0 |
| 62 | OP-20260611214330-ba7bd2a3 | business_operation | enterprise_operation |  |  | confirmed | {"_intent": "update_lead_status", "new_status": "signed", "customer_id": 11, "lost_reason": null, "customer_name": "欧阳全", "current_status": "new", "latest_fo... |  | 1 | 1 | 2026-06-11 21:43:49 |  | 2026-06-11 21:43:31 | 2026-06-11 21:43:49 | 0 |
| 63 | DR-20260612100634-28da9641 | report | report |  |  | generation_failed | {"filters": {"date_end": "2026-06-07", "date_start": "2026-06-01", "department_id": null, "owner_user_id": null}, "report_type": "complaint_weekly", "error_m... | report-8a6bf1c86bc1491bb370f36c4ddfe515 | 1 |  |  |  | 2026-06-12 10:06:35 | 2026-06-12 10:06:35 | 0 |
| 64 | OP-20260612101150-5f28bdcd | business_operation | enterprise_operation |  |  | confirmed | {"phone": "13800138001", "_intent": "create_lead", "budget_range": "25万", "current_grade": "大三", "customer_name": "测试用户", "source_channel": "官网咨询", "target_c... |  | 1 | 1 | 2026-06-12 10:12:10 |  | 2026-06-12 10:11:51 | 2026-06-12 10:12:10 | 0 |
| 65 | DR-20260612102353-0aa489ee | report | report |  |  | generation_failed | {"filters": {"date_end": "2026-06-07", "date_start": "2026-06-01", "department_id": null, "owner_user_id": null}, "report_type": "complaint_weekly", "error_m... | report-e0b31e8b88434dce928fa02f41e79a00 | 1 |  |  |  | 2026-06-12 10:23:54 | 2026-06-12 10:23:54 | 0 |

### `ai_report`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | - |
| report_no | VARCHAR(50) | ? | - | - |
| report_type | VARCHAR(50) | ? | - | - |
| title | VARCHAR(200) | ? | - | - |
| status | VARCHAR(30) | ? | 'confirmed' | - |
| content_json | JSON | ? | - | - |
| source_draft_id | BIGINT | ? | - | - |
| date_start | DATE | ? | - | - |
| date_end | DATE | ? | - | - |
| department_id | BIGINT | ? | - | - |
| created_by | BIGINT | ? | - | - |
| published_by | BIGINT | ? | - | - |
| published_time | DATETIME | ? | - | - |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | - |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | - |
| is_deleted | TINYINT | ? | '0' | - |

| id | report_no | report_type | title | status | content_json | source_draft_id | date_start | date_end | department_id | created_by | published_by | published_time | create_time | update_time | is_deleted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | RP-20260612210047-889ddf46 | customer_operation | 全域客户经营分析报告（2026-06-05 至 2026-06-12） | published | {"risks": [], "title": "全域客户经营分析报告（2026-06-05 至 2026-06-12）", "filters": {"date_end": "2026-06-12", "date_start": "2026-06-05", "department_id": null, "owner... | 75 | 2026-06-05 | 2026-06-12 |  | 1 | 1 | 2026-06-12 21:00:57 | 2026-06-12 21:00:48 | 2026-06-12 21:00:57 | 0 |

### `alembic_version`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| version_num | VARCHAR(32) | ? | - | - |

| version_num |
| --- |
| 20260612_0005 |

### `audit_log`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 审计日志ID |
| operator_user_id | BIGINT | ? | - | 操作人用户ID |
| operator_role | VARCHAR(50) | ? | - | 操作人角色 |
| action_type | VARCHAR(80) | ? | - | 操作类型 |
| biz_module | VARCHAR(50) | ? | - | 业务模块 |
| biz_object_type | VARCHAR(80) | ? | - | 业务对象类型 |
| biz_object_id | BIGINT | ? | - | 业务对象ID |
| before_json | JSON | ? | - | 操作前数据摘要 |
| after_json | JSON | ? | - | 操作后数据摘要 |
| draft_id | BIGINT | ? | - | 关联AI草稿ID |
| trace_id | VARCHAR(100) | ? | - | 链路追踪ID |
| result | VARCHAR(30) | ? | 'success' | 执行结果 |
| error_message | VARCHAR(1000) | ? | - | 失败原因 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | - |
| is_deleted | TINYINT | ? | '0' | - |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | - |

| id | operator_user_id | operator_role | action_type | biz_module | biz_object_type | biz_object_id | before_json | after_json | draft_id | trace_id | result | error_message | create_time | is_deleted | update_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 1 | employee | customer_judge | report | customer_analysis_record | 11 | null | {"status": "completed", "analysis_no": "CA2026011", "match_level": "high", "match_score": 85} |  | cj-ec5637146d86 | success |  | 2026-06-11 20:43:15 | 0 | 2026-06-11 20:43:15 |
| 36 | 1 |  | create | enterprise_operation | crm_lead | 11 |  | {"id": 11, "phone": "13777730001", "_intent": "create_lead", "lead_no": "LEAD-20260611214148-C822F3", "budget_range": "31万", "current_grade": "大四", "customer... | 61 |  | success |  | 2026-06-11 21:41:48 | 0 | 2026-06-11 21:41:48 |
| 37 | 1 |  | update | enterprise_operation | crm_lead | 11 |  | {"_intent": "update_lead_status", "new_status": "signed", "old_status": "new", "customer_id": 11, "lost_reason": null, "customer_name": "欧阳全", "current_statu... | 62 |  | success |  | 2026-06-11 21:43:49 | 0 | 2026-06-11 21:43:49 |
| 38 | 1 | employee | customer_judge | report | customer_analysis_record | 12 | null | {"status": "completed", "analysis_no": "CA2026012", "match_level": "high", "match_score": 85} |  | cj-9ca99db71f16 | success |  | 2026-06-11 22:01:45 | 0 | 2026-06-11 22:01:45 |
| 39 | 1 | employee | customer_judge | report | customer_analysis_record | 13 | null | {"status": "completed", "analysis_no": "CA2026013", "match_level": "high", "match_score": 85} |  | cj-12b62d8dc1b4 | success |  | 2026-06-11 22:01:53 | 0 | 2026-06-11 22:01:53 |

### `course_project`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 课程项目ID |
| project_name | VARCHAR(200) | ? | - | 课程或项目名称 |
| project_type | VARCHAR(50) | ? | - | 项目类型：language语言培训/background背景提升/application留学申请/upgrade学历提升 |
| target_country | VARCHAR(100) | ? | - | 适用国家 |
| target_education_level | VARCHAR(100) | ? | - | 适用学历阶段 |
| target_audience | VARCHAR(500) | ? | - | 适合人群 |
| project_desc | TEXT | ? | - | 项目详情 |
| price_range | VARCHAR(100) | ? | - | 价格区间 |
| status | VARCHAR(20) | ? | 'enabled' | 状态：enabled上架/disabled下架 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | project_name | project_type | target_country | target_education_level | target_audience | project_desc | price_range | status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 英国硕士申请全程服务 | application | 英国 | 本科 | 计划申请英国硕士的本科生 | 覆盖选校定位、文书规划、网申递交和签证指导。 | 30000-50000 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | 美国商科硕士申请服务 | application | 美国 | 本科 | 计划申请美国商科硕士的学生 | 针对金融、市场、管理等商科方向提供申请规划。 | 50000-80000 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 澳洲本科转学规划 | application | 澳大利亚 | 本科 | 希望转学澳洲本科的学生 | 评估转学分、院校匹配和申请材料。 | 25000-45000 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 加拿大硕士申请与移民规划 | application | 加拿大 | 本科 | 关注加拿大硕士和就业移民路径的学生 | 结合院校申请和就业移民政策提供规划。 | 40000-60000 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 新加坡公立大学硕士冲刺 | application | 新加坡 | 本科 | 绩点较高、希望冲刺新加坡公立大学的学生 | 侧重新加坡院校定位、材料打磨和面试准备。 | 35000-55000 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `crm_lead`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 意向客户ID |
| lead_no | VARCHAR(50) | ? | - | 线索编号 |
| customer_name | VARCHAR(100) | ? | - | 客户姓名 |
| phone | VARCHAR(30) | ? | - | 手机号 |
| wechat_no | VARCHAR(100) | ? | - | 微信号 |
| email | VARCHAR(120) | ? | - | 邮箱 |
| source_channel | VARCHAR(100) | ? | - | 来源渠道 |
| education_level | VARCHAR(100) | ? | - | 学历阶段 |
| school_name | VARCHAR(200) | ? | - | 学校名称 |
| major | VARCHAR(200) | ? | - | 专业 |
| current_grade | VARCHAR(100) | ? | - | 当前年级 |
| target_country | VARCHAR(100) | ? | - | 意向国家 |
| target_program | VARCHAR(200) | ? | - | 意向项目 |
| budget_range | VARCHAR(100) | ? | - | 预算区间 |
| background_info | TEXT | ? | - | 客户背景补充信息 |
| follow_up_history | TEXT | ? | - | 前期简化保存历史跟进内容，后续可拆成crm_lead_followup表 |
| latest_follow_up_summary | VARCHAR(1000) | ? | - | 最近跟进摘要 |
| status | VARCHAR(30) | ? | 'new' | 线索状态：new新增/following跟进中/signed已签约/lost已流失/invalid无效 |
| owner_employee_id | BIGINT | ? | - | 负责员工ID |
| last_follow_up_time | DATETIME | ? | - | 最近跟进时间 |
| lost_reason | VARCHAR(500) | ? | - | 流失原因 |
| signed_time | DATETIME | ? | - | 签约时间 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | lead_no | customer_name | phone | wechat_no | email | source_channel | education_level | school_name | major | current_grade | target_country | target_program | budget_range | background_info | follow_up_history | latest_follow_up_summary | status | owner_employee_id | last_follow_up_time | lost_reason | signed_time | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | L2026001 | 王一鸣 | 13***01 | wx_wangym | w***@example.com | 官网咨询 | 本科 | 北京语言大学 | 英语 | 大三 | 英国 | 硕士申请 | 30-40万 | 学生英语基础较好，家长关注签证成功率。 | 2026-06-01 初次电话沟通；2026-06-05 发送英国硕士方案。 | 已约6月12日线上方案沟通 | following | 2 | 2026-06-05 15:30:00 |  |  | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | L2026002 | 李思琪 | 13***02 | wx_lisq | l***@example.com | 讲座报名 | 本科 | 上海大学 | 金融 | 大四 | 美国 | 硕士申请 | 50-60万 | 目标商科方向，希望申请排名靠前院校。 | 2026-06-02 参加讲座；2026-06-04 添加微信。 | 待补充托福成绩和GPA | new | 2 | 2026-06-04 11:00:00 |  |  | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | L2026003 | 张浩然 | 13***03 | wx_zhanghr | z***@example.com | 小红书私信 | 本科 | 南京理工大学 | 计算机 | 大三 | 加拿大 | 硕士申请 | 40-50万 | 计算机专业，关注移民政策。 | 2026-05-29 初次沟通；2026-06-06 发送加拿大项目介绍。 | 家长希望了解就业和移民政策 | following | 5 | 2026-06-06 10:20:00 |  |  | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | L2026004 | 赵可欣 | 13***04 | wx_zhaokx | z***@example.com | 老客户推荐 | 高中 | 杭州外国语学校 | 国际课程 | 高二 | 澳大利亚 | 本科申请 | 35-45万 | 学生正在准备雅思，家长重视院校安全性。 | 2026-06-03 推荐客户建档；2026-06-07 完成第一次面谈。 | 已完成面谈，等待家长确认服务合同 | following | 5 | 2026-06-07 16:00:00 |  |  | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | L2026005 | 陈子涵 | 13***05 | wx_chenzh | c***@example.com | 线下展会 | 本科 | 武汉理工大学 | 材料工程 | 大四 | 新加坡 | 硕士申请 | 25-35万 | 希望申请新加坡公立大学，绩点较高。 | 2026-06-01 展会留资；2026-06-08 发送申请时间规划。 | 客户对服务内容认可，准备签约 | signed | 2 | 2026-06-08 09:30:00 |  | 2026-06-08 18:00:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `customer_analysis_record`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 客户研判记录ID |
| analysis_no | VARCHAR(50) | ? | - | 研判编号 |
| source_type | VARCHAR(30) | ? | - | 来源类型：text文本/pdf简历/excel表格/manual手工录入 |
| source_file_name | VARCHAR(300) | ? | - | 来源文件名 |
| raw_content | LONGTEXT | ? | - | 待研判原始内容 |
| target_product | VARCHAR(100) | ? | - | 研判目标产品或服务 |
| lead_id | BIGINT | ? | - | 关联意向客户ID |
| is_target_customer | TINYINT | ? | - | 是否符合目标客户画像：1是/0否，未研判为空 |
| match_score | DECIMAL(5, 2) | ? | - | 匹配分数0-100 |
| match_level | VARCHAR(30) | ? | - | 匹配等级：high高/medium中/low低 |
| reason_summary | TEXT | ? | - | 研判理由摘要 |
| suggestion | TEXT | ? | - | 后续跟进建议 |
| status | VARCHAR(30) | ? | 'pending' | 状态：pending待研判/completed已完成/failed失败 |
| submitter_user_id | BIGINT | ? | - | 提交人用户ID |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | analysis_no | source_type | source_file_name | raw_content | target_product | lead_id | is_target_customer | match_score | match_level | reason_summary | suggestion | status | submitter_user_id | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | CA2026001 | text |  | 王一鸣，本科大三，英语专业，计划申请英国硕士，预算30-40万。 | 英国硕士申请全程服务 | 1 | 1 | 86.5 | high | 学历、目标国家和预算均匹配英国硕士服务。 | 建议尽快安排方案沟通并展示成功案例。 | completed | 2 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | CA2026002 | text |  | 李思琪，金融专业本科大四，目标美国商科硕士，预算50-60万。 | 美国商科硕士申请服务 | 2 | 1 | 90.0 | high | 目标明确，预算充足，适合美国商科申请服务。 | 补充托福和GPA后给出选校方案。 | completed | 2 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | CA2026003 | text |  | 张浩然，计算机专业本科大三，关注加拿大硕士和移民政策。 | 加拿大硕士申请与移民规划 | 3 | 1 | 82.0 | high | 专业和目标国家匹配，关注移民政策。 | 邀请签证顾问参与后续沟通。 | completed | 5 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | CA2026004 | manual |  | 赵可欣，高二国际课程，家长关注澳洲本科和院校安全。 | 澳洲本科转学规划 | 4 | 1 | 76.0 | medium | 目标国家匹配，但当前阶段更适合本科申请规划。 | 先完成学术背景和语言水平评估。 | completed | 5 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | CA2026005 | text |  | 陈子涵，本科大四，目标新加坡公立大学硕士，绩点较高。 | 新加坡公立大学硕士冲刺 | 5 | 1 | 88.0 | high | 绩点和目标院校匹配度较高。 | 推进签约并启动材料准备。 | completed | 2 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `employee_daily_report`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 员工日报ID |
| employee_id | BIGINT | ? | - | 员工ID |
| department_id | BIGINT | ? | - | 所属部门ID |
| report_date | DATE | ? | - | 日报日期 |
| raw_content | TEXT | ? | - | 原始口述或输入内容 |
| summary | TEXT | ? | - | AI摘要 |
| key_progress | TEXT | ? | - | 关键进展 |
| risks | TEXT | ? | - | 风险与问题 |
| tomorrow_plan | TEXT | ? | - | 明日计划 |
| report_status | VARCHAR(20) | ? | 'submitted' | 状态：draft草稿/submitted已提交/archived已归档 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | employee_id | department_id | report_date | raw_content | summary | key_progress | risks | tomorrow_plan | report_status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 2026-06-09 | 今天召开项目周会，确认企业智能助手优先上线客户录入、日报和查询功能。 | 确认企业智能助手第一阶段范围。 | 完成***源。 | 学生端联动接口需要尽快确定。 | 明天跟进接口负责人和演示数据准备。 | submitted | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | 2 | 2 | 2026-06-09 | 今天跟进王一鸣、李思琪、陈子涵三个客户，陈子涵已签约，王一鸣约了方案沟通。 | 跟进3名客户，其中1名已签约。 | 陈子***间。 | 李思琪托福成绩未补充，转化节奏偏慢。 | 明天重点跟进王一鸣和李思琪。 | submitted | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 3 | 3 | 2026-06-09 | 处理张明请假申请，录入周琪雅思阅读成绩，并查看两名学生学习进度。 | 完成请假和成绩相关教务工作。 | 张明***入。 | 部分学生成绩录入不完整。 | 明天核对本周模考成绩。 | submitted | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 4 | 4 | 2026-06-09 | 回复官网咨询12条，登记吴昊线索，协助客户完成讲座报名。 | 完成客服咨询接待和活动报名支持。 | 新增***复。 | 部分客户对费用政策反复询问。 | 明天整理费用FAQ。 | submitted | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 5 | 5 | 2026-06-09 | 跟进张浩然、赵可欣、郑文博三个市场渠道客户，赵可欣等待合同确认。 | 市场渠道客户持续推进。 | 赵可***单。 | 张浩然家长关注移民政策，需签证部支持。 | 明天邀请签证顾问一起沟通。 | submitted | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `employee_profile`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 员工ID |
| user_id | BIGINT | ? | - | 关联用户ID |
| employee_no | VARCHAR(50) | ? | - | 员工编号 |
| employee_name | VARCHAR(100) | ? | - | 员工姓名 |
| department_id | BIGINT | ? | - | 所属部门ID |
| role_code | VARCHAR(50) | ? | - | 角色编码：sales顾问/teacher老师/service客服/manager主管/admin管理员 |
| job_title | VARCHAR(100) | ? | - | 岗位名称 |
| status | VARCHAR(20) | ? | 'active' | 员工状态：active在职/resigned离职/disabled停用 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | user_id | employee_no | employee_name | department_id | role_code | job_title | status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | E1001 | 高远 | 1 | manager | 总经理 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | 2 | E1002 | 李娜 | 2 | sales | 销售顾问 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 3 | E1003 | 王强 | 3 | teacher | 教务主管 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 4 | E1004 | 赵敏 | 4 | service | 客服专员 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 5 | E1005 | 陈磊 | 5 | sales | 市场顾问 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `event_lecture`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 活动讲座ID |
| event_no | VARCHAR(50) | ? | - | 活动编号 |
| event_name | VARCHAR(200) | ? | - | 活动名称 |
| event_type | VARCHAR(30) | ? | - | 活动类型：online线上/offline线下 |
| topic | VARCHAR(300) | ? | - | 活动主题 |
| speaker | VARCHAR(200) | ? | - | 主讲人 |
| start_time | DATETIME | ? | - | 开始时间 |
| end_time | DATETIME | ? | - | 结束时间 |
| location | VARCHAR(300) | ? | - | 线下地点 |
| online_url | VARCHAR(500) | ? | - | 线上链接 |
| max_participants | INTEGER | ? | - | 最大报名人数 |
| current_participants | INTEGER | ? | '0' | 当前报名人数 |
| status | VARCHAR(30) | ? | 'open' | 活动状态：open报名中/full已满/closed已结束/cancelled已取消 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | event_no | event_name | event_type | topic | speaker | start_time | end_time | location | online_url | max_participants | current_participants | status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | EV2026001 | 英国硕士申请趋势分享会 | online | 英国硕士申请时间线与选校策略 | 李娜 | 2026-06-15 19:00:00 | 2026-06-15 20:30:00 |  | https://meeting.example.com/uk-master | 200 | 12 | open | 2026-06-10 12:03:21 | 2026-06-12 13:01:56 | 0 |
| 2 | EV2026002 | 美国商科申请讲座 | online | 美国商科申请材料与职业规划 | 高远 | 2026-06-16 19:00:00 | 2026-06-16 20:30:00 |  | https://meeting.example.com/us-business | 150 | 2 | open | 2026-06-10 12:03:21 | 2026-06-12 10:13:34 | 0 |
| 3 | EV2026003 | 澳洲本科转学线下咨询日 | offline | 澳洲转学分与院校选择 | 陈磊 | 2026-06-17 14:00:00 | 2026-06-17 17:00:00 | 上海校区A教室 |  | 50 | 2 | open | 2026-06-10 12:03:21 | 2026-06-12 10:13:46 | 0 |
| 4 | EV2026004 | 加拿大留学与移民政策说明会 | online | 加拿大硕士申请和就业政策 | 周航 | 2026-06-18 19:30:00 | 2026-06-18 21:00:00 |  | https://meeting.example.com/canada-policy | 180 | 1 | open | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | EV2026005 | 新加坡名校申请策略课 | offline | 新加坡公立大学申请要点 | 王强 | 2026-06-19 15:00:00 | 2026-06-19 17:00:00 | 北京校区3号会议室 |  | 60 | 1 | open | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `event_registration`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 活动报名ID |
| event_id | BIGINT | ? | - | 活动ID |
| lead_id | BIGINT | ? | - | 关联意向客户ID，可为空 |
| visitor_name | VARCHAR(100) | ? | - | 报名人姓名 |
| visitor_phone | VARCHAR(30) | ? | - | 报名人手机号 |
| registration_status | VARCHAR(30) | ? | 'registered' | 报名状态：registered已报名/cancelled已取消/attended已参加/no_show未到场 |
| remark | VARCHAR(500) | ? | - | 备注 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 报名时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | event_id | lead_id | visitor_name | visitor_phone | registration_status | remark | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 王一鸣 | 13***01 | registered | 关注英国硕士申请时间线。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | 2 | 2 | 李思琪 | 13***02 | registered | 计划申请美国商科。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 3 | 4 | 赵可欣 | 13***04 | registered | 咨询澳洲本科申请。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 4 | 3 | 张浩然 | 13***03 | registered | 关注加拿大移民政策。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 5 | 5 | 陈子涵 | 13***05 | attended | 已参加新加坡申请讲座。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `faq_qa`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | FAQ ID |
| module_scope | VARCHAR(50) | ? | - | 适用模块：customer_service/enterprise_assistant/student_assistant/common |
| category | VARCHAR(100) | ? | - | 问题分类 |
| question | VARCHAR(800) | ? | - | 标准问题 |
| answer | TEXT | ? | - | 标准答案 |
| keywords | VARCHAR(500) | ? | - | 关键词 |
| status | VARCHAR(20) | ? | 'enabled' | 状态：enabled启用/disabled停用 |
| sort_order | INTEGER | ? | '0' | 排序号 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | module_scope | category | question | answer | keywords | status | sort_order | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | enterprise_assistant | 客户管理 | 新员工如何录入意向客户？ | 进入企业智能助手后，输入或口述客户姓名、联系方式、意向国家、目标项目等信息，系统会生成确认卡片，确认后写入CRM。 | 客户***客户 | enabled | 1 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | enterprise_assistant | 日报 | 员工日报怎么提交？ | 员工可以直接口述当天工作内容，AI会自动整理为摘要、关键进展、风险问题和明日计划，确认后提交。 | 日报***日报 | enabled | 2 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | enterprise_assistant | 审批 | 请假申请怎么审批？ | 老师可以询问“我有哪些待审批请假”，查看学生请假详情后点击通过或驳回，审批结果会更新到请假申请表。 | 请假***助手 | enabled | 3 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | enterprise_assistant | 投诉处理 | 投诉反馈如何处理？ | 员工可以查询自己负责的待处理投诉，补充处理方案并更新状态为处理中、已解决或已关闭。 | 投诉***工单 | enabled | 4 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | customer_service | 公司信息 | 你们主要提供哪些服务？ | 我们主要提供留学申请、语言培训、背景提升、签证指导和海外生活支持等服务。 | 服务***申请 | enabled | 5 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `report_export_record`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | - |
| report_id | BIGINT | ? | - | - |
| export_type | VARCHAR(20) | ? | - | - |
| file_name | VARCHAR(255) | ? | - | - |
| file_path | VARCHAR(500) | ? | - | - |
| status | VARCHAR(30) | ? | - | - |
| error_message | VARCHAR(1000) | ? | - | - |
| created_by | BIGINT | ? | - | - |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | - |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | - |
| is_deleted | TINYINT | ? | '0' | - |

| id | report_id | export_type | file_name | file_path | status | error_message | created_by | create_time | update_time | is_deleted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | word | RP-20260612210047-889ddf46.docx | storage\reports\RP-20260612210047-889ddf46.docx | success |  | 1 | 2026-06-12 21:01:08 | 2026-06-12 21:01:08 | 0 |

### `student_application_progress`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 申请进度ID |
| student_id | BIGINT | ? | - | 学生ID |
| progress_stage | VARCHAR(80) | ? | - | 进度阶段：essay文书/school_apply院校申请/visa签证/offer录取/other其他 |
| target_country | VARCHAR(100) | ? | - | 目标国家 |
| school_name | VARCHAR(200) | ? | - | 申请院校 |
| program_name | VARCHAR(200) | ? | - | 申请项目 |
| progress_status | VARCHAR(50) | ? | 'processing' | 进度状态：pending待开始/processing处理中/completed已完成/blocked受阻 |
| progress_desc | TEXT | ? | - | 进度说明 |
| handler_employee_id | BIGINT | ? | - | 负责人员工ID |
| expected_finish_time | DATETIME | ? | - | 预计完成时间 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |
| crm_record_id | VARCHAR(100) | ? | - | CRM系统记录ID |
| crm_sync_status | VARCHAR(30) | ? | 'not_synced' | CRM同步状态：not_synced/syncing/synced/failed |
| crm_last_sync_time | DATETIME | ? | - | 最近CRM同步时间 |

| id | student_id | progress_stage | target_country | school_name | program_name | progress_status | progress_desc | handler_employee_id | expected_finish_time | create_time | update_time | is_delete | crm_record_id | crm_sync_status | crm_last_sync_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | essay | 英国 | 曼彻斯特大学 | 教育学硕士 | completed | regression test done | 6 | 2026-06-20 18:00:00 | 2026-06-10 12:03:21 | 2026-06-12 10:08:46 | 0 |  | not_synced |  |
| 2 | 2 | school_apply | 美国 | 纽约大学 | 金融硕士 | pending | 等待托福成绩和GPA确认后启动网申。 | 2 | 2026-07-01 18:00:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |  | not_synced |  |
| 3 | 3 | school_apply | 澳大利亚 | 悉尼大学 | 本科转学 | processing | 正在评估转学分和课程描述。 | 5 | 2026-06-28 18:00:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |  | not_synced |  |
| 4 | 4 | visa | 加拿大 | 多伦多大学 | 计算机硕士 | pending | 等待资金证明和学习计划材料。 | 7 | 2026-07-05 18:00:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |  | not_synced |  |
| 5 | 5 | offer | 新加坡 | 新加坡国立大学 | 材料科学硕士 | completed | 已收到录取，准备签证材料。 | 7 | 2026-06-30 18:00:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |  | not_synced |  |

### `student_feedback_ticket`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 反馈工单ID |
| ticket_no | VARCHAR(50) | ? | - | 工单编号 |
| student_id | BIGINT | ? | - | 学生ID |
| ticket_type | VARCHAR(30) | ? | 'complaint' | 工单类型：complaint投诉/suggestion建议/consult咨询 |
| category | VARCHAR(100) | ? | - | 反馈分类：教学/服务/顾问/财务/签证/院校申请/生活服务/其他 |
| title | VARCHAR(300) | ? | - | 反馈标题 |
| content_summary | TEXT | ? | - | AI摘要 |
| detail | TEXT | ? | - | 详细反馈内容 |
| priority_level | VARCHAR(30) | ? | 'normal' | 优先级：normal普通/urgent紧急/severe严重 |
| status | VARCHAR(30) | ? | 'pending' | 状态：pending待处理/processing处理中/resolved已解决/closed已关闭 |
| handler_employee_id | BIGINT | ? | - | 当前处理人员工ID |
| solution | TEXT | ? | - | 处理方案或最终结果 |
| satisfaction_score | TINYINT | ? | - | 满意度评分1-5 |
| is_notified | TINYINT | ? | '0' | 是否已通知学生：1是/0否 |
| close_time | DATETIME | ? | - | 关闭时间 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | ticket_no | student_id | ticket_type | category | title | content_summary | detail | priority_level | status | handler_employee_id | solution | satisfaction_score | is_notified | close_time | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FB2026001 | 1 | complaint | 教学 | updated title | 学生反馈上周作文批改反馈较慢。 | 张明反馈上周提交作文后等待三天才收到批改建议，希望提高反馈速度。 | urgent | closed | 3 | 已与任课老师沟通，后续作文批改时限控制在48小时内。 | 4 | 1 | 2026-06-11 11:03:27 | 2026-06-10 12:03:21 | 2026-06-12 10:09:24 | 0 |
| 2 | FB2026002 | 2 | suggestion | 服务 | 希望增加申请节点提醒 | 学生希望系统主动提醒申请材料截止时间。 | 李雨建议在申请系统中增加文书、网申、推荐信等节点提醒。 | normal | closed | 6 | Issue resolved properly | 4 | 1 | 2026-06-11 11:04:25 | 2026-06-10 12:03:21 | 2026-06-11 11:04:24 | 0 |
| 3 | FB2026003 | 3 | complaint | 顾问 | 方案说明不够清晰 | 学生认为顾问对澳洲本科转学路径解释不够细。 | 王璐反馈首次咨询时对转学分和院校选择规则不够理解，希望重新讲解。 | urgent | closed | 1 | Issue resolved properly | 4 | 1 | 2026-06-11 11:18:29 | 2026-06-10 12:03:21 | 2026-06-11 11:18:29 | 0 |
| 4 | FB2026004 | 4 | consult | 签证 | 加拿大签证材料疑问 | 学生咨询资金证明和学习计划材料要求。 | 赵晨希望确认加拿大签证所需资金证明时间和学习计划模板。 | normal | closed | 7 | 已发送材料清单和学习计划模板。 | 4 | 1 | 2026-06-11 11:29:52 | 2026-06-10 12:03:21 | 2026-06-11 11:29:51 | 0 |
| 5 | FB2026005 | 5 | complaint | 财务 | 费用发票开具延迟 | 学生反馈发票开具等待时间较长。 | 陈安反馈缴费后尚未收到发票，希望确认开具时间。 | normal | closed | 8 | Issue resolved properly | 4 | 1 | 2026-06-11 11:36:35 | 2026-06-10 12:03:21 | 2026-06-11 11:36:35 | 0 |

### `student_leave_request`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 请假申请ID |
| request_no | VARCHAR(50) | ? | - | 请假单号 |
| student_id | BIGINT | ? | - | 学生ID |
| leave_type | VARCHAR(50) | ? | - | 请假类型：sick病假/personal事假/other其他 |
| reason | TEXT | ? | - | 请假原因 |
| start_time | DATETIME | ? | - | 开始时间 |
| end_time | DATETIME | ? | - | 结束时间 |
| status | VARCHAR(30) | ? | 'pending' | 审批状态：pending待审批/approved已通过/rejected已驳回/cancelled已撤销 |
| approver_employee_id | BIGINT | ? | - | 审批员工ID |
| approval_comment | VARCHAR(1000) | ? | - | 审批意见 |
| approve_time | DATETIME | ? | - | 审批时间 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | request_no | student_id | leave_type | reason | start_time | end_time | status | approver_employee_id | approval_comment | approve_time | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | LR2026001 | 1 | sick | 感冒发烧，需要休息一天。 | 2026-06-10 09:00:00 | 2026-06-10 18:00:00 | approved | 3 | 同意，请注意休息并补交作业。 | 2026-06-09 10:30:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | LR2026002 | 2 | personal | 参加家庭重要事务。 | 2026-06-11 14:00:00 | 2026-06-11 18:00:00 | approved | 1 |  | 2026-06-11 11:03:26 | 2026-06-10 12:03:21 | 2026-06-11 11:03:26 | 0 |
| 3 | LR2026003 | 3 | sick | 身体不适，需要线上休息。 | 2026-06-12 09:00:00 | 2026-06-12 12:00:00 | rejected | 3 | 当天有重要测评，建议课后补充说明。 | 2026-06-09 11:15:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | LR2026004 | 4 | personal | 办理证件材料。 | 2026-06-13 10:00:00 | 2026-06-13 17:00:00 | approved | 6 | 同意，请及时上传材料回执。 | 2026-06-09 13:20:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | LR2026005 | 5 | other | 参加学校活动。 | 2026-06-14 09:00:00 | 2026-06-14 11:30:00 | rejected | 1 | Insufficient reason | 2026-06-11 11:03:26 | 2026-06-10 12:03:21 | 2026-06-11 11:03:26 | 0 |

### `student_profile`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 学生ID |
| user_id | BIGINT | ? | - | 关联用户ID，未开通账号时可为空 |
| student_no | VARCHAR(50) | ? | - | 学生编号 |
| student_name | VARCHAR(100) | ? | - | 学生姓名 |
| phone | VARCHAR(30) | ? | - | 手机号 |
| email | VARCHAR(120) | ? | - | 邮箱 |
| current_school | VARCHAR(200) | ? | - | 当前学校 |
| current_grade | VARCHAR(100) | ? | - | 当前年级/阶段 |
| target_country | VARCHAR(100) | ? | - | 目标留学国家 |
| target_program | VARCHAR(200) | ? | - | 目标申请项目 |
| counselor_employee_id | BIGINT | ? | - | 负责顾问员工ID |
| teacher_employee_id | BIGINT | ? | - | 负责老师员工ID |
| status | VARCHAR(30) | ? | 'active' | 学生状态：active服务中/graduated已结课/inactive停用 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | user_id | student_no | student_name | phone | email | current_school | current_grade | target_country | target_program | counselor_employee_id | teacher_employee_id | status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 11 | S2026001 | 张明 | 13***01 | z***@student.example.com | 北京外国语大学 | 本科大三 | 英国 | 硕士申请 | 2 | 3 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | 12 | S2026002 | 李雨 | 13***02 | l***@student.example.com | 上海财经大学 | 本科大四 | 美国 | 硕士申请 | 2 | 6 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 13 | S2026003 | 王璐 | 13***03 | w***@student.example.com | 南京大学 | 本科大二 | 澳大利亚 | 本科转学 | 5 | 3 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 14 | S2026004 | 赵晨 | 13***04 | z***@student.example.com | 浙江大学 | 本科大三 | 加拿大 | 硕士申请 | 5 | 6 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 15 | S2026005 | 陈安 | 13***05 | c***@student.example.com | 华中科技大学 | 本科大四 | 新加坡 | 硕士申请 | 2 | 7 | active | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `student_psych_alert`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 心理预警ID |
| alert_no | VARCHAR(50) | ? | - | 预警编号 |
| student_id | BIGINT | ? | - | 学生ID |
| trigger_reason | TEXT | ? | - | 触发原因 |
| risk_level | VARCHAR(30) | ? | - | 风险等级：medium中/high高/critical危急 |
| status | VARCHAR(30) | ? | 'pending' | 处理状态：pending未处理/processing跟进中/resolved已解除/closed已关闭 |
| teacher_employee_id | BIGINT | ? | - | 负责跟进老师ID |
| handle_result | TEXT | ? | - | 处理结果 |
| close_time | DATETIME | ? | - | 关闭时间 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | alert_no | student_id | trigger_reason | risk_level | status | teacher_employee_id | handle_result | close_time | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PA2026001 | 1 | 多次提到担心申请进度落后和作业反馈不及时。 | medium | closed | 10 | 已完成关怀沟通，建议保持每周一次进度同步。 | 2026-06-11 11:03:26 | 2026-06-10 12:03:21 | 2026-06-11 11:03:26 | 0 |
| 2 | PA2026002 | 2 | 申请节点不明确引发轻微不安。 | medium | closed | 10 | 已发送申请节点表，学生反馈状态稳定。 | 2026-06-08 20:30:00 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | PA2026003 | 3 | 表示对澳洲转学路径不确定，出现明显焦虑表达。 | high | closed | 10 | Counseling completed, student improved | 2026-06-11 11:04:25 | 2026-06-10 12:03:21 | 2026-06-11 11:04:24 | 0 |
| 4 | PA2026004 | 4 | 签证材料压力上升，但未出现高危表达。 | medium | closed | 10 | 签证顾问已补充材料清单。 | 2026-06-11 11:18:29 | 2026-06-10 12:03:21 | 2026-06-11 11:18:29 | 0 |
| 5 | PA2026005 | 5 | 因费用和发票问题产生烦躁情绪。 | medium | closed | 10 | Counseling completed, student improved | 2026-06-11 11:29:52 | 2026-06-10 12:03:21 | 2026-06-11 11:29:51 | 0 |

### `student_psych_profile`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 心理健康画像ID |
| student_id | BIGINT | ? | - | 学生ID |
| latest_emotion_tag | VARCHAR(100) | ? | - | 最新情绪标签 |
| emotion_score | TINYINT | ? | - | 情绪分值0-100，越高越积极 |
| risk_level | VARCHAR(30) | ? | 'low' | 风险等级：low低/medium中/high高/critical危急 |
| last_interaction_time | DATETIME | ? | - | 最近心理相关交互时间 |
| emotion_summary | TEXT | ? | - | 长期情绪摘要 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | student_id | latest_emotion_tag | emotion_score | risk_level | last_interaction_time | emotion_summary | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 困惑 | 50 | low | 2026-06-13 10:35:44 | 情绪对话：???????? | 2026-06-10 12:03:21 | 2026-06-13 10:35:43 | 0 |
| 2 | 2 | 平稳 | 78 | low | 2026-06-08 19:30:00 | 整体状态平稳，主要关注申请节点提醒。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 3 | 焦虑 | 48 | high | 2026-06-09 09:20:00 | 对转学路径和未来适应存在明显焦虑。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 4 | 积极 | 82 | low | 2026-06-07 18:00:00 | 材料准备积极，情绪稳定。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 5 | 轻微烦躁 | 66 | medium | 2026-06-08 21:00:00 | 因发票和签证材料准备稍有烦躁。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `student_score`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 学生成绩ID |
| student_id | BIGINT | ? | - | 学生ID |
| course_name | VARCHAR(200) | ? | - | 课程名称 |
| score | DECIMAL(5, 2) | ? | - | 成绩分数 |
| exam_type | VARCHAR(50) | ? | - | 考试类型：daily平时/midterm期中/final期末/makeup补考/other其他 |
| semester | VARCHAR(100) | ? | - | 学期 |
| exam_date | DATE | ? | - | 考试日期 |
| operator_employee_id | BIGINT | ? | - | 录入员工ID |
| remark | VARCHAR(500) | ? | - | 备注 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | student_id | course_name | score | exam_type | semester | exam_date | operator_employee_id | remark | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 雅思听力 | 7.0 | daily | 2026春季 | 2026-06-01 | 3 | 模考听力表现稳定。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | 2 | 托福阅读 | 26.0 | daily | 2026春季 | 2026-06-02 | 6 | 阅读速度较快，细节题需加强。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 3 | 雅思写作 | 6.0 | midterm | 2026春季 | 2026-06-03 | 3 | 论证结构需要优化。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 4 | GRE数学 | 98.0 | daily | 2026春季 | 2026-06-04 | 6 | GRE数学按百分制折算为98分。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 5 | 雅思口语 | 6.5 | daily | 2026春季 | 2026-06-05 | 7 | 表达流畅度提升明显。 | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `sys_department`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 部门ID |
| department_name | VARCHAR(100) | ? | - | 部门名称 |
| parent_id | BIGINT | ? | - | 上级部门ID，顶级部门为空 |
| leader_employee_id | BIGINT | ? | - | 部门负责人ID，前期只存ID不强制外键，避免循环依赖 |
| department_desc | VARCHAR(500) | ? | - | 部门职责说明 |
| sort_order | INTEGER | ? | '0' | 排序号 |
| status | VARCHAR(20) | ? | 'enabled' | 状态：enabled启用/disabled停用 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | department_name | parent_id | leader_employee_id | department_desc | sort_order | status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 总裁办 |  | 1 | 负责公司整体战略、经营管理和跨部门协调。 | 1 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | 销售部 | 1 | 2 | 负责意向客户跟进、方案沟通、签约转化。 | 2 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | 教务部 | 1 | 3 | 负责课程安排、学生成绩、请假审批和学业管理。 | 3 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | 客服部 | 1 | 4 | 负责客户咨询、活动报名、常见问题解答。 | 4 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | 市场部 | 1 | 5 | 负责市场活动、讲座推广、私域流量沉淀。 | 5 | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |

### `sys_user`

| ?? | ?? | ??? | ??? | ?? |
| --- | --- | --- | --- | --- |
| id | BIGINT | ? | - | 用户ID |
| username | VARCHAR(80) | ? | - | 登录账号 |
| password_hash | VARCHAR(255) | ? | - | 密码哈希，若接入第三方登录可为空 |
| real_name | VARCHAR(100) | ? | - | 真实姓名 |
| user_type | VARCHAR(20) | ? | - | 用户类型：employee员工/student学生/customer访客/admin管理员 |
| phone | VARCHAR(30) | ? | - | 手机号 |
| email | VARCHAR(120) | ? | - | 邮箱 |
| status | VARCHAR(20) | ? | 'enabled' | 账号状态：enabled启用/disabled禁用 |
| create_time | DATETIME | ? | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | ? | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| is_delete | TINYINT | ? | '0' | 软删除标记：0-未删除，1-已删除 |

| id | username | password_hash | real_name | user_type | phone | email | status | create_time | update_time | is_delete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | emp001 | $2***01 | 高远 | employee | 13***01 | g***@example.com | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 2 | emp002 | $2***02 | 李娜 | employee | 13***02 | l***@example.com | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 3 | emp003 | $2***03 | 王强 | employee | 13***03 | w***@example.com | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 4 | emp004 | $2***04 | 赵敏 | employee | 13***04 | z***@example.com | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
| 5 | emp005 | $2***05 | 陈磊 | employee | 13***05 | c***@example.com | enabled | 2026-06-10 12:03:21 | 2026-06-10 12:03:21 | 0 |
