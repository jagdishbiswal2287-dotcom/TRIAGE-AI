"""
Modular AI & Heuristic Triage Service
Evaluates clinical intake data using standardized Emergency Severity Index (ESI)
and Manchester Triage System principles for review prioritization.

NON-DIAGNOSTIC NOTICE:
This module does not identify illnesses, prescribe drugs, or dictate clinical treatment.
It identifies vital instability, clinical red flags, missing intake fields, and
generates screening questions to streamline human clinical evaluation.
"""

import re
import json
import requests
import logging
from typing import List, Tuple
from backend.schemas.triage import TriageAssessmentRequest, TriageAssessmentResponse, VitalsInput
from backend.config import settings

def has_unnegated_phrase(keyword: str, text: str) -> bool:
    """
    Checks if a clinical symptom phrase appears without being negated.
    E.g. 'no chest pain', 'denies shortness of breath' returns False.
    """
    kw = re.escape(keyword.lower())
    # Check if preceded by negation within 1-4 words
    pattern = rf"(?:(?:no|denies|without|nil|not experiencing|rules? out)\s+(?:any\s+)?(?:acute\s+)?(?:severe\s+)?){kw}"
    if re.search(pattern, text, re.IGNORECASE):
        return False
    return bool(re.search(rf"\b{kw}\b", text, re.IGNORECASE))

CATEGORY_META = {
    1: {
        "label": "Category 1: Immediate / Resuscitation",
        "color": "red",
        "description": "Critical vital instability or life-threatening red flags requiring immediate clinician evaluation."
    },
    2: {
        "label": "Category 2: Very Urgent / High Risk",
        "color": "orange",
        "description": "High-risk presentations, severe pain, or significantly altered vitals needing prompt review."
    },
    3: {
        "label": "Category 3: Urgent / Moderate Risk",
        "color": "yellow",
        "description": "Moderate acute discomfort with stable vital signs, suitable for orderly queued review."
    },
    4: {
        "label": "Category 4: Standard / Routine",
        "color": "green",
        "description": "Mild, non-urgent, or chronic symptoms with normal vitals for standard clinical consultation."
    }
}

