<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { authState, logout, roleLabelMap } from "@/stores/authStore";

const router = useRouter();
const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");

function handleLogout() {
  logout();
  router.push("/login");
}
</script>

<template>
  <div class="app-frame">
    <AppSidebar active-key="" />

    <main class="dashboard">
      <header class="topbar">
        <div>
          <p class="eyebrow">权限限制</p>
          <h1>无权限访问</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <section class="empty-state">
        <p>当前账号没有访问该功能模块的权限。</p>
        <button class="primary-button" type="button" @click="router.push('/dashboard')">返回工作台</button>
      </section>
    </main>
  </div>
</template>
