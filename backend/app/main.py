"""后端服务的 FastAPI 应用入口。"""
from fastapi import FastAPI
import uvicorn
from backend.app.controllers.enterprise_assistant_controller import router as enterprise_assistant_router
from backend.app.operations.router import router as operation_router

app = FastAPI(
    title="Education Service System",
    version="0.1.0",
    description="教育服务平台后端 API。",
)

# 挂载企业管理查询助手路由，保证服务启动后即可访问该模块接口。
app.include_router(enterprise_assistant_router, prefix="/enterprise", tags=["企业智能助手模块"])
# 挂载企业业务办理助手路由。
app.include_router(operation_router, prefix="/enterprise", tags=["企业业务办理助手"])


if __name__ == '__main__':
    uvicorn.run('backend.app.main:app', host='0.0.0.0', port=8088, reload=True)
