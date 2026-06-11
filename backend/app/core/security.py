"""权限模块（前期统一返回默认用户，权限上线后启用 Header 鉴权）。"""
from dataclasses import dataclass
from secrets import compare_digest

from fastapi import Depends

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
