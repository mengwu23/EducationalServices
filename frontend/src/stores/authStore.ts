import { reactive } from "vue";
import { clearStoredToken, getStoredToken } from "@/api/request";
import { getCurrentPermissions, getCurrentUser, login as loginApi } from "@/api/auth";
import type { CurrentUser } from "@/types/auth";

interface AuthState {
  token: string;
  user: CurrentUser | null;
  permissions: string[];
  loading: boolean;
}

export const authState = reactive<AuthState>({
  token: getStoredToken(),
  user: null,
  permissions: [],
  loading: false,
});

export const roleLabelMap: Record<string, string> = {
  admin: "管理员",
  manager: "主管",
  employee: "员工",
  student: "学生",
};

export async function login(username: string, password: string): Promise<void> {
  authState.loading = true;
  try {
    const result = await loginApi({ username, password });
    authState.token = result.access_token;
    authState.user = result.user;
    const permissionResult = await getCurrentPermissions();
    authState.permissions = permissionResult.permissions;
  } finally {
    authState.loading = false;
  }
}

export async function bootstrapAuth(): Promise<void> {
  if (!authState.token || authState.user) {
    return;
  }
  authState.loading = true;
  try {
    authState.user = await getCurrentUser();
    authState.permissions = (await getCurrentPermissions()).permissions;
  } catch {
    logout();
  } finally {
    authState.loading = false;
  }
}

export function logout(): void {
  clearStoredToken();
  authState.token = "";
  authState.user = null;
  authState.permissions = [];
}

export function hasPermission(permission: string): boolean {
  return authState.permissions.includes("*") || authState.permissions.includes(permission);
}
