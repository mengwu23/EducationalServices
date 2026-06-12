<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  getPendingPsychAlertCount,
  handlePsychAlert,
  listPendingPsychAlerts,
  listPsychAlertHistory,
  listPsychProfiles,
} from "@/api/studentAssistant";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { PsychAlert, PsychProfile } from "@/types/studentAssistant";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const pendingCount = ref(0);
const profiles = ref<PsychProfile[]>([]);
const pendingAlerts = ref<PsychAlert[]>([]);
const alertHistory = ref<PsychAlert[]>([]);
const selectedAlert = ref<PsychAlert | null>(null);
const activeTab = ref<"pending" | "history">("pending");
const riskFilter = ref("");
const handleResult = ref("已联系学生并安排顾问跟进，后续观察情绪变化。");

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const visibleAlerts = computed(() => (activeTab.value === "pending" ? pendingAlerts.value : alertHistory.value));
const highRiskCount = computed(() => profiles.value.filter((item) => ["high", "critical"].includes(item.risk_level)).length);
const averageScore = computed(() => {
  const scores = profiles.value.map((item) => item.emotion_score).filter((item): item is number => typeof item === "number");
  if (!scores.length) return "-";
  return Math.round(scores.reduce((sum, item) => sum + item, 0) / scores.length);
});

const riskLabelMap: Record<string, string> = {
  low: "低",
  medium: "中",
  high: "高",
  critical: "危急",
};

const statusLabelMap: Record<string, string> = {
  pending: "待处理",
  processing: "跟进中",
  resolved: "已解除",
  closed: "已关闭",
};

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

function riskLabel(value: string): string {
  return riskLabelMap[value] || value;
}

