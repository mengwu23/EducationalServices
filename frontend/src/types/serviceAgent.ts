export interface ServiceAgentMessageResponse {
  visitor_id: string;
  conversation_id: string | null;
  visitor_message: string;
  reply_text: string;
  intent: string | null;
  suggested_actions: Array<Record<string, unknown>>;
  references: Array<Record<string, unknown>>;
  trace_id: string | null;
}

export interface ServiceFaqItem {
  id?: number;
  question?: string;
  answer?: string;
  category?: string | null;
  keywords?: string | null;
  [key: string]: unknown;
}

export interface ServiceProjectItem {
  id?: number;
  project_name?: string;
  project_type?: string | null;
  target_country?: string | null;
  education_level?: string | null;
  [key: string]: unknown;
}

export interface ServiceEventItem {
  id: number;
  event_name?: string;
  title?: string;
  event_type?: string | null;
  status?: string | null;
  start_time?: string | null;
  [key: string]: unknown;
}
