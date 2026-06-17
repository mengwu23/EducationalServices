import { createRouter, createWebHistory } from "vue-router";
import LoginView from "@/views/LoginView.vue";
import ForbiddenView from "@/views/ForbiddenView.vue";
import DashboardView from "@/views/DashboardView.vue";
import StudentLeaveView from "@/views/StudentLeaveView.vue";
import StudentPsychView from "@/views/StudentPsychView.vue";
import StudentProgressView from "@/views/StudentProgressView.vue";
import StudentFeedbackView from "@/views/StudentFeedbackView.vue";
import ReportView from "@/views/ReportView.vue";
import CustomerJudgementView from "@/views/CustomerJudgementView.vue";
import EnterpriseQueryView from "@/views/EnterpriseQueryView.vue";
import StudentMyLeaveView from "@/views/StudentMyLeaveView.vue";
import StudentPsychCareView from "@/views/StudentPsychCareView.vue";
import StudentMyFeedbackView from "@/views/StudentMyFeedbackView.vue";
import StudentAssistantView from "@/views/StudentAssistantView.vue";
import AcademicEventView from "@/views/AcademicEventView.vue";
import ServiceCenterView from "@/views/ServiceCenterView.vue";
import PermissionAdminView from "@/views/PermissionAdminView.vue";
import { getNavigationItemByRoute, hasAccessToNavigationItem } from "@/config/navigation";
import { authState, bootstrapAuth } from "@/stores/authStore";

function routeMeta(route: string) {
  return { ...getNavigationItemByRoute(route) };
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/login", component: LoginView, meta: { public: true } },
    { path: "/forbidden", component: ForbiddenView },
    { path: "/dashboard", component: DashboardView, meta: routeMeta("/dashboard") },
    { path: "/students/leaves", component: StudentLeaveView, meta: routeMeta("/students/leaves") },
    { path: "/students/psych", component: StudentPsychView, meta: routeMeta("/students/psych") },
    { path: "/students/progress", component: StudentProgressView, meta: routeMeta("/students/progress") },
    { path: "/students/feedback", component: StudentFeedbackView, meta: routeMeta("/students/feedback") },
    { path: "/reports", component: ReportView, meta: routeMeta("/reports") },
    { path: "/customer-judgement", component: CustomerJudgementView, meta: routeMeta("/customer-judgement") },
    { path: "/business-query", component: EnterpriseQueryView, meta: routeMeta("/business-query") },
    { path: "/student/leaves", component: StudentMyLeaveView, meta: routeMeta("/student/leaves") },
    { path: "/student/psych-care", component: StudentPsychCareView, meta: routeMeta("/student/psych-care") },
    { path: "/student/feedback", component: StudentMyFeedbackView, meta: routeMeta("/student/feedback") },
    { path: "/student/assistant", component: StudentAssistantView, meta: routeMeta("/student/assistant") },
    { path: "/academic-events", component: AcademicEventView, meta: routeMeta("/academic-events") },
    { path: "/service-center", component: ServiceCenterView, meta: routeMeta("/service-center") },
    { path: "/admin/permissions", component: PermissionAdminView, meta: routeMeta("/admin/permissions") },
  ],
});

router.beforeEach(async (to) => {
  if (!to.meta.public) {
    await bootstrapAuth();
    if (!authState.token || !authState.user) {
      return "/login";
    }
    const navigationItem = getNavigationItemByRoute(to.path);
    if (to.path !== "/forbidden" && navigationItem && !hasAccessToNavigationItem(navigationItem, authState.user.role, authState.permissions)) {
      return { path: "/forbidden", query: { from: to.fullPath } };
    }
  }
  if (to.path === "/login" && authState.token) {
    await bootstrapAuth();
    if (authState.user) {
      return "/dashboard";
    }
  }
  return true;
});

export default router;
