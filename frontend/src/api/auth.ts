import { request, setStoredToken } from "@/api/request";
import type { CurrentUser, LoginPayload, LoginResult, PermissionResult } from "@/types/auth";

export async function login(payload: LoginPayload): Promise<LoginResult> {
  const result = await request<LoginResult>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setStoredToken(result.access_token);
  return result;
}

export function getCurrentUser(): Promise<CurrentUser> {
  return request<CurrentUser>("/api/auth/me");
}

export function getCurrentPermissions(): Promise<PermissionResult> {
  return request<PermissionResult>("/api/auth/permissions");
}
