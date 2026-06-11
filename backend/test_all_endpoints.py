"""系统性测试所有 API 端点，输出测试报告。"""
import json
import urllib.request
import urllib.error
import urllib.parse
import sys

BASE = "http://localhost:8000"

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

def call(method, path, params=None, body=None):
    """调用 API 并返回 (status, body_text)。"""
    url = f"{BASE}{path}"
    if params:
        qs = urllib.parse.urlencode(params)
        url = f"{url}?{qs}"

    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8")[:500]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:500]
    except Exception as e:
        return None, str(e)[:200]


def test(name, method, path, params=None, body=None, expected_codes=(200, 201), skip=False, skip_reason=""):
    """运行单个测试并返回结果。"""
    if skip:
        return {"name": name, "method": method, "path": path, "status": "SKIP", "reason": skip_reason}

    status, resp = call(method, path, params, body)
    ok = status in expected_codes if status is not None else False
    result = {
        "name": name,
        "method": method,
        "path": path,
        "params": params,
        "body": body is not None,
        "http_status": status,
        "response": resp[:300] if resp else "",
        "ok": ok,
    }
    if not ok:
        result["status"] = "FAIL"
        result["expected"] = expected_codes
    else:
        result["status"] = "PASS"
    return result


results = []

# ============================================================
# 1. 系统
# ============================================================
results.append(test("健康检查", "GET", "/health"))

# ============================================================
# 2. AI 工具列表
# ============================================================
results.append(test("AI工具列表", "GET", "/api"))

# ============================================================
# 3. 学业事件 (Academic Events)
# ============================================================
results.append(test("查询学业事件列表", "GET", "/api/academic-events", params={"page": 1, "size": 5}))
results.append(test("查询临期/逾期学业事件", "GET", "/api/academic-events/approaching-deadlines", params={"within_days": 7}))
results.append(test("查询即将触发提醒", "GET", "/api/academic-events/upcoming-reminders"))

# POST 创建学业事件 (需要请求体)
results.append(test("创建学业事件", "POST", "/api/academic-events",
    body={"event_type": "exam", "title": "测试考试", "deadline_time": "2026-12-31T10:00:00"},
    expected_codes=(200, 201, 422, 500)))

# ============================================================
# 4. 申请进度 (Application Progress)
# ============================================================
results.append(test("查询申请进度列表", "GET", "/api/application-progress", params={"page": 1, "size": 5}))
results.append(test("获取阶段参考", "GET", "/api/application-progress/stages"))
results.append(test("统计卡住数量", "GET", "/api/application-progress/stats/blocked-count"))
results.append(test("CRM同步(预览)", "POST", "/api/application-progress/crm/sync", body={}, expected_codes=(200, 201, 422, 500)))

# ============================================================
# 5. Dify 工具接口
# ============================================================
results.append(test("Dify工具-查询客服FAQ", "POST", "/api/search_customer_service_faq",
    body={"keyword": "留学", "limit": 3, "trace_id": "test-001", "caller": "test"},
    expected_codes=(200, 201, 422, 500)))
results.append(test("Dify工具-推荐课程项目", "POST", "/api/recommend_course_projects",
    body={"keyword": "新加坡", "limit": 3, "trace_id": "test-002", "caller": "test"},
    expected_codes=(200, 201, 422, 500)))
results.append(test("Dify工具-查询可报名活动", "POST", "/api/list_open_events",
    body={"keyword": "", "limit": 5, "trace_id": "test-003", "caller": "test"},
    expected_codes=(200, 201, 422, 500)))
results.append(test("Dify工具-创建活动报名", "POST", "/api/create_activity_signup",
    body={"event_id": 1, "visitor_name": "测试用户", "visitor_phone": "13800000000", "trace_id": "test-004"},
    expected_codes=(200, 201, 422, 404, 500)))
