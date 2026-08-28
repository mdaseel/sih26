"use client";

import { useEffect, useMemo, useState } from "react";

import { RiskBadge } from "@/components/RiskBadge";
import { TwinDiagram } from "@/components/TwinDiagram";
import { api, ApiError } from "@/lib/api";
import type { Bus, TwinResponse } from "@/lib/types";

export default function DiscomGridTwin() {
  const [buses, setBuses] = useState<Bus[] | null>(null);
  const [busId, setBusId] = useState("734");
  const [existingKw, setExistingKw] = useState(0);
  const [newKw, setNewKw] = useState(66);
  const [twin, setTwin] = useState<TwinResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.buses().then(setBuses).catch((e: ApiError) => setError(e.message));
  }, []);

  const selected = useMemo(() => buses?.find((b) => b.bus_id === busId) ?? null, [buses, busId]);

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

  useEffect(() => {
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Grid twin</h1>
        <p className="mt-1 text-sm text-slate-500">
          Trace any connection point from the substation and see what a proposed
          system does to it.
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
          {selected && (
            <span className="text-xs text-slate-500">
              {selected.transformer_association} · {selected.transformer_sn_kva} kVA ·{" "}
              {selected.feeder_distance_km.toFixed(2)} km from source
            </span>
          )}
          {twin && (
            <span className="ml-auto">
              <RiskBadge risk={twin.assessment.engineering.engineering_risk} />
            </span>
          )}
        </div>
      </div>

      {twin && <TwinDiagram twin={twin} />}
    </div>
  );
}
