<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { createMyStudentFeedbackTicket, listMyStudentFeedbackTickets } from "@/api/studentFeedback";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { StudentFeedbackTicket } from "@/types/studentFeedback";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const tickets = ref<StudentFeedbackTicket[]>([]);
const selectedTicket = ref<StudentFeedbackTicket | null>(null);
const form = ref({
  ticket_type: "consult",
  title: "",
  detail: "",
  priority_level: "normal",
});

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const ticketTypeLabelMap: Record<string, string> = {
  complaint: "投诉",
  suggestion: "建议",
  consult: "咨询",
};
const statusLabelMap: Record<string, string> = {
  pending: "待处理",
  processing: "处理中",
  resolved: "已解决",
  closed: "已关闭",
};
const categoryLabelMap: Record<string, string> = {
  course: "教学课程",
  service: "服务顾问",
  visa: "签证办理",
  school: "院校申请",
  life: "生活服务",
  finance: "财务费用",
  other: "其他",
};

function ticketTypeLabel(value?: string | null): string {
  if (!value) return "-";
  return ticketTypeLabelMap[value] || value;
}

function statusLabel(value?: string | null): string {
  if (!value) return "-";
  return statusLabelMap[value] || value;
}

function categoryLabel(value?: string | null): string {
  if (!value) return "未分类";
  return categoryLabelMap[value] || value;
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const result = await listMyStudentFeedbackTickets({ page: 1, size: 20 });
    tickets.value = result.items || [];
    selectedTicket.value = tickets.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "我的反馈加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleCreate() {
  actionLoading.value = true;
  message.value = "";
  try {
    await createMyStudentFeedbackTicket({
      ticket_type: form.value.ticket_type,
      title: form.value.title,
      detail: form.value.detail,
      priority_level: form.value.priority_level,
    });
    message.value = "反馈已提交";
    form.value.title = "";
    form.value.detail = "";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "反馈提交失败";
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
    <AppSidebar active-key="student-feedback" />
    <main class="dashboard feedback-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生端</p>
          <h1>我的反馈</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>
      <p v-if="message" class="module-message">{{ message }}</p>
      <section class="student-grid">
        <div class="feedback-list-panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">反馈记录</p>
              <h2>我的工单</h2>
            </div>
          </div>
          <div v-if="loading" class="empty-state">正在加载...</div>
          <table v-else class="leave-table">
            <thead>
              <tr>
                <th>工单信息</th>
                <th>类型</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in tickets" :key="item.id" :class="{ selected: selectedTicket?.id === item.id }" @click="selectedTicket = item">
                <td>
                  <strong>{{ item.title }}</strong>
                  <span>{{ item.ticket_no }}</span>
                </td>
                <td>{{ ticketTypeLabel(item.ticket_type) }}</td>
                <td><span :class="['status-chip', item.status]">{{ statusLabel(item.status) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <aside class="leave-detail-panel">
          <p class="eyebrow">提交反馈</p>
          <h2>新工单</h2>
          <label class="reject-comment">
            <span>类型</span>
            <select v-model="form.ticket_type">
              <option value="consult">咨询</option>
              <option value="suggestion">建议</option>
              <option value="complaint">投诉</option>
            </select>
          </label>
          <label class="reject-comment">
            <span>标题</span>
            <input v-model="form.title" />
          </label>
          <label class="reject-comment">
            <span>内容</span>
            <textarea v-model="form.detail" rows="5" />
          </label>
          <button class="primary-button" :disabled="actionLoading" type="button" @click="handleCreate">提交反馈</button>
          <div class="reason-box">
            <strong>处理结果</strong>
            <p v-if="selectedTicket">分类：{{ categoryLabel(selectedTicket.category) }}</p>
            <p v-if="selectedTicket">状态：{{ statusLabel(selectedTicket.status) }}</p>
            <p v-if="selectedTicket">类型：{{ ticketTypeLabel(selectedTicket.ticket_type) }}</p>
            <p>{{ selectedTicket?.solution || selectedTicket?.content_summary || "请选择一条反馈记录查看处理结果" }}</p>
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>
