"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { api, ApiError } from "@/lib/api";
import type { ApplicationStatus, SolarApplication } from "@/lib/types";

/**
 * The citizen's dashboard.
 *
 * No network-model card here. The feeder's bus and transformer counts are a
 * DISCOM concern and say nothing to a householder about their own request;
 * that card lives on the DISCOM dashboard, where someone is paid to care.
 *
 * The applications list is the substance of this page, so it gets the room —
 * and a fixed height, because a list that grows with every submission would
 * eventually push everything else off the screen.
 */

const AWAITING: ApplicationStatus[] = [
  "SUBMITTED",
  "ASSESSING",
  "ASSESSED",
  "UNDER_DISCOM_REVIEW",
  "ENGINEERING_REVIEW",
];

const DECIDED: ApplicationStatus[] = [
  "APPROVED",
  "VENDOR_SELECTED",
  "INSTALLING",
  "INSTALLED",
  "VERIFIED",
];

/** Colour by what the status means to the applicant, not by its name. */
function statusTone(status: ApplicationStatus): string {
  if (status === "REJECTED" || status === "CANCELLED")
    return "border-red-900 bg-red-950/40 text-red-300";
  if (status === "VERIFIED") return "border-green-900 bg-green-950/40 text-green-300";
  if (DECIDED.includes(status)) return "border-sky-900 bg-sky-950/40 text-sky-300";
  return "border-slate-700 bg-slate-900/60 text-slate-400";
}

function friendlyStatus(status: ApplicationStatus): string {
  switch (status) {
    case "SUBMITTED":
      return "In progress";
    case "ASSESSING":
      return "Grid check running";
    case "ASSESSED":
    case "UNDER_DISCOM_REVIEW":
    case "ENGINEERING_REVIEW":
      return "With the DISCOM";
    default:
      return status.replace(/_/g, " ").toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
  }
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? "—"
    : d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

export default function DashboardPage() {
  const [apps, setApps] = useState<SolarApplication[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listApplications()
      .then(setApps)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const stats = useMemo(() => {
    if (!apps) return null;
    return {
      total: apps.length,
      awaiting: apps.filter((a) => AWAITING.includes(a.status)).length,
      approved: apps.filter((a) => DECIDED.includes(a.status)).length,
      requestedKw: apps.reduce((s, a) => s + Number(a.new_pv_kw), 0),
    };
  }, [apps]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">
            Your rooftop solar connection requests
          </p>
        </div>
        <Link href="/citizen/applications/new" className="btn-primary">
          New application
        </Link>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="metric-label">Applications</div>
          <div className="metric-value">{stats?.total ?? "—"}</div>
        </div>
        <div className="card">
          <div className="metric-label">Awaiting a decision</div>
          <div className="metric-value">{stats?.awaiting ?? "—"}</div>
        </div>
        <div className="card">
          <div className="metric-label">Approved</div>
          <div className="metric-value">{stats?.approved ?? "—"}</div>
        </div>
        <div className="card">
          <div className="metric-label">Total capacity requested</div>
          <div className="metric-value">
            {stats ? stats.requestedKw.toFixed(1) : "—"}
            <span className="ml-1 text-xs text-slate-500">kW</span>
          </div>
        </div>
      </div>

      {/* ---- recent applications ---- */}
      <div className="card">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Recent applications</h2>
            <p className="mt-0.5 text-xs text-slate-500">
              {apps?.length
                ? `${apps.length} ${apps.length === 1 ? "application" : "applications"}, newest first`
                : "Everything you have submitted"}
            </p>
          </div>
          {apps && apps.length > 0 && (
            <Link
              href="/citizen/applications"
              className="text-xs text-sky-400 hover:underline"
            >
              View all →
            </Link>
          )}
        </div>

        {apps === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

        {apps?.length === 0 && (
          <div className="rounded-lg border border-dashed border-slate-800 py-10 text-center">
            <p className="text-sm text-slate-400">No applications yet.</p>
            <Link href="/citizen/applications/new" className="btn-primary mt-4">
              Start your first application
            </Link>
          </div>
        )}

        {apps && apps.length > 0 && (
          <div className="scroll-pane max-h-[30rem] space-y-3">
            {apps.map((a) => (
              <Link
                key={a.id}
                href={`/citizen/applications/${a.id}`}
                className="block rounded-lg border border-slate-800 bg-slate-950/40 p-4 transition hover:border-slate-700 hover:bg-slate-900/50"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="font-mono text-sm text-slate-200">
                      {a.application_number}
                    </div>
                    <div className="mt-0.5 truncate text-xs text-slate-500">
                      {[a.address_line, a.district, a.state].filter(Boolean).join(", ") ||
                        "No address on file"}
                    </div>
                  </div>
                  <span
                    className={`shrink-0 rounded border px-2 py-0.5 text-xs ${statusTone(a.status)}`}
                  >
                    {friendlyStatus(a.status)}
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <div>
                    <div className="metric-label">Requested</div>
                    <div className="font-mono text-sm tabular-nums text-slate-200">
                      {Number(a.new_pv_kw).toFixed(1)} kW
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Existing</div>
                    <div className="font-mono text-sm tabular-nums text-slate-400">
                      {Number(a.existing_pv_kw).toFixed(1)} kW
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Total after install</div>
                    <div className="font-mono text-sm tabular-nums text-slate-400">
                      {Number(a.total_pv_kw).toFixed(1)} kW
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Submitted</div>
                    <div className="text-sm text-slate-400">{formatDate(a.created_at)}</div>
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
                  <span>Connection point: Bus {a.pv_bus}</span>
                  {a.roof_type && <span>Roof: {a.roof_type}</span>}
                  {a.roof_area_sqm != null && <span>{a.roof_area_sqm} m²</span>}
                  {a.monthly_consumption_kwh != null && (
                    <span>{a.monthly_consumption_kwh} kWh/month</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
