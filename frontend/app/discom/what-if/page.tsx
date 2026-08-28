"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { RiskBadge } from "@/components/RiskBadge";
import { TwinDiagram } from "@/components/TwinDiagram";
import { api, ApiError, discomApi } from "@/lib/api";
import type { Bus, TwinResponse, WhatIfResult } from "@/lib/types";

const DEFAULT_SIZES = [10, 25, 50, 100, 250, 500];

/**
 * What-if analysis.
 *
 * The whole sweep is one request; the server solves a power flow per capacity.
 * Selecting a row loads the digital twin for that exact capacity, so the
 * engineer sees which assets move rather than only the summary numbers.
 *
 * Nothing between the tested capacities is interpolated. The precise limit is
 * the bisected hosting capacity, shown alongside for comparison.
 */
export default function DiscomWhatIf() {
  const [buses, setBuses] = useState<Bus[] | null>(null);
  const [busId, setBusId] = useState("734");
  const [existingKw, setExistingKw] = useState(0);
  const [sizes, setSizes] = useState<number[]>(DEFAULT_SIZES);
  const [customKw, setCustomKw] = useState("");

  const [result, setResult] = useState<WhatIfResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedKw, setSelectedKw] = useState<number | null>(null);
  const [twin, setTwin] = useState<TwinResponse | null>(null);
  const [twinBusy, setTwinBusy] = useState(false);

  useEffect(() => {
    api
      .buses()
      .then(setBuses)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const selectedBus = useMemo(
    () => buses?.find((b) => b.bus_id === busId) ?? null,
    [buses, busId]
  );

  async function run() {
    setError(null);
    setBusy(true);
    setResult(null);
    setTwin(null);
    setSelectedKw(null);
    try {
      setResult(await discomApi.whatIf(busId, existingKw, sizes));
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusy(false);
    }
  }

  /** Load the twin for one tested capacity, so the diagram matches the row. */
  async function showTwin(kw: number) {
    setSelectedKw(kw);
    setTwinBusy(true);
    try {
      setTwin(await api.twin({ pv_bus: busId, existing_pv_kw: existingKw, new_pv_kw: kw }));
    } catch {
      setTwin(null);
    } finally {
      setTwinBusy(false);
    }
  }

  useEffect(() => {
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function addCustom() {
    const kw = Number(customKw);
    if (!Number.isFinite(kw) || kw <= 0) return;
    setSizes((s) => Array.from(new Set([...s, kw])).sort((a, b) => a - b));
    setCustomKw("");
  }

  const capacity = result?.hosting_capacity;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">What-if analysis</h1>
        <p className="mt-1 text-sm text-slate-500">
          Test capacities at a connection point. Every row is a real power-flow
          solve on the feeder model.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      <div className="card">
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="sm:col-span-2">
            <label className="label">Connection point</label>
            <select className="input" value={busId} onChange={(e) => setBusId(e.target.value)}>
              {buses?.map((b) => (
                <option key={b.bus_id} value={b.bus_id}>
                  Bus {b.bus_id} · {b.transformer_association} · {b.feeder_section}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Existing solar (kW)</label>
            <input
              type="number"
              min={0}
              className="input"
              value={existingKw}
              onChange={(e) => setExistingKw(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="mt-4">
          <label className="label">Capacities to test (kW)</label>
          <div className="flex flex-wrap items-center gap-1.5">
            {sizes.map((kw) => (
              <span
                key={kw}
                className="flex items-center gap-1 rounded-md border border-slate-700 px-2 py-1 text-xs text-slate-300"
              >
                {kw}
                <button
                  onClick={() => setSizes((s) => s.filter((v) => v !== kw))}
                  className="text-slate-500 hover:text-red-400"
                  aria-label={`Remove ${kw} kW`}
                >
                  ×
                </button>
              </span>
            ))}
            <input
              className="input !w-24 !py-1 text-xs"
              placeholder="add kW"
              value={customKw}
              onChange={(e) => setCustomKw(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addCustom()}
            />
            <button onClick={addCustom} className="btn-ghost !px-2.5 !py-1 !text-xs">
              Add
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button onClick={run} disabled={busy || sizes.length === 0} className="btn-primary">
            {busy ? "Simulating…" : `Run ${sizes.length} simulations`}
          </button>
          {selectedBus && (
            <span className="text-xs text-slate-500">
              {selectedBus.transformer_association} · {selectedBus.transformer_sn_kva} kVA · load{" "}
              {selectedBus.existing_load_kw} kW · {selectedBus.feeder_distance_km.toFixed(2)} km out
            </span>
          )}
        </div>
      </div>

      {capacity && (
        <div className="card border-sky-900/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="metric-label">Hosting capacity at this bus</div>
              <div className="font-mono text-2xl tabular-nums text-sky-300">
                {capacity.hosting_capacity_kw.toFixed(0)}
                <span className="ml-1 text-xs text-slate-500">kW</span>
              </div>
            </div>
            <div className="max-w-xl text-xs text-slate-400">
              <div>
                Limited by <b>{capacity.limiting_constraint.replace(/_/g, " ")}</b> —{" "}
                {capacity.limiting_reason}
              </div>
              <div className="mt-1 text-slate-600">
                {capacity.method}, {capacity.power_flows_run} power flows, resolution{" "}
                {capacity.resolution_kw} kW
              </div>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3 text-right">Capacity</th>
                <th className="px-4 py-3">Risk</th>
                <th className="px-4 py-3 text-right">Voltage</th>
                <th className="px-4 py-3 text-right">Rise</th>
                <th className="px-4 py-3 text-right">Transformer</th>
                <th className="px-4 py-3 text-right">Line</th>
                <th className="px-4 py-3">Reverse</th>
                <th className="px-4 py-3 text-right">Losses</th>
                <th className="px-4 py-3">Binding constraint</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {result.points.map((p) => {
                if (!p.converged || !p.metrics) {
                  return (
                    <tr key={p.new_pv_kw} className="border-b border-slate-900 last:border-0">
                      <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-200">
                        {p.new_pv_kw} kW
                      </td>
                      <td className="px-4 py-3 text-xs text-red-300" colSpan={9}>
                        No solution — {p.error}
                      </td>
                    </tr>
                  );
                }
                const m = p.metrics;
                const overCapacity =
                  capacity != null && p.new_pv_kw > capacity.hosting_capacity_kw;
                return (
                  <tr
                    key={p.new_pv_kw}
                    className={
                      "border-b border-slate-900 last:border-0 " +
                      (selectedKw === p.new_pv_kw
                        ? "bg-sky-950/30"
                        : overCapacity
                          ? "bg-red-950/10"
                          : "hover:bg-slate-900/40")
                    }
                  >
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-200">
                      {p.new_pv_kw} kW
                    </td>
                    <td className="px-4 py-3">
                      {p.engineering_risk && <RiskBadge risk={p.engineering_risk} size="sm" />}
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                      {m.pv_voltage_pu.toFixed(4)}
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-300">
                      {m.voltage_rise_pu.toFixed(5)}
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                      {m.max_transformer_loading_pct.toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                      {m.max_line_loading_pct.toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {m.reverse_power_flow ? "Yes" : "No"}
                    </td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                      {m.power_loss_kw.toFixed(0)}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {p.constraint_type === "none" ? "—" : p.constraint_reason}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => showTwin(p.new_pv_kw)}
                        className="text-xs text-sky-400 hover:underline"
                      >
                        View twin
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {twinBusy && <div className="card text-sm text-slate-400">Loading the twin…</div>}

      {twin && selectedKw !== null && (
        <div>
          <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">
            Digital twin at {selectedKw} kW
          </div>
          <TwinDiagram twin={twin} />
        </div>
      )}

      {result && (
        <p className="text-xs text-slate-600">
          {result.note} Section-level limits are on the{" "}
          <Link href="/discom/hosting-capacity" className="text-sky-400 hover:underline">
            hosting capacity
          </Link>{" "}
          page.
        </p>
      )}
    </div>
  );
}
