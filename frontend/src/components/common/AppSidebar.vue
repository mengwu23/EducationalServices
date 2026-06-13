<script setup lang="ts">
import { computed } from "vue";
import { authState, hasPermission } from "@/stores/authStore";

interface MenuItem {
  key: string;
  label: string;
  route: string;
  roles: string[];
  permission?: string;
}

defineProps<{
  activeKey: string;
}>();

const menuItems: MenuItem[] = [
  { key: "dashboard", label: "工作台", route: "/dashboard", roles: ["admin", "manager", "employee", "student"] },
  { key: "student-leaves", label: "我的请假", route: "/student/leaves", roles: ["admin", "student"], permission: "student_leave:own" },
  { key: "student-psych-care", label: "心理关怀", route: "/student/psych-care", roles: ["admin", "student"], permission: "student_psych:own" },
  { key: "student-feedback", label: "我的反馈", route: "/student/feedback", roles: ["admin", "student"] },
  { key: "student-assistant", label: "学生助手", route: "/student/assistant", roles: ["admin", "student"] },
  { key: "leave-approval", label: "请假审批", route: "/students/leaves", roles: ["admin", "manager", "employee"], permission: "student_leave:read" },
  { key: "psych-alert", label: "心理预警", route: "/students/psych", roles: ["admin", "manager", "employee"], permission: "student_psych:read" },
  { key: "academic-events", label: "学业事件", route: "/academic-events", roles: ["admin", "manager", "employee"] },
  { key: "application-progress", label: "申请进度", route: "/students/progress", roles: ["admin", "manager", "employee", "student"] },
  { key: "feedback", label: "反馈工单", route: "/students/feedback", roles: ["admin", "manager", "employee"], permission: "enterprise_operation:execute" },
  { key: "reports", label: "智能报告", route: "/reports", roles: ["admin", "manager", "employee"], permission: "report:read" },
  { key: "customer-judgement", label: "客户研判", route: "/customer-judgement", roles: ["admin", "manager", "employee"], permission: "customer_judgement:read" },
  { key: "enterprise-query", label: "企业查询", route: "/business-query", roles: ["admin", "manager", "employee"], permission: "enterprise_operation:execute" },
  { key: "service-center", label: "客服中心", route: "/service-center", roles: ["admin", "manager", "employee"] },
];

const visibleItems = computed(() => {
  const role = authState.user?.role || "";
  return menuItems.filter((item) => {
    const roleMatched = item.roles.includes(role);
    const permissionMatched = !item.permission || hasPermission(item.permission);
    return roleMatched && permissionMatched;
  });
});
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-mark">留</div>
      <div>
        <strong>教育服务系统</strong>
        <span>留学服务运营中台</span>
      </div>
    </div>
    <nav>
      <RouterLink
        v-for="item in visibleItems"
        :key="item.key"
        :class="{ active: activeKey === item.key }"
        :to="item.route"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
  </aside>
</template>
