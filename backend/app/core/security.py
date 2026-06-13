"""认证与权限辅助函数。"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass
from secrets import compare_digest
from typing import Any

from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, Query, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.employee_profile import EmployeeProfile
from backend.app.models.student_profile import StudentProfile
from backend.app.models.sys_user import SysUser


bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="JWT认证",
    description="请输入登录接口返回的 access_token，不需要填写 Bearer 前缀。",
)


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str
    username: str | None = None
    real_name: str | None = None
    user_type: str | None = None
    role_code: str | None = None
    employee_id: int | None = None
    student_id: int | None = None
    department_id: int | None = None
    permissions: tuple[str, ...] = ()

    @property
    def user_id(self) -> int:
        return self.id

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


ROLE_PERMISSION_MAP: dict[str, set[str]] = {
    "admin": {"*"},
    "manager": {
        "report:read",
        "report:generate",
        "report:review",
        "report:export",
        "customer_judgement:read",
        "customer_judgement:write",
        "enterprise_operation:execute",
        "student_leave:read",
        "student_leave:approve",
        "student_psych:read",
        "student_psych:manage",
    },
    "employee": {
        "report:read",
        "report:generate",
        "report:export",
        "customer_judgement:read",
        "customer_judgement:write",
        "enterprise_operation:execute",
        "student_leave:read",
        "student_leave:approve",
        "student_psych:read",
        "student_psych:manage",
    },
    "student": {
        "student_leave:own",
        "student_psych:own",
    },
}


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def create_access_token(subject: int | str, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    if settings.jwt_algorithm != "HS256":
        raise RuntimeError("内置认证工具仅支持 HS256 JWT")

    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + settings.jwt_access_token_expire_minutes * 60,
    }
    if extra_claims:
        payload.update(extra_claims)

    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}"
        header = json.loads(_b64url_decode(header_segment))
        payload = json.loads(_b64url_decode(payload_segment))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌") from exc

    if header.get("alg") != "HS256":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="不支持的认证令牌算法")

    expected = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    try:
        actual = _b64url_decode(signature_segment)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌签名") from exc
    if not compare_digest(actual, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌签名")

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证令牌已过期")
    return payload


def build_current_user(db: Session, user_id: int, role_override: str | None = None) -> CurrentUser:
    user = (
        db.query(SysUser)
        .filter(SysUser.id == user_id, SysUser.is_delete == 0, SysUser.status == "enabled")
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已停用")

    employee = None
    student = None
    if user.user_type == "employee":
        employee = (
            db.query(EmployeeProfile)
            .filter(EmployeeProfile.user_id == user.id, EmployeeProfile.is_delete == 0, EmployeeProfile.status == "active")
            .first()
        )
    elif user.user_type == "student":
        student = (
            db.query(StudentProfile)
            .filter(StudentProfile.user_id == user.id, StudentProfile.is_delete == 0, StudentProfile.status == "active")
            .first()
        )

    role = role_override or _resolve_effective_role(user.user_type, employee.role_code if employee else None)
    permissions = tuple(sorted(resolve_permissions(role)))
    return CurrentUser(
        id=int(user.id),
        role=role,
        username=user.username,
        real_name=user.real_name,
        user_type=user.user_type,
        role_code=employee.role_code if employee else None,
        employee_id=int(employee.id) if employee else None,
        student_id=int(student.id) if student else None,
        department_id=int(employee.department_id) if employee and employee.department_id is not None else None,
        permissions=permissions,
    )


def _resolve_effective_role(user_type: str, role_code: str | None) -> str:
    if user_type == "admin":
        return "admin"
    if user_type == "employee":
        return role_code if role_code in {"admin", "manager"} else "employee"
    if user_type == "student":
        return "student"
    return user_type


def resolve_permissions(role: str) -> set[str]:
    return set(ROLE_PERMISSION_MAP.get(role, set()))


def has_permission(user: CurrentUser, permission: str) -> bool:
    user_permissions = set(user.permissions) if user.permissions else resolve_permissions(user.role)
    return "*" in user_permissions or permission in user_permissions


def require_permissions(*required_permissions: str) -> Callable[[CurrentUser], CurrentUser]:
    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        missing = [permission for permission in required_permissions if not has_permission(user, permission)]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {missing}",
            )
        return user

    return dependency


def require_any_permission(*allowed_permissions: str) -> Callable[[CurrentUser], CurrentUser]:
    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if any(has_permission(user, permission) for permission in allowed_permissions):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少权限: {list(allowed_permissions)}",
        )

    return dependency


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    dev_user_id: int | None = Query(default=None, alias="user_id"),
    dev_user_type: str | None = Query(default=None, alias="user_type"),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """从 JWT 解析当前用户，并兼容旧的开发测试凭证。"""
    if credentials:
        if credentials.scheme.lower() != "bearer" or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证头格式应为 Bearer token")
        payload = decode_access_token(credentials.credentials)
        try:
            user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证令牌缺少用户标识") from exc
        return build_current_user(db, user_id)

    settings = get_settings()
    if settings.auth_dev_header_enabled and x_user_id:
        try:
            user_id = int(x_user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Id 必须是数字") from exc
        return build_current_user(db, user_id, role_override=x_user_role)

    if settings.auth_dev_header_enabled and dev_user_id is not None:
        return build_current_user(db, dev_user_id, role_override=dev_user_type)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证凭证")


def require_roles(user: CurrentUser, allowed_roles: set[str]) -> None:
    """校验用户是否拥有允许的有效角色。"""
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"角色 {user.role} 无权限执行此操作，需要以下角色之一: {allowed_roles}",
        )


def require_roles(user: CurrentUser, allowed_roles: set[str]) -> None:
    """校验用户角色，不在允许列表中则抛出 403。"""
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"无权操作，需要角色: {', '.join(allowed_roles)}",
        )


def verify_ai_tools_secret(
    request: Request,
    x_ai_tools_secret: str = Header(default="", alias="X-AI-Tools-Secret"),
) -> None:
    """校验 AI Tools 共享密钥。"""
    settings = get_settings()
    if not settings.ai_tools_secret:
        return
    if not compare_digest(x_ai_tools_secret, settings.ai_tools_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AI Tools 密钥无效")