class LocalClinicalTriageEngine:
    """
    Zero-dependency, rule-based clinical intake analyzer.
    Ensures the system works 100% reliably in local hackathon environments.
    """

    @classmethod
    def evaluate(cls, data: TriageAssessmentRequest) -> TriageAssessmentResponse:
        vitals = data.vitals or VitalsInput()
        flags: List[str] = []
        missing: List[str] = []
        questions: List[str] = []
        
        # Priority starts at Category 4 (Routine) and escalates based on findings
        computed_category = 4

        # 1. EVALUATE CRITICAL VITALS (Red flags -> Cat 1 or 2)
        # Oxygen Saturation (SpO2)
        if vitals.spo2 is not None:
            if vitals.spo2 < 90:
                flags.append(f"Severe Hypoxia: SpO2 is critically low ({vitals.spo2}%). Normal is ≥95%.")
                computed_category = min(computed_category, 1)
            elif vitals.spo2 < 94:
                flags.append(f"Borderline Low SpO2 ({vitals.spo2}%). Supplemental oxygen screening required.")
                computed_category = min(computed_category, 2)
        else:
            missing.append("SpO2 (Pulse Oximetry) is unrecorded - critical for respiratory assessment.")

        is_pediatric = (data.age <= 3)

        # Heart Rate (Pulse)
        if vitals.heart_rate is not None:
            if is_pediatric:
                if vitals.heart_rate > 190 or vitals.heart_rate < 70:
                    flags.append(f"Critical Pediatric Heart Rate ({vitals.heart_rate} BPM).")
                    computed_category = min(computed_category, 1)
                elif vitals.heart_rate > 165 or vitals.heart_rate < 80:
                    flags.append(f"Pediatric Tachycardia/Bradycardia ({vitals.heart_rate} BPM).")
                    computed_category = min(computed_category, 2)
            else:
                if vitals.heart_rate > 140 or vitals.heart_rate < 45:
                    flags.append(f"Critical Heart Rate: Extreme pulse rate ({vitals.heart_rate} BPM).")
                    computed_category = min(computed_category, 1)
                elif vitals.heart_rate > 115 or vitals.heart_rate < 55:
                    flags.append(f"Tachycardia/Bradycardia: Elevated or depressed pulse ({vitals.heart_rate} BPM).")
                    computed_category = min(computed_category, 2)
        else:
            missing.append("Heart Rate (BPM) is unrecorded.")

        # Blood Pressure
        if vitals.systolic_bp is not None and vitals.diastolic_bp is not None:
            if vitals.systolic_bp >= 190 or vitals.diastolic_bp >= 120:
                flags.append(f"Hypertensive Crisis range: BP {vitals.systolic_bp}/{vitals.diastolic_bp} mmHg.")
                computed_category = min(computed_category, 2)
            elif vitals.systolic_bp < 85:
                flags.append(f"Hypotension Alert: Systolic BP critically low ({vitals.systolic_bp} mmHg). Risk of shock.")
                computed_category = min(computed_category, 1)
            elif vitals.systolic_bp >= 160 or vitals.diastolic_bp >= 100:
                flags.append(f"Elevated Blood Pressure: {vitals.systolic_bp}/{vitals.diastolic_bp} mmHg.")
                computed_category = min(computed_category, 3)
        else:
            missing.append("Blood Pressure (Systolic/Diastolic) is unrecorded.")

        # Respiratory Rate
        if vitals.respiratory_rate is not None:
            if is_pediatric:
                if vitals.respiratory_rate > 55 or vitals.respiratory_rate < 18:
                    flags.append(f"Severe Pediatric Respiratory Distress ({vitals.respiratory_rate} breaths/min).")
                    computed_category = min(computed_category, 1)
                elif vitals.respiratory_rate > 38:
                    flags.append(f"Pediatric Tachypnea ({vitals.respiratory_rate} breaths/min).")
                    computed_category = min(computed_category, 2)
            else:
                if vitals.respiratory_rate > 32 or vitals.respiratory_rate < 10:
                    flags.append(f"Severe Respiratory Distress: Rate is {vitals.respiratory_rate} breaths/min.")
                    computed_category = min(computed_category, 1)
                elif vitals.respiratory_rate > 24:
                    flags.append(f"Tachypnea: Accelerated breathing rate ({vitals.respiratory_rate} breaths/min).")
                    computed_category = min(computed_category, 2)
        else:
            missing.append("Respiratory Rate is unrecorded.")

        # Temperature
        if vitals.temperature_f is not None:
            if vitals.temperature_f >= 104.0:
                flags.append(f"Hyperpyrexia: Dangerously high temperature ({vitals.temperature_f}°F).")
                computed_category = min(computed_category, 1)
            elif vitals.temperature_f >= 102.0:
                flags.append(f"High Fever: Elevated body temperature ({vitals.temperature_f}°F).")
                computed_category = min(computed_category, 2)
            elif data.age <= 2 and vitals.temperature_f >= 100.4:
                flags.append(f"Pediatric Fever Alert: Infant/toddler fever ({vitals.temperature_f}°F). High vulnerability.")
                computed_category = min(computed_category, 2)
            elif vitals.temperature_f >= 99.5:
                flags.append(f"Low-grade fever recorded ({vitals.temperature_f}°F).")
                computed_category = min(computed_category, 3)
        else:
            missing.append("Body Temperature is unrecorded.")

        # 2. EVALUATE SYMPTOM TEXT & CHIEF COMPLAINT RED FLAGS
        symptom_combined = f"{data.chief_complaint} {data.symptom_details} {data.extracted_report_text}".lower()

        # Severe Red Flags (Category 1)
        cat1_keywords = [
            "crushing chest pain", "radiating to arm", "radiating to jaw",
            "unconscious", "unresponsive", "sudden numbness", "facial droop",
            "slurred speech", "massive bleeding", "hemoptysis", "anaphylaxis",
            "stridor", "unable to breathe", "seizure", "convulsions"
        ]
        for kw in cat1_keywords:
            if has_unnegated_phrase(kw, symptom_combined):
                flags.append(f"Clinical Red Flag Detected: '{kw.title()}'.")
                computed_category = min(computed_category, 1)

        # High-Risk Indicators (Category 2)
        cat2_keywords = [
            "chest pain", "shortness of breath", "dyspnea",
            "severe headache", "stiff neck", "worst headache", "diabetic ketoacidosis",
            "persistent vomiting", "blood in stool", "melena", "fainting", "syncope",
            "severe burn", "acute trauma", "high fever with chills"
        ]
        for kw in cat2_keywords:
            if has_unnegated_phrase(kw, symptom_combined) and computed_category > 2:
                flags.append(f"Urgent Symptom Indicator: '{kw.title()}'.")
                computed_category = min(computed_category, 2)

        # Moderate Indicators (Category 3)
        cat3_keywords = [
            "wheezing", "abdominal pain", "mild wheeze", "sprain", "fracture suspected",
            "moderate fever", "urinary pain", "dysuria", "productive cough", "vomiting"
        ]
        for kw in cat3_keywords:
            if has_unnegated_phrase(kw, symptom_combined) and computed_category > 3:
                computed_category = min(computed_category, 3)

        # 3. IDENTIFY MISSING INTAKE INFORMATION
        if not data.duration or data.duration.strip() == "":
            missing.append("Symptom Duration is missing (e.g. onset hours/days).")
        if not data.allergies or data.allergies.strip() == "":
            missing.append("Allergy status not documented (Ask patient: Any drug/food allergies?).")
        if not data.past_medical_history or data.past_medical_history.strip() == "":
            missing.append("Past Medical History not noted (Ask patient: Hypertension, Diabetes, Asthma, etc.?).")

        # 4. GENERATE TARGETED SCREENING QUESTIONS FOR HEALTH WORKERS
        # Questions tailored to presenting symptoms:
        if any(w in symptom_combined for w in ["chest", "heart", "angina", "tightness"]):
            questions.append("Does the chest discomfort radiate to the left shoulder, arm, neck, or back?")
            questions.append("Did the pain start suddenly at rest or during physical exertion?")
            questions.append("Are you feeling excessive cold sweat (diaphoresis), dizziness, or nausea?")

        if any(w in symptom_combined for w in ["breath", "cough", "wheez", "short of breath", "asthma"]):
            questions.append("Are you having difficulty speaking complete sentences without pausing for breath?")
            questions.append("Is there any discoloration (yellow/green) or blood in the phlegm/cough?")
            questions.append("Do you have a personal history of asthma, COPD, or tuberculosis?")

        if any(w in symptom_combined for w in ["fever", "chills", "temperature", "pyrexia"]):
            questions.append("How many consecutive days has this fever been present?")
            questions.append("Have you noticed any body rashes, joint aches, or burning during urination?")
            questions.append("Have you traveled recently or been exposed to stagnant water/mosquitoes?")

        if any(w in symptom_combined for w in ["abdom", "stomach", "belly", "vomit", "nausea", "diarrhea"]):
            questions.append("Is the stomach pain continuous or coming in waves (cramping)?")
            questions.append("Are you able to keep oral fluids down, or vomiting everything consumed?")
            questions.append("Have you observed dark, black, or blood-streaked stools?")

        if any(w in symptom_combined for w in ["headache", "head", "dizzy", "vision"]):
            questions.append("Did this headache peak instantly like a sudden blow ('thunderclap')?")
            questions.append("Are you having neck stiffness when bending chin to chest, or sensitivity to light?")
            questions.append("Is there any unilateral tingling, arm weakness, or blurred vision?")

        if data.age <= 5:
            questions.append("Pediatric Screen: Is the child active and alert, or excessively drowsy and limp?")
            questions.append("Pediatric Screen: How many wet diapers or urine outputs in the last 12 hours?")

        if not questions:
            # General baseline triage questions
            questions.append("When did the primary symptom first appear, and has it worsened rapidly?")
            questions.append("Have you taken any home medications, pain relievers, or antibiotics for this?")
            questions.append("Has anyone in your household or close proximity had similar complaints?")

        # 5. CONSTRUCT STRUCTURED CLINICAL TRIAGE NOTE
        vitals_summary = []
        if vitals.systolic_bp and vitals.diastolic_bp:
            vitals_summary.append(f"BP {vitals.systolic_bp:.0f}/{vitals.diastolic_bp:.0f} mmHg")
        if vitals.heart_rate:
            vitals_summary.append(f"HR {vitals.heart_rate:.0f} bpm")
        if vitals.temperature_f:
            vitals_summary.append(f"Temp {vitals.temperature_f:.1f}°F")
        if vitals.spo2:
            vitals_summary.append(f"SpO2 {vitals.spo2:.0f}%")
        if vitals.respiratory_rate:
            vitals_summary.append(f"RR {vitals.respiratory_rate:.0f}/min")

        vitals_text = ", ".join(vitals_summary) if vitals_summary else "Vitals pending intake recording"

        summary_lines = [
            f"CLINICAL INTAKE PROFILE: {data.age}yo {data.gender}",
            f"CHIEF COMPLAINT: {data.chief_complaint}",
            f"DURATION: {data.duration if data.duration else 'Not specified'}",
            f"RECORDED VITALS: {vitals_text}",
            f"SYMPTOM NARRATIVE: {data.symptom_details if data.symptom_details else 'None provided'}",
            f"ALLERGIES: {data.allergies if data.allergies else 'Not documented'}",
            f"PAST HISTORY: {data.past_medical_history if data.past_medical_history else 'Not documented'}"
        ]

        if data.extracted_report_text and data.extracted_report_text.strip():
            summary_lines.append(f"UPLOADED REPORT DATA: {data.extracted_report_text.strip()[:300]}...")

        triage_summary = "\n".join(summary_lines)

        meta = CATEGORY_META[computed_category]

        return TriageAssessmentResponse(
            triage_category=computed_category,
            triage_category_label=meta["label"],
            triage_category_color=meta["color"],
            triage_summary=triage_summary,
            clinical_flags=flags,
            missing_information=missing,
            follow_up_questions=questions
        )


