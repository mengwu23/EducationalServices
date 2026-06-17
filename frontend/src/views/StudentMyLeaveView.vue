<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import PaginationBar from "@/components/common/PaginationBar.vue";
import { cancelLeave, createLeave, listMyLeaves } from "@/api/studentAssistant";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { LeaveRecord } from "@/types/studentAssistant";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const statusFilter = ref("");
const leaves = ref<LeaveRecord[]>([]);
const selectedLeave = ref<LeaveRecord | null>(null);
const page = ref(1);
const pageSize = 10;
const total = ref(0);
const form = ref({
  leave_type: "personal",
  reason: "",
  start_time: "",
  end_time: "",
});

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const todayDate = computed(() => new Date().toISOString().slice(0, 10));
const endMinDate = computed(() => form.value.start_time || todayDate.value);

const statusMap: Record<string, string> = {
  pending: "待审批",
  approved: "已通过",
  rejected: "已驳回",
  cancelled: "已取消",
};

const typeMap: Record<string, string> = {
  sick: "病假",
  personal: "事假",
  other: "其他",
};

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.slice(0, 10);
}

function toLeaveDateTime(value: string, endOfDay = false): string {
  return `${value}T${endOfDay ? "23:59:59" : "00:00:00"}`;
}

function validateLeaveForm(): boolean {
  if (!form.value.start_time || !form.value.end_time) {
    message.value = "请选择请假开始日期和结束日期";
    return false;
  }
  if (form.value.start_time < todayDate.value) {
    message.value = "开始日期不能早于今天";
    return false;
  }
  if (form.value.end_time < form.value.start_time) {
    message.value = "结束日期不能早于开始日期";
    return false;
  }
  if (!form.value.reason.trim()) {
    message.value = "请填写请假原因";
    return false;
  }
  return true;
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const result = await listMyLeaves(page.value, pageSize, statusFilter.value);
    leaves.value = result.items || [];
    total.value = result.total || 0;
    selectedLeave.value = leaves.value.find((item) => item.id === selectedLeave.value?.id) || leaves.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "我的请假加载失败";
  } finally {
    loading.value = false;
  }
}

function reloadFromFirstPage() {
  page.value = 1;
  loadData();
}

function handlePageChange(nextPage: number) {
  page.value = nextPage;
  loadData();
}

async function handleCreate() {
  if (!validateLeaveForm()) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await createLeave({
      leave_type: form.value.leave_type,
      reason: form.value.reason,
      start_time: toLeaveDateTime(form.value.start_time),
      end_time: toLeaveDateTime(form.value.end_time, true),
    });
    message.value = "请假申请已提交";
    form.value.reason = "";
    form.value.start_time = "";
    form.value.end_time = "";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "请假提交失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleCancel() {
  if (!selectedLeave.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await cancelLeave(selectedLeave.value.id, "学生主动取消");
    message.value = "请假已取消";
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
    <AppSidebar active-key="student-leaves" />
    <main class="dashboard leave-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生端</p>
          <h1>我的请假</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="student-grid">
        <div class="leave-list-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">申请记录</p>
              <h2>请假列表</h2>
            </div>
            <select v-model="statusFilter" @change="reloadFromFirstPage">
              <option value="">全部状态</option>
              <option value="pending">待审批</option>
              <option value="approved">已通过</option>
              <option value="rejected">已驳回</option>
              <option value="cancelled">已取消</option>
            </select>
          </div>
          <div v-if="loading" class="empty-state">正在加载...</div>
          <table v-else class="leave-table">
            <thead>
              <tr>
                <th>单号</th>
                <th>类型</th>
                <th>开始</th>
                <th>结束</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in leaves" :key="item.id" :class="{ selected: selectedLeave?.id === item.id }" @click="selectedLeave = item">
                <td>{{ item.request_no }}</td>
                <td>{{ typeMap[item.leave_type] || item.leave_type }}</td>
                <td>{{ formatDateTime(item.start_time) }}</td>
                <td>{{ formatDateTime(item.end_time) }}</td>
                <td><span :class="['status-chip', item.status]">{{ statusMap[item.status] || item.status }}</span></td>
              </tr>
            </tbody>
          </table>
          <PaginationBar
            :page="page"
            :page-size="pageSize"
            :total="total"
            :disabled="loading"
            @change="handlePageChange"
          />
        </div>

        <aside class="leave-detail-panel">
          <p class="eyebrow">提交请假</p>
          <h2>新申请</h2>
          <label class="reject-comment">
            <span>类型</span>
            <select v-model="form.leave_type">
              <option value="personal">事假</option>
              <option value="sick">病假</option>
              <option value="other">其他</option>
            </select>
          </label>
          <label class="reject-comment">
            <span>开始时间</span>
            <input v-model="form.start_time" :min="todayDate" type="date" />
          </label>
          <label class="reject-comment">
            <span>结束时间</span>
            <input v-model="form.end_time" :min="endMinDate" type="date" />
          </label>
          <label class="reject-comment">
            <span>原因</span>
            <textarea v-model="form.reason" rows="4" />
          </label>
          <div class="action-row">
            <button class="primary-button" :disabled="actionLoading" type="button" @click="handleCreate">提交</button>
            <button class="danger-button" :disabled="!selectedLeave || selectedLeave.status !== 'pending' || actionLoading" type="button" @click="handleCancel">
              取消选中
            </button>
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>
