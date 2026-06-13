import { getStoredToken, request } from "@/api/request";
import type {
  AssistantChatResult,
  EmotionCheckinResult,
  FaqListResult,
  LeaveRecord,
  PagedResult,
  PsychAlert,
  PsychChatResult,
  PsychProfile,
} from "@/types/studentAssistant";

async function plainRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(url, { ...options, headers });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(payload?.message || payload?.detail || `请求失败：${response.status}`);
  }
  return payload as T;
}

export function getPendingLeaveCount(): Promise<{ count: number }> {
  return request<{ count: number }>("/api/v1/student-assistant/leaves/pending/count");
}

export function listPendingLeaves(page = 1, pageSize = 10): Promise<PagedResult<LeaveRecord>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<PagedResult<LeaveRecord>>(`/api/v1/student-assistant/leaves/pending?${params.toString()}`);
}

export function createLeave(payload: { leave_type: string; reason: string; start_time: string; end_time: string }): Promise<LeaveRecord> {
  return request<LeaveRecord>("/api/v1/student-assistant/leaves", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listMyLeaves(page = 1, pageSize = 10, status = ""): Promise<PagedResult<LeaveRecord>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (status) params.set("status", status);
  return request<PagedResult<LeaveRecord>>(`/api/v1/student-assistant/leaves?${params.toString()}`);
}

export function cancelLeave(leaveId: number, reason = ""): Promise<LeaveRecord> {
  return request<LeaveRecord>(`/api/v1/student-assistant/leaves/${leaveId}/cancel`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function listApprovalHistory(page = 1, pageSize = 10): Promise<PagedResult<LeaveRecord>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<PagedResult<LeaveRecord>>(`/api/v1/student-assistant/leaves/history?${params.toString()}`);
}

export function approveLeave(leaveId: number): Promise<LeaveRecord> {
  return request<LeaveRecord>(`/api/v1/student-assistant/leaves/${leaveId}/approve`, {
    method: "POST",
  });
}

export function rejectLeave(leaveId: number, comment: string): Promise<LeaveRecord> {
  return request<LeaveRecord>(`/api/v1/student-assistant/leaves/${leaveId}/reject`, {
    method: "POST",
    body: JSON.stringify({ comment }),
  });
}

export function listPsychProfiles(page = 1, pageSize = 10, riskLevel = ""): Promise<PagedResult<PsychProfile>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (riskLevel) {
    params.set("risk_level", riskLevel);
  }
  return request<PagedResult<PsychProfile>>(`/api/v1/student-assistant/psych/profiles?${params.toString()}`);
}

export function getMyPsychProfile(): Promise<PsychProfile> {
  return request<PsychProfile>("/api/v1/student-assistant/psych/profile");
}

export function emotionCheckin(content: string): Promise<EmotionCheckinResult> {
  return request<EmotionCheckinResult>("/api/v1/student-assistant/psych/profile/checkin", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function listMyPsychAlerts(page = 1, pageSize = 10, status = ""): Promise<PagedResult<PsychAlert>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (status) params.set("status", status);
  return request<PagedResult<PsychAlert>>(`/api/v1/student-assistant/psych/alerts?${params.toString()}`);
}

export function getPendingPsychAlertCount(): Promise<{ count: number }> {
  return request<{ count: number }>("/api/v1/student-assistant/psych/alerts/pending/count");
}

export function listPendingPsychAlerts(page = 1, pageSize = 10): Promise<PagedResult<PsychAlert>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<PagedResult<PsychAlert>>(`/api/v1/student-assistant/psych/alerts/pending?${params.toString()}`);
}

export function listPsychAlertHistory(page = 1, pageSize = 10): Promise<PagedResult<PsychAlert>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<PagedResult<PsychAlert>>(`/api/v1/student-assistant/psych/alerts/history?${params.toString()}`);
}

export function handlePsychAlert(alertId: number, action: "process" | "resolve" | "close", handleResult = "") {
  return request<PsychAlert>(`/api/v1/student-assistant/psych/alerts/${alertId}/action`, {
    method: "POST",
    body: JSON.stringify({
      action,
      handle_result: handleResult || undefined,
    }),
  });
}

export function listLifeSupportFaq(keyword = "", limit = 10): Promise<FaqListResult> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (keyword) params.set("keyword", keyword);
  return plainRequest<FaqListResult>(`/api/v1/student-assistant/life-support/faq?${params.toString()}`);
}

export function chatLifeAssistant(query: string): Promise<AssistantChatResult> {
  const params = new URLSearchParams({ query });
  return plainRequest<AssistantChatResult>(`/api/v1/student-assistant/life-support/chat?${params.toString()}`, {
    method: "POST",
  });
}

export function chatPolicyAssistant(query: string): Promise<AssistantChatResult> {
  const params = new URLSearchParams({ query });
  return plainRequest<AssistantChatResult>(`/api/v1/student-assistant/policy/chat?${params.toString()}`, {
    method: "POST",
  });
}

export function chatPsychAssistant(message: string): Promise<PsychChatResult> {
  return plainRequest<PsychChatResult>("/api/v1/student-assistant/psych/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}
