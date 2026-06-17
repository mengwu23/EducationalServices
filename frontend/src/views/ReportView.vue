<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import PaginationBar from "@/components/common/PaginationBar.vue";
import {
  confirmReportDraft,
  exportReport,
  generateReportDraft,
  listReportDrafts,
  listReportExports,
  listReports,
  publishReport,
  rejectReportDraft,
} from "@/api/reports";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { AiReport, ExportType, ReportDraft, ReportExportRecord, ReportType } from "@/types/reports";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const activeTab = ref<"drafts" | "reports">("drafts");
const drafts = ref<ReportDraft[]>([]);
const reports = ref<AiReport[]>([]);
const exports = ref<ReportExportRecord[]>([]);
const draftPage = ref(1);
const reportPage = ref(1);
const pageSize = 8;
const selectedDraft = ref<ReportDraft | null>(null);
const selectedReport = ref<AiReport | null>(null);
const rejectReason = ref("报告数据口径需要补充说明后重新生成。");
const reportType = ref<ReportType>("complaint_weekly");
const dateStart = ref(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10));
const dateEnd = ref(new Date().toISOString().slice(0, 10));
const departmentId = ref("");

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

const currentContent = computed(() => {
  if (activeTab.value === "drafts") return selectedDraft.value?.content_json || null;
  return selectedReport.value?.content_json || null;
});

const pendingDraftCount = computed(() => drafts.value.filter((item) => item.status === "pending_confirm").length);
const generatedCount = computed(() => drafts.value.length);
const publishedCount = computed(() => reports.value.filter((item) => item.status === "published").length);
const failedDraftCount = computed(() => drafts.value.filter((item) => item.status === "generation_failed").length);
const pagedDrafts = computed(() => drafts.value.slice((draftPage.value - 1) * pageSize, draftPage.value * pageSize));
const pagedReports = computed(() => reports.value.slice((reportPage.value - 1) * pageSize, reportPage.value * pageSize));

const reportTypeOptions: Array<{ value: ReportType; label: string }> = [
  { value: "complaint_weekly", label: "投诉周报" },
  { value: "customer_operation", label: "客户运营报告" },
  { value: "employee_daily_summary", label: "员工日报汇总" },
  { value: "employee_weekly_summary", label: "员工周报汇总" },
  { value: "student_psych_weekly", label: "学生心理周报" },
];

const statusLabelMap: Record<string, string> = {
  generating: "生成中",
  pending_confirm: "待确认",
  confirmed: "已确认",
  rejected: "已驳回",
  generation_failed: "生成失败",
  pending_second_confirm: "待二次确认",
  published: "已发布",
};

watch(selectedReport, async (report) => {
  if (!report) {
    exports.value = [];
    return;
  }
  try {
    exports.value = await listReportExports(report.id);
  } catch {
    exports.value = [];
  }
});

function reportTypeLabel(value?: string): string {
  return reportTypeOptions.find((item) => item.value === value)?.label || value || "未知报告";
}

function handleDraftPageChange(nextPage: number) {
  draftPage.value = nextPage;
}

function handleReportPageChange(nextPage: number) {
  reportPage.value = nextPage;
}

function statusLabel(value: string): string {
  return statusLabelMap[value] || value;
}

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

function contentTitle(item: ReportDraft | AiReport): string {
  return item.content_json.title || ("report_no" in item ? item.title : item.draft_no);
}

