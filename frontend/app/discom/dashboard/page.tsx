"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { RiskBadge } from "@/components/RiskBadge";
import { ApiError, discomApi } from "@/lib/api";
import type { DiscomApplication, DiscomSummary } from "@/lib/types";

export default function DiscomDashboard() {
  const [summary, setSummary] = useState<DiscomSummary | null>(null);
  const [apps, setApps] = useState<DiscomApplication[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([discomApi.summary(), discomApi.applications()])
      .then(([s, a]) => {
        setSummary(s);
        setApps(a);
      })
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const queue = apps
    .filter((a) =>
      ["SUBMITTED", "ASSESSED", "UNDER_DISCOM_REVIEW", "ENGINEERING_REVIEW"].includes(a.status)
    )
    .slice(0, 8);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Network overview</h1>
        <p className="mt-1 text-sm text-slate-500">
          Connection requests and their effect on the distribution network
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {summary && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Total applications" value={summary.total_applications} />
            <Stat label="Pending review" value={summary.pending_review} accent="amber" />
            <Stat
              label="Approved capacity"
              value={summary.approved_solar_kw.toFixed(1)}
              unit="kW"
            />
            <Stat
              label="Pending capacity"
              value={summary.pending_solar_kw.toFixed(1)}
              unit="kW"
              accent="amber"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="SAFE" value={summary.by_risk.SAFE} accent="green" />
            <Stat label="CAUTION" value={summary.by_risk.CAUTION} accent="yellow" />
            <Stat label="CONSTRAINED" value={summary.by_risk.CONSTRAINED} accent="red" />
          </div>

          {summary.ml_engineering_disagreements > 0 && (
            <div className="rounded-lg border border-amber-900 bg-amber-950/30 p-4 text-sm text-amber-200">
              <b>{summary.ml_engineering_disagreements}</b> application
              {summary.ml_engineering_disagreements === 1 ? "" : "s"} where the ML
              pre-screen and the power flow disagree. The power-flow result stands;
              these are flagged for engineering attention, not reconciled.
            </div>
          )}

          <p className="text-xs text-slate-600">{summary.capacity_note}</p>
        </>
      )}

      <div className="card">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200">Awaiting decision</h2>
          <Link href="/discom/applications" className="text-xs text-sky-400 hover:underline">
            All applications →
          </Link>
        </div>

        {queue.length === 0 ? (
          <p className="text-sm text-slate-500">Nothing awaiting review.</p>
        ) : (
          <div className="space-y-2">
            {queue.map((a) => (
              <Link
                key={a.id}
                href={`/discom/applications/${a.id}`}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/40 px-4 py-3 transition hover:border-slate-700"
              >
                <div>
                  <div className="font-mono text-sm text-slate-200">
                    {a.application_number}
                  </div>
                  <div className="text-xs text-slate-500">
                    {a.applicant_name} · Bus {a.pv_bus} · {Number(a.new_pv_kw).toFixed(1)} kW
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {a.engineering_risk ? (
                    <RiskBadge risk={a.engineering_risk} size="sm" />
                  ) : (
                    <span className="text-xs text-slate-500">not assessed</span>
                  )}
                  <span className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-400">
                    {a.status.replace(/_/g, " ")}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {summary && (
        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-slate-200">Network model</h2>
          <div className="grid gap-3 text-sm sm:grid-cols-5">
            <Field label="Engine" value={`${summary.network.engine} ${summary.network.engine_version}`} />
            <Field label="Buses" value={summary.network.buses} />
            <Field label="Lines" value={summary.network.lines} />
            <Field label="Transformers" value={summary.network.transformers} />
            <Field label="Regulators" value={summary.network.regulator_handling} />
          </div>
          <p className="mt-3 text-xs text-slate-600">{summary.data_class}</p>
        </div>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  unit,
  accent,
}: {
  label: string;
  value: number | string;
  unit?: string;
  accent?: "green" | "yellow" | "red" | "amber";
}) {
  const tone =
    accent === "green"
      ? "text-green-300"
      : accent === "yellow"
        ? "text-yellow-300"
        : accent === "red"
          ? "text-red-300"
          : accent === "amber"
            ? "text-amber-300"
            : "text-slate-100";
  return (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className={`font-mono text-2xl tabular-nums ${tone}`}>
        {value}
        {unit && <span className="ml-1 text-xs text-slate-500">{unit}</span>}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <div className="metric-label">{label}</div>
      <div className="text-slate-300">{value}</div>
    </div>
  );
}
