import GlassCard from "./GlassCard";

type ScoreCardProps = {
  title: string;
  score: number;
};

export default function ScoreCard({ title, score }: ScoreCardProps) {
  return (
    <GlassCard className="p-4 text-center text-slate-50">
      <div className="mb-1 text-sm uppercase tracking-[0.16em] text-white/60">{title}</div>
      <div className="text-2xl font-semibold text-white">{score.toFixed(2)}</div>
    </GlassCard>
  );
}