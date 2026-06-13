import { request } from "@/api/request";
import type { AcademicEvent, AcademicEventPage, AcademicEventPayload } from "@/types/academicEvents";

interface AcademicEventParams {
  student_id?: number;
  event_type?: string;
  status?: string;
  keyword?: string;
  page?: number;
  size?: number;
}

function toQuery(params: AcademicEventParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  return search.toString();
}

export function listAcademicEvents(params: AcademicEventParams = {}): Promise<AcademicEventPage> {
  const query = toQuery({ page: 1, size: 20, ...params });
  return request<AcademicEventPage>(`/api/academic-events?${query}`);
}

export function listApproachingDeadlines(withinDays = 7): Promise<AcademicEventPage> {
  const query = new URLSearchParams({ within_days: String(withinDays), include_overdue: "true" });
  return request<AcademicEventPage>(`/api/academic-events/approaching-deadlines?${query.toString()}`);
}

export function createAcademicEvent(payload: AcademicEventPayload): Promise<AcademicEvent> {
  return request<AcademicEvent>("/api/academic-events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function completeAcademicEvent(eventId: number): Promise<AcademicEvent> {
  return request<AcademicEvent>(`/api/academic-events/${eventId}/complete`, {
    method: "POST",
  });
}

export function cancelAcademicEvent(eventId: number): Promise<AcademicEvent> {
  return request<AcademicEvent>(`/api/academic-events/${eventId}/cancel`, {
    method: "POST",
  });
}
