"use client";

import { useEffect, useMemo, useState } from "react";

import { RiskBadge } from "@/components/RiskBadge";
import { TwinDiagram } from "@/components/TwinDiagram";
import { api, ApiError } from "@/lib/api";
import type { Bus, TwinResponse } from "@/lib/types";

/**
 * Interactive twin explorer.
 *
 * Every capacity tried here runs a real power flow on the server. Nothing is
 * interpolated between results and no curve is fitted — if a number changes on
 * screen, a simulation produced it.
 */
export default function TwinExplorerPage() {
  const [buses, setBuses] = useState<Bus[] | null>(null);
  const [busId, setBusId] = useState("734");
  const [existingKw, setExistingKw] = useState(0);
  const [newKw, setNewKw] = useState(66);

  const [twin, setTwin] = useState<TwinResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .buses()
      .then(setBuses)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const selected = useMemo(
    () => buses?.find((b) => b.bus_id === busId) ?? null,
    [buses, busId]
  );

  async function run() {
    setError(null);
    setBusy(true);
    try {
      setTwin(await api.twin({ pv_bus: busId, existing_pv_kw: existingKw, new_pv_kw: newKw }));
    } catch (e) {
      setError((e as ApiError).message);
      setTwin(null);
    } finally {
      setBusy(false);
    }
  }

  // Run once on first load so the page is never an empty shell.
  useEffect(() => {
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Grid twin</h1>
        <p className="mt-1 text-sm text-slate-500">
          See what a proposed system does to the network between the substation
          and your connection point.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      <div className="card">
        <div className="grid gap-4 sm:grid-cols-4">
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
              step={1}
              className="input"
              value={existingKw}
              onChange={(e) => setExistingKw(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="label">Proposed solar (kW)</label>
            <input
              type="number"
              min={1}
              step={1}
              className="input"
              value={newKw}
              onChange={(e) => setNewKw(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button onClick={run} disabled={busy || newKw <= 0} className="btn-primary">
            {busy ? "Simulating…" : "Run simulation"}
          </button>

          <div className="flex flex-wrap gap-1.5">
            {[5, 15, 30, 66, 100, 250].map((kw) => (
              <button
                key={kw}
                onClick={() => setNewKw(kw)}
                className={`rounded-md border px-2.5 py-1 text-xs transition ${
                  newKw === kw
                    ? "border-sky-600 bg-sky-950/60 text-sky-300"
                    : "border-slate-700 text-slate-400 hover:bg-slate-800"
                }`}
              >
                {kw} kW
              </button>
            ))}
          </div>

          {twin && (
            <div className="ml-auto">
              <RiskBadge risk={twin.assessment.engineering.engineering_risk} />
            </div>
          )}
        </div>

        {selected && (
          <div className="mt-4 grid gap-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-xs sm:grid-cols-4">
            <div>
              <div className="metric-label">Transformer</div>
              <div className="text-slate-300">
                {selected.transformer_association} · {selected.transformer_sn_kva} kVA
              </div>
            </div>
            <div>
              <div className="metric-label">Existing load</div>
              <div className="text-slate-300">{selected.existing_load_kw} kW</div>
            </div>
            <div>
              <div className="metric-label">Distance from source</div>
              <div className="text-slate-300">{selected.feeder_distance_km.toFixed(2)} km</div>
            </div>
            <div>
              <div className="metric-label">Upstream impedance</div>
              <div className="text-slate-300">{selected.upstream_z_ohm.toFixed(2)} Ω</div>
            </div>
          </div>
        )}
      </div>

      {twin && <TwinDiagram twin={twin} />}

      {twin && (
        <div className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-200">Engineering verdict</h3>
          <p className="text-sm text-slate-300">
            {twin.assessment.engineering.constraint_reason}
          </p>
        </div>
      )}
    </div>
  );
}
