import GlassCard from "../../components/ui/GlassCard";
import { SustainedRegion, StableRegion, PitchTransition } from "../../../lib/api";
import { Timer, Radio, RefreshCw, ChevronUp, ChevronDown } from "lucide-react";

interface RegionsListProps {
  sustainedRegions: SustainedRegion[];
  stableRegions: StableRegion[];
  transitions: PitchTransition[];
}

export default function RegionsList({
  sustainedRegions,
  stableRegions,
  transitions,
}: RegionsListProps) {
  return (
    <div className="space-y-6 w-full">
      {/* Sustained Regions */}
      <GlassCard className="border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-3">
          <Timer className="h-5 w-5 text-indigo-400" />
          <div>
            <h3 className="font-bold text-white text-base">Sustained Vocal Regions</h3>
            <p className="text-xs text-white/40">Contiguous voiced intervals held on a single musical note</p>
          </div>
        </div>

        {sustainedRegions.length === 0 ? (
          <p className="text-sm text-white/35 py-4 text-center">No sustained regions detected in this recording.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50 text-xs uppercase tracking-wider">
                  <th className="py-2 px-3">Note</th>
                  <th className="py-2 px-3">Start Time</th>
                  <th className="py-2 px-3">Duration</th>
                  <th className="py-2 px-3">Avg Frequency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {sustainedRegions.map((region, idx) => (
                  <tr key={idx} className="hover:bg-white/5 transition-colors">
                    <td className="py-3 px-3">
                      <span className="font-bold text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded text-xs">
                        {region.note}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-white/80">{region.start_time.toFixed(2)} s</td>
                    <td className="py-3 px-3 text-white/80">{region.duration.toFixed(2)} seconds</td>
                    <td className="py-3 px-3 text-white/60">{region.average_pitch.toFixed(1)} Hz</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* Stable Regions */}
      <GlassCard className="border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-3">
          <Radio className="h-5 w-5 text-emerald-400" />
          <div>
            <h3 className="font-bold text-white text-base">Stable Pitch Regions</h3>
            <p className="text-xs text-white/40">Vocal regions displaying exceptionally low frequency variance</p>
          </div>
        </div>

        {stableRegions.length === 0 ? (
          <p className="text-sm text-white/35 py-4 text-center">No stable regions detected in this recording.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50 text-xs uppercase tracking-wider">
                  <th className="py-2 px-3">Interval</th>
                  <th className="py-2 px-3">Duration</th>
                  <th className="py-2 px-3">Average Pitch</th>
                  <th className="py-2 px-3">Stability (Std Dev)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {stableRegions.map((region, idx) => (
                  <tr key={idx} className="hover:bg-white/5 transition-colors">
                    <td className="py-3 px-3 text-white/80">
                      {region.start_time.toFixed(2)} s – {region.end_time.toFixed(2)} s
                    </td>
                    <td className="py-3 px-3 text-white/80">{region.duration.toFixed(2)} s</td>
                    <td className="py-3 px-3">
                      <span className="text-white font-medium mr-2">{region.average_pitch.toFixed(1)} Hz</span>
                      <span className="text-xs text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded font-bold">
                        {region.note}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-white/60">
                      ±{region.stability.toFixed(2)} semitones
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* Pitch Transitions */}
      <GlassCard className="border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-3">
          <RefreshCw className="h-5 w-5 text-rose-400" />
          <div>
            <h3 className="font-bold text-white text-base">Key Pitch Transitions</h3>
            <p className="text-xs text-white/40">Vocal pitch jumps of 2 semitones or more detected</p>
          </div>
        </div>

        {transitions.length === 0 ? (
          <p className="text-sm text-white/35 py-4 text-center">No major pitch transitions detected.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50 text-xs uppercase tracking-wider">
                  <th className="py-2 px-3">Time</th>
                  <th className="py-2 px-3">Transition</th>
                  <th className="py-2 px-3">Interval Change</th>
                  <th className="py-2 px-3">Direction</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {transitions.map((t, idx) => (
                  <tr key={idx} className="hover:bg-white/5 transition-colors">
                    <td className="py-3 px-3 text-white/80">{t.time.toFixed(2)} s</td>
                    <td className="py-3 px-3 flex items-center gap-2 text-white/80 mt-1">
                      <span className="font-bold text-white/95">{t.from_note}</span>
                      <span className="text-white/30 text-xs">→</span>
                      <span className="font-bold text-white/95">{t.to_note}</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`font-semibold ${t.direction === "up" ? "text-emerald-400" : "text-rose-400"}`}>
                        {t.semitone_change > 0 ? `+${t.semitone_change.toFixed(1)}` : t.semitone_change.toFixed(1)} semitones
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {t.direction === "up" ? (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                          <ChevronUp className="h-3 w-3" /> Up
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full">
                          <ChevronDown className="h-3 w-3" /> Down
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
