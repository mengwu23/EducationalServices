"""
FastAPI 应用入口
=================

负责创建 FastAPI 实例、注册路由、异常处理器和中间件。

当前已注册的路由：
    - /api/v1/student-assistant/leaves/*  — 学生请假审批模块
    - /api/v1/student-assistant/psych/*   — 心理关怀模块

待注册（后续模块逐步加入）：
    - /api/v1/student-assistant/complaints  — 投诉建议
    - /api/v1/student-assistant/scores      — 成绩查询
    - /api/v1/student-assistant/events      — 考务查询
    - /api/v1/student-assistant/progress    — 申请进度
    - /api/v1/student-assistant/messages    — AI 聊天
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.common.exceptions import AppException
from app.common.responses import error_response
from app.controllers.student_leave_controller import router as student_leave_router
from app.controllers.student_psych_controller import router as student_psych_router

# ============================================================
# 创建 FastAPI 应用实例
# ============================================================

app = FastAPI(
    title="教育服务系统 API",
    description="教育服务系统后端接口文档 — 学生智能助手模块",
    version="0.1.0",
    docs_url="/docs",           # Swagger UI 地址：http://127.0.0.1:8000/docs
    redoc_url="/redoc",         # ReDoc 地址：http://127.0.0.1:8000/redoc
)

# ============================================================
# CORS 中间件（允许前端开发时跨域访问）
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 开发阶段允许所有来源，上线后需收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 全局异常处理器
# ============================================================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """捕获所有 AppException 及其子类，返回统一错误响应格式

    这样 Controller 中抛出 AppException 时，无需在每个方法中写 try-except，
    异常会直接冒泡到这里被统一处理。
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=exc.code, message=exc.message).model_dump(),
    )

# ============================================================
# 健康检查接口
# ============================================================

@app.get("/health", tags=["系统"])
async def health_check():
    """服务健康检查

    用于负载均衡或 Docker 健康检查。返回当前服务状态和时间。
    """
    from datetime import datetime
    return {
        "status": "ok",
        "service": "education-service",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
    }

# ============================================================
# 注册路由
# ============================================================
# 每完成一个新模块，在这里添加一行 app.include_router(...)

app.include_router(student_leave_router)
app.include_router(student_psych_router)

app.include_router(academic_event_router, prefix="/api")
app.include_router(student_feedback_ticket_router, prefix="/api")
app.include_router(ai_tool_router, prefix="/api")

# ============================================================
# 启动提示
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,        # 开发模式：代码变更自动重启
    )
