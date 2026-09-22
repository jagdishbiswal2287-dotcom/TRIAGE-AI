/**
 * TRIAGE-AI Voice Dictation Service
 * Uses the modern browser-native Web Speech API for real-time speech-to-text.
 * Zero external API keys or server roundtrip required.
 */

class VoiceDictation {
  constructor(targetElementId, toggleBtnId) {
    this.targetInput = document.getElementById(targetElementId);
    this.toggleBtn = document.getElementById(toggleBtnId);
    this.recognition = null;
    this.isListening = false;
    this.init();
  }

  init() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      if (this.toggleBtn) {
        this.toggleBtn.title = "Voice recognition not supported in this browser (Use Chrome or Edge)";
        this.toggleBtn.addEventListener("click", () => {
          alert("Voice dictation is supported in modern browsers like Google Chrome and Microsoft Edge. You can also type symptoms directly into the box.");
        });
      }
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = "en-IN"; // English (India) / Hindi can be selected

    this.recognition.onstart = () => {
      this.isListening = true;
      if (this.toggleBtn) {
        this.toggleBtn.classList.add("recording");
        this.toggleBtn.title = "Listening... Click to stop recording";
      }
    };

    this.recognition.onresult = (event) => {
      let finalTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + " ";
        }
      }
      if (finalTranscript && this.targetInput) {
        const existing = this.targetInput.value.trim();
        this.targetInput.value = existing ? `${existing} ${finalTranscript.trim()}` : finalTranscript.trim();
        // Trigger input event to re-evaluate preview if active
        this.targetInput.dispatchEvent(new Event("input"));
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("Speech recognition notice:", event.error);
      this.stop();
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (this.toggleBtn) {
        this.toggleBtn.classList.remove("recording");
        this.toggleBtn.title = "Click to dictate symptoms with microphone";
      }
    };

    if (this.toggleBtn) {
      this.toggleBtn.addEventListener("click", () => this.toggle());
    }
  }

  toggle() {
    if (!this.recognition) return;
    if (this.isListening) {
      this.stop();
    } else {
      this.start();
    }
  }

  start() {
    if (this.recognition && !this.isListening) {
      try {
        // Adjust recognition language based on current UI selection
        const langCode = localStorage.getItem("triage_ai_lang") || "en";
        this.recognition.lang = langCode === "hi" ? "hi-IN" : "en-IN";
        this.recognition.start();
      } catch (err) {
        console.error("Failed to start speech recognition:", err);
      }
    }
  }

  stop() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (err) {
        console.error("Failed to stop speech recognition:", err);
      }
    }
  }
}

// Global initialization
window.VoiceDictation = VoiceDictation;
