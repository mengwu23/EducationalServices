<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { createActivitySignup, listServiceEvents, searchServiceFaq, searchServiceProjects, sendServiceMessage } from "@/api/serviceAgent";
import { authState, logout, roleLabelMap } from "@/stores/authStore";
import type { ServiceEventItem, ServiceFaqItem, ServiceProjectItem } from "@/types/serviceAgent";

const router = useRouter();
const loading = ref(false);
const actionLoading = ref(false);
const message = ref("");
const keyword = ref("");
const faqs = ref<ServiceFaqItem[]>([]);
const projects = ref<ServiceProjectItem[]>([]);
const events = ref<ServiceEventItem[]>([]);
const visitorMessage = ref("我想了解英国硕士申请服务");
const reply = ref("");
const conversationId = ref<string | null>(null);
const signupName = ref("");
const signupPhone = ref("");
const selectedEvent = ref<ServiceEventItem | null>(null);

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

async function loadData() {
  loading.value = true;
  message.value = "";
  try {
    const [faqResult, projectResult, eventResult] = await Promise.all([
      searchServiceFaq(keyword.value, 6),
      searchServiceProjects({ keyword: keyword.value, limit: 6 }),
      listServiceEvents({ keyword: keyword.value, limit: 8 }),
    ]);
    faqs.value = faqResult || [];
    projects.value = projectResult || [];
    events.value = eventResult || [];
    selectedEvent.value = events.value[0] || null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "客服中心数据加载失败";
  } finally {
    loading.value = false;
  }
}

async function handleMessage() {
  actionLoading.value = true;
  try {
    const result = await sendServiceMessage(visitorMessage.value, conversationId.value);
    reply.value = result.reply_text;
    conversationId.value = result.conversation_id;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "客服消息发送失败";
  } finally {
    actionLoading.value = false;
  }
}

async function handleSignup() {
  if (!selectedEvent.value) return;
  actionLoading.value = true;
  try {
    await createActivitySignup({
      event_id: selectedEvent.value.id,
      visitor_name: signupName.value,
      visitor_phone: signupPhone.value,
      conversation_id: conversationId.value,
    });
    message.value = "活动报名已创建";
  } catch (error) {
    message.value = error instanceof Error ? error.message : "活动报名失败";
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
    <AppSidebar active-key="service-center" />
    <main class="dashboard">
      <header class="topbar">
        <div>
          <p class="eyebrow">访客服务</p>
          <h1>客服中心</h1>
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
              <p class="eyebrow">资源检索</p>
              <h2>FAQ / 项目 / 活动</h2>
            </div>
            <button class="ghost-button" type="button" @click="loadData">查询</button>
          </div>
          <div class="filter-row">
            <input v-model="keyword" placeholder="关键词" @keyup.enter="loadData" />
          </div>
          <article v-for="item in faqs" :key="String(item.id || item.question)" class="assistant-message">
            <strong>{{ item.question || "FAQ" }}</strong>
            <p>{{ item.answer }}</p>
          </article>
          <div class="module-grid">
            <article v-for="project in projects" :key="String(project.id || project.project_name)" class="module-card sand">
              <div><span>项</span><strong>{{ project.project_name || "推荐项目" }}</strong></div>
              <p>{{ project.target_country || project.education_level || "留学项目" }}</p>
            </article>
          </div>
        </div>
        <aside class="assistant-panel">
          <p class="eyebrow">客服对话</p>
          <h2>访客消息</h2>
          <label class="reject-comment">
            <span>消息</span>
            <textarea v-model="visitorMessage" rows="4" />
          </label>
          <button class="primary-button" :disabled="actionLoading" type="button" @click="handleMessage">发送</button>
          <div class="reason-box"><strong>回复</strong><p>{{ reply || "暂无回复" }}</p></div>
          <label class="reject-comment"><span>报名姓名</span><input v-model="signupName" /></label>
          <label class="reject-comment"><span>报名电话</span><input v-model="signupPhone" /></label>
          <select v-model="selectedEvent">
            <option v-for="event in events" :key="event.id" :value="event">{{ event.event_name || event.title || `活动 ${event.id}` }}</option>
          </select>
          <button class="secondary-button" :disabled="actionLoading || !selectedEvent" type="button" @click="handleSignup">创建报名</button>
        </aside>
      </section>
    </main>
  </div>
</template>
