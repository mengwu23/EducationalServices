"""后端服务的 FastAPI 应用入口。"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
"""教育服务系统 API 入口。"""

import sys
import uvicorn
import logging
import time
from pathlib import Path

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
from backend.app.core.logging import configure_logging, log_exception

configure_logging()
logger = logging.getLogger("app.api")

# ── 控制器路由 ──
from backend.app.controllers.academic_event_controller import router as academic_event_router
from backend.app.controllers.ai_tool_controller import router as ai_tool_router
from backend.app.controllers.application_progress_controller import router as application_progress_router
from backend.app.controllers.auth_controller import router as auth_router
from backend.app.controllers.enterprise_assistant_controller import router as enterprise_assistant_router
from backend.app.controllers.voice_controller import router as voice_router
from backend.app.operations.router import router as operation_router
from backend.app.controllers.enterprise_nl2sql_controller import router as enterprise_nl2sql_router
from backend.app.controllers.report_controller import router as report_router
from backend.app.controllers.student_assistant_controller import router as student_assistant_router
from backend.app.controllers.student_feedback_ticket_controller import router as student_feedback_ticket_router
from backend.app.controllers.student_leave_controller import router as student_leave_router
from backend.app.controllers.student_psych_controller import router as student_psych_router
from backend.app.controllers.service_agent_controller import router as service_agent_router
from backend.app.controllers.customer_judgement_controller import router as customer_judgement_router

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


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_exception(
            logger,
            f"请求处理异常 | {request.method} {request.url.path} | 耗时 {duration_ms:.2f} ms",
            exc,
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "请求完成 | %s %s | 状态码 %s | 耗时 %.2f ms | 客户端 %s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request.client.host if request.client else "-",
    )
    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    if exc.status_code >= 500:
        log_exception(logger, f"业务异常 | {request.method} {request.url.path}", exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=exc.code, message=exc.message).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code >= 500:
        log_exception(logger, f"HTTP 异常 | {request.method} {request.url.path}", exc)
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

app.include_router(auth_router, prefix="/api")
app.include_router(student_leave_router)
app.include_router(student_psych_router)
app.include_router(student_assistant_router)
app.include_router(report_router)
app.include_router(academic_event_router, prefix="/api")
app.include_router(application_progress_router)
app.include_router(student_feedback_ticket_router, prefix="/api")
app.include_router(ai_tool_router, prefix="/api")
app.include_router(ai_tool_router, prefix="/api/v1")
# 兼容线上已发布 Dify 工作流的回调路径（/ai-tools 段）
app.include_router(ai_tool_router, prefix="/api/ai-tools")
app.include_router(ai_tool_router, prefix="/api/v1/ai-tools")


def create_app() -> FastAPI:
    return app

# 挂载企业管理查询助手路由，保证服务启动后即可访问该模块接口。
app.include_router(enterprise_assistant_router, prefix="/enterprise", tags=["企业智能助手模块"])
# 挂载企业业务办理助手路由。
app.include_router(operation_router, prefix="/enterprise", tags=["企业业务办理助手"])
# 挂载语音识别路由。
app.include_router(voice_router, prefix="/enterprise", tags=["语音识别"])
app.include_router(enterprise_nl2sql_router, prefix="/enterprise", tags=["企业智能助手NL2SQL模块"])
app.include_router(service_agent_router, prefix="/api", tags=["客服Agent模块"])
app.include_router(customer_judgement_router, tags=["客户研判模块"])

# 挂载静态文件（前端页面）
from fastapi.staticfiles import StaticFiles
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/app", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
