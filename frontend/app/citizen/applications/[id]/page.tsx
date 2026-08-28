"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { AssessmentResult } from "@/components/AssessmentResult";
import { TwinDiagram } from "@/components/TwinDiagram";
import { api, ApiError } from "@/lib/api";
import type { Assessment, SolarApplication, TwinResponse } from "@/lib/types";

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

  useEffect(() => {
    loadAssessment();
  }, [loadAssessment]);

  // The twin needs per-element detail, which is not stored on the application
  // row. It is derived from the same pipeline but persists nothing.
  useEffect(() => {
    if (!app) return;
    api
      .twin({
        pv_bus: app.pv_bus,
        existing_pv_kw: Number(app.existing_pv_kw),
        new_pv_kw: Number(app.new_pv_kw),
      })
      .then(setTwin)
      .catch(() => setTwin(null));
  }, [app]);

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

  return (
    <div className="space-y-6">
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
            {app.applicant_name} · Bus {app.pv_bus}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="rounded border border-slate-700 px-2.5 py-1 text-xs text-slate-400">
            {app.status.replace(/_/g, " ")}
          </span>
          <button
            onClick={runAssessment}
            disabled={running}
            className="btn-ghost"
          >
            {running ? "Running…" : "Re-run assessment"}
          </button>
        </div>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Request</h2>
        <div className="grid gap-3 sm:grid-cols-4">
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
      </div>

      {running && !assessment && (
        <div className="card text-sm text-slate-400">
          Running ML pre-screen and power-flow simulation…
        </div>
      )}

      {twin && <TwinDiagram twin={twin} />}

      {assessment && <AssessmentResult result={assessment} />}

      {!assessment && !running && (
        <div className="card text-sm text-slate-400">
          No assessment yet.{" "}
          <button onClick={runAssessment} className="text-sky-400 hover:underline">
            Run it now
          </button>
        </div>
      )}
    </div>
  );
}