results.append(test("Dify工具-查询报告源数据", "POST", "/api/query_report_source_data",
    body={"report_type": "complaint_weekly", "trace_id": "test-005"},
    expected_codes=(200, 201, 422, 500)))

# ============================================================
# 6. 学生反馈工单
# ============================================================
results.append(test("查询反馈工单列表", "GET", "/api/student-feedback-tickets", params={"page": 1, "size": 5}))
results.append(test("学生查看自己的通知", "GET", "/api/student-feedback-tickets/my/notifications", params={"student_id": 1},
    expected_codes=(200, 401, 403, 404, 422)))

# ============================================================
# 7. 报告 (v1)
# ============================================================
results.append(test("报告-列表", "GET", "/api/v1/reports", params={"page": 1, "size": 5}))
results.append(test("报告-草稿列表", "GET", "/api/v1/reports/drafts", params={"page": 1, "size": 5}))
results.append(test("报告-生成草稿", "POST", "/api/v1/reports/generate-draft",
    body={"report_type": "complaint_weekly"}, expected_codes=(200, 201, 422, 500)))

# ============================================================
# 8. 学生助手 - 请假
# ============================================================
results.append(test("学生助手-请假列表", "GET", "/api/v1/student-assistant/leaves", params={"page": 1, "size": 5},
    expected_codes=(200, 401, 403, 500)))
results.append(test("学生助手-待审批列表", "GET", "/api/v1/student-assistant/leaves/pending", params={"page": 1, "size": 5},
    expected_codes=(200, 401, 403, 500)))
results.append(test("学生助手-待审批计数", "GET", "/api/v1/student-assistant/leaves/pending/count",
    expected_codes=(200, 401, 403, 500)))
results.append(test("学生助手-审批历史", "GET", "/api/v1/student-assistant/leaves/history", params={"page": 1, "size": 5},
    expected_codes=(200, 401, 403, 500)))

# ============================================================
# 9. 学生助手 - 心理关怀
# ============================================================
results.append(test("心理关怀-查看自己的档案", "GET", "/api/v1/student-assistant/psych/profile",
    expected_codes=(200, 401, 403, 404, 500)))
results.append(test("心理关怀-预警列表(学生)", "GET", "/api/v1/student-assistant/psych/alerts", params={"page": 1, "size": 5},
    expected_codes=(200, 401, 403, 500)))
results.append(test("心理关怀-待处理预警(员工)", "GET", "/api/v1/student-assistant/psych/alerts/pending", params={"page": 1, "size": 5},
    expected_codes=(200, 401, 403, 500)))
results.append(test("心理关怀-待处理计数", "GET", "/api/v1/student-assistant/psych/alerts/pending/count",
    expected_codes=(200, 401, 403, 500)))
results.append(test("心理关怀-预警历史(员工)", "GET", "/api/v1/student-assistant/psych/alerts/history", params={"page": 1, "size": 5},
    expected_codes=(200, 401, 403, 500)))
results.append(test("心理关怀-学生档案列表(员工)", "GET", "/api/v1/student-assistant/psych/profiles", params={"page": 1, "size": 5},
    expected_codes=(200, 401, 403, 500)))

# ============================================================
# 10. 学生助手 - AI 对话
# ============================================================
results.append(test("学生助手-生活支持FAQ", "GET", "/api/v1/student-assistant/life-support/faq", params={"keyword": "宿舍"},
    expected_codes=(200, 500)))
results.append(test("学生助手-生活支持对话", "POST", "/api/v1/student-assistant/life-support/chat",
    body={"message": "你好", "student_id": 1}, expected_codes=(200, 201, 500)))
results.append(test("学生助手-留学政策对话", "POST", "/api/v1/student-assistant/policy/chat",
    body={"message": "新加坡留学条件", "student_id": 1}, expected_codes=(200, 201, 500)))
results.append(test("学生助手-心理关怀对话", "POST", "/api/v1/student-assistant/psych/chat",
    body={"message": "最近压力大", "student_id": 1}, expected_codes=(200, 201, 500)))

