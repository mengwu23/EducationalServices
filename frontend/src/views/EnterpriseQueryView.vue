<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import PaginationBar from "@/components/common/PaginationBar.vue";
import {
  confirmEnterpriseOperation,
  executeEnterpriseOperation,
  queryNl2Sql,
  queryOnboardingGuide,
  searchLeads,
  searchStudents,
  summarizeStatistics,
  summarizeTodos,
} from "@/api/enterpriseAssistant";
import { uploadVoiceForRecognition } from "@/api/voice";
import type { VoiceRecognizeResult } from "@/types/voice";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type {
  LeadItem,
  Nl2SqlResult,
  OnboardingGuideResult,
  OperationResponse,
  StatisticsSummaryResult,
  StudentProfileItem,
  TodoSummaryResult,
} from "@/types/enterpriseAssistant";

interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string;
  readonly message: string;
}

interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognition;
    webkitSpeechRecognition?: new () => SpeechRecognition;
  }
}

const router = useRouter();
const loading = ref(false);
const queryLoading = ref(false);
const message = ref("");
const activeTab = ref<"leads" | "students" | "todos" | "statistics" | "nl2sql" | "operation" | "guide">("leads");
const leads = ref<LeadItem[]>([]);
const students = ref<StudentProfileItem[]>([]);
const leadTotal = ref(0);
const studentTotal = ref(0);
const leadPage = ref(1);
const studentPage = ref(1);
const pageSize = 10;
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
const operationQuery = ref("新增客户，王一鸣，本科大三，想去英国读硕士，预算30万，电话13700030001，来源官网咨询");
const operationResult = ref<OperationResponse | null>(null);
const rejectReason = ref("信息不完整，暂不执行。");
const dropdownOpen = ref(false);

const tabOptions = [
  { value: "leads", label: "线索", icon: "🔍", desc: "客户线索检索与筛选" },
  { value: "students", label: "学生", icon: "🎓", desc: "学生档案与申请信息" },
  { value: "todos", label: "待办", icon: "📋", desc: "请假、反馈与超时线索" },
  { value: "statistics", label: "统计", icon: "📊", desc: "运营数据汇总与摘要" },
  { value: "nl2sql", label: "问数", icon: "💬", desc: "自然语言智能问数" },
  { value: "operation", label: "办理", icon: "⚡", desc: "语音/文本输入，业务解析执行" },
  { value: "guide", label: "指引", icon: "📖", desc: "制度流程与入职问答" },
];

function selectTab(value: string) {
  activeTab.value = value as typeof activeTab.value;
  dropdownOpen.value = false;
}

function currentTabLabel(): string {
  return tabOptions.find((t) => t.value === activeTab.value)?.label || "";
}

function currentTabIcon(): string {
  return tabOptions.find((t) => t.value === activeTab.value)?.icon || "";
}

// Voice input state
const voiceMode = ref<"none" | "browser" | "upload">("none");
const isListening = ref(false);
const voiceUploadLoading = ref(false);
const selectedFileName = ref("");
const selectedFileBlob = ref<Blob | null>(null);
const audioFormat = ref("wav");
const sampleRate = ref(16000);
const isDragging = ref(false);
const recordingSeconds = ref(0);
const browserVoiceSupported = ref(false);
let recordingTimer: ReturnType<typeof setInterval> | null = null;
let recognitionInstance: SpeechRecognition | null = null;
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

const studentStatusMap: Record<string, string> = {
  active: "服务中",
  graduated: "已结课",
  inactive: "停用",
};

function statusLabel(value?: string | null): string {
  if (!value) return "-";
  return leadStatusMap[value] || value;
}

function studentStatusLabel(value?: string | null): string {
  if (!value) return "-";
  return studentStatusMap[value] || value;
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
    page: leadPage.value,
    page_size: pageSize,
  });
  leads.value = result.items || [];
  leadTotal.value = result.total;
  selectedLead.value = leads.value[0] || null;
}

