<script setup lang="ts">
import { computed } from "vue";
import { getVisibleNavigationItems } from "@/config/navigation";
import { authState } from "@/stores/authStore";

defineProps<{
  activeKey: string;
}>();

const visibleItems = computed(() => {
  const role = authState.user?.role || "";
  return getVisibleNavigationItems(role, authState.permissions);
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