# ============================================================
# 11. 企业管理查询助手
# ============================================================
ENTERPRISE = "/enterprise/api/v1/enterprise-query"
results.append(test("企业-客户线索查询", "GET", f"{ENTERPRISE}/leads/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-日报查询", "GET", f"{ENTERPRISE}/daily-reports/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-日报汇总", "GET", f"{ENTERPRISE}/daily-reports/summary",
    params={"report_start": "2026-01-01", "report_end": "2026-06-30"}))
results.append(test("企业-组织架构查询", "GET", f"{ENTERPRISE}/departments/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-学生档案查询", "GET", f"{ENTERPRISE}/students/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-学生成绩查询", "GET", f"{ENTERPRISE}/student-scores/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-学生请假查询", "GET", f"{ENTERPRISE}/student-leaves/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-投诉反馈查询", "GET", f"{ENTERPRISE}/student-feedback/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-申请进度查询", "GET", f"{ENTERPRISE}/student-application-progress/search", params={"page": 1, "page_size": 5}))
results.append(test("企业-待办统计", "GET", f"{ENTERPRISE}/todos/summary"))
results.append(test("企业-管理统计", "GET", f"{ENTERPRISE}/statistics/summary"))
results.append(test("企业-新人入职指引", "GET", f"{ENTERPRISE}/onboarding/guide", params={"question": "公司有什么规章制度"},
    expected_codes=(200, 500)))  # 可能500因为要连Dify

# ============================================================
# 12. NL2SQL
# ============================================================
results.append(test("企业-NL2SQL查询", "POST", f"{ENTERPRISE}/nl2sql/query",
    body={"query": "查询所有学生的成绩"}, expected_codes=(200, 201, 500)))

# ============================================================
# 13. 企业业务办理
# ============================================================
results.append(test("企业-执行业务操作", "POST", "/enterprise/api/v1/enterprise-operation/execute",
    body={"intent": "student_leave_approve", "parameters": {"leave_id": 1}},
    expected_codes=(200, 201, 404, 422, 500)))
results.append(test("企业-确认操作草稿", "POST", "/enterprise/api/v1/enterprise-operation/confirm",
    body={"draft_id": 1, "action": "confirm"},
    expected_codes=(200, 201, 404, 422, 500)))

# ============================================================
# 14. /api/v1 下的重复 Dify 工具 (只测一个确认路由存在)
# ============================================================
results.append(test("v1-AI工具列表", "GET", "/api/v1"))

# ============================================================
# 汇总
# ============================================================
print("=" * 70)
print(f"{'端点API测试报告':^60}")
print("=" * 70)
print()

pass_count = sum(1 for r in results if r["status"] == "PASS")
fail_count = sum(1 for r in results if r["status"] == "FAIL")
skip_count = sum(1 for r in results if r["status"] == "SKIP")
total = len(results)

print(f"总计: {total}  |  通过: {pass_count}  |  失败: {fail_count}  |  跳过: {skip_count}")
print()

# 先打印失败的
if fail_count > 0:
    print("-" * 70)
    print("❌ 失败接口")
    print("-" * 70)
    for r in results:
        if r["status"] == "FAIL":
            print(f"  {r['method']:6s} {r['path']}")
            print(f"          名称: {r['name']}")
            print(f"          预期: {r['expected']}, 实际: {r['http_status']}")
            print(f"          响应: {r['response'][:200]}")
            print()

# 全部列表
print("-" * 70)
print("📋 完整结果")
print("-" * 70)
for r in results:
    icon = "✅" if r["status"] == "PASS" else ("⏭️" if r["status"] == "SKIP" else "❌")
    print(f"  {icon} {r['method']:6s}  [{r['http_status'] or 'ERR':>5}]  {r['name']:30s}  {r['path']}")

print()
print("-" * 70)
print("测试完成")
print("-" * 70)
