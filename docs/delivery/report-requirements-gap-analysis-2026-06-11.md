
# 报告模块五类报告 vs 真实需求 — 差距分析与改进方案

**生成日期**：2026-06-11
**对比基准**：真实 Dify 输出（`report-five-types-real-dify-2026-06-11.md`），数据源为真实 MySQL
**统计口径**：咨询一部（department_id=1），周期 2026-06-01 至 2026-06-07

---

## 总体结论

真实 Dify（DeepSeek）版**全面达成需求核心意图**，质量远超 Mock 模板版——LLM 真正做到主动计算衍生指标、跨字段关联分析、分层给建议。

五类报告共 **5 项"部分达成"**，无"完全未达成"项。员工日报 5/5 全达成、无缺口。5 项缺口全部指向**数据采集/入库的上游环节**，报告生成模块本身（DAO 聚合 + Dify LLM）已具备需求要求的全部洞察能力。

| 报告 | 达成度 | 部分达成项 |
|---|---|---|
| 投诉处理周报 | 5/7 | AI 智能分类、根因归因 |
| 全域客户经营 | 4/5 | 特征聚类画像 |
| 员工日报汇总 | 5/5 | —（全达成） |
| 学生心理健康 | 4/6 | 情绪/文化冲突识别、留学周期节点 |

---

## 一、投诉处理周报

**需求原文要点**：实时汇总投诉总量及同环比 → AI 对投诉内容智能分类（签证/院校/生活等）→ 追踪跟进状态/处理时效/满意度 → 自动识别长期未决案件并预警 → 可视化处理进度与归因分析。

| 需求点 | 达成 | 说明 |
|---|---|---|
| 投诉总量 + 同环比 | ✅ | 10 件、环比 +42.9%、上升趋势 |
| AI 智能分类 | ⚠️ | 报告按 7 类中文分类展示分布，但分类值来自工单入库时人工/预设的 `category` 字段，非读 `detail` 正文实时判定 |
| 跟进状态追踪 | ✅ | 待处理/处理中/已解决/已关闭 + 解决率 60% |
| 处理时效 | ✅ | 平均 31.7h + 与 48h 阈值对比 |
| 满意度 | ✅ | 3.8 分 + 结合解决率判断服务质量 |
| 长期未决预警 | ✅ | 超期 6 件，列入风险并要求专人限时闭环 |
| 归因分析 | ⚠️ | LLM 基于分类计数推测"教学/签证类涉及复杂流程"，非每条投诉正文的根因定位 |

**差距与根因**：真正的"AI 智能分类/归因"需在工单入库时对 `detail` 正文做语义打标，目前为业务预设字段。

---

## 二、全域客户经营分析报告

**需求原文要点**：覆盖意向/成交/流失三大客群 → 意向客户统计新增及同环比、特征聚类提炼共性画像 → 成交客户深度复盘转化路径与高价值特征 → 流失客户智能归因并预警 → 全链路决策支持。

| 需求点 | 达成 | 说明 |
|---|---|---|
| 意向客户：新增 + 同环比 | ✅ | 8 条、环比 +60% |
| 意向客户：特征聚类画像 | ⚠️ | 输出国家/项目/预算/学历四维分布，但为**单维计数**，非"美国+计算机+高预算"组合聚类 |
| 成交客户：转化路径 + 高价值特征 | ✅ | 2 单、转化率 25%、转化周期 3.5 天、成交渠道(活动+微信)、研判等级均高意向 |
| 流失客户：智能归因 + 预警 | ✅ | 流失 2 条 + 归因(预算不足/竞品) + 渠道 + 挽回策略 |
| 全链路决策支持 | ✅ | 获客→转化→留存全链路建议 |

**差距与根因**："特征聚类"目前是单维分布统计，真聚类需多维交叉分析（上游数据建模）。

---

## 三、员工日报智能汇总报告（日 + 周）

**需求原文要点**：日/周多维时间粒度 → AI 智能提取核心进展、关键产出及潜在风险 → 碎片化记录转为结构化简报 → 降低领导阅读成本、感知团队进度与项目健康度 → 支撑资源协调与战略决策。

