<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import AppSidebar from "@/components/common/AppSidebar.vue";
import { authState, logout, refreshCurrentRolePermissions, roleLabelMap } from "@/stores/authStore";
import { permissionCatalog, permissionState, resetRolePermissions, setRolePermissions } from "@/stores/permissionStore";

const router = useRouter();
const selectedRole = ref<"manager" | "employee" | "student">("employee");
const message = ref("");

const user = computed(() => authState.user);
const roleLabel = computed(() => roleLabelMap[user.value?.role || ""] || user.value?.role || "-");
const groupedPermissions = computed(() => {
  return permissionCatalog.reduce<Record<string, typeof permissionCatalog>>((groups, item) => {
    if (!groups[item.group]) groups[item.group] = [];
    groups[item.group].push(item);
    return groups;
  }, {});
});
const selectedPermissions = computed(() => permissionState.rolePermissions[selectedRole.value] || []);
const selectedPermissionSet = computed(() => new Set(selectedPermissions.value));

function hasRolePermission(code: string): boolean {
  return selectedPermissionSet.value.has(code);
}

function togglePermission(code: string): void {
  const next = new Set(selectedPermissions.value);
  if (next.has(code)) {
    next.delete(code);
  } else {
    next.add(code);
  }
  setRolePermissions(selectedRole.value, Array.from(next));
  refreshCurrentRolePermissions();
  message.value = "权限配置已更新";
}

function selectAll(): void {
  setRolePermissions(selectedRole.value, permissionCatalog.map((item) => item.code));
  refreshCurrentRolePermissions();
  message.value = "已勾选当前角色全部权限";
}

function clearAll(): void {
  setRolePermissions(selectedRole.value, []);
  refreshCurrentRolePermissions();
  message.value = "已清空当前角色权限";
}

function handleReset(): void {
  resetRolePermissions();
  refreshCurrentRolePermissions();
  message.value = "已恢复默认权限配置";
}

function handleLogout() {
  logout();
  router.push("/login");
}
</script>

<template>
  <div class="app-frame">
    <AppSidebar active-key="permission-admin" />
    <main class="dashboard permission-admin-page">
      <header class="topbar">
        <div>
          <p class="eyebrow">系统管理</p>
          <h1>权限调整</h1>
        </div>
        <div class="user-chip">
          <span>{{ roleLabel }}</span>
          <strong>{{ user?.real_name || user?.username }}</strong>
          <button type="button" @click="handleLogout">退出</button>
        </div>
      </header>

      <p v-if="message" class="module-message">{{ message }}</p>

      <section class="permission-admin-layout">
        <aside class="permission-role-panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">角色</p>
              <h2>选择角色</h2>
            </div>
          </div>
          <button
            v-for="role in ['manager', 'employee', 'student']"
            :key="role"
            :class="{ active: selectedRole === role }"
            type="button"
            @click="selectedRole = role as 'manager' | 'employee' | 'student'"
          >
            <strong>{{ roleLabelMap[role] || role }}</strong>
            <span>{{ (permissionState.rolePermissions[role] || []).length }} 项权限</span>
          </button>
        </aside>

        <section class="permission-matrix">
          <div class="section-heading">
            <div>
              <p class="eyebrow">权限矩阵</p>
              <h2>{{ roleLabelMap[selectedRole] }}权限</h2>
            </div>
            <div class="permission-actions">
              <button class="ghost-button" type="button" @click="selectAll">全选</button>
              <button class="ghost-button" type="button" @click="clearAll">清空</button>
              <button class="danger-button" type="button" @click="handleReset">恢复默认</button>
            </div>
          </div>

          <div class="permission-group-grid">
            <article v-for="(items, group) in groupedPermissions" :key="group" class="permission-group">
              <h3>{{ group }}</h3>
              <label v-for="item in items" :key="item.code" class="permission-check">
                <input :checked="hasRolePermission(item.code)" type="checkbox" @change="togglePermission(item.code)" />
                <span>
                  <strong>{{ item.label }}</strong>
                  <em>{{ item.code }}</em>
                </span>
              </label>
            </article>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>
