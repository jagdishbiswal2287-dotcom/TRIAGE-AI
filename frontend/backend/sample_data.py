"""
Realistic Demo Cases for Hackathon Presentation
Allows judges and testers to test diverse clinical intake profiles with 1 click.
"""

from typing import List, Dict, Any

SAMPLE_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "preset-1",
        "title": "Case 1: Severe Acute Chest Pain (Immediate / Resuscitation - Category 1)",
        "patient": {
            "full_name": "Ramesh Kumar",
            "age": 58,
            "gender": "Male",
            "contact_phone": "+91 98765 43210",
            "location": "Sector 4 Industrial Estate Clinic"
        },
        "chief_complaint": "Crushing central chest pain radiating to left arm and jaw",
        "symptom_details": "Patient began experiencing severe retrosternal pressure 2 hours ago while working. Associated with excessive cold sweating (diaphoresis), nausea, and lightheadedness.",
        "duration": "2 hours",
        "vitals": {
            "systolic_bp": 84.0,
            "diastolic_bp": 54.0,
            "heart_rate": 132.0,
            "temperature_f": 98.2,
            "spo2": 88.0,
            "respiratory_rate": 28.0
        },
        "allergies": "No known drug allergies (NKDA)",
        "past_medical_history": "Hypertension (unmedicated), Heavy smoker (25 years)"
    },
    {
        "id": "preset-2",
        "title": "Case 2: Pediatric High Fever with Lethargy (Very Urgent - Category 2)",
        "patient": {
            "full_name": "Ananya Sharma",
            "age": 2,
            "gender": "Female",
            "contact_phone": "+91 98111 22233",
            "location": "Primary Health Centre (PHC) Rampur"
        },
        "chief_complaint": "Continuous high fever and refusing all liquids",
        "symptom_details": "Mother reports child has been burning hot for 36 hours. Vomited twice this morning. Decreased urination (only 1 wet diaper in past 10 hours). Lethargic and irritable when handled.",
        "duration": "36 hours",
        "vitals": {
            "systolic_bp": 92.0,
            "diastolic_bp": 58.0,
            "heart_rate": 146.0,
            "temperature_f": 103.6,
            "spo2": 96.0,
            "respiratory_rate": 34.0
        },
        "allergies": "None known",
        "past_medical_history": "Born full term, fully vaccinated for age"
    },
    {
        "id": "preset-3",
        "title": "Case 3: Acute Asthma Exacerbation (Urgent - Category 3)",
        "patient": {
            "full_name": "Priya Sundaram",
            "age": 22,
            "gender": "Female",
            "contact_phone": "+91 99440 12345",
            "location": "University Campus Health Center"
        },
        "chief_complaint": "Exertional wheezing and tight chest",
        "symptom_details": "Student developed mild-to-moderate audible wheezing following campus sports. Salbutamol inhaler was left at hostel. Able to speak in full sentences.",
        "duration": "4 hours",
        "vitals": {
            "systolic_bp": 122.0,
            "diastolic_bp": 78.0,
            "heart_rate": 94.0,
            "temperature_f": 98.6,
            "spo2": 96.0,
            "respiratory_rate": 20.0
        },
        "allergies": "Dust mite and pollen allergy",
        "past_medical_history": "Bronchial asthma diagnosed age 12"
    },
    {
        "id": "preset-4",
        "title": "Case 4: Mild Seasonal Rhinitis & Cough (Routine - Category 4)",
        "patient": {
            "full_name": "Deepak Patel",
            "age": 34,
            "gender": "Male",
            "contact_phone": "+91 97230 98765",
            "location": "Community Health Camp Ward 12"
        },
        "chief_complaint": "Runny nose and mild scratchy throat",
        "symptom_details": "Clear nasal discharge and occasional dry cough. No shortness of breath, no chest pain, normal appetite and energy levels.",
        "duration": "3 days",
        "vitals": {
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "heart_rate": 72.0,
            "temperature_f": 98.4,
            "spo2": 99.0,
            "respiratory_rate": 16.0
        },
        "allergies": "None",
        "past_medical_history": "No chronic medical conditions"
    }
]


def seed_database_if_empty(db):
    """
    Automatically creates preloaded sample triage records if the database
    is newly created. This ensures the Reviewer Dashboard immediately has
    realistic cases to inspect on the first run.
    """
    import json
    from backend.models.triage import Patient, TriageRecord
    from backend.services.ai_triage import assess_triage
    from backend.schemas.triage import TriageAssessmentRequest, VitalsInput

    # Check if records already exist
    if db.query(Patient).count() > 0:
        return

    for idx, preset in enumerate(SAMPLE_PRESETS):
        # 1. Create Patient
        p_data = preset["patient"]
        patient = Patient(
            patient_identifier=f"TRG-2026-{101 + idx}",
            full_name=p_data["full_name"],
            age=p_data["age"],
            gender=p_data["gender"],
            contact_phone=p_data.get("contact_phone", ""),
            location=p_data.get("location", "")
        )
        db.add(patient)
        db.flush()

        # 2. Run Triage Assessment
        v_dict = preset.get("vitals", {})
        vitals_obj = VitalsInput(**v_dict) if v_dict else None
        
        req = TriageAssessmentRequest(
            age=p_data["age"],
            gender=p_data["gender"],
            chief_complaint=preset["chief_complaint"],
            symptom_details=preset.get("symptom_details", ""),
            duration=preset.get("duration", ""),
            vitals=vitals_obj,
            allergies=preset.get("allergies", ""),
            past_medical_history=preset.get("past_medical_history", "")
        )
        assessment = assess_triage(req)

        # 3. Create Triage Record
        record = TriageRecord(
            patient_id=patient.id,
            chief_complaint=preset["chief_complaint"],
            symptom_details=preset.get("symptom_details", ""),
            duration=preset.get("duration", ""),
            systolic_bp=v_dict.get("systolic_bp"),
            diastolic_bp=v_dict.get("diastolic_bp"),
            heart_rate=v_dict.get("heart_rate"),
            temperature_f=v_dict.get("temperature_f"),
            spo2=v_dict.get("spo2"),
            respiratory_rate=v_dict.get("respiratory_rate"),
            allergies=preset.get("allergies", ""),
            past_medical_history=preset.get("past_medical_history", ""),
            triage_category=assessment.triage_category,
            triage_summary=assessment.triage_summary,
            missing_information=json.dumps(assessment.missing_information),
            follow_up_questions=json.dumps(assessment.follow_up_questions),
            clinical_flags=json.dumps(assessment.clinical_flags),
            reviewer_status="PENDING" if idx != 3 else "COMPLETED",
            reviewer_notes="Routine consultation completed. Advised hydration and rest." if idx == 3 else None,
            reviewed_by="Dr. S. Roy, MBBS" if idx == 3 else None
        )
        db.add(record)

    db.commit()
