import type { RiskLevel } from "@/lib/types";

const STYLES: Record<RiskLevel, { box: string; dot: string; label: string }> = {
  SAFE: {
    box: "border-green-800 bg-green-950/60 text-green-300",
    dot: "bg-green-400",
    label: "Safe",
  },
  CAUTION: {
    box: "border-yellow-800 bg-yellow-950/60 text-yellow-300",
    dot: "bg-yellow-400",
    label: "Caution",
  },
  CONSTRAINED: {
    box: "border-red-800 bg-red-950/60 text-red-300",
    dot: "bg-red-400",
    label: "Constrained",
  },
};

export function RiskBadge({
  risk,
  size = "md",
}: {
  risk: RiskLevel;
  size?: "sm" | "md" | "lg";
}) {
  const s = STYLES[risk];
  const sizing =
    size === "lg"
      ? "px-4 py-2 text-base"
      : size === "sm"
        ? "px-2 py-0.5 text-xs"
        : "px-3 py-1 text-sm";

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border font-semibold ${s.box} ${sizing}`}
    >
      <span className={`h-2 w-2 rounded-full ${s.dot}`} aria-hidden />
      {s.label}
    </span>
  );
}

/** Probability bar for one ML class. */
export function ProbabilityBar({
  risk,
  value,
}: {
  risk: RiskLevel;
  value: number;
}) {
  const fill =
    risk === "SAFE"
      ? "bg-green-500"
      : risk === "CAUTION"
        ? "bg-yellow-500"
        : "bg-red-500";
  const pct = Math.round(value * 1000) / 10;

  return (
    <div className="flex items-center gap-3">
      <span className="w-28 shrink-0 text-xs text-slate-400">{risk}</span>
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full ${fill}`}
          style={{ width: `${Math.max(pct, 0.5)}%` }}
        />
      </div>
      <span className="w-14 shrink-0 text-right font-mono text-xs tabular-nums text-slate-300">
        {pct.toFixed(1)}%
      </span>
    </div>
  );
}
