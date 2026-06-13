from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.common.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.session import get_db
from backend.app.schemas.auth_schema import CurrentUserResponse, LoginRequest, PermissionResponse, TokenResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证授权"])


@router.post("/login", summary="用户登录", description="使用用户名和密码登录，成功后返回 JWT 访问令牌和当前用户信息。")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    data = AuthService(db).login(request.username, request.password)
    return success(TokenResponse(**data).model_dump())


@router.get("/me", summary="获取当前用户信息", description="根据 Bearer Token 或开发测试凭证解析当前登录用户。")
def me(user: CurrentUser = Depends(get_current_user)):
    return success(CurrentUserResponse(**user.model_dump()).model_dump())


@router.get("/permissions", summary="获取当前用户权限", description="返回当前用户的有效角色和权限码列表，供前端菜单、按钮和路由控制使用。")
def permissions(user: CurrentUser = Depends(get_current_user)):
    return success(PermissionResponse(role=user.role, permissions=user.permissions).model_dump())
