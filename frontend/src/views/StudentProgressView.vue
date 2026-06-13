<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import {
  getApplicationProgressStages,
  getMyApplicationTimeline,
  listApplicationProgress,
  listMyApplicationProgress,
  updateApplicationProgress,
} from "@/api/applicationProgress";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { ProgressRecord, ProgressStageReference, ProgressTimelineItem } from "@/types/applicationProgress";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const keyword = ref("");
const stageFilter = ref("");
const statusFilter = ref("");
const records = ref<ProgressRecord[]>([]);
const total = ref(0);
const timeline = ref<ProgressTimelineItem[]>([]);
const timelineSummary = ref("");
const selectedRecord = ref<ProgressRecord | null>(null);
const nextStatus = ref("");
const progressNote = ref("");
const reference = ref<ProgressStageReference>({
  stages: {
    essay: "文书审核",
    school_apply: "院校申请",
    visa: "签证办理",
    offer: "录取通知",
    other: "其他",
  },
  statuses: {
    pending: "待开始",
    processing: "处理中",
    completed: "已完成",
    blocked: "受阻",
  },
});

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const isStudent = computed(() => user.value?.role === "student");
const canEdit = computed(() => !isStudent.value);

const filteredRecords = computed(() => {
  const text = keyword.value.trim().toLowerCase();
  if (!text) return records.value;
  return records.value.filter((item) =>
    [
      item.student_name,
      item.school_name,
      item.program_name,
      item.target_country,
      item.progress_desc,
      item.handler_name,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(text)),
  );
});

const pendingCount = computed(() => records.value.filter((item) => item.progress_status === "pending").length);
const processingCount = computed(() => records.value.filter((item) => item.progress_status === "processing").length);
const blockedCount = computed(() => records.value.filter((item) => item.progress_status === "blocked").length);
const completedRate = computed(() => {
  if (!records.value.length) return "0%";
  const completed = records.value.filter((item) => item.progress_status === "completed").length;
  return `${Math.round((completed / records.value.length) * 100)}%`;
});

const timelineItems = computed(() => {
  if (timeline.value.length) return timeline.value;
  const latestByStage = new Map<string, ProgressRecord>();
  records.value.forEach((record) => {
    const current = latestByStage.get(record.progress_stage);
    if (!current || record.update_time > current.update_time) {
      latestByStage.set(record.progress_stage, record);
    }
  });
  return Array.from(latestByStage.values()).map((record) => ({
    id: record.id,
    stage: record.progress_stage,
    stage_label: stageLabel(record.progress_stage),
    status: record.progress_status,
    status_label: statusLabel(record.progress_status),
    desc: record.progress_desc,
    handler_name: record.handler_name,
    school_name: record.school_name,
    expected_finish_time: record.expected_finish_time,
    update_time: record.update_time,
  }));
});

const stageOptions = computed(() => Object.entries(reference.value.stages));
const statusOptions = computed(() => Object.entries(reference.value.statuses));

watch(selectedRecord, (record) => {
  nextStatus.value = record?.progress_status || "";
  progressNote.value = record?.progress_desc || "";
});

function stageLabel(value: string): string {
  return reference.value.stages[value] || value;
}

function statusLabel(value: string): string {
  return reference.value.statuses[value] || value;
}

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

function currentStudentUserId(): number {
  return user.value?.id || 0;
}

