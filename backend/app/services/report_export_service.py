from pathlib import Path

from xhtml2pdf import pisa

from app.common.enums import ExportType
from app.core.config import Settings
from app.models.report import AiReport
from app.services.report_template_service import ReportTemplateService


class ReportExportService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.template_service = ReportTemplateService()

    def export(self, report: AiReport, export_type: str) -> tuple[str, str]:
        if export_type == ExportType.WORD:
            return self._export_word(report)
        if export_type == ExportType.PDF:
            return self._export_pdf(report)
        raise ValueError("不支持的导出类型")

    def _export_word(self, report: AiReport) -> tuple[str, str]:
        export_dir = self.settings.export_dir_path
        export_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{report.report_no}.docx"
        file_path = export_dir / file_name
        self.template_service.write_docx(report, file_path)
        return file_name, str(file_path)

    def _export_pdf(self, report: AiReport) -> tuple[str, str]:
        export_dir = self.settings.export_dir_path
        export_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{report.report_no}.pdf"
        file_path = export_dir / file_name
        html = self.template_service.render_html(report)
        with Path(file_path).open("wb") as pdf_file:
            result = pisa.CreatePDF(html, dest=pdf_file, encoding="UTF-8")
        if result.err:
            raise RuntimeError("PDF 模板渲染失败")
        return file_name, str(file_path)
