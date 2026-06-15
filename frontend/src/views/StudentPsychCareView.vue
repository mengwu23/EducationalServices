<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import PaginationBar from "@/components/common/PaginationBar.vue";
import {
  chatPsychAssistant,
  confirmPsychDraft,
  emotionCheckin,
  getMyPsychProfile,
  listMyPsychAlerts,
  listPsychDrafts,
  rejectPsychDraft,
} from "@/api/studentAssistant";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { PsychAlert, PsychChatResult, PsychDraft, PsychProfile } from "@/types/studentAssistant";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const profile = ref<PsychProfile | null>(null);
const alerts = ref<PsychAlert[]>([]);
const checkinText = ref("最近申请压力比较大，担心材料准备不够充分。");
const chatMessage = ref("我最近因为申请结果很焦虑，应该怎么调整？");
const chatResult = ref<PsychChatResult | null>(null);
const drafts = ref<PsychDraft[]>([]);
const rejectReason = ref("");
const rejectingDraftId = ref<number | null>(null);
const alertPage = ref(1);
const draftPage = ref(1);
const pageSize = 8;
const alertTotal = ref(0);
const draftTotal = ref(0);

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
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
const draftStatusLabelMap: Record<string, string> = {
  pending_confirm: "待确认",
  confirmed: "已确认",
  rejected: "已驳回",
};
const emotionTagLabelMap: Record<string, string> = {
  anxious: "焦虑",
  anxiety: "焦虑",
  test_anxiety: "焦虑",
  stable: "平稳",
  depressed: "低落",
  excited: "兴奋",
  lonely: "孤独",
  stressed: "压力大",
  happy: "积极",
  neutral: "平静",
  cultural_conflict: "文化冲突",
};
const summaryLabelMap: Record<string, string> = {
  "test emotion summary": "测试情绪摘要",
};

function riskLabel(value?: string | null): string {
  if (!value) return "-";
  return riskLabelMap[value] || value;
}

function statusLabel(value?: string | null): string {
  if (!value) return "-";
  return statusLabelMap[value] || value;
}

function draftStatusLabel(value?: string | null): string {
  if (!value) return "-";
  return draftStatusLabelMap[value] || value;
}

function emotionTagLabel(value?: string | null): string {
  if (!value) return "暂无情绪标签";
  const normalized = value.trim().toLowerCase().replace(/[\s-]+/g, "_");
  return emotionTagLabelMap[normalized] || emotionTagLabelMap[value] || value;
}

function summaryLabel(value?: string | null): string {
  if (!value) return "暂无画像摘要";
  const normalized = value.trim().toLowerCase().replace(/\s+/g, " ");
  return summaryLabelMap[normalized] || value;
}

function formatTime(value?: string | null): string {
  if (!value) return "-";
  return new Date(value).toLocaleString("zh-CN");
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const [profileResult, alertResult, draftResult] = await Promise.all([
      getMyPsychProfile(),
      listMyPsychAlerts(alertPage.value, pageSize),
      listPsychDrafts(draftPage.value, pageSize),
    ]);
    profile.value = profileResult;
    alerts.value = alertResult.items || [];
    drafts.value = draftResult.items || [];
    alertTotal.value = alertResult.total || 0;
    draftTotal.value = draftResult.total || 0;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "心理关怀数据加载失败";
  } finally {
    loading.value = false;
  }
}

function handleDraftPageChange(nextPage: number) {
  draftPage.value = nextPage;
  loadData();
}

function handleAlertPageChange(nextPage: number) {
  alertPage.value = nextPage;
  loadData();
}

