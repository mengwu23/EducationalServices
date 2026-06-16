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
const operationQueries = ref<Record<string, string>>({});
const operationResults = ref<Record<string, OperationResponse | null>>({});
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

interface OpFunction {
  value: string;
  label: string;
  icon: string;
  voice: boolean;
  example: string;
  required: string;
  placeholder: string;
}

const operationFunctions: OpFunction[] = [
  {
    value: "create_lead",
    label: "意向客户录入",
    icon: "👤",
    voice: true,
    example: "新增客户，王一鸣，手机13812345678，本科大三，计算机科学，意向英国硕士，预算30万，来源官网咨询，微信wx_wang01",
    required: "客户姓名、手机号（必填）\n选填：微信号、邮箱、来源渠道、学历、学校、专业、年级、意向国家、意向项目、预算",
    placeholder: "描述客户信息，姓名和手机号为必填…",
  },
  {
    value: "update_lead_status",
    label: "客户状态更新",
    icon: "🔄",
    voice: true,
    example: "把王一鸣改为已签约，最近跟进：家长确认意向，下周签约",
    required: "客户姓名、目标状态（必填）\n可选状态：new 新增 / following 跟进中 / signed 已签约 / lost 已流失 / invalid 无效\n改为 lost 时需补充流失原因",
    placeholder: "如：把王一鸣改为已签约、把李思琪改为已流失，原因预算不足…",
  },
  {
    value: "submit_daily_report",
    label: "口述日报提交",
    icon: "📝",
    voice: true,
    example: "日报：今天跟进了5个客户，王一鸣已签约，处理了王璐的投诉。风险是李思琪转化慢需重点跟进。明日计划推进张明的申请材料。",
    required: "日报内容、关键进展、风险问题、明日计划（均为必填）",
    placeholder: "口述今日工作内容、进展、风险和明日计划…",
  },
  {
    value: "enter_student_score",
    label: "学生成绩录入",
    icon: "📊",
    voice: true,
    example: "给张明录入成绩，科目雅思听力，分数7.5，考试类型模考，学期2026春季，考试日期2026-06-10，备注表现稳定",
    required: "学生姓名、课程名称、成绩分数、考试类型、学期、考试日期、备注（均为必填）\n支持一条指令录入多科：数学90分，英语85分",
    placeholder: "如：给张明录入雅思听力7.5分，学期2026春季…",
  },
  {
    value: "approve_leave",
    label: "请假审批",
    icon: "✅",
    voice: true,
    example: "同意周琪的请假，审批意见：情况属实，批准",
    required: "学生姓名、审批操作（必填：同意/驳回）\n选填：审批意见、请假类型",
    placeholder: "如：同意周琪的请假、驳回孙悦的请假，理由不符规定…",
  },
  {
    value: "handle_complaint",
    label: "投诉反馈处理",
    icon: "🔧",
    voice: true,
    example: "将王璐的投诉改为处理中，处理方案是已联系学生了解情况并发送材料清单",
    required: "学生姓名、操作动作（必填）\n可选操作：处理中 / 已解决 / 关闭\n选填：处理方案、内容摘要",
    placeholder: "如：将王璐的投诉改为处理中，处理方案是…",
  },
];

const operationSubTab = ref(operationFunctions[0].value);
const currentOpFunc = computed(() => operationFunctions.find((f) => f.value === operationSubTab.value)!);

const operationQuery = computed({
  get: () => operationQueries.value[operationSubTab.value] || "",
  set: (val: string) => { operationQueries.value[operationSubTab.value] = val; },
});

const operationResult = computed({
  get: () => operationResults.value[operationSubTab.value] || null,
  set: (val: OperationResponse | null) => { operationResults.value[operationSubTab.value] = val; },
});

function selectOpFunc(value: string) {
  operationSubTab.value = value;
  operationResult.value = null;
  voiceMode.value = "none";
  stopListening();
}
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
const nlColumns = computed(() => nlResult.value?.columns || []);
const nlRows = computed(() => nlResult.value?.rows || []);

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

