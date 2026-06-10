import Link from "next/link";
import PageContainer from "./components/layout/PageContainer";
import GlassCard from "./components/ui/GlassCard";

export default function Home() {
  return (
    <PageContainer className="flex min-h-[calc(100vh-56px)] items-center justify-center">
      <div className="w-full max-w-3xl">
        <GlassCard className="p-8 text-center text-white sm:p-10">
          <div className="mx-auto max-w-2xl space-y-5">
            <p className="text-sm uppercase tracking-[0.3em] text-white/55">AI Music Analysis Prototype</p>
            <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Upload, analyze, and review vocal performance.</h1>
            <p className="mx-auto max-w-xl text-sm leading-7 text-slate-200 sm:text-base">
              Compare a reference vocal against a user recording, then optionally generate AI feedback after scoring.
            </p>
            <div className="pt-2">
              <Link
                href="/analyze"
                className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition-colors hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-white/60"
              >
                Start Analysis
              </Link>
            </div>
          </div>
        </GlassCard>
      </div>
    </PageContainer>
  );
}
