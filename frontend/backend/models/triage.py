"""
SQLAlchemy Models for Patient and Triage Records
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Patient(Base):
    """Stores fundamental patient demographic details."""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_identifier = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)  # Male, Female, Other, Prefer not to say
    contact_phone = Column(String(30), nullable=True)
    location = Column(String(120), nullable=True)  # Village/Ward/Clinic location
    created_at = Column(DateTime, default=utc_now)

    # One patient can have multiple triage visits over time
    triage_records = relationship("TriageRecord", back_populates="patient", cascade="all, delete-orphan")


class TriageRecord(Base):
    """
    Stores non-diagnostic intake summaries, vital observations,
    flagged missing data, and clinical reviewer sign-offs.
    """
    __tablename__ = "triage_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Reported symptoms and timeline
    chief_complaint = Column(String(255), nullable=False)
    symptom_details = Column(Text, nullable=True)
    duration = Column(String(100), nullable=True)
    
    # Vital signs (nullable if unrecorded)
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)
    heart_rate = Column(Float, nullable=True)       # beats/min
    temperature_f = Column(Float, nullable=True)    # Fahrenheit
    spo2 = Column(Float, nullable=True)             # % oxygen saturation
    respiratory_rate = Column(Float, nullable=True) # breaths/min
    
    # Clinical history & report
    allergies = Column(Text, nullable=True)
    past_medical_history = Column(Text, nullable=True)
    report_filename = Column(String(255), nullable=True)
    extracted_report_text = Column(Text, nullable=True)
    
    # Non-diagnostic Triage AI Output
    triage_category = Column(Integer, nullable=False, default=4)  # 1: Red, 2: Orange, 3: Yellow, 4: Green
    triage_summary = Column(Text, nullable=False)
    missing_information = Column(Text, nullable=True)  # JSON string array
    follow_up_questions = Column(Text, nullable=True)  # JSON string array
    clinical_flags = Column(Text, nullable=True)       # JSON string array of vital alerts
    
    # Qualified Human Reviewer Sign-Off
    reviewer_status = Column(String(30), default="PENDING")  # PENDING, IN_REVIEW, COMPLETED
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(120), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    patient = relationship("Patient", back_populates="triage_records")
