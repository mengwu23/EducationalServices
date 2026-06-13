<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { cancelAcademicEvent, completeAcademicEvent, createAcademicEvent, listAcademicEvents, listApproachingDeadlines } from "@/api/academicEvents";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { AcademicEvent } from "@/types/academicEvents";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const keyword = ref("");
const statusFilter = ref("active");
const events = ref<AcademicEvent[]>([]);
const approaching = ref<AcademicEvent[]>([]);
const selectedEvent = ref<AcademicEvent | null>(null);
const form = ref({
  student_id: "",
  event_type: "course_deadline",
  title: "",
  course_name: "",
  deadline_time: "",
  reminder_time: "",
  event_desc: "",
});

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const [eventResult, approachingResult] = await Promise.all([
      listAcademicEvents({ keyword: keyword.value, status: statusFilter.value, page: 1, size: 20 }),
      listApproachingDeadlines(14),
    ]);
    events.value = eventResult.items || [];
    approaching.value = approachingResult.items || [];
    selectedEvent.value = events.value.find((item) => item.id === selectedEvent.value?.id) || events.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "学业事件加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleCreate() {
  actionLoading.value = true;
  message.value = "";
  try {
    await createAcademicEvent({
      student_id: form.value.student_id ? Number(form.value.student_id) : null,
      event_type: form.value.event_type,
      title: form.value.title,
      course_name: form.value.course_name || null,
      deadline_time: form.value.deadline_time,
      reminder_time: form.value.reminder_time || null,
      event_desc: form.value.event_desc || null,
      status: "active",
    });
    message.value = "学业事件已创建";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "学业事件创建失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleComplete() {
  if (!selectedEvent.value) return;
  actionLoading.value = true;
  try {
    await completeAcademicEvent(selectedEvent.value.id);
    message.value = "学业事件已完成";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "完成失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleCancel() {
  if (!selectedEvent.value) return;
  actionLoading.value = true;
  try {
    await cancelAcademicEvent(selectedEvent.value.id);
    message.value = "学业事件已取消";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "取消失败";
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
    <AppSidebar active-key="academic-events" />
    <main class="dashboard">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生服务</p>
          <h1>学业事件</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>
      <section class="leave-summary progress-summary">
        <article>
          <span>事件总数</span>
          <strong>{{ events.length }}</strong>
          <p>当前筛选范围内的学业节点</p>
        </article>
        <article>
          <span>临期事件</span>
          <strong>{{ approaching.length }}</strong>
          <p>未来 14 天内需要提醒</p>
        </article>
        <article>
          <span>选中状态</span>
          <strong>{{ selectedEvent?.status || "-" }}</strong>
          <p>可完成或取消当前事件</p>
        </article>
      </section>
      <p v-if="message" class="module-message">{{ message }}</p>
      <section class="student-grid">
        <div class="leave-list-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">事件列表</p>
              <h2>考试与 Deadline</h2>
            </div>
            <button class="ghost-button" type="button" @click="loadData">刷新</button>
          </div>
          <div class="filter-row">
            <input v-model="keyword" placeholder="搜索标题或课程" @keyup.enter="loadData" />
            <select v-model="statusFilter" @change="loadData">
              <option value="">全部状态</option>
              <option value="active">进行中</option>
              <option value="completed">已完成</option>
              <option value="cancelled">已取消</option>
            </select>
          </div>
          <div v-if="loading" class="empty-state">正在加载...</div>
          <table v-else class="leave-table">
            <tbody>
              <tr v-for="item in events" :key="item.id" :class="{ selected: selectedEvent?.id === item.id }" @click="selectedEvent = item">
                <td>
                  <strong>{{ item.title }}</strong>
                  <span>{{ item.course_name || item.event_type }}</span>
                </td>
                <td>{{ formatDateTime(item.deadline_time) }}</td>
                <td><span :class="['status-chip', item.status]">{{ item.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <aside class="leave-detail-panel">
          <p class="eyebrow">新建事件</p>
          <h2>学业提醒</h2>
          <label class="reject-comment"><span>学生 ID</span><input v-model="form.student_id" /></label>
          <label class="reject-comment"><span>标题</span><input v-model="form.title" /></label>
          <label class="reject-comment"><span>课程</span><input v-model="form.course_name" /></label>
          <label class="reject-comment"><span>截止时间</span><input v-model="form.deadline_time" type="datetime-local" /></label>
          <label class="reject-comment"><span>提醒时间</span><input v-model="form.reminder_time" type="datetime-local" /></label>
          <label class="reject-comment"><span>说明</span><textarea v-model="form.event_desc" rows="3" /></label>
          <button class="primary-button" :disabled="actionLoading" type="button" @click="handleCreate">创建事件</button>
          <div class="action-row">
            <button class="success-button" :disabled="actionLoading || !selectedEvent" type="button" @click="handleComplete">完成</button>
            <button class="danger-button" :disabled="actionLoading || !selectedEvent" type="button" @click="handleCancel">取消</button>
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>
