from dataclasses import dataclass
from secrets import compare_digest

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str


def get_current_user(
    x_user_id: int = Header(default=1, alias="X-User-Id"),
    x_user_role: str = Header(default="admin", alias="X-User-Role"),
) -> CurrentUser:
    return CurrentUser(id=x_user_id, role=x_user_role.lower())


def require_roles(user: CurrentUser, allowed_roles: set[str]) -> None:
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前角色无权访问该接口",
        )


def verify_ai_tools_secret(
    x_ai_tools_secret: str | None = Header(default=None, alias="X-AI-Tools-Secret"),
) -> None:
    expected_secret = get_settings().ai_tools_secret
    if not expected_secret:
        return
    if not x_ai_tools_secret or not compare_digest(x_ai_tools_secret, expected_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AI Tools 调用密钥无效",
        )
