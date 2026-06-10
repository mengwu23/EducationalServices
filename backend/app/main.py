import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.controllers.academic_event_controller import router as academic_event_router
from backend.app.controllers.ai_tool_controller import router as ai_tool_router
from backend.app.controllers.student_feedback_ticket_controller import (
    router as student_feedback_ticket_router,
)

app = FastAPI(title="Educational Services API")

app.include_router(academic_event_router, prefix="/api")
app.include_router(student_feedback_ticket_router, prefix="/api")
app.include_router(ai_tool_router, prefix="/api")

if __name__ == '__main__':
    uvicorn.run('backend.app.main:app', host='0.0.0.0', port=8088, reload=False)