const nlColumnLabelMap: Record<string, string> = {
  id: "ID",
  user_id: "用户ID",
  student_id: "学生ID",
  student_no: "学生编号",
  student_name: "学生姓名",
  employee_id: "员工ID",
  employee_no: "员工编号",
  employee_name: "员工姓名",
  department_id: "部门ID",
  department_name: "部门名称",
  lead_id: "线索ID",
  lead_no: "线索编号",
  customer_name: "客户姓名",
  phone: "手机号",
  email: "邮箱",
  source_channel: "来源渠道",
  school_name: "学校名称",
  major: "专业",
  current_school: "当前学校",
  current_grade: "当前年级",
  target_country: "目标国家",
  target_program: "目标项目",
  budget_range: "预算区间",
  owner_employee_id: "负责员工ID",
  counselor_employee_id: "顾问员工ID",
  teacher_employee_id: "老师员工ID",
  status: "状态",
  report_status: "日报状态",
  create_time: "创建时间",
  update_time: "更新时间",
  course_name: "课程名称",
  score: "成绩",
  avg_score: "平均成绩",
  exam_type: "考试类型",
  semester: "学期",
  exam_date: "考试日期",
  leave_type: "请假类型",
  reason: "请假原因",
  start_time: "开始时间",
  end_time: "结束时间",
  ticket_no: "工单编号",
  ticket_type: "工单类型",
  category: "分类",
  title: "标题",
  priority_level: "优先级",
  handler_employee_id: "处理员工ID",
  progress_stage: "进度阶段",
  progress_status: "进度状态",
  progress_desc: "进度说明",
  program_name: "申请项目",
  count: "数量",
  total: "总数",
  total_count: "总数",
  lead_count: "线索数量",
  student_count: "学生数量",
  employee_count: "员工数量",
  report_count: "日报数量",
  ticket_count: "工单数量",
  leave_count: "请假数量",
  progress_count: "进度数量",
};

function statusLabel(value?: string | null): string {
  if (!value) return "-";
  return leadStatusMap[value] || value;
}

function studentStatusLabel(value?: string | null): string {
  if (!value) return "-";
  return studentStatusMap[value] || value;
}