| 需求点 | 达成 | 说明 |
|---|---|---|
| 日/周多粒度 | ✅ | 日报、周报独立成报 |
| AI 提取核心进展/关键产出 | ✅ | 日报提炼 5 项关键进展，覆盖销售/客服/文书岗位 |
| AI 提取潜在风险 | ✅ | 周报高频风险主题：进度 10/时间 7/资料 7/客户 6/签约 6 |
| 结构化简报降低阅读成本 | ✅ | 摘要 + 分章节 + 指标表 + 建议 |
| 团队进度/项目健康度感知 | ✅ | 提交率、峰谷日、风险密度、覆盖率 |

**亮点**：周报识别"周三低谷"并建议增设提醒；日报指出"80% 含风险，签约/院校/预算三类集中爆发属核心风险链"。

**差距**：几乎无。唯一小细节——LLM 对单日"提交率 25%"反推"应交约 20 份"，是它对口径的推算，与周报口径略有差异，不影响判断。

---

## 四、学生心理健康周报

**需求原文要点**：基于情绪打卡/学业压力/跨文化适应 → AI 汇总整体心理态势 → 识别孤独感/学业焦虑/文化冲突风险群体 → 结合留学周期节点（考试周/假期）生成情绪波动趋势 → 智能推荐个性化疏导方案与社群支持 → 主动关怀增强客户粘性。

| 需求点 | 达成 | 说明 |
|---|---|---|
| 整体心理态势汇总 | ✅ | 6 画像、均分 50.5、低于阈值判断 |
| 识别孤独/学业焦虑/文化冲突 | ⚠️ | 识别出焦虑/低落/孤独/压力，但依赖 `latest_emotion_tag` 预打标；无"文化冲突"专门标签 |
| 留学周期节点（考试周/假期） | ⚠️ | LLM 结合"学期中段、考试临近"分析，但 period_hint 按月硬编码近似，非真实学期日历 |
| 情绪波动趋势 | ✅ | 逐日互动趋势 + 峰值判断 + "6月4-6日中断需核实" |
| 个性化疏导 + 社群支持 | ✅ | 分层建议：critical→危机干预、high→朋辈导师、考试季→减压团体活动 |
| 主动关怀增强粘性 | ✅ | 引用情绪摘录（隐私合规，无 student_id） |

**亮点**：LLM 引用真实情绪摘录增强叙事，识别"周末互动中断可能是求助通道阻塞"。

**差距与根因**：情绪标签和留学周期依赖上游数据预设，非报告层的实时语义识别。

---

## 共性差距与根因

所有"⚠️ 部分达成"项的根因相同：需求中的"AI 智能分类/聚类/识别"指对**原始文本**（投诉正文、线索背景、心理记录）做语义理解并打标，而当前架构中这些标签是**业务录入时预设**的字段，报告生成阶段只是消费这些字段。

报告生成本身（DAO 聚合 + Dify LLM 分析）已实现需求要求的全部"洞察"能力。

**补齐方向**（独立于报告模块的上游功能）：
1. 投诉工单入库时调用 Dify 对 `detail` 正文做实时分类与根因打标。
2. 线索录入时由 AI 提取多维画像并做交叉聚类（如"美国+计算机+高预算"客群）。
3. 心理记录引入情绪语义识别模型，补充"文化冲突"等细分标签。
4. 接入院校学期日历表，替代 period_hint 的按月近似。

---

## 工程侧本轮修复记录

| 修复项 | 文件 | 说明 |
|---|---|---|
| 成交客户数恒为 0 | `dify_client.py` | 中文 key 查询改为英文枚举 `signed`，并接入 DAO 成交专项字段 |
| 成交专项聚合缺失 | `report_dao.py` | 新增 signed_count/signed_source_breakdown/avg_conversion_days/signed_conversion_rate |
| 流失状态枚举错配 | `report_dao.py` | 统一为 `["lost","invalid"]`，对齐模型定义 |
| 风险主题词恒空 | `report_dao.py` | 关键词表编码损坏（10 个 `??`）已恢复中文 |
| 处理时长未渲染 | `dify_client.py` | 投诉周报补渲染 avg_processing_hours |
| 报告 JSON 截断 | `dify_client.py` | 新增 `_repair_truncated_json` 括号栈兜底，挽救被截断的 LLM 输出 |
| 测试误打真实 Dify | `conftest.py` | autouse fixture 强制测试期 Mock，与 .env 解耦 |
| Dify 输出截断根因 | `reports.yml` | max_tokens 提至 384000、关闭 thinking 模式 |

