"""执行报告模块全链路验收并生成 Markdown 结果。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy import create_engine, text


REPORT_CASES: list[dict[str, Any]] = [
    {
        "name": "投诉处理周报",
        "report_type": "complaint_weekly",
        "payload": {
            "report_type": "complaint_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 10,
            "trace_id": "acceptance-mock-complaint-weekly",
        },
    },
    {
        "name": "客户经营分析报告",
        "report_type": "customer_operation",
        "payload": {
            "report_type": "customer_operation",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 10,
            "owner_user_id": 102,
            "trace_id": "acceptance-mock-customer-operation",
        },
    },
    {
        "name": "员工日报汇总报告（日）",
        "report_type": "employee_daily_summary",
        "payload": {
            "report_type": "employee_daily_summary",
            "date_start": "2026-06-02",
            "date_end": "2026-06-02",
            "department_id": 10,
            "trace_id": "acceptance-mock-employee-daily",
        },
    },
    {
        "name": "员工日报汇总报告（周）",
        "report_type": "employee_weekly_summary",
        "payload": {
            "report_type": "employee_weekly_summary",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 10,
            "trace_id": "acceptance-mock-employee-weekly",
        },
    },
    {
        "name": "学生心理健康周报",
        "report_type": "student_psych_weekly",
        "payload": {
            "report_type": "student_psych_weekly",
            "date_start": "2026-06-01",
            "date_end": "2026-06-07",
            "department_id": 10,
            "trace_id": "acceptance-mock-student-psych",
        },
    },
]

ADMIN_HEADERS = {"X-User-Id": "101", "X-User-Role": "admin"}
EMPLOYEE_HEADERS = {"X-User-Id": "102", "X-User-Role": "employee"}
STUDENT_HEADERS = {"X-User-Id": "105", "X-User-Role": "student"}


class AcceptanceRecorder:
    def __init__(self, document_path: Path, phase: str, base_url: str, database_url: str | None, ai_tools_secret: str):
        self.document_path = document_path
        self.phase = phase
        self.base_url = base_url.rstrip("/")
        self.database_url = database_url
        self.ai_tools_secret = ai_tools_secret
        self.failures: list[str] = []
        self.lines: list[str] = []

    def start(self, reset_document: bool) -> None:
        self.document_path.parent.mkdir(parents=True, exist_ok=True)
        if reset_document:
            self.document_path.write_text(self._document_header(), encoding="utf-8")
        self.lines.append(f"\n## {self.phase} 阶段\n")
        self.lines.append(f"- 执行时间：`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
        self.lines.append(f"- 后端地址：`{self.base_url}`")
        self.lines.append(f"- 数据库：`{self._safe_database_label()}`")
        self.lines.append(f"- AI Tools Secret：`{'已配置' if self.ai_tools_secret else '未配置'}`\n")

    def finish(self) -> None:
        self.lines.append("\n### 阶段结论\n")
        if self.failures:
            self.lines.append(f"- 结果：失败，失败步骤数 `{len(self.failures)}`")
            for failure in self.failures:
                self.lines.append(f"- {failure}")
        else:
            self.lines.append("- 结果：通过")
        self.lines.append("\n")
        with self.document_path.open("a", encoding="utf-8") as file:
            file.write("\n".join(self.lines))

    def record_http(
        self,
        title: str,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
        expected_status: set[int] | None = None,
        binary_response: bool = False,
    ) -> httpx.Response:
        headers = headers or {}
        response = self._send(method, path, headers=headers, json_body=json_body)
        expected_status = expected_status or {200}
        if response.status_code not in expected_status:
            self.failures.append(f"{title} 返回状态码 {response.status_code}，期望 {sorted(expected_status)}")

        self.lines.append(f"\n### {title}\n")
        self.lines.append("请求：")
        self.lines.append("```json")
        self.lines.append(
            json.dumps(
                {
                    "method": method,
                    "url": path,
                    "headers": self._sanitize_headers(headers),
                    "json": json_body,
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        self.lines.append("```")
        self.lines.append("响应：")
        self.lines.append("```json")
        self.lines.append(json.dumps(self._response_payload(response, binary_response), ensure_ascii=False, indent=2, default=str))
        self.lines.append("```")
        return response

    def record_database_summary(self) -> None:
        if not self.database_url:
            self.lines.append("\n### 数据库落表统计\n\n未提供 `DATABASE_URL`，跳过数据库统计。\n")
            return
        tables = ["ai_draft", "ai_report", "report_export_record", "audit_log", "ai_tool_call_log"]
        engine = create_engine(self.database_url, pool_pre_ping=True)
        try:
            summary = {}
            with engine.connect() as connection:
                for table in tables:
                    summary[table] = connection.scalar(text(f"SELECT COUNT(*) FROM {table}"))
            self.lines.append("\n### 数据库落表统计\n")
            self.lines.append("```json")
            self.lines.append(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
            self.lines.append("```")
        finally:
            engine.dispose()

    def _send(self, method: str, path: str, *, headers: dict[str, str], json_body: dict[str, Any] | None) -> httpx.Response:
        url = f"{self.base_url}{path}"
        request_headers = dict(headers)
        if path.startswith("/api/v1/ai-tools") and self.ai_tools_secret:
            request_headers.setdefault("X-AI-Tools-Secret", self.ai_tools_secret)
        with httpx.Client(timeout=90) as client:
            return client.request(method, url, headers=request_headers, json=json_body)

    def _response_payload(self, response: httpx.Response, binary_response: bool) -> dict[str, Any]:
        base = {
            "status_code": response.status_code,
            "headers": self._selected_response_headers(response),
        }
        if binary_response:
            content = response.content
            base["binary"] = {
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "first_16_bytes_hex": content[:16].hex(),
            }
            return base
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                base["json"] = response.json()
                return base
            except ValueError:
                pass
        base["text"] = response.text
        return base

    def _selected_response_headers(self, response: httpx.Response) -> dict[str, str]:
        keep = {"content-type", "content-length", "content-disposition"}
        return {key: value for key, value in response.headers.items() if key.lower() in keep}

    def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        sanitized = {}
        for key, value in headers.items():
            if key.lower() == "x-ai-tools-secret":
                sanitized[key] = "<configured>"
            else:
                sanitized[key] = value
        if self.ai_tools_secret:
            sanitized.setdefault("X-AI-Tools-Secret", "<configured>")
        return sanitized

    def _safe_database_label(self) -> str:
        if not self.database_url:
            return "未提供"
        parsed = urlparse(self.database_url)
        return f"{parsed.scheme}://{parsed.hostname}:{parsed.port or ''}{parsed.path}"

    def _document_header(self) -> str:
        return "\n".join(
            [
                "# 报告模块全链路验收结果",
                "",
                "本文档由 `backend/scripts/run_report_full_acceptance.py` 自动生成，记录报告模块后端全链路测试的完整接口输入输出。",
                "",
                "敏感信息处理：MySQL 密码、Dify Key、AI Tools Secret 不写入本文档；二进制文件只记录大小、哈希和文件头摘要。",
                "",
                "## 测试数据摘要",
                "",
                "- 统计周期：`2026-06-01` 至 `2026-06-07`",
                "- 主测部门：`10`，跨部门对照部门：`20`",
                "- 主测管理员用户：`101`，主测员工用户：`102`，主测学生用户：`105`",
                "- 覆盖数据：投诉工单、客户线索、客户研判、活动报名、员工日报、学生心理画像、学生心理预警",
                "- 过滤验证：包含跨部门数据和 `is_delete=1` 逻辑删除数据",
                "- 验收流程：AI Tool 聚合、生成草稿、确认草稿、发布报告、Word/PDF 导出和下载",
                "",
            ]
        )


def run_report_case(recorder: AcceptanceRecorder, case: dict[str, Any]) -> None:
    payload = dict(case["payload"])
    payload["trace_id"] = f"{recorder.phase}-{case['report_type']}"
    recorder.record_http(
        f"{case['name']} - AI Tool 聚合数据",
        "POST",
        "/api/v1/ai-tools/query_report_source_data",
        json_body={
            **payload,
            "conversation_id": f"{recorder.phase}-{case['report_type']}-conversation",
            "caller": "other",
        },
    )

    generate = recorder.record_http(
        f"{case['name']} - 生成草稿",
        "POST",
        "/api/v1/reports/generate-draft",
        headers=ADMIN_HEADERS,
        json_body=payload,
    )
    draft_id = _response_data(generate).get("id")
    if not draft_id:
        return

    confirm = recorder.record_http(
        f"{case['name']} - 确认草稿",
        "POST",
        f"/api/v1/reports/drafts/{draft_id}/confirm",
        headers=ADMIN_HEADERS,
    )
    report_id = _response_data(confirm).get("id")
    if not report_id:
        return

    recorder.record_http(
        f"{case['name']} - 发布报告",
        "POST",
        f"/api/v1/reports/{report_id}/publish",
        headers=ADMIN_HEADERS,
    )

    for export_type in ["word", "pdf"]:
        export = recorder.record_http(
            f"{case['name']} - 导出 {export_type.upper()}",
            "POST",
            f"/api/v1/reports/{report_id}/exports",
            headers=ADMIN_HEADERS,
            json_body={"export_type": export_type},
        )
        export_id = _response_data(export).get("id")
        if not export_id:
            continue
        recorder.record_http(
            f"{case['name']} - 下载 {export_type.upper()}",
            "GET",
            f"/api/v1/reports/exports/{export_id}/download",
            headers=ADMIN_HEADERS,
            binary_response=True,
        )


def run_permission_checks(recorder: AcceptanceRecorder) -> None:
    recorder.lines.append("\n## 权限与安全补充场景\n")
    recorder.record_http(
        "学生访问报告生成接口应被拒绝",
        "POST",
        "/api/v1/reports/generate-draft",
        headers=STUDENT_HEADERS,
        json_body=REPORT_CASES[0]["payload"],
        expected_status={403},
    )
    recorder.record_http(
        "员工发布不存在报告应被拒绝",
        "POST",
        "/api/v1/reports/99999999/publish",
        headers=EMPLOYEE_HEADERS,
        expected_status={403},
    )
    if recorder.ai_tools_secret:
        recorder.record_http(
            "AI Tools Secret 错误应被拒绝",
            "POST",
            "/api/v1/ai-tools/query_report_source_data",
            headers={"X-AI-Tools-Secret": "wrong-secret"},
            json_body={**REPORT_CASES[0]["payload"], "caller": "other"},
            expected_status={401},
        )


def _response_data(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        return {}
    data = payload.get("data")
    return data if isinstance(data, dict) else {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行报告模块全链路验收")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--phase", required=True, choices=["mock", "real-dify"])
    parser.add_argument("--document", default="docs/delivery/report-module-full-acceptance-results.md")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", ""))
    parser.add_argument("--ai-tools-secret", default=os.getenv("AI_TOOLS_SECRET", ""))
    parser.add_argument("--reset-document", action="store_true")
    parser.add_argument("--allow-failures", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    recorder = AcceptanceRecorder(
        document_path=Path(args.document),
        phase=args.phase,
        base_url=args.base_url,
        database_url=args.database_url,
        ai_tools_secret=args.ai_tools_secret,
    )
    recorder.start(reset_document=args.reset_document)
    for case in REPORT_CASES:
        run_report_case(recorder, case)
    run_permission_checks(recorder)
    recorder.record_database_summary()
    recorder.finish()

    if recorder.failures and not args.allow_failures:
        raise SystemExit(f"{args.phase} 阶段验收失败，详见 {args.document}")


if __name__ == "__main__":
    main()
