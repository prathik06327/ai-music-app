"use client";

import { ResponsiveContainer, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Line } from "recharts";
import GlassCard from "../../components/ui/GlassCard";
import { PitchPoint } from "../../../lib/api";

interface PitchGraphProps {
  pitchPoints: PitchPoint[];
  minPitch: number;
  maxPitch: number;
  frequencyToNote: (freq: number) => string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: PitchPoint;
  }>;
}

export default function PitchGraph({
  pitchPoints,
  minPitch,
  maxPitch,
  frequencyToNote,
}: PitchGraphProps) {
  // Pad the vertical domain slightly to give the line breathing room
  const yDomainMin = Math.max(0, Math.floor(minPitch - 20));
  const yDomainMax = Math.ceil(maxPitch + 20);

  // Custom tool tip component to match the dark theme and float beautifully
  const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as PitchPoint;
      const note = frequencyToNote(data.pitch);

      return (
        <div className="rounded-xl border border-white/20 bg-slate-950/90 p-4 shadow-xl backdrop-blur-md">
          <p className="text-[10px] uppercase font-bold tracking-widest text-sky-400">Vocal Pitch Point</p>
          <div className="mt-2 space-y-1 text-sm text-white">
            <div className="flex justify-between gap-6">
              <span className="text-white/50">Time:</span>
              <span className="font-semibold">{data.time.toFixed(2)} s</span>
            </div>
            <div className="flex justify-between gap-6">
              <span className="text-white/50">Pitch:</span>
              <span className="font-semibold">{data.pitch.toFixed(1)} Hz</span>
            </div>
            {note && (
              <div className="flex justify-between gap-6">
                <span className="text-white/50">Musical Note:</span>
                <span className="font-bold text-indigo-300 bg-indigo-500/10 px-1.5 py-0.5 rounded text-xs">
                  {note}
                </span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <GlassCard className="p-6 border border-white/10 w-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-6">
        <div>
          <h3 className="font-bold text-white text-base">Pitch Tracking Contour</h3>
          <p className="text-xs text-white/40">Real-time pitch tracking profile extracted in Hz</p>
        </div>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-sky-500" />
            <span className="text-white/60">Pitch Contour</span>
          </div>
        </div>
      </div>

      <div className="h-[350px] w-full select-none">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={pitchPoints}
            margin={{ top: 5, right: 10, left: -20, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255, 255, 255, 0.05)"
              vertical={false}
            />
            <XAxis
              dataKey="time"
              type="number"
              domain={["auto", "auto"]}
              stroke="rgba(255, 255, 255, 0.3)"
              tick={{ fill: "rgba(255, 255, 255, 0.5)", fontSize: 11 }}
              tickFormatter={(val: number) => `${val.toFixed(1)}s`}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="number"
              domain={[yDomainMin, yDomainMax]}
              stroke="rgba(255, 255, 255, 0.3)"
              tick={{ fill: "rgba(255, 255, 255, 0.5)", fontSize: 11 }}
              tickFormatter={(val: number) => `${val.toFixed(0)}Hz`}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{ stroke: "rgba(255, 255, 255, 0.15)", strokeWidth: 1 }}
              wrapperStyle={{ outline: "none" }}
            />
            <Line
              type="monotone"
              dataKey="pitch"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 4,
                stroke: "#ffffff",
                strokeWidth: 2,
                fill: "#0ea5e9",
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