**测试**：55 passed（含截断挽救新测试）。

---

# 改进方案

针对上述 5 项"部分达成"缺口的落地方案。所有缺口均位于**数据采集/入库的上游环节**，报告生成模块本身无需改动。

## 可复用基础（关键前提）

探查发现项目已有可直接复用的轻量 LLM 调用模式，无需依赖 Dify 服务：

- **直连 DeepSeek**：`enterprise_nl2sql_service.py` 用 OpenAI SDK 直连（`from openai import OpenAI`），配置项 `nl2sql_llm_api_key` / `nl2sql_llm_base_url` / `nl2sql_llm_model` 已就绪。这是做文本分类、情绪识别等轻量 AI 任务的**最佳路径**（延迟低、无外部依赖）。
- **调用模板**：`client.chat.completions.create(model, messages, temperature=0, max_tokens)` → 解析 `response.choices[0].message.content`。仿照 NL2SQL 的 `build_messages` + `extract_sql` 改成 `build_prompt` + `parse_tag` 即可。
- **入库切入点**：工单 `StudentFeedbackTicketService.create_ticket()`、心理 `StudentPsychService.update_emotion()` 都有现成方法可挂 AI 打标。

## 方案 A：投诉工单 AI 实时分类 + 根因打标（缺口 1、2）

**切入点**：`backend/app/services/student_feedback_ticket_service.py` 的 `create_ticket()`，工单落库后。

**做法**：
1. 新建 `TextClassifier` service（仿 NL2SQL 的 OpenAI SDK 模式），对 `detail` 正文调 DeepSeek。
2. 输出分类标签 → 写回 `category`（覆盖或补全人工值）。
3. 输出根因摘要 → 写回目前**闲置的 `content_summary` 字段**。

**同步 vs 异步**：创建接口同步调 LLM 增加 1-2 秒延迟，建议**创建后异步更新**（后台任务或独立打标接口），不阻塞用户提交。

**报告侧**：DAO 已聚合 `category`，无需改；`content_summary` 可作为新维度喂给 Dify 做真正的根因分析。

**工作量**：中（新增 1 个 service + 1 段 prompt + create_ticket 挂钩）。

## 方案 B：客户线索多维聚类画像（缺口 3）

分两层，按投入选择：

**B-轻量（推荐先做）**：在 `report_dao._query_customer_operation` 加一个**组合维度 GROUP BY**——按 `(target_country, target_program, budget_range)` 组合计数，取 Top-N 输出"美国+计算机硕士+50-80万（3人）"这样的真聚类客群。纯 SQL，无 LLM。

**B-重量（可选）**：线索录入时调 LLM 对 `background_info` 正文提取结构化画像标签再聚类。

**前置依赖**：`CustomerAnalysisRecord` 的 controller/service 目前是**空壳文件**（`ai_tools/customer_judgement_tools.py` 也为空），`match_level` 等字段无赋值逻辑。要让研判数据真实可用，需先从零实现研判 service（可同时接 AI 判定 match_level）。

**工作量**：B-轻量小；补齐研判 service 中等。

## 方案 C：心理情绪语义识别 + 文化冲突标签（缺口 4）

**切入点**：`backend/app/services/student_psych_service.py` 的 `update_emotion()` 之前。目前情绪字段全靠人工传入。

**做法**：
1. 新增"情绪打卡/交流"入口（目前**无**学生自助打卡接口），学生输入文本 → DeepSeek 识别 → 自动生成 `latest_emotion_tag` / `emotion_score` / `emotion_summary`，再调现有 `update_emotion()`。
2. 在 `dify_client.py` 的 `EMOTION_TAG_MAP` 补 `"cultural_conflict": "文化冲突"`，识别 prompt 里加入这一类。