function statusLabel(value: string): string {
  return statusLabelMap[value] || value;
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const [countResult, profileResult, pendingResult, historyResult] = await Promise.all([
      getPendingPsychAlertCount(),
      listPsychProfiles(1, 8, riskFilter.value),
      listPendingPsychAlerts(1, 8),
      listPsychAlertHistory(1, 6),
    ]);
    pendingCount.value = countResult.count;
    profiles.value = profileResult.items || [];
    pendingAlerts.value = pendingResult.items || [];
    alertHistory.value = historyResult.items || [];
    selectedAlert.value = pendingAlerts.value[0] || alertHistory.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "心理预警数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleAction(action: "process" | "resolve" | "close") {
  if (!selectedAlert.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await handlePsychAlert(selectedAlert.value.id, action, handleResult.value);
    message.value = action === "process" ? "已开始跟进" : action === "resolve" ? "预警已解除" : "预警已关闭";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "预警处理失败";
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
        <a class="active">心理预警</a>
        <RouterLink to="/students/progress">申请进度</RouterLink>
        <RouterLink to="/students/feedback">反馈工单</RouterLink>
        <RouterLink to="/reports">智能报告</RouterLink>
        <RouterLink to="/customer-judgement">客户研判</RouterLink>
        <RouterLink to="/business-query">企业查询</RouterLink>
      </nav>
    </aside>

    <main class="dashboard psych-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生服务</p>
          <h1>心理预警</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="leave-summary">
        <article>
          <span>待处理预警</span>
          <strong>{{ pendingCount }}</strong>
          <p>当前需要员工跟进的心理预警</p>
        </article>
        <article>
          <span>高风险学生</span>
          <strong>{{ highRiskCount }}</strong>
          <p>高风险与危急等级画像数量</p>
        </article>
        <article>
          <span>平均情绪分</span>
          <strong>{{ averageScore }}</strong>
          <p>基于当前画像列表计算</p>
        </article>
      </section>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="psych-grid">
        <div class="profile-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">心理画像</p>
              <h2>学生风险分布</h2>
            </div>
            <select v-model="riskFilter" @change="loadData">
              <option value="">全部风险</option>
              <option value="low">低风险</option>
              <option value="medium">中风险</option>
              <option value="high">高风险</option>
              <option value="critical">危急</option>
            </select>
          </div>

          <div v-if="loading" class="empty-state">正在加载心理画像...</div>
          <div v-else class="profile-list">
            <article v-for="profile in profiles" :key="profile.id" class="profile-card">
              <div>
                <strong>{{ profile.student_name || `学生 ${profile.student_id}` }}</strong>
                <span :class="['risk-tag', riskLabel(profile.risk_level)]">{{ riskLabel(profile.risk_level) }}</span>
              </div>
              <p>{{ profile.emotion_summary || "暂无长期情绪摘要" }}</p>
              <div class="score-line">
                <span>情绪分</span>
                <strong>{{ profile.emotion_score ?? "-" }}</strong>
              </div>
            </article>
          </div>
        </div>

        <div class="alert-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">预警记录</p>
              <h2>跟进队列</h2>
            </div>
            <div class="tab-control">
              <button :class="{ active: activeTab === 'pending' }" type="button" @click="activeTab = 'pending'">
                待处理
              </button>
              <button :class="{ active: activeTab === 'history' }" type="button" @click="activeTab = 'history'">
                历史
              </button>
            </div>
          </div>

          <div v-if="loading" class="empty-state">正在加载预警记录...</div>
          <table v-else class="leave-table">
            <thead>
              <tr>
                <th>学生</th>
                <th>风险等级</th>
                <th>状态</th>
                <th>触发时间</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in visibleAlerts"
                :key="item.id"
                :class="{ selected: selectedAlert?.id === item.id }"
                @click="selectedAlert = item"
              >
                <td>
                  <strong>{{ item.student_name || `学生 ${item.student_id}` }}</strong>
                  <span>{{ item.alert_no }}</span>
                </td>
                <td><span :class="['risk-tag', riskLabel(item.risk_level)]">{{ riskLabel(item.risk_level) }}</span></td>
                <td><span :class="['status-chip', item.status]">{{ statusLabel(item.status) }}</span></td>
                <td>{{ formatDateTime(item.create_time) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <aside class="leave-detail-panel psych-detail">
          <template v-if="selectedAlert">
            <p class="eyebrow">预警详情</p>
            <h2>{{ selectedAlert.student_name || `学生 ${selectedAlert.student_id}` }}</h2>
            <div class="detail-tags">
              <span :class="['risk-tag', riskLabel(selectedAlert.risk_level)]">{{ riskLabel(selectedAlert.risk_level) }}</span>
              <span :class="['status-chip', selectedAlert.status]">{{ statusLabel(selectedAlert.status) }}</span>
            </div>

            <dl>
              <div>
                <dt>跟进老师</dt>
                <dd>{{ selectedAlert.teacher_name || "-" }}</dd>
              </div>
              <div>
                <dt>创建时间</dt>
                <dd>{{ formatDateTime(selectedAlert.create_time) }}</dd>
              </div>
              <div>
                <dt>关闭时间</dt>
                <dd>{{ formatDateTime(selectedAlert.close_time) }}</dd>
              </div>
            </dl>

            <div class="reason-box">
              <strong>触发原因</strong>
              <p>{{ selectedAlert.trigger_reason }}</p>
            </div>

            <label class="reject-comment">
              <span>处理结果</span>
              <textarea v-model="handleResult" rows="5" />
            </label>

            <div class="psych-action-row">
              <button
                class="primary-button"
                :disabled="actionLoading || selectedAlert.status !== 'pending'"
                type="button"
                @click="handleAction('process')"
              >
                开始跟进
              </button>
              <button
                class="success-button"
                :disabled="actionLoading || !['pending', 'processing'].includes(selectedAlert.status)"
                type="button"
                @click="handleAction('resolve')"
              >
                解除预警
              </button>
              <button
                class="danger-button"
                :disabled="actionLoading || selectedAlert.status === 'closed'"
                type="button"
                @click="handleAction('close')"
              >
                关闭
              </button>
            </div>
          </template>
          <div v-else class="empty-state">请选择一条预警记录</div>
        </aside>
      </section>
    </main>
  </div>
</template>
