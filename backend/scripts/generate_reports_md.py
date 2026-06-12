"""通过真实后端 + 真实 Dify 生成五类报告正文，输出到 Markdown。

前置：后端已在 127.0.0.1:8000 运行，.env 配置真实 Dify（mock=false）+ 真实 MySQL，
      已执行 prepare_upstream_demo 补齐四方案上游数据。

用法：python -m backend.scripts.generate_reports_md <输出md路径>
"""

import sys
import time
from datetime import datetime

import httpx

BASE = "http://127.0.0.1:8000"
ADMIN = {"X-User-Id": "1", "X-User-Role": "admin"}
DEPT = 1

CASES = [
    ("投诉处理周报", "complaint_weekly", "2026-06-01", "2026-06-07", None),
    ("全域客户经营分析报告", "customer_operation", "2026-06-01", "2026-06-07", None),
    ("员工日报智能汇总报告（日）", "employee_daily_summary", "2026-06-02", "2026-06-02", None),
    ("员工日报智能汇总报告（周）", "employee_weekly_summary", "2026-06-01", "2026-06-07", None),
    ("学生心理健康周报", "student_psych_weekly", "2026-06-01", "2026-06-07", None),
]


def gen_one(client, report_type, date_start, date_end, owner):
    payload = {
        "report_type": report_type,
        "date_start": date_start,
        "date_end": date_end,
        "department_id": DEPT,
        "trace_id": f"genmd-{report_type}",
    }
    if owner is not None:
        payload["owner_user_id"] = owner
    last_err = None
    for attempt in range(4):
        try:
            r = client.post(f"{BASE}/api/v1/reports/generate-draft", json=payload, headers=ADMIN)
            r.raise_for_status()
            data = r.json().get("data", {})
            return data.get("content_json", {})
        except httpx.HTTPStatusError as e:
            last_err = e
            code = e.response.status_code
            if code in (502, 503, 504) and attempt < 3:
                print(f"  {code} 网关错误，第 {attempt+1} 次重试...", flush=True)
                time.sleep(3 * (attempt + 1))
                continue
            raise
    raise last_err


def render(name, report_type, content):
    L = [f"## {name}", "", f"**报告类型**：`{report_type}`", ""]
    L.append(f"### {content.get('title', '(无标题)')}")
    L.append("")
    L.append(f"**摘要**：{content.get('summary', '')}")
    L.append("")
    for sec in content.get("sections", []):
        L.append(f"#### {sec.get('heading', '')}")
        L.append("")
        L.append(sec.get("content", ""))
        L.append("")
        metrics = sec.get("metrics", [])
        if metrics:
            L.append("| 指标 | 数值 |")
            L.append("|---|---|")
            for m in metrics:
                L.append(f"| {m.get('name', '')} | {m.get('value', '')} |")
            L.append("")
    risks = content.get("risks", [])
    if risks:
        L.append("**风险提示**")
        L.append("")
        for x in risks:
            L.append(f"- {x}")
        L.append("")
    recs = content.get("recommendations", [])
    if recs:
        L.append("**建议事项**")
        L.append("")
        for x in recs:
            L.append(f"- {x}")
        L.append("")
    refs = content.get("source_refs", [])
    if refs:
        L.append("**来源引用**")
        L.append("")
        for x in refs:
            L.append(f"- {x}")
        L.append("")
    L.append("---")
    L.append("")
    return "\n".join(L)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "docs/delivery/report-five-types-enhanced.md"
    header = [
        "# 智能报告模块 — 五类报告正文输出（改进后 / 真实 Dify 版）",
        "",
        f"**生成日期**：{datetime.now().strftime('%Y-%m-%d')}",
        "**数据源**：真实 MySQL（education_service_ai_test）",
        "**生成方式**：真实 Dify 工作流（DIFY_MOCK_ENABLED=false），deepseek-v4-flash 生成",
        "**统计部门**：咨询一部（department_id=1）",
        "**统计周期**：2026-06-01 至 2026-06-07（日报取 2026-06-02 单日）",
        "",
        "本轮四方案上游数据已就绪：方案A（工单 AI 分类+根因，真实 DeepSeek 打标）、"
        "方案B（线索三维组合聚类）、方案C（情绪识别含文化冲突，真实 DeepSeek 打标）、"
        "方案D（academic_event 真实学期日历派生 period_hint）。",
        "",
        "---",
        "",
    ]
    parts = ["\n".join(header)]
    failures = []
    with httpx.Client(timeout=180) as client:
        for name, rt, ds, de, owner in CASES:
            print(f"生成中：{name} ...", flush=True)
            try:
                content = gen_one(client, rt, ds, de, owner)
                parts.append(render(name, rt, content))
                print(f"  完成：{content.get('title', '(无标题)')}", flush=True)
            except Exception as e:
                failures.append(name)
                parts.append(f"## {name}\n\n**报告类型**：`{rt}`\n\n> ⚠️ 生成失败：{repr(e)[:200]}\n\n---\n")
                print(f"  失败：{repr(e)[:160]}", flush=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"\n已写入：{out_path}")
    if failures:
        print(f"失败 {len(failures)} 个：{failures}")


if __name__ == "__main__":
    main()
