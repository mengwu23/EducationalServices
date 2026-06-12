export type ReportType =
  | "complaint_weekly"
  | "customer_operation"
  | "employee_daily_summary"
  | "employee_weekly_summary"
  | "student_psych_weekly"
  | string;

export type DraftStatus =
  | "generating"
  | "pending_confirm"
  | "confirmed"
  | "rejected"
  | "generation_failed"
  | "pending_second_confirm"
  | string;

export type ReportStatus = "confirmed" | "published" | string;
export type ExportType = "word" | "pdf";
export type ExportStatus = "success" | "fail" | string;

export interface ReportSection {
  heading: string;
  content: string;
  metrics?: Array<Record<string, unknown>>;
}

export interface ReportContent {
  title?: string;
  summary?: string;
  sections?: ReportSection[];
  risks?: string[];
  recommendations?: string[];
  source_refs?: string[];
  report_type?: ReportType;
  filters?: {
    date_start?: string;
    date_end?: string;
    department_id?: number | null;
    owner_user_id?: number | null;
  };
  source_data?: Record<string, unknown>;
  error_message?: string;
  [key: string]: unknown;
}

export interface ReportDraft {
  id: number;
  draft_no: string;
  status: DraftStatus;
  content_json: ReportContent;
  trace_id: string | null;
}

export interface AiReport {
  id: number;
  report_no: string;
  report_type: ReportType;
  title: string;
  status: ReportStatus;
  content_json: ReportContent;
  source_draft_id: number;
  date_start: string;
  date_end: string;
  department_id: number | null;
  created_by: number | null;
  published_by: number | null;
  published_time: string | null;
}

export interface ReportExportRecord {
  id: number;
  report_id: number;
  export_type: ExportType | string;
  file_name: string;
  file_path: string;
  status: ExportStatus;
  error_message: string | null;
}

export interface ReportGenerateDraftPayload {
  report_type: ReportType;
  date_start: string;
  date_end: string;
  department_id?: number | null;
  owner_user_id?: number | null;
  trace_id?: string | null;
}
