export interface LeaveRecord {
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

export interface PagedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PsychProfile {
  id: number;
  student_id: number;
  student_name: string | null;
  latest_emotion_tag: string | null;
  emotion_score: number | null;
  risk_level: string;
  last_interaction_time: string | null;
  emotion_summary: string | null;
  create_time: string;
  update_time: string;
}

export interface PsychAlert {
  id: number;
  alert_no: string;
  student_id: number;
  student_name: string | null;
  trigger_reason: string;
  risk_level: string;
  status: string;
  teacher_employee_id: number | null;
  teacher_name: string | null;
  handle_result: string | null;
  close_time: string | null;
  create_time: string;
  update_time: string;
}

export interface LifeSupportFaq {
  id: number;
  category: string | null;
  question: string;
  answer: string;
  keywords: string | null;
}

export interface FaqListResult {
  items: LifeSupportFaq[];
  keyword: string | null;
  total: number;
}

export interface AssistantChatResult {
  answer: string;
  conversation_id: string | null;
}

export interface PsychChatResult {
  reply: string;
  emotion_tag: string;
  emotion_score: number;
  risk_level: string;
  alert_created: boolean;
  assigned_teacher?: string | null;
  degraded?: boolean;
  warning?: string;
  summary?: string;
}

export interface EmotionCheckinResult {
  profile: PsychProfile;
  alert?: PsychAlert | null;
  emotion?: Record<string, unknown>;
}
