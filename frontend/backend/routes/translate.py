"""
Translation API Routes
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.translation_service import TranslationService

router = APIRouter(prefix="/api/translate", tags=["Translation"])

class TranslationRequest(BaseModel):
    text: str
    target_language: str = "hi"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    target_language: str

@router.get("/languages")
def get_languages():
    """Returns supported languages for triage intake."""
    return TranslationService.get_supported_languages()

@router.post("/phrase", response_model=TranslationResponse)
def translate_phrase(req: TranslationRequest):
    """Translates clinical phrase to regional language."""
    translated = TranslationService.translate_phrase(req.text, req.target_language)
    return TranslationResponse(
        original_text=req.text,
        translated_text=translated,
        target_language=req.target_language
    )
