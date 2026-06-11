"""学生智能助手 — 公共业务服务。"""

import json
import re
import urllib.request

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.daos.student_assistant_dao import StudentAssistantDao

settings = get_settings()
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.student_profile import StudentProfile
from backend.app.models.sys_user import SysUser
from backend.app.schemas.student_assistant_schema import LifeFaqItem, LifeFaqResult
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
  "reply": "你对学生的温暖回复内容"
}

## 风险判断标准
- low：正常情绪波动、轻度吐槽、日常闲聊
- medium：明显消极情绪、持续压力、轻微焦虑或低落
- high：强烈负面情绪、频繁表达无助感、明显抑郁倾向、社交回避
- critical：涉及自伤/自杀/伤害他人/暴力倾向等紧急情况

## 回复原则
1. 共情为先，先理解再建议
2. 语气温暖自然，像朋友一样聊天
3. 不说"我理解你"这种空话，要具体回应学生说的内容
4. 如果风险是 low/medium，给予鼓励和实用小建议
5. 如果风险是 high/critical，告诉学生"我会立即帮你联系老师，请稍等"，不要给建议"""


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
        body = json.dumps({
            "model": "deepseek-chat", "messages": messages, "temperature": 0.7,
        }).encode("utf-8")
        req = urllib.request.Request(
            settings.deepseek_api_url, data=body,
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            raw = data["choices"][0]["message"]["content"].strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```\w*\n?", "", raw)
                raw = re.sub(r"\n?```$", "", raw)
            return json.loads(raw)

    @staticmethod
    def search_life_faq(db: Session, keyword: str, limit: int = 10) -> LifeFaqResult:
        """本地 FAQ 知识库搜索。"""
        items, total = StudentAssistantDao.search_life_faq(db, keyword, limit)
        return LifeFaqResult(
            items=[LifeFaqItem.model_validate(i) for i in items],
            keyword=keyword, total=total,
        )

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
        """心理关怀 AI 对话。每次更新画像，高危自动创建预警并分配老师。"""
        # 1. DeepSeek 对话
        result = StudentAssistantService._call_deepseek([
            {"role": "system", "content": PSYCH_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ])
        reply = result.get("reply", "")
        emotion_tag = result.get("emotion_tag", "未知")
        emotion_score = result.get("emotion_score", 50)
        risk_level = result.get("risk_level", "low")

        # 2. 查学生
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if student is None:
            return {"reply": reply, "emotion_tag": emotion_tag, "emotion_score": emotion_score,
                    "risk_level": risk_level, "alert_created": False, "warning": "未找到学生档案"}

        # 3. 更新画像（每次必做）
        psych_service = StudentPsychService(db)
        psych_service.update_emotion(
            current_user_id=user_id, current_user_type="admin",
            student_id=student.id,
            data=EmotionUpdateRequest(
                emotion_tag=emotion_tag, emotion_score=emotion_score,
                risk_level=risk_level, summary=f"情绪对话：{message[:200]}",
            ),
        )

        # 4. 高危 → 创建预警 + 分配老师
        alert_created = False
        assigned_teacher = None
        if risk_level in ("high", "critical"):
            alert = psych_service.create_alert(
                current_user_id=1, current_user_type="admin",
                data=PsychAlertCreateRequest(
                    student_id=student.id,
                    trigger_reason=f"AI 心理对话检测到{risk_level}风险：{message[:300]}",
                    risk_level=risk_level,
                ),
            )
            alert_created = True
            assignee_id = student.teacher_employee_id or student.counselor_employee_id
            if assignee_id:
                from backend.app.daos.student_psych_dao import StudentPsychDao
                StudentPsychDao(db).update_alert(alert.id, teacher_employee_id=assignee_id)
                db.commit()
                emp = db.query(EmployeeProfile).filter(EmployeeProfile.id == assignee_id).first()
                if emp:
                    u = db.query(SysUser).filter(SysUser.id == emp.user_id).first()
                    assigned_teacher = u.real_name if u else None

        return {
            "reply": reply, "emotion_tag": emotion_tag, "emotion_score": emotion_score,
            "risk_level": risk_level, "alert_created": alert_created, "assigned_teacher": assigned_teacher,
        }
