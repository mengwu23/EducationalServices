export interface EnterprisePageResult<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface SummaryBlock {
  text: string;
  metrics: Record<string, unknown>;
}

export interface LeadItem {
  id: number;
  lead_no: string;
  customer_name: string;
  phone: string | null;
  wechat_no: string | null;
  email: string | null;
  source_channel: string | null;
  education_level: string | null;
  school_name: string | null;
  major: string | null;
  current_grade: string | null;
  target_country: string | null;
  target_program: string | null;
  budget_range: string | null;
  background_info: string | null;
  follow_up_history: string | null;
  latest_follow_up_summary: string | null;
  status: string;
  owner_employee_id: number | null;
  owner_name: string | null;
  last_follow_up_time: string | null;
  lost_reason: string | null;
  signed_time: string | null;
  create_time: string;
  update_time: string;
}

export interface StudentProfileItem {
  id: number;
  user_id: number | null;
  student_no: string | null;
  student_name: string;
  phone: string | null;
  email: string | null;
  current_school: string | null;
  current_grade: string | null;
  target_country: string | null;
  target_program: string | null;
  counselor_employee_id: number | null;
  teacher_employee_id: number | null;
  status: string;
  create_time: string;
  update_time: string;
}

export interface DailyReportItem {
  id: number;
  employee_id: number;
  employee_name: string | null;
  department_id: number | null;
  department_name: string | null;
  report_date: string;
  raw_content: string;
  summary: string | null;
  key_progress: string | null;
  risks: string | null;
  tomorrow_plan: string | null;
  report_status: string;
  create_time: string;
  update_time: string;
}

export interface StudentLeaveItem {
  id: number;
  request_no: string;
  student_id: number;
  student_name: string | null;
  leave_type: string;
  reason: string;
  start_time: string;
  end_time: string;
  status: string;
  approver_employee_id: number | null;
  approver_name: string | null;
  approval_comment: string | null;
  approve_time: string | null;
  create_time: string;
  update_time: string;
}

export interface StudentFeedbackItem {
  id: number;
  ticket_no: string;
  student_id: number;
  student_name: string | null;
  ticket_type: string;
  category: string | null;
  title: string;
  content_summary: string | null;
  detail: string | null;
  priority_level: string;
  status: string;
  handler_employee_id: number | null;
  handler_name: string | null;
  solution: string | null;
  satisfaction_score: number | null;
  is_notified: number;
  close_time: string | null;
  create_time: string;
  update_time: string;
}

export interface TodoSummaryResult {
  summary: SummaryBlock;
  pending_leaves: StudentLeaveItem[];
  feedback_tickets: StudentFeedbackItem[];
  stale_leads: LeadItem[];
}

export interface StatisticsSummaryResult {
  summary: SummaryBlock;
  lead_count_by_status: Record<string, number>;
  lead_count_by_country: Record<string, number>;
  daily_report_count: number;
  pending_leave_count: number;
  pending_feedback_count: number;
  leads: LeadItem[];
  daily_reports: DailyReportItem[];
  pending_leaves: StudentLeaveItem[];
  pending_feedback_tickets: StudentFeedbackItem[];
}

export interface Nl2SqlResult {
  query?: string;
  sql?: string;
  columns?: string[];
  rows?: Array<Record<string, unknown> | unknown[]>;
  row_count?: number;
  summary?: string;
  error?: string;
  [key: string]: unknown;
}

export interface OnboardingGuideResult {
  status: string;
  message: string;
  question: string;
  category: string | null;
  answer: string | null;
  conversation_id: string | null;
  message_id: string | null;
  metadata: Record<string, unknown>;
}

export interface OperationFieldItem {
  key: string;
  label: string;
  value: unknown;
  required: boolean;
  editable: boolean;
}

export interface OperationConfirmationCard {
  title: string;
  intent: string;
  fields: OperationFieldItem[];
  summary: string | null;
}

export interface MissingFieldItem {
  key: string;
  label: string;
  question: string;
}

export interface CandidateItem {
  id: number;
  label: string;
  description: string | null;
}

export interface OperationResponse {
  status: string;
  message: string;
  draft_id: number | null;
  intent: string | null;
  confirmation_card: OperationConfirmationCard | null;
  missing_fields: MissingFieldItem[];
  candidates: CandidateItem[];
  selection_type: string | null;
  question: string | null;
  conversation_id: string | null;
  error: string | null;
}
