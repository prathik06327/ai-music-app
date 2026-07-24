import Link from "next/link";
import PageContainer from "./components/layout/PageContainer";
import GlassCard from "./components/ui/GlassCard";

export default function Home() {
  return (
    <PageContainer className="flex min-h-[calc(100vh-120px)] items-center justify-center py-12">
      <div className="w-full max-w-2xl">
        <GlassCard className="p-8 text-center text-white sm:p-12">
          <div className="mx-auto max-w-xl space-y-6">
            <p className="text-xs uppercase tracking-[0.3em] text-white/50">Vocal Assessment Tool</p>
            <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl text-white">
              AI Music Performance Analyzer
            </h1>
            <p className="mx-auto text-sm leading-relaxed text-slate-300 sm:text-base">
              Upload a reference recording and a performance recording. The system analyzes vocals using machine learning models and generates performance scores.
            </p>
            <div className="pt-4 flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/analyze"
                className="inline-flex items-center justify-center rounded-full bg-white px-8 py-3 text-sm font-semibold text-slate-950 transition-all hover:bg-slate-200 hover:scale-[1.03] focus:outline-none focus:ring-2 focus:ring-white/60 active:scale-[0.98] duration-150 cursor-pointer shadow-lg w-full sm:w-auto"
              >
                Start Analysis
              </Link>
              <Link
                href="/pitch-visualization"
                className="inline-flex items-center justify-center rounded-full border border-white/20 bg-white/5 px-8 py-3 text-sm font-semibold text-white transition-all hover:bg-white/10 hover:scale-[1.03] focus:outline-none focus:ring-2 focus:ring-white/60 active:scale-[0.98] duration-150 cursor-pointer shadow-lg w-full sm:w-auto"
              >
                Pitch Visualization
              </Link>
            </div>
          </div>
        </GlassCard>
      </div>
    </PageContainer>
  );
}
