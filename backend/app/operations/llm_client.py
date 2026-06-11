"""LLM 意图解析客户端。

支持 DeepSeek（主）和 mock（保底）两种模式。
DeepSeek 模式下将用户 query 和意图 Schema 发送给大模型，
返回结构化的 {intent, parameters}。
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .intent_schemas import INTENT_SCHEMA_REGISTRY


# ---------- 全局 DeepSeek 客户端 ----------

_DEEPSEEK_CLIENT: Optional[OpenAI] = None

def _load_dotenv_safe() -> None:
    """尝试从多个路径加载 .env 文件，确保环境变量可用。"""
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent.parent.parent  # EducationalServices/
        for env_path in [base / ".env", base / "backend" / ".env"]:
            if env_path.exists():
                load_dotenv(env_path, override=False)
    except ImportError:
        pass  # python-dotenv 未安装


def _get_deepseek_client() -> Optional[OpenAI]:
    """获取 DeepSeek 客户端（懒加载，未配置 key 时返回 None）。

    加载顺序（按优先级）：
    1. Settings（含 .env 配置的绝对路径）
    2. os.environ 环境变量
    3. 直接加载 .env 文件（兜底）
    """
    global _DEEPSEEK_CLIENT
    if _DEEPSEEK_CLIENT is None:
        from ..core.config import get_settings
        # 先尝试从 Settings 读（如果 @lru_cache 缓存了空值，继续往下走）
        settings = get_settings()
        api_key = settings.deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
        base_url = settings.deepseek_base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        # Settings 没读到，尝试直接加载 .env
        if not api_key:
            _load_dotenv_safe()
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        if api_key:
            _DEEPSEEK_CLIENT = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
    return _DEEPSEEK_CLIENT


# ---------- 数据结构 ----------


class ParsedIntent:
    """LLM 解析结果。"""
    def __init__(self, intent: str, parameters: Dict[str, Any], conversation_id: Optional[str] = None):
        self.intent = intent
        self.parameters = parameters
        self.conversation_id = conversation_id


class IntentionParseError(Exception):
    """意图解析失败异常。"""
    pass


# ---------- Prompt 构建 ----------


def _build_schema_text() -> str:
    """从 INTENT_SCHEMA_REGISTRY 动态生成意图描述的文本。"""
    lines = []
    for intent, schema in INTENT_SCHEMA_REGISTRY.items():
        lines.append(f"### {intent}（{schema.description}）")
        required = [f for f in schema.fields if f.required]
        optional = [f for f in schema.fields if not f.required]
        if required:
            lines.append(f"必填字段：{', '.join([f'{f.key}({f.label})' for f in required])}")
        if optional:
            lines.append(f"可选字段：{', '.join([f'{f.key}({f.label})' for f in optional])}")
        lines.append("")
    return "\n".join(lines)


_SYSTEM_PROMPT_TPL = """你是一个企业业务办理助手的自然语言解析引擎。
你的任务是将用户的自然语言输入解析为结构化的操作意图和参数。

## 支持的意图

{schema_text}

## 解析规则

1. 如果用户意图是"查询"类型（查待审批、查待办等），action 设为 "query"
2. 金额单位统一转为"万"（如"10w" → "10万"，"100k" → "10万"）
3. 手机号提取完整 11 位数字
4. 学生姓名和客户姓名不要包含"同学"后缀
5. 状态值必须返回英文码：new=新增, following=跟进中, signed=已签约, lost=已流失, invalid=无效

## 投诉处理 action 映射

对于 `handle_complaint` 意图，`action` 字段必须严格使用以下值：
- 用户说"改为处理中""在处理" → `action` = "process"
- 用户说"已解决""解决方案""处理方案" → `action` = "resolve"
- 用户说"关闭""关单" → `action` = "close"
- 用户说"通知" → `action` = "notify"

## 成绩录入格式

对于 `enter_student_score` 意图：
- `course_name` 是科目名称（如"阅读""写作""听力""口语""数学"等），不是考试类型
- `exam_type` 是考试类型（如"模考""期中""期末""daily"等）
- 如果输入中有多条成绩，每条成绩作为独立字段：`course_name` 填第一条科目，`score` 填第一条分数
  多余的成绩会被系统自动拆分，只需正确提取第一条即可

