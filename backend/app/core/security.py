"""权限模块（前期统一返回默认用户，权限上线后启用 Header 鉴权）。"""
from dataclasses import dataclass
from secrets import compare_digest

from fastapi import Header, HTTPException, Request, status

from backend.app.core.config import get_settings


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str


# 默认用户：对应 sys_user.id=1（员工 高远，总裁办总经理）
# 权限模块上线后改为从 X-User-Id / X-User-Role Header 读取
_DEFAULT_USER = CurrentUser(id=1, role="employee")


def get_current_user() -> CurrentUser:
    """返回当前登录用户（未上线权限模块时使用默认用户）。"""
    return _DEFAULT_USER


def verify_ai_tools_secret(
    request: Request,
    x_ai_tools_secret: str = Header(default="", alias="X-AI-Tools-Secret"),
) -> None:
    """校验 AI Tools 接口密钥。"""
    settings = get_settings()
    if not settings.ai_tools_secret:
        return
    if not compare_digest(x_ai_tools_secret, settings.ai_tools_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AI Tools 密钥无效")