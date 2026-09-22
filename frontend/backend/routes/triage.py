"""
Triage API Routes
Handles intake assessment, record creation, queue listing, and reviewer sign-off.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from backend.database import get_db
from backend.models.triage import Patient, TriageRecord
from backend.schemas.triage import (
    TriageAssessmentRequest,
    TriageAssessmentResponse,
    TriageRecordCreate,
    TriageRecordResponse,
    PatientResponse,
    ReviewerUpdate
)
from backend.services.ai_triage import assess_triage, CATEGORY_META
from backend.sample_data import SAMPLE_PRESETS

router = APIRouter(prefix="/api/triage", tags=["Triage"])

def _format_record_response(rec: TriageRecord) -> TriageRecordResponse:
    """Helper to convert database model to validated Pydantic response."""
    cat_meta = CATEGORY_META.get(rec.triage_category, CATEGORY_META[4])
    
    missing_list = []
    if rec.missing_information:
        try:
            missing_list = json.loads(rec.missing_information)
        except Exception:
            missing_list = [rec.missing_information]

    questions_list = []
    if rec.follow_up_questions:
        try:
            questions_list = json.loads(rec.follow_up_questions)
        except Exception:
            questions_list = [rec.follow_up_questions]

    flags_list = []
    if rec.clinical_flags:
        try:
            flags_list = json.loads(rec.clinical_flags)
        except Exception:
            flags_list = [rec.clinical_flags]

    patient_resp = None
    if rec.patient:
        patient_resp = PatientResponse(
            id=rec.patient.id,
            patient_identifier=rec.patient.patient_identifier,
            full_name=rec.patient.full_name,
            age=rec.patient.age,
            gender=rec.patient.gender,
            contact_phone=rec.patient.contact_phone,
            location=rec.patient.location,
            created_at=rec.patient.created_at
        )

    return TriageRecordResponse(
        id=rec.id,
        patient_id=rec.patient_id,
        patient=patient_resp,
        chief_complaint=rec.chief_complaint,
        symptom_details=rec.symptom_details,
        duration=rec.duration,
        systolic_bp=rec.systolic_bp,
        diastolic_bp=rec.diastolic_bp,
        heart_rate=rec.heart_rate,
        temperature_f=rec.temperature_f,
        spo2=rec.spo2,
        respiratory_rate=rec.respiratory_rate,
        allergies=rec.allergies,
        past_medical_history=rec.past_medical_history,
        report_filename=rec.report_filename,
        extracted_report_text=rec.extracted_report_text,
        triage_category=rec.triage_category,
        triage_category_label=cat_meta["label"],
        triage_category_color=cat_meta["color"],
        triage_summary=rec.triage_summary,
        missing_information=missing_list,
        follow_up_questions=questions_list,
        clinical_flags=flags_list,
        reviewer_status=rec.reviewer_status,
        reviewer_notes=rec.reviewer_notes,
        reviewed_by=rec.reviewed_by,
        reviewed_at=rec.reviewed_at,
        created_at=rec.created_at,
        updated_at=rec.updated_at
    )


@router.post("/assess", response_model=TriageAssessmentResponse)
def assess_intake_preview(payload: TriageAssessmentRequest):
    """
    Generates an instant non-diagnostic triage preview (category, flags, missing data, questions)
    without persisting to the database. Useful for real-time frontend feedback.
    """
    return assess_triage(payload)


@router.post("/records", response_model=TriageRecordResponse)
def create_triage_record(payload: TriageRecordCreate, db: Session = Depends(get_db)):
    """
    Persists patient demographic data and complete triage intake evaluation.
    """
    # Generate unique patient identifier if omitted
    identifier = payload.patient.patient_identifier
    if not identifier:
        count = db.query(Patient).count() + 1
        identifier = f"TRG-{datetime.now(timezone.utc).year}-{count:04d}"

    # Check if patient exists by identifier, or create new
    patient = db.query(Patient).filter(Patient.patient_identifier == identifier).first()
    if not patient:
        patient = Patient(
            patient_identifier=identifier,
            full_name=payload.patient.full_name,
            age=payload.patient.age,
            gender=payload.patient.gender,
            contact_phone=payload.patient.contact_phone or "",
            location=payload.patient.location or ""
        )
        db.add(patient)
        db.flush()

    # Evaluate triage with AI/heuristic service
    assessment_req = TriageAssessmentRequest(
        age=patient.age,
        gender=patient.gender,
        chief_complaint=payload.chief_complaint,
        symptom_details=payload.symptom_details or "",
        duration=payload.duration or "",
        vitals=payload.vitals,
        allergies=payload.allergies or "",
        past_medical_history=payload.past_medical_history or "",
        extracted_report_text=payload.extracted_report_text or ""
    )
    assessment = assess_triage(assessment_req)

    # Vitals unpacking
    v = payload.vitals
    rec = TriageRecord(
        patient_id=patient.id,
        chief_complaint=payload.chief_complaint,
        symptom_details=payload.symptom_details,
        duration=payload.duration,
        systolic_bp=v.systolic_bp if v else None,
        diastolic_bp=v.diastolic_bp if v else None,
        heart_rate=v.heart_rate if v else None,
        temperature_f=v.temperature_f if v else None,
        spo2=v.spo2 if v else None,
        respiratory_rate=v.respiratory_rate if v else None,
        allergies=payload.allergies,
        past_medical_history=payload.past_medical_history,
        report_filename=payload.report_filename,
        extracted_report_text=payload.extracted_report_text,
        triage_category=assessment.triage_category,
        triage_summary=assessment.triage_summary,
        missing_information=json.dumps(assessment.missing_information),
        follow_up_questions=json.dumps(assessment.follow_up_questions),
        clinical_flags=json.dumps(assessment.clinical_flags),
        reviewer_status="PENDING"
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return _format_record_response(rec)


@router.get("/records", response_model=List[TriageRecordResponse])
def list_triage_records(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, IN_REVIEW, COMPLETED"),
    category: Optional[int] = Query(None, description="Filter by category 1-4"),
    search: Optional[str] = Query(None, description="Search by patient name or ID"),
    db: Session = Depends(get_db)
):
    """
    Returns triage queue sorted by critical urgency (Category 1 first) then time.
    """
    query = db.query(TriageRecord).join(Patient)

    if status:
        query = query.filter(TriageRecord.reviewer_status == status.upper())

    if category:
        query = query.filter(TriageRecord.triage_category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Patient.full_name.ilike(search_pattern)) | 
            (Patient.patient_identifier.ilike(search_pattern)) |
            (TriageRecord.chief_complaint.ilike(search_pattern))
        )

    # Sort: Category 1 (Most Urgent) first, then newly arrived records
    records = query.order_by(asc(TriageRecord.triage_category), desc(TriageRecord.created_at)).all()
    return [_format_record_response(r) for r in records]


@router.get("/records/{record_id}", response_model=TriageRecordResponse)
def get_triage_record(record_id: int, db: Session = Depends(get_db)):
    """Retrieves a single triage record by its primary ID."""
    rec = db.query(TriageRecord).filter(TriageRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Triage record not found.")
    return _format_record_response(rec)


@router.patch("/records/{record_id}/review", response_model=TriageRecordResponse)
def update_reviewer_status(record_id: int, payload: ReviewerUpdate, db: Session = Depends(get_db)):
    """
    Enables a qualified medical reviewer (doctor/nurse) to sign off on a case,
    record clinical review notes, and confirm/adjust the priority category.
    """
    rec = db.query(TriageRecord).filter(TriageRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Triage record not found.")

    rec.reviewer_status = payload.reviewer_status.upper()
    rec.reviewer_notes = payload.reviewer_notes
    rec.reviewed_by = payload.reviewed_by
    rec.reviewed_at = datetime.now(timezone.utc)
    
    if payload.confirmed_category:
        rec.triage_category = payload.confirmed_category

    db.commit()
    db.refresh(rec)
    return _format_record_response(rec)


@router.get("/presets")
def get_sample_presets():
    """Returns the list of 1-click hackathon demo cases."""
    return SAMPLE_PRESETS


@router.get("/stats")
def get_triage_statistics(db: Session = Depends(get_db)):
    """Returns live count aggregates for the dashboard header metrics."""
    total = db.query(TriageRecord).count()
    pending = db.query(TriageRecord).filter(TriageRecord.reviewer_status == "PENDING").count()
    in_review = db.query(TriageRecord).filter(TriageRecord.reviewer_status == "IN_REVIEW").count()
    completed = db.query(TriageRecord).filter(TriageRecord.reviewer_status == "COMPLETED").count()

    cat1 = db.query(TriageRecord).filter(TriageRecord.triage_category == 1).count()
    cat2 = db.query(TriageRecord).filter(TriageRecord.triage_category == 2).count()
    cat3 = db.query(TriageRecord).filter(TriageRecord.triage_category == 3).count()
    cat4 = db.query(TriageRecord).filter(TriageRecord.triage_category == 4).count()

    return {
        "total_records": total,
        "pending_reviews": pending,
        "in_review": in_review,
        "completed_reviews": completed,
        "by_category": {
            "cat1_immediate": cat1,
            "cat2_very_urgent": cat2,
            "cat3_urgent": cat3,
            "cat4_routine": cat4
        }
    }
