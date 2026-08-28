/**
 * Threshold comparison, in one place.
 *
 * This logic was duplicated in GridMap and TwinDiagram, which is how two views
 * of the same network end up disagreeing about what counts as a violation.
 * It lives here instead so both render the same judgement, and so it can be
 * tested without mounting a component.
 *
 * These functions apply thresholds; they never define them. Every limit arrives
 * from the API as `thresholds_snapshot`, sourced from scenario_config.json. The
 * fallbacks below exist only so a missing key degrades to the documented value
 * rather than to `undefined`, which would compare false and quietly paint
 * everything green.
 */

import type { RiskLevel } from "@/lib/types";

export type Thresholds = Record<string, number>;

export const RISK_COLOURS = {
  SAFE: { fill: "#052e16", stroke: "#22c55e" },
  CAUTION: { fill: "#3b2f05", stroke: "#eab308" },
  CONSTRAINED: { fill: "#450a0a", stroke: "#ef4444" },
} as const;

export const NEUTRAL = "#64748b";

/** Documented defaults from scenario_config.json, used only if a key is absent. */
const FALLBACK: Thresholds = {
  voltage_hard_low_pu: 0.9,
  voltage_hard_high_pu: 1.05,
  voltage_caution_low_pu: 0.9,
  voltage_caution_high_pu: 1.03,
  voltage_rise_hard_pu: 0.05,
  voltage_rise_caution_pu: 0.03,
  line_loading_hard_pct: 100,
  line_loading_caution_pct: 80,
  transformer_loading_hard_pct: 100,
  transformer_loading_caution_pct: 95,
};

function limit(t: Thresholds, key: string): number {
  const value = t?.[key];
  return typeof value === "number" && Number.isFinite(value) ? value : FALLBACK[key];
}

/**
 * Judge a bus by its own voltage.
 *
 * Mirrors the backend rule order: hard limits first, then the caution band.
 */
export function voltageRisk(pu: number | null | undefined, t: Thresholds): RiskLevel | null {
  if (pu == null || !Number.isFinite(pu)) return null;
  if (pu > limit(t, "voltage_hard_high_pu") || pu < limit(t, "voltage_hard_low_pu")) {
    return "CONSTRAINED";
  }
  if (pu > limit(t, "voltage_caution_high_pu") || pu < limit(t, "voltage_caution_low_pu")) {
    return "CAUTION";
  }
  return "SAFE";
}

/**
 * Judge a connection point by how far its own voltage moved.
 *
 * Note the asymmetry, which matches dataset_generation_phase2.py: the hard
 * limit uses `>` and the caution band uses `>=`. That is how the training
 * labels were produced, so it is how they are reproduced.
 */
export function voltageRiseRisk(
  deltaPu: number | null | undefined,
  t: Thresholds
): RiskLevel | null {
  if (deltaPu == null || !Number.isFinite(deltaPu)) return null;
  const rise = Math.abs(deltaPu);
  if (rise > limit(t, "voltage_rise_hard_pu")) return "CONSTRAINED";
  if (rise >= limit(t, "voltage_rise_caution_pu")) return "CAUTION";
  return "SAFE";
}

export function loadingRisk(
  pct: number | null | undefined,
  hardKey: string,
  cautionKey: string,
  t: Thresholds
): RiskLevel | null {
  if (pct == null || !Number.isFinite(pct)) return null;
  if (pct > limit(t, hardKey)) return "CONSTRAINED";
  if (pct >= limit(t, cautionKey)) return "CAUTION";
  return "SAFE";
}

export const transformerRisk = (pct: number | null | undefined, t: Thresholds) =>
  loadingRisk(pct, "transformer_loading_hard_pct", "transformer_loading_caution_pct", t);

export const lineRisk = (pct: number | null | undefined, t: Thresholds) =>
  loadingRisk(pct, "line_loading_hard_pct", "line_loading_caution_pct", t);

/** The worst of several judgements. A null contributes nothing. */
export function worstRisk(...risks: (RiskLevel | null)[]): RiskLevel | null {
  const order: RiskLevel[] = ["SAFE", "CAUTION", "CONSTRAINED"];
  const present = risks.filter((r): r is RiskLevel => r != null);
  if (present.length === 0) return null;
  return present.reduce((worst, r) => (order.indexOf(r) > order.indexOf(worst) ? r : worst));
}

export function strokeFor(risk: RiskLevel | null): string {
  return risk ? RISK_COLOURS[risk].stroke : NEUTRAL;
}

export function fillFor(risk: RiskLevel | null): string {
  return risk ? RISK_COLOURS[risk].fill : "#0f172a";
}
