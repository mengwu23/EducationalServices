"""FastAPI application entrypoint."""

import sys
from pathlib import Path

from fastapi import FastAPI
import uvicorn

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.controllers.customer_judgement_controller import router as customer_judgement_router
from app.controllers.enterprise_assistant_controller import router as enterprise_assistant_router
from app.controllers.report_controller import router as report_router
from app.controllers.service_agent_controller import router as service_agent_router

app = FastAPI(
    title="Education Service System",
    version="0.1.0",
    description="教育服务平台后端 API。",
)

app.include_router(service_agent_router, prefix="/api/v1/service-agent", tags=["客服 Agent 模块"])
app.include_router(report_router)
app.include_router(enterprise_assistant_router, prefix="/enterprise", tags=["企业智能助手模块"])
app.include_router(customer_judgement_router)


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8088, reload=True)
