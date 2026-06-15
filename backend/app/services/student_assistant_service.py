"""学生智能助手 — 公共业务服务。"""

import json
import logging
import re
from datetime import datetime
from uuid import uuid4

import httpx

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("app.api")
from backend.app.models.draft import AiDraft
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.student_profile import StudentProfile
from backend.app.models.sys_user import SysUser
from backend.app.schemas.student_psych_schema import EmotionUpdateRequest, PsychAlertCreateRequest
from backend.app.services.student_psych_service import StudentPsychService


# DeepSeek 心理关怀 System Prompt
PSYCH_SYSTEM_PROMPT = """你是一个温暖、专业的校园心理关怀助手，名叫"小助"。你的职责是与学生进行日常情绪对话，提供共情支持。

## 你的能力
- 倾听学生的情绪表达，给予温暖回应
- 识别学生的情绪状态和风险等级
- 对普通情绪给予鼓励和建议，对高风险情绪及时预警

## 每次回复必须以 JSON 格式输出（不要用 markdown 代码块包裹）：
{
  "emotion_tag": "情绪标签（如：焦虑、学业压力、人际关系、家庭压力、平稳、开心、孤独、迷茫）",
  "emotion_score": 情绪分值（0-100 整数，0=极度消极，50=中性，100=非常积极乐观）,
  "risk_level": "风险等级（low=低风险, medium=中风险, high=高风险, critical=危急）",
  "confidence": 置信度（0.0-1.0 浮点数，表示你对本次情绪判断的把握程度，0.0=完全不确定，1.0=非常有把握）,
  "reply": "你对学生的温暖回复内容"
}

## 风险判断标准
- low：正常情绪波动、轻度吐槽、日常闲聊
- medium：明显消极情绪、持续压力、轻微焦虑或低落
- high：强烈负面情绪、频繁表达无助感、明显抑郁倾向、社交回避
- critical：涉及自伤/自杀/伤害他人/暴力倾向等紧急情况

## 置信度判断标准
- 0.8-1.0：学生明确表达了情绪，你能清晰判断情绪类型和严重程度
- 0.6-0.8：学生表达较为模糊，但你仍能做出合理推断
- 0.4-0.6：学生表述不明确，判断可能不够准确
- 0.0-0.4：信息严重不足，难以做出可靠判断

## 回复原则
1. 共情为先，先理解再建议
2. 语气温暖自然，像朋友一样聊天
3. 不说"我理解你"这种空话，要具体回应学生说的内容
4. 如果风险是 low/medium，给予鼓励和实用小建议
5. 如果风险是 high/critical，告诉学生"我会立即帮你联系老师，请稍等"，不要给建议"""

# 风险等级中文映射
RISK_LEVEL_CN = {"low": "低风险", "medium": "中风险", "high": "高风险", "critical": "危急"}


