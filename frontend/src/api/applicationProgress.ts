import { request } from "@/api/request";
import type {
  ProgressPagedResult,
  ProgressRecord,
  ProgressStageReference,
  ProgressTimeline,
  ProgressUpdatePayload,
} from "@/types/applicationProgress";

interface ProgressListParams {
  page?: number;
  page_size?: number;
  student_id?: number;
  progress_stage?: string;
  progress_status?: string;
  handler_employee_id?: number;
}

function toQuery(params: ProgressListParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  return search.toString();
}

export function listApplicationProgress(params: ProgressListParams = {}): Promise<ProgressPagedResult> {
  const query = toQuery({ page: 1, page_size: 20, ...params });
  return request<ProgressPagedResult>(`/api/application-progress?${query}`);
}

export function listMyApplicationProgress(params: ProgressListParams & { student_user_id: number }): Promise<ProgressPagedResult> {
  const query = toQuery({ page: 1, page_size: 20, ...params });
  return request<ProgressPagedResult>(`/api/application-progress/my-progress?${query}`);
}

export function getMyApplicationTimeline(studentUserId: number): Promise<ProgressTimeline> {
  const query = new URLSearchParams({ student_user_id: String(studentUserId) });
  return request<ProgressTimeline>(`/api/application-progress/my-progress/timeline?${query.toString()}`);
}

export function getApplicationProgressStages(): Promise<ProgressStageReference> {
  return request<ProgressStageReference>("/api/application-progress/stages");
}

export function updateApplicationProgress(progressId: number, payload: ProgressUpdatePayload): Promise<ProgressRecord> {
  return request<ProgressRecord>(`/api/application-progress/${progressId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