function nlCellValue(row: Record<string, unknown> | unknown[], column: string, index: number): string {
  const value = Array.isArray(row) ? row[index] : row[column];
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function nlColumnLabel(column: string): string {
  const key = column.includes(".") ? column.split(".").pop() || column : column;
  const normalized = key.trim().replace(/`/g, "").toLowerCase();
  if (nlColumnLabelMap[normalized]) return nlColumnLabelMap[normalized];
  if (/^count\(/i.test(normalized) || normalized.includes("count")) return "数量";
  if (/^avg\(/i.test(normalized) || normalized.includes("avg")) return "平均值";
  if (/^sum\(/i.test(normalized) || normalized.includes("sum")) return "合计";
  if (/^max\(/i.test(normalized) || normalized.includes("max")) return "最大值";
  if (/^min\(/i.test(normalized) || normalized.includes("min")) return "最小值";
  return column;
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
      const prev = operationQuery.value.trimEnd();
      operationQuery.value = prev ? `${prev}\n${last[0].transcript}` : last[0].transcript;
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
    const prev = operationQuery.value.trimEnd();
    operationQuery.value = prev ? `${prev}\n${result.text}` : result.text;
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
              <template v-else>
                <div class="nl-sql-block">
                  <span>SQL 语句</span>
                  <pre>{{ nlResult.sql || "未返回 SQL" }}</pre>
                </div>
                <div v-if="nlColumns.length && nlRows.length" class="nl-table-wrap">
                  <table class="nl-result-table">
                    <thead>
                      <tr>
                        <th v-for="column in nlColumns" :key="column">{{ nlColumnLabel(column) }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in nlRows" :key="rowIndex">
                        <td v-for="(column, columnIndex) in nlColumns" :key="column">
                          {{ nlCellValue(row, column, columnIndex) }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-else>查询成功，暂无数据。</p>
              </template>
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
            <!-- 6-function sub-tabs -->
            <div class="op-func-tabs">
              <button
                v-for="func in operationFunctions"
                :key="func.value"
                :class="{ active: operationSubTab === func.value }"
                type="button"
                @click="selectOpFunc(func.value)"
              >
                <span class="op-func-tab-icon">{{ func.icon }}</span>
                <span>{{ func.label }}</span>
              </button>
            </div>

            <!-- Function guide card -->
            <div class="op-func-card">
              <span class="op-func-icon">{{ currentOpFunc.icon }}</span>
              <div>
                <strong>{{ currentOpFunc.label }}</strong>
                <p class="op-func-example">示例：{{ currentOpFunc.example }}</p>
                <p class="op-func-required">必填：{{ currentOpFunc.required }}</p>
              </div>
            </div>

            <!-- Voice input (only for voice-supported functions) -->
            <template v-if="currentOpFunc.voice">
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
                <span v-if="isListening" class="voice-mic-status listening"><span class="voice-rec-dot" />正在聆听… {{ formatDuration(recordingSeconds) }}</span>
                <span v-else class="voice-mic-status">点击麦克风说话，结果自动填入文本框</span>
              </div>

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
                    <option value="wav">WAV</option><option value="mp3">MP3</option><option value="webm">WebM</option>
                    <option value="m4a">M4A</option><option value="aac">AAC</option><option value="opus">OPUS</option><option value="pcm">PCM</option>
                  </select></label>
                  <label>采样率 <select v-model="sampleRate"><option :value="16000">16k</option><option :value="8000">8k</option></select></label>
                  <button class="primary-button compact-button" type="button" :disabled="voiceUploadLoading || !selectedFileBlob" @click="handleVoiceUpload">
                    {{ voiceUploadLoading ? "识别中…" : "开始识别" }}
                  </button>
                </div>
              </div>
            </template>

            <div class="enterprise-query-box">
              <textarea v-model="operationQuery" rows="4" :placeholder="currentOpFunc.placeholder" />
              <div class="enterprise-query-actions">
                <button class="ghost-button" type="button" @click="operationQuery = ''">清空</button>
                <button class="primary-button compact-button" :disabled="queryLoading" type="button" @click="handleOperationExecute">
                  解析办理
                </button>
              </div>
            </div>
            <div class="enterprise-result-box">
              <strong>办理结果</strong>
              <p v-if="!operationResult">输入自然语言业务操作后，系统会返回确认卡片或追问信息。</p>
              <template v-else>
                <p :class="operationResult.status === 'failed' ? 'op-result-error' : 'op-result-msg'">{{ operationResult.message }}</p>

                <!-- missing fields -->
                <div v-if="operationResult.missing_fields?.length" class="op-missing-card">
                  <strong>⚠️ 请补充以下信息</strong>
                  <ul>
                    <li v-for="f in operationResult.missing_fields" :key="f.key">
                      <span class="op-missing-label">{{ f.label }}</span>
                      <span class="op-missing-question">{{ f.question }}</span>
                    </li>
                  </ul>
                  <p class="op-hint">请在文本框中补充缺失信息后，再次点击「解析办理」</p>
                </div>

                <!-- candidate selection -->
                <div v-if="operationResult.candidates?.length" class="op-candidate-card">
                  <strong>{{ operationResult.question || "请选择" }}</strong>
                  <ul>
                    <li v-for="c in operationResult.candidates" :key="c.id">
                      <button type="button" @click="operationQuery = `第${operationResult.candidates?.indexOf(c) + 1}个`; handleOperationExecute()">
                        {{ c.label }}
                      </button>
                    </li>
                  </ul>
                </div>

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
                <div v-if="operationResult.draft_id && (operationResult.status === 'pending_confirm' || operationResult.status === 'missing_fields')" class="action-row">
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
            <span class="status-chip resolved">{{ studentStatusLabel(selectedStudent.status) }}</span>
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
