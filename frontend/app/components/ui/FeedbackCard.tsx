import GlassCard from "./GlassCard";

type FeedbackCardProps = {
  feedback: string;
};

export default function FeedbackCard({ feedback }: FeedbackCardProps) {
  return (
    <GlassCard className="p-6 text-slate-50">
      <h3 className="mb-4 text-xl font-semibold text-white">AI Performance Review</h3>
      <p className="whitespace-pre-line text-sm leading-7 text-slate-200">{feedback}</p>
    </GlassCard>
  );
}