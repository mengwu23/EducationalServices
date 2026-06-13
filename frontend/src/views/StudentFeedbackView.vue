<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import {
  assignStudentFeedbackTicket,
  classifyStudentFeedbackTicket,
  closeStudentFeedbackTicket,
  listStudentFeedbackTickets,
  notifyStudentFeedbackTicket,
  resolveStudentFeedbackTicket,
} from "@/api/studentFeedback";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { StudentFeedbackTicket } from "@/types/studentFeedback";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const keyword = ref("");
const statusFilter = ref("");
const priorityFilter = ref("");
const typeFilter = ref("");
const tickets = ref<StudentFeedbackTicket[]>([]);
const total = ref(0);
const selectedTicket = ref<StudentFeedbackTicket | null>(null);
const solutionText = ref("");
const notifyStudent = ref(true);
const satisfactionScore = ref<number | undefined>(5);

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const canHandle = computed(() => user.value?.role !== "student");

const ticketTypeLabelMap: Record<string, string> = {
  complaint: "投诉",
  suggestion: "建议",
  consult: "咨询",
};

const priorityLabelMap: Record<string, string> = {
  normal: "普通",
  urgent: "紧急",
  severe: "严重",
};

const statusLabelMap: Record<string, string> = {
  pending: "待处理",
  processing: "处理中",
  resolved: "已解决",
  closed: "已关闭",
};

const visibleTickets = computed(() => {
  const text = keyword.value.trim().toLowerCase();
  if (!text) return tickets.value;
  return tickets.value.filter((item) =>
    [item.ticket_no, item.title, item.category, item.content_summary, item.detail, item.solution]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(text)),
  );
});

const pendingCount = computed(() => tickets.value.filter((item) => item.status === "pending").length);
const processingCount = computed(() => tickets.value.filter((item) => item.status === "processing").length);
const highPriorityCount = computed(() =>
  tickets.value.filter((item) => ["urgent", "severe"].includes(item.priority_level)).length,
);
const notifiedCount = computed(() => tickets.value.filter((item) => item.is_notified === 1).length);

watch(selectedTicket, (ticket) => {
  solutionText.value = ticket?.solution || "已核实学生反馈，建议安排顾问补充说明并同步后续处理结果。";
  satisfactionScore.value = ticket?.satisfaction_score || 5;
  notifyStudent.value = true;
});

function ticketTypeLabel(value: string): string {
  return ticketTypeLabelMap[value] || value;
}

function priorityLabel(value: string): string {
  return priorityLabelMap[value] || value;
}