function contentSummary(item: ReportDraft | AiReport): string {
  return item.content_json.summary || item.content_json.error_message || "暂无报告摘要";
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const [draftResult, reportResult] = await Promise.all([listReportDrafts(), listReports()]);
    drafts.value = draftResult || [];
    reports.value = reportResult || [];
    selectedDraft.value = drafts.value.find((item) => item.id === selectedDraft.value?.id) || drafts.value[0] || null;
    selectedReport.value = reports.value.find((item) => item.id === selectedReport.value?.id) || reports.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "智能报告数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleGenerateDraft() {
  actionLoading.value = true;
  message.value = "";
  try {
    const payload = {
      report_type: reportType.value,
      date_start: dateStart.value,
      date_end: dateEnd.value,
      department_id: departmentId.value ? Number(departmentId.value) : null,
    };
    const draft = await generateReportDraft(payload);
    message.value = "报告草稿已生成，等待确认";
    selectedDraft.value = draft;
    activeTab.value = "drafts";
    draftPage.value = 1;
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "报告草稿生成失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleConfirmDraft() {
  if (!selectedDraft.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    const report = await confirmReportDraft(selectedDraft.value.id);
    message.value = "草稿已确认并生成正式报告";
    selectedReport.value = report;
    activeTab.value = "reports";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "草稿确认失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleRejectDraft() {
  if (!selectedDraft.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await rejectReportDraft(selectedDraft.value.id, rejectReason.value);
    message.value = "草稿已驳回";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "草稿驳回失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handlePublishReport() {
  if (!selectedReport.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await publishReport(selectedReport.value.id);
    message.value = "报告已发布";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "报告发布失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleExportReport(type: ExportType) {
  if (!selectedReport.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    const record = await exportReport(selectedReport.value.id, type);
    message.value = `报告导出成功：${record.file_name}`;
    exports.value = await listReportExports(selectedReport.value.id);
  } catch (error) {
    message.value = error instanceof Error ? error.message : "报告导出失败";
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
    <AppSidebar active-key="reports" />

    <main class="dashboard report-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">智能报告</p>
          <h1>报告生成与确认</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="leave-summary report-summary">
        <article>
          <span>草稿总数</span>
          <strong>{{ generatedCount }}</strong>
          <p>已生成或失败的报告草稿</p>
        </article>
        <article>
          <span>待确认</span>
          <strong>{{ pendingDraftCount }}</strong>
          <p>需要主管确认后转正式报告</p>
        </article>
        <article>
          <span>已发布</span>
          <strong>{{ publishedCount }}</strong>
          <p>可进行 Word 或 PDF 导出</p>
        </article>
        <article>
          <span>生成失败</span>
          <strong>{{ failedDraftCount }}</strong>
          <p>需要检查模型或源数据配置</p>
        </article>
      </section>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="report-workspace">
        <div class="report-left">
          <section class="report-generate-panel">
            <div class="section-heading">
              <div>
                <p class="eyebrow">生成入口</p>
                <h2>创建报告草稿</h2>
              </div>
              <button class="primary-button compact-button" :disabled="actionLoading" type="button" @click="handleGenerateDraft">
                生成草稿
              </button>
            </div>
            <div class="report-form-grid">
              <label>
                <span>报告类型</span>
                <select v-model="reportType">
                  <option v-for="item in reportTypeOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
                </select>
              </label>
              <label>
                <span>开始日期</span>
                <input v-model="dateStart" type="date" />
              </label>
              <label>
                <span>结束日期</span>
                <input v-model="dateEnd" type="date" />
              </label>
              <label>
                <span>部门 ID</span>
                <input v-model="departmentId" placeholder="可为空" />
              </label>
            </div>
          </section>

          <section class="report-list-panel">
            <div class="section-heading">
              <div>
                <p class="eyebrow">报告队列</p>
                <h2>草稿与正式报告</h2>
              </div>
              <div class="tab-control">
                <button :class="{ active: activeTab === 'drafts' }" type="button" @click="activeTab = 'drafts'">草稿</button>
                <button :class="{ active: activeTab === 'reports' }" type="button" @click="activeTab = 'reports'">报告</button>
              </div>
            </div>

            <div v-if="loading" class="empty-state">正在加载智能报告...</div>
            <div v-else-if="activeTab === 'drafts' && !drafts.length" class="empty-state">暂无报告草稿</div>
            <div v-else-if="activeTab === 'reports' && !reports.length" class="empty-state">暂无正式报告</div>
            <div v-else class="report-list">
              <article
                v-for="draft in pagedDrafts"
                v-show="activeTab === 'drafts'"
                :key="draft.id"
                :class="['report-row', { selected: selectedDraft?.id === draft.id }]"
                @click="selectedDraft = draft"
              >
                <div>
                  <strong>{{ contentTitle(draft) }}</strong>
                  <span>{{ draft.draft_no }} · {{ reportTypeLabel(draft.content_json.report_type) }}</span>
                </div>
                <span :class="['status-chip', draft.status]">{{ statusLabel(draft.status) }}</span>
              </article>
              <article
                v-for="report in pagedReports"
                v-show="activeTab === 'reports'"
                :key="report.id"
                :class="['report-row', { selected: selectedReport?.id === report.id }]"
                @click="selectedReport = report"
              >
                <div>
                  <strong>{{ report.title }}</strong>
                  <span>{{ report.report_no }} · {{ report.date_start }} 至 {{ report.date_end }}</span>
                </div>
                <span :class="['status-chip', report.status]">{{ statusLabel(report.status) }}</span>
              </article>
            </div>
            <PaginationBar
              v-if="activeTab === 'drafts'"
              :page="draftPage"
              :page-size="pageSize"
              :total="drafts.length"
              :disabled="loading"
              @change="handleDraftPageChange"
            />
            <PaginationBar
              v-else
              :page="reportPage"
              :page-size="pageSize"
              :total="reports.length"
              :disabled="loading"
              @change="handleReportPageChange"
            />
          </section>
        </div>

        <aside class="report-preview-panel">
          <template v-if="currentContent">
            <p class="eyebrow">报告预览</p>
            <h2>{{ currentContent.title || "未命名报告" }}</h2>
            <p class="report-summary-text">{{ currentContent.summary || currentContent.error_message || "暂无摘要" }}</p>

            <div class="report-section-list">
              <article v-for="section in currentContent.sections || []" :key="section.heading">
                <strong>{{ section.heading }}</strong>
                <p>{{ section.content }}</p>
              </article>
            </div>

            <div v-if="currentContent.risks?.length" class="report-note-box risk-note">
              <strong>风险提示</strong>
              <p v-for="risk in currentContent.risks" :key="risk">{{ risk }}</p>
            </div>
            <div v-if="currentContent.recommendations?.length" class="report-note-box">
              <strong>行动建议</strong>
              <p v-for="item in currentContent.recommendations" :key="item">{{ item }}</p>
            </div>

            <div v-if="activeTab === 'drafts' && selectedDraft" class="report-actions">
              <label class="reject-comment">
                <span>驳回原因</span>
                <textarea v-model="rejectReason" rows="3" />
              </label>
              <div class="action-row">
                <button
                  class="primary-button"
                  :disabled="actionLoading || selectedDraft.status !== 'pending_confirm'"
                  type="button"
                  @click="handleConfirmDraft"
                >
                  确认草稿
                </button>
                <button
                  class="danger-button"
                  :disabled="actionLoading || selectedDraft.status !== 'pending_confirm'"
                  type="button"
                  @click="handleRejectDraft"
                >
                  驳回草稿
                </button>
              </div>
            </div>

            <div v-if="activeTab === 'reports' && selectedReport" class="report-actions">
              <div class="report-button-grid">
                <button
                  class="primary-button"
                  :disabled="actionLoading || selectedReport.status === 'published'"
                  type="button"
                  @click="handlePublishReport"
                >
                  发布报告
                </button>
                <button
                  class="secondary-button"
                  :disabled="actionLoading || selectedReport.status !== 'published'"
                  type="button"
                  @click="handleExportReport('word')"
                >
                  导出 Word
                </button>
                <button
                  class="secondary-button"
                  :disabled="actionLoading || selectedReport.status !== 'published'"
                  type="button"
                  @click="handleExportReport('pdf')"
                >
                  导出 PDF
                </button>
              </div>
              <div class="export-list">
                <strong>导出记录</strong>
                <p v-if="!exports.length">暂无导出记录</p>
                <p v-for="item in exports" :key="item.id">{{ item.file_name }} · {{ statusLabel(item.status) }}</p>
              </div>
            </div>
          </template>
          <div v-else class="empty-state">请选择一个报告草稿或正式报告</div>
        </aside>
      </section>
    </main>
  </div>
</template>
