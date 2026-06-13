export type FeedbackTicketType = "complaint" | "suggestion" | "consult" | string;
export type FeedbackPriorityLevel = "normal" | "urgent" | "severe" | string;
export type FeedbackTicketStatus = "pending" | "processing" | "resolved" | "closed" | string;

export interface StudentFeedbackTicket {
  id: number;
  ticket_no: string;
  student_id: number;
  ticket_type: FeedbackTicketType;
  category: string | null;
  title: string;
  content_summary: string | null;
  detail: string;
  priority_level: FeedbackPriorityLevel;
  status: FeedbackTicketStatus;
  handler_employee_id: number | null;
  solution: string | null;
  satisfaction_score: number | null;
  is_notified: number;
  close_time: string | null;
  create_time: string;
  update_time: string;
}

export interface StudentFeedbackPage {
  items: StudentFeedbackTicket[];
  total: number;
  page: number;
  size: number;
}

export interface StudentFeedbackListParams {
  student_id?: number;
  status?: string;
  handler_employee_id?: number;
  category?: string;
  priority_level?: string;
  keyword?: string;
  page?: number;
  size?: number;
}

export interface StudentFeedbackCreatePayload {
  student_id: number;
  ticket_type: FeedbackTicketType;
  category?: string;
  title: string;
  content_summary?: string;
  detail: string;
  priority_level: FeedbackPriorityLevel;
  handler_employee_id?: number;
}

export interface StudentFeedbackMyCreatePayload {
  ticket_type: FeedbackTicketType;
  category?: string;
  title: string;
  content_summary?: string;
  detail: string;
  priority_level: FeedbackPriorityLevel;
}
