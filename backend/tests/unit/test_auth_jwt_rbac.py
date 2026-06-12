import pytest
from fastapi import HTTPException

from backend.app.core.security import CurrentUser, require_any_permission, require_permissions, require_roles
from backend.app.models.sys_user import SysUser
from backend.app.services.auth_service import hash_password


def _set_password(db_session, username: str, password: str) -> None:
    user = db_session.query(SysUser).filter(SysUser.username == username).one()
    user.password_hash = hash_password(password, salt=f"test-{username}")
    db_session.commit()


def test_login_issues_token_and_me_returns_current_user(client, db_session):
    _set_password(db_session, "employee", "secret123")

    response = client.post("/api/auth/login", json={"username": "employee", "password": "secret123"})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    token = body["data"]["access_token"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["role"] == "employee"
    assert body["data"]["user"]["employee_id"] == 1

    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    me = me_response.json()["data"]
    assert me["id"] == 2
    assert me["username"] == "employee"
    assert me["role"] == "employee"
    assert me["role_code"] == "service"
    assert "report:read" in me["permissions"]

    permissions_response = client.get("/api/auth/permissions", headers={"Authorization": f"Bearer {token}"})
    assert permissions_response.status_code == 200
    assert "report:generate" in permissions_response.json()["data"]["permissions"]


def test_login_rejects_wrong_password(client, db_session):
    _set_password(db_session, "admin", "secret123")

    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["code"] == 401


def test_me_requires_token_or_dev_header(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == 401


def test_dev_header_fallback_keeps_existing_regression_headers(client):
    response = client.get("/api/auth/me", headers={"X-User-Id": "2", "X-User-Role": "admin"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 2
    assert data["role"] == "admin"
    assert data["user_type"] == "employee"
    assert "*" in data["permissions"]


def test_dev_query_fallback_keeps_student_module_compatibility(client):
    response = client.get("/api/auth/me?user_id=3&user_type=student")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 3
    assert data["role"] == "student"
    assert "student_leave:own" in data["permissions"]


def test_require_roles_allows_and_rejects():
    require_roles(CurrentUser(id=1, role="admin"), {"admin"})

    with pytest.raises(HTTPException) as exc_info:
        require_roles(CurrentUser(id=2, role="employee"), {"admin"})
    assert exc_info.value.status_code == 403


def test_require_permissions_allows_admin_wildcard_and_rejects_missing_permission():
    admin_dependency = require_permissions("report:review")
    assert admin_dependency(CurrentUser(id=1, role="admin", permissions=("*",))).id == 1

    employee_dependency = require_permissions("report:review")
    with pytest.raises(HTTPException) as exc_info:
        employee_dependency(CurrentUser(id=2, role="employee", permissions=("report:read",)))
    assert exc_info.value.status_code == 403


def test_require_any_permission_accepts_one_matching_permission():
    dependency = require_any_permission("student_leave:own", "student_leave:read")
    user = CurrentUser(id=3, role="student", permissions=("student_leave:own",))

    assert dependency(user).id == 3


def test_report_route_rejects_student_without_report_permission(client):
    response = client.get("/api/v1/reports", headers={"X-User-Id": "3", "X-User-Role": "student"})

    assert response.status_code == 403
    assert response.json()["code"] == 403


def test_openapi_exposes_bearer_authorize_lock(client):
    schema = client.get("/openapi.json").json()

    assert schema["components"]["securitySchemes"]["JWT认证"]["type"] == "http"
    assert schema["components"]["securitySchemes"]["JWT认证"]["scheme"] == "bearer"
    assert "security" not in schema["paths"]["/api/auth/login"]["post"]
    assert schema["paths"]["/api/auth/me"]["get"]["security"] == [{"JWT认证": []}]
    assert schema["paths"]["/api/v1/reports"]["get"]["security"] == [{"JWT认证": []}]