## 姓名提取规则（重要—严格遵守）

✅ 正确示例：
  "我要新增一个同学，张满昌" → customer_name = "张满昌"
  "帮我新增一个客户，李思琪" → customer_name = "李思琪"
  "新增一个 同学：涂丽同学" → customer_name = "涂丽"
  "新增客户，王一鸣，电话13700030001" → customer_name = "王一鸣"
  "把王同学改成已签约" → customer_name = "王同学"
  "给张同学录入雅思成绩" → student_name = "张同学"
  "同意张三同学的请假申请" → student_name = "张三"

❌ 错误示例（绝不能犯）：
  "我要新增一个同学，张满昌" → customer_name 绝不能是"我要新增一个"或"我要新增一个同学"
  "帮我新增一个客户" → 客户姓名未知时，不填 customer_name
  "新增一个 同学：涂丽同学" → customer_name 是"涂丽"不是"新增一个"

## 输出格式

只输出 JSON，不要 markdown 代码块标记，不要额外说明：

{{
  "intent": "意图编码",
  "parameters": {{
    "字段名": "值"
  }}
}}"""


_SUPPLEMENT_PROMPT_TPL = """你是一个企业业务办理助手的自然语言补全引擎。
用户之前已经提交了部分信息，现在补充了新的内容。
请将新输入的内容合并到已有参数中。

## 已有参数

{existing_params}

## 用户新输入

{new_query}

## 输出格式

只输出 JSON，不要 markdown 代码块标记：

