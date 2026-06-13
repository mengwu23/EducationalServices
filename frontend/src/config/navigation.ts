export interface NavigationItem {
  key: string;
  label: string;
  route: string;
  roles: string[];
  permission?: string;
  description?: string;
  count?: string;
  tone?: string;
}

export const navigationItems: NavigationItem[] = [
  {
    key: "dashboard",
    label: "工作台",
    route: "/dashboard",
    roles: ["admin", "manager", "employee", "student"],
  },
  {
    key: "student-leaves",
    label: "我的请假",
    route: "/student/leaves",
    roles: ["student"],
    permission: "student_leave:own",
    description: "学生提交请假、查看审批进度和取消待审批申请",
    count: "自助",
    tone: "amber",
  },
  {
    key: "student-psych-care",
    label: "心理关怀",
    route: "/student/psych-care",
    roles: ["student"],
    permission: "student_psych:own",
    description: "查看个人心理画像、提交情绪打卡和获取心理支持",
    count: "关怀",
    tone: "green",
  },
  {
    key: "student-feedback",
    label: "我的反馈",
    route: "/student/feedback",
    roles: ["student"],
    description: "提交服务反馈并查看个人工单处理进度",
    count: "反馈",
    tone: "clay",
  },
  {
    key: "student-assistant",
    label: "学生助手",
    route: "/student/assistant",
    roles: ["student"],
    description: "生活支持、留学政策咨询和心理支持对话",
    count: "AI",
    tone: "green",
  },
  {
    key: "leave-approval",
    label: "请假审批",
    route: "/students/leaves",
    roles: ["admin", "manager", "employee"],
    permission: "student_leave:read",
    description: "学生请假申请、审批历史与待处理统计",
    count: "12",
    tone: "amber",
  },
  {
    key: "psych-alert",
    label: "心理预警",
    route: "/students/psych",
    roles: ["admin", "manager", "employee"],
    permission: "student_psych:read",
    description: "心理画像、风险预警、处理闭环",
    count: "6",
    tone: "red",
  },
  {
    key: "academic-events",
    label: "学业事件",
    route: "/academic-events",
    roles: ["admin", "manager", "employee"],
    description: "考试、论文、课程 Deadline 与提醒管理",
    count: "DDL",
    tone: "sand",
  },
  {
    key: "application-progress",
    label: "申请进度",
    route: "/students/progress",
    roles: ["admin", "manager", "employee", "student"],
    description: "文书、院校、签证、Offer 等关键节点追踪",
    count: "32",
    tone: "sand",
  },
  {
    key: "feedback",
    label: "反馈工单",
    route: "/students/feedback",
    roles: ["admin", "manager", "employee"],
    permission: "enterprise_operation:execute",
    description: "投诉、建议、咨询的分派处理与学生通知",
    count: "11",
    tone: "clay",
  },
  {
    key: "reports",
    label: "智能报告",
    route: "/reports",
    roles: ["admin", "manager", "employee"],
    permission: "report:read",
    description: "报告生成、草稿确认、发布与导出",
    count: "18",
    tone: "green",
  },
  {
    key: "customer-judgement",
    label: "客户研判",
    route: "/customer-judgement",
    roles: ["admin", "manager", "employee"],
    permission: "customer_judgement:read",
    description: "客户资料分析、匹配等级与跟进建议",
    count: "24",
    tone: "clay",
  },
  {
    key: "enterprise-query",
    label: "企业查询",
    route: "/business-query",
    roles: ["admin", "manager", "employee"],
    permission: "enterprise_operation:execute",
    description: "线索、日报、组织、学生与待办汇总",
    count: "9",
    tone: "sand",
  },
  {
    key: "service-center",
    label: "客服中心",
    route: "/service-center",
    roles: ["admin", "manager", "employee"],
    description: "访客咨询、FAQ、项目推荐和活动报名",
    count: "客",
    tone: "green",
  },
];

export function getNavigationItemByRoute(route: string): NavigationItem | undefined {
  return navigationItems.find((item) => item.route === route);
}

export function hasAccessToNavigationItem(
  item: NavigationItem,
  role: string,
  permissions: string[],
): boolean {
  const roleMatched = item.roles.includes(role);
  const permissionMatched = !item.permission || permissions.includes("*") || permissions.includes(item.permission);
  return roleMatched && permissionMatched;
}

export function getVisibleNavigationItems(role: string, permissions: string[]): NavigationItem[] {
  return navigationItems.filter((item) => hasAccessToNavigationItem(item, role, permissions));
}
