<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  queryNl2Sql,
  queryOnboardingGuide,
  searchLeads,
  searchStudents,
  summarizeStatistics,
  summarizeTodos,
} from "@/api/enterpriseAssistant";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type {
  LeadItem,
  Nl2SqlResult,
  OnboardingGuideResult,
  StatisticsSummaryResult,
  StudentProfileItem,
  TodoSummaryResult,
} from "@/types/enterpriseAssistant";

const router = useRouter();
const loading = ref(false);
const queryLoading = ref(false);
const message = ref("");
const activeTab = ref<"leads" | "students" | "todos" | "statistics" | "nl2sql" | "guide">("leads");
const leads = ref<LeadItem[]>([]);
const students = ref<StudentProfileItem[]>([]);
const leadTotal = ref(0);
const studentTotal = ref(0);
const leadKeyword = ref("");
const studentKeyword = ref("");
const leadStatus = ref("");
const targetCountry = ref("");
const todoSummary = ref<TodoSummaryResult | null>(null);
const statistics = ref<StatisticsSummaryResult | null>(null);
const nlQuery = ref("统计各线索状态的客户数量，按数量倒序");
const nlResult = ref<Nl2SqlResult | null>(null);
const guideQuestion = ref("新人入职后如何提交日报？");
const guideResult = ref<OnboardingGuideResult | null>(null);
const selectedLead = ref<LeadItem | null>(null);
const selectedStudent = ref<StudentProfileItem | null>(null);

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const staleLeadCount = computed(() => todoSummary.value?.stale_leads.length || 0);
const pendingLeaveCount = computed(() => todoSummary.value?.pending_leaves.length || 0);
const pendingFeedbackCount = computed(() => todoSummary.value?.feedback_tickets.length || 0);
const leadStatusCount = computed(() => {
  const source = statistics.value?.lead_count_by_status || {};
  return Object.values(source).reduce((sum, item) => sum + Number(item), 0);
});

const leadStatusMap: Record<string, string> = {
  new: "新增",
  following: "跟进中",
  signed: "已签约",
  lost: "已流失",
  invalid: "无效",
};

function statusLabel(value?: string | null): string {
  if (!value) return "-";
  return leadStatusMap[value] || value;
}

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

async function loadLeads() {
  const result = await searchLeads({
    customer_name: leadKeyword.value,
    status: leadStatus.value,
    target_country: targetCountry.value,
    page: 1,
    page_size: 10,
  });
  leads.value = result.items || [];
  leadTotal.value = result.total;
  selectedLead.value = leads.value[0] || null;
}

async function loadStudents() {
  const result = await searchStudents({
    student_name: studentKeyword.value,
    target_country: targetCountry.value,
    page: 1,
    page_size: 10,
  });
  students.value = result.items || [];
  studentTotal.value = result.total;
  selectedStudent.value = students.value[0] || null;
}

async function loadSummaries() {
  const [todoResult, statisticsResult] = await Promise.all([
    summarizeTodos(3, 10),
    summarizeStatistics({ detail_limit: 10 }),
  ]);
  todoSummary.value = todoResult;
  statistics.value = statisticsResult;
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    await Promise.all([loadLeads(), loadStudents(), loadSummaries()]);
  } catch (error) {
    message.value = error instanceof Error ? error.message : "企业查询数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function refreshCurrentTab() {
  loading.value = true;
  message.value = "";
  try {
    if (activeTab.value === "leads") await loadLeads();
    if (activeTab.value === "students") await loadStudents();
    if (activeTab.value === "todos" || activeTab.value === "statistics") await loadSummaries();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "数据刷新失败";
  } finally {
    loading.value = false;
  }
}

async function handleNl2Sql() {
  if (!nlQuery.value.trim()) return;
  queryLoading.value = true;
  message.value = "";
  try {
    nlResult.value = await queryNl2Sql(nlQuery.value.trim());
  } catch (error) {
    message.value = error instanceof Error ? error.message : "智能问数失败";
  } finally {
    queryLoading.value = false;
  }
}

async function handleGuideQuery() {
  if (!guideQuestion.value.trim()) return;
  queryLoading.value = true;
  message.value = "";
  try {
    guideResult.value = await queryOnboardingGuide(guideQuestion.value.trim());
  } catch (error) {
    message.value = error instanceof Error ? error.message : "入职指引查询失败";
  } finally {
    queryLoading.value = false;
  }
}

function handleLogout() {
  logout();
  router.push("/login");
}

onMounted(loadData);
</script>

