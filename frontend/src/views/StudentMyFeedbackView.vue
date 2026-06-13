<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { createStudentFeedbackTicket, listStudentFeedbackTickets } from "@/api/studentFeedback";
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
const studentId = computed(() => user.value?.student_id || 0);

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const result = await listStudentFeedbackTickets({ student_id: studentId.value, page: 1, size: 20 });
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
    await createStudentFeedbackTicket({
      student_id: studentId.value,
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
            <tbody>
              <tr v-for="item in tickets" :key="item.id" :class="{ selected: selectedTicket?.id === item.id }" @click="selectedTicket = item">
                <td>
                  <strong>{{ item.title }}</strong>
                  <span>{{ item.ticket_no }}</span>
                </td>
                <td>{{ item.ticket_type }}</td>
                <td><span :class="['status-chip', item.status]">{{ item.status }}</span></td>
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
          <button class="primary-button" :disabled="actionLoading || !studentId" type="button" @click="handleCreate">提交反馈</button>
          <div class="reason-box">
            <strong>处理结果</strong>
            <p>{{ selectedTicket?.solution || selectedTicket?.content_summary || "请选择一条反馈记录查看处理结果" }}</p>
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>
