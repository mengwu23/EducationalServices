"""后端服务的 FastAPI 应用入口。"""
import sys
from pathlib import Path

# 确保 backend/ 在 Python 路径中，使 app.* 导入可用
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from fastapi import FastAPI
import uvicorn
from backend.app.controllers.customer_judgement_controller import router as customer_judgement_router
from backend.app.controllers.enterprise_assistant_controller import router as enterprise_assistant_router

app = FastAPI(
    title="Education Service System",
    version="0.1.0",
    description="教育服务平台后端 API。",
)

# 挂载企业管理查询助手路由，保证服务启动后即可访问该模块接口。
app.include_router(enterprise_assistant_router, prefix="/enterprise", tags=["企业智能助手模块"])

# 挂载客户画像研判路由。
app.include_router(customer_judgement_router)


if __name__ == '__main__':
    uvicorn.run('backend.app.main:app', host='0.0.0.0', port=8088, reload=True)