async function loadReference() {
  try {
    reference.value = await getApplicationProgressStages();
  } catch {
    // 保留本地默认阶段文案，避免参考接口异常影响主流程。
  }
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    await loadReference();
    const params = {
      page: 1,
      page_size: 50,
      progress_stage: stageFilter.value,
      progress_status: statusFilter.value,
    };

    if (isStudent.value) {
      const studentUserId = currentStudentUserId();
      const [listResult, timelineResult] = await Promise.all([
        listMyApplicationProgress({ ...params, student_user_id: studentUserId }),
        getMyApplicationTimeline(studentUserId),
      ]);
      records.value = listResult.items || [];
      total.value = listResult.total;
      timeline.value = timelineResult.stages || [];
      timelineSummary.value = timelineResult.summary;
    } else {
      const listResult = await listApplicationProgress(params);
      records.value = listResult.items || [];
      total.value = listResult.total;
      timeline.value = [];
      timelineSummary.value = "按当前列表自动汇总各阶段最新进度";
    }

    selectedRecord.value = records.value.find((item) => item.id === selectedRecord.value?.id) || records.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "申请进度数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleUpdateStatus() {
  if (!selectedRecord.value || !nextStatus.value) return;
  actionLoading.value = true;
  message.value = "";
  try {
    await updateApplicationProgress(selectedRecord.value.id, {
      progress_status: nextStatus.value,
      progress_desc: progressNote.value,
    });
    message.value = "申请进度已更新";
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "申请进度更新失败";
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
    <AppSidebar active-key="application-progress" />

    <main class="dashboard progress-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生服务</p>
          <h1>申请进度追踪</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="leave-summary progress-summary">
        <article>
          <span>进度记录</span>
          <strong>{{ total }}</strong>
          <p>当前筛选范围内的申请服务节点</p>
        </article>
        <article>
          <span>推进中</span>
          <strong>{{ processingCount }}</strong>
          <p>正在由顾问或文案老师处理</p>
        </article>
        <article>
          <span>完成率</span>
          <strong>{{ completedRate }}</strong>
          <p>基于当前列表的已完成比例</p>
        </article>
        <article>
          <span>受阻提醒</span>
          <strong>{{ blockedCount }}</strong>
          <p>需要优先协调材料或院校反馈</p>
        </article>
      </section>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="progress-workspace">
        <div class="progress-main">
          <div class="section-heading">
            <div>
              <p class="eyebrow">申请管线</p>
              <h2>阶段时间线</h2>
            </div>
            <span>{{ timelineSummary }}</span>
          </div>

          <div v-if="loading" class="empty-state">正在加载申请进度...</div>
          <div v-else-if="!timelineItems.length" class="empty-state">暂无申请进度时间线</div>
          <div v-else class="progress-timeline">
            <article
              v-for="item in timelineItems"
              :key="`${item.stage}-${item.id}`"
              :class="['progress-step', item.status]"
            >
              <span class="step-dot"></span>
              <div>
                <strong>{{ item.stage_label }}</strong>
                <p>{{ item.desc || item.school_name || "暂无进度说明" }}</p>
              </div>
              <em>{{ item.status_label }}</em>
            </article>
          </div>

          <div class="progress-list-panel">
            <div class="section-heading">
              <div>
                <p class="eyebrow">进度列表</p>
                <h2>服务节点</h2>
              </div>
              <button class="ghost-button" :disabled="loading" type="button" @click="loadData">刷新</button>
            </div>

            <div class="filter-row progress-filter">
              <input v-model="keyword" placeholder="搜索学生、院校、项目或说明" />
              <select v-model="stageFilter" @change="loadData">
                <option value="">全部阶段</option>
                <option v-for="[value, label] in stageOptions" :key="value" :value="value">{{ label }}</option>
              </select>
              <select v-model="statusFilter" @change="loadData">
                <option value="">全部状态</option>
                <option v-for="[value, label] in statusOptions" :key="value" :value="value">{{ label }}</option>
              </select>
            </div>

            <div v-if="loading" class="empty-state">正在加载申请记录...</div>
            <div v-else-if="!filteredRecords.length" class="empty-state">暂无匹配的申请进度</div>
            <table v-else class="leave-table">
              <thead>
                <tr>
                  <th>学生</th>
                  <th>阶段</th>
                  <th>院校/项目</th>
                  <th>负责人</th>
                  <th>状态</th>
                  <th>更新时间</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in filteredRecords"
                  :key="item.id"
                  :class="{ selected: selectedRecord?.id === item.id }"
                  @click="selectedRecord = item"
                >
                  <td>
                    <strong>{{ item.student_name || `学生 ${item.student_id}` }}</strong>
                    <span>{{ item.target_country || "目标国家未填" }}</span>
                  </td>
                  <td>{{ item.progress_stage_label || stageLabel(item.progress_stage) }}</td>
                  <td>
                    <strong>{{ item.school_name || "院校未填" }}</strong>
                    <span>{{ item.program_name || "项目未填" }}</span>
                  </td>
                  <td>{{ item.handler_name || "-" }}</td>
                  <td>
                    <span :class="['status-chip', item.progress_status]">
                      {{ item.progress_status_label || statusLabel(item.progress_status) }}
                    </span>
                  </td>
                  <td>{{ formatDateTime(item.update_time) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <aside class="leave-detail-panel progress-detail">
          <template v-if="selectedRecord">
            <p class="eyebrow">节点详情</p>
            <h2>{{ selectedRecord.school_name || stageLabel(selectedRecord.progress_stage) }}</h2>
            <div class="detail-tags">
              <span :class="['status-chip', selectedRecord.progress_status]">
                {{ selectedRecord.progress_status_label || statusLabel(selectedRecord.progress_status) }}
              </span>
              <span class="risk-tag 中">{{ selectedRecord.progress_stage_label || stageLabel(selectedRecord.progress_stage) }}</span>
            </div>

            <dl>
              <div>
                <dt>学生姓名</dt>
                <dd>{{ selectedRecord.student_name || `学生 ${selectedRecord.student_id}` }}</dd>
              </div>
              <div>
                <dt>目标国家</dt>
                <dd>{{ selectedRecord.target_country || "-" }}</dd>
              </div>
              <div>
                <dt>申请项目</dt>
                <dd>{{ selectedRecord.program_name || "-" }}</dd>
              </div>
              <div>
                <dt>负责人</dt>
                <dd>{{ selectedRecord.handler_name || "-" }}</dd>
              </div>
              <div>
                <dt>预计完成</dt>
                <dd>{{ formatDateTime(selectedRecord.expected_finish_time) }}</dd>
              </div>
              <div>
                <dt>最近更新</dt>
                <dd>{{ formatDateTime(selectedRecord.update_time) }}</dd>
              </div>
            </dl>

            <div class="reason-box">
              <strong>进度说明</strong>
              <p>{{ selectedRecord.progress_desc || "暂无进度说明" }}</p>
            </div>

            <div v-if="canEdit" class="progress-edit">
              <label class="reject-comment">
                <span>调整状态</span>
                <select v-model="nextStatus">
                  <option v-for="[value, label] in statusOptions" :key="value" :value="value">{{ label }}</option>
                </select>
              </label>
              <label class="reject-comment">
                <span>更新说明</span>
                <textarea v-model="progressNote" rows="5" />
              </label>
              <button class="primary-button" :disabled="actionLoading" type="button" @click="handleUpdateStatus">
                保存进度
              </button>
            </div>
            <p v-else class="student-readonly-tip">学生账号仅查看本人申请进度，如需调整请联系服务顾问。</p>
          </template>
          <div v-else class="empty-state">请选择一条申请进度</div>
        </aside>
      </section>
    </main>
  </div>
</template>
