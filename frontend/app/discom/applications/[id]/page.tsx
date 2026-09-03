"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { ProbabilityBar, RiskBadge } from "@/components/RiskBadge";
import { DigitalTwinView } from "@/components/twin/DigitalTwinView";
import { api, ApiError, discomApi } from "@/lib/api";
import type { DiscomApplicationDetail, TwinResponse } from "@/lib/types";

/**
 * DISCOM review console for one application.
 *
 * The order on this page follows the review the product describes: who is
 * asking, what the grid does about it, what the model thought, what the power
 * flow measured, and only then the decision controls.
 */
export default function DiscomApplicationReview() {
  const { id } = useParams<{ id: string }>();

  const [detail, setDetail] = useState<DiscomApplicationDetail | null>(null);
  const [twin, setTwin] = useState<TwinResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const d = await discomApi.application(id);
      setDetail(d);
      setNotes(d.application.review_notes ?? "");
      api
        .twin({
          pv_bus: d.application.pv_bus,
          existing_pv_kw: Number(d.application.existing_pv_kw),
          new_pv_kw: Number(d.application.new_pv_kw),
        })
        .then(setTwin)
        .catch(() => setTwin(null));
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function decide(decision: string) {
    setBusy(true);
    setError(null);
    setOutcome(null);
    try {
      const res = await discomApi.decide(id, decision, notes || undefined);
      setOutcome(res.note);
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusy(false);
    }
  }

  if (error && !detail) {
    return (
      <div className="space-y-4">
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
        <Link href="/discom/applications" className="btn-ghost">
          Back to applications
        </Link>
      </div>
    );
  }

  if (!detail) return <p className="text-sm text-slate-500">Loading…</p>;

  const { application: a, assessment, simulation, history, bus } = detail;
  const decided = ["APPROVED", "REJECTED", "CANCELLED"].includes(a.status);
  const constrained = assessment?.engineering_risk === "CONSTRAINED";
  const num = (v: unknown, d = 2) =>
    v === null || v === undefined ? "—" : Number(v).toFixed(d);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link
            href="/discom/applications"
            className="text-xs text-slate-500 hover:text-slate-300"
          >
            ← All applications
          </Link>
          <h1 className="mt-1 font-mono text-xl font-semibold text-slate-100">
            {a.application_number}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {a.applicant_name} · Bus {a.pv_bus} · {Number(a.new_pv_kw).toFixed(1)} kW requested
          </p>
        </div>
        <div className="flex items-center gap-3">
          {assessment && <RiskBadge risk={assessment.engineering_risk} />}
          <span className="rounded border border-slate-700 px-2.5 py-1 text-xs text-slate-400">
            {a.status.replace(/_/g, " ")}
          </span>
        </div>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
      {outcome && (
        <p className="rounded-lg border border-sky-900 bg-sky-950/40 p-3 text-sm text-sky-200">
          {outcome}
        </p>
      )}

      {/* ---- applicant ---- */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Applicant</h2>
        <div className="grid gap-3 text-sm sm:grid-cols-4">
          <Field label="Name" value={a.applicant_name} />
          <Field label="Phone" value={a.contact_phone} />
          <Field label="Consumer number" value={a.consumer_number} />
          <Field label="Connection type" value={a.connection_type} />
          <Field label="Address" value={a.address_line} />
          <Field label="District" value={a.district} />
          <Field label="Sanctioned load" value={a.sanctioned_load_kw ? `${a.sanctioned_load_kw} kW` : null} />
          <Field
            label="Monthly consumption"
            value={a.monthly_consumption_kwh ? `${a.monthly_consumption_kwh} kWh` : null}
          />
        </div>
      </div>

      {/* ---- Digital Twin grid impact ---- */}
      {twin && (
        <DigitalTwinView
          twin={twin}
          busId={a?.pv_bus}
          title="Grid Connection Digital Twin"
          subtitle="Review applicant grid impact in 3D aerial distribution twin or 2D schematic"
        />
      )}

      {/* ---- ML vs engineering ---- */}
      {assessment && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="card">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-slate-200">ML pre-screening</h2>
                <p className="text-xs text-slate-500">
                  {assessment.model_file} · {assessment.feature_count} features
                </p>
              </div>
              <RiskBadge risk={assessment.ml_prediction} size="sm" />
            </div>
            <div className="space-y-2">
              <ProbabilityBar risk="SAFE" value={Number(assessment.safe_probability)} />
              <ProbabilityBar risk="CAUTION" value={Number(assessment.caution_probability)} />
              <ProbabilityBar
                risk="CONSTRAINED"
                value={Number(assessment.constrained_probability)}
              />
            </div>
          </div>

          <div className="card">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-slate-200">
                  Power-flow verification
                </h2>
                <p className="text-xs text-slate-500">deterministic · decides the outcome</p>
              </div>
              <RiskBadge risk={assessment.engineering_risk} size="sm" />
            </div>
            <p className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-300">
              {assessment.constraint_reason}
            </p>
            {assessment.ml_agrees_with_engineering === false && (
              <p className="mt-3 rounded-lg border border-amber-900 bg-amber-950/40 p-2.5 text-xs text-amber-200">
                The model and the power flow disagree. The power-flow result stands.
              </p>
            )}
          </div>
        </div>
      )}

      {/* ---- electrical metrics ---- */}
      {simulation && (
        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-slate-200">Electrical metrics</h2>
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-4">
            <Metric label="Voltage before" value={num(simulation.base_voltage_pu, 4)} unit="pu" />
            <Metric label="Voltage after" value={num(simulation.pv_voltage_pu, 4)} unit="pu" />
            <Metric label="Voltage rise" value={num(simulation.voltage_rise_pu, 5)} unit="pu" />
            <Metric
              label="Feeder min / max"
              value={`${num(simulation.feeder_min_voltage_pu, 4)} / ${num(simulation.feeder_max_voltage_pu, 4)}`}
              unit="pu"
            />
            <Metric
              label="Transformer loading"
              value={num(simulation.max_transformer_loading_pct)}
              unit="%"
            />
            <Metric label="Line loading" value={num(simulation.max_line_loading_pct)} unit="%" />
            <Metric
              label="Reverse power flow"
              value={simulation.reverse_power_flow ? "Yes" : "No"}
              unit=""
            />
            <Metric label="Losses" value={num(simulation.power_loss_kw)} unit="kW" />
          </div>
          {bus && (
            <div className="mt-3 grid gap-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-xs sm:grid-cols-4">
              <Field label="Transformer" value={`${bus.transformer_association} · ${bus.transformer_sn_kva} kVA`} />
              <Field label="Feeder section" value={bus.feeder_section} />
              <Field label="Distance from source" value={`${bus.feeder_distance_km.toFixed(2)} km`} />
              <Field label="Upstream impedance" value={`${bus.upstream_z_ohm.toFixed(2)} Ω`} />
            </div>
          )}
        </div>
      )}

      {/* ---- decision ---- */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Decision</h2>

        {decided ? (
          <p className="text-sm text-slate-400">
            This application is <b>{a.status.replace(/_/g, " ")}</b>
            {a.reviewed_at ? ` · reviewed ${new Date(a.reviewed_at).toLocaleString()}` : ""}
            {a.review_notes ? ` · "${a.review_notes}"` : ""}
          </p>
        ) : (
          <>
            <label className="label">Review notes</label>
            <textarea
              className="input min-h-[70px]"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Reason for the decision, conditions, or what engineering should examine…"
            />

            {constrained && (
              <p className="mt-3 rounded-lg border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">
                The power flow found a hard violation:{" "}
                <b>{assessment?.constraint_reason}</b>. Approving anyway is recorded
                in the audit log as an override of an engineering objection.
              </p>
            )}

            <div className="mt-4 flex flex-wrap gap-2">
              <button
                onClick={() => decide("APPROVED")}
                disabled={busy || !assessment}
                className="btn-primary"
              >
                {constrained ? "Approve despite objection" : "Approve"}
              </button>
              <button
                onClick={() => decide("ENGINEERING_REVIEW")}
                disabled={busy}
                className="btn-ghost"
              >
                Request engineering review
              </button>
              <button
                onClick={() => decide("REJECTED")}
                disabled={busy}
                className="btn-ghost !border-red-900 !text-red-300"
              >
                Reject
              </button>
            </div>

            {!assessment && (
              <p className="mt-3 text-xs text-amber-300">
                Approval is blocked until the application has been assessed.
              </p>
            )}
          </>
        )}
      </div>

      {/* ---- history ---- */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Status history</h2>
        <div className="space-y-1.5 text-xs">
          {history.map((h) => (
            <div key={h.id} className="flex flex-wrap items-center gap-2 text-slate-400">
              <span className="font-mono text-slate-600">
                {new Date(h.created_at).toLocaleString()}
              </span>
              <span>
                {h.from_status ? `${h.from_status.replace(/_/g, " ")} → ` : ""}
                <b className="text-slate-300">{h.to_status.replace(/_/g, " ")}</b>
              </span>
              {h.note && <span className="text-slate-600">· {h.note}</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div>
      <div className="metric-label">{label}</div>
      <div className="text-slate-300">{value ?? "—"}</div>
    </div>
  );
}

function Metric({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
      <div className="metric-label">{label}</div>
      <div className="font-mono text-lg tabular-nums text-slate-100">
        {value}
        {unit && <span className="ml-1 text-xs text-slate-500">{unit}</span>}
      </div>
    </div>
  );
}
