<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { chatPsychAssistant, emotionCheckin, getMyPsychProfile, listMyPsychAlerts } from "@/api/studentAssistant";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { PsychAlert, PsychChatResult, PsychProfile } from "@/types/studentAssistant";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const profile = ref<PsychProfile | null>(null);
const alerts = ref<PsychAlert[]>([]);
const checkinText = ref("最近申请压力比较大，担心材料准备不够充分。");
const chatMessage = ref("我最近因为申请结果很焦虑，应该怎么调整？");
const chatResult = ref<PsychChatResult | null>(null);

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
const emotionTagLabelMap: Record<string, string> = {
  anxious: "焦虑",
  stable: "平稳",
  depressed: "低落",
  excited: "兴奋",
  lonely: "孤独",
  stressed: "压力大",
  happy: "积极",
  neutral: "平静",
  cultural_conflict: "文化冲突",
};

function riskLabel(value?: string | null): string {
  if (!value) return "-";
  return riskLabelMap[value] || value;
}

function statusLabel(value?: string | null): string {
  if (!value) return "-";
  return statusLabelMap[value] || value;
}

function emotionTagLabel(value?: string | null): string {
  if (!value) return "暂无情绪标签";
  return emotionTagLabelMap[value] || value;
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const [profileResult, alertResult] = await Promise.all([getMyPsychProfile(), listMyPsychAlerts(1, 8)]);
    profile.value = profileResult;
    alerts.value = alertResult.items || [];
  } catch (error) {
    message.value = error instanceof Error ? error.message : "心理关怀数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleCheckin() {
  actionLoading.value = true;
  message.value = "";
  try {
    await emotionCheckin(checkinText.value);
    message.value = "情绪打卡已完成";
    await loadData();
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
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "心理对话失败";
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
            <p>{{ profile?.emotion_summary || "暂无画像摘要" }}</p>
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
          <div class="reason-box">
            <strong>回复</strong>
            <template v-if="chatResult">
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
              </dl>
              <p v-if="chatResult.alert_created">系统已自动创建心理预警。</p>
              <p v-if="chatResult.assigned_teacher">已分配老师：{{ chatResult.assigned_teacher }}</p>
              <p v-if="chatResult.degraded" class="module-message">{{ chatResult.warning }}</p>
            </template>
            <pre v-else>暂无回复</pre>
          </div>
        </aside>
      </section>
      <section class="table-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">预警记录</p>
            <h2>我的预警</h2>
          </div>
        </div>
        <table>
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
      </section>
    </main>
  </div>
</template>
