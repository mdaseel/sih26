"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { ApplicationTracker } from "@/components/ApplicationTracker";
import { AssessmentResult } from "@/components/AssessmentResult";
import { TwinDiagram } from "@/components/TwinDiagram";
import { api, ApiError } from "@/lib/api";
import type {
  ApplicationStatus,
  Assessment,
  SolarApplication,
  TwinResponse,
} from "@/lib/types";

/**
 * One application, in two acts.
 *
 * Before the DISCOM has decided, this page shows what the applicant submitted
 * and where the request has got to — nothing else. The engineering result
 * exists by then, but showing a citizen a SAFE verdict while their application
 * is still under review invites them to read it as an approval, and it is not
 * one. The DISCOM decides; the simulation only advises.
 *
 * Once a decision is recorded, the full evidence opens up: the digital twin,
 * the constraint that governed, the ML and power-flow results. At that point
 * it explains a decision that has already been made, which is the honest use
 * for it.
 */

/** A decision has been recorded, or the case has moved past needing one. */
const DECIDED: ApplicationStatus[] = [
  "APPROVED",
  "REJECTED",
  "VENDOR_SELECTED",
  "INSTALLING",
  "INSTALLED",
  "VERIFIED",
];

function statusTone(status: ApplicationStatus): string {
  if (status === "REJECTED" || status === "CANCELLED")
    return "border-red-900 bg-red-950/40 text-red-300";
  if (status === "VERIFIED") return "border-green-900 bg-green-950/40 text-green-300";
  if (DECIDED.includes(status)) return "border-sky-900 bg-sky-950/40 text-sky-300";
  return "border-slate-700 bg-slate-900/60 text-slate-400";
}

function Field({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <div className="metric-label">{label}</div>
      <div className="mt-0.5 break-words text-sm text-slate-300">{value || "—"}</div>
    </div>
  );
}

