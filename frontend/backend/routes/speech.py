"""
Speech-to-Text API Routes
Provides voice transcription backend for mobile/recorded audio inputs.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.services.stt_service import SpeechToTextService

router = APIRouter(prefix="/api/speech", tags=["Speech"])

@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(None),
    language: str = Form("en")
):
    """
    Transcribes audio speech into clinical symptom text.
    Frontend can also use browser-native Web Speech API directly.
    """
    audio_bytes = b""
    filename = "audio.wav"
    if file:
        audio_bytes = await file.read()
        filename = file.filename

    result = SpeechToTextService.transcribe_audio(audio_bytes, filename, language=language)
    return result