async function handleCheckin() {
  const content = checkinText.value.trim();
  if (!content) {
    message.value = "请输入情绪打卡内容";
    return;
  }
  actionLoading.value = true;
  message.value = "";
  try {
    const result = await emotionCheckin(content);
    profile.value = result.profile;
    message.value = "情绪打卡已完成";
    alertPage.value = 1;
    const alertResult = await listMyPsychAlerts(alertPage.value, pageSize);
    alerts.value = alertResult.items || [];
    alertTotal.value = alertResult.total || 0;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "情绪打卡失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleChat() {
  const question = chatMessage.value.trim();
  if (!question) {
    message.value = "请输入需要咨询的问题";
    return;
  }
  actionLoading.value = true;
  message.value = "";
  try {
    chatResult.value = await chatPsychAssistant(question);
    if (!chatResult.value.need_confirm) {
      await loadData();
    } else {
      draftPage.value = 1;
      const draftResult = await listPsychDrafts(draftPage.value, pageSize);
      drafts.value = draftResult.items || [];
      draftTotal.value = draftResult.total || 0;
      if (chatResult.value.low_confidence) {
        message.value = chatResult.value.warning || "AI 对本次判断的置信度较低，请仔细确认后再提交";
      } else {
        message.value = "AI 回复已生成，请确认情绪分析结果是否准确";
      }
    }
  } catch (error) {
    message.value = error instanceof Error ? error.message : "心理对话失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleConfirm(draftId: number) {
  actionLoading.value = true;
  message.value = "";
  try {
    const result = await confirmPsychDraft(draftId);
    chatResult.value = result;
    message.value = "情绪记录已确认，心理画像已更新";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "确认失败";
  } finally {
    actionLoading.value = false;
  }
}

function showRejectInput(draftId: number) {
  rejectingDraftId.value = draftId;
  rejectReason.value = "";
}

function cancelReject() {
  rejectingDraftId.value = null;
  rejectReason.value = "";
}

async function handleReject(draftId: number) {
  actionLoading.value = true;
  message.value = "";
  try {
    await rejectPsychDraft(draftId, rejectReason.value);
    message.value = "情绪记录已驳回，不更新心理画像";
    rejectingDraftId.value = null;
    rejectReason.value = "";
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
    <AppSidebar active-key="student-psych-care" />
    <main class="dashboard psych-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生端</p>
          <h1>心理关怀</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>
      <p v-if="message" class="module-message">{{ message }}</p>
      <section class="student-grid">
        <div class="profile-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">心理画像</p>
              <h2>{{ emotionTagLabel(profile?.latest_emotion_tag) }}</h2>
            </div>
            <span :class="['risk-tag', profile?.risk_level || 'low']">{{ riskLabel(profile?.risk_level) }}</span>
          </div>
          <dl class="psych-meta-list">
            <div>
              <dt>情绪标签</dt>
              <dd>{{ emotionTagLabel(profile?.latest_emotion_tag) }}</dd>
            </div>
            <div>
              <dt>风险等级</dt>
              <dd>{{ riskLabel(profile?.risk_level) }}</dd>
            </div>
            <div>
              <dt>情绪分</dt>
              <dd>{{ profile?.emotion_score ?? "-" }}</dd>
            </div>
          </dl>
          <div class="reason-box">
            <strong>画像摘要</strong>
            <p>{{ summaryLabel(profile?.emotion_summary) }}</p>
          </div>
          <label class="reject-comment">
            <span>情绪打卡</span>
            <textarea v-model="checkinText" rows="5" />
          </label>
          <button class="primary-button" :disabled="actionLoading" type="button" @click="handleCheckin">提交打卡</button>
        </div>

        <aside class="leave-detail-panel">
          <p class="eyebrow">AI 对话</p>
          <h2>心理支持</h2>
          <label class="reject-comment">
            <span>问题</span>
            <textarea v-model="chatMessage" rows="5" />
          </label>
          <button class="primary-button" :disabled="actionLoading" type="button" @click="handleChat">发送</button>

          <!-- 最新对话结果 -->
          <div v-if="chatResult" class="reason-box">
            <strong>最新回复</strong>
            <p>{{ chatResult.reply }}</p>
            <dl class="psych-meta-list psych-meta-list--compact">
              <div>
                <dt>情绪标签</dt>
                <dd>{{ emotionTagLabel(chatResult.emotion_tag) }}</dd>
              </div>
              <div>
                <dt>风险等级</dt>
                <dd>{{ riskLabel(chatResult.risk_level) }}</dd>
              </div>
              <div>
                <dt>情绪分</dt>
                <dd>{{ chatResult.emotion_score }}</dd>
              </div>
              <div v-if="chatResult.confidence != null">
                <dt>置信度</dt>
                <dd>{{ (chatResult.confidence * 100).toFixed(0) }}%</dd>
              </div>
            </dl>
            <!-- 确认/驳回操作 -->
            <div v-if="chatResult.need_confirm && chatResult.draft_id" class="confirm-actions">
              <p class="confirm-hint">请确认以上 AI 情绪分析结果是否准确：</p>
              <div class="confirm-buttons">
                <button class="primary-button confirm-btn" :disabled="actionLoading" type="button" @click="handleConfirm(chatResult.draft_id)">确认并更新画像</button>
                <button class="secondary-button reject-btn" :disabled="actionLoading" type="button" @click="showRejectInput(chatResult.draft_id)">驳回</button>
              </div>
              <div v-if="rejectingDraftId === chatResult.draft_id" class="reject-input-area">
                <label class="reject-comment">
                  <span>驳回原因（可选）</span>
                  <textarea v-model="rejectReason" rows="3" placeholder="请说明为什么 AI 的判断不准确…" />
                </label>
                <div class="confirm-buttons">
                  <button class="secondary-button" :disabled="actionLoading" type="button" @click="handleReject(chatResult.draft_id!)">确认驳回</button>
                  <button class="text-button" type="button" @click="cancelReject">取消</button>
                </div>
              </div>
            </div>
            <p v-if="chatResult.low_confidence" class="module-message low-conf-warning">⚠ AI 置信度较低，请仔细确认情绪标签和风险等级是否准确</p>
            <p v-if="chatResult.alert_created">系统已自动创建心理预警。</p>
            <p v-if="chatResult.assigned_teacher">已分配老师：{{ chatResult.assigned_teacher }}</p>
            <p v-if="chatResult.degraded" class="module-message">{{ chatResult.warning }}</p>
          </div>
        </aside>
      </section>

      <!-- 对话历史 -->
      <section class="table-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">对话记录</p>
            <h2>历史对话</h2>
          </div>
        </div>
        <table v-if="drafts.length > 0">
          <thead>
            <tr>
              <th>时间</th>
              <th>学生输入</th>
              <th>情绪标签</th>
              <th>风险等级</th>
              <th>置信度</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in drafts" :key="item.id">
              <td>{{ formatTime(item.create_time) }}</td>
              <td class="text-ellipsis">{{ (item.user_message || "").substring(0, 50) }}{{ (item.user_message || "").length > 50 ? "…" : "" }}</td>
              <td>{{ emotionTagLabel(item.emotion_tag) }}</td>
              <td><span :class="['risk-tag', item.risk_level || 'low']">{{ riskLabel(item.risk_level) }}</span></td>
              <td>{{ item.confidence != null ? (item.confidence * 100).toFixed(0) + "%" : "-" }}</td>
              <td><span :class="['status-chip', item.status]">{{ draftStatusLabel(item.status) }}</span></td>
              <td>
                <div v-if="item.status === 'pending_confirm'" class="inline-actions">
                  <button class="small-primary-btn" :disabled="actionLoading" type="button" @click="handleConfirm(item.id)">确认</button>
                  <button class="small-secondary-btn" :disabled="actionLoading" type="button" @click="showRejectInput(item.id)">驳回</button>
                </div>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty-hint">暂无对话记录</p>
        <PaginationBar
          :page="draftPage"
          :page-size="pageSize"
          :total="draftTotal"
          :disabled="loading"
          @change="handleDraftPageChange"
        />
      </section>

      <!-- 驳回原因弹窗（历史记录用） -->
      <div v-if="rejectingDraftId && (!chatResult || !chatResult.draft_id || rejectingDraftId !== chatResult.draft_id)" class="reject-overlay">
        <div class="reject-dialog">
          <p class="eyebrow">驳回情绪记录</p>
          <label class="reject-comment">
            <span>驳回原因（可选）</span>
            <textarea v-model="rejectReason" rows="3" placeholder="请说明为什么 AI 的判断不准确…" />
          </label>
          <div class="confirm-buttons">
            <button class="primary-button" :disabled="actionLoading" type="button" @click="handleReject(rejectingDraftId!)">确认驳回</button>
            <button class="secondary-button" type="button" @click="cancelReject">取消</button>
          </div>
        </div>
      </div>

      <section class="table-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">预警记录</p>
            <h2>我的预警</h2>
          </div>
        </div>
        <table v-if="alerts.length > 0">
          <thead>
            <tr>
              <th>预警编号</th>
              <th>触发原因</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in alerts" :key="item.id">
              <td>{{ item.alert_no }}</td>
              <td>{{ item.trigger_reason }}</td>
              <td><span :class="['status-chip', item.status]">{{ statusLabel(item.status) }}</span></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty-hint">暂无预警记录</p>
        <PaginationBar
          :page="alertPage"
          :page-size="pageSize"
          :total="alertTotal"
          :disabled="loading"
          @change="handleAlertPageChange"
        />
      </section>
    </main>
  </div>
</template>
