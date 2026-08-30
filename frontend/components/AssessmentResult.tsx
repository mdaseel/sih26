"use client";

import type { Assessment } from "@/lib/types";
import { ProbabilityBar, RiskBadge } from "@/components/RiskBadge";

/**
 * Renders one complete assessment.
 *
 * Every number displayed comes from the backend response. Nothing is derived,
 * rounded into a different meaning, or filled in when missing — a value the
 * server did not send is shown as "—".
 */

/**
 * Human labels for the model's inputs.
 *
 * The keys are the training-time feature names and must not be renamed —
 * enrich_features.py and the pickle agree on them. This is presentation only.
 */
const FEATURE_LABELS: Record<string, string> = {
  pv_bus: "Connection point",
  pv_bus_vn_kv: "Voltage level",
  existing_pv_kw: "Existing solar",
  new_pv_kw: "Requested solar",
  total_pv_kw: "Total solar after install",
  existing_load_at_bus_kw: "Connected load at bus",
  pv_penetration_ratio: "Solar vs local load",
  transformer_association: "Transformer",
  feeder_section: "Feeder section",
  transformer_sn_kva: "Transformer rating",
  pv_to_transformer_ratio: "Solar vs transformer",
  load_to_transformer_ratio: "Load vs transformer",
  base_voltage_pu: "Base voltage",
  feeder_distance_km: "Distance from source",
  upstream_r_ohm: "Upstream resistance",
  upstream_x_ohm: "Upstream reactance",
  upstream_z_ohm: "Upstream impedance",
  phase_configuration: "Phase configuration",
  voltage_level_label: "Voltage class",
};

const FEATURE_UNITS: Record<string, string> = {
  pv_bus_vn_kv: "kV",
  existing_pv_kw: "kW",
  new_pv_kw: "kW",
  total_pv_kw: "kW",
  existing_load_at_bus_kw: "kW",
  transformer_sn_kva: "kVA",
  base_voltage_pu: "pu",
  feeder_distance_km: "km",
  upstream_r_ohm: "Ω",
  upstream_x_ohm: "Ω",
  upstream_z_ohm: "Ω",
};

function formatFeature(value: number | string): string {
  if (typeof value === "string") return value;
  if (!Number.isFinite(value)) return "—";
  if (Number.isInteger(value)) return String(value);
  return Math.abs(value) < 0.01 ? value.toExponential(2) : value.toFixed(4);
}

/**
 * Probabilities as tree counts.
 *
 * The forest's output really is a vote — each tree returns a class and the
 * proportion is the probability — so showing "231 of 300 trees" is a
 * restatement of the same number, not a new claim. Rounded to whole trees,
 * because a fractional tree does not exist.
 */
function treeVote(probability: number, trees: number | null): string | null {
  if (!trees || !Number.isFinite(probability)) return null;
  return `${Math.round(probability * trees)} of ${trees}`;
}

function Metric({
  label,
  value,
  unit,
  hint,
  emphasis,
}: {
  label: string;
  value: number | string | boolean | null | undefined;
  unit?: string;
  hint?: string;
  emphasis?: "normal" | "warn" | "bad";
}) {
  const display =
    value === null || value === undefined
      ? "—"
      : typeof value === "boolean"
        ? value
          ? "Yes"
          : "No"
        : value;

  const tone =
    emphasis === "bad"
      ? "text-red-300"
      : emphasis === "warn"
        ? "text-yellow-300"
        : "text-slate-100";

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
      <div className="metric-label">{label}</div>
      <div className={`font-mono text-lg tabular-nums ${tone}`}>
        {display}
        {unit && display !== "—" ? (
          <span className="ml-1 text-xs text-slate-500">{unit}</span>
        ) : null}
      </div>
      {hint ? <div className="mt-1 text-[11px] text-slate-500">{hint}</div> : null}
    </div>
  );
}

