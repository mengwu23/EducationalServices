import { request } from "@/api/request";
import type {
  EnterprisePageResult,
  LeadItem,
  Nl2SqlResult,
  OnboardingGuideResult,
  OperationResponse,
  StatisticsSummaryResult,
  StudentProfileItem,
  TodoSummaryResult,
} from "@/types/enterpriseAssistant";

interface SearchParams {
  [key: string]: string | number | null | undefined;
}

function toQuery(params: SearchParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  return search.toString();
}

export function searchLeads(params: SearchParams = {}): Promise<EnterprisePageResult<LeadItem>> {
  const query = toQuery({ page: 1, page_size: 10, ...params });
  return request<EnterprisePageResult<LeadItem>>(`/enterprise/api/v1/enterprise-query/leads/search?${query}`);
}

export function searchStudents(params: SearchParams = {}): Promise<EnterprisePageResult<StudentProfileItem>> {
  const query = toQuery({ page: 1, page_size: 10, ...params });
  return request<EnterprisePageResult<StudentProfileItem>>(`/enterprise/api/v1/enterprise-query/students/search?${query}`);
}

export function summarizeTodos(staleLeadDays = 3, detailLimit = 20): Promise<TodoSummaryResult> {
  const query = toQuery({ stale_lead_days: staleLeadDays, detail_limit: detailLimit });
  return request<TodoSummaryResult>(`/enterprise/api/v1/enterprise-query/todos/summary?${query}`);
}

export function summarizeStatistics(params: SearchParams = {}): Promise<StatisticsSummaryResult> {
  const query = toQuery({ detail_limit: 20, ...params });
  return request<StatisticsSummaryResult>(`/enterprise/api/v1/enterprise-query/statistics/summary?${query}`);
}

export function queryNl2Sql(queryText: string): Promise<Nl2SqlResult> {
  const query = toQuery({ query: queryText });
  return request<Nl2SqlResult>(`/enterprise/api/v1/enterprise-query/nl2sql/query?${query}`, {
    method: "POST",
  });
}

export function queryOnboardingGuide(question: string): Promise<OnboardingGuideResult> {
  const query = toQuery({ question });
  return request<OnboardingGuideResult>(`/enterprise/api/v1/enterprise-query/onboarding/guide?${query}`);
}

export function executeEnterpriseOperation(query: string, draftId?: number | null): Promise<OperationResponse> {
  return request<OperationResponse>("/enterprise/api/v1/enterprise-operation/execute", {
    method: "POST",
    body: JSON.stringify({ query, draft_id: draftId || undefined }),
  });
}

export function confirmEnterpriseOperation(draftId: number, action: "confirm" | "reject", rejectReason = ""): Promise<OperationResponse> {
  return request<OperationResponse>("/enterprise/api/v1/enterprise-operation/confirm", {
    method: "POST",
    body: JSON.stringify({ draft_id: draftId, action, reject_reason: rejectReason || undefined }),
  });
}
