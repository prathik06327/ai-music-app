import GlassCard from "../../components/ui/GlassCard";
import { PitchSummary } from "../../../lib/api";
import { ArrowDown, ArrowUp, Activity, Circle, Percent } from "lucide-react";

interface SummaryCardsProps {
  summary: PitchSummary;
  frequencyToNote: (freq: number) => string;
}

export default function SummaryCards({ summary, frequencyToNote }: SummaryCardsProps) {
  const cards = [
    {
      label: "Minimum Pitch",
      value: `${summary.minimum_pitch} Hz`,
      note: summary.minimum_note || frequencyToNote(summary.minimum_pitch),
      icon: ArrowDown,
      color: "text-sky-400 bg-sky-500/10 border-sky-500/20",
    },
    {
      label: "Maximum Pitch",
      value: `${summary.maximum_pitch} Hz`,
      note: summary.maximum_note || frequencyToNote(summary.maximum_pitch),
      icon: ArrowUp,
      color: "text-rose-400 bg-rose-500/10 border-rose-500/20",
    },
    {
      label: "Average Pitch",
      value: `${summary.average_pitch} Hz`,
      note: summary.average_note || frequencyToNote(summary.average_pitch),
      icon: Activity,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
    {
      label: "Median Pitch",
      value: `${summary.median_pitch} Hz`,
      note: frequencyToNote(summary.median_pitch),
      icon: Circle,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    },
    {
      label: "Pitch Range",
      value: `${summary.pitch_range} Hz`,
      note: "Interval",
      icon: Percent,
      color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    },
  ];

  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 w-full">
      {cards.map((card) => {
        const IconComponent = card.icon;
        return (
          <GlassCard key={card.label} className="flex flex-col justify-between p-5 transition-all duration-300 hover:scale-[1.02] hover:border-white/30 border border-white/10 relative overflow-hidden group">
            {/* Soft decorative background glow */}
            <div className="absolute -right-6 -bottom-6 w-16 h-16 bg-white/5 rounded-full blur-xl group-hover:bg-white/10 transition-all duration-300 pointer-events-none" />
            
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs font-semibold tracking-wider text-white/55 uppercase">
                {card.label}
              </span>
              <span className={`p-1.5 rounded-lg border ${card.color}`}>
                <IconComponent className="h-4 w-4" />
              </span>
            </div>

            <div className="mt-4 space-y-1">
              <div className="text-xl font-extrabold text-white tracking-tight">
                {card.value}
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] uppercase font-bold tracking-widest text-white/45">
                  Note:
                </span>
                <span className="text-xs font-semibold text-white/90 bg-white/5 px-2 py-0.5 rounded">
                  {card.note}
                </span>
              </div>
            </div>
          </GlassCard>
        );
      })}
    </div>
  );
}
