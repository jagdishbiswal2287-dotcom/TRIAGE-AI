"""
Modular Multilingual Translation Service
Supports English, Hindi, Tamil, Telugu, and Bengali for patient triage
in primary health centers and public health camps across India.
"""

from typing import Dict

CLINICAL_DICTIONARY = {
    "hi": {
        "Immediate / Resuscitation": "तत्काल / पुनर्जीवन (अत्यंत गंभीर)",
        "Very Urgent / High Risk": "अति आवश्यक / उच्च जोखिम",
        "Urgent / Moderate Risk": "आवश्यक / मध्यम जोखिम",
        "Standard / Routine": "मानक / सामान्य परामर्श",
        "Chief Complaint": "मुख्य शिकायत",
        "Vital Signs": "महत्वपूर्ण शारीरिक संकेत (वाइटल्स)",
        "Missing Information": "छूटी हुई महत्वपूर्ण जानकारी",
        "Follow-up Screening Questions": "स्वास्थ्य कार्यकर्ता के लिए अनुवर्ती प्रश्न",
        "Non-Diagnostic Disclaimer": "गैर-नैदानिक अस्वीकरण: यह प्रणाली किसी बीमारी का निदान नहीं करती है और न ही दवा लिखती है। इसका उद्देश्य केवल योग्य डॉक्टरों के लिए प्राथमिक समीक्षा को प्राथमिकता देना है।"
    },
    "ta": {
        "Immediate / Resuscitation": "உடனடி / தீவிர அவசர சிகிச்சை",
        "Very Urgent / High Risk": "மிக அவசரம் / அதிக ஆபத்து",
        "Urgent / Moderate Risk": "அவசரம் / நடுத்தர ஆபத்து",
        "Standard / Routine": "வழக்கமான / சாதாரண சிகிச்சை",
        "Chief Complaint": "முக்கிய பிரச்சனை",
        "Vital Signs": "முக்கிய உடல் அறிகுறிகள்",
        "Missing Information": "விடுபட்ட தகவல்கள்",
        "Follow-up Screening Questions": "பரிசோதனை கேள்விகள்",
        "Non-Diagnostic Disclaimer": "மருத்துவ மறுப்பு: இந்த அமைப்பு எந்த நோயையும் கண்டறியவோ மருந்துகளை பரிந்துரைக்கவோ இல்லை. இது தகுதிவாய்ந்த மருத்துவர்களின் பரிசீலனையை ஒழுங்குபடுத்த மட்டுமே."
    },
    "te": {
        "Immediate / Resuscitation": "తక్షణ / పునరుజ్జీవనం",
        "Very Urgent / High Risk": "అత్యవసరం / అధిక ప్రమాదం",
        "Urgent / Moderate Risk": "అవసరం / మధ్యస్థ ప్రమాదం",
        "Standard / Routine": "సాధారణ / రొటీన్",
        "Chief Complaint": "ప్రధాన సమస్య",
        "Vital Signs": "జీవ సంకేతాలు",
        "Missing Information": "మిస్ అయిన సమాచారం",
        "Follow-up Screening Questions": "ఫాలో-అప్ ప్రశ్నలు",
        "Non-Diagnostic Disclaimer": "నాన్-డయాగ్నస్టిక్ నిరాకరణ: ఈ వ్యవస్థ వ్యాధులను నిర్ధారించదు లేదా మందులను సూచించదు."
    },
    "bn": {
        "Immediate / Resuscitation": "অবিলম্বে / পুনরুজ্জীবন (জরুরি)",
        "Very Urgent / High Risk": "খুব জরুরি / উচ্চ ঝুঁকি",
        "Urgent / Moderate Risk": "জরুরি / মাঝারি ঝুঁকি",
        "Standard / Routine": "সাধারণ / রুটিন",
        "Chief Complaint": "প্রধান অভিযোগ",
        "Vital Signs": "গুরুত্বপূর্ণ লক্ষণ",
        "Missing Information": "অনুপস্থিত তথ্য",
        "Follow-up Screening Questions": "অনুসন্ধানমূলক প্রশ্ন",
        "Non-Diagnostic Disclaimer": "অ-রোগনির্ণয় অস্বীকৃতি: এই সিস্টেমটি কোনও রোগ নির্ণয় করে না বা ওষুধ প্রেসক্রাইব করে না।"
    }
}

class TranslationService:
    @classmethod
    def translate_phrase(cls, text: str, target_lang: str) -> str:
        """Translates clinical phrase or key terms."""
        if target_lang == "en" or not text:
            return text
            
        lang_dict = CLINICAL_DICTIONARY.get(target_lang, {})
        # Direct phrase match
        if text in lang_dict:
            return lang_dict[text]
            
        # Fallback: check case-insensitive match
        for k, v in lang_dict.items():
            if k.lower() == text.lower():
                return v
                
        return text

    @classmethod
    def get_supported_languages(cls) -> Dict[str, str]:
        """Returns map of language codes to display names."""
        return {
            "en": "English",
            "hi": "हिन्दी (Hindi)",
            "ta": "தமிழ் (Tamil)",
            "te": "తెలుగు (Telugu)",
            "bn": "বাংলা (Bengali)"
        }
