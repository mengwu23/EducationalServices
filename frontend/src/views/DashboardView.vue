<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { getVisibleNavigationItems } from "@/config/navigation";
import { authState, logout, roleLabelMap } from "@/stores/authStore";

const router = useRouter();

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const isStudent = computed(() => user.value?.role === "student");
const permissionValue = computed(() => (authState.permissions.includes("*") ? "全部" : String(authState.permissions.length)));
const permissionDesc = computed(() => (authState.permissions.includes("*") ? "全部权限" : `${authState.permissions.length} 项权限`));

const modules = computed(() => {
  const role = user.value?.role || "";
  return getVisibleNavigationItems(role, authState.permissions).filter((item) => item.key !== "dashboard" && item.description);
});

const serviceItems = [
  { name: "张明", stage: "材料清单", status: "待补充成绩单", risk: "中" },
  { name: "李雨", stage: "院校申请", status: "3 所院校待反馈", risk: "低" },
  { name: "王璐", stage: "签证准备", status: "需确认资金证明", risk: "高" },
  { name: "赵晨", stage: "顾问沟通", status: "今日需回访", risk: "中" },
];

const dashboardMetrics = computed(() => {
  if (isStudent.value) {
    return [
      { label: "可用功能", value: String(modules.value.length), desc: "当前账号可访问的学生服务入口" },
      { label: "当前身份", value: "学生", desc: "仅展示本人相关服务数据" },
      { label: "服务范围", value: "本人", desc: "请假、反馈、心理与申请进度" },
      { label: "数据边界", value: "已限制", desc: "不展示其他学生服务记录" },
    ];
  }
  return [
    { label: "今日待办", value: "27", desc: "审批、回访、报告确认" },
    { label: "风险提醒", value: "8", desc: "心理预警与服务节点" },
    { label: "申请推进", value: "64%", desc: "本周目标完成率" },
    { label: "报告草稿", value: "5", desc: "待确认与待发布" },
  ];
});

function handleLogout() {
  logout();
  router.push("/login");
}

function openModule(route: string) {
  if (route) {
    router.push(route);
  }
}
</script>

<template>
  <div class="app-frame">
    <AppSidebar active-key="dashboard" />

    <main class="dashboard">
      <header class="topbar">
        <div>
          <p class="eyebrow">工作台</p>
          <h1>{{ isStudent ? "我的服务总览" : "今日服务总览" }}</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="hero-band">
        <div>
          <p class="eyebrow">留学服务</p>
          <h2>{{ isStudent ? "查看自己的申请进度、请假反馈和心理关怀" : "把申请规划、学生风险和顾问协同放在同一个工作面" }}</h2>
          <p>{{ isStudent ? "登录后系统只展示与你本人相关的学生服务入口。" : "登录后系统已加载当前权限，工作台仅展示你可处理的业务模块。" }}</p>
        </div>
        <div class="permission-panel">
          <span>当前权限</span>
          <strong>{{ permissionValue }}</strong>
          <p>{{ permissionDesc }}</p>
        </div>
      </section>

      <section class="metric-grid">
        <article v-for="item in dashboardMetrics" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.desc }}</p>
        </article>
      </section>

      <section class="content-grid">
        <div class="module-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">业务模块</p>
              <h2>可访问功能</h2>
            </div>
            <span>{{ modules.length }} 个模块</span>
          </div>

          <div class="module-grid">
            <article
              v-for="item in modules"
              :key="item.key"
              :class="['module-card', item.tone, { clickable: item.route }]"
              @click="openModule(item.route)"
            >
              <div>
                <span>{{ item.count }}</span>
                <strong>{{ item.label }}</strong>
              </div>
              <p>{{ item.description }}</p>
            </article>
          </div>
        </div>

        <aside v-if="!isStudent" class="assistant-panel">
          <p class="eyebrow">AI 助手</p>
          <h2>服务动作建议</h2>
          <div class="assistant-message">
            <strong>建议优先处理高风险学生</strong>
            <p>王璐的签证材料存在缺口，同时有一条服务风险提醒，建议今天完成顾问回访。</p>
          </div>
          <button class="secondary-button">生成服务摘要</button>
        </aside>
      </section>

      <section v-if="!isStudent" class="table-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">学生服务动态</p>
            <h2>重点跟进列表</h2>
          </div>
          <button class="ghost-button" type="button" @click="router.push('/students/progress')">查看全部</button>
        </div>
        <table>
          <thead>
            <tr>
              <th>学生姓名</th>
              <th>当前阶段</th>
              <th>服务状态</th>
              <th>风险等级</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in serviceItems" :key="item.name">
              <td>{{ item.name }}</td>
              <td>{{ item.stage }}</td>
              <td>{{ item.status }}</td>
              <td><span :class="['risk-tag', item.risk]">{{ item.risk }}</span></td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>
