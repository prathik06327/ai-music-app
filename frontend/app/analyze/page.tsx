"use client";

import { useState } from "react";
import FeedbackCard from "../components/ui/FeedbackCard";
import GlassCard from "../components/ui/GlassCard";
import OverallScoreCard from "../components/ui/OverallScoreCard";
import PageContainer from "../components/layout/PageContainer";
import ScoreCard from "../components/ui/ScoreCard";

type Scores = {
  overall_score: number;
  pitch_score: number;
  rhythm_score: number;
  tempo_score: number;
  timbre_score: number;
};

type ErrorResponse = {
  detail?: string;
};

const API_BASE = "http://localhost:8000";

function getErrorMessage(error: unknown, fallback: string) {
  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}

export default function AnalyzePage() {
  const [referenceFile, setReferenceFile] = useState<File | null>(null);
  const [userFile, setUserFile] = useState<File | null>(null);
  const [referencePath, setReferencePath] = useState<string>("");
  const [userPath, setUserPath] = useState<string>("");
  const [loading, setLoading] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [scores, setScores] = useState<Scores | null>(null);
  const [feedback, setFeedback] = useState<string>("");
  const [feedbackLoading, setFeedbackLoading] = useState<boolean>(false);

  const handleUpload = async (file: File | null, type: "reference" | "user") => {
    if (!file) {
      setError(`Please select a ${type} file.`);
      return;
    }

    setLoading(`Uploading ${type} audio and extracting vocals...`);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = (await res.json()) as ErrorResponse;
        throw new Error(errData.detail || `Upload failed for ${type}`);
      }

      const data = await res.json();

      if (type === "reference") {
        setReferencePath(data.vocals_path);
      } else {
        setUserPath(data.vocals_path);
      }
    } catch (error: unknown) {
      setError(getErrorMessage(error, `Upload failed for ${type}`));
    } finally {
      setLoading("");
    }
  };

  const handleAnalyze = async () => {
    if (!referencePath || !userPath) {
      setError("Please upload and process both reference and user files first.");
      return;
    }

    setLoading("Analyzing performance (this may take a minute)...");
    setError("");
    setScores(null);
    setFeedback("");

    try {
      const res = await fetch(`${API_BASE}/analyze-performance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reference_vocals_path: referencePath,
          user_vocals_path: userPath,
        }),
      });

      if (!res.ok) {
        const errData = (await res.json()) as ErrorResponse;
        throw new Error(errData.detail || "Analysis failed");
      }

      const data = await res.json();
      setScores({
        overall_score: data.overall_score,
        pitch_score: data.pitch_score,
        rhythm_score: data.rhythm_score,
        tempo_score: data.tempo_score,
        timbre_score: data.timbre_score,
      });
    } catch (error: unknown) {
      setError(getErrorMessage(error, "Analysis failed"));
    } finally {
      setLoading("");
    }
  };

  const handleGenerateFeedback = async () => {
    if (!scores) {
      setError("Please analyze performance first.");
      return;
    }

    setError("");
    setFeedbackLoading(true);

    try {
      const res = await fetch(`${API_BASE}/generate-feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pitch_score: scores.pitch_score,
          rhythm_score: scores.rhythm_score,
          tempo_score: scores.tempo_score,
          timbre_score: scores.timbre_score,
          overall_score: scores.overall_score,
        }),
      });

      if (!res.ok) {
        const errData = (await res.json()) as ErrorResponse;
        throw new Error(errData.detail || "AI feedback generation failed");
      }

      const data = await res.json();
      setFeedback(data.feedback || "");
    } catch (error: unknown) {
      setError(getErrorMessage(error, "AI feedback generation failed"));
    } finally {
      setFeedbackLoading(false);
    }
  };

  return (
    <PageContainer className="flex flex-col gap-8">
      <section className="space-y-3 text-center">
        <p className="text-sm uppercase tracking-[0.3em] text-white/55">Analyze Page</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Performance Analysis</h1>
        <p className="mx-auto max-w-2xl text-sm leading-7 text-slate-200 sm:text-base">
          Upload your reference and user vocals, run the analysis, then optionally generate AI feedback.
        </p>
      </section>

      {error && (
        <div className="rounded-2xl border border-rose-400/30 bg-rose-500/15 px-4 py-3 text-sm text-rose-100 backdrop-blur-md">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="rounded-2xl border border-sky-400/30 bg-sky-500/15 px-4 py-3 text-center text-sm font-medium text-sky-100 backdrop-blur-md animate-pulse">
          {loading}
        </div>
      )}

      <section className="grid gap-6 md:grid-cols-2">
        <GlassCard className="text-white">
          <div className="space-y-4">
            <div>
              <p className="text-sm uppercase tracking-[0.22em] text-white/55">Reference Upload</p>
              <h2 className="mt-1 text-xl font-semibold">1. Reference Audio</h2>
            </div>
            <input
              type="file"
              accept=".wav,.mp3"
              onChange={(e) => setReferenceFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-white/70 file:mr-4 file:rounded-full file:border-0 file:bg-white file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950 hover:file:bg-slate-200"
            />
            <button
              onClick={() => handleUpload(referenceFile, "reference")}
              disabled={!referenceFile || !!loading || !!referencePath}
              className={`w-full rounded-full px-4 py-3 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
                referencePath ? "bg-emerald-500/80 text-white" : "bg-white text-slate-950 hover:bg-slate-200"
              }`}
            >
              {referencePath ? "Reference Processed ✓" : "Upload Reference"}
            </button>
          </div>
        </GlassCard>

        <GlassCard className="text-white">
          <div className="space-y-4">
            <div>
              <p className="text-sm uppercase tracking-[0.22em] text-white/55">User Upload</p>
              <h2 className="mt-1 text-xl font-semibold">2. User Performance</h2>
            </div>
            <input
              type="file"
              accept=".wav,.mp3"
              onChange={(e) => setUserFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-white/70 file:mr-4 file:rounded-full file:border-0 file:bg-white file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950 hover:file:bg-slate-200"
            />
            <button
              onClick={() => handleUpload(userFile, "user")}
              disabled={!userFile || !!loading || !!userPath}
              className={`w-full rounded-full px-4 py-3 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
                userPath ? "bg-emerald-500/80 text-white" : "bg-white text-slate-950 hover:bg-slate-200"
              }`}
            >
              {userPath ? "Performance Processed ✓" : "Upload User Audio"}
            </button>
          </div>
        </GlassCard>
      </section>

      <div className="flex justify-center">
        <button
          onClick={handleAnalyze}
          disabled={!referencePath || !userPath || !!loading}
          className="rounded-full bg-sky-500 px-8 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-sky-500/20 transition-colors hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Analyze Performance
        </button>
      </div>

      {scores && (
        <section className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="md:col-span-2">
              <OverallScoreCard value={scores.overall_score} />
            </div>
            <ScoreCard label="Pitch" value={scores.pitch_score} />
            <ScoreCard label="Rhythm" value={scores.rhythm_score} />
            <ScoreCard label="Tempo" value={scores.tempo_score} />
            <ScoreCard label="Timbre" value={scores.timbre_score} />
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold text-white">AI Feedback</h3>
              <p className="mt-1 text-sm text-slate-300">Optional feedback generated only when you request it.</p>
            </div>

            {!feedback && (
              <button
                onClick={handleGenerateFeedback}
                disabled={feedbackLoading}
                className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition-colors hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {feedbackLoading && <span className="h-4 w-4 rounded-full border-2 border-slate-950/20 border-t-slate-950 animate-spin" />}
                {feedbackLoading ? "Generating AI feedback..." : "Generate AI Feedback"}
              </button>
            )}

            {feedback && <FeedbackCard feedback={feedback} />}
          </div>
        </section>
      )}
    </PageContainer>
  );
}