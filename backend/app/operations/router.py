"""企业业务办理助手的 HTTP 接口。

提供两个统一端点：
- POST /execute : 解析自然语言，返回确认卡片或追问
- POST /confirm : 确认/拒绝草稿，执行写库
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.security import CurrentUser, require_permissions
from backend.app.database import get_db

from .dependence import get_orchestrator
from .orchestrator import OperationOrchestrator
from .schemas import ConfirmRequest, ExecuteRequest, ExecuteResult, OperationResponse

router = APIRouter(prefix="/api/v1/enterprise-operation", tags=["企业业务办理助手"])


def success_response(data, trace_id: str | None = None):
    """统一成功响应包装。"""
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "trace_id": trace_id,
    }


def _commit(db: Session) -> None:
    """提交数据库事务，确保跨会话可见。"""
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.post("/execute", summary="执行自然语言业务操作",
             description="""
接收自然语言 query，经 DeepSeek 大模型解析 → 意图路由 → 字段校验 → 返回确认卡片或追问。

---

## 功能 1：意向客户录入

```json
{"query": "新增客户，王一鸣，本科大三，想去英国读硕士，预算30万，电话13700030001，来源官网咨询"}
{"query": "帮我新增一个 同学：涂丽同学，本科毕业，想去沃林进修，预算10w，电话19749721947，来源微信朋友圈"}
```

## 功能 2：客户状态更新

```json
{"query": "把王一鸣改成已签约"}
{"query": "把李思琪改成已流失，原因预算不足"}
```

## 功能 3：口述日报提交

```json
{"query": "日报：今天跟进了5个客户，王一鸣已签约，明天准备推进李思琪"}
```

## 功能 4：学生成绩录入

```json
{"query": "给张明录入成绩，雅思听力7.5分，学期2026春季，考试日期2026-06-10，备注模考表现稳定"}
{"query": "给李雨录入模考成绩，阅读6分，写作6分，学期2026春季，考试日期2026-06-11，备注模考训练"}
```

## 功能 5：请假审批

```json
{"query": "同意周琪的请假"}
{"query": "驳回孙悦的请假"}
```

## 功能 6：投诉反馈处理

```json
{"query": "把王璐的投诉改为处理中"}
{"query": "处理方案是已发送材料清单，将刘洋的投诉改为已解决"}
```
""")
def execute_operation(
    req: ExecuteRequest,
    user: CurrentUser = Depends(require_permissions("enterprise_operation:execute")),
    orchestrator: OperationOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db),
):
    data = orchestrator.execute(req, user)
    # 创建草稿后提交，确保后续 confirm 能读到
    if data.draft_id:
        _commit(db)
    return success_response(data)


@router.post("/confirm", summary="确认或拒绝操作草稿",description='confirm确认，reject拒绝')
def confirm_operation(
    req: ConfirmRequest,
    user: CurrentUser = Depends(require_permissions("enterprise_operation:execute")),
    orchestrator: OperationOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db),
):
    data = orchestrator.confirm(req, user)
    if data.status == "success":
        _commit(db)
    return success_response(data)
