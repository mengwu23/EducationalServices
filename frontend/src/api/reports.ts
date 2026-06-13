import { request } from "@/api/request";
import type {
  AiReport,
  ExportType,
  ReportDraft,
  ReportExportRecord,
  ReportGenerateDraftPayload,
} from "@/types/reports";

export function generateReportDraft(payload: ReportGenerateDraftPayload): Promise<ReportDraft> {
  return request<ReportDraft>("/api/v1/reports/generate-draft", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listReportDrafts(): Promise<ReportDraft[]> {
  return request<ReportDraft[]>("/api/v1/reports/drafts");
}

export function confirmReportDraft(draftId: number): Promise<AiReport> {
  return request<AiReport>(`/api/v1/reports/drafts/${draftId}/confirm`, {
    method: "POST",
  });
}

export function rejectReportDraft(draftId: number, reason: string): Promise<ReportDraft> {
  return request<ReportDraft>(`/api/v1/reports/drafts/${draftId}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function listReports(): Promise<AiReport[]> {
  return request<AiReport[]>("/api/v1/reports");
}

export function publishReport(reportId: number): Promise<AiReport> {
  return request<AiReport>(`/api/v1/reports/${reportId}/publish`, {
    method: "POST",
  });
}

export function exportReport(reportId: number, exportType: ExportType): Promise<ReportExportRecord> {
  return request<ReportExportRecord>(`/api/v1/reports/${reportId}/exports`, {
    method: "POST",
    body: JSON.stringify({ export_type: exportType }),
  });
}

export function listReportExports(reportId: number): Promise<ReportExportRecord[]> {
  return request<ReportExportRecord[]>(`/api/v1/reports/${reportId}/exports`);
}