class GeminiEnhancementAdapter:
    @classmethod
    def enhance(cls, data: TriageAssessmentRequest, local_result: TriageAssessmentResponse) -> TriageAssessmentResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        
        prompt = f"""
        You are a non-diagnostic medical intake assistant. Do NOT diagnose, prescribe, or recommend treatment.
        Review the following patient intake data and organize it.
        
        Input Data:
        Age: {data.age}
        Gender: {data.gender}
        Chief Complaint: {data.chief_complaint}
        Details: {data.symptom_details}
        Duration: {data.duration}
        Allergies: {data.allergies}
        History: {data.past_medical_history}
        Report Text: {data.extracted_report_text}
        
        Local Flags Detected: {', '.join(local_result.clinical_flags)}
        
        Return ONLY a valid JSON object (without markdown wrapping) with exactly these 3 keys:
        1. "triage_summary": A clearly organized clinical intake note (SBAR style). Keep it professional and concise.
        2. "missing_information": A list of strings describing what important information is missing from the intake.
        3. "follow_up_questions": A list of strings containing suggested screening questions for the health worker.
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        
        try:
            # Reasonable timeout of 5 seconds
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            resp_data = resp.json()
            
            content_text = resp_data["candidates"][0]["content"]["parts"][0]["text"]
            enhanced_data = json.loads(content_text)
            
            # Gemini only enhances the summary, missing info, and questions
            if "triage_summary" in enhanced_data:
                local_result.triage_summary = enhanced_data["triage_summary"]
            if "missing_information" in enhanced_data:
                # Merge local missing info with Gemini's
                local_result.missing_information = list(set(local_result.missing_information + enhanced_data["missing_information"]))
            if "follow_up_questions" in enhanced_data:
                local_result.follow_up_questions = enhanced_data["follow_up_questions"]
                
        except Exception as e:
            logging.warning(f"Gemini enhancement failed or timed out. Falling back to local engine. Error: {str(e)}")
            
        return local_result

def assess_triage(data: TriageAssessmentRequest) -> TriageAssessmentResponse:
    """
    Main entrypoint for triage evaluation.
    Modular design ensures local engine safety, with optional Gemini enhancement.
    """
    # 1. ALWAYS run local deterministic engine first for safety and priority
    local_result = LocalClinicalTriageEngine.evaluate(data)
    
    # 2. OPTIONALLY enhance with Gemini if enabled
    if getattr(settings, 'GEMINI_ENABLED', False) and settings.GEMINI_API_KEY:
        local_result = GeminiEnhancementAdapter.enhance(data, local_result)
            
    return local_result

