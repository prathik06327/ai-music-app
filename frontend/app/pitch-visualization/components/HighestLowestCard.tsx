import GlassCard from "../../components/ui/GlassCard";
import { PitchExtremePoint } from "../../../lib/api";
import { ArrowUpCircle, ArrowDownCircle } from "lucide-react";

interface HighestLowestCardProps {
  highest: PitchExtremePoint;
  lowest: PitchExtremePoint;
}

export default function HighestLowestCard({ highest, lowest }: HighestLowestCardProps) {
  return (
    <div className="grid gap-6 md:grid-cols-2 w-full">
      {/* Highest Pitch Card */}
      <GlassCard className="flex flex-col justify-between border-sky-500/20 bg-sky-500/5 hover:border-sky-500/30 transition-all duration-300 p-6 relative overflow-hidden group">
        <div className="absolute right-0 top-0 w-24 h-24 bg-sky-500/5 rounded-full blur-2xl group-hover:bg-sky-500/10 transition-all duration-300 pointer-events-none" />
        
        <div className="flex items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-[10px] tracking-widest font-extrabold uppercase text-sky-400 bg-sky-500/10 px-2.5 py-1 rounded-full">
              Highest Vocal Extreme
            </span>
            <h3 className="text-lg font-bold text-white mt-2">Highest Note Reached</h3>
          </div>
          <span className="text-sky-400 p-2 bg-sky-500/10 border border-sky-500/20 rounded-xl">
            <ArrowUpCircle className="h-6 w-6" />
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-white/5">
          <div>
            <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider">Musical Note</p>
            <p className="text-xl font-extrabold text-white mt-1">{highest.note || "N/A"}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider">Frequency</p>
            <p className="text-xl font-extrabold text-white mt-1">{highest.pitch} Hz</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider">Timestamp</p>
            <p className="text-xl font-extrabold text-white mt-1">{highest.time} s</p>
          </div>
        </div>
      </GlassCard>

      {/* Lowest Pitch Card */}
      <GlassCard className="flex flex-col justify-between border-rose-500/20 bg-rose-500/5 hover:border-rose-500/30 transition-all duration-300 p-6 relative overflow-hidden group">
        <div className="absolute right-0 top-0 w-24 h-24 bg-rose-500/5 rounded-full blur-2xl group-hover:bg-rose-500/10 transition-all duration-300 pointer-events-none" />

        <div className="flex items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-[10px] tracking-widest font-extrabold uppercase text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-full">
              Lowest Vocal Extreme
            </span>
            <h3 className="text-lg font-bold text-white mt-2">Lowest Note Reached</h3>
          </div>
          <span className="text-rose-400 p-2 bg-rose-500/10 border border-rose-500/20 rounded-xl">
            <ArrowDownCircle className="h-6 w-6" />
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-white/5">
          <div>
            <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider">Musical Note</p>
            <p className="text-xl font-extrabold text-white mt-1">{lowest.note || "N/A"}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider">Frequency</p>
            <p className="text-xl font-extrabold text-white mt-1">{lowest.pitch} Hz</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider">Timestamp</p>
            <p className="text-xl font-extrabold text-white mt-1">{lowest.time} s</p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
