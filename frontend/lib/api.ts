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

export type PitchPoint = {
  time: number;
  pitch: number;
};

export type PitchSummary = {
  minimum_pitch: number;
  maximum_pitch: number;
  average_pitch: number;
  median_pitch: number;
  pitch_range: number;
  minimum_note: string;
  maximum_note: string;
  average_note: string;
};

export type PitchExtremePoint = {
  time: number;
  pitch: number;
  note: string;
};

export type SustainedRegion = {
  start_time: number;
  end_time: number;
  duration: number;
  average_pitch: number;
  note: string;
};

export type StableRegion = {
  start_time: number;
  end_time: number;
  duration: number;
  average_pitch: number;
  note: string;
  stability: number;
};

export type PitchTransition = {
  time: number;
  from_pitch: number;
  to_pitch: number;
  from_note: string;
  to_note: string;
  semitone_change: number;
  direction: "up" | "down";
};

export type PitchVisualizationResult = {
  duration: number;
  sample_rate: number;
  frame_count: number;
  pitch_points: PitchPoint[];
  summary: PitchSummary;
  highest_pitch_point: PitchExtremePoint;
  lowest_pitch_point: PitchExtremePoint;
  sustained_regions: SustainedRegion[];
  stable_regions: StableRegion[];
  pitch_transitions: PitchTransition[];
};

/**
 * Generates pitch visualization contour and metadata from a vocal audio path.
 */
export async function getPitchVisualization(
  audioPath: string
): Promise<PitchVisualizationResult> {
  const res = await fetch(`${API_BASE}/visualize-pitch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      audio_path: audioPath,
    }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Pitch visualization failed");
  }

  return res.json();
}

