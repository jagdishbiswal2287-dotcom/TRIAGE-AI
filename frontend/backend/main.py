"""
TRIAGE-AI: Human-in-the-Loop Healthcare Triage Assistant
Main FastAPI Application Entrypoint
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.models.triage import Patient, TriageRecord
from backend.sample_data import seed_database_if_empty
from backend.routes import triage_router, reports_router, speech_router, translate_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events:
    Initializes database tables and seeds demo data on first boot.
    """
    # 1. Initialize SQLite / PostgreSQL tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed realistic demo patients if table is empty
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()

    yield

app = FastAPI(
    title="TRIAGE-AI API",
    description="Human-in-the-Loop Healthcare Triage Assistant - Clinical Intake & Prioritization System",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local development and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(triage_router)
app.include_router(reports_router)
app.include_router(speech_router)
app.include_router(translate_router)

# Mount uploaded files directory
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Frontend directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve frontend static assets (CSS, JS)
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_index():
    """Serves the main single-page healthcare dashboard."""
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "online", "service": "TRIAGE-AI Backend API", "docs": "/docs"}

@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "non_diagnostic": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
