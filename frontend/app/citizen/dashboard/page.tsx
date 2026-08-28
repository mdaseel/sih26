"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { RiskBadge } from "@/components/RiskBadge";
import { api, ApiError } from "@/lib/api";
import type { GridSummary, SolarApplication } from "@/lib/types";

export default function DashboardPage() {
  const [apps, setApps] = useState<SolarApplication[] | null>(null);
  const [grid, setGrid] = useState<GridSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.listApplications(), api.gridSummary()])
      .then(([a, g]) => {
        setApps(a);
        setGrid(g);
      })
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const totalRequested = apps?.reduce((s, a) => s + Number(a.new_pv_kw), 0) ?? 0;
  const assessed = apps?.filter((a) => a.status !== "DRAFT" && a.status !== "SUBMITTED").length ?? 0;

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

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card">
          <div className="metric-label">Applications</div>
          <div className="metric-value">{apps?.length ?? "—"}</div>
        </div>
        <div className="card">
          <div className="metric-label">Assessed</div>
          <div className="metric-value">{apps ? assessed : "—"}</div>
        </div>
        <div className="card">
          <div className="metric-label">Total capacity requested</div>
          <div className="metric-value">
            {apps ? totalRequested.toFixed(1) : "—"}
            <span className="ml-1 text-xs text-slate-500">kW</span>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Recent applications
        </h2>

        {apps === null && !error && (
          <p className="text-sm text-slate-500">Loading…</p>
        )}

        {apps?.length === 0 && (
          <p className="text-sm text-slate-500">
            No applications yet.{" "}
            <Link
              href="/citizen/applications/new"
              className="text-sky-400 hover:underline"
            >
              Start one
            </Link>
            .
          </p>
        )}

        <div className="space-y-2">
          {apps?.slice(0, 5).map((a) => (
            <Link
              key={a.id}
              href={`/citizen/applications/${a.id}`}
              className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/40 px-4 py-3 transition hover:border-slate-700"
            >
              <div>
                <div className="font-mono text-sm text-slate-200">
                  {a.application_number}
                </div>
                <div className="text-xs text-slate-500">
                  Bus {a.pv_bus} · {a.new_pv_kw} kW requested
                </div>
              </div>
              <span className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-400">
                {a.status.replace(/_/g, " ")}
              </span>
            </Link>
          ))}
        </div>
      </div>

      {grid && (
        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-slate-200">
            Network model
          </h2>
          <div className="grid gap-3 text-sm sm:grid-cols-4">
            <div>
              <div className="metric-label">Feeder</div>
              <div className="text-slate-300">{grid.feeder_id}</div>
            </div>
            <div>
              <div className="metric-label">Buses</div>
              <div className="text-slate-300">{grid.network.buses}</div>
            </div>
            <div>
              <div className="metric-label">Transformers</div>
              <div className="text-slate-300">{grid.network.transformers}</div>
            </div>
            <div>
              <div className="metric-label">Connection points</div>
              <div className="text-slate-300">{grid.eligible_bus_count}</div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-600">{grid.provenance}</p>
        </div>
      )}
    </div>
  );
}
