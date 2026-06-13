import { createRouter, createWebHistory } from "vue-router";
import LoginView from "@/views/LoginView.vue";
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
import { authState, bootstrapAuth } from "@/stores/authStore";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/login", component: LoginView, meta: { public: true } },
    { path: "/dashboard", component: DashboardView },
    { path: "/students/leaves", component: StudentLeaveView },
    { path: "/students/psych", component: StudentPsychView },
    { path: "/students/progress", component: StudentProgressView },
    { path: "/students/feedback", component: StudentFeedbackView },
    { path: "/reports", component: ReportView },
    { path: "/customer-judgement", component: CustomerJudgementView },
    { path: "/business-query", component: EnterpriseQueryView },
    { path: "/student/leaves", component: StudentMyLeaveView },
    { path: "/student/psych-care", component: StudentPsychCareView },
    { path: "/student/feedback", component: StudentMyFeedbackView },
    { path: "/student/assistant", component: StudentAssistantView },
    { path: "/academic-events", component: AcademicEventView },
    { path: "/service-center", component: ServiceCenterView },
  ],
});

router.beforeEach(async (to) => {
  if (!to.meta.public) {
    await bootstrapAuth();
    if (!authState.token || !authState.user) {
      return "/login";
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
