"use client";

import { useEffect, useMemo, useState } from "react";

import { api, ApiError, discomApi } from "@/lib/api";
import { RiskBadge } from "@/components/RiskBadge";
import type { FeederCapacityResult, HostingCapacityRow } from "@/lib/types";

export default function DiscomHostingCapacity() {
  const [rows, setRows] = useState<HostingCapacityRow[] | null>(null);
  const [feeders, setFeeders] = useState<FeederCapacityResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sortTightest, setSortTightest] = useState(true);

  useEffect(() => {
    api
      .hostingCapacity()
      .then((r) => setRows(r.buses))
      .catch((e: ApiError) => setError(e.message));
    discomApi
      .feederCapacity()
      .then(setFeeders)
      .catch(() => setFeeders(null));
  }, []);

  const sorted = useMemo(() => {
    if (!rows) return [];
    const copy = [...rows];
    copy.sort((a, b) =>
      sortTightest
        ? a.hosting_capacity_kw - b.hosting_capacity_kw
        : a.bus_id.localeCompare(b.bus_id)
    );
    return copy;
  }, [rows, sortTightest]);

  const stats = useMemo(() => {
    if (!rows?.length) return null;
    const values = rows.map((r) => r.hosting_capacity_kw).sort((a, b) => a - b);
    const byConstraint: Record<string, number> = {};
    for (const r of rows) {
      const k = r.limiting_constraint ?? "unknown";
      byConstraint[k] = (byConstraint[k] ?? 0) + 1;
    }
    return {
      min: values[0],
      median: values[Math.floor(values.length / 2)],
      max: values[values.length - 1],
      byConstraint,
    };
  }, [rows]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Hosting capacity</h1>
        <p className="mt-1 text-sm text-slate-500">
          The largest system each connection point can take before a hard limit is
          breached — found by binary search on the power flow, not estimated.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {stats && (
        <>
          <div className="grid gap-4 sm:grid-cols-4">
            <Stat label="Connection points" value={rows!.length} />
            <Stat label="Tightest" value={stats.min.toFixed(0)} unit="kW" accent="red" />
            <Stat label="Median" value={stats.median.toFixed(0)} unit="kW" />
            <Stat label="Largest" value={stats.max.toFixed(0)} unit="kW" accent="green" />
          </div>

          <div className="card">
            <div className="metric-label mb-2">What limits capacity</div>
            <div className="flex flex-wrap gap-4 text-sm">
              {Object.entries(stats.byConstraint).map(([k, v]) => (
                <span key={k} className="text-slate-300">
                  {k.replace(/_/g, " ")}: <b className="font-mono">{v}</b> buses
                </span>
              ))}
            </div>
          </div>
        </>
      )}

      {feeders && (
        <div className="space-y-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-200">By feeder section</h2>
            <p className="text-xs text-slate-500">
              Measured with every connection in the section energised together.
            </p>
          </div>

          <div className="card overflow-x-auto p-0">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-800 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Section</th>
                  <th className="px-4 py-3 text-right">Current solar</th>
                  <th className="px-4 py-3 text-right">Pending solar</th>
                  <th className="px-4 py-3 text-right">Hosting capacity</th>
                  <th className="px-4 py-3 text-right">Remaining</th>
                  <th className="px-4 py-3 text-right">Used</th>
                  <th className="px-4 py-3">Limiting constraint</th>
                  <th className="px-4 py-3">Risk</th>
                </tr>
              </thead>
              <tbody>
                {feeders.sections.map((f) => (
                  <tr
                    key={f.feeder_section}
                    className="border-b border-slate-900 last:border-0 hover:bg-slate-900/40"
                  >
                    <td className="px-4 py-3 font-mono text-slate-200">{f.feeder_section}</td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-300">
                      {f.current_solar_kw.toFixed(1)} kW
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-amber-300">
                      {f.pending_solar_kw > 0 ? f.pending_solar_kw.toFixed(1) + " kW" : "—"}
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-100">
                      {f.hosting_capacity_kw.toFixed(0)} kW
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-green-300">
                      {f.remaining_capacity_kw.toFixed(0)} kW
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                      {f.utilisation_pct.toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {f.limiting_constraint?.replace(/_/g, " ") ?? "—"}
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge risk={f.risk} size="sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
            <p>{feeders.method_note}</p>
            <p className="mt-2">{feeders.risk_note}</p>
            {feeders.sections.some((f) => f.overstatement_factor) && (
              <p className="mt-2 text-slate-400">
                For comparison, adding up each bus&rsquo;s individual capacity would
                overstate these sections by{" "}
                {feeders.sections
                  .filter((f) => f.overstatement_factor)
                  .map((f) => `${f.feeder_section} ${f.overstatement_factor}x`)
                  .join(", ")}
                .
              </p>
            )}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-sm font-semibold text-slate-200">By connection point</h2>
        <p className="text-xs text-slate-500">
          Each bus assessed on its own, as the only new connection.
        </p>
      </div>

      <button onClick={() => setSortTightest((s) => !s)} className="btn-ghost !text-xs">
        Sort by {sortTightest ? "bus id" : "tightest first"}
      </button>

      {rows === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {sorted.length > 0 && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Bus</th>
                <th className="px-4 py-3">Transformer</th>
                <th className="px-4 py-3">Section</th>
                <th className="px-4 py-3 text-right">Hosting capacity</th>
                <th className="px-4 py-3">Limited by</th>
                <th className="px-4 py-3">Reason at the limit</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r) => (
                <tr
                  key={r.bus_id}
                  className="border-b border-slate-900 last:border-0 hover:bg-slate-900/40"
                >
                  <td className="px-4 py-3 font-mono text-slate-200">{r.bus_id}</td>
                  <td className="px-4 py-3 text-slate-400">{r.transformer_association}</td>
                  <td className="px-4 py-3 text-slate-500">{r.feeder_section}</td>
                  <td
                    className={
                      "px-4 py-3 text-right font-mono tabular-nums " +
                      (r.hosting_capacity_kw < 60
                        ? "text-red-300"
                        : r.hosting_capacity_kw < 150
                          ? "text-yellow-300"
                          : "text-green-300")
                    }
                  >
                    {r.hosting_capacity_kw.toFixed(0)} kW
                  </td>
                  <td className="px-4 py-3 text-slate-400">
                    {r.limiting_constraint?.replace(/_/g, " ")}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{r.limiting_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {rows?.[0]?.method && (
        <p className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
          Method: {rows[0].method}. Each value is the outcome of repeated power-flow
          solves against the thresholds in scenario_config.json. Capacities are
          computed per bus independently — connecting several at once interacts, so
          they do not simply add.
        </p>
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
  accent?: "green" | "red";
}) {
  const tone =
    accent === "green" ? "text-green-300" : accent === "red" ? "text-red-300" : "text-slate-100";
  return (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className={"font-mono text-2xl tabular-nums " + tone}>
        {value}
        {unit && <span className="ml-1 text-xs text-slate-500">{unit}</span>}
      </div>
    </div>
  );
}
