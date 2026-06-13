"""后端服务的 FastAPI 应用入口。"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from backend.app.controllers.enterprise_assistant_controller import router as enterprise_assistant_router
from backend.app.controllers.voice_controller import router as voice_router
from backend.app.operations.router import router as operation_router
from backend.app.controllers.enterprise_nl2sql_controller import router as enterprise_nl2sql_router

app = FastAPI(
    title="Education Service System",
    version="0.1.0",
    description="教育服务平台后端 API。",
)

# 挂载企业管理查询助手路由，保证服务启动后即可访问该模块接口。
app.include_router(enterprise_assistant_router, prefix="/enterprise", tags=["企业智能助手模块"])
# 挂载企业业务办理助手路由。
app.include_router(operation_router, prefix="/enterprise", tags=["企业业务办理助手"])
# 挂载语音识别路由。
app.include_router(voice_router, prefix="/enterprise", tags=["语音识别"])
app.include_router(enterprise_nl2sql_router, prefix="/enterprise", tags=["企业智能助手NL2SQL模块"])

# 挂载静态文件（前端页面）
from fastapi.staticfiles import StaticFiles
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/app", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == '__main__':
    uvicorn.run('backend.app.main:app', host='0.0.0.0', port=8097, reload=True)
