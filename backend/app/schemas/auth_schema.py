from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=80, description="登录账号")
    password: str = Field(..., min_length=1, max_length=128, description="登录密码")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌有效期，单位：秒")
    user: dict = Field(..., description="当前用户信息")


class CurrentUserResponse(BaseModel):
    id: int = Field(..., description="用户 ID，对应 sys_user.id")
    role: str = Field(..., description="当前有效角色")
    username: str | None = Field(default=None, description="登录账号")
    real_name: str | None = Field(default=None, description="真实姓名")
    user_type: str | None = Field(default=None, description="用户类型：admin/employee/student/customer")
    role_code: str | None = Field(default=None, description="员工角色编码")
    employee_id: int | None = Field(default=None, description="员工档案 ID")
    student_id: int | None = Field(default=None, description="学生档案 ID")
    department_id: int | None = Field(default=None, description="所属部门 ID")
    permissions: tuple[str, ...] = Field(default=(), description="当前用户拥有的权限码")


class PermissionResponse(BaseModel):
    role: str = Field(..., description="当前有效角色")
    permissions: tuple[str, ...] = Field(..., description="当前用户拥有的权限码")
