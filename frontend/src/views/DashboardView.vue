<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { authState, hasPermission, logout, roleLabelMap } from "@/stores/authStore";

const router = useRouter();

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

const modules = computed(() => {
  const role = user.value?.role || "";
  return [
  {
    title: "我的请假",
    desc: "学生提交请假、查看审批进度和取消待审批申请",
    roles: ["student", "admin"],
    permission: "student_leave:own",
    count: "自助",
    tone: "amber",
    route: "/student/leaves",
  },
  {
    title: "学生助手",
    desc: "生活支持、留学政策咨询和心理支持对话",
    roles: ["student", "admin"],
    permission: "student_psych:own",
    count: "AI",
    tone: "green",
    route: "/student/assistant",
  },
  {
    title: "请假审批",
    desc: "学生请假申请、审批历史与待处理统计",
    roles: ["manager", "employee", "admin"],
    permission: "student_leave:read",
    count: "12",
    tone: "amber",
    route: "/students/leaves",
  },
  {
    title: "学业事件",
    desc: "考试、论文、课程 Deadline 与提醒管理",
    roles: ["manager", "employee", "admin"],
    permission: "student_psych:read",
    count: "DDL",
    tone: "sand",
    route: "/academic-events",
  },
  {
    title: "心理预警",
    desc: "心理画像、风险预警、处理闭环",
    roles: ["manager", "employee", "admin"],
    permission: "student_psych:read",
    count: "6",
    tone: "red",
    route: "/students/psych",
  },
  {
    title: "客服中心",
    desc: "访客咨询、FAQ、项目推荐和活动报名",
    roles: ["manager", "employee", "admin"],
    permission: "enterprise_operation:execute",
    count: "客",
    tone: "green",
    route: "/service-center",
  },
  {
    title: "申请进度",
    desc: "文书、院校、签证、Offer 等关键节点追踪",
    roles: ["student", "manager", "employee", "admin"],
    permission: "",
    count: "32",
    tone: "sand",
    route: "/students/progress",
  },
  {
    title: "反馈工单",
    desc: "投诉、建议、咨询的分派处理与学生通知",
    roles: ["manager", "employee", "admin"],
    permission: "enterprise_operation:execute",
    count: "11",
    tone: "clay",
    route: "/students/feedback",
  },
  {
    title: "智能报告",
    desc: "报告生成、草稿确认、发布与导出",
    roles: ["manager", "employee", "admin"],
    permission: "report:read",
    count: "18",
    tone: "green",
    route: "/reports",
  },
  {
    title: "客户研判",
    desc: "客户资料分析、匹配等级与跟进建议",
    roles: ["manager", "employee", "admin"],
    permission: "customer_judgement:read",
    count: "24",
    tone: "clay",
    route: "/customer-judgement",
  },
  {
    title: "企业查询",
    desc: "线索、日报、组织、学生与待办汇总",
    roles: ["manager", "employee", "admin"],
    permission: "enterprise_operation:execute",
    count: "9",
    tone: "sand",
    route: "/business-query",
  },
  ].filter((item) => item.roles.includes(role) && (!item.permission || hasPermission(item.permission)));
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
              :key="item.title"
              :class="['module-card', item.tone, { clickable: item.route }]"
              @click="openModule(item.route)"
            >
              <div>
                <span>{{ item.count }}</span>
                <strong>{{ item.title }}</strong>
              </div>
              <p>{{ item.desc }}</p>
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
