"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

import { RiskBadge } from "@/components/RiskBadge";
import { TwinDiagram } from "@/components/TwinDiagram";
import type { TwinResponse } from "@/lib/types";

const DistributionTwin3D = dynamic(
  () => import("@/components/twin/DistributionTwin3D").then((m) => m.DistributionTwin3D),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[580px] items-center justify-center rounded-2xl border border-slate-800 bg-[#0b1e33]">
        <div className="flex flex-col items-center gap-2">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-sky-400 border-t-transparent" />
          <span className="text-xs text-slate-400">Loading 3D Digital Twin environment…</span>
        </div>
      </div>
    ),
  }
);

interface DigitalTwinViewProps {
  twin?: TwinResponse | null;
  busId?: string;
  onSelectBus?: (bus: string) => void;
  title?: string;
  subtitle?: string;
  initialMode?: "2D" | "3D";
}

export function DigitalTwinView({
  twin,
  busId,
  onSelectBus,
  title = "Grid Digital Twin",
  subtitle = "Interactive 3D aerial distribution view & 2D schematic power flow",
  initialMode = "3D",
}: DigitalTwinViewProps) {
  const [mode, setMode] = useState<"2D" | "3D">(initialMode);

  return (
    <div className="space-y-3">
      {/* Top Controls Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/90 px-4 py-3 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-lg">
            {mode === "3D" ? "🌐" : "⚡"}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
              {twin?.assessment?.engineering?.engineering_risk && (
                <RiskBadge risk={twin.assessment.engineering.engineering_risk} />
              )}
            </div>
            <p className="text-xs text-slate-400">{subtitle}</p>
          </div>
        </div>

        {/* 2D / 3D Toggle Pill */}
        <div className="flex items-center gap-1 rounded-xl border border-slate-700/80 bg-slate-950 p-1 shadow-inner">
          <button
            type="button"
            onClick={() => setMode("2D")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              mode === "2D"
                ? "bg-gradient-to-r from-sky-600 to-blue-600 text-white shadow-md"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <span>📈</span>
            <span>2D Schematic</span>
          </button>

          <button
            type="button"
            onClick={() => setMode("3D")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              mode === "3D"
                ? "bg-gradient-to-r from-sky-600 to-blue-600 text-white shadow-md"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <span>🌐</span>
            <span>3D Aerial Twin</span>
          </button>
        </div>
      </div>

      {/* Main Render View */}
      {mode === "3D" ? (
        <DistributionTwin3D
          twin={twin}
          busId={busId}
          onSelectBus={onSelectBus}
          onToggle2D={() => setMode("2D")}
        />
      ) : (
        twin && <TwinDiagram twin={twin} />
      )}

      {!twin && mode === "2D" && (
        <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/40 p-8 text-center text-sm text-slate-500">
          No simulation dataset loaded for 2D schematic. Run a simulation to populate power flow results.
        </div>
      )}
    </div>
  );
}
