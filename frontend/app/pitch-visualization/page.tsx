"use client";

import { useState } from "react";
import Link from "next/link";
import { uploadAudio, getPitchVisualization, PitchVisualizationResult } from "../../lib/api";
import PageContainer from "../components/layout/PageContainer";
import GlassCard from "../components/ui/GlassCard";
import PitchGraph from "./components/PitchGraph";
import SummaryCards from "./components/SummaryCards";
import HighestLowestCard from "./components/HighestLowestCard";
import RegionsList from "./components/RegionsList";
import { Music, UploadCloud } from "lucide-react";

// Note mapping constants and helper
const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const frequencyToNote = (frequencyHz: number): string => {
  if (!isFinite(frequencyHz) || frequencyHz <= 0) return "N/A";
  const midiNote = Math.round(69 + 12 * Math.log2(frequencyHz / 440));
  const noteName = NOTE_NAMES[((midiNote % 12) + 12) % 12];
  const octave = Math.floor(midiNote / 12) - 1;
  return `${noteName}${octave}`;
};

// Size formatting helper
const formatBytes = (bytes: number, decimals = 2) => {
  if (!bytes) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

export default function PitchVisualizationPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingText, setLoadingText] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [visualizationData, setVisualizationData] = useState<PitchVisualizationResult | null>(null);

  // Start processing vocal pitch track
  const handleGenerateVisualization = async () => {
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    setLoading(true);
    setError("");
    setVisualizationData(null);

    try {
      // Step 1: Upload the raw recording to separate vocals using Demucs
      setLoadingText("Uploading audio & separating vocals...");
      const uploadRes = await uploadAudio(file);

      if (!uploadRes.success || !uploadRes.vocals_path) {
        throw new Error("Vocal extraction failed. Invalid response format.");
      }

      // Step 2: Pitch tracking analysis and metadata generation
      setLoadingText("Generating pitch visualization...");
      const visRes = await getPitchVisualization(uploadRes.vocals_path);
      setVisualizationData(visRes);
    } catch (err: unknown) {
      console.error("Pitch visualization error:", err);
      // Clean display card error as per user constraints (no stack traces)
      setError("Visualization generation failed. Please try another recording.");
    } finally {
      setLoading(false);
      setLoadingText("");
    }
  };

  const handleReset = () => {
    setFile(null);
    setError("");
    setVisualizationData(null);
    setLoading(false);
    setLoadingText("");
  };

  return (
    <PageContainer className="flex flex-col gap-8 pb-24">
      {/* Header section with back navigation */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <Link
            href="/"
            className="text-xs uppercase tracking-wider text-white/50 hover:text-white transition-colors duration-150"
          >
            ← Back to Home
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1">
            Pitch Visualization
          </h1>
        </div>
        {visualizationData && (
          <button
            onClick={handleReset}
            className="rounded-full border border-white/20 bg-white/5 px-4 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-white/10 cursor-pointer"
          >
            Reset Visualization
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

      {/* UPLOAD SECTION CARD */}
      {!visualizationData && !loading && (
        <GlassCard className="flex flex-col space-y-6 max-w-xl mx-auto w-full border border-white/10 p-6 sm:p-8">
          <div className="space-y-2 text-center">
            <div className="inline-flex p-3 rounded-full bg-white/5 border border-white/10 text-white/80 mb-2">
              <UploadCloud className="h-6 w-6" />
            </div>
            <h2 className="text-lg font-bold text-white">Upload Vocal Performance</h2>
            <p className="text-xs text-white/40 max-w-md mx-auto">
              Upload a .wav or .mp3 recording. We will isolate the vocals and render an interactive pitch tracker.
            </p>
          </div>

          <div className="space-y-4">
            <div className="relative border-2 border-dashed border-white/10 hover:border-white/20 rounded-xl p-8 transition-colors duration-150 bg-white/[0.01]">
              <input
                type="file"
                accept=".mp3,.wav"
                onChange={(e) => {
                  setFile(e.target.files?.[0] || null);
                  setError("");
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={loading}
              />
              <div className="text-center space-y-2">
                <Music className="mx-auto h-8 w-8 text-white/20" />
                <p className="text-sm font-semibold text-white/80">
                  {file ? file.name : "Select or drag file here"}
                </p>
                {file && (
                  <p className="text-xs text-sky-400 font-medium">
                    File Size: {formatBytes(file.size)}
                  </p>
                )}
                {!file && <p className="text-xs text-white/30">Supported formats: .wav, .mp3 (Max 50MB)</p>}
              </div>
            </div>

            <button
              onClick={handleGenerateVisualization}
              disabled={!file || loading}
              className="w-full rounded-full bg-white hover:bg-slate-200 active:scale-[0.99] transition-all px-6 py-3 text-sm font-extrabold text-slate-950 disabled:opacity-40 disabled:cursor-not-allowed disabled:scale-100 cursor-pointer flex items-center justify-center gap-2"
            >
              Generate Visualization
            </button>
          </div>
        </GlassCard>
      )}

      {/* LOADING STATE CARD */}
      {loading && (
        <GlassCard className="flex flex-col items-center justify-center p-12 border border-white/10 max-w-xl mx-auto w-full space-y-4 min-h-[220px]">
          <span className="h-8 w-8 rounded-full border-2 border-white/20 border-t-sky-500 animate-spin" />
          <p className="text-sm text-sky-400 font-semibold animate-pulse">{loadingText}</p>
        </GlassCard>
      )}

      {/* EMPTY STATE */}
      {!visualizationData && !loading && (
        <div className="text-center py-10 border border-dashed border-white/5 rounded-xl bg-white/[0.01]">
          <p className="text-sm text-white/30">No visualization generated yet.</p>
        </div>
      )}

      {/* VISUALIZATION RESULTS */}
      {visualizationData && !loading && (
        <div className="space-y-8 animate-fade-in">
          {/* Pitch Chart Graph */}
          <PitchGraph
            pitchPoints={visualizationData.pitch_points}
            minPitch={visualizationData.summary.minimum_pitch}
            maxPitch={visualizationData.summary.maximum_pitch}
            frequencyToNote={frequencyToNote}
          />

          {/* Grid of Summary Stats */}
          <SummaryCards
            summary={visualizationData.summary}
            frequencyToNote={frequencyToNote}
          />

          {/* Highest / Lowest Note cards */}
          <HighestLowestCard
            highest={visualizationData.highest_pitch_point}
            lowest={visualizationData.lowest_pitch_point}
          />

          {/* Regions and transitions sections */}
          <RegionsList
            sustainedRegions={visualizationData.sustained_regions}
            stableRegions={visualizationData.stable_regions}
            transitions={visualizationData.pitch_transitions}
          />
        </div>
      )}
    </PageContainer>
  );
}
