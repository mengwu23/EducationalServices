from datetime import date
from pathlib import Path
from uuid import uuid4

from docx import Document

from backend.app.common.enums import ExportType
from backend.app.core.config import Settings
from backend.app.models.report import AiReport
from backend.app.services.report_export_service import ReportExportService


def build_report() -> AiReport:
    return AiReport(
        id=1,
        report_no="RP-TEMPLATE",
        report_type="complaint_weekly",
        title="投诉处理周报",
        status="published",
        content_json={
            "title": "投诉处理周报",
            "summary": "本周投诉处理整体平稳。",
            "sections": [
                {
                    "heading": "投诉概览",
                    "content": "本周共处理投诉 2 条。",
                    "metrics": [
                        {"name": "open", "value": 1},
                        {"name": "closed", "value": 1},
                    ],
                }
            ],
            "risks": ["仍有未关闭投诉需要跟进"],
            "recommendations": ["下周优先关闭超时工单"],
            "source_refs": ["student_feedback_ticket"],
        },
        source_draft_id=1,
        date_start=date(2026, 6, 1),
        date_end=date(2026, 6, 7),
        department_id=1,
        created_by=1,
    )


def build_export_dir() -> Path:
    return Path("storage/test_reports") / uuid4().hex


def test_export_word_uses_report_template():
    export_dir = build_export_dir()
    service = ReportExportService(Settings(report_export_dir=str(export_dir)))
    report = build_report()

    file_name, file_path = service.export(report, ExportType.WORD)

    assert file_name == "RP-TEMPLATE.docx"
    assert Path(file_path).exists()
    document = Document(file_path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "投诉处理周报" in text
    assert "本周投诉处理整体平稳。" in text
    assert "投诉概览" in text
    assert "open：1" in text
    assert "仍有未关闭投诉需要跟进" in text


def test_export_pdf_uses_report_template():
    export_dir = build_export_dir()
    service = ReportExportService(Settings(report_export_dir=str(export_dir)))
    report = build_report()

    file_name, file_path = service.export(report, ExportType.PDF)

    assert file_name == "RP-TEMPLATE.pdf"
    pdf_path = Path(file_path)
    assert pdf_path.exists()
    assert pdf_path.read_bytes().startswith(b"%PDF")
