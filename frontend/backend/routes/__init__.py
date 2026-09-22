from backend.routes.triage import router as triage_router
from backend.routes.reports import router as reports_router
from backend.routes.speech import router as speech_router
from backend.routes.translate import router as translate_router

__all__ = ["triage_router", "reports_router", "speech_router", "translate_router"]
