"""学生成绩录入处理器。

关键设计：
- 一条自然语言可录入多个科目的成绩
- 会先按学生姓名查找匹配
- 同名学生需用户选择
- 成绩范围校验 0-100
"""

from typing import Any, Dict, List, Optional

from backend.app.common.enums import DraftStatus
from backend.app.core.security import CurrentUser
from backend.app.models.draft import AiDraft

from ..base_handler import OperationHandler
from ..llm_client import OperationLlmClient
from ..operation_dao import OperationDao
from ..schemas import (
    CandidateItem,
    ConfirmationCard,
    ExecuteResult,
    FieldItem,
    MissingField,
    OperationResponse,
)
from ..intent_schemas import ENTER_STUDENT_SCORE_SCHEMA, IntentSchema


class EnterStudentScoreHandler(OperationHandler):
    """学生成绩录入处理器。"""

    def __init__(self, db_session, llm_client: Optional[OperationLlmClient] = None):
        self.dao = OperationDao(db_session)
        self.llm = llm_client or OperationLlmClient()
        self._card_title = "成绩录入确认"

    @property
    def intent(self) -> str:
        return "enter_student_score"

    @property
    def schema(self) -> IntentSchema:
        return ENTER_STUDENT_SCORE_SCHEMA

    # 除 is_delete、create_time、update_time 外，所有表字段都必须填写
    _SCORE_REQUIRED_FIELDS = [
        ("exam_type", "考试类型", "请输入考试类型（如模考/期中/期末/补考）"),
        ("semester", "学期", "请输入学期（如2026春季）"),
        ("exam_date", "考试日期", "请输入考试日期（如2026-06-10）"),
        ("remark", "备注", "请输入成绩备注（如模考成绩表现稳定）"),
    ]

    def create_draft(self, params: Dict[str, Any], user: CurrentUser) -> OperationResponse:
        # 归一化 scores：兼容 DeepSeek 返回的 {course_name, score} 单值格式
        params["_scores"] = params.get("_scores", [])
        if not params["_scores"] and params.get("course_name") and params.get("score"):
            try:
                params["_scores"] = [{"course_name": params["course_name"], "score": float(params["score"])}]
            except (ValueError, TypeError):
                pass

        # 第一步：校验基础必填（学生姓名、成绩）
        missing = self._check_base_required(params)
        if missing:
            return self._build_missing_response(missing)

        student_name = params["student_name"]
        scores = params["_scores"]
        if not scores:
            return OperationResponse(
                status="failed", message="未能从输入中识别出科目和成绩",
                intent=self.intent,
            )

        # 第二步：校验表字段完整性（exam_type, semester, exam_date, remark）
        missing_fields = self._check_score_fields(params)
        if missing_fields:
            return self._build_missing_response(missing_fields)

        # 查找学生
        students = self.dao.find_students_by_name(student_name)
        if not students:
            return OperationResponse(
                status="failed", message=f"未找到名为「{student_name}」的学生",
                intent=self.intent,
            )
        if len(students) > 1:
            return self._build_student_selection(students, params, user)

        student = students[0]

        # 校验成绩范围
        for s in scores:
            if s["score"] < 0 or s["score"] > 100:
                return OperationResponse(
                    status="failed",
                    message=f"成绩「{s['course_name']}: {s['score']}」超出有效范围（0-100）",
                    intent=self.intent,
                )

        draft_content = {
            "_intent": self.intent,
            "student_id": student.id,
            "student_name": student.student_name,
            "exam_type": params.get("exam_type"),
            "exam_date": params.get("exam_date"),
            "semester": params.get("semester"),
            "remark": params.get("remark"),
            "scores": scores,
        }
        draft = self.dao.create_draft(
            intent=self.intent, content_json=draft_content,
            created_by=user.id, status=DraftStatus.PENDING_CONFIRM,
        )
        return self._build_confirm(draft, student, scores, params)

    def supplement(self, draft: AiDraft, query: str, user: CurrentUser) -> OperationResponse:
        content = dict(draft.content_json)
        state = content.get("_state", "")

        if state == "student_selection":
            return self._handle_selection(draft, query, user)

        merged = self.llm.supplement_fields(query, content)
        self.dao.update_draft_content(draft, merged)
        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)

        student_name = merged.get("student_name", "")
        students = self.dao.find_students_by_name(student_name)
        student = students[0] if students else None
        return self._build_confirm(draft, student, merged.get("scores", []), merged)

    def execute(self, draft: AiDraft, user: CurrentUser) -> ExecuteResult:
        content = dict(draft.content_json)
        student_id = content.get("student_id")
        exam_type = content.get("exam_type")
        semester = content.get("semester")
        exam_date = content.get("exam_date")
        remark = content.get("remark")
        scores_list = content.get("scores", [])
        operator_id = None

        emp = self.dao.get_employee_by_user_id(user.id)
        if emp:
            operator_id = emp.id

        inserted_ids = []
        for s in scores_list:
            score_rec = self.dao.create_student_score(
                student_id=student_id,
                course_name=s["course_name"],
                score=s["score"],
                exam_type=exam_type,
                semester=semester,
                exam_date=exam_date,
                remark=remark,
                operator_employee_id=operator_id,
            )
            inserted_ids.append(score_rec.id)

        self.dao.update_draft_status(
            draft, status=DraftStatus.CONFIRMED, confirmed_by=user.id,
        )
        self.dao.add_audit_log(
            operator_user_id=user.id, action_type="create",
            biz_module="enterprise_operation",
            biz_object_type="student_score",
            biz_object_id=inserted_ids[0] if inserted_ids else None,
            after_json={"count": len(inserted_ids), "scores": scores_list, "student_id": student_id},
            draft_id=draft.id,
        )

        student_name = content.get("student_name", "")
        return ExecuteResult(
            status="success",
            message=f"已为「{student_name}」录入 {len(inserted_ids)} 科成绩",
            biz_object_type="student_score",
            biz_object_id=inserted_ids[0] if inserted_ids else None,
            details={"student_name": student_name, "count": len(inserted_ids), "score_ids": inserted_ids},
        )

    # ---------- internal ----------

    def _check_base_required(self, params: Dict[str, Any]) -> List[MissingField]:
        """校验基础必填：学生姓名、成绩。"""
        missing = []
        for key in self.schema.required_keys:
            if key in ("course_name", "score"):
                continue  # 用 _scores 替代校验
            value = params.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(MissingField(key=key, label=self.get_field_label(key), question=f"请输入{self.get_field_label(key)}"))
        if not params.get("_scores"):
            missing.append(MissingField(key="score", label="成绩", question="请输入科目和成绩"))
        return missing

    def _check_score_fields(self, params: Dict[str, Any]) -> List[MissingField]:
        """校验 student_score 表的完整字段。"""
        missing = []
        for key, label, question in self._SCORE_REQUIRED_FIELDS:
            value = params.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(MissingField(key=key, label=label, question=question))
        return missing

    def _build_student_selection(self, students, params, user):
        candidates = [CandidateItem(id=s.id, label=f"{s.student_name}（{s.current_school or '未知学校'}）") for s in students]
        draft_content = {"_intent": self.intent, "_state": "student_selection", "student_name": params.get("student_name"),
                         "exam_type": params.get("exam_type"), "exam_date": params.get("exam_date"),
                         "semester": params.get("semester"), "remark": params.get("remark"),
                         "scores": params.get("_scores", []),
                         "_candidates": [{"id": c.id, "label": c.label} for c in candidates]}
        draft = self.dao.create_draft(intent=self.intent, content_json=draft_content, created_by=user.id, status=DraftStatus.GENERATING)
        return OperationResponse(status="requires_selection", message=f"找到多个名为「{params.get('student_name','')}」的学生",
                                 draft_id=draft.id, intent=self.intent, selection_type="student_selection",
                                 candidates=candidates, question="请选择学生")

    def _handle_selection(self, draft, query, user):
        import re
        content = dict(draft.content_json)
        candidates_data = content.get("_candidates", [])
        idx_match = re.search(r"第[零一二三四五六七八九十\d]+[个个位]", query)
        selected = None
        if idx_match:
            idx_text = idx_match.group(0)
            idx = self._chinese_to_int(idx_text)
            if idx and 0 < idx <= len(candidates_data):
                from backend.app.models.student_profile import StudentProfile
                from sqlalchemy import select
                stmt = select(StudentProfile).where(StudentProfile.id == candidates_data[idx - 1]["id"])
                selected = self.dao.db.scalar(stmt)
        if not selected:
            return OperationResponse(status="requires_selection", candidates=[CandidateItem(**c) for c in candidates_data],
                                     question="请选择学生（回复序号）", draft_id=draft.id, intent=self.intent, selection_type="student_selection")

        content["student_id"] = selected.id
        content["_state"] = ""
        self.dao.update_draft_content(draft, content)
        self.dao.update_draft_status(draft, DraftStatus.PENDING_CONFIRM)
        return self._build_confirm(draft, selected, content.get("scores", []), content)

    def _build_confirm(self, draft, student, scores_list, params):
        fields = [FieldItem(key="student_name", label="学生姓名", value=student.student_name, required=True, editable=False)]
        if params.get("exam_type"):
            fields.append(FieldItem(key="exam_type", label="考试类型", value=params["exam_type"], required=False))
        for s in scores_list:
            fields.append(FieldItem(key=f"score_{s['course_name']}", label=s["course_name"], value=str(s["score"]), required=True))
        if params.get("semester"):
            fields.append(FieldItem(key="semester", label="学期", value=params["semester"], required=False))
        if params.get("exam_date"):
            fields.append(FieldItem(key="exam_date", label="考试日期", value=params["exam_date"], required=False))
        if params.get("remark"):
            fields.append(FieldItem(key="remark", label="备注", value=params["remark"], required=False))
        score_texts = [s["course_name"] + " " + str(s["score"]) + "分" for s in scores_list]
        summary = student.student_name + "：" + "，".join(score_texts)
        return OperationResponse(status="pending_confirm", message=f"AI已识别你要为「{student.student_name}」录入成绩",
                                 draft_id=draft.id, intent=self.intent,
                                 confirmation_card=ConfirmationCard(title=self._card_title, intent=self.intent, fields=fields, summary=summary))

    @staticmethod
    def _chinese_to_int(text: str) -> Optional[int]:
        cn_map = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
        import re
        digits = re.findall(r"[一二三四五六七八九十\d]", text)
        if not digits:
            return None
        if digits[0].isdigit():
            return int(digits[0])
        return cn_map.get(digits[0])

    def _build_missing_response(self, missing):
        return OperationResponse(status="missing_fields", message=f"请补充：{', '.join(m.label for m in missing)}",
                                 intent=self.intent, missing_fields=missing)
