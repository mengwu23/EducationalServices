<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { login, loginAsVisitor } from "@/stores/authStore";

const router = useRouter();
const username = ref("");
const password = ref("");
const remember = ref(false);
const errorMessage = ref("");
const submitting = ref(false);
const employeeDemoAccount = {
  username: "emp002",
  password: "123456",
};

const canSubmit = computed(() => username.value.trim() && password.value.trim() && !submitting.value);

async function handleLogin() {
  if (!canSubmit.value) {
    return;
  }
  errorMessage.value = "";
  submitting.value = true;
  try {
    await login(username.value.trim(), password.value);
    if (remember.value) {
      localStorage.setItem("education_service_remembered_username", username.value.trim());
    } else {
      localStorage.removeItem("education_service_remembered_username");
    }
    await router.push("/dashboard");
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "登录失败，请稍后重试";
  } finally {
    submitting.value = false;
  }
}

async function handleVisitorLogin() {
  errorMessage.value = "";
  submitting.value = true;
  try {
    loginAsVisitor();
    localStorage.removeItem("education_service_remembered_username");
    await router.push("/service-center");
  } finally {
    submitting.value = false;
  }
}

function useDemoAccount(account: "manager" | "employee" | "student" | "admin") {
  const map = {
    manager: "emp001",
    employee: employeeDemoAccount.username,
    student: "stu001",
    admin: "emp008",
  };
  username.value = map[account];
  password.value = "123456";
}
</script>

<template>
  <main class="login-page">
    <section class="login-shell">
      <div class="login-intro">
        <div class="brand-mark">留</div>
        <p class="eyebrow">留学服务运营中台</p>
        <h1>教育服务系统</h1>
        <p class="intro-copy">
          面向顾问、老师、客服和主管的统一工作入口，集中管理申请规划、材料进度、服务风险与智能报告。
        </p>

        <div class="marketing-grid" aria-label="产品服务能力">
          <article>
            <span>01</span>
            <strong>全流程留学规划</strong>
            <p>从选校定位到申请节奏，全程清晰推进。</p>
          </article>
          <article>
            <span>02</span>
            <strong>材料与进度协同</strong>
            <p>文书、签证、成绩、院校状态统一跟踪。</p>
          </article>
          <article>
            <span>03</span>
            <strong>顾问服务闭环</strong>
            <p>沟通记录、待办提醒、风险预警及时同步。</p>
          </article>
        </div>
      </div>

      <form class="login-card" @submit.prevent="handleLogin">
        <div class="form-heading">
          <p class="eyebrow">统一登录</p>
          <h2>进入工作台</h2>
          <span>登录后自动加载当前角色与权限菜单。</span>
        </div>

        <label>
          <span>账号</span>
          <input v-model="username" autocomplete="username" placeholder="请输入账号" />
        </label>

        <label>
          <span>密码</span>
          <input v-model="password" autocomplete="current-password" placeholder="请输入密码" type="password" />
        </label>

        <div class="form-row">
          <label class="checkbox-line">
            <input v-model="remember" type="checkbox" />
            <span>记住账号</span>
          </label>
          <div class="demo-actions">
            <button type="button" @click="useDemoAccount('employee')">员工</button>
            <button type="button" @click="useDemoAccount('manager')">主管</button>
            <button type="button" @click="useDemoAccount('student')">学生</button>
            <button type="button" @click="useDemoAccount('admin')">管理员</button>
          </div>
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button class="primary-button" :disabled="!canSubmit" type="submit">
          {{ submitting ? "登录中..." : "登录" }}
        </button>
        <button class="secondary-button visitor-login-button" :disabled="submitting" type="button" @click="handleVisitorLogin">
          游客进入客服中心
        </button>
      </form>

      <aside class="study-visual" aria-label="留学服务视觉">
        <div class="visual-top">
          <div>
            <p class="eyebrow">留学服务</p>
            <h3>申请规划</h3>
          </div>
          <span class="status-pill">进行中</span>
        </div>
        <div class="timeline">
          <div><span></span><strong>选校定位</strong><em>已完成</em></div>
          <div><span></span><strong>材料清单</strong><em>8/12</em></div>
          <div><span></span><strong>院校进度</strong><em>3 所待反馈</em></div>
          <div><span></span><strong>签证准备</strong><em>下周启动</em></div>
        </div>
        <div class="document-stack">
          <div class="document-card">
            <strong>顾问协同</strong>
            <p>今日 5 项待办，2 条风险提醒</p>
          </div>
          <div class="document-card secondary">
            <strong>AI 助手</strong>
            <p>可生成阶段总结与服务报告</p>
          </div>
        </div>
      </aside>
    </section>
  </main>
</template>