export function AssessmentResult({ result }: { result: Assessment }) {
  const { ml, engineering, metrics } = result;
  const t = engineering.thresholds_snapshot;

  const riseExceeded = Math.abs(metrics.voltage_rise_pu) > (t.voltage_rise_hard_pu ?? 0.05);
  const riseWarn = Math.abs(metrics.voltage_rise_pu) >= (t.voltage_rise_caution_pu ?? 0.03);
  const trafoBad = metrics.max_transformer_loading_pct > (t.transformer_loading_hard_pct ?? 100);
  const trafoWarn = metrics.max_transformer_loading_pct >= (t.transformer_loading_caution_pct ?? 95);
  const lineBad = metrics.max_line_loading_pct > (t.line_loading_hard_pct ?? 100);
  const lineWarn = metrics.max_line_loading_pct >= (t.line_loading_caution_pct ?? 80);

  return (
    <div className="space-y-5">
      {/* ---- decision, stated once and compactly ---- */}
      {/*
        The order below puts the model first and the simulation after it,
        because that is the order they run in and it is the model a reader
        wants explained. It does not change which one governs: the power flow
        is the authority, and this header says so before anything else.
      */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-500">
              Final result — decided by the power-flow simulation
            </div>
            <div className="mt-2">
              <RiskBadge risk={engineering.engineering_risk} size="lg" />
            </div>
          </div>
          <div className="text-right text-xs text-slate-500">
            <div>{metrics.engine} {metrics.engine_version}</div>
            <div>{metrics.runtime_ms} ms</div>
          </div>
        </div>

        <p className="mt-4 rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-300">
          <span className="font-medium text-slate-400">
            {engineering.constraint_type === "none"
              ? "Result: "
              : `${engineering.constraint_type.replace(/_/g, " ")}: `}
          </span>
          {engineering.constraint_reason}
        </p>
      </div>

      {/* ---- how the model read it ---- */}
      <div className="card border-sky-900/50">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-slate-100">
              How the model read your request
            </h3>
            <p className="mt-0.5 text-xs text-slate-500">
              {ml.model_file} · {ml.feature_count} inputs
              {ml.tree_count ? ` · ${ml.tree_count} decision trees` : ""} · runs
              before the simulation
            </p>
          </div>
          <RiskBadge risk={ml.prediction} size="lg" />
        </div>

        {/* the vote */}
        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
              {ml.tree_count ? "How the trees voted" : "Model confidence"}
            </span>
            {ml.tree_count && (
              <span className="text-[11px] text-slate-600">
                each tree learned from a different slice of the training
                scenarios and classifies independently
              </span>
            )}
          </div>

          <div className="space-y-3">
            {(
              [
                ["SAFE", ml.safe_probability],
                ["CAUTION", ml.caution_probability],
                ["CONSTRAINED", ml.constrained_probability],
              ] as const
            ).map(([risk, probability]) => (
              <div key={risk}>
                <ProbabilityBar risk={risk} value={probability} />
                {treeVote(probability, ml.tree_count) && (
                  <div className="mt-0.5 text-right text-[11px] text-slate-600">
                    {treeVote(probability, ml.tree_count)} trees
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* what it was given */}
        {Object.keys(ml.features_used ?? {}).length > 0 && (
          <div className="mt-4">
            <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                What the model was given
              </span>
              <span className="text-[11px] text-slate-600">
                inputs only — no simulation result is among them
              </span>
            </div>
            <div className="scroll-pane grid max-h-72 gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(ml.features_used).map(([key, value]) => (
                <div
                  key={key}
                  className="rounded-lg border border-slate-800 bg-slate-950/40 px-3 py-2"
                >
                  <div className="text-[11px] text-slate-500">
                    {FEATURE_LABELS[key] ?? key.replace(/_/g, " ")}
                  </div>
                  <div className="font-mono text-sm tabular-nums text-slate-200">
                    {formatFeature(value)}
                    {FEATURE_UNITS[key] && (
                      <span className="ml-1 text-[11px] text-slate-500">
                        {FEATURE_UNITS[key]}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="mt-4 text-[11px] leading-relaxed text-slate-500">
          This is a prediction from the inputs above, made before any electrical
          calculation. It is advisory: it can be quick where a full simulation is
          slow, and it can be wrong. The power flow below is what decides.
        </p>

        {!result.ml_agrees_with_engineering && (
          <p className="mt-3 rounded-lg border border-amber-900 bg-amber-950/40 p-3 text-xs text-amber-200">
            The model predicted <strong>{ml.prediction}</strong> but the power
            flow determined <strong>{engineering.engineering_risk}</strong>. The
            power-flow result stands. Disagreement is recorded for engineering
            review rather than reconciled.
          </p>
        )}
      </div>

      {/* ---- the simulation, in brief ---- */}
      <details className="card" open={engineering.engineering_risk !== "SAFE"}>
        <summary className="cursor-pointer list-none">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">
                What the simulation measured
              </h3>
              <p className="mt-0.5 text-xs text-slate-500">
                Newton-Raphson power flow on {metrics.network_file} — the
                authority for the result above
              </p>
            </div>
            <span className="text-xs text-slate-500">show / hide</span>
          </div>
        </summary>

        <div className="mt-4 space-y-5">

      {/* ---- Voltage ---- */}
      <div className="card">
        <h3 className="mb-3 text-sm font-semibold text-slate-200">
          Voltage at the connection point
        </h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Metric
            label="Before (base)"
            value={metrics.base_voltage_pu.toFixed(4)}
            unit="pu"
          />
          <Metric
            label="After (with PV)"
            value={metrics.pv_voltage_pu.toFixed(4)}
            unit="pu"
          />
          <Metric
            label="Voltage rise"
            value={metrics.voltage_rise_pu.toFixed(5)}
            unit="pu"
            hint={`hard limit ${t.voltage_rise_hard_pu ?? 0.05}`}
            emphasis={riseExceeded ? "bad" : riseWarn ? "warn" : "normal"}
          />
          <Metric
            label="Solar penetration"
            value={metrics.solar_penetration_pct.toFixed(2)}
            unit="% of feeder load"
          />
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <Metric
            label="Feeder minimum voltage"
            value={metrics.feeder_min_voltage_pu.toFixed(4)}
            unit="pu"
            hint={`at bus ${metrics.min_voltage_bus} · limit ${t.voltage_hard_low_pu ?? 0.9}`}
          />
          <Metric
            label="Feeder maximum voltage"
            value={metrics.feeder_max_voltage_pu.toFixed(4)}
            unit="pu"
            hint={`at bus ${metrics.max_voltage_bus} · limit ${t.voltage_hard_high_pu ?? 1.05}`}
          />
        </div>
      </div>

      {/* ---- Loading and power ---- */}
      <div className="card">
        <h3 className="mb-3 text-sm font-semibold text-slate-200">
          Equipment loading and power flow
        </h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Metric
            label="Transformer loading"
            value={metrics.max_transformer_loading_pct.toFixed(2)}
            unit="%"
            hint={`${metrics.worst_transformer} · was ${metrics.base_max_transformer_loading_pct.toFixed(2)}%`}
            emphasis={trafoBad ? "bad" : trafoWarn ? "warn" : "normal"}
          />
          <Metric
            label="Line loading"
            value={metrics.max_line_loading_pct.toFixed(2)}
            unit="%"
            hint={`${metrics.worst_line} · was ${metrics.base_max_line_loading_pct.toFixed(2)}%`}
            emphasis={lineBad ? "bad" : lineWarn ? "warn" : "normal"}
          />
          <Metric
            label="Reverse power flow"
            value={metrics.reverse_power_flow}
            hint={metrics.reverse_reason !== "none" ? metrics.reverse_reason : undefined}
            emphasis={metrics.reverse_power_flow ? "warn" : "normal"}
          />
          <Metric
            label="Feeder losses"
            value={metrics.power_loss_kw.toFixed(2)}
            unit="kW"
            hint={`change ${metrics.delta_losses_kw >= 0 ? "+" : ""}${metrics.delta_losses_kw.toFixed(2)} kW`}
          />
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <Metric label="Existing solar" value={metrics.existing_pv_kw} unit="kW" />
          <Metric label="Requested solar" value={metrics.new_pv_kw} unit="kW" />
          <Metric label="Total solar" value={metrics.total_pv_kw} unit="kW" />
        </div>
        </div>
        </div>
      </details>

      <p className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
        {result.disclaimer} Grid model: {result.data_class}. Decision authority:{" "}
        {result.authority.replace("_", " ")}.
      </p>
    </div>
  );
}