<template>
  <div class="app-frame">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-mark">留</div>
        <div>
          <strong>教育服务系统</strong>
          <span>留学服务运营中台</span>
        </div>
      </div>
      <nav>
        <RouterLink to="/dashboard">工作台</RouterLink>
        <RouterLink to="/students/leaves">请假审批</RouterLink>
        <RouterLink to="/students/psych">心理预警</RouterLink>
        <RouterLink to="/students/progress">申请进度</RouterLink>
        <RouterLink to="/students/feedback">反馈工单</RouterLink>
        <RouterLink to="/reports">智能报告</RouterLink>
        <RouterLink to="/customer-judgement">客户研判</RouterLink>
        <a class="active">企业查询</a>
      </nav>
    </aside>

    <main class="dashboard enterprise-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">企业管理</p>
          <h1>企业查询</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="leave-summary enterprise-summary">
        <article>
          <span>客户线索</span>
          <strong>{{ leadTotal }}</strong>
          <p>可按姓名、状态和国家筛选</p>
        </article>
        <article>
          <span>学生档案</span>
          <strong>{{ studentTotal }}</strong>
          <p>查询在读、目标国家和顾问关联</p>
        </article>
        <article>
          <span>待办事项</span>
          <strong>{{ pendingLeaveCount + pendingFeedbackCount + staleLeadCount }}</strong>
          <p>请假、反馈和超时未跟进线索</p>
        </article>
        <article>
          <span>统计线索</span>
          <strong>{{ leadStatusCount }}</strong>
          <p>按状态汇总当前运营数据</p>
        </article>
      </section>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="enterprise-workspace">
        <div class="enterprise-main-panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">查询范围</p>
              <h2>业务数据检索</h2>
            </div>
            <div class="enterprise-tabs">
              <button :class="{ active: activeTab === 'leads' }" type="button" @click="activeTab = 'leads'">线索</button>
              <button :class="{ active: activeTab === 'students' }" type="button" @click="activeTab = 'students'">学生</button>
              <button :class="{ active: activeTab === 'todos' }" type="button" @click="activeTab = 'todos'">待办</button>
              <button :class="{ active: activeTab === 'statistics' }" type="button" @click="activeTab = 'statistics'">统计</button>
              <button :class="{ active: activeTab === 'nl2sql' }" type="button" @click="activeTab = 'nl2sql'">问数</button>
              <button :class="{ active: activeTab === 'guide' }" type="button" @click="activeTab = 'guide'">指引</button>
            </div>
          </div>

          <template v-if="activeTab === 'leads'">
            <div class="filter-row enterprise-filter">
              <input v-model="leadKeyword" placeholder="客户姓名" @keyup.enter="refreshCurrentTab" />
              <select v-model="leadStatus" @change="refreshCurrentTab">
                <option value="">全部状态</option>
                <option value="new">新增</option>
                <option value="following">跟进中</option>
                <option value="signed">已签约</option>
                <option value="lost">已流失</option>
                <option value="invalid">无效</option>
              </select>
              <input v-model="targetCountry" placeholder="目标国家" @keyup.enter="refreshCurrentTab" />
              <button class="ghost-button" type="button" @click="refreshCurrentTab">查询</button>
            </div>
            <div v-if="loading" class="empty-state">正在加载客户线索...</div>
            <table v-else class="leave-table">
              <thead>
                <tr>
                  <th>客户</th>
                  <th>目标国家</th>
                  <th>项目</th>
                  <th>负责人</th>
                  <th>状态</th>
                  <th>最近跟进</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in leads" :key="item.id" :class="{ selected: selectedLead?.id === item.id }" @click="selectedLead = item">
                  <td>
                    <strong>{{ item.customer_name }}</strong>
                    <span>{{ item.lead_no }}</span>
                  </td>
                  <td>{{ item.target_country || "-" }}</td>
                  <td>{{ item.target_program || "-" }}</td>
                  <td>{{ item.owner_name || "-" }}</td>
                  <td><span :class="['status-chip', item.status]">{{ statusLabel(item.status) }}</span></td>
                  <td>{{ formatDateTime(item.last_follow_up_time) }}</td>
                </tr>
              </tbody>
            </table>
          </template>

          <template v-if="activeTab === 'students'">
            <div class="filter-row enterprise-filter">
              <input v-model="studentKeyword" placeholder="学生姓名" @keyup.enter="refreshCurrentTab" />
              <input v-model="targetCountry" placeholder="目标国家" @keyup.enter="refreshCurrentTab" />
              <button class="ghost-button" type="button" @click="refreshCurrentTab">查询</button>
            </div>
            <div v-if="loading" class="empty-state">正在加载学生档案...</div>
            <table v-else class="leave-table">
              <thead>
                <tr>
                  <th>学生</th>
                  <th>当前学校</th>
                  <th>年级</th>
                  <th>目标国家</th>
                  <th>目标项目</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in students"
                  :key="item.id"
                  :class="{ selected: selectedStudent?.id === item.id }"
                  @click="selectedStudent = item"
                >
                  <td>
                    <strong>{{ item.student_name }}</strong>
                    <span>{{ item.student_no || `ID ${item.id}` }}</span>
                  </td>
                  <td>{{ item.current_school || "-" }}</td>
                  <td>{{ item.current_grade || "-" }}</td>
                  <td>{{ item.target_country || "-" }}</td>
                  <td>{{ item.target_program || "-" }}</td>
                  <td><span class="status-chip resolved">{{ item.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </template>

          <template v-if="activeTab === 'todos'">
            <div class="enterprise-card-grid">
              <article>
                <span>待审批请假</span>
                <strong>{{ pendingLeaveCount }}</strong>
                <p>来自学生请假审批队列</p>
              </article>
              <article>
                <span>待处理反馈</span>
                <strong>{{ pendingFeedbackCount }}</strong>
                <p>投诉、咨询、建议未闭环</p>
              </article>
              <article>
                <span>超时线索</span>
                <strong>{{ staleLeadCount }}</strong>
                <p>超过 3 天未跟进</p>
              </article>
            </div>
            <div class="assistant-message enterprise-summary-text">
              <strong>待办摘要</strong>
              <p>{{ todoSummary?.summary.text || "暂无待办摘要" }}</p>
            </div>
          </template>

          <template v-if="activeTab === 'statistics'">
            <div class="enterprise-card-grid">
              <article v-for="(count, status) in statistics?.lead_count_by_status || {}" :key="status">
                <span>{{ statusLabel(String(status)) }}</span>
                <strong>{{ count }}</strong>
                <p>线索状态分布</p>
              </article>
            </div>
            <div class="assistant-message enterprise-summary-text">
              <strong>统计摘要</strong>
              <p>{{ statistics?.summary.text || "暂无统计摘要" }}</p>
            </div>
          </template>

          <template v-if="activeTab === 'nl2sql'">
            <div class="enterprise-query-box">
              <textarea v-model="nlQuery" rows="4" />
              <button class="primary-button compact-button" :disabled="queryLoading" type="button" @click="handleNl2Sql">
                执行问数
              </button>
            </div>
            <div class="enterprise-result-box">
              <strong>查询结果</strong>
              <p v-if="!nlResult">请输入自然语言问题并执行。</p>
              <pre v-else>{{ JSON.stringify(nlResult, null, 2) }}</pre>
            </div>
          </template>

          <template v-if="activeTab === 'guide'">
            <div class="enterprise-query-box">
              <textarea v-model="guideQuestion" rows="4" />
              <button class="primary-button compact-button" :disabled="queryLoading" type="button" @click="handleGuideQuery">
                查询指引
              </button>
            </div>
            <div class="enterprise-result-box">
              <strong>{{ guideResult?.category || "入职指引" }}</strong>
              <p>{{ guideResult?.answer || guideResult?.message || "请输入制度或流程问题。" }}</p>
            </div>
          </template>
        </div>

        <aside class="enterprise-detail-panel">
          <template v-if="activeTab === 'leads' && selectedLead">
            <p class="eyebrow">线索详情</p>
            <h2>{{ selectedLead.customer_name }}</h2>
            <span :class="['status-chip', selectedLead.status]">{{ statusLabel(selectedLead.status) }}</span>
            <dl>
              <div><dt>电话</dt><dd>{{ selectedLead.phone || "-" }}</dd></div>
              <div><dt>学校</dt><dd>{{ selectedLead.school_name || "-" }}</dd></div>
              <div><dt>专业</dt><dd>{{ selectedLead.major || "-" }}</dd></div>
              <div><dt>预算</dt><dd>{{ selectedLead.budget_range || "-" }}</dd></div>
            </dl>
            <div class="reason-box">
              <strong>最近跟进</strong>
              <p>{{ selectedLead.latest_follow_up_summary || selectedLead.background_info || "暂无跟进摘要" }}</p>
            </div>
          </template>
          <template v-else-if="activeTab === 'students' && selectedStudent">
            <p class="eyebrow">学生详情</p>
            <h2>{{ selectedStudent.student_name }}</h2>
            <span class="status-chip resolved">{{ selectedStudent.status }}</span>
            <dl>
              <div><dt>电话</dt><dd>{{ selectedStudent.phone || "-" }}</dd></div>
              <div><dt>邮箱</dt><dd>{{ selectedStudent.email || "-" }}</dd></div>
              <div><dt>顾问</dt><dd>{{ selectedStudent.counselor_employee_id || "-" }}</dd></div>
              <div><dt>老师</dt><dd>{{ selectedStudent.teacher_employee_id || "-" }}</dd></div>
            </dl>
            <div class="reason-box">
              <strong>申请目标</strong>
              <p>{{ selectedStudent.target_country || "-" }} · {{ selectedStudent.target_program || "-" }}</p>
            </div>
          </template>
          <template v-else>
            <p class="eyebrow">运营侧栏</p>
            <h2>查询说明</h2>
            <div class="reason-box">
              <strong>可查询范围</strong>
              <p>客户线索、学生档案、日报、请假、反馈、申请进度、组织架构和管理统计。</p>
            </div>
          </template>
        </aside>
      </section>
    </main>
  </div>
</template>
