import type { ReactNode } from "react";

type GlassCardProps = {
  children: ReactNode;
  className?: string;
};

export default function GlassCard({ children, className = "" }: GlassCardProps) {
  return (
    <div className={`rounded-2xl border border-white/20 bg-white/10 p-5 shadow-lg backdrop-blur-md ${className}`}>
      {children}
    </div>
  );
}