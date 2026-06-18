"use client";

import { useEffect, useState } from "react";
import { getBackendStatus } from "../../../lib/api";

export default function StatusBadge() {
  const [status, setStatus] = useState<"checking" | "connected" | "offline">("checking");

  useEffect(() => {
    const checkStatus = async () => {
      const isConnected = await getBackendStatus();
      setStatus(isConnected ? "connected" : "offline");
    };

    checkStatus();
    // Check status every 10 seconds
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`border-b border-white/10 px-4 py-2 text-sm font-medium backdrop-blur-md transition-colors duration-500 ${
        status === "connected"
          ? "bg-emerald-500/15 text-emerald-200"
          : status === "offline"
            ? "bg-rose-500/15 text-rose-200"
            : "bg-amber-500/15 text-amber-100"
      }`}
    >
      <div className="mx-auto flex max-w-[1200px] items-center justify-center gap-2">
        <span className="uppercase tracking-[0.2em] text-[11px] text-white/60">Backend Status</span>
        {status === "checking" && <span className="flex items-center gap-1.5 font-semibold text-amber-400">Checking <span className="inline-block animate-bounce">⏳</span></span>}
        {status === "connected" && <span className="font-semibold text-emerald-400">Connected ✓</span>}
        {status === "offline" && <span className="font-semibold text-rose-400 animate-pulse">Offline ✗</span>}
      </div>
    </div>
  );
}