export default function ApplicationDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [app, setApp] = useState<SolarApplication | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [twin, setTwin] = useState<TwinResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const load = useCallback(async () => {
    try {
      const { application } = await api.getApplication(id);
      setApp(application);
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const decided = app ? DECIDED.includes(app.status) : false;

  /**
   * Loads the assessment already on record. Viewing a page must never create
   * a new simulation — that would spend CPU re-deriving a result the database
   * already holds, and would fill the audit trail with rows nobody asked for.
   */
  const loadAssessment = useCallback(async () => {
    try {
      setAssessment(await api.storedAssessment(id));
    } catch (e) {
      // 404 simply means it has not been assessed yet.
      if ((e as ApiError).status !== 404) setError((e as ApiError).message);
    }
  }, [id]);

  /** Explicit user action: run the pipeline again and record a new result. */
  const runAssessment = useCallback(async () => {
    setError(null);
    setRunning(true);
    try {
      const result = await api.assessApplication(id);
      setAssessment(result);
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setRunning(false);
    }
  }, [id, load]);

  // Only fetched once there is a decision to explain — see the page docstring.
  useEffect(() => {
    if (decided) loadAssessment();
  }, [decided, loadAssessment]);

  // The twin needs per-element detail, which is not stored on the application
  // row. It is derived from the same pipeline but persists nothing.
  useEffect(() => {
    if (!app || !decided) return;
    api
      .twin({
        pv_bus: app.pv_bus,
        existing_pv_kw: Number(app.existing_pv_kw),
        new_pv_kw: Number(app.new_pv_kw),
      })
      .then(setTwin)
      .catch(() => setTwin(null));
  }, [app, decided]);

  if (error && !app) {
    return (
      <div className="space-y-4">
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
        <Link href="/citizen/applications" className="btn-ghost">
          Back to applications
        </Link>
      </div>
    );
  }

  if (!app) return <p className="text-sm text-slate-500">Loading…</p>;

  const address =
    [app.address_line, app.district, app.state, app.pincode].filter(Boolean).join(", ") ||
    null;
  const coordinates =
    app.latitude != null && app.longitude != null
      ? `${Number(app.latitude).toFixed(5)}, ${Number(app.longitude).toFixed(5)}`
      : null;

  return (
    <div className="space-y-6">
      {/* ---- header ---- */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link
            href="/citizen/applications"
            className="text-xs text-slate-500 hover:text-slate-300"
          >
            ← All applications
          </Link>
          <h1 className="mt-1 font-mono text-xl font-semibold text-slate-100">
            {app.application_number}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {app.applicant_name} · submitted{" "}
            {new Date(app.created_at).toLocaleDateString(undefined, {
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`rounded border px-2.5 py-1 text-xs ${statusTone(app.status)}`}>
            {app.status.replace(/_/g, " ")}
          </span>
          {decided && (
            <button onClick={runAssessment} disabled={running} className="btn-ghost">
              {running ? "Running…" : "Re-run assessment"}
            </button>
          )}
        </div>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {/* ---- tracking, expanded ---- */}
      <div className="card">
        <h2 className="mb-4 text-sm font-semibold text-slate-200">Progress</h2>
        <ApplicationTracker applicationId={id} status={app.status} />
      </div>

      {/* ---- what was submitted ---- */}
      <div className="card space-y-5">
        <h2 className="text-sm font-semibold text-slate-200">Your application</h2>

        <div>
          <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">
            Applicant
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Application ID" value={app.application_number} />
            <Field label="Full name" value={app.applicant_name} />
            <Field label="Phone" value={app.contact_phone} />
            <Field label="Consumer number" value={app.consumer_number} />
            <Field label="Connection type" value={app.connection_type} />
            <Field
              label="Monthly consumption"
              value={
                app.monthly_consumption_kwh != null
                  ? `${app.monthly_consumption_kwh} kWh`
                  : null
              }
            />
          </div>
        </div>

        <div className="border-t border-slate-800 pt-4">
          <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">Site</div>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="sm:col-span-2">
              <Field label="Address" value={address} />
            </div>
            <Field label="Coordinates" value={coordinates} />
            <Field label="Roof type" value={app.roof_type} />
            <Field
              label="Roof area"
              value={app.roof_area_sqm != null ? `${app.roof_area_sqm} m²` : null}
            />
            <Field label="Shading" value={app.shading_level} />
          </div>
        </div>

        <div className="border-t border-slate-800 pt-4">
          <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">
            Solar capacity
          </div>
          <div className="grid gap-4 sm:grid-cols-4">
            <div>
              <div className="metric-label">Existing solar</div>
              <div className="metric-value">
                {Number(app.existing_pv_kw).toFixed(1)}
                <span className="ml-1 text-xs text-slate-500">kW</span>
              </div>
            </div>
            <div>
              <div className="metric-label">Requested</div>
              <div className="metric-value">
                {Number(app.new_pv_kw).toFixed(1)}
                <span className="ml-1 text-xs text-slate-500">kW</span>
              </div>
            </div>
            <div>
              <div className="metric-label">Total after install</div>
              <div className="metric-value">
                {Number(app.total_pv_kw).toFixed(1)}
                <span className="ml-1 text-xs text-slate-500">kW</span>
              </div>
            </div>
            <div>
              <div className="metric-label">Connection point</div>
              <div className="metric-value">Bus {app.pv_bus}</div>
            </div>
          </div>
          {app.sanctioned_load_kw != null && (
            <p className="mt-3 text-xs text-slate-600">
              Connected load at this connection point:{" "}
              <span className="font-mono tabular-nums text-slate-500">
                {Number(app.sanctioned_load_kw).toFixed(2)} kW
              </span>{" "}
              — taken from the network model by the system, not something you were
              asked to supply. The DISCOM&apos;s own sanctioned figure takes precedence.
            </p>
          )}
        </div>
      </div>

      {/* ---- before a decision: say what happens next, show nothing more ---- */}
      {!decided && (
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-200">What happens next</h2>
          <p className="mt-2 text-sm text-slate-400">
            Your application has been screened against the local distribution network and
            is now with the DISCOM. A reviewer there decides whether the connection is
            approved.
          </p>
          <p className="mt-3 text-xs text-slate-600">
            The technical assessment — the network simulation, the constraint that
            governed it, and the digital twin of your connection — is released here once
            the DISCOM records its decision. Until then it is under review, and a
            screening result is not an approval.
          </p>
        </div>
      )}

      {/* ---- after a decision: the full evidence ---- */}
      {decided && (
        <>
          {running && !assessment && (
            <div className="card text-sm text-slate-400">
              Running ML pre-screen and power-flow simulation…
            </div>
          )}

          {twin && <TwinDiagram twin={twin} />}

          {assessment && <AssessmentResult result={assessment} />}

          {!assessment && !running && (
            <div className="card text-sm text-slate-400">
              No assessment is on record for this application.{" "}
              <button onClick={runAssessment} className="text-sky-400 hover:underline">
                Run it now
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
