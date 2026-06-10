from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.common.enums import ExportType
from app.core.config import Settings
from app.models.report import AiReport


class ReportExportService:
    def __init__(self, settings: Settings):
        self.settings = settings

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
        self._write_minimal_docx(file_path, report)
        return file_name, str(file_path)

    def _export_pdf(self, report: AiReport) -> tuple[str, str]:
        converter = self.settings.report_pdf_converter_path.strip()
        if not converter:
            raise RuntimeError("当前环境未配置 PDF 转换器，无法生成 PDF")
        raise RuntimeError("PDF 转换器尚未完成本地联调")

    def _write_minimal_docx(self, file_path: Path, report: AiReport) -> None:
        content = report.content_json
        paragraphs = [content.get("title", report.title), content.get("summary", "")]
        for section in content.get("sections", []):
            paragraphs.append(section.get("heading", ""))
            paragraphs.append(section.get("content", ""))
        document_xml = self._document_xml(paragraphs)
        with ZipFile(file_path, "w", ZIP_DEFLATED) as docx:
            docx.writestr("[Content_Types].xml", self._content_types_xml())
            docx.writestr("_rels/.rels", self._rels_xml())
            docx.writestr("word/document.xml", document_xml)

    def _document_xml(self, paragraphs: list[str]) -> str:
        body = "".join(f"<w:p><w:r><w:t>{self._escape_xml(text)}</w:t></w:r></w:p>" for text in paragraphs)
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{body}</w:body>"
            "</w:document>"
        )

    def _content_types_xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>"
        )

    def _rels_xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>"
        )

    def _escape_xml(self, value: object) -> str:
        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )
