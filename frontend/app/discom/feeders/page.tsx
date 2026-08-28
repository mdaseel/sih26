"use client";

import { useEffect, useState } from "react";

import { ApiError, discomApi } from "@/lib/api";
import type { FeederRow } from "@/lib/types";

export default function DiscomFeeders() {
  const [rows, setRows] = useState<FeederRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    discomApi
      .feeders()
      .then(setRows)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Feeder sections</h1>
        <p className="mt-1 text-sm text-slate-500">
          Capacity requested against each section of the feeder.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
      {rows === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {rows && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Section</th>
                <th className="px-4 py-3 text-right">Points</th>
                <th className="px-4 py-3 text-right">Load</th>
                <th className="px-4 py-3 text-right">Applications</th>
                <th className="px-4 py-3 text-right">Pending PV</th>
                <th className="px-4 py-3 text-right">Approved PV</th>
                <th className="px-4 py-3 text-right">Tightest bus</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.feeder_section}
                  className="border-b border-slate-900 last:border-0 hover:bg-slate-900/40"
                >
                  <td className="px-4 py-3 font-mono text-slate-200">{r.feeder_section}</td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-400">
                    {r.connection_points}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                    {r.total_load_kw.toFixed(1)} kW
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-400">
                    {r.applications}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-amber-300">
                    {r.pending_pv_kw > 0 ? r.pending_pv_kw.toFixed(1) + " kW" : "—"}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-300">
                    {r.approved_pv_kw > 0 ? r.approved_pv_kw.toFixed(1) + " kW" : "—"}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-300">
                    {r.min_hosting_capacity_kw == null
                      ? "—"
                      : r.min_hosting_capacity_kw.toFixed(0) + " kW"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {rows?.[0] && (
        <p className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
          {rows[0].capacity_note}
        </p>
      )}
    </div>
  );
}
