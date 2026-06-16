<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import PaginationBar from "@/components/common/PaginationBar.vue";
import {
  approveLeave,
  getPendingLeaveCount,
  listApprovalHistory,
  listPendingLeaves,
  rejectLeave,
} from "@/api/studentAssistant";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { LeaveRecord } from "@/types/studentAssistant";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const pendingCount = ref(0);
const pendingLeaves = ref<LeaveRecord[]>([]);
const approvalHistory = ref<LeaveRecord[]>([]);
const selectedLeave = ref<LeaveRecord | null>(null);
const rejectComment = ref("请补充请假原因或相关证明后重新提交。");
const activeTab = ref<"pending" | "history">("pending");
const filterStudentName = ref("");
const filterLeaveType = ref("");
const filterStatus = ref("");
const pendingPage = ref(1);
const historyPage = ref(1);
const pageSize = 8;
const pendingTotal = ref(0);
const historyTotal = ref(0);

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

const visibleRows = computed(() => (activeTab.value === "pending" ? pendingLeaves.value : approvalHistory.value));

const leaveTypeMap: Record<string, string> = {
  sick: "病假",
  personal: "事假",
  other: "其他",
};

const statusMap: Record<string, string> = {
  pending: "待审批",
  approved: "已通过",
  rejected: "已驳回",
  cancelled: "已取消",
};

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

function getLeaveType(type: string): string {
  return leaveTypeMap[type] || type;
}

function getStatus(status: string): string {
  return statusMap[status] || status;
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const [countResult, pendingResult, historyResult] = await Promise.all([
      getPendingLeaveCount(),
      listPendingLeaves(pendingPage.value, pageSize, filterLeaveType.value, filterStudentName.value),
      listApprovalHistory(historyPage.value, pageSize, filterStatus.value, filterLeaveType.value, filterStudentName.value),
    ]);
    pendingCount.value = countResult.count;
    pendingLeaves.value = pendingResult.items || [];
    approvalHistory.value = historyResult.items || [];
    pendingTotal.value = pendingResult.total || 0;
    historyTotal.value = historyResult.total || 0;
    selectedLeave.value = pendingLeaves.value[0] || approvalHistory.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "请假数据加载失败";
  } finally {
    loading.value = false;
  }
}

function reloadFromFirstPage() {
  pendingPage.value = 1;
  historyPage.value = 1;
  loadData();
}

function handlePageChange(nextPage: number) {
  if (activeTab.value === "pending") {
    pendingPage.value = nextPage;
  } else {
    historyPage.value = nextPage;
  }
  loadData();
}

async function handleApprove() {
  if (!selectedLeave.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await approveLeave(selectedLeave.value.id);
    message.value = "审批通过成功";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "审批失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleReject() {
  if (!selectedLeave.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await rejectLeave(selectedLeave.value.id, rejectComment.value);
    message.value = "驳回申请成功";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "驳回失败";
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
    <AppSidebar active-key="leave-approval" />

    <main class="dashboard leave-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生服务</p>
          <h1>请假审批</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="leave-summary">
        <article>
          <span>待审批</span>
          <strong>{{ pendingCount }}</strong>
          <p>当前需要处理的请假申请</p>
        </article>
        <article>
          <span>今日建议</span>
          <strong>优先处理</strong>
          <p>临近开始时间的申请需要尽快反馈</p>
        </article>
        <article>
          <span>协同提醒</span>
          <strong>顾问同步</strong>
          <p>审批结果会影响学生服务节奏</p>
        </article>
      </section>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="leave-workspace">
        <div class="leave-list-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">审批列表</p>
              <h2>请假申请</h2>
            </div>
            <div class="tab-control">
              <button :class="{ active: activeTab === 'pending' }" type="button" @click="activeTab = 'pending'">
                待审批
              </button>
              <button :class="{ active: activeTab === 'history' }" type="button" @click="activeTab = 'history'">
                审批历史
              </button>
            </div>
          </div>

          <div class="filter-row">
            <input v-model="filterStudentName" placeholder="搜索学生姓名" @change="reloadFromFirstPage" />
            <select v-model="filterLeaveType" @change="reloadFromFirstPage">
              <option value="">全部类型</option>
              <option value="sick">病假</option>
              <option value="personal">事假</option>
              <option value="other">其他</option>
            </select>
            <select v-model="filterStatus" @change="reloadFromFirstPage">
              <option value="">全部状态</option>
              <option value="pending">待审批</option>
              <option value="approved">已通过</option>
              <option value="rejected">已驳回</option>
            </select>
          </div>

          <div v-if="loading" class="empty-state">正在加载请假数据...</div>
          <div v-else-if="!visibleRows.length" class="empty-state">暂无请假申请</div>
          <table v-else class="leave-table">
            <thead>
              <tr>
                <th>学生姓名</th>
                <th>请假类型</th>
                <th>开始时间</th>
                <th>结束时间</th>
                <th>审批状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in visibleRows"
                :key="item.id"
                :class="{ selected: selectedLeave?.id === item.id }"
                @click="selectedLeave = item"
              >
                <td>
                  <strong>{{ item.student_name || `学生 ${item.student_id}` }}</strong>
                  <span>{{ item.request_no }}</span>
                </td>
                <td>{{ getLeaveType(item.leave_type) }}</td>
                <td>{{ formatDateTime(item.start_time) }}</td>
                <td>{{ formatDateTime(item.end_time) }}</td>
                <td><span :class="['status-chip', item.status]">{{ getStatus(item.status) }}</span></td>
                <td><button class="ghost-button" type="button">查看详情</button></td>
              </tr>
            </tbody>
          </table>
          <PaginationBar
            :page="activeTab === 'pending' ? pendingPage : historyPage"
            :page-size="pageSize"
            :total="activeTab === 'pending' ? pendingTotal : historyTotal"
            :disabled="loading"
            @change="handlePageChange"
          />
        </div>

        <aside class="leave-detail-panel">
          <template v-if="selectedLeave">
            <p class="eyebrow">申请详情</p>
            <h2>{{ selectedLeave.student_name || `学生 ${selectedLeave.student_id}` }}</h2>
            <span :class="['status-chip', selectedLeave.status]">{{ getStatus(selectedLeave.status) }}</span>

            <dl>
              <div>
                <dt>请假类型</dt>
                <dd>{{ getLeaveType(selectedLeave.leave_type) }}</dd>
              </div>
              <div>
                <dt>开始时间</dt>
                <dd>{{ formatDateTime(selectedLeave.start_time) }}</dd>
              </div>
              <div>
                <dt>结束时间</dt>
                <dd>{{ formatDateTime(selectedLeave.end_time) }}</dd>
              </div>
              <div>
                <dt>审批人</dt>
                <dd>{{ selectedLeave.approver_name || "-" }}</dd>
              </div>
            </dl>

            <div class="reason-box">
              <strong>请假原因</strong>
              <p>{{ selectedLeave.reason }}</p>
            </div>

            <label class="reject-comment">
              <span>驳回说明</span>
              <textarea v-model="rejectComment" rows="4" />
            </label>

            <div class="action-row">
              <button
                class="primary-button"
                :disabled="selectedLeave.status !== 'pending' || actionLoading"
                type="button"
                @click="handleApprove"
              >
                审批通过
              </button>
              <button
                class="danger-button"
                :disabled="selectedLeave.status !== 'pending' || actionLoading"
                type="button"
                @click="handleReject"
              >
                驳回申请
              </button>
            </div>
          </template>
          <div v-else class="empty-state">请选择一条请假申请</div>
        </aside>
      </section>
    </main>
  </div>
</template>
