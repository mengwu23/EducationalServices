<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import PaginationBar from "@/components/common/PaginationBar.vue";
import { chatLifeAssistant, chatPolicyAssistant, listLifeSupportFaq } from "@/api/studentAssistant";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { LifeSupportFaq } from "@/types/studentAssistant";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const keyword = ref("");
const faqs = ref<LifeSupportFaq[]>([]);
const pagedFaqs = computed(() => faqs.value.slice((page.value - 1) * pageSize, page.value * pageSize));
const page = ref(1);
const pageSize = 5;
const total = ref(0);
const lifeQuestion = ref("宿舍网络不稳定应该联系谁？");
const policyQuestion = ref("英国硕士申请通常需要准备哪些材料？");
const answer = ref("");

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

async function loadFaq() {
  loading.value = true;
  try {
    const result = await listLifeSupportFaq(keyword.value, 50);
    faqs.value = result.items || [];
    total.value = faqs.value.length;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "FAQ 加载失败";
  } finally {
    loading.value = false;
  }
}

function reloadFromFirstPage() {
  page.value = 1;
  loadFaq();
}

function handlePageChange(nextPage: number) {
  page.value = nextPage;
  loadFaq();
}

async function askLife() {
  actionLoading.value = true;
  try {
    answer.value = (await chatLifeAssistant(lifeQuestion.value)).answer;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "生活助手请求失败";
  } finally {
    actionLoading.value = false;
  }
}

async function askPolicy() {
  actionLoading.value = true;
  try {
    answer.value = (await chatPolicyAssistant(policyQuestion.value)).answer;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "政策咨询请求失败";
  } finally {
    actionLoading.value = false;
  }
}

function handleLogout() {
  logout();
  router.push("/login");
}

onMounted(loadFaq);
</script>

<template>
  <div class="app-frame">
    <AppSidebar active-key="student-assistant" />
    <main class="dashboard">
      <header class="topbar">
        <div>
          <p class="eyebrow">学生端</p>
          <h1>学生助手</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>
      <p v-if="message" class="module-message">{{ message }}</p>
      <section class="student-grid">
        <div class="module-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">生活支持</p>
              <h2>FAQ</h2>
            </div>
            <button class="ghost-button" type="button" @click="reloadFromFirstPage">查询</button>
          </div>
          <div class="filter-row">
            <input v-model="keyword" placeholder="搜索生活服务问题" @keyup.enter="reloadFromFirstPage" />
          </div>
          <article v-for="item in pagedFaqs" :key="item.id" class="assistant-message">
            <strong>{{ item.question }}</strong>
            <p>{{ item.answer }}</p>
          </article>
          <PaginationBar :page="page" :page-size="pageSize" :total="total" :disabled="loading" @change="handlePageChange" />
        </div>
        <aside class="assistant-panel">
          <p class="eyebrow">AI 咨询</p>
          <h2>生活与政策</h2>
          <label class="reject-comment">
            <span>生活问题</span>
            <textarea v-model="lifeQuestion" rows="3" />
          </label>
          <button class="primary-button" :disabled="actionLoading" type="button" @click="askLife">问生活助手</button>
          <label class="reject-comment">
            <span>政策问题</span>
            <textarea v-model="policyQuestion" rows="3" />
          </label>
          <button class="secondary-button" :disabled="actionLoading" type="button" @click="askPolicy">问政策助手</button>
          <div class="reason-box">
            <strong>回复</strong>
            <p>{{ answer || "暂无回复" }}</p>
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>
