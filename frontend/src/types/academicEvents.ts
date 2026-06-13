export interface AcademicEvent {
  id: number;
  student_id: number | null;
  event_type: string;
  title: string;
  event_desc: string | null;
  course_name: string | null;
  deadline_time: string;
  reminder_time: string | null;
  status: string;
  create_time: string;
  update_time: string;
}

export interface AcademicEventPage {
  items: AcademicEvent[];
  total: number;
  page: number;
  size: number;
}

export interface AcademicEventPayload {
  student_id?: number | null;
  event_type: string;
  title: string;
  event_desc?: string | null;
  course_name?: string | null;
  deadline_time: string;
  reminder_time?: string | null;
  status?: string;
}