async function loadStudents() {
  const result = await searchStudents({
    student_name: studentKeyword.value,
    target_country: targetCountry.value,
    page: studentPage.value,
    page_size: pageSize,
  });
  students.value = result.items || [];
  studentTotal.value = result.total;
  selectedStudent.value = students.value[0] || null;
}

function reloadCurrentListFromFirstPage() {
  if (activeTab.value === "leads") {
    leadPage.value = 1;
  }
  if (activeTab.value === "students") {
    studentPage.value = 1;
  }
  refreshCurrentTab();
}

function handleLeadPageChange(nextPage: number) {
  leadPage.value = nextPage;
  refreshCurrentTab();
}

function handleStudentPageChange(nextPage: number) {
  studentPage.value = nextPage;
  refreshCurrentTab();
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

async function handleOperationExecute() {
  if (!operationQuery.value.trim()) return;
  queryLoading.value = true;
  message.value = "";
  try {
    operationResult.value = await executeEnterpriseOperation(operationQuery.value.trim(), operationResult.value?.draft_id);
  } catch (error) {
    message.value = error instanceof Error ? error.message : "业务办理解析失败";
  } finally {
    queryLoading.value = false;
  }
}

async function handleOperationConfirm(action: "confirm" | "reject") {
  if (!operationResult.value?.draft_id) return;
  queryLoading.value = true;
  message.value = "";
  try {
    operationResult.value = await confirmEnterpriseOperation(operationResult.value.draft_id, action, rejectReason.value);
    message.value = action === "confirm" ? "业务操作已确认执行" : "业务操作已拒绝";
  } catch (error) {
    message.value = error instanceof Error ? error.message : "业务办理确认失败";
  } finally {
    queryLoading.value = false;
  }
}

// ====== Voice input helpers ======

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function startRecordingTimer() {
  recordingSeconds.value = 0;
  recordingTimer = setInterval(() => {
    recordingSeconds.value++;
  }, 1000);
}

function clearRecordingTimer() {
  if (recordingTimer) {
    clearInterval(recordingTimer);
    recordingTimer = null;
  }
}

function initRecognition(): SpeechRecognition | null {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const r = new SR();
  r.lang = "zh-CN";
  r.continuous = false;
  r.interimResults = false;
  r.onresult = (event: SpeechRecognitionEvent) => {
    const last = event.results[event.resultIndex];
    if (last && last[0]) {
      operationQuery.value = last[0].transcript;
    }
  };
  r.onerror = (event: SpeechRecognitionErrorEvent) => {
    if (event.error !== "no-speech" && event.error !== "aborted") {
      message.value = `语音识别错误：${event.message || event.error}`;
    }
    isListening.value = false;
    clearRecordingTimer();
  };
  r.onend = () => {
    isListening.value = false;
    clearRecordingTimer();
  };
  return r;
}

function startListening() {
  message.value = "";
  const rec = initRecognition();
  if (!rec) {
    message.value = "当前浏览器不支持语音识别，请使用 Chrome 或 Edge，或切换到「上传」模式。";
    return;
  }
  recognitionInstance = rec;
  try {
    rec.start();
    isListening.value = true;
    startRecordingTimer();
  } catch {
    message.value = "启动语音识别失败，请检查麦克风权限。";
  }
}

function stopListening() {
  recognitionInstance?.stop();
  isListening.value = false;
  clearRecordingTimer();
}

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    selectedFileName.value = file.name;
    selectedFileBlob.value = file;
    message.value = "";
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (ext && ["wav", "pcm", "opus", "mp3", "m4a", "webm", "aac"].includes(ext)) {
      audioFormat.value = ext === "m4a" ? "m4a" : ext;
    }
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault();
  isDragging.value = true;
}

function onDragLeave() {
  isDragging.value = false;
}

