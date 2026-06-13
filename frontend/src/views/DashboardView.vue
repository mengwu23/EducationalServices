<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { navigationItems } from "@/config/navigation";
import { authState, hasPermission, logout, roleLabelMap } from "@/stores/authStore";

const router = useRouter();

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

const modules = computed(() => {
  const role = user.value?.role || "";
  return navigationItems.filter((item) => {
    const isBusinessModule = item.key !== "dashboard" && item.description;
    const roleMatched = item.roles.includes(role);
    const permissionMatched = !item.permission || hasPermission(item.permission);
    return isBusinessModule && roleMatched && permissionMatched;
  });
});

const serviceItems = [
  { name: "张明", stage: "材料清单", status: "待补充成绩单", risk: "中" },
  { name: "李雨", stage: "院校申请", status: "3 所院校待反馈", risk: "低" },
  { name: "王璐", stage: "签证准备", status: "需确认资金证明", risk: "高" },
  { name: "赵晨", stage: "顾问沟通", status: "今日需回访", risk: "中" },
];

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
          <h1>今日服务总览</h1>
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
          <h2>把申请规划、学生风险和顾问协同放在同一个工作面</h2>
          <p>登录后系统已加载当前权限，工作台仅展示你可处理的业务模块。</p>
        </div>
        <div class="permission-panel">
          <span>当前权限</span>
          <strong>{{ authState.permissions.length }}</strong>
          <p>{{ authState.permissions.includes("*") ? "全部权限" : "按角色授权" }}</p>
        </div>
      </section>

      <section class="metric-grid">
        <article>
          <span>今日待办</span>
          <strong>27</strong>
          <p>审批、回访、报告确认</p>
        </article>
        <article>
          <span>风险提醒</span>
          <strong>8</strong>
          <p>心理预警与服务节点</p>
        </article>
        <article>
          <span>申请推进</span>
          <strong>64%</strong>
          <p>本周目标完成率</p>
        </article>
        <article>
          <span>报告草稿</span>
          <strong>5</strong>
          <p>待确认与待发布</p>
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

        <aside class="assistant-panel">
          <p class="eyebrow">AI 助手</p>
          <h2>服务动作建议</h2>
          <div class="assistant-message">
            <strong>建议优先处理高风险学生</strong>
            <p>王璐的签证材料存在缺口，同时有一条服务风险提醒，建议今天完成顾问回访。</p>
          </div>
          <button class="secondary-button">生成服务摘要</button>
        </aside>
      </section>

      <section class="table-section">
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
