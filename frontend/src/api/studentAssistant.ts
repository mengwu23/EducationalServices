import { request } from "@/api/request";
import type { LeaveRecord, PagedResult, PsychAlert, PsychProfile } from "@/types/studentAssistant";

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