**工作量**：中（新增打卡接口 + 情绪识别 service + 标签体系扩展）。

## 方案 D：接入学期日历替代按月近似（缺口 5）

**做法**：新增（或复用库中已有的 `academic_event` 表）一张学期日历表，存考试周/假期/开学的真实日期区间；`report_dao` 查当前周期落在哪个节点，替代 `dify_client.py` 中 `period_hint` 的硬编码月份判断。

**工作量**：小到中（建表 + 区间查询 + 替换硬编码）。

## 优先级建议

| 优先级 | 方案 | 理由 |
|---|---|---|
| P0 | B-轻量（组合维度聚类） | 纯 SQL，工作量最小，直接补上"特征聚类"需求原话 |
| P0 | D（学期日历） | 工作量小，去掉明显的"近似"硬编码 |
| P1 | A（工单 AI 打标） | 中等工作量，补齐投诉两个缺口，复用现成 DeepSeek 模式 |
| P1 | C（情绪识别） | 中等工作量，需先设计学生打卡入口 |
| P2 | B-补齐研判 service | 较大，独立功能模块，可单独立项 |

四项均为**报告模块之外的上游功能**，互相独立，可分批实施。报告生成模块（DAO + Dify LLM）已无需改动。

---

## 本轮落地记录（2026-06-11）

P0+P1 四个方案已实现，P2（研判 service）按计划单独立项暂未做。

| 方案 | 状态 | 落地内容 |
|---|---|---|
| A 工单 AI 打标 | ✅ 已实现 | 新增 `ticket_classifier_service.py`（复用共享 LLM 客户端），挂到 `create_ticket()` 后做分类+根因打标，写回 `category`/`content_summary`；新增 `POST /student-feedback-tickets/{id}/classify` 支持异步重标。仅补全空字段，LLM 不可用时静默跳过不阻塞创建。 |
| B-轻量 组合聚类 | ✅ 已实现 | `report_dao._query_customer_operation` 新增 `(target_country, target_program, budget_range)` 组合 GROUP BY，输出 Top-5 `cluster_breakdown`（如"美国+计算机硕士+50-80万（3人）"）；dify_client 客群画像章节渲染，reports.yml prompt 同步增补。纯 SQL。 |
| C 情绪识别 | ✅ 已实现 | 新增 `emotion_recognition_service.py`（识别情绪标签/分值/摘要，含 `cultural_conflict` 文化冲突标签并映射风险等级）；新增学生情绪打卡 `POST /psych/profile/checkin` → 调 AI → 更新心理画像；dify_client `EMOTION_TAG_MAP` 与 reports.yml 补充文化冲突类。 |
| D 学期日历 | ✅ 已实现 | 复用现有 `academic_event` 表，`report_dao._derive_period_hint()` 查询周期内公共学业事件（考试/论文 DDL）派生真实 `period_hint`；dify_client 优先用该值，无真实事件时回退按月近似。 |
| 共享基础 | ✅ 已实现 | 新增 `llm_text_client.py`，仿 NL2SQL 的 OpenAI SDK 直连模式封装通用文本补全 + 容错 JSON 解析，供 A/C 复用；无 API Key 时 `is_available()` 返回 False，调用方优雅降级。 |
| B-研判 service | ⏸ 未做 | P2，独立功能模块，按计划单独立项。 |

**测试**：新增 5 个测试文件共 34 个用例（LLM 客户端解析、工单分类降级/写回、情绪识别风险映射、组合聚类 SQL、period_hint 派生、打卡端到端）。全量 **89 passed, 3 skipped**（基线 55 passed，零回归）。

**测试基建修复**：conftest 新增 `@compiles(BigInteger, "sqlite")→INTEGER` 钩子，使 SQLite 下 BigInt 主键能自增（此前 `create_ticket` 等不显式赋 id 的插入在 SQLite 无法落库，真实 MySQL 不受影响）。
