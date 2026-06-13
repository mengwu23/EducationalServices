export interface ProgressRecord {
  id: number;
  student_id: number;
  student_name: string | null;
  progress_stage: string;
  progress_stage_label: string | null;
  target_country: string | null;
  school_name: string | null;
  program_name: string | null;
  progress_status: string;
  progress_status_label: string | null;
  progress_desc: string | null;
  handler_employee_id: number | null;
  handler_name: string | null;
  expected_finish_time: string | null;
  crm_record_id: string | null;
  crm_sync_status: string | null;
  crm_last_sync_time: string | null;
  create_time: string;
  update_time: string;
}

export interface ProgressPagedResult {
  items: ProgressRecord[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProgressTimelineItem {
  id: number;
  stage: string;
  stage_label: string;
  status: string;
  status_label: string;
  desc: string | null;
  handler_name: string | null;
  school_name: string | null;
  expected_finish_time: string | null;
  update_time: string;
}

export interface ProgressTimeline {
  student_id: number;
  student_name: string;
  stages: ProgressTimelineItem[];
  summary: string;
}

export interface ProgressStageReference {
  stages: Record<string, string>;
  statuses: Record<string, string>;
}

export interface ProgressUpdatePayload {
  progress_stage?: string;
  target_country?: string;
  school_name?: string;
  program_name?: string;
  progress_status?: string;
  progress_desc?: string;
  handler_employee_id?: number;
  expected_finish_time?: string;
}
