from fastapi import FastAPI
import uvicorn

from app.controllers.ai_tool_controller import router as ai_tool_router
from app.controllers.customer_judgement_controller import router as customer_judgement_router
from app.controllers.enterprise_assistant_controller import router as enterprise_assistant_router
from app.controllers.report_controller import router as report_router
from app.controllers.service_agent_controller import router as service_agent_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Education Service System",
        version="0.1.0",
        description="教育服务平台后端 API",
    )
    application.include_router(service_agent_router)
    application.include_router(ai_tool_router)
    application.include_router(report_router)
    application.include_router(enterprise_assistant_router, prefix="/enterprise", tags=["enterprise-assistant"])
    application.include_router(customer_judgement_router)
    return application


app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8088, reload=True)
