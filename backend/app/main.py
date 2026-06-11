"""教育服务系统 API 入口。"""

import os
import uvicorn
import sys
from pathlib import Path

# ── 数据库配置（在导入业务模块前设置）──
os.environ.setdefault(
    "DATABASE_URL",
    "mysql+pymysql://root:123456@localhost:3306/education_service_ai",
)

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.common.exceptions import AppException
from backend.app.common.responses import ApiResponse, error_response, success_response

# ── 控制器路由 ──
from backend.app.controllers.academic_event_controller import router as academic_event_router
from backend.app.controllers.ai_tool_controller import router as ai_tool_router
from backend.app.controllers.application_progress_controller import router as application_progress_router
from backend.app.controllers.enterprise_assistant_controller import router as enterprise_assistant_router
from backend.app.controllers.enterprise_nl2sql_controller import router as enterprise_nl2sql_router
from backend.app.controllers.report_controller import router as report_router
from backend.app.controllers.student_assistant_controller import router as student_assistant_router
from backend.app.controllers.student_feedback_ticket_controller import router as student_feedback_ticket_router
from backend.app.controllers.student_leave_controller import router as student_leave_router
from backend.app.controllers.student_psych_controller import router as student_psych_router

# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title="教育服务系统 API",
    description="教育服务系统后端接口文档",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 异常处理 ──

def _json_error(status_code: int, code: int, message: str, data=None):
    return JSONResponse(status_code=status_code, content=error_response(code=code, message=message, data=data).model_dump())


@app.exception_handler(AppException)
async def _app_exception_handler(request: Request, exc: AppException):
    return _json_error(exc.status_code, exc.code, exc.message)


@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
    msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return _json_error(exc.status_code, exc.status_code, msg)


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(request: Request, exc: RequestValidationError):
    return _json_error(422, 422, "参数校验失败", jsonable_encoder(exc.errors()))


# ── 系统 ──

@app.get("/health", tags=["系统"], response_model=ApiResponse)
async def health_check():
    return success_response(data={
        "status": "ok",
        "service": "education-service",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
    })


# ── 路由注册 ──

_ROUTES = [
    # (router, prefix)
    (student_leave_router,            ""),
    (student_psych_router,            ""),
    (student_assistant_router,        ""),
    (enterprise_assistant_router,     ""),
    (enterprise_nl2sql_router,        ""),
    (report_router,                   ""),
    (application_progress_router,     ""),
    (academic_event_router,           "/api"),
    (student_feedback_ticket_router,  "/api"),
    (ai_tool_router,                  "/api"),
    (ai_tool_router,                  "/api/v1"),
]

for router, prefix in _ROUTES:
    kwargs = {"prefix": prefix} if prefix else {}
    app.include_router(router, **kwargs)


def create_app() -> FastAPI:
    return app


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
