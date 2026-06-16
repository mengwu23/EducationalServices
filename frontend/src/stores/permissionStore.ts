import { reactive } from "vue";

export const permissionCatalog = [
  { code: "report:read", label: "查看报告", group: "智能报告" },
  { code: "report:generate", label: "生成报告", group: "智能报告" },
  { code: "report:review", label: "审核报告", group: "智能报告" },
  { code: "report:export", label: "导出报告", group: "智能报告" },
  { code: "customer_judgement:read", label: "查看客户研判", group: "客户管理" },
  { code: "customer_judgement:write", label: "执行客户研判", group: "客户管理" },
  { code: "enterprise_operation:execute", label: "企业查询与办理", group: "企业查询" },
  { code: "student_leave:read", label: "查看请假", group: "学生服务" },
  { code: "student_leave:approve", label: "审批请假", group: "学生服务" },
  { code: "student_psych:read", label: "查看心理预警", group: "学生服务" },
  { code: "student_psych:manage", label: "处理心理预警", group: "学生服务" },
  { code: "application_progress:read", label: "查看申请进度", group: "申请进度" },
  { code: "application_progress:write", label: "更新申请进度", group: "申请进度" },
  { code: "student_feedback:read", label: "查看反馈工单", group: "反馈工单" },
  { code: "student_feedback:manage", label: "处理反馈工单", group: "反馈工单" },
  { code: "student_leave:own", label: "学生查看本人请假", group: "学生端" },
  { code: "student_psych:own", label: "学生心理关怀", group: "学生端" },
  { code: "application_progress:own", label: "学生查看本人进度", group: "学生端" },
  { code: "student_feedback:own", label: "学生查看本人反馈", group: "学生端" },
];

export const rolePermissionDefaults: Record<string, string[]> = {
  admin: ["*"],
  manager: [
    "report:read",
    "report:generate",
    "report:review",
    "report:export",
    "customer_judgement:read",
    "customer_judgement:write",
    "enterprise_operation:execute",
    "student_leave:read",
    "student_leave:approve",
    "student_psych:read",
    "student_psych:manage",
    "application_progress:read",
    "application_progress:write",
    "student_feedback:read",
    "student_feedback:manage",
  ],
  employee: [
    "report:read",
    "report:generate",
    "report:export",
    "customer_judgement:read",
    "customer_judgement:write",
    "enterprise_operation:execute",
    "student_leave:read",
    "student_leave:approve",
    "student_psych:read",
    "student_psych:manage",
    "application_progress:read",
    "application_progress:write",
    "student_feedback:read",
    "student_feedback:manage",
  ],
  student: ["student_leave:own", "student_psych:own", "application_progress:own", "student_feedback:own"],
};

const STORAGE_KEY = "education_service_role_permissions";

export const permissionState = reactive({
  rolePermissions: loadRolePermissions(),
});

export function getEffectivePermissions(role: string, fallback: string[] = []): string[] {
  if (!role) return fallback;
  return permissionState.rolePermissions[role] || fallback;
}

export function setRolePermissions(role: string, permissions: string[]): void {
  permissionState.rolePermissions[role] = Array.from(new Set(permissions));
  persistRolePermissions();
}

export function resetRolePermissions(): void {
  permissionState.rolePermissions = cloneDefaults();
  persistRolePermissions();
}

function loadRolePermissions(): Record<string, string[]> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return cloneDefaults();
    return { ...cloneDefaults(), ...JSON.parse(raw) };
  } catch {
    return cloneDefaults();
  }
}

function persistRolePermissions(): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(permissionState.rolePermissions));
}

function cloneDefaults(): Record<string, string[]> {
  return Object.fromEntries(Object.entries(rolePermissionDefaults).map(([role, permissions]) => [role, [...permissions]]));
}
