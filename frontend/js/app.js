/**
 * TRIAGE-AI: Main Application Controller
 * Handles UI interactions, 1-click hackathon presets, OCR uploads,
 * real-time prioritization rendering, and clinician review actions.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  const state = {
    currentTab: "intake",
    uploadedReport: null,
    latestAssessment: null,
    currentRecordForReview: null,
    presets: []
  };

  // DOM Elements
  
  function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = "toast " + type;
    toast.innerHTML = "<div class='toast-message'>" + message + "</div>";
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  const tabIntake = document.getElementById("tabIntake");
  const tabQueue = document.getElementById("tabQueue");
  const tabProtocols = document.getElementById("tabProtocols");
  const sectionIntake = document.getElementById("sectionIntake");
  const sectionQueue = document.getElementById("sectionQueue");
  const sectionProtocols = document.getElementById("sectionProtocols");

  const intakeForm = document.getElementById("intakeForm");
  const btnPreview = document.getElementById("btnPreview");
  const btnSubmit = document.getElementById("btnSubmit");
  const btnClear = document.getElementById("btnClear");
  const presetsContainer = document.getElementById("presetsContainer");

  const fileInput = document.getElementById("reportFileInput");
  const dropzone = document.getElementById("reportDropzone");
  const ocrPreviewBox = document.getElementById("ocrPreviewBox");
  const ocrFilename = document.getElementById("ocrFilename");
  const ocrExtractedText = document.getElementById("ocrExtractedText");
  const ocrMarkersList = document.getElementById("ocrMarkersList");

  // Assessment Output Elements
  const priorityBanner = document.getElementById("priorityBanner");
  const priorityIcon = document.getElementById("priorityIcon");
  const priorityTitle = document.getElementById("priorityTitle");
  const priorityDesc = document.getElementById("priorityDesc");
  const clinicalFlagsBox = document.getElementById("clinicalFlagsBox");
  const clinicalFlagsList = document.getElementById("clinicalFlagsList");
  const missingInfoBox = document.getElementById("missingInfoBox");
  const missingInfoList = document.getElementById("missingInfoList");
  const screeningQuestionsList = document.getElementById("screeningQuestionsList");
  const triageNoteBox = document.getElementById("triageNoteBox");

  // Queue Elements
  const queueTableBody = document.getElementById("queueTableBody");
  const queueStatusFilter = document.getElementById("queueStatusFilter");
  const queueCategoryFilter = document.getElementById("queueCategoryFilter");
  const queueSearch = document.getElementById("queueSearch");

  // Review Modal Elements
  const reviewModal = document.getElementById("reviewModal");
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const modalCancelBtn = document.getElementById("modalCancelBtn");
  const reviewForm = document.getElementById("reviewForm");
  const modalPatientSummary = document.getElementById("modalPatientSummary");
  const modalTriageNote = document.getElementById("modalTriageNote");
  const reviewDoctorName = document.getElementById("reviewDoctorName");
  const reviewNotes = document.getElementById("reviewNotes");
  const reviewConfirmedCategory = document.getElementById("reviewConfirmedCategory");
  const reviewStatus = document.getElementById("reviewStatus");
  const btnPrintModal = document.getElementById("btnPrintModal");

  // Initialize Speech Dictation for Symptoms
  new window.VoiceDictation("symptomDetails", "voiceBtn");

  // 1. Navigation Tabs
  function switchTab(tab) {
    state.currentTab = tab;
    [tabIntake, tabQueue, tabProtocols].forEach(t => t?.classList.remove("active"));
    [sectionIntake, sectionQueue, sectionProtocols].forEach(s => {
      if (s) s.style.display = "none";
    });

    if (tab === "intake") {
      tabIntake?.classList.add("active");
      if (sectionIntake) sectionIntake.style.display = "grid";
    } else if (tab === "queue") {
      tabQueue?.classList.add("active");
      if (sectionQueue) sectionQueue.style.display = "block";
      loadQueue();
    } else if (tab === "protocols") {
      tabProtocols?.classList.add("active");
      if (sectionProtocols) sectionProtocols.style.display = "block";
    }
  }

  tabIntake?.addEventListener("click", () => switchTab("intake"));
  tabQueue?.addEventListener("click", () => switchTab("queue"));
  tabProtocols?.addEventListener("click", () => switchTab("protocols"));

  // 2. Load Stats
  async function refreshStats() {
    try {
      const stats = await window.TriageAPI.getStats();
      document.getElementById("statTotal").textContent = stats.total_records || 0;
      document.getElementById("statPending").textContent = stats.pending_reviews || 0;
      document.getElementById("statCat1").textContent = stats.by_category?.cat1_immediate || 0;
      document.getElementById("statCat2").textContent = stats.by_category?.cat2_very_urgent || 0;
      document.getElementById("statCat3").textContent = stats.by_category?.cat3_urgent || 0;
      document.getElementById("statCat4").textContent = stats.by_category?.cat4_routine || 0;
    } catch (err) {
      console.warn("Could not refresh stats:", err);
    }
  }

  // 3. 1-Click Hackathon Presets
  async function loadPresets() {
    try {
      state.presets = await window.TriageAPI.getPresets();
      presetsContainer.innerHTML = "";

      state.presets.forEach((preset, idx) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `preset-btn cat${idx + 1}`;
        btn.innerHTML = `<span>⚡</span> <span>${preset.title.split(":")[1] || preset.title}</span>`;
        btn.addEventListener("click", () => applyPreset(preset));
        presetsContainer.appendChild(btn);
      });
    } catch (err) {
      console.warn("Failed to load presets:", err);
    }
  }

  function applyPreset(preset) {
    document.getElementById("fullName").value = preset.patient.full_name || "";
    document.getElementById("age").value = preset.patient.age || "";
    document.getElementById("gender").value = preset.patient.gender || "Male";
    document.getElementById("contactPhone").value = preset.patient.contact_phone || "";
    document.getElementById("location").value = preset.patient.location || "";

    document.getElementById("chiefComplaint").value = preset.chief_complaint || "";
    document.getElementById("symptomDetails").value = preset.symptom_details || "";
    document.getElementById("duration").value = preset.duration || "";

    const v = preset.vitals || {};
    document.getElementById("systolicBp").value = v.systolic_bp || "";
    document.getElementById("diastolicBp").value = v.diastolic_bp || "";
    document.getElementById("heartRate").value = v.heart_rate || "";
    document.getElementById("temperatureF").value = v.temperature_f || "";
    document.getElementById("spo2").value = v.spo2 || "";
    document.getElementById("respiratoryRate").value = v.respiratory_rate || "";

    document.getElementById("allergies").value = preset.allergies || "";
    document.getElementById("medicalHistory").value = preset.past_medical_history || "";

    // Clear previously attached report on preset switch
    state.uploadedReport = null;
    ocrPreviewBox.style.display = "none";

    // Auto-trigger live preview so judges instantly see results
    triggerLivePreview();
  }

  // 4. Form Data Extractor
  function getFormData() {
    const vitals = {
      systolic_bp: parseFloat(document.getElementById("systolicBp").value) || null,
      diastolic_bp: parseFloat(document.getElementById("diastolicBp").value) || null,
      heart_rate: parseFloat(document.getElementById("heartRate").value) || null,
      temperature_f: parseFloat(document.getElementById("temperatureF").value) || null,
      spo2: parseFloat(document.getElementById("spo2").value) || null,
      respiratory_rate: parseFloat(document.getElementById("respiratoryRate").value) || null
    };

    return {
      patient: {
        full_name: document.getElementById("fullName").value.trim(),
        age: parseInt(document.getElementById("age").value, 10) || 0,
        gender: document.getElementById("gender").value,
        contact_phone: document.getElementById("contactPhone").value.trim(),
        location: document.getElementById("location").value.trim()
      },
      chief_complaint: document.getElementById("chiefComplaint").value.trim(),
      symptom_details: document.getElementById("symptomDetails").value.trim(),
      duration: document.getElementById("duration").value.trim(),
      vitals: vitals,
      allergies: document.getElementById("allergies").value.trim(),
      past_medical_history: document.getElementById("medicalHistory").value.trim(),
      report_filename: state.uploadedReport?.filename || null,
      extracted_report_text: state.uploadedReport?.raw_text || null
    };
  }

  // 5. Live Assessment Preview
  async function triggerLivePreview() {
    const data = getFormData();
    if (!data.chief_complaint) {
      showToast("Please enter at least a Chief Complaint (Primary Symptom) to evaluate.");
      return;
    }

    btnPreview.disabled = true;
    btnPreview.innerHTML = `<span class="spinner"></span> Organizing intake information...`;

    try {
      const payload = {
        age: data.patient.age,
        gender: data.patient.gender,
        chief_complaint: data.chief_complaint,
        symptom_details: data.symptom_details,
        duration: data.duration,
        vitals: data.vitals,
        allergies: data.allergies,
        past_medical_history: data.past_medical_history,
        extracted_report_text: data.extracted_report_text
      };

      const assessment = await window.TriageAPI.assessPreview(payload);
      state.latestAssessment = assessment;
      renderAssessment(assessment);
    } catch (err) {
      showToast("Evaluation error: " + err.message, "error");
    } finally {
      btnPreview.disabled = false;
      btnPreview.innerHTML = "⚡ Live AI Prioritization Preview";
    }
  }

  btnPreview?.addEventListener("click", triggerLivePreview);

  // 6. Render Assessment Output in UI
  function renderAssessment(assessment) {
    const color = assessment.triage_category_color;
    priorityBanner.className = `priority-banner ${color}`;
    
    const icons = {
      red: "🚨",
      orange: "⚠️",
      yellow: "⏱️",
      green: "🟢"
    };
    priorityIcon.textContent = icons[color] || "📋";
    priorityTitle.textContent = assessment.triage_category_label;

    const descriptions = {
      1: "Immediate clinical intervention required. Alert attending physician immediately.",
      2: "Very urgent case. Fast-track for qualified clinical examination.",
      3: "Urgent. Stable vitals, suitable for orderly queued consultation.",
      4: "Routine / standard clinical intake. Non-urgent."
    };
    priorityDesc.textContent = descriptions[assessment.triage_category] || "";

    // Clinical Flags
    clinicalFlagsList.innerHTML = "";
    if (assessment.clinical_flags && assessment.clinical_flags.length > 0) {
      clinicalFlagsBox.style.display = "block";
      assessment.clinical_flags.forEach(flag => {
        const li = document.createElement("li");
        li.textContent = flag;
        clinicalFlagsList.appendChild(li);
      });
    } else {
      clinicalFlagsBox.style.display = "none";
    }

    // Missing Info
    missingInfoList.innerHTML = "";
    if (assessment.missing_information && assessment.missing_information.length > 0) {
      missingInfoBox.style.display = "block";
      assessment.missing_information.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        missingInfoList.appendChild(li);
      });
    } else {
      missingInfoBox.style.display = "none";
    }

    // Screening Questions
    screeningQuestionsList.innerHTML = "";
    if (assessment.follow_up_questions && assessment.follow_up_questions.length > 0) {
      assessment.follow_up_questions.forEach(q => {
        const li = document.createElement("li");
        li.className = "question-item";
        li.textContent = `❓ ${q}`;
        screeningQuestionsList.appendChild(li);
      });
    }

    // Triage Note
    triageNoteBox.textContent = assessment.triage_summary;
  }

  // 7. Save & Queue Record
  intakeForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = getFormData();

    if (!data.patient.full_name) {
      showToast("Please enter patient name.", "error");
      return;
    }
    if (!data.chief_complaint) {
      showToast("Please enter chief complaint.", "error");
      return;
    }

    btnSubmit.disabled = true;
    btnSubmit.textContent = "Saving to Database...";

    try {
      const record = await window.TriageAPI.saveRecord(data);
      showToast(`Patient intake successfully queued!\nPatient ID: ${record.patient.patient_identifier}\nTriage Priority: ${record.triage_category_label}`);
      
      // Reset form
      clearForm();
      refreshStats();

      // Switch to Reviewer Queue tab to view newly queued patient
      switchTab("queue");
    } catch (err) {
      showToast("Error saving record: " + err.message, "error");
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.textContent = "✓ Save & Queue for Clinical Review";
    }
  });

  function clearForm() {
    intakeForm.reset();
    state.uploadedReport = null;
    ocrPreviewBox.style.display = "none";
    priorityBanner.className = "priority-banner green";
    priorityIcon.textContent = "📋";
    priorityTitle.textContent = "Category 4: Standard / Routine";
    priorityDesc.textContent = "Awaiting intake details or preset selection...";
    clinicalFlagsBox.style.display = "none";
    missingInfoBox.style.display = "none";
    screeningQuestionsList.innerHTML = "";
    triageNoteBox.textContent = "Clinical summary will be automatically generated upon entering symptoms.";
  }

  btnClear?.addEventListener("click", clearForm);

  // 8. Report Upload & OCR
  dropzone?.addEventListener("click", () => fileInput.click());

  dropzone?.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--primary)";
  });

  dropzone?.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "#cbd5e1";
  });

  dropzone?.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "#cbd5e1";
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput?.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  });

  async function handleFileUpload(file) {
    ocrPreviewBox.style.display = "block";
    ocrFilename.textContent = `Processing ${file.name} via Modular OCR...`;
    ocrExtractedText.textContent = "Extracting laboratory text...";
    ocrMarkersList.innerHTML = "";

    try {
      const res = await window.TriageAPI.uploadReport(file);
      state.uploadedReport = {
        filename: res.saved_filename,
        raw_text: res.raw_text
      };

      ocrFilename.textContent = `📄 ${res.original_filename}`;
      ocrExtractedText.textContent = res.raw_text;

      // Render parsed lab marker tags
      if (res.detected_markers && res.detected_markers.length > 0) {
        res.detected_markers.forEach(m => {
          const tag = document.createElement("span");
          tag.className = `marker-tag ${m.status.toLowerCase()}`;
          tag.innerHTML = `<strong>${m.parameter}:</strong> ${m.value} (${m.status})`;
          ocrMarkersList.appendChild(tag);
        });
      }

      // Re-trigger live preview to incorporate newly extracted report data
      triggerLivePreview();
    } catch (err) {
      ocrFilename.textContent = "Error processing report";
      ocrExtractedText.textContent = err.message;
    }
  }

  // 9. Reviewer Queue Management
  async function loadQueue() {
    queueTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px;">Loading reviewer queue...</td></tr>`;

    const filters = {
      status: queueStatusFilter?.value || undefined,
      category: queueCategoryFilter?.value ? parseInt(queueCategoryFilter.value, 10) : undefined,
      search: queueSearch?.value || undefined
    };

    try {
      const records = await window.TriageAPI.getRecords(filters);
      queueTableBody.innerHTML = "";

      if (records.length === 0) {
        queueTableBody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-state-icon">📋</div><h3>No Patients Found</h3><p>No triage cases matching the current filters.</p></div></td></tr>`;
        return;
      }

      records.forEach(rec => {
        const tr = document.createElement("tr");

        // Format vital summary snippet
        const vitalsArr = [];
        if (rec.spo2) vitalsArr.push(`SpO2: ${rec.spo2}%`);
        if (rec.heart_rate) vitalsArr.push(`HR: ${rec.heart_rate}`);
        if (rec.systolic_bp) vitalsArr.push(`BP: ${rec.systolic_bp}/${rec.diastolic_bp || '-'}`);
        if (rec.temperature_f) vitalsArr.push(`Temp: ${rec.temperature_f}°F`);
        const vitalsDisplay = vitalsArr.length > 0 ? vitalsArr.join(" | ") : "None recorded";

        tr.innerHTML = `
          <td>
            <span class="badge-cat ${rec.triage_category_color}">
              Cat ${rec.triage_category}
            </span>
          </td>
          <td>
            <strong>${rec.patient?.full_name || 'Anonymous'}</strong><br>
            <small style="color:var(--text-muted);">${rec.patient?.patient_identifier || ''} • ${rec.patient?.age || '-'}y/${rec.patient?.gender || '-'}</small>
          </td>
          <td>
            <strong>${rec.chief_complaint}</strong><br>
            <small style="color:var(--text-muted);">${rec.duration || 'Duration unrecorded'}</small>
          </td>
          <td>
            <small>${vitalsDisplay}</small>
          </td>
          <td>
            <span class="badge-status ${rec.reviewer_status.toLowerCase()}">
              ${rec.reviewer_status}
            </span>
          </td>
          <td>
            <button class="btn btn-secondary review-action-btn" style="padding: 4px 10px; font-size: 0.78rem;" data-id="${rec.id}">
              🩺 Review
            </button>
          </td>
        `;

        tr.querySelector(".review-action-btn").addEventListener("click", () => openReviewModal(rec));
        queueTableBody.appendChild(tr);
      });
    } catch (err) {
      queueTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:red; padding: 20px;">Failed to load queue: ${err.message}</td></tr>`;
    }
  }

  [queueStatusFilter, queueCategoryFilter].forEach(el => el?.addEventListener("change", loadQueue));
  queueSearch?.addEventListener("input", () => {
    clearTimeout(window._searchTimer);
    window._searchTimer = setTimeout(loadQueue, 300);
  });

  // 10. Reviewer Sign-Off Modal
  function openReviewModal(record) {
    state.currentRecordForReview = record;
    modalPatientSummary.innerHTML = `
      <div style="background:var(--bg-subtle); padding:12px; border-radius:6px; margin-bottom:12px;">
        <strong>Patient:</strong> ${record.patient?.full_name} (${record.patient?.patient_identifier})<br>
        <strong>Demographics:</strong> ${record.patient?.age} yo ${record.patient?.gender} • Phone: ${record.patient?.contact_phone || 'None'}<br>
        <strong>Location:</strong> ${record.patient?.location || 'General Intake'}
      </div>
    `;

    modalTriageNote.textContent = record.triage_summary;
    reviewDoctorName.value = record.reviewed_by || "";
    reviewNotes.value = record.reviewer_notes || "";
    reviewConfirmedCategory.value = record.triage_category;
    reviewStatus.value = record.reviewer_status;

    reviewModal.classList.add("open");
  }

  function closeReviewModal() {
    reviewModal.classList.remove("open");
    state.currentRecordForReview = null;
  }

  modalCloseBtn?.addEventListener("click", closeReviewModal);
  modalCancelBtn?.addEventListener("click", closeReviewModal);

  reviewForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.currentRecordForReview) return;

    const payload = {
      reviewed_by: reviewDoctorName.value.trim(),
      reviewer_notes: reviewNotes.value.trim(),
      confirmed_category: parseInt(reviewConfirmedCategory.value, 10),
      reviewer_status: reviewStatus.value
    };

    if (!payload.reviewed_by) {
      showToast("Please enter the name/designation of the reviewing clinician.", "error");
      return;
    }

    try {
      await window.TriageAPI.updateReview(state.currentRecordForReview.id, payload);
      showToast("Clinical review updated successfully!", "success");
      closeReviewModal();
      loadQueue();
      refreshStats();
    } catch (err) {
      showToast("Failed to update review: " + err.message, "error");
    }
  });

  // Print Triage Note
  btnPrintModal?.addEventListener("click", () => {
    window.print();
  });

  // Initial Boot
  refreshStats();
  loadPresets();
});
