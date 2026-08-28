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
      {/* ---- Final verdict ---- */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-500">
              Engineering assessment — power-flow verified
            </div>
            <div className="mt-2">
              <RiskBadge risk={engineering.engineering_risk} size="lg" />
            </div>
          </div>
          <div className="text-right text-xs text-slate-500">
            <div>{metrics.engine} {metrics.engine_version}</div>
            <div>{metrics.network_file}</div>
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

      {/* ---- ML pre-screen ---- */}
      <div className="card">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              ML pre-screening
            </h3>
            <p className="text-xs text-slate-500">
              {ml.model_file} · {ml.feature_count} features · advisory only
            </p>
          </div>
          <RiskBadge risk={ml.prediction} size="sm" />
        </div>

        <div className="space-y-2">
          <ProbabilityBar risk="SAFE" value={ml.safe_probability} />
          <ProbabilityBar risk="CAUTION" value={ml.caution_probability} />
          <ProbabilityBar risk="CONSTRAINED" value={ml.constrained_probability} />
        </div>

        {!result.ml_agrees_with_engineering && (
          <p className="mt-4 rounded-lg border border-amber-900 bg-amber-950/40 p-3 text-xs text-amber-200">
            The model predicted <strong>{ml.prediction}</strong> but the power
            flow determined <strong>{engineering.engineering_risk}</strong>. The
            power-flow result stands. Disagreement is recorded for engineering
            review rather than reconciled.
          </p>
        )}
      </div>

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

      <p className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
        {result.disclaimer} Grid model: {result.data_class}. Decision authority:{" "}
        {result.authority.replace("_", " ")}.
      </p>
    </div>
  );
}
