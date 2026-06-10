from backend.app.ai_tools.academic_event_tools import (
    AcademicEventToolCreate,
    AcademicEventToolList,
    create_academic_event,
    list_active_academic_events,
)
from backend.app.ai_tools.student_feedback_ticket_tools import (
    FeedbackTicketToolCreate,
    FeedbackTicketToolList,
    create_feedback_ticket,
    list_feedback_tickets,
)
from backend.app.common.exceptions import NotFoundError


AI_TOOL_REGISTRY = {
    "academic_event.create": {
        "handler": create_academic_event,
        "schema": AcademicEventToolCreate,
    },
    "academic_event.list_active": {
        "handler": list_active_academic_events,
        "schema": AcademicEventToolList,
    },
    "student_feedback_ticket.create": {
        "handler": create_feedback_ticket,
        "schema": FeedbackTicketToolCreate,
    },
    "student_feedback_ticket.list": {
        "handler": list_feedback_tickets,
        "schema": FeedbackTicketToolList,
    },
}


def get_ai_tool(name: str):
    return AI_TOOL_REGISTRY.get(name)


def invoke_ai_tool(name: str, db, arguments: dict):
    tool = get_ai_tool(name)
    if tool is None:
        raise NotFoundError("AI tool is not registered")
    payload = tool["schema"](**arguments)
    return tool["handler"](db, payload)
