"""
Medical & Lab Report Upload and OCR API Routes
"""

import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import settings
from backend.services.ocr_service import OCRService

router = APIRouter(prefix="/api/reports", tags=["Reports & OCR"])

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

@router.post("/upload")
async def upload_medical_report(file: UploadFile = File(...)):
    """
    Accepts medical reports (PDF, PNG, JPEG), stores them safely in uploads/,
    and runs the modular OCR extraction service.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type ({ext}). Please upload PDF or image files (PNG, JPG)."
        )

    # Secure unique filename
    unique_name = f"{uuid.uuid4().hex[:10]}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Process through modular OCR service
    ocr_result = OCRService.process_document(save_path)

    return {
        "status": "success",
        "original_filename": file.filename,
        "saved_filename": unique_name,
        "raw_text": ocr_result["raw_text"],
        "detected_markers": ocr_result["detected_markers"]
    }
