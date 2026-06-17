<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import PaginationBar from "@/components/common/PaginationBar.vue";
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
const faqPage = ref(1);
const projectPage = ref(1);
const eventPage = ref(1);
const faqPageSize = 3;
const projectPageSize = 3;
const eventPageSize = 4;
const visitorMessage = ref("");
const chatLoading = ref(false);
const signupName = ref("");
const signupPhone = ref("");
const selectedEventId = ref<number | null>(null);
const chatHistoryRef = ref<HTMLElement | null>(null);

// ── Chat message interface ──
interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  isLoading?: boolean;
  error?: string;
  suggestedQuestions?: string[];
}

const chatMessages = ref<ChatMessage[]>([]);

// ── Conversation persistence ──
const STORAGE_KEY = "service_center_conversation_id";
const conversationId = ref<string | null>(
  localStorage.getItem(STORAGE_KEY) || null
);

watch(conversationId, (newVal) => {
  if (newVal) {
    localStorage.setItem(STORAGE_KEY, newVal);
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
});

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

const pagedFaqs = computed(() => faqs.value.slice((faqPage.value - 1) * faqPageSize, faqPage.value * faqPageSize));
const pagedProjects = computed(() => projects.value.slice((projectPage.value - 1) * projectPageSize, projectPage.value * projectPageSize));
const pagedEvents = computed(() => events.value.slice((eventPage.value - 1) * eventPageSize, eventPage.value * eventPageSize));

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
    faqPage.value = 1;
    projectPage.value = 1;
    eventPage.value = 1;
    selectedEventId.value = events.value[0]?.id ?? null;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "客服中心数据加载失败";
  } finally {
    loading.value = false;
  }
}

function handleFaqPageChange(nextPage: number) {
  faqPage.value = nextPage;
}

function handleProjectPageChange(nextPage: number) {
  projectPage.value = nextPage;
}

function handleEventPageChange(nextPage: number) {
  eventPage.value = nextPage;
  selectedEventId.value = pagedEvents.value[0]?.id ?? selectedEventId.value;
}

function scrollChatToBottom() {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight;
    }
  });
}

async function handleMessage() {
  const text = visitorMessage.value.trim();
  if (!text || chatLoading.value) return;

  // Add user message
  const userMsg: ChatMessage = {
    id: `u-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    role: "user",
    content: text,
    timestamp: Date.now(),
  };
  chatMessages.value.push(userMsg);

  // Add loading placeholder
  const loadingMsg: ChatMessage = {
    id: `a-loading-${Date.now()}`,
    role: "assistant",
    content: "",
    timestamp: Date.now(),
    isLoading: true,
  };
  chatMessages.value.push(loadingMsg);

  // Clear input
  visitorMessage.value = "";
  scrollChatToBottom();

  chatLoading.value = true;
  try {
    const result = await sendServiceMessage(text, conversationId.value);
    // Replace loading message with real reply
    const loadingIndex = chatMessages.value.findIndex(m => m.id === loadingMsg.id);
    if (loadingIndex !== -1) {
      chatMessages.value[loadingIndex] = {
        id: `a-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        role: "assistant",
        content: result.reply_text || "（无回复内容）",
        timestamp: Date.now(),
        suggestedQuestions: result.suggested_questions,
      };
    }
    conversationId.value = result.conversation_id;
  } catch (error) {
    let errMsg = "客服消息发送失败";
    if (error instanceof Error) {
      const raw = error.message;
      if (raw.includes("不可达") || raw.includes("ConnectError") || raw.includes("ConnectTimeout")) {
        errMsg = "智能客服暂时不可用，请稍后重试或联系人工客服";
      } else if (raw.includes("超时") || raw.includes("Timeout")) {
        errMsg = "客服响应超时，请稍后重试";
      } else if (raw.includes("API Key") || raw.includes("未授权")) {
        errMsg = "客服系统配置异常，请联系管理员";
      } else {
        errMsg = raw;
      }
    }
    // Replace loading message with error state
    const loadingIndex = chatMessages.value.findIndex(m => m.id === loadingMsg.id);
    if (loadingIndex !== -1) {
      chatMessages.value[loadingIndex] = {
        id: `a-err-${Date.now()}`,
        role: "assistant",
        content: "",
        timestamp: Date.now(),
        error: errMsg,
      };
    }
    message.value = errMsg;
  } finally {
    chatLoading.value = false;
    scrollChatToBottom();
  }
}

