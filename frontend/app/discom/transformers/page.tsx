"use client";

import { useEffect, useState } from "react";

import { ApiError, discomApi } from "@/lib/api";
import type { TransformerRow } from "@/lib/types";

const TONE = {
  SAFE: "text-green-300",
  CAUTION: "text-yellow-300",
  CONSTRAINED: "text-red-300",
} as const;

export default function DiscomTransformers() {
  const [rows, setRows] = useState<TransformerRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    discomApi
      .transformers()
      .then(setRows)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Transformers</h1>
        <p className="mt-1 text-sm text-slate-500">
          Loading measured by a base power flow, ordered by how loaded each one
          already is.
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
                <th className="px-4 py-3">Transformer</th>
                <th className="px-4 py-3 text-right">Rating</th>
                <th className="px-4 py-3 text-right">Base loading</th>
                <th className="px-4 py-3 text-right">Load</th>
                <th className="px-4 py-3 text-right">Points</th>
                <th className="px-4 py-3 text-right">Tightest capacity</th>
                <th className="px-4 py-3 text-right">Pending PV</th>
                <th className="px-4 py-3 text-right">Approved PV</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.name}
                  className="border-b border-slate-900 last:border-0 hover:bg-slate-900/40"
                >
                  <td className="px-4 py-3 font-mono text-slate-200">{r.name}</td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                    {r.sn_kva == null ? "—" : r.sn_kva.toFixed(0) + " kVA"}
                  </td>
                  <td
                    className={
                      "px-4 py-3 text-right font-mono tabular-nums " +
                      (r.loading_status ? TONE[r.loading_status] : "text-slate-500")
                    }
                  >
                    {r.base_loading_pct == null ? "—" : r.base_loading_pct.toFixed(1) + "%"}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                    {r.total_load_kw.toFixed(1)} kW
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-400">
                    {r.connection_points}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-300">
                    {r.min_hosting_capacity_kw == null
                      ? "—"
                      : r.min_hosting_capacity_kw.toFixed(0) + " kW"}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-amber-300">
                    {r.pending_pv_kw > 0 ? r.pending_pv_kw.toFixed(1) + " kW" : "—"}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-300">
                    {r.approved_pv_kw > 0 ? r.approved_pv_kw.toFixed(1) + " kW" : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-slate-600">
        Tightest capacity is the smallest hosting capacity among the connection
        points a transformer serves — the bus that would constrain first.
      </p>
    </div>
  );
}
