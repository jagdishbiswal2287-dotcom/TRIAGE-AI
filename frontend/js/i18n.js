/**
 * TRIAGE-AI Multilingual UI Dictionary & Switcher
 * Supports instantaneous client-side UI translation for English, Hindi, Tamil, Telugu, Bengali.
 */

const UI_TRANSLATIONS = {
  en: {
    disclaimer: "⚠️ NON-DIAGNOSTIC PROTOCOL: TRIAGE-AI does NOT diagnose diseases, prescribe medication, or replace doctors. For clinical intake prioritization only.",
    brandSubtitle: "Human-in-the-Loop Healthcare Triage Assistant",
    tabIntake: "New Patient Intake",
    tabQueue: "Reviewer Queue",
    tabGuidelines: "Triage Protocols",
    presetsLabel: "⚡ Quick Demo Presets:",
    cardPatientInfo: "1. Patient Demographics",
    cardVitals: "2. Vital Signs",
    cardSymptoms: "3. Presenting Symptoms & Timeline",
    cardReport: "4. Medical / Lab Report (Optional)",
    cardSummary: "Non-Diagnostic Triage Summary",
    btnPreview: "Live AI Prioritization Preview",
    btnSubmit: "Save & Queue for Clinical Review",
    btnClear: "Clear Form",
    fullName: "Full Name",
    age: "Age (Years)",
    gender: "Gender",
    phone: "Contact Phone",
    location: "Center / Location",
    chiefComplaint: "Chief Complaint (Primary Symptom)",
    symptomDetails: "Symptom Narrative / Observations",
    duration: "Symptom Duration",
    allergies: "Known Allergies",
    medicalHistory: "Past Medical History",
    bp: "Blood Pressure (BP)",
    hr: "Heart Rate (BPM)",
    temp: "Temperature (°F)",
    spo2: "Oxygen (SpO2 %)",
    rr: "Respiratory Rate (/min)",
    dropzoneText: "Click or Drag & Drop Medical / Lab Report",
    dropzoneSub: "PDF, PNG, JPG accepted (Up to 10MB)",
    missingInfoTitle: "Flagged Missing Information",
    screeningQuestionsTitle: "Targeted Screening Questions for Health Worker",
    clinicalNoteTitle: "Structured Clinical Intake Note",
    queueTitle: "Qualified Reviewer Queue",
    queueSubtitle: "Patients awaiting clinician evaluation sorted by emergency triage category",
    colPriority: "Priority",
    colPatient: "Patient Info",
    colComplaint: "Chief Complaint",
    colVitals: "Flagged Vitals",
    colStatus: "Review Status",
    colAction: "Action",
    btnReview: "Review & Sign Off",
    btnPrint: "Print Triage Note"
  },
  hi: {
    disclaimer: "⚠️ गैर-नैदानिक प्रोटोकॉल: TRIAGE-AI किसी बीमारी का निदान नहीं करता, न दवा लिखता है। केवल प्राथमिकता निर्धारण हेतु।",
    brandSubtitle: "मानव-सत्यापित स्वास्थ्य सेवा ट्राइएज सहायक",
    tabIntake: "नया मरीज पंजीकरण",
    tabQueue: "समीक्षा कतार",
    tabGuidelines: "ट्राइएज दिशानिर्देश",
    presetsLabel: "⚡ डेमो प्रीसेट:",
    cardPatientInfo: "1. मरीज की बुनियादी जानकारी",
    cardVitals: "2. महत्वपूर्ण शारीरिक संकेत (वाइटल्स)",
    cardSymptoms: "3. मुख्य लक्षण एवं अवधि",
    cardReport: "4. मेडिकल / लैब रिपोर्ट (वैकल्पिक)",
    cardSummary: "गैर-नैदानिक ट्राइएज सारांश",
    btnPreview: "लाइव ट्राइएज पूर्वावलोकन",
    btnSubmit: "सुरक्षित करें एवं कतार में भेजें",
    btnClear: "फॉर्म साफ़ करें",
    fullName: "मरीज का पूरा नाम",
    age: "उम्र (वर्ष)",
    gender: "लिंग",
    phone: "संपर्क फोन",
    location: "स्वास्थ्य केंद्र / स्थान",
    chiefComplaint: "मुख्य शिकायत (प्राथमिक लक्षण)",
    symptomDetails: "लक्षणों का विस्तृत विवरण",
    duration: "लक्षणों की अवधि",
    allergies: "एलर्जी विवरण",
    medicalHistory: "पिछला चिकित्सीय इतिहास",
    bp: "रक्तचाप (BP)",
    hr: "हृदय गति (Heart Rate)",
    temp: "शरीर का तापमान (°F)",
    spo2: "ऑक्सीजन स्तर (SpO2 %)",
    rr: "श्वास दर (Respiratory Rate)",
    dropzoneText: "मेडिकल/लैब रिपोर्ट यहाँ अपलोड करें",
    dropzoneSub: "PDF, PNG, JPG समर्थित (अधिकतम 10MB)",
    missingInfoTitle: "छूटी हुई महत्वपूर्ण जानकारी",
    screeningQuestionsTitle: "स्वास्थ्य कार्यकर्ता के लिए अनुवर्ती प्रश्न",
    clinicalNoteTitle: "संरचित क्लिनिकल ट्राइएज नोट",
    queueTitle: "योग्य चिकित्सक समीक्षा कतार",
    queueSubtitle: "आपातकालीन ट्राइएज प्राथमिकता के आधार पर क्रमबद्ध मरीज",
    colPriority: "प्राथमिकता",
    colPatient: "मरीज की जानकारी",
    colComplaint: "मुख्य शिकायत",
    colVitals: "वाइटल्स",
    colStatus: "समीक्षा स्थिति",
    colAction: "कार्रवाई",
    btnReview: "समीक्षा एवं हस्ताक्षर",
    btnPrint: "ट्राइएज नोट प्रिंट करें"
  },
  ta: {
    disclaimer: "⚠️ மருத்துவ மறுப்பு: இந்த அமைப்பு எந்த நோயையும் கண்டறியவோ மருந்துகளை பரிந்துரைக்கவோ இல்லை. பரிசீலனைக்கு மட்டுமே.",
    brandSubtitle: "சுகாதார சிகிச்சை வரிசைப்படுத்துதல் உதவியாளர்",
    tabIntake: "புதிய நோயாளி சேர்க்கை",
    tabQueue: "மருத்துவர் வரிசை",
    tabGuidelines: "வழிகாட்டுதல்கள்",
    presetsLabel: "⚡ மாதிரி அமைப்புகள்:",
    cardPatientInfo: "1. நோயாளி விவரங்கள்",
    cardVitals: "2. உடல் அறிகுறிகள் (Vitals)",
    cardSymptoms: "3. முக்கிய புகார்கள்",
    cardReport: "4. மருத்துவ அறிக்கை (விருப்பம்)",
    cardSummary: "மருத்துவ மதிப்பீடு சுருக்கம்",
    btnPreview: "முன்னோட்டம்",
    btnSubmit: "சேமித்து வரிசைப்படுத்து",
    btnClear: "படிவத்தை அழிக்கவும்",
    fullName: "முழு பெயர்",
    age: "வயது",
    gender: "பாலினம்",
    phone: "தொலைபேசி",
    location: "சுகாதார மையம்",
    chiefComplaint: "முக்கிய புகார்",
    symptomDetails: "அறிகுறிகள் விவரம்",
    duration: "கால அளவு",
    allergies: "ஒவ்வாமை விவரம்",
    medicalHistory: "முந்தைய மருத்துவ வரலாறு",
    bp: "இரத்த அழுத்தம் (BP)",
    hr: "இதய துடிப்பு",
    temp: "வெப்பநிலை (°F)",
    spo2: "ஆக்சிஜன் (SpO2 %)",
    rr: "சுவாச விகிதம்",
    dropzoneText: "மருத்துவ அறிக்கையை பதிவேற்றவும்",
    dropzoneSub: "PDF, PNG, JPG (10MB வரை)",
    missingInfoTitle: "விடுபட்ட தகவல்கள்",
    screeningQuestionsTitle: "பரிசோதனை கேள்விகள்",
    clinicalNoteTitle: "மருத்துவ குறிப்பு",
    queueTitle: "மருத்துவர் ஆய்வு வரிசை",
    queueSubtitle: "அவசர முன்னுரிமையின் அடிப்படையில் வரிசைப்படுத்தப்பட்டுள்ளது",
    colPriority: "முன்னுரிமை",
    colPatient: "நோயாளி",
    colComplaint: "புகார்",
    colVitals: "அறிகுறிகள்",
    colStatus: "நிலை",
    colAction: "செயல்",
    btnReview: "ஆய்வு செய்து முடி",
    btnPrint: "அச்சு எடு"
  }
};

let currentLanguage = "en";

function setLanguage(lang) {
  if (!UI_TRANSLATIONS[lang]) lang = "en";
  currentLanguage = lang;
  applyTranslations();
  localStorage.setItem("triage_ai_lang", lang);
}

function applyTranslations() {
  const dict = UI_TRANSLATIONS[currentLanguage] || UI_TRANSLATIONS["en"];
  document.querySelectorAll("[data-i18n]").forEach(elem => {
    const key = elem.getAttribute("data-i18n");
    if (dict[key]) {
      if (elem.tagName === "INPUT" || elem.tagName === "TEXTAREA") {
        elem.placeholder = dict[key];
      } else {
        elem.textContent = dict[key];
      }
    }
  });
}

// Auto-initialize from localStorage if previously set
document.addEventListener("DOMContentLoaded", () => {
  const savedLang = localStorage.getItem("triage_ai_lang") || "en";
  const selectElem = document.getElementById("languageSelect");
  if (selectElem) {
    selectElem.value = savedLang;
    selectElem.addEventListener("change", (e) => setLanguage(e.target.value));
  }
  setLanguage(savedLang);
});
