import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import StatusBadge from "./components/ui/StatusBadge";
import Threads from "./components/background/Threads";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Music Analysis Prototype",
  description: "MVP for demonstrating backend music analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-950 text-slate-50 overflow-x-hidden`}>
        <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden bg-slate-950">
          <Threads
            className="absolute inset-0 h-full w-full"
            color={[0.9, 0.95, 1]}
            amplitude={0.9}
            distance={0.15}
            enableMouseInteraction={false}
          />
          <div className="absolute inset-0 bg-slate-950/70" />
        </div>
        <div className="relative z-20">
          <StatusBadge />
        </div>
        {children}
      </body>
    </html>
  );
}
