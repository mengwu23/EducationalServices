from fastapi import FastAPI

from app.controllers import ai_tool_controller, report_controller
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="教育服务系统后端", version="0.1.0")
    app.include_router(report_controller.router)
    app.include_router(ai_tool_controller.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
