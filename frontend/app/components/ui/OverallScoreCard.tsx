import GlassCard from "./GlassCard";

type OverallScoreCardProps = {
  value: number;
};

export default function OverallScoreCard({ value }: OverallScoreCardProps) {
  return (
    <GlassCard className="p-6 text-center text-slate-50 md:p-8">
      <div className="mb-2 text-sm uppercase tracking-[0.22em] text-white/60">Overall Score</div>
      <div className="text-5xl font-semibold leading-none text-white sm:text-6xl">{value.toFixed(2)}</div>
      <div className="mt-2 text-sm text-white/60">out of 100</div>
    </GlassCard>
  );
}