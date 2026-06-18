"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  getBackendStatus,
  uploadAudio,
  analyzePerformance,
  generateFeedback,
  Scores,
} from "../../lib/api";
import PageContainer from "../components/layout/PageContainer";
import GlassCard from "../components/ui/GlassCard";
import OverallScoreCard from "../components/ui/OverallScoreCard";
import ScoreCard from "../components/ui/ScoreCard";
import FeedbackCard from "../components/ui/FeedbackCard";

export default function AnalyzePage() {
  // Section 1: Backend Status State
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);

  // Section 2 & 3: Audio Upload States
  const [referenceFile, setReferenceFile] = useState<File | null>(null);
  const [performanceFile, setPerformanceFile] = useState<File | null>(null);
  const [referencePath, setReferencePath] = useState<string>("");
  const [userPath, setUserPath] = useState<string>("");

  // Loading and Error States
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingText, setLoadingText] = useState<string>("");
  const [error, setError] = useState<string>("");

  // Section 5: Results State
  const [scores, setScores] = useState<Scores | null>(null);
  const [graphPath, setGraphPath] = useState<string | undefined>(undefined);

  // Section 6: AI Feedback State
  const [feedback, setFeedback] = useState<string>("");
  const [feedbackLoading, setFeedbackLoading] = useState<boolean>(false);

  // Check backend status on load
  useEffect(() => {
    const checkStatus = async () => {
      const isConnected = await getBackendStatus();
      setBackendConnected(isConnected);
    };
    checkStatus();
  }, []);

  // Handle file uploads
  const handleUpload = async (file: File | null, type: "reference" | "user") => {
    if (!file) {
      setError(`Please select a file to upload for ${type} recording.`);
      return;
    }

    setLoading(true);
    setLoadingText(`Uploading ${type === "reference" ? "Reference" : "Performance"} recording...`);
    setError("");

    try {
      const response = await uploadAudio(file);
      if (response.success && response.vocals_path) {
        if (type === "reference") {
          setReferencePath(response.vocals_path);
        } else {
          setUserPath(response.vocals_path);
        }
      } else {
        throw new Error("Invalid response format received from upload server.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to process audio file.";
      setError(`Upload failed: ${msg}`);
    } finally {
      setLoading(false);
      setLoadingText("");
    }
  };

  // Run performance analysis
  const handleAnalyze = async () => {
    if (!referencePath || !userPath) {
      setError("Please ensure both Reference and Performance files are uploaded successfully.");
      return;
    }

    setLoading(true);
    setLoadingText("Analyzing Performance...");
    setError("");
    setScores(null);
    setGraphPath(undefined);
    setFeedback("");

    try {
      const result = await analyzePerformance(referencePath, userPath);
      setScores(result);
      if (result.graph_path) {
        setGraphPath(result.graph_path);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Backend was unable to analyze audio files.";
      setError(`Analysis failed: ${msg}`);
    } finally {
      setLoading(false);
      setLoadingText("");
    }
  };

  // Generate Optional AI Feedback
  const handleGenerateFeedback = async () => {
    if (!scores) {
      setError("Please perform the analysis before requesting AI Feedback.");
      return;
    }

    setError("");
    setFeedbackLoading(true);

    try {
      const result = await generateFeedback({
        pitch_score: scores.pitch_score,
        rhythm_score: scores.rhythm_score,
        tempo_score: scores.tempo_score,
        timbre_score: scores.timbre_score,
        overall_score: scores.overall_score,
      });
      setFeedback(result.feedback);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Backend could not connect to feedback models.";
      setError(`Feedback generation failed: ${msg}`);
    } finally {
      setFeedbackLoading(false);
    }
  };

  // Clear all states to start a new analysis
  const handleReset = () => {
    setReferenceFile(null);
    setPerformanceFile(null);
    setReferencePath("");
    setUserPath("");
    setScores(null);
    setGraphPath(undefined);
    setFeedback("");
    setError("");
  };

  return (
    <PageContainer className="flex flex-col gap-8 pb-24">
      {/* Back navigation & Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <Link
            href="/"
            className="text-xs uppercase tracking-wider text-white/50 hover:text-white transition-colors duration-150"
          >
            ← Back to Home
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1">
            Performance Analyzer
          </h1>
        </div>
        {scores && (
          <button
            onClick={handleReset}
            className="rounded-full border border-white/20 bg-white/5 px-4 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-white/10 cursor-pointer"
          >
            Reset Analysis
          </button>
        )}
      </div>

      {/* ERROR DISPLAY */}
      {error && (
        <GlassCard className="border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">
          <div className="flex gap-2">
            <span className="font-bold">Error:</span>
            <p className="flex-1">{error}</p>
          </div>
        </GlassCard>
      )}



      {/* SECTIONS 2 & 3: Upload Area */}
      <section className="grid gap-6 md:grid-cols-2">
        {/* Section 2: Reference Recording Upload Card */}
        <GlassCard className="flex flex-col justify-between space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-white/70">
                Reference Recording
              </h2>
              <span className="text-[10px] uppercase font-bold tracking-widest text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded">
                Source File
              </span>
            </div>
            <p className="text-xs text-slate-300">
              Provide the high-quality target or coach vocal recording to align pitches against.
            </p>
          </div>

          <div className="space-y-4">
            <div className="relative border-2 border-dashed border-white/10 hover:border-white/20 rounded-xl p-4 transition-colors duration-150">
              <input
                type="file"
                accept=".mp3,.wav"
                onChange={(e) => setReferenceFile(e.target.files?.[0] || null)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={loading}
              />
              <div className="text-center space-y-1">
                <p className="text-sm font-medium text-white/70">
                  {referenceFile ? referenceFile.name : "Select or drag .mp3 / .wav file"}
                </p>
                <p className="text-xs text-white/30">Maximum size 50MB</p>
              </div>
            </div>

            {referencePath ? (
              <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 text-center text-sm font-semibold text-emerald-300 animate-fade-in">
                ✓ Upload Successful
              </div>
            ) : (
              <button
                onClick={() => handleUpload(referenceFile, "reference")}
                disabled={!referenceFile || loading}
                className="w-full rounded-full bg-white px-4 py-2.5 text-xs font-bold text-slate-950 transition-all hover:bg-slate-200 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                Upload & Process Reference
              </button>
            )}
          </div>
        </GlassCard>

        {/* Section 3: Performance Recording Upload Card */}
        <GlassCard className="flex flex-col justify-between space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-white/70">
                Performance Recording
              </h2>
              <span className="text-[10px] uppercase font-bold tracking-widest text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded">
                Your Attempt
              </span>
            </div>
            <p className="text-xs text-slate-300">
              Upload your vocal performance recording to be separated and scored.
            </p>
          </div>

          <div className="space-y-4">
            <div className="relative border-2 border-dashed border-white/10 hover:border-white/20 rounded-xl p-4 transition-colors duration-150">
              <input
                type="file"
                accept=".mp3,.wav"
                onChange={(e) => setPerformanceFile(e.target.files?.[0] || null)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={loading}
              />
              <div className="text-center space-y-1">
                <p className="text-sm font-medium text-white/70">
                  {performanceFile ? performanceFile.name : "Select or drag .mp3 / .wav file"}
                </p>
                <p className="text-xs text-white/30">Maximum size 50MB</p>
              </div>
            </div>

            {userPath ? (
              <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 text-center text-sm font-semibold text-emerald-300 animate-fade-in">
                ✓ Upload Successful
              </div>
            ) : (
              <button
                onClick={() => handleUpload(performanceFile, "user")}
                disabled={!performanceFile || loading}
                className="w-full rounded-full bg-white px-4 py-2.5 text-xs font-bold text-slate-950 transition-all hover:bg-slate-200 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                Upload & Process Performance
              </button>
            )}
          </div>
        </GlassCard>
      </section>

      {/* SECTION 4: Analyze Button & Spinner */}
      <section id="analyze-action" className="flex flex-col items-center justify-center py-4 space-y-4">
        {loading && loadingText && (
          <div className="flex flex-col items-center gap-3 animate-pulse">
            <span className="h-6 w-6 rounded-full border-2 border-white/20 border-t-white animate-spin" />
            <p className="text-sm text-sky-400 font-semibold">{loadingText}</p>
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={!referencePath || !userPath || loading}
          className="rounded-full bg-sky-500 hover:bg-sky-400 active:scale-[0.98] transition-all px-10 py-3.5 text-sm font-extrabold text-slate-950 shadow-lg shadow-sky-500/20 disabled:opacity-40 disabled:cursor-not-allowed disabled:scale-100 cursor-pointer flex items-center gap-2"
        >
          {loading && loadingText === "Analyzing Performance..." && (
            <span className="h-4 w-4 rounded-full border-2 border-slate-950/20 border-t-slate-950 animate-spin" />
          )}
          {loading && loadingText === "Analyzing Performance..."
            ? "Analyzing Performance..."
            : "Analyze Performance"}
        </button>

        {!referencePath || !userPath ? (
          <p className="text-[11px] text-white/35">
            * Please process both Reference and Performance audio tracks above to activate analysis.
          </p>
        ) : null}
      </section>

      {/* SECTION 5: Results Rendering */}
      {scores && (
        <section id="analysis-results" className="space-y-8 scroll-mt-6 border-t border-white/10 pt-8">
          <div className="space-y-2 text-center">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-white/70">
              Performance Results
            </h2>
            <p className="text-xs text-white/40">
              Comparing aligned vocal features across 10 distinct scoring dimensions
            </p>
          </div>

          {/* Overall Score - Centered and Large */}
          <div className="flex justify-center">
            <div className="w-full max-w-lg">
              <OverallScoreCard value={scores.overall_score} />
            </div>
          </div>

          {/* Grid of Other 10 Metrics */}
          <div className="grid gap-4 sm:grid-cols-2">
            <ScoreCard title="Pitch Accuracy" score={scores.pitch_score} />
            <ScoreCard title="Rhythm Precision" score={scores.rhythm_score} />
            <ScoreCard title="Tempo Consistency" score={scores.tempo_score} />
            <ScoreCard title="Timbre Similarity" score={scores.timbre_score} />
            <ScoreCard title="Melodic Interval" score={scores.melody_score} />
            <ScoreCard title="Dynamics Control" score={scores.dynamics_score} />
            <ScoreCard title="Vocal Stability" score={scores.stability_score} />
            <ScoreCard title="Pronunciation" score={scores.pronunciation_score} />
            <ScoreCard title="Vocal Range" score={scores.range_score} />
            <ScoreCard title="Harmonic Alignment" score={scores.harmonic_score} />
          </div>

          {/* Visualization Subsection */}
          {graphPath ? (
            <div className="space-y-3 pt-4 border-t border-white/5">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70 text-center">
                Pitch Comparison Graph
              </h3>
              <GlassCard className="p-4 flex flex-col items-center justify-center overflow-hidden">
                {/* Visualizing Pitch Comparison via direct backend static route */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`http://localhost:8000/${graphPath}`}
                  alt="Pitch Comparison"
                  className="rounded-lg max-h-[350px] w-auto border border-white/10 object-contain"
                  onError={() => setGraphPath(undefined)} // Hide image block if file fails to load
                />
                <p className="text-xs text-white/40 mt-2">
                  Aligned pitch tracking profiles (Hz) vs frame timeline
                </p>
              </GlassCard>
            </div>
          ) : null}
        </section>
      )}

      {/* SECTION 6: AI Feedback */}
      {scores && (
        <section id="ai-feedback" className="space-y-6 scroll-mt-6 border-t border-white/10 pt-8">
          <div className="space-y-2 text-center">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-white/70">
              AI Feedback
            </h2>
            <p className="text-xs text-white/40">
              Generate constructive vocal coach notes based on your metric scores
            </p>
          </div>

          <div className="flex flex-col items-center justify-center space-y-4">
            {!feedback && (
              <button
                onClick={handleGenerateFeedback}
                disabled={feedbackLoading}
                className="inline-flex items-center gap-2.5 rounded-full bg-emerald-500 hover:bg-emerald-400 active:scale-[0.98] transition-all px-8 py-3 text-xs font-bold text-slate-950 disabled:opacity-55 disabled:cursor-not-allowed cursor-pointer"
              >
                {feedbackLoading && (
                  <span className="h-4 w-4 rounded-full border-2 border-slate-950/20 border-t-slate-950 animate-spin" />
                )}
                {feedbackLoading ? "Generating Feedback..." : "Generate AI Feedback"}
              </button>
            )}

            {feedback && <FeedbackCard feedback={feedback} />}
          </div>
        </section>
      )}
    </PageContainer>
  );
}