function onDrop(e: DragEvent) {
  e.preventDefault();
  isDragging.value = false;
  const file = e.dataTransfer?.files?.[0];
  if (file && file.type.startsWith("audio/")) {
    selectedFileName.value = file.name;
    selectedFileBlob.value = file;
    message.value = "";
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (ext && ["wav", "pcm", "opus", "mp3", "m4a", "webm", "aac"].includes(ext)) {
      audioFormat.value = ext === "m4a" ? "m4a" : ext;
    }
  } else if (file) {
    message.value = "请上传音频文件（wav/pcm/opus/mp3/m4a/webm/aac）";
  }
}

async function handleVoiceUpload() {
  if (!selectedFileBlob.value) {
    message.value = "请先选择音频文件";
    return;
  }
  voiceUploadLoading.value = true;
  message.value = "";
  try {
    const result = await uploadVoiceForRecognition(selectedFileBlob.value, audioFormat.value, sampleRate.value);
    operationQuery.value = result.text;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "语音识别失败";
  } finally {
    voiceUploadLoading.value = false;
  }
}

function handleLogout() {
  logout();
  router.push("/login");
}

onMounted(() => {
  loadData();
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  browserVoiceSupported.value = !!SR;
});

onUnmounted(() => {
  recognitionInstance?.abort();
  clearRecordingTimer();
});
</script>

