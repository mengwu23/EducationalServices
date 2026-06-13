import { request } from "@/api/request";
import type {
  StudentFeedbackCreatePayload,
  StudentFeedbackListParams,
  StudentFeedbackPage,
  StudentFeedbackTicket,
} from "@/types/studentFeedback";

function toQuery(params: StudentFeedbackListParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  return search.toString();
}

export function listStudentFeedbackTickets(params: StudentFeedbackListParams = {}): Promise<StudentFeedbackPage> {
  const query = toQuery({ page: 1, size: 20, ...params });
  return request<StudentFeedbackPage>(`/api/student-feedback-tickets?${query}`);
}

export function createStudentFeedbackTicket(payload: StudentFeedbackCreatePayload): Promise<StudentFeedbackTicket> {
  return request<StudentFeedbackTicket>("/api/student-feedback-tickets", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function classifyStudentFeedbackTicket(ticketId: number): Promise<StudentFeedbackTicket> {
  return request<StudentFeedbackTicket>(`/api/student-feedback-tickets/${ticketId}/classify`, {
    method: "POST",
  });
}

export function assignStudentFeedbackTicket(ticketId: number, handlerEmployeeId: number): Promise<StudentFeedbackTicket> {
  return request<StudentFeedbackTicket>(`/api/student-feedback-tickets/${ticketId}/assign`, {
    method: "POST",
    body: JSON.stringify({ handler_employee_id: handlerEmployeeId }),
  });
}

export function resolveStudentFeedbackTicket(
  ticketId: number,
  solution: string,
  notifyStudent = true,
): Promise<StudentFeedbackTicket> {
  return request<StudentFeedbackTicket>(`/api/student-feedback-tickets/${ticketId}/resolve`, {
    method: "POST",
    body: JSON.stringify({ solution, notify_student: notifyStudent }),
  });
}

export function closeStudentFeedbackTicket(ticketId: number, satisfactionScore?: number): Promise<StudentFeedbackTicket> {
  return request<StudentFeedbackTicket>(`/api/student-feedback-tickets/${ticketId}/close`, {
    method: "POST",
    body: JSON.stringify({ satisfaction_score: satisfactionScore }),
  });
}

export function notifyStudentFeedbackTicket(ticketId: number): Promise<StudentFeedbackTicket> {
  return request<StudentFeedbackTicket>(`/api/student-feedback-tickets/${ticketId}/notify`, {
    method: "POST",
  });
}
