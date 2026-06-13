<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { analyzeCustomer, getCustomerJudgement, listCustomerJudgements } from "@/api/customerJudgement";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { JudgementRecordDetail, JudgementRecordItem } from "@/types/customerJudgement";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const statusFilter = ref("");
const levelFilter = ref("");
const dateStart = ref("");
const dateEnd = ref("");
const records = ref<JudgementRecordItem[]>([]);
const total = ref(0);
const selectedRecord = ref<JudgementRecordItem | null>(null);
const recordDetail = ref<JudgementRecordDetail | null>(null);
const analyzeText = ref("学员王明，22岁，南京大学软件工程本科大四在读，GPA 3.6，雅思6.5。意向申请新加坡国立大学计算机硕士，预算25-30万/年，有一段腾讯实习经历。");
const sysQuery = ref("请判断是否适合新加坡计算机硕士申请，并给出下一步跟进建议。");
const targetProduct = ref("新加坡国际本硕升学计划");
const leadId = ref("");
const fileInput = ref<HTMLInputElement | null>(null);
const attachedFiles = ref<File[]>([]);

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

const completedCount = computed(() => records.value.filter((item) => item.status === "completed").length);
const failedCount = computed(() => records.value.filter((item) => item.status === "failed").length);
const highMatchCount = computed(() => records.value.filter((item) => item.match_level === "high").length);
const averageScore = computed(() => {
  const scores = records.value.map((item) => item.match_score).filter((item): item is number => typeof item === "number");
  if (!scores.length) return "-";
  return Math.round(scores.reduce((sum, item) => sum + item, 0) / scores.length);
});

const statusLabelMap: Record<string, string> = {
  pending: "待研判",
  completed: "已完成",
  failed: "失败",
};

const levelLabelMap: Record<string, string> = {
  high: "高匹配",
  medium: "中匹配",
  low: "低匹配",
};

watch(selectedRecord, async (record) => {
  if (!record) {
    recordDetail.value = null;
    return;
  }
  try {
    recordDetail.value = await getCustomerJudgement(record.id);
  } catch {
    recordDetail.value = null;
  }
});

function statusLabel(value: string): string {
  return statusLabelMap[value] || value;
}

function levelLabel(value?: string | null): string {
  return value ? levelLabelMap[value] || value : "未评级";
}

function targetLabel(value?: number | null): string {
  if (value === 1) return "目标客户";
  if (value === 0) return "非目标客户";
  return "待判断";
}

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
}

