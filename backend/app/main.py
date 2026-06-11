import os
import sys
from pathlib import Path

# ── 数据库配置 ──────────────────────────────────────────────
# 在导入其他模块前设置 DATABASE_URL，确保 database.py 能读取到
# 配置来源：项目根 backend/database.py 中的硬编码连接信息
os.environ.setdefault(
    "DATABASE_URL",
    "mysql+pymysql://root:123456@localhost:3306/education_service_ai",
)

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.common.exceptions import AppException
from backend.app.common.responses import ApiResponse, error_response, success_response
from backend.app.controllers.academic_event_controller import router as academic_event_router
from backend.app.controllers.application_progress_controller import (
    router as application_progress_router,
)
from backend.app.controllers.ai_tool_controller import router as ai_tool_router
from backend.app.controllers.enterprise_assistant_controller import (
    router as enterprise_assistant_router,
)
from backend.app.controllers.enterprise_nl2sql_controller import (
    router as enterprise_nl2sql_router,
)
from backend.app.controllers.report_controller import router as report_router
from backend.app.controllers.student_feedback_ticket_controller import (
    router as student_feedback_ticket_router,
)
from backend.app.controllers.student_leave_controller import router as student_leave_router
from backend.app.controllers.student_psych_controller import router as student_psych_router

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


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=exc.code, message=exc.message).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=exc.status_code, message=message).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(
            code=422,
            message="参数校验失败",
            data=jsonable_encoder(exc.errors()),
        ).model_dump(),
    )


@app.get("/health", tags=["系统"], response_model=ApiResponse)
async def health_check():
    from datetime import datetime

    return success_response(
        data={
            "status": "ok",
            "service": "education-service",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
        }
    )


app.include_router(student_leave_router)
app.include_router(student_psych_router)
app.include_router(enterprise_assistant_router)
app.include_router(enterprise_nl2sql_router)
app.include_router(report_router)
app.include_router(academic_event_router, prefix="/api")
app.include_router(application_progress_router)
app.include_router(student_feedback_ticket_router, prefix="/api")
app.include_router(ai_tool_router, prefix="/api")
app.include_router(ai_tool_router, prefix="/api/v1")


def create_app() -> FastAPI:
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
