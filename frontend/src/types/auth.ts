export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  trace_id: string;
}

export interface CurrentUser {
  id: number;
  role: "admin" | "manager" | "employee" | "student" | string;
  username: string | null;
  real_name: string | null;
  user_type: string | null;
  role_code: string | null;
  employee_id: number | null;
  student_id: number | null;
  department_id: number | null;
  permissions: string[];
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: CurrentUser;
}

export interface PermissionResult {
  role: string;
  permissions: string[];
}