<template>
  <div class="app-frame">
    <AppSidebar active-key="enterprise-query" />

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
          </div>
          <div class="enterprise-tabs enterprise-tabs-center">
            <div class="func-dropdown">
              <button class="func-dropdown-btn" type="button" @click="dropdownOpen = !dropdownOpen">
                <span class="func-dropdown-icon">{{ currentTabIcon() }}</span>
                <span>{{ currentTabLabel() }}</span>
                <svg class="func-dropdown-chevron" :class="{ open: dropdownOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg>
              </button>
              <div v-if="dropdownOpen" class="func-dropdown-panel" @mouseleave="dropdownOpen = false">
                <button
                  v-for="opt in tabOptions"
                  :key="opt.value"
                  :class="{ selected: activeTab === opt.value }"
                  type="button"
                  @click="selectTab(opt.value)"
                >
                  <span class="func-opt-icon">{{ opt.icon }}</span>
                  <span class="func-opt-body">
                    <strong>{{ opt.label }}</strong>
                    <span>{{ opt.desc }}</span>
                  </span>
                </button>
              </div>
            </div>
            <div v-if="dropdownOpen" class="func-dropdown-overlay" @click="dropdownOpen = false" />
          </div>

          <template v-if="activeTab === 'leads'">
            <div class="filter-row enterprise-filter">
              <input v-model="leadKeyword" placeholder="客户姓名" @keyup.enter="reloadCurrentListFromFirstPage" />
              <select v-model="leadStatus" @change="reloadCurrentListFromFirstPage">
                <option value="">全部状态</option>
                <option value="new">新增</option>
                <option value="following">跟进中</option>
                <option value="signed">已签约</option>
                <option value="lost">已流失</option>
                <option value="invalid">无效</option>
              </select>
              <input v-model="targetCountry" placeholder="目标国家" @keyup.enter="reloadCurrentListFromFirstPage" />
              <button class="ghost-button" type="button" @click="reloadCurrentListFromFirstPage">查询</button>
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
            <PaginationBar
              :page="leadPage"
              :page-size="pageSize"
              :total="leadTotal"
              :disabled="loading"
              @change="handleLeadPageChange"
            />
          </template>

          <template v-if="activeTab === 'students'">
            <div class="filter-row enterprise-filter">
              <input v-model="studentKeyword" placeholder="学生姓名" @keyup.enter="reloadCurrentListFromFirstPage" />
              <input v-model="targetCountry" placeholder="目标国家" @keyup.enter="reloadCurrentListFromFirstPage" />
              <button class="ghost-button" type="button" @click="reloadCurrentListFromFirstPage">查询</button>
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
                  <td><span class="status-chip resolved">{{ studentStatusLabel(item.status) }}</span></td>
                </tr>
              </tbody>
            </table>
            <PaginationBar
              :page="studentPage"
              :page-size="pageSize"
              :total="studentTotal"
              :disabled="loading"
              @change="handleStudentPageChange"
            />
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

          <template v-if="activeTab === 'operation'">
            <div class="voice-mode-tabs">
              <button :class="{ active: voiceMode === 'none' }" type="button" @click="voiceMode = 'none'; stopListening()">文本输入</button>
              <button :class="{ active: voiceMode === 'browser' }" type="button" @click="voiceMode = 'browser'">
                <svg class="voice-tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
                麦克风
              </button>
              <button :class="{ active: voiceMode === 'upload' }" type="button" @click="voiceMode = 'upload'; stopListening()">
                <svg class="voice-tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                上传
              </button>
            </div>

            <!-- Browser mic mode -->
            <div v-if="voiceMode === 'browser'" class="voice-mic-inline">
              <button
                class="voice-mic-btn"
                :class="{ listening: isListening }"
                type="button"
                @click="isListening ? stopListening() : startListening()"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" y1="19" x2="12" y2="22" />
                </svg>
              </button>
              <span v-if="isListening" class="voice-mic-status listening">
                <span class="voice-rec-dot" />正在聆听… {{ formatDuration(recordingSeconds) }}
              </span>
              <span v-else class="voice-mic-status">点击麦克风，说出业务内容</span>
            </div>

            <!-- Upload mode -->
            <div v-if="voiceMode === 'upload'" class="voice-upload-inline">
              <div
                class="voice-dropzone-sm"
                :class="{ dragging: isDragging }"
                @dragover="onDragOver"
                @dragleave="onDragLeave"
                @drop="onDrop"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <span>{{ selectedFileName || "拖拽音频到此处，或点击选择" }}</span>
                <input type="file" accept="audio/*" @change="onFileChange" />
              </div>
              <div class="voice-upload-opts">
                <label>格式 <select v-model="audioFormat">
                  <option value="wav">WAV</option>
                  <option value="mp3">MP3</option>
                  <option value="webm">WebM</option>
                  <option value="m4a">M4A</option>
                  <option value="aac">AAC</option>
                  <option value="opus">OPUS</option>
                  <option value="pcm">PCM</option>
                </select></label>
                <label>采样率 <select v-model="sampleRate">
                  <option :value="16000">16k</option>
                  <option :value="8000">8k</option>
                </select></label>
                <button class="primary-button compact-button" type="button" :disabled="voiceUploadLoading || !selectedFileBlob" @click="handleVoiceUpload">
                  {{ voiceUploadLoading ? "识别中…" : "开始识别" }}
                </button>
              </div>
            </div>

            <div class="enterprise-query-box">
              <textarea v-model="operationQuery" rows="4" placeholder="例如：新增客户，王一鸣，本科大三，想去英国读硕士，预算30万，电话13700030001，来源官网咨询" />
              <button class="primary-button compact-button" :disabled="queryLoading" type="button" @click="handleOperationExecute">
                解析办理
              </button>
            </div>
            <div class="enterprise-result-box">
              <strong>办理结果</strong>
              <p v-if="!operationResult">输入自然语言业务操作后，系统会返回确认卡片或追问信息。</p>
              <template v-else>
                <p>{{ operationResult.message }}</p>
                <div v-if="operationResult.confirmation_card" class="operation-card">
                  <strong>{{ operationResult.confirmation_card.title }}</strong>
                  <p>{{ operationResult.confirmation_card.summary }}</p>
                  <dl>
                    <div v-for="field in operationResult.confirmation_card.fields" :key="field.key">
                      <dt>{{ field.label }}</dt>
                      <dd>{{ field.value ?? "-" }}</dd>
                    </div>
                  </dl>
                </div>
                <div v-if="operationResult.draft_id" class="action-row">
                  <button class="primary-button" :disabled="queryLoading" type="button" @click="handleOperationConfirm('confirm')">
                    确认执行
                  </button>
                  <button class="danger-button" :disabled="queryLoading" type="button" @click="handleOperationConfirm('reject')">
                    拒绝
                  </button>
                </div>
              </template>
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
