const API_BASE = "http://localhost:8000";

export type Scores = {
  overall_score: number;
  pitch_score: number;
  rhythm_score: number;
  tempo_score: number;
  timbre_score: number;
  melody_score: number;
  dynamics_score: number;
  stability_score: number;
  pronunciation_score: number;
  range_score: number;
  harmonic_score: number;
};

export type AnalysisResponse = Scores & {
  graph_path?: string;
};

export type FeedbackResponse = {
  feedback: string;
};

export type UploadResponse = {
  success: boolean;
  vocals_path: string;
};

/**
 * Checks the status of the backend server.
 */
export async function getBackendStatus(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/`);
    if (!res.ok) return false;
    const data = await res.json();
    return data.message === "AI Music App Running";
  } catch {
    return false;
  }
}

/**
 * Uploads an audio file (.mp3 or .wav) to the backend.
 */
export async function uploadAudio(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Upload failed");
  }

  return res.json();
}

/**
 * Sends both vocals paths to the backend for performance analysis.
 * Passes both reference_vocals_path/user_vocals_path and reference_path/user_path
 * keys to ensure absolute compatibility with backend schemas.
 */
export async function analyzePerformance(
  referenceVocalsPath: string,
  userVocalsPath: string
): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyze-performance`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      reference_vocals_path: referenceVocalsPath,
      user_vocals_path: userVocalsPath,
      reference_path: referenceVocalsPath,
      user_path: userVocalsPath,
    }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Analysis failed");
  }

  return res.json();
}

/**
 * Generates AI feedback based on the analysis scores.
 */
export async function generateFeedback(scores: {
  pitch_score: number;
  rhythm_score: number;
  tempo_score: number;
  timbre_score: number;
  overall_score: number;
}): Promise<FeedbackResponse> {
  const res = await fetch(`${API_BASE}/generate-feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pitch_score: scores.pitch_score,
      rhythm_score: scores.rhythm_score,
      tempo_score: scores.tempo_score,
      timbre_score: scores.timbre_score,
      overall_score: scores.overall_score,
    }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Feedback generation failed");
  }

  return res.json();
}
