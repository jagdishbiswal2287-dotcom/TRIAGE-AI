/**
 * TRIAGE-AI Backend API Client
 * Clean asynchronous REST fetch handlers with error handling.
 */

const API_BASE = ""; // Relative path when served together via FastAPI

const TriageAPI = {
  /** Fetch dashboard aggregate counts */
  async getStats() {
    const res = await fetch(`${API_BASE}/api/triage/stats`);
    if (!res.ok) throw new Error("Failed to fetch triage statistics.");
    return await res.json();
  },

  /** Fetch hackathon demo presets */
  async getPresets() {
    const res = await fetch(`${API_BASE}/api/triage/presets`);
    if (!res.ok) throw new Error("Failed to fetch presets.");
    return await res.json();
  },

  /** Live triage assessment preview (without saving) */
  async assessPreview(payload) {
    const res = await fetch(`${API_BASE}/api/triage/assess`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Triage evaluation failed.");
    }
    return await res.json();
  },

  /** Persist patient and triage record */
  async saveRecord(payload) {
    const res = await fetch(`${API_BASE}/api/triage/records`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to save triage record.");
    }
    return await res.json();
  },

  /** Retrieve reviewer queue */
  async getRecords(params = {}) {
    const url = new URL(`${window.location.origin}/api/triage/records`);
    if (params.status) url.searchParams.set("status", params.status);
    if (params.category) url.searchParams.set("category", params.category);
    if (params.search) url.searchParams.set("search", params.search);

    const res = await fetch(url.toString());
    if (!res.ok) throw new Error("Failed to fetch triage records.");
    return await res.json();
  },

  /** Get single triage record */
  async getRecord(id) {
    const res = await fetch(`${API_BASE}/api/triage/records/${id}`);
    if (!res.ok) throw new Error("Record not found.");
    return await res.json();
  },

  /** Update reviewer notes and category confirmation */
  async updateReview(id, updatePayload) {
    const res = await fetch(`${API_BASE}/api/triage/records/${id}/review`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatePayload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to update review status.");
    }
    return await res.json();
  },

  /** Upload report file (PDF/Image) for OCR extraction */
  async uploadReport(file) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/api/reports/upload`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Report upload and OCR failed.");
    }
    return await res.json();
  }
};

window.TriageAPI = TriageAPI;
