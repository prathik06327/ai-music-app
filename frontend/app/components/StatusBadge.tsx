"use client";

import { useEffect, useState } from "react";

export default function StatusBadge() {
  const [status, setStatus] = useState<"checking" | "connected" | "offline">("checking");

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch("http://localhost:8000/");
        if (response.ok) {
          const data = await response.json();
          if (data.message === "AI Music App Running") {
            setStatus("connected");
            return;
          }
        }
        setStatus("offline");
      } catch {
        setStatus("offline");
      }
    };

    checkStatus();
    // Optional: Check status every 10 seconds
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`border-b border-white/10 px-4 py-2 text-sm font-medium backdrop-blur-md ${
        status === "connected"
          ? "bg-emerald-500/15 text-emerald-200"
          : status === "offline"
            ? "bg-rose-500/15 text-rose-200"
            : "bg-amber-500/15 text-amber-100"
      }`}
    >
      <div className="mx-auto flex max-w-[1200px] items-center justify-center gap-2">
        <span className="uppercase tracking-[0.2em] text-[11px] text-white/60">Backend Status</span>
        {status === "checking" && <span>Checking ⏳</span>}
        {status === "connected" && <span>Connected ✅</span>}
        {status === "offline" && <span>Offline ❌</span>}
      </div>
    </div>
  );
}
