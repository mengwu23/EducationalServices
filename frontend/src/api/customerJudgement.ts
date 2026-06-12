import { request } from "@/api/request";
import type {
  CustomerAnalyzePayload,
  JudgementListParams,
  JudgementPage,
  JudgementRecordDetail,
} from "@/types/customerJudgement";

function toQuery(params: JudgementListParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  return search.toString();
}

export function listCustomerJudgements(params: JudgementListParams = {}): Promise<JudgementPage> {
  const query = toQuery({ page: 1, page_size: 20, ...params });
  return request<JudgementPage>(`/api/v1/customer-judgement/records?${query}`);
}

export function getCustomerJudgement(recordId: number): Promise<JudgementRecordDetail> {
  return request<JudgementRecordDetail>(`/api/v1/customer-judgement/records/${recordId}`);
}

export function analyzeCustomer(payload: CustomerAnalyzePayload): Promise<JudgementRecordDetail | { batch: boolean; total_customers: number; records: JudgementRecordDetail[] }> {
  const form = new FormData();
  form.set("text", payload.text);
  if (payload.sys_query) form.set("sys_query", payload.sys_query);
  if (payload.lead_id) form.set("lead_id", String(payload.lead_id));
  if (payload.target_product) form.set("target_product", payload.target_product);
  payload.files?.forEach((file) => form.append("files", file));
  return request<JudgementRecordDetail | { batch: boolean; total_customers: number; records: JudgementRecordDetail[] }>(
    "/api/v1/customer-judgement/analyze",
    {
      method: "POST",
      body: form,
    },
  );
}
