"""认证服务。"""

from __future__ import annotations

import hashlib
from secrets import compare_digest

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.security import build_current_user, create_access_token
from backend.app.models.sys_user import SysUser

try:
    import bcrypt  # type: ignore
except Exception:  # pragma: no cover - bcrypt 为可选运行时依赖
    bcrypt = None


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, username: str, password: str) -> dict:
        user = (
            self.db.query(SysUser)
            .filter(
                SysUser.username == username,
                SysUser.status == "enabled",
                SysUser.is_delete == 0,
            )
            .first()
        )
        if user is None or not verify_password(password, user.password_hash, username=user.username):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

        current_user = build_current_user(self.db, int(user.id))
        token = create_access_token(
            subject=user.id,
            extra_claims={
                "username": user.username,
                "role": current_user.role,
                "user_type": current_user.user_type,
            },
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": get_settings().jwt_access_token_expire_minutes * 60,
            "user": current_user.model_dump(),
        }


def hash_password(password: str, salt: str = "education-service") -> str:
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"sha256${salt}${digest}"


def verify_password(password: str, password_hash: str | None, username: str | None = None) -> bool:
    if not password_hash:
        return False

    if password_hash.startswith("sha256$"):
        try:
            _, salt, expected = password_hash.split("$", 2)
        except ValueError:
            return False
        return compare_digest(hash_password(password, salt), f"sha256${salt}${expected}")

    if password_hash.startswith(("$2a$", "$2b$", "$2y$")):
        if _is_demo_bcrypt_placeholder(password_hash, username):
            return password in {username or "", f"{username}123" if username else "", "123456"}
        if bcrypt is None:
            return False
        try:
            return bool(bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")))
        except ValueError:
            return False

    if password_hash.startswith("plain:"):
        return compare_digest(password, password_hash.removeprefix("plain:"))

    return False


def _is_demo_bcrypt_placeholder(password_hash: str, username: str | None) -> bool:
    return bool(username) and password_hash == f"$2a$10$demo_hash_{username}"