function statusLabel(value: string): string {
  return statusLabelMap[value] || value;
}

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const result = await listStudentFeedbackTickets({
      page: 1,
      size: 50,
      status: statusFilter.value,
      priority_level: priorityFilter.value,
      keyword: keyword.value,
    });
    let items = result.items || [];
    if (typeFilter.value) {
      items = items.filter((item) => item.ticket_type === typeFilter.value);
    }
    tickets.value = items;
    total.value = result.total;
    selectedTicket.value = tickets.value.find((item) => item.id === selectedTicket.value?.id) || tickets.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "反馈工单数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleAssignToMe() {
  if (!selectedTicket.value || !user.value?.employee_id) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await assignStudentFeedbackTicket(selectedTicket.value.id, user.value.employee_id);
    message.value = "工单已分配给当前账号";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "工单分配失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleResolve() {
  if (!selectedTicket.value || !solutionText.value.trim()) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await resolveStudentFeedbackTicket(selectedTicket.value.id, solutionText.value.trim(), notifyStudent.value);
    message.value = "工单已标记为解决";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "工单解决失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleClose() {
  if (!selectedTicket.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await closeStudentFeedbackTicket(selectedTicket.value.id, satisfactionScore.value);
    message.value = "工单已关闭";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "工单关闭失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleNotify() {
  if (!selectedTicket.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await notifyStudentFeedbackTicket(selectedTicket.value.id);
    message.value = "已通知学生处理结果";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "通知发送失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleClassify() {
  if (!selectedTicket.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await classifyStudentFeedbackTicket(selectedTicket.value.id);
    message.value = "AI 分类已完成";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "AI 分类失败";
  } finally {
    actionLoading.value = false;
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
    <AppSidebar active-key="feedback" />

    <main class="dashboard feedback-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生服务</p>
          <h1>反馈工单</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="leave-summary feedback-summary">
        <article>
          <span>工单总数</span>
          <strong>{{ total }}</strong>
          <p>当前筛选范围内的反馈记录</p>
        </article>
        <article>
          <span>待处理</span>
          <strong>{{ pendingCount }}</strong>
          <p>需要尽快分配处理人的工单</p>
        </article>
        <article>
          <span>处理中</span>
          <strong>{{ processingCount }}</strong>
          <p>已进入服务跟进流程</p>
        </article>
        <article>
          <span>高优先级</span>
          <strong>{{ highPriorityCount }}</strong>
          <p>紧急与严重工单需要优先闭环</p>
        </article>
      </section>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="feedback-workspace">
        <div class="feedback-list-panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">工单队列</p>
              <h2>投诉、建议与咨询</h2>
            </div>
            <button class="ghost-button" :disabled="loading" type="button" @click="loadData">刷新</button>
          </div>

          <div class="filter-row feedback-filter">
            <input v-model="keyword" placeholder="搜索标题、编号、分类或处理方案" @keyup.enter="loadData" />
            <select v-model="typeFilter" @change="loadData">
              <option value="">全部类型</option>
              <option value="complaint">投诉</option>
              <option value="suggestion">建议</option>
              <option value="consult">咨询</option>
            </select>
            <select v-model="priorityFilter" @change="loadData">
              <option value="">全部优先级</option>
              <option value="normal">普通</option>
              <option value="urgent">紧急</option>
              <option value="severe">严重</option>
            </select>
            <select v-model="statusFilter" @change="loadData">
              <option value="">全部状态</option>
              <option value="pending">待处理</option>
              <option value="processing">处理中</option>
              <option value="resolved">已解决</option>
              <option value="closed">已关闭</option>
            </select>
          </div>

          <div v-if="loading" class="empty-state">正在加载反馈工单...</div>
          <div v-else-if="!visibleTickets.length" class="empty-state">暂无匹配的反馈工单</div>
          <table v-else class="leave-table">
            <thead>
              <tr>
                <th>工单</th>
                <th>类型</th>
                <th>分类</th>
                <th>优先级</th>
                <th>状态</th>
                <th>更新时间</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in visibleTickets"
                :key="item.id"
                :class="{ selected: selectedTicket?.id === item.id }"
                @click="selectedTicket = item"
              >
                <td>
                  <strong>{{ item.title }}</strong>
                  <span>{{ item.ticket_no }} · 学生 {{ item.student_id }}</span>
                </td>
                <td>{{ ticketTypeLabel(item.ticket_type) }}</td>
                <td>{{ item.category || "未分类" }}</td>
                <td>
                  <span :class="['priority-chip', item.priority_level]">{{ priorityLabel(item.priority_level) }}</span>
                </td>
                <td>
                  <span :class="['status-chip', item.status]">{{ statusLabel(item.status) }}</span>
                </td>
                <td>{{ formatDateTime(item.update_time) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <aside class="leave-detail-panel feedback-detail">
          <template v-if="selectedTicket">
            <p class="eyebrow">工单详情</p>
            <h2>{{ selectedTicket.title }}</h2>
            <div class="detail-tags">
              <span :class="['priority-chip', selectedTicket.priority_level]">
                {{ priorityLabel(selectedTicket.priority_level) }}
              </span>
              <span :class="['status-chip', selectedTicket.status]">{{ statusLabel(selectedTicket.status) }}</span>
              <span class="risk-tag 中">{{ ticketTypeLabel(selectedTicket.ticket_type) }}</span>
            </div>

            <dl>
              <div>
                <dt>工单编号</dt>
                <dd>{{ selectedTicket.ticket_no }}</dd>
              </div>
              <div>
                <dt>学生 ID</dt>
                <dd>{{ selectedTicket.student_id }}</dd>
              </div>
              <div>
                <dt>处理人</dt>
                <dd>{{ selectedTicket.handler_employee_id || "-" }}</dd>
              </div>
              <div>
                <dt>已通知</dt>
                <dd>{{ selectedTicket.is_notified === 1 ? "是" : "否" }}</dd>
              </div>
              <div>
                <dt>满意度</dt>
                <dd>{{ selectedTicket.satisfaction_score || "-" }}</dd>
              </div>
              <div>
                <dt>创建时间</dt>
                <dd>{{ formatDateTime(selectedTicket.create_time) }}</dd>
              </div>
            </dl>

            <div class="reason-box">
              <strong>反馈内容</strong>
              <p>{{ selectedTicket.detail }}</p>
            </div>
            <div class="reason-box feedback-summary-box">
              <strong>AI 摘要</strong>
              <p>{{ selectedTicket.content_summary || "暂无摘要，可使用 AI 分类补全。" }}</p>
            </div>

            <div v-if="canHandle" class="feedback-actions">
              <label class="reject-comment">
                <span>处理方案</span>
                <textarea v-model="solutionText" rows="5" />
              </label>
              <label class="checkbox-line feedback-checkbox">
                <input v-model="notifyStudent" type="checkbox" />
                <span>解决时同步通知学生</span>
              </label>
              <label class="reject-comment">
                <span>关闭满意度</span>
                <select v-model.number="satisfactionScore">
                  <option :value="5">5 分</option>
                  <option :value="4">4 分</option>
                  <option :value="3">3 分</option>
                  <option :value="2">2 分</option>
                  <option :value="1">1 分</option>
                </select>
              </label>

              <div class="feedback-button-grid">
                <button
                  class="secondary-button"
                  :disabled="actionLoading || !user?.employee_id || selectedTicket.status === 'closed'"
                  type="button"
                  @click="handleAssignToMe"
                >
                  分配给我
                </button>
                <button
                  class="primary-button"
                  :disabled="actionLoading || selectedTicket.status === 'closed'"
                  type="button"
                  @click="handleResolve"
                >
                  标记解决
                </button>
                <button
                  class="success-button"
                  :disabled="actionLoading || selectedTicket.status !== 'resolved'"
                  type="button"
                  @click="handleClose"
                >
                  关闭工单
                </button>
                <button
                  class="ghost-button"
                  :disabled="actionLoading || !['resolved', 'closed'].includes(selectedTicket.status)"
                  type="button"
                  @click="handleNotify"
                >
                  通知学生
                </button>
                <button class="ghost-button" :disabled="actionLoading" type="button" @click="handleClassify">
                  AI 分类
                </button>
              </div>
            </div>
            <p v-else class="student-readonly-tip">学生账号仅查看自己的通知与处理结果，工单处理由服务团队完成。</p>
          </template>
          <div v-else class="empty-state">请选择一条反馈工单</div>
        </aside>
      </section>
    </main>
  </div>
</template>
