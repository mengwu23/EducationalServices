import { request } from "@/api/request";
import type { ServiceAgentMessageResponse, ServiceEventItem, ServiceFaqItem, ServiceProjectItem } from "@/types/serviceAgent";

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

export function sendServiceMessage(message: string, conversationId?: string | null): Promise<ServiceAgentMessageResponse> {
  return request<ServiceAgentMessageResponse>("/api/messages", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId || undefined }),
  });
}

export function searchServiceFaq(keyword = "", limit = 5): Promise<ServiceFaqItem[]> {
  const query = toQuery({ keyword, limit });
  return request<ServiceFaqItem[]>(`/api/faqs?${query}`);
}

export function searchServiceProjects(params: SearchParams = {}): Promise<ServiceProjectItem[]> {
  const query = toQuery({ limit: 6, ...params });
  return request<ServiceProjectItem[]>(`/api/projects?${query}`);
}

export function listServiceEvents(params: SearchParams = {}): Promise<ServiceEventItem[]> {
  const query = toQuery({ limit: 10, status: "open", ...params });
  return request<ServiceEventItem[]>(`/api/events?${query}`);
}

export function createActivitySignup(payload: {
  event_id: number;
  visitor_name: string;
  visitor_phone?: string;
  remark?: string;
  conversation_id?: string | null;
}): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>("/api/activity-signups", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
