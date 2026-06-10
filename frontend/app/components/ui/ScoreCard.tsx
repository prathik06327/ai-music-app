import GlassCard from "./GlassCard";

type ScoreCardProps = {
  label: string;
  value: number;
};

export default function ScoreCard({ label, value }: ScoreCardProps) {
  return (
    <GlassCard className="p-4 text-center text-slate-50">
      <div className="mb-1 text-sm uppercase tracking-[0.16em] text-white/60">{label}</div>
      <div className="text-2xl font-semibold text-white">{value.toFixed(2)}</div>
    </GlassCard>
  );
}