function onFilesChange(event: Event) {
  const input = event.target as HTMLInputElement;
  attachedFiles.value = Array.from(input.files || []);
}

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const result = await listCustomerJudgements({
      page: 1,
      page_size: 50,
      status: statusFilter.value,
      match_level: levelFilter.value,
      date_start: dateStart.value,
      date_end: dateEnd.value,
    });
    records.value = result.items || [];
    total.value = result.total;
    selectedRecord.value = records.value.find((item) => item.id === selectedRecord.value?.id) || records.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "客户研判数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleAnalyze() {
  if (!analyzeText.value.trim()) {
    message.value = "请先填写客户信息";
    return;
  }
  actionLoading.value = true;
  message.value = "";
  try {
    const result = await analyzeCustomer({
      text: analyzeText.value.trim(),
      sys_query: sysQuery.value.trim() || undefined,
      target_product: targetProduct.value.trim() || undefined,
      lead_id: leadId.value ? Number(leadId.value) : null,
      files: attachedFiles.value,
    });
    message.value = "客户研判已完成";
    if ("batch" in result && result.records?.length) {
      recordDetail.value = result.records[0];
      selectedRecord.value = result.records[0];
    } else if (!("batch" in result)) {
      recordDetail.value = result;
      selectedRecord.value = result;
    }
    if (fileInput.value) fileInput.value.value = "";
    attachedFiles.value = [];
    await loadData();
  } catch (error) {
    message.value = error instanceof Error ? error.message : "客户研判提交失败";
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
    <AppSidebar active-key="customer-judgement" />

    <main class="dashboard judgement-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">客户运营</p>
          <h1>客户研判</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="leave-summary judgement-summary">
        <article>
          <span>研判记录</span>
          <strong>{{ total }}</strong>
          <p>当前筛选范围内的客户画像研判</p>
        </article>
        <article>
          <span>已完成</span>
          <strong>{{ completedCount }}</strong>
          <p>已返回匹配等级和建议</p>
        </article>
        <article>
          <span>高匹配</span>
          <strong>{{ highMatchCount }}</strong>
          <p>适合优先跟进的意向客户</p>
        </article>
        <article>
          <span>均分</span>
          <strong>{{ averageScore }}</strong>
          <p>基于当前列表计算</p>
        </article>
      </section>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="judgement-workspace">
        <div class="judgement-left">
          <section class="judgement-analyze-panel">
            <div class="section-heading">
              <div>
                <p class="eyebrow">研判入口</p>
                <h2>提交客户信息</h2>
              </div>
              <button class="primary-button compact-button" :disabled="actionLoading" type="button" @click="handleAnalyze">
                开始研判
              </button>
            </div>
            <div class="judgement-form-grid">
              <label class="wide-field">
                <span>客户信息</span>
                <textarea v-model="analyzeText" rows="5" />
              </label>
              <label>
                <span>目标产品</span>
                <input v-model="targetProduct" placeholder="例如：新加坡国际本硕升学计划" />
              </label>
              <label>
                <span>线索 ID</span>
                <input v-model="leadId" placeholder="可为空" />
              </label>
              <label class="wide-field">
                <span>补充要求</span>
                <input v-model="sysQuery" placeholder="补充研判口径" />
              </label>
              <label class="wide-field">
                <span>附件</span>
                <input ref="fileInput" type="file" multiple @change="onFilesChange" />
              </label>
            </div>
          </section>

          <section class="judgement-list-panel">
            <div class="section-heading">
              <div>
                <p class="eyebrow">研判记录</p>
                <h2>客户匹配队列</h2>
              </div>
              <button class="ghost-button" :disabled="loading" type="button" @click="loadData">刷新</button>
            </div>

            <div class="filter-row judgement-filter">
              <select v-model="statusFilter" @change="loadData">
                <option value="">全部状态</option>
                <option value="pending">待研判</option>
                <option value="completed">已完成</option>
                <option value="failed">失败</option>
              </select>
              <select v-model="levelFilter" @change="loadData">
                <option value="">全部等级</option>
                <option value="high">高匹配</option>
                <option value="medium">中匹配</option>
                <option value="low">低匹配</option>
              </select>
              <input v-model="dateStart" type="date" @change="loadData" />
              <input v-model="dateEnd" type="date" @change="loadData" />
            </div>

            <div v-if="loading" class="empty-state">正在加载客户研判记录...</div>
            <div v-else-if="!records.length" class="empty-state">暂无客户研判记录</div>
            <table v-else class="leave-table">
              <thead>
                <tr>
                  <th>编号</th>
                  <th>目标产品</th>
                  <th>匹配</th>
                  <th>分数</th>
                  <th>状态</th>
                  <th>创建时间</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in records"
                  :key="item.id"
                  :class="{ selected: selectedRecord?.id === item.id }"
                  @click="selectedRecord = item"
                >
                  <td>
                    <strong>{{ item.analysis_no }}</strong>
                    <span>{{ targetLabel(item.is_target_customer) }}</span>
                  </td>
                  <td>{{ item.target_product || "未指定" }}</td>
                  <td><span :class="['match-chip', item.match_level || 'unknown']">{{ levelLabel(item.match_level) }}</span></td>
                  <td>{{ item.match_score ?? "-" }}</td>
                  <td><span :class="['status-chip', item.status]">{{ statusLabel(item.status) }}</span></td>
                  <td>{{ formatDateTime(item.create_time) }}</td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>

        <aside class="judgement-detail-panel">
          <template v-if="recordDetail || selectedRecord">
            <p class="eyebrow">研判详情</p>
            <h2>{{ recordDetail?.analysis_no || selectedRecord?.analysis_no }}</h2>
            <div class="detail-tags">
              <span :class="['match-chip', (recordDetail || selectedRecord)?.match_level || 'unknown']">
                {{ levelLabel((recordDetail || selectedRecord)?.match_level) }}
              </span>
              <span :class="['status-chip', (recordDetail || selectedRecord)?.status]">
                {{ statusLabel((recordDetail || selectedRecord)?.status || '-') }}
              </span>
            </div>

            <dl>
              <div>
                <dt>目标客户</dt>
                <dd>{{ targetLabel((recordDetail || selectedRecord)?.is_target_customer) }}</dd>
              </div>
              <div>
                <dt>匹配分</dt>
                <dd>{{ (recordDetail || selectedRecord)?.match_score ?? "-" }}</dd>
              </div>
              <div>
                <dt>线索 ID</dt>
                <dd>{{ (recordDetail || selectedRecord)?.lead_id || "-" }}</dd>
              </div>
              <div>
                <dt>来源</dt>
                <dd>{{ (recordDetail || selectedRecord)?.source_type || "-" }}</dd>
              </div>
            </dl>

            <div class="reason-box">
              <strong>研判摘要</strong>
              <p>{{ recordDetail?.executive_summary || selectedRecord?.reason_summary || "暂无摘要" }}</p>
            </div>
            <div class="reason-box judgement-box">
              <strong>跟进建议</strong>
              <p>{{ (recordDetail || selectedRecord)?.suggestion || "暂无建议" }}</p>
            </div>
            <div class="reason-box judgement-box">
              <strong>原始信息</strong>
              <p>{{ recordDetail?.raw_content || "选择记录后加载原始输入内容" }}</p>
            </div>

            <div v-if="recordDetail?.ai_result?.final_next_steps?.length" class="judgement-next">
              <strong>下一步动作</strong>
              <p v-for="step in recordDetail.ai_result.final_next_steps" :key="step">{{ step }}</p>
            </div>
          </template>
          <div v-else class="empty-state">请选择一条客户研判记录</div>
        </aside>
      </section>
    </main>
  </div>
</template>
