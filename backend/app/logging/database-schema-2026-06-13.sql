
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `academic_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `academic_event` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '学业考务事件ID',
  `student_id` bigint DEFAULT NULL COMMENT '学生ID，为空表示公共事件',
  `event_type` varchar(50) NOT NULL COMMENT '事件类型：paper_deadline论文DDL/exam考试/course_deadline课程截止/other其他',
  `title` varchar(300) NOT NULL COMMENT '事件标题',
  `event_desc` text COMMENT '事件说明',
  `course_name` varchar(200) DEFAULT NULL COMMENT '关联课程',
  `deadline_time` datetime NOT NULL COMMENT '截止或考试时间',
  `reminder_time` datetime DEFAULT NULL COMMENT '提醒时间',
  `status` varchar(30) NOT NULL DEFAULT 'active' COMMENT '状态：active有效/completed已完成/cancelled已取消',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_academic_student_id` (`student_id`),
  KEY `idx_academic_type` (`event_type`),
  KEY `idx_academic_deadline_time` (`deadline_time`),
  KEY `idx_academic_status` (`status`),
  CONSTRAINT `fk_academic_student` FOREIGN KEY (`student_id`) REFERENCES `student_profile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学业考务事件表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `ai_draft`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ai_draft` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'AI草稿ID',
  `draft_no` varchar(50) NOT NULL COMMENT '草稿编号',
  `draft_type` varchar(50) NOT NULL COMMENT '草稿类型',
  `biz_module` varchar(50) NOT NULL COMMENT '业务模块',
  `biz_object_type` varchar(80) DEFAULT NULL COMMENT '关联业务对象类型',
  `biz_object_id` bigint DEFAULT NULL COMMENT '关联业务对象ID',
  `status` varchar(30) NOT NULL DEFAULT 'generating' COMMENT '草稿状态',
  `content_json` json NOT NULL COMMENT '草稿内容JSON',
  `source_trace_id` varchar(100) DEFAULT NULL COMMENT '来源链路ID',
  `created_by` bigint DEFAULT NULL COMMENT '创建人用户ID',
  `confirmed_by` bigint DEFAULT NULL COMMENT '确认人用户ID',
  `confirmed_time` datetime DEFAULT NULL COMMENT '确认时间',
  `reject_reason` varchar(500) DEFAULT NULL COMMENT '驳回原因',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_ai_draft_no` (`draft_no`),
  KEY `idx_ai_draft_type` (`draft_type`),
  KEY `idx_ai_draft_module` (`biz_module`),
  KEY `idx_ai_draft_status` (`status`),
  KEY `idx_ai_draft_created_by` (`created_by`),
  KEY `idx_ai_draft_confirmed_by` (`confirmed_by`)
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI草稿公共表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `ai_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ai_report` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `report_no` varchar(50) NOT NULL,
  `report_type` varchar(50) NOT NULL,
  `title` varchar(200) NOT NULL,
  `status` varchar(30) NOT NULL DEFAULT 'confirmed',
  `content_json` json NOT NULL,
  `source_draft_id` bigint NOT NULL,
  `date_start` date NOT NULL,
  `date_end` date NOT NULL,
  `department_id` bigint DEFAULT NULL,
  `created_by` bigint DEFAULT NULL,
  `published_by` bigint DEFAULT NULL,
  `published_time` datetime DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_no` (`report_no`),
  KEY `source_draft_id` (`source_draft_id`),
  KEY `department_id` (`department_id`),
  KEY `created_by` (`created_by`),
  KEY `published_by` (`published_by`),
  CONSTRAINT `ai_report_ibfk_1` FOREIGN KEY (`source_draft_id`) REFERENCES `ai_draft` (`id`),
  CONSTRAINT `ai_report_ibfk_2` FOREIGN KEY (`department_id`) REFERENCES `sys_department` (`id`),
  CONSTRAINT `ai_report_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `sys_user` (`id`),
  CONSTRAINT `ai_report_ibfk_4` FOREIGN KEY (`published_by`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_log` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '审计日志ID',
  `operator_user_id` bigint DEFAULT NULL COMMENT '操作人用户ID',
  `operator_role` varchar(50) DEFAULT NULL COMMENT '操作人角色',
  `action_type` varchar(80) NOT NULL COMMENT '操作类型',
  `biz_module` varchar(50) NOT NULL COMMENT '业务模块',
  `biz_object_type` varchar(80) DEFAULT NULL COMMENT '业务对象类型',
  `biz_object_id` bigint DEFAULT NULL COMMENT '业务对象ID',
  `before_json` json DEFAULT NULL COMMENT '操作前数据摘要',
  `after_json` json DEFAULT NULL COMMENT '操作后数据摘要',
  `draft_id` bigint DEFAULT NULL COMMENT '关联AI草稿ID',
  `trace_id` varchar(100) DEFAULT NULL COMMENT '链路追踪ID',
  `result` varchar(30) NOT NULL DEFAULT 'success' COMMENT '执行结果',
  `error_message` varchar(1000) DEFAULT NULL COMMENT '失败原因',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_audit_operator` (`operator_user_id`),
  KEY `idx_audit_action_type` (`action_type`),
  KEY `idx_audit_draft_id` (`draft_id`),
  KEY `idx_audit_trace_id` (`trace_id`),
  KEY `idx_audit_create_time` (`create_time`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统操作审计日志表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `course_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_project` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '课程项目ID',
  `project_name` varchar(200) NOT NULL COMMENT '课程或项目名称',
  `project_type` varchar(50) NOT NULL COMMENT '项目类型：language语言培训/background背景提升/application留学申请/upgrade学历提升',
  `target_country` varchar(100) DEFAULT NULL COMMENT '适用国家',
  `target_education_level` varchar(100) DEFAULT NULL COMMENT '适用学历阶段',
  `target_audience` varchar(500) DEFAULT NULL COMMENT '适合人群',
  `project_desc` text COMMENT '项目详情',
  `price_range` varchar(100) DEFAULT NULL COMMENT '价格区间',
  `status` varchar(20) NOT NULL DEFAULT 'enabled' COMMENT '状态：enabled上架/disabled下架',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_project_type` (`project_type`),
  KEY `idx_project_country` (`target_country`),
  KEY `idx_project_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='课程与项目表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `crm_lead`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_lead` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '意向客户ID',
  `lead_no` varchar(50) NOT NULL COMMENT '线索编号',
  `customer_name` varchar(100) NOT NULL COMMENT '客户姓名',
  `phone` varchar(30) DEFAULT NULL COMMENT '手机号',
  `wechat_no` varchar(100) DEFAULT NULL COMMENT '微信号',
  `email` varchar(120) DEFAULT NULL COMMENT '邮箱',
  `source_channel` varchar(100) DEFAULT NULL COMMENT '来源渠道',
  `education_level` varchar(100) DEFAULT NULL COMMENT '学历阶段',
  `school_name` varchar(200) DEFAULT NULL COMMENT '学校名称',
  `major` varchar(200) DEFAULT NULL COMMENT '专业',
  `current_grade` varchar(100) DEFAULT NULL COMMENT '当前年级',
  `target_country` varchar(100) DEFAULT NULL COMMENT '意向国家',
  `target_program` varchar(200) DEFAULT NULL COMMENT '意向项目',
  `budget_range` varchar(100) DEFAULT NULL COMMENT '预算区间',
  `background_info` text COMMENT '客户背景补充信息',
  `follow_up_history` text COMMENT '前期简化保存历史跟进内容，后续可拆成crm_lead_followup表',
  `latest_follow_up_summary` varchar(1000) DEFAULT NULL COMMENT '最近跟进摘要',
  `status` varchar(30) NOT NULL DEFAULT 'new' COMMENT '线索状态：new新增/following跟进中/signed已签约/lost已流失/invalid无效',
  `owner_employee_id` bigint DEFAULT NULL COMMENT '负责员工ID',
  `last_follow_up_time` datetime DEFAULT NULL COMMENT '最近跟进时间',
  `lost_reason` varchar(500) DEFAULT NULL COMMENT '流失原因',
  `signed_time` datetime DEFAULT NULL COMMENT '签约时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_lead_no` (`lead_no`),
  KEY `idx_lead_phone` (`phone`),
  KEY `idx_lead_owner` (`owner_employee_id`),
  KEY `idx_lead_status` (`status`),
  KEY `idx_lead_target_country` (`target_country`),
  KEY `idx_lead_create_time` (`create_time`),
  CONSTRAINT `fk_lead_owner` FOREIGN KEY (`owner_employee_id`) REFERENCES `employee_profile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='意向客户线索表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `customer_analysis_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_analysis_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '客户研判记录ID',
  `analysis_no` varchar(50) NOT NULL COMMENT '研判编号',
  `source_type` varchar(30) NOT NULL COMMENT '来源类型：text文本/pdf简历/excel表格/manual手工录入',
  `source_file_name` varchar(300) DEFAULT NULL COMMENT '来源文件名',
  `raw_content` longtext COMMENT '待研判原始内容',
  `target_product` varchar(100) DEFAULT NULL COMMENT '研判目标产品或服务',
  `lead_id` bigint DEFAULT NULL COMMENT '关联意向客户ID',
  `is_target_customer` tinyint DEFAULT NULL COMMENT '是否符合目标客户画像：1是/0否，未研判为空',
  `match_score` decimal(5,2) DEFAULT NULL COMMENT '匹配分数0-100',
  `match_level` varchar(30) DEFAULT NULL COMMENT '匹配等级：high高/medium中/low低',
  `reason_summary` text COMMENT '研判理由摘要',
  `suggestion` text COMMENT '后续跟进建议',
  `status` varchar(30) NOT NULL DEFAULT 'pending' COMMENT '状态：pending待研判/completed已完成/failed失败',
  `submitter_user_id` bigint DEFAULT NULL COMMENT '提交人用户ID',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_analysis_no` (`analysis_no`),
  KEY `idx_analysis_lead_id` (`lead_id`),
  KEY `idx_analysis_status` (`status`),
  KEY `idx_analysis_score` (`match_score`),
  KEY `fk_analysis_submitter` (`submitter_user_id`),
  CONSTRAINT `fk_analysis_lead` FOREIGN KEY (`lead_id`) REFERENCES `crm_lead` (`id`),
  CONSTRAINT `fk_analysis_submitter` FOREIGN KEY (`submitter_user_id`) REFERENCES `sys_user` (`id`),
  CONSTRAINT `chk_analysis_match_score` CHECK (((`match_score` is null) or ((`match_score` >= 0) and (`match_score` <= 100))))
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户研判记录表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `employee_daily_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_daily_report` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '员工日报ID',
  `employee_id` bigint NOT NULL COMMENT '员工ID',
  `department_id` bigint DEFAULT NULL COMMENT '所属部门ID',
  `report_date` date NOT NULL COMMENT '日报日期',
  `raw_content` text NOT NULL COMMENT '原始口述或输入内容',
  `summary` text COMMENT 'AI摘要',
  `key_progress` text COMMENT '关键进展',
  `risks` text COMMENT '风险与问题',
  `tomorrow_plan` text COMMENT '明日计划',
  `report_status` varchar(20) NOT NULL DEFAULT 'submitted' COMMENT '状态：draft草稿/submitted已提交/archived已归档',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_daily_report_employee_date` (`employee_id`,`report_date`),
  KEY `idx_daily_report_department` (`department_id`),
  KEY `idx_daily_report_date` (`report_date`),
  CONSTRAINT `fk_daily_report_department` FOREIGN KEY (`department_id`) REFERENCES `sys_department` (`id`),
  CONSTRAINT `fk_daily_report_employee` FOREIGN KEY (`employee_id`) REFERENCES `employee_profile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='员工日报表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `employee_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_profile` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '员工ID',
  `user_id` bigint NOT NULL COMMENT '关联用户ID',
  `employee_no` varchar(50) NOT NULL COMMENT '员工编号',
  `employee_name` varchar(100) NOT NULL COMMENT '员工姓名',
  `department_id` bigint DEFAULT NULL COMMENT '所属部门ID',
  `role_code` varchar(50) NOT NULL COMMENT '角色编码：sales顾问/teacher老师/service客服/manager主管/admin管理员',
  `job_title` varchar(100) DEFAULT NULL COMMENT '岗位名称',
  `status` varchar(20) NOT NULL DEFAULT 'active' COMMENT '员工状态：active在职/resigned离职/disabled停用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_employee_user_id` (`user_id`),
  UNIQUE KEY `uk_employee_no` (`employee_no`),
  KEY `idx_employee_department_id` (`department_id`),
  KEY `idx_employee_role_code` (`role_code`),
  KEY `idx_employee_status` (`status`),
  CONSTRAINT `fk_employee_department` FOREIGN KEY (`department_id`) REFERENCES `sys_department` (`id`),
  CONSTRAINT `fk_employee_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='员工档案表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `event_lecture`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_lecture` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '活动讲座ID',
  `event_no` varchar(50) NOT NULL COMMENT '活动编号',
  `event_name` varchar(200) NOT NULL COMMENT '活动名称',
  `event_type` varchar(30) NOT NULL COMMENT '活动类型：online线上/offline线下',
  `topic` varchar(300) DEFAULT NULL COMMENT '活动主题',
  `speaker` varchar(200) DEFAULT NULL COMMENT '主讲人',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `location` varchar(300) DEFAULT NULL COMMENT '线下地点',
  `online_url` varchar(500) DEFAULT NULL COMMENT '线上链接',
  `max_participants` int DEFAULT NULL COMMENT '最大报名人数',
  `current_participants` int NOT NULL DEFAULT '0' COMMENT '当前报名人数',
  `status` varchar(30) NOT NULL DEFAULT 'open' COMMENT '活动状态：open报名中/full已满/closed已结束/cancelled已取消',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_event_no` (`event_no`),
  KEY `idx_event_start_time` (`start_time`),
  KEY `idx_event_type` (`event_type`),
  KEY `idx_event_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='活动与讲座表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `event_registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_registration` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '活动报名ID',
  `event_id` bigint NOT NULL COMMENT '活动ID',
  `lead_id` bigint DEFAULT NULL COMMENT '关联意向客户ID，可为空',
  `visitor_name` varchar(100) NOT NULL COMMENT '报名人姓名',
  `visitor_phone` varchar(30) DEFAULT NULL COMMENT '报名人手机号',
  `registration_status` varchar(30) NOT NULL DEFAULT 'registered' COMMENT '报名状态：registered已报名/cancelled已取消/attended已参加/no_show未到场',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_registration_event_id` (`event_id`),
  KEY `idx_registration_lead_id` (`lead_id`),
  KEY `idx_registration_phone` (`visitor_phone`),
  CONSTRAINT `fk_registration_event` FOREIGN KEY (`event_id`) REFERENCES `event_lecture` (`id`),
  CONSTRAINT `fk_registration_lead` FOREIGN KEY (`lead_id`) REFERENCES `crm_lead` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='活动报名表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `faq_qa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faq_qa` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'FAQ ID',
  `module_scope` varchar(50) NOT NULL COMMENT '适用模块：customer_service/enterprise_assistant/student_assistant/common',
  `category` varchar(100) DEFAULT NULL COMMENT '问题分类',
  `question` varchar(800) NOT NULL COMMENT '标准问题',
  `answer` text NOT NULL COMMENT '标准答案',
  `keywords` varchar(500) DEFAULT NULL COMMENT '关键词',
  `status` varchar(20) NOT NULL DEFAULT 'enabled' COMMENT '状态：enabled启用/disabled停用',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序号',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_faq_scope` (`module_scope`),
  KEY `idx_faq_category` (`category`),
  KEY `idx_faq_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='FAQ标准问答表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `report_export_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_export_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `report_id` bigint NOT NULL,
  `export_type` varchar(20) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `status` varchar(30) NOT NULL,
  `error_message` varchar(1000) DEFAULT NULL,
  `created_by` bigint DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `report_id` (`report_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `report_export_record_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `ai_report` (`id`),
  CONSTRAINT `report_export_record_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `student_application_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_application_progress` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '申请进度ID',
  `student_id` bigint NOT NULL COMMENT '学生ID',
  `progress_stage` varchar(80) NOT NULL COMMENT '进度阶段：essay文书/school_apply院校申请/visa签证/offer录取/other其他',
  `target_country` varchar(100) DEFAULT NULL COMMENT '目标国家',
  `school_name` varchar(200) DEFAULT NULL COMMENT '申请院校',
  `program_name` varchar(200) DEFAULT NULL COMMENT '申请项目',
  `progress_status` varchar(50) NOT NULL DEFAULT 'processing' COMMENT '进度状态：pending待开始/processing处理中/completed已完成/blocked受阻',
  `progress_desc` text COMMENT '进度说明',
  `handler_employee_id` bigint DEFAULT NULL COMMENT '负责人员工ID',
  `expected_finish_time` datetime DEFAULT NULL COMMENT '预计完成时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  `crm_record_id` varchar(100) DEFAULT NULL COMMENT 'CRM系统记录ID',
  `crm_sync_status` varchar(30) NOT NULL DEFAULT 'not_synced' COMMENT 'CRM同步状态：not_synced/syncing/synced/failed',
  `crm_last_sync_time` datetime DEFAULT NULL COMMENT '最近CRM同步时间',
  PRIMARY KEY (`id`),
  KEY `idx_progress_student_id` (`student_id`),
  KEY `idx_progress_stage` (`progress_stage`),
  KEY `idx_progress_status` (`progress_status`),
  KEY `idx_progress_handler` (`handler_employee_id`),
  KEY `idx_progress_crm_record` (`crm_record_id`),
  CONSTRAINT `fk_progress_handler` FOREIGN KEY (`handler_employee_id`) REFERENCES `employee_profile` (`id`),
  CONSTRAINT `fk_progress_student` FOREIGN KEY (`student_id`) REFERENCES `student_profile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生申请进度表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `student_feedback_ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_feedback_ticket` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '反馈工单ID',
  `ticket_no` varchar(50) NOT NULL COMMENT '工单编号',
  `student_id` bigint NOT NULL COMMENT '学生ID',
  `ticket_type` varchar(30) NOT NULL DEFAULT 'complaint' COMMENT '工单类型：complaint投诉/suggestion建议/consult咨询',
  `category` varchar(100) DEFAULT NULL COMMENT '反馈分类：教学/服务/顾问/财务/签证/院校申请/生活服务/其他',
  `title` varchar(300) NOT NULL COMMENT '反馈标题',
  `content_summary` text COMMENT 'AI摘要',
  `detail` text NOT NULL COMMENT '详细反馈内容',
  `priority_level` varchar(30) NOT NULL DEFAULT 'normal' COMMENT '优先级：normal普通/urgent紧急/severe严重',
  `status` varchar(30) NOT NULL DEFAULT 'pending' COMMENT '状态：pending待处理/processing处理中/resolved已解决/closed已关闭',
  `handler_employee_id` bigint DEFAULT NULL COMMENT '当前处理人员工ID',
  `solution` text COMMENT '处理方案或最终结果',
  `satisfaction_score` tinyint DEFAULT NULL COMMENT '满意度评分1-5',
  `is_notified` tinyint NOT NULL DEFAULT '0' COMMENT '是否已通知学生：1是/0否',
  `close_time` datetime DEFAULT NULL COMMENT '关闭时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_feedback_ticket_no` (`ticket_no`),
  KEY `idx_feedback_student_id` (`student_id`),
  KEY `idx_feedback_status` (`status`),
  KEY `idx_feedback_handler` (`handler_employee_id`),
  KEY `idx_feedback_category` (`category`),
  CONSTRAINT `fk_feedback_handler` FOREIGN KEY (`handler_employee_id`) REFERENCES `employee_profile` (`id`),
  CONSTRAINT `fk_feedback_student` FOREIGN KEY (`student_id`) REFERENCES `student_profile` (`id`),
  CONSTRAINT `chk_feedback_satisfaction` CHECK (((`satisfaction_score` is null) or (`satisfaction_score` between 1 and 5)))
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生投诉与售后反馈工单表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `student_leave_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_leave_request` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '请假申请ID',
  `request_no` varchar(50) NOT NULL COMMENT '请假单号',
  `student_id` bigint NOT NULL COMMENT '学生ID',
  `leave_type` varchar(50) NOT NULL COMMENT '请假类型：sick病假/personal事假/other其他',
  `reason` text NOT NULL COMMENT '请假原因',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime NOT NULL COMMENT '结束时间',
  `status` varchar(30) NOT NULL DEFAULT 'pending' COMMENT '审批状态：pending待审批/approved已通过/rejected已驳回/cancelled已撤销',
  `approver_employee_id` bigint DEFAULT NULL COMMENT '审批员工ID',
  `approval_comment` varchar(1000) DEFAULT NULL COMMENT '审批意见',
  `approve_time` datetime DEFAULT NULL COMMENT '审批时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_leave_request_no` (`request_no`),
  KEY `idx_leave_student_id` (`student_id`),
  KEY `idx_leave_status` (`status`),
  KEY `idx_leave_approver` (`approver_employee_id`),
  CONSTRAINT `fk_leave_approver` FOREIGN KEY (`approver_employee_id`) REFERENCES `employee_profile` (`id`),
  CONSTRAINT `fk_leave_student` FOREIGN KEY (`student_id`) REFERENCES `student_profile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生请假申请表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `student_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_profile` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '学生ID',
  `user_id` bigint DEFAULT NULL COMMENT '关联用户ID，未开通账号时可为空',
  `student_no` varchar(50) DEFAULT NULL COMMENT '学生编号',
  `student_name` varchar(100) NOT NULL COMMENT '学生姓名',
  `phone` varchar(30) DEFAULT NULL COMMENT '手机号',
  `email` varchar(120) DEFAULT NULL COMMENT '邮箱',
  `current_school` varchar(200) DEFAULT NULL COMMENT '当前学校',
  `current_grade` varchar(100) DEFAULT NULL COMMENT '当前年级/阶段',
  `target_country` varchar(100) DEFAULT NULL COMMENT '目标留学国家',
  `target_program` varchar(200) DEFAULT NULL COMMENT '目标申请项目',
  `counselor_employee_id` bigint DEFAULT NULL COMMENT '负责顾问员工ID',
  `teacher_employee_id` bigint DEFAULT NULL COMMENT '负责老师员工ID',
  `status` varchar(30) NOT NULL DEFAULT 'active' COMMENT '学生状态：active服务中/graduated已结课/inactive停用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_student_user_id` (`user_id`),
  UNIQUE KEY `uk_student_no` (`student_no`),
  KEY `idx_student_name` (`student_name`),
  KEY `idx_student_phone` (`phone`),
  KEY `idx_student_counselor` (`counselor_employee_id`),
  KEY `idx_student_teacher` (`teacher_employee_id`),
  KEY `idx_student_status` (`status`),
  CONSTRAINT `fk_student_counselor` FOREIGN KEY (`counselor_employee_id`) REFERENCES `employee_profile` (`id`),
  CONSTRAINT `fk_student_teacher` FOREIGN KEY (`teacher_employee_id`) REFERENCES `employee_profile` (`id`),
  CONSTRAINT `fk_student_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生档案表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `student_psych_alert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_psych_alert` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '心理预警ID',
  `alert_no` varchar(50) NOT NULL COMMENT '预警编号',
  `student_id` bigint NOT NULL COMMENT '学生ID',
  `trigger_reason` text NOT NULL COMMENT '触发原因',
  `risk_level` varchar(30) NOT NULL COMMENT '风险等级：medium中/high高/critical危急',
  `status` varchar(30) NOT NULL DEFAULT 'pending' COMMENT '处理状态：pending未处理/processing跟进中/resolved已解除/closed已关闭',
  `teacher_employee_id` bigint DEFAULT NULL COMMENT '负责跟进老师ID',
  `handle_result` text COMMENT '处理结果',
  `close_time` datetime DEFAULT NULL COMMENT '关闭时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_psych_alert_no` (`alert_no`),
  KEY `idx_psych_alert_student_id` (`student_id`),
  KEY `idx_psych_alert_status` (`status`),
  KEY `idx_psych_alert_risk_level` (`risk_level`),
  KEY `fk_psych_alert_teacher` (`teacher_employee_id`),
  CONSTRAINT `fk_psych_alert_student` FOREIGN KEY (`student_id`) REFERENCES `student_profile` (`id`),
  CONSTRAINT `fk_psych_alert_teacher` FOREIGN KEY (`teacher_employee_id`) REFERENCES `employee_profile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生心理预警表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `student_psych_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_psych_profile` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '心理健康画像ID',
  `student_id` bigint NOT NULL COMMENT '学生ID',
  `latest_emotion_tag` varchar(100) DEFAULT NULL COMMENT '最新情绪标签',
  `emotion_score` tinyint DEFAULT NULL COMMENT '情绪分值0-100，越高越积极',
  `risk_level` varchar(30) NOT NULL DEFAULT 'low' COMMENT '风险等级：low低/medium中/high高/critical危急',
  `last_interaction_time` datetime DEFAULT NULL COMMENT '最近心理相关交互时间',
  `emotion_summary` text COMMENT '长期情绪摘要',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_psych_student_id` (`student_id`),
  KEY `idx_psych_risk_level` (`risk_level`),
  CONSTRAINT `fk_psych_profile_student` FOREIGN KEY (`student_id`) REFERENCES `student_profile` (`id`),
  CONSTRAINT `chk_psych_emotion_score` CHECK (((`emotion_score` is null) or ((`emotion_score` >= 0) and (`emotion_score` <= 100))))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生心理健康画像表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `student_score`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_score` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '学生成绩ID',
  `student_id` bigint NOT NULL COMMENT '学生ID',
  `course_name` varchar(200) NOT NULL COMMENT '课程名称',
  `score` decimal(5,2) NOT NULL COMMENT '成绩分数',
  `exam_type` varchar(50) DEFAULT NULL COMMENT '考试类型：daily平时/midterm期中/final期末/makeup补考/other其他',
  `semester` varchar(100) DEFAULT NULL COMMENT '学期',
  `exam_date` date DEFAULT NULL COMMENT '考试日期',
  `operator_employee_id` bigint DEFAULT NULL COMMENT '录入员工ID',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_score_student_id` (`student_id`),
  KEY `idx_score_course_name` (`course_name`),
  KEY `idx_score_semester` (`semester`),
  KEY `idx_score_exam_date` (`exam_date`),
  KEY `fk_score_operator` (`operator_employee_id`),
  CONSTRAINT `fk_score_operator` FOREIGN KEY (`operator_employee_id`) REFERENCES `employee_profile` (`id`),
  CONSTRAINT `fk_score_student` FOREIGN KEY (`student_id`) REFERENCES `student_profile` (`id`),
  CONSTRAINT `chk_student_score_range` CHECK (((`score` >= 0) and (`score` <= 100)))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生成绩表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `sys_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_department` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '部门ID',
  `department_name` varchar(100) NOT NULL COMMENT '部门名称',
  `parent_id` bigint DEFAULT NULL COMMENT '上级部门ID，顶级部门为空',
  `leader_employee_id` bigint DEFAULT NULL COMMENT '部门负责人ID，前期只存ID不强制外键，避免循环依赖',
  `department_desc` varchar(500) DEFAULT NULL COMMENT '部门职责说明',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序号',
  `status` varchar(20) NOT NULL DEFAULT 'enabled' COMMENT '状态：enabled启用/disabled停用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  KEY `idx_department_parent_id` (`parent_id`),
  KEY `idx_department_status` (`status`),
  CONSTRAINT `fk_department_parent` FOREIGN KEY (`parent_id`) REFERENCES `sys_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='部门组织架构表';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(80) NOT NULL COMMENT '登录账号',
  `password_hash` varchar(255) DEFAULT NULL COMMENT '密码哈希，若接入第三方登录可为空',
  `real_name` varchar(100) NOT NULL COMMENT '真实姓名',
  `user_type` varchar(20) NOT NULL COMMENT '用户类型：employee员工/student学生/customer访客/admin管理员',
  `phone` varchar(30) DEFAULT NULL COMMENT '手机号',
  `email` varchar(120) DEFAULT NULL COMMENT '邮箱',
  `status` varchar(20) NOT NULL DEFAULT 'enabled' COMMENT '账号状态：enabled启用/disabled禁用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` tinyint NOT NULL DEFAULT '0' COMMENT '软删除标记：0-未删除，1-已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_username` (`username`),
  KEY `idx_user_phone` (`phone`),
  KEY `idx_user_type` (`user_type`),
  KEY `idx_user_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='统一用户表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

