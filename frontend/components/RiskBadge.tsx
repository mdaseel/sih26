import type { RiskLevel } from "@/lib/types";

const STYLES: Record<RiskLevel, { box: string; dot: string; label: string; glow: string }> = {
  SAFE: { box: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300", dot: "bg-emerald-500", label: "Safe", glow: "shadow-emerald-500/20" },
  CAUTION: { box: "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-300", dot: "bg-amber-500", label: "Caution", glow: "shadow-amber-500/20" },
  CONSTRAINED: { box: "border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-950/50 dark:text-red-300", dot: "bg-red-500", label: "Constrained", glow: "shadow-red-500/20" },
};

export function RiskBadge({ risk, size = "md" }: { risk: RiskLevel; size?: "sm" | "md" | "lg" }) {
  const s = STYLES[risk];
  const sizing = size === "lg" ? "px-4 py-2 text-sm" : size === "sm" ? "px-2.5 py-1 text-xs" : "px-3 py-1.5 text-xs";
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border font-bold shadow-sm transition-all hover:scale-[1.03] active:scale-95 ${s.box} ${s.glow} ${sizing}`}>
      <span className="relative flex h-2 w-2">
        <span className={`absolute inline-flex h-full w-full animate-ping rounded-full ${s.dot} opacity-60`} />
        <span className={`relative inline-flex h-2 w-2 rounded-full ${s.dot}`} />
      </span>
      {s.label}
    </span>
  );
}

export function ProbabilityBar({ risk, value }: { risk: RiskLevel; value: number }) {
  const fill = risk === "SAFE" ? "bg-emerald-500" : risk === "CAUTION" ? "bg-amber-500" : "bg-red-500";
  const pct = Math.round(value * 1000) / 10;
  return (
    <div className="flex items-center gap-3">
      <span className="w-24 shrink-0 text-xs font-medium" style={{ color: "rgb(var(--ink-faint))" }}>{risk}</span>
      <div className="h-2.5 flex-1 overflow-hidden rounded-full" style={{ background: "rgb(var(--panel-raised))" }}>
        <div className={`h-full rounded-full transition-all duration-700 ease-[cubic-bezier(0.23,1,0.32,1)] ${fill}`} style={{ width: `${Math.max(pct, 0.5)}%` }} />
      </div>
      <span className="w-14 shrink-0 text-right font-mono text-xs font-bold tabular-nums" style={{ color: "rgb(var(--ink))" }}>{pct.toFixed(1)}%</span>
    </div>
  );
}
