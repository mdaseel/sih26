"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ApplicationTracker } from "@/components/ApplicationTracker";
import { api, ApiError } from "@/lib/api";
import type { ApplicationStatus, SolarApplication } from "@/lib/types";

/**
 * Every application the citizen has submitted.
 *
 * Each row can expand into a live tracker rather than navigating away, because
 * "where has it got to?" is the question this page is usually opened to answer,
 * and making someone lose their place to find out is a poor trade. Only the
 * open tracker polls — see ApplicationTracker.
 */

const DECIDED: ApplicationStatus[] = [
  "APPROVED",
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

export default function ApplicationsPage() {
  const [apps, setApps] = useState<SolarApplication[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tracking, setTracking] = useState<string | null>(null);

  useEffect(() => {
    api
      .listApplications()
      .then(setApps)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">My applications</h1>
          <p className="mt-1 text-sm text-slate-500">
            Every request you have submitted
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

      {apps === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {apps?.length === 0 && (
        <div className="card text-center">
          <p className="text-sm text-slate-400">You have no applications yet.</p>
          <Link href="/citizen/applications/new" className="btn-primary mt-4">
            Create your first application
          </Link>
        </div>
      )}

      {apps && apps.length > 0 && (
        <div className="scroll-pane max-h-[46rem] space-y-4">
          {apps.map((a) => {
            const open = tracking === a.id;
            return (
              <div key={a.id} className="card">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-sm text-slate-200">
                        {a.application_number}
                      </span>
                      <span
                        className={`rounded border px-2 py-0.5 text-xs ${statusTone(a.status)}`}
                      >
                        {friendlyStatus(a.status)}
                      </span>
                    </div>
                    <div className="mt-1 truncate text-xs text-slate-500">
                      {[a.address_line, a.district, a.state, a.pincode]
                        .filter(Boolean)
                        .join(", ") || "No address on file"}
                    </div>
                  </div>

                  <div className="flex shrink-0 items-center gap-2">
                    <button
                      onClick={() => setTracking(open ? null : a.id)}
                      aria-expanded={open}
                      className={`btn !px-3 !py-1.5 !text-xs ${
                        open
                          ? "border border-sky-600 bg-sky-950/60 text-sky-300"
                          : "border border-slate-700 text-slate-300 hover:bg-slate-800"
                      }`}
                    >
                      {open ? "Hide tracking" : "Track"}
                    </button>
                    <Link
                      href={`/citizen/applications/${a.id}`}
                      className="btn-ghost !px-3 !py-1.5 !text-xs"
                    >
                      View
                    </Link>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-5">
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
                    <div className="metric-label">Total</div>
                    <div className="font-mono text-sm tabular-nums text-slate-400">
                      {Number(a.total_pv_kw).toFixed(1)} kW
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Connection point</div>
                    <div className="text-sm text-slate-400">Bus {a.pv_bus}</div>
                  </div>
                  <div>
                    <div className="metric-label">Submitted</div>
                    <div className="text-sm text-slate-400">{formatDate(a.created_at)}</div>
                  </div>
                </div>

                {open && (
                  <div className="mt-5 border-t border-slate-800 pt-5">
                    <ApplicationTracker applicationId={a.id} status={a.status} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