class StudentAssistantService:
    """学生助手通用业务。"""

    @staticmethod
    def _call_dify(key: str, query: str, user: str = "student") -> dict:
        """调用 Dify API。"""
        body = json.dumps({
            "inputs": {}, "query": query, "response_mode": "blocking", "user": user,
        }).encode("utf-8")
        req = urllib.request.Request(
            settings.dify_api_url, data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return {"answer": data.get("answer", ""), "conversation_id": data.get("conversation_id", "")}

    @staticmethod
    def _call_deepseek(messages: list) -> dict:
        """调用 DeepSeek API，返回解析后的 JSON。"""
        if not settings.deepseek_api_key:
            raise RuntimeError("DeepSeek API Key 未配置，心理支持服务已切换为本地兜底回复")

        try:
            resp = httpx.post(
                settings.deepseek_api_url,
                json={"model": "deepseek-chat", "messages": messages, "temperature": 0.7},
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.ConnectError as exc:
            raise RuntimeError("DeepSeek 网络连接失败，心理支持服务已切换为本地兜底回复") from exc
        except httpx.TimeoutException as exc:
            raise RuntimeError("DeepSeek 请求超时，心理支持服务已切换为本地兜底回复") from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            raise RuntimeError(f"DeepSeek 返回 HTTP {exc.response.status_code}，心理支持服务已切换为本地兜底回复：{detail}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("DeepSeek 响应不是有效 JSON，心理支持服务已切换为本地兜底回复") from exc

        try:
            raw = data["choices"][0]["message"]["content"].strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```\w*\n?", "", raw)
                raw = re.sub(r"\n?```$", "", raw)
            result = json.loads(raw)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("DeepSeek 回复格式异常，心理支持服务已切换为本地兜底回复") from exc

        return result

    @staticmethod
    def _fallback_psych_reply(message: str, warning: str) -> dict:
        """外部模型不可用时返回本地心理支持兜底回复。"""
        logger.warning("心理支持 AI 降级返回：%s", warning)
        return {
            "reply": (
                "我看到了你的压力和焦虑。可以先把眼前最担心的事情写成三项：已经完成的、正在处理的、需要老师协助的。"
                "如果现在情绪很强烈，先暂停十分钟，做几轮缓慢呼吸，再联系顾问或老师一起确认下一步。"
                "如果你出现伤害自己或他人的念头，请立刻联系身边可信的人或当地紧急求助渠道。"
            ),
            "emotion_tag": "焦虑",
            "emotion_score": 50,
            "risk_level": "medium",
            "confidence": 0.3,
        }

    @staticmethod
    def _create_psych_draft(db: Session, content_json: dict, user_id: int) -> AiDraft:
        """创建心理对话 AI 草稿记录（复用 ai_draft 表）。"""
        draft = AiDraft(
            draft_no=f"PE-{datetime.now():%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
            draft_type="psych_emotion",
            biz_module="student_psych",
            status="pending_confirm",
            content_json=content_json,
            created_by=user_id,
        )
        db.add(draft)
        db.flush()
        return draft

    @staticmethod
    def _build_draft_response(draft: AiDraft, degraded: bool = False,
                               warning: str | None = None) -> dict:
        """从 AiDraft.content_json 构建响应。"""
        c = draft.content_json or {}
        confidence = c.get("confidence", 0.5)
        threshold = settings.psych_confidence_threshold
        low_confidence = confidence < threshold
        low_conf_warning = None
        if low_confidence:
            low_conf_warning = (
                f"AI 对本次情绪判断的置信度较低（{confidence:.0%}），"
                f"低于阈值（{threshold:.0%}）。请在确认时仔细检查情绪标签和风险等级是否准确。"
            )

        return {
            "draft_id": draft.id,
            "reply": c.get("reply", c.get("ai_reply", "")),
            "emotion_tag": c.get("emotion_tag", "未知"),
            "emotion_score": c.get("emotion_score", 50),
            "risk_level": c.get("risk_level", "low"),
            "confidence": confidence,
            "need_confirm": draft.status == "pending_confirm",
            "low_confidence": low_confidence,
            "warning": warning or low_conf_warning,
            "degraded": degraded,
            "alert_created": False,
            "assigned_teacher": None,
        }

    @staticmethod
    def ask_life_assistant(query: str) -> dict:
        """Dify 生活支持助手。"""
        return StudentAssistantService._call_dify(settings.dify_life_key, query)

    @staticmethod
    def ask_policy_assistant(query: str) -> dict:
        """Dify 留学政策咨询助手。"""
        return StudentAssistantService._call_dify(settings.dify_policy_key, query)

    @staticmethod
    def chat_psych(db: Session, message: str, user_id: int) -> dict:
        """心理关怀 AI 对话。

        流程（符合 PRD 草稿确认要求）：
        1. 调用 DeepSeek 进行情绪分析
        2. 创建 AiDraft（status=pending_confirm，content_json 存储完整对话数据）
        3. 返回结果给学生，等待确认
        4. 确认后才更新心理画像（由 confirm 接口触发）
        """
        # 1. DeepSeek 对话
        degraded = False
        warning = None
        try:
            result = StudentAssistantService._call_deepseek([
                {"role": "system", "content": PSYCH_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ])
        except RuntimeError as exc:
            result = StudentAssistantService._fallback_psych_reply(message, str(exc))
            degraded = True
            warning = str(exc)

        reply = result.get("reply", "")
        emotion_tag = result.get("emotion_tag", "未知")
        try:
            emotion_score = int(result.get("emotion_score", 50))
        except (TypeError, ValueError):
            emotion_score = 50
        emotion_score = max(0, min(100, emotion_score))
        risk_level = result.get("risk_level", "low")
        if risk_level not in {"low", "medium", "high", "critical"}:
            risk_level = "low"
        try:
            confidence = float(result.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))

        # 查学生
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if student is None:
            return {
                "draft_id": None, "reply": reply, "emotion_tag": emotion_tag,
                "emotion_score": emotion_score, "risk_level": risk_level,
                "confidence": confidence, "need_confirm": False, "low_confidence": False,
                "warning": "未找到学生档案", "degraded": degraded, "alert_created": False,
                "assigned_teacher": None,
            }

        # 2. 创建 AI 草稿（复用 ai_draft 表，content_json 存储全部对话数据）
        draft = StudentAssistantService._create_psych_draft(db, {
            "user_message": message,
            "reply": reply,
            "emotion_tag": emotion_tag,
            "emotion_score": emotion_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "degraded": degraded,
        }, user_id)

        db.commit()

        return StudentAssistantService._build_draft_response(draft, degraded=degraded, warning=warning)

    @staticmethod
    def confirm_psych_draft(db: Session, draft_id: int, user_id: int) -> dict:
        """确认心理对话草稿，将 AI 分析结果写入心理画像。

        流程：
        1. 校验 draft 存在、属于当前用户、状态为 pending_confirm
        2. 更新 draft 状态为 confirmed
        3. 更新 student_psych_profile
        4. 仅当 PSYCH_AUTO_ALERT_ENABLED=true 且 risk_level 为 high/critical 时创建预警
        """
        draft = db.query(AiDraft).filter(
            AiDraft.id == draft_id,
            AiDraft.is_deleted == False,
        ).first()
        if draft is None:
            raise ValueError("草稿不存在")
        if draft.biz_module != "student_psych":
            raise ValueError("非心理关怀草稿，无法确认")
        if draft.created_by != user_id:
            raise ValueError("无权操作他人的草稿")
        if draft.status != "pending_confirm":
            raise ValueError(f"草稿状态为 {draft.status}，无法确认")

        c = draft.content_json or {}
        risk_level = c.get("risk_level", "low")

        # 查学生
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if student is None:
            raise ValueError("未找到关联学生档案")

        # 更新画像
        psych_service = StudentPsychService(db)
        psych_service.update_emotion(
            current_user_id=user_id, current_user_type="admin",
            student_id=student.id,
            data=EmotionUpdateRequest(
                emotion_tag=c.get("emotion_tag"),
                emotion_score=c.get("emotion_score"),
                risk_level=risk_level,
                summary=f"情绪对话确认：{c.get('user_message', '')[:200]}",
            ),
        )

        # 更新草稿状态
        draft.status = "confirmed"
        draft.confirmed_by = user_id
        draft.confirmed_time = datetime.now()

        # 创建预警（仅配置启用时）
        alert_created = False
        assigned_teacher = None
        if settings.psych_auto_alert_enabled and risk_level in ("high", "critical"):
            alert = psych_service.create_alert(
                current_user_id=1, current_user_type="admin",
                data=PsychAlertCreateRequest(
                    student_id=student.id,
                    trigger_reason=StudentAssistantService._build_trigger_reason(c, risk_level),
                    risk_level=risk_level,
                ),
            )
            alert_created = True
            assignee_id = student.teacher_employee_id or student.counselor_employee_id
            if assignee_id:
                from backend.app.daos.student_psych_dao import StudentPsychDao
                StudentPsychDao(db).update_alert(alert.id, teacher_employee_id=assignee_id)
                emp = db.query(EmployeeProfile).filter(EmployeeProfile.id == assignee_id).first()
                if emp:
                    u = db.query(SysUser).filter(SysUser.id == emp.user_id).first()
                    assigned_teacher = u.real_name if u else None

        db.commit()

        result = StudentAssistantService._build_draft_response(draft)
        result["alert_created"] = alert_created
        result["assigned_teacher"] = assigned_teacher
        result["need_confirm"] = False
        return result

    @staticmethod
    def reject_psych_draft(db: Session, draft_id: int, user_id: int,
                           reason: str | None = None) -> dict:
        """驳回心理对话草稿，不更新心理画像。

        流程：
        1. 校验 draft 存在、属于当前用户、状态为 pending_confirm
        2. 更新 draft 状态为 rejected
        """
        draft = db.query(AiDraft).filter(
            AiDraft.id == draft_id,
            AiDraft.is_deleted == False,
        ).first()
        if draft is None:
            raise ValueError("草稿不存在")
        if draft.biz_module != "student_psych":
            raise ValueError("非心理关怀草稿，无法驳回")
        if draft.created_by != user_id:
            raise ValueError("无权操作他人的草稿")
        if draft.status != "pending_confirm":
            raise ValueError(f"草稿状态为 {draft.status}，无法驳回")

        draft.status = "rejected"
        draft.confirmed_by = user_id
        draft.confirmed_time = datetime.now()
        draft.reject_reason = reason

        db.commit()

        return {
            "draft_id": draft.id,
            "status": "rejected",
            "message": "情绪记录已驳回，不更新心理画像",
        }

    @staticmethod
    def _build_trigger_reason(content_json: dict, risk_level: str) -> str:
        """根据 AI 分析结果生成中文预警触发原因。

        Args:
            content_json: AiDraft.content_json，包含 emotion_tag/emotion_score/user_message
            risk_level: 风险等级（low/medium/high/critical）

        Returns:
            结构化中文触发原因描述
        """
        emotion_tag = content_json.get("emotion_tag", "未知")
        risk_cn = RISK_LEVEL_CN.get(risk_level, risk_level)
        try:
            score = content_json.get("emotion_score", "--")
        except (TypeError, ValueError):
            score = "--"
        user_msg = (content_json.get("user_message", "") or "")[:200]

        return (
            f"学生在AI心理对话中表达出{risk_cn}信号"
            f"（情绪标签：{emotion_tag}，情绪分值：{score}）。"
            f"学生原话摘要：「{user_msg}」"
        )