{{
  "parameters": {{
    "字段名": "值（合并后的完整参数）"
  }}
}}"""


# ---------- 客户端 ----------


class OperationLlmClient:
    """统一 LLM 客户端，优先使用 DeepSeek，不可用时回退 mock。"""

    # ==================== mock 模式保留（保底） ====================

    INTENT_KEYWORDS: Dict[str, List[str]] = {
        "approve_leave": ["审批", "请假", "假条", "同意请假", "驳回请假"],
        "submit_daily_report": ["日报", "今天工作", "今日工作", "口述日报", "今天的日报", "工作日报"],
        "update_lead_status": ["改状态", "更新状态", "状态更新", "改成", "转为", "变更为", "更新为"],
        "enter_student_score": ["成绩", "分数", "录入成绩", "考试"],
        "handle_complaint": ["投诉", "反馈", "工单", "处理投诉"],
        "create_lead": ["新增客户", "录入客户", "添加客户", "新增意向", "新线索", "录入意向",
                         "新增一个", "增加一个", "我要新增", "我要增加", "帮我新增", "帮我增加"],
    }

    STATUS_MAP: Dict[str, str] = {
        "跟进中": "following", "跟进": "following",
        "已签约": "signed", "签约": "signed",
        "已流失": "lost", "流失": "lost",
        "新增": "new", "新": "new",
        "无效": "invalid",
    }

    _VAL = r"(?P<val>[^，。；\s,;]{1,30})"
    _ANY_SEP = r"[：:为叫做是，,、\s]*"
    FIELD_PATTERNS: Dict[str, List[str]] = {
        "customer_name": [rf"(?:客户|姓名|名字|学生){_ANY_SEP}{_VAL}"],
        "phone": [rf"(?:电话|手机|联系方式|手机号|tel|手机号码){_ANY_SEP}(1\d{{10}}|0\d{{2,3}}-?\d{{7,8}})",
                  r"(?<!\d)(1[3-9]\d{9})(?!\d)"],
        "source_channel": [rf"(?:来源|渠道|来自|通过){_ANY_SEP}{_VAL}"],
        "education_level": [rf"(?:学历|教育背景|教育阶段|在读){_ANY_SEP}{_VAL}",
                            r"(本科|硕士|博士|研究生|高中|大专|专升本)"],
        "target_country": [rf"(?:意向国家|目标国家|想去|留学国家){_ANY_SEP}{_VAL}"],
        "target_program": [r"(?:申请|想去|去|读|考).*?(硕士|本科|博士|研究生|语言|预科|高中|专升本)",
                           rf"(?:意向项目|目标项目|项目){_ANY_SEP}{_VAL}"],
        "budget_range": [rf"(?:预算|费用|花费){_ANY_SEP}([\d.]+\s*万|\d{{2,}}\s*万元?)",
                         rf"(\d{{2,}}\s*万)"],
        "key_progress": [r"(?:跟进|完成|处理|新增|约了|安排|推进)(?:了)?\s*(\d+\s*[个位]|[^，。；\s,;]{2,30})"],
        "risks": [r"(?:风险|问题|担忧|不稳定|犹豫)\s*[：:为]?\s*([^，。；\s,;]{4,50})",
                  r"([^，。；\s,;]{2,20})\s*(?:风险|问题|不稳定|意愿不稳定)"],
        "tomorrow_plan": [rf"(?:明天|明日|计划){_ANY_SEP}([^，。；\s,;]{{4,50}})?"],
        "exam_type": [rf"(?:考试类型|考试|exam){_ANY_SEP}{_VAL}"],
    }

    def __init__(self):
        self._deepseek = _get_deepseek_client()

    # ==================== 主入口 ====================

    def parse_intent(self, query: str, conversation_id: Optional[str] = None) -> ParsedIntent:
        """解析用户输入，优先使用 DeepSeek。"""
        if self._deepseek:
            try:
                return self._deepseek_parse(query, conversation_id)
            except Exception as e:
                # DeepSeek 失败，静默降级到 mock
                print(f"[LLM] DeepSeek 解析失败，降级到 mock: {e}")
        return self._mock_parse(query, conversation_id)

    def supplement_fields(self, query: str, existing_params: Dict[str, Any]) -> Dict[str, Any]:
        """追问补全，优先使用 DeepSeek。"""
        if self._deepseek:
            try:
                return self._deepseek_supplement(query, existing_params)
            except Exception as e:
                print(f"[LLM] DeepSeek 追问失败，降级到 mock: {e}")
        return self._mock_supplement(query, existing_params)

    # ==================== DeepSeek 模式 ====================

    def _build_system_prompt(self) -> str:
        return _SYSTEM_PROMPT_TPL.format(schema_text=_build_schema_text())

    def _deepseek_parse(self, query: str, conversation_id: Optional[str] = None) -> ParsedIntent:
        """调用 DeepSeek 解析意图。"""
        from ..core.config import get_settings
        model = get_settings().deepseek_model or "deepseek-chat"
        response = self._deepseek.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": query},
            ],
            temperature=0.01,
            max_tokens=1024,
        )
        content = response.choices[0].message.content.strip()
        return self._parse_llm_response(content, conversation_id, query)

    def _deepseek_supplement(self, query: str, existing_params: Dict[str, Any]) -> Dict[str, Any]:
        """调用 DeepSeek 补全字段。"""
        from ..core.config import get_settings
        model = get_settings().deepseek_model or "deepseek-chat"
        prompt = _SUPPLEMENT_PROMPT_TPL.format(
            existing_params=json.dumps(existing_params, ensure_ascii=False),
            new_query=query,
        )
        response = self._deepseek.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.01,
            max_tokens=1024,
        )
        content = response.choices[0].message.content.strip()
        result = self._parse_json_response(content)
        merged = result.get("parameters", {})
        # 将已有参数与 LLM 返回合并（LLM 返回的是完整参数）
        final = {**existing_params}
        for k, v in merged.items():
            if v is not None and v != "":
                final[k] = v
        return final

    # 常见非姓名关键词（用于后处理校验）
    _NAME_BLACKLIST = [
        "我要新增", "帮我新增", "新增一个", "新增客户", "录入客户",
        "添加客户", "帮我添加", "我要添加", "一个同学", "一个客户",
        "我要增加", "帮我增加", "增加一个", "一个",
    ]

    @staticmethod
    def _validate_name(name: Any) -> bool:
        """客户/学生姓名后处理校验：排除明显不是人名的值。"""
        if not name or not isinstance(name, str):
            return False
        name = name.strip()
        if len(name) < 2 or len(name) > 8:  # 中文名 2-6 字
            return False
        for kw in OperationLlmClient._NAME_BLACKLIST:
            if kw in name:
                return False
        return True

    def _parse_llm_response(self, content: str, conversation_id: Optional[str] = None, query: str = "") -> ParsedIntent:
        """解析 LLM 返回的 JSON。"""
        data = self._parse_json_response(content)
        intent = data.get("intent", "create_lead")
        params = data.get("parameters", {})
        # 清理参数中的 None 值
        params = {k: v for k, v in params.items() if v is not None}

        # 补充：多科成绩场景（DeepSeek 只返回一条，用 mock 解析补充）
        if intent == "enter_student_score" and query:
            mock_scores = self._extract_multi_scores(query)
            if mock_scores:
                # 如果 DeepSeek 已识别到部分成绩，合并去重
                existing = params.get("_scores", [])
                seen_courses = {s["course_name"] for s in existing}
                for s in mock_scores:
                    if s["course_name"] not in seen_courses:
                        existing.append(s)
                        seen_courses.add(s["course_name"])
                if existing:
                    params["_scores"] = existing
                    # 补充 exam_type（DeepSeek 可能已提取）
                    if not params.get("exam_type"):
                        import re
                        em = re.search(r"(?:模考|期中|期末|月考|周考|daily|midterm|final)", query)
                        if em:
                            params["exam_type"] = em.group(0)

        return ParsedIntent(intent=intent, parameters=params, conversation_id=conversation_id)

    @staticmethod
    def _parse_json_response(content: str) -> dict:
        """从 LLM 回复中提取 JSON（兼容带 markdown 代码块的情况）。"""
        # 尝试直接解析
        content = content.strip()
        if content.startswith("{"):
            return json.loads(content)
        # 尝试从 ```json ... ``` 中提取
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if m:
            return json.loads(m.group(1))
        raise IntentionParseError(f"无法解析 LLM 响应: {content[:200]}")

    # ==================== mock 模式（保底） ====================

    def _detect_intent(self, query: str) -> str:
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in query:
                    return intent
        if any(w in query for w in ["改为", "更新", "修改", "转成", "变为"]):
            return "update_lead_status"
        return "create_lead"

    def _extract_fields(self, query: str, schema_keys: List[str]) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        for key in schema_keys:
            patterns = self.FIELD_PATTERNS.get(key, [])
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    value = match.group(1).strip()
                    if value:
                        params[key] = value
                        break

        # 特殊处理：年级
        if "current_grade" in schema_keys and "current_grade" not in params:
            gm = re.search(r"([大高])([一二三四五])", query)
            if gm:
                params["current_grade"] = gm.group(1) + gm.group(2)

        # 特殊处理：状态
        if "status" in schema_keys and "status" not in params:
            for zh, en in self.STATUS_MAP.items():
                if zh in query:
                    params["status"] = en
                    break

        # 特殊处理：客户姓名兜底
        if "customer_name" in schema_keys and "customer_name" not in params:
            nm = re.search(r"把\s*(\S{1,10}?)\s*(?:状态|的|改成|改为)", query)
            if nm:
                params["customer_name"] = nm.group(1).strip()

        # 特殊处理："同学：XXX同学" 格式
        if "customer_name" in schema_keys and "customer_name" not in params:
            m = re.search(r"同学[：:]\s*(\S{1,10}?)(?:同学|$)", query)
            if m and m.group(1).strip():
                params["customer_name"] = m.group(1).strip()
            else:
                for m in re.finditer(r"(\S{1,10})同学(?:[，。；\s,;]|$)", query):
                    name = m.group(1).strip()
                    # 跳过黑名单词（如"一个"、"新增一个"等），取真正的人名
                    if name and len(name) >= 2 and self._validate_name(name):
                        params["customer_name"] = name
                        break
                # 兜底："同学，XXX，" 格式 —— 取逗号后的第一个词
                if "customer_name" not in params:
                    tail = re.split(r"同学[，,]\s*", query)
                    if len(tail) > 1:
                        after = tail[1].strip().lstrip("，,")
                        name = re.split(r"[，,。；\s]", after)[0].strip()
                        if name and len(name) >= 2 and self._validate_name(name):
                            params["customer_name"] = name

        # 特殊处理：日报 raw_content
        if "raw_content" in schema_keys and "raw_content" not in params:
            params["raw_content"] = query

        # 特殊处理：学生姓名
        if "student_name" in schema_keys and "student_name" not in params:
            nm = re.search(r"[给为]\s*(\S{1,10})(?:录入|登记|添加|记录)", query)
            if nm:
                params["student_name"] = nm.group(1).strip()

        # 特殊处理：请假/投诉 action
        if "action" in schema_keys and "action" not in params:
            if any(w in query for w in ["待审批", "待处理", "有哪些", "还有哪些", "我的待办", "需要处理"]):
                params["action"] = "query"
            elif any(w in query for w in ["处理中", "在处理"]):
                params["action"] = "process"
            elif any(w in query for w in ["已解决", "解决方案", "处理方案", "处理结果"]):
                params["action"] = "resolve"
            elif any(w in query for w in ["关闭", "关单"]):
                params["action"] = "close"
            elif any(w in query for w in ["同意", "通过", "批准"]):
                params["action"] = "approve"
            elif any(w in query for w in ["驳回", "拒绝", "不同意"]):
                params["action"] = "reject"

        # 特殊处理：多科成绩
        if "course_name" in schema_keys or "score" in schema_keys:
            scores = self._extract_multi_scores(query)
            if scores:
                params["_scores"] = scores

        return params

    def _mock_parse(self, query: str, conversation_id: Optional[str] = None) -> ParsedIntent:
        intent = self._detect_intent(query)
        schema = INTENT_SCHEMA_REGISTRY.get(intent)
        all_keys = [f.key for f in schema.fields] if schema else []
        params = self._extract_fields(query, all_keys)
        return ParsedIntent(intent=intent, parameters=params, conversation_id=conversation_id)

    def _mock_supplement(self, query: str, existing_params: Dict[str, Any]) -> Dict[str, Any]:
        intent = existing_params.get("_intent", "create_lead")
        schema = INTENT_SCHEMA_REGISTRY.get(intent) or INTENT_SCHEMA_REGISTRY.get("create_lead")
        all_keys = [f.key for f in schema.fields] if schema else []
        missing_keys = [k for k in all_keys if k not in existing_params or not existing_params[k]]
        new_params = self._extract_fields(query, missing_keys)
        return {**existing_params, **new_params}

    SCORE_COURSE_KEYWORDS = [
        "听力", "阅读", "口语", "写作", "语法", "词汇", "作文", "翻译",
        "数学", "物理", "化学", "生物", "历史", "地理", "政治",
        "语文", "英语", "总分", "综合",
    ]

    def _extract_multi_scores(self, query: str) -> List[Dict[str, Any]]:
        results = []
        pattern1 = rf"(?:{'|'.join(self.SCORE_COURSE_KEYWORDS)})(\d+(?:\.\d+)?)\s*分"
        for m in re.finditer(pattern1, query):
            # 科目名紧跟在数字前，直接从 match 的起始位置获取关键词
            matched_text = query[m.start():m.end()]
            course = None
            for kw in sorted(self.SCORE_COURSE_KEYWORDS, key=len, reverse=True):
                # 检查关键词是否出现在匹配文本的开头
                if matched_text.startswith(kw):
                    course = kw
                    break
            if course:
                results.append({"course_name": course, "score": float(m.group(1))})
        prefix = ["雅思", "托福", "GRE", "GMAT", "SAT"]
        for p in prefix:
            if p in query:
                for r in results:
                    if not r["course_name"].startswith(p):
                        r["course_name"] = f"{p}{r['course_name']}"
        return results

    def _generate_report_summary(self, query: str, params: Dict[str, Any]) -> Optional[str]:
        parts = []
        progress = params.get("key_progress")
        risks = params.get("risks")
        plan = params.get("tomorrow_plan")
        if progress:
            parts.append(f"关键进展：{progress}")
        if risks:
            parts.append(f"风险问题：{risks}")
        if plan:
            parts.append(f"明日计划：{plan}")
        if parts:
            return "；".join(parts)
        return query[:40] + ("…" if len(query) > 40 else "")