function handleSuggestedClick(question: string) {
  visitorMessage.value = question;
  handleMessage();
}

async function handleSignup() {
  const selectedEvent = events.value.find(e => e.id === selectedEventId.value);
  if (!selectedEvent) return;
  actionLoading.value = true;
  try {
    await createActivitySignup({
      event_id: selectedEvent.id,
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
          <article v-for="item in pagedFaqs" :key="String(item.id || item.question)" class="assistant-message">
            <strong>{{ item.question || "FAQ" }}</strong>
            <p>{{ item.answer }}</p>
          </article>
          <PaginationBar :page="faqPage" :page-size="faqPageSize" :total="faqs.length" :disabled="loading" @change="handleFaqPageChange" />
          <div class="module-grid">
            <article v-for="project in pagedProjects" :key="String(project.id || project.project_name)" class="module-card sand">
              <div><span>项</span><strong>{{ project.project_name || "推荐项目" }}</strong></div>
              <p>{{ project.target_country || project.education_level || "留学项目" }}</p>
            </article>
          </div>
          <PaginationBar :page="projectPage" :page-size="projectPageSize" :total="projects.length" :disabled="loading" @change="handleProjectPageChange" />
        </div>
        <aside class="assistant-panel">
          <p class="eyebrow">客服对话</p>
          <h2>访客消息</h2>

          <!-- Chat history -->
          <div ref="chatHistoryRef" class="chat-history">
            <div v-if="chatMessages.length === 0" class="chat-empty">
              👋 您好！我是客服小助手，请输入您的问题开始对话~
            </div>
            <div
              v-for="msg in chatMessages"
              :key="msg.id"
              :class="['chat-bubble', msg.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--assistant']"
            >
              <div class="chat-bubble__role">{{ msg.role === 'user' ? '访客' : '客服' }}</div>
              <!-- Loading dots -->
              <div v-if="msg.isLoading" class="chat-loading">
                <span class="chat-dot"></span><span class="chat-dot"></span><span class="chat-dot"></span>
              </div>
              <!-- Error state -->
              <div v-else-if="msg.error" class="chat-error">{{ msg.error }}</div>
              <!-- Normal content -->
              <div v-else class="chat-content">{{ msg.content }}</div>
              <!-- Suggested questions -->
              <div v-if="msg.suggestedQuestions && msg.suggestedQuestions.length" class="chat-suggestions">
                <button
                  v-for="q in msg.suggestedQuestions"
                  :key="q"
                  class="chat-suggestion-chip"
                  type="button"
                  @click="handleSuggestedClick(q)"
                >
                  {{ q }}
                </button>
              </div>
              <div class="chat-time">{{ new Date(msg.timestamp).toLocaleTimeString() }}</div>
            </div>
          </div>

          <!-- Input area -->
          <label class="reject-comment">
            <span>消息</span>
            <textarea
              v-model="visitorMessage"
              rows="4"
              placeholder="输入您的问题，Ctrl+Enter 发送..."
              @keyup.ctrl.enter="handleMessage"
            />
          </label>
          <button
            class="primary-button"
            :disabled="chatLoading || !visitorMessage.trim()"
            type="button"
            @click="handleMessage"
          >
            {{ chatLoading ? '发送中...' : '发送' }}
          </button>

          <label class="reject-comment"><span>报名姓名</span><input v-model="signupName" /></label>
          <label class="reject-comment"><span>报名电话</span><input v-model="signupPhone" /></label>
          <select v-model="selectedEventId">
            <option v-for="event in pagedEvents" :key="event.id" :value="event.id">{{ event.event_name || event.title || `活动 ${event.id}` }}</option>
          </select>
          <PaginationBar :page="eventPage" :page-size="eventPageSize" :total="events.length" :disabled="loading" @change="handleEventPageChange" />
          <button class="secondary-button" :disabled="actionLoading || !selectedEventId" type="button" @click="handleSignup">创建报名</button>
        </aside>
      </section>
    </main>
  </div>
</template>
