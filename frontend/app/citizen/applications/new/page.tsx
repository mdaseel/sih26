"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { AssessmentResult } from "@/components/AssessmentResult";
import { api, ApiError } from "@/lib/api";
import type { Assessment, Bus } from "@/lib/types";

/**
 * New application form.
 *
 * The "Check the grid" button runs the real backend pipeline (ML + power flow)
 * without persisting anything, so an applicant can see the electrical
 * consequence of a capacity before committing to it. Submitting then creates
 * the application and re-runs the same pipeline, this time recording the result.
 */
export default function NewApplicationPage() {
  const router = useRouter();

  const [buses, setBuses] = useState<Bus[] | null>(null);
  const [busQuery, setBusQuery] = useState("");

  const [form, setForm] = useState({
    applicant_name: "",
    contact_phone: "",
    address_line: "",
    district: "",
    state: "",
    pincode: "",
    consumer_number: "",
    connection_type: "Residential",
    sanctioned_load_kw: "",
    monthly_consumption_kwh: "",
    roof_area_sqm: "",
    roof_type: "RCC flat",
    shading_level: "Low",
    pv_bus: "",
    existing_pv_kw: "0",
    new_pv_kw: "5",
  });

  const [preview, setPreview] = useState<Assessment | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .buses()
      .then(setBuses)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const selectedBus = useMemo(
    () => buses?.find((b) => b.bus_id === form.pv_bus) ?? null,
    [buses, form.pv_bus]
  );

  const filteredBuses = useMemo(() => {
    if (!buses) return [];
    const q = busQuery.trim().toLowerCase();
    if (!q) return buses;
    return buses.filter(
      (b) =>
        b.bus_id.includes(q) ||
        b.feeder_section.toLowerCase().includes(q) ||
        b.transformer_association.toLowerCase().includes(q)
    );
  }, [buses, busQuery]);

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
    // A changed input invalidates the previous preview — never leave a stale
    // electrical result on screen next to different inputs.
    setPreview(null);
  }

  const canAssess =
    form.pv_bus !== "" && Number(form.new_pv_kw) > 0 && !Number.isNaN(Number(form.new_pv_kw));

  async function runPreview() {
    setError(null);
    setPreviewing(true);
    try {
      const result = await api.assess({
        pv_bus: form.pv_bus,
        existing_pv_kw: Number(form.existing_pv_kw) || 0,
        new_pv_kw: Number(form.new_pv_kw),
      });
      setPreview(result);
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setPreviewing(false);
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const numeric = (v: string) => (v === "" ? null : Number(v));

    try {
      const created = await api.createApplication({
        applicant_name: form.applicant_name,
        contact_phone: form.contact_phone || null,
        address_line: form.address_line || null,
        district: form.district || null,
        state: form.state || null,
        pincode: form.pincode || null,
        consumer_number: form.consumer_number || null,
        connection_type: form.connection_type || null,
        sanctioned_load_kw: numeric(form.sanctioned_load_kw),
        monthly_consumption_kwh: numeric(form.monthly_consumption_kwh),
        roof_area_sqm: numeric(form.roof_area_sqm),
        roof_type: form.roof_type || null,
        shading_level: form.shading_level || null,
        pv_bus: form.pv_bus,
        existing_pv_kw: Number(form.existing_pv_kw) || 0,
        new_pv_kw: Number(form.new_pv_kw),
        submit: true,
      });

      // Assess immediately so the applicant lands on a completed result.
      await api.assessApplication(created.id).catch(() => null);
      router.push(`/citizen/applications/${created.id}`);
    } catch (e) {
      setError((e as ApiError).message);
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">New application</h1>
        <p className="mt-1 text-sm text-slate-500">
          Your request is screened against the distribution network before it
          reaches the DISCOM.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      <form onSubmit={onSubmit} className="grid gap-6 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-3">
          {/* ---- Applicant ---- */}
          <div className="card space-y-4">
            <h2 className="text-sm font-semibold text-slate-200">Your details</h2>

            <div>
              <label className="label">Full name</label>
              <input
                required
                className="input"
                value={form.applicant_name}
                onChange={(e) => set("applicant_name", e.target.value)}
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label">Phone</label>
                <input
                  className="input"
                  value={form.contact_phone}
                  onChange={(e) => set("contact_phone", e.target.value)}
                />
              </div>
              <div>
                <label className="label">Consumer number</label>
                <input
                  className="input"
                  value={form.consumer_number}
                  onChange={(e) => set("consumer_number", e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="label">Address</label>
              <input
                className="input"
                value={form.address_line}
                onChange={(e) => set("address_line", e.target.value)}
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="label">District</label>
                <input
                  className="input"
                  value={form.district}
                  onChange={(e) => set("district", e.target.value)}
                />
              </div>
              <div>
                <label className="label">State</label>
                <input
                  className="input"
                  value={form.state}
                  onChange={(e) => set("state", e.target.value)}
                />
              </div>
              <div>
                <label className="label">PIN code</label>
                <input
                  className="input"
                  value={form.pincode}
                  onChange={(e) => set("pincode", e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* ---- Connection and roof ---- */}
          <div className="card space-y-4">
            <h2 className="text-sm font-semibold text-slate-200">
              Connection and roof
            </h2>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label">Connection type</label>
                <select
                  className="input"
                  value={form.connection_type}
                  onChange={(e) => set("connection_type", e.target.value)}
                >
                  <option>Residential</option>
                  <option>Commercial</option>
                  <option>Institutional</option>
                </select>
              </div>
              <div>
                <label className="label">Sanctioned load (kW)</label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  className="input"
                  value={form.sanctioned_load_kw}
                  onChange={(e) => set("sanctioned_load_kw", e.target.value)}
                />
              </div>
              <div>
                <label className="label">Monthly consumption (kWh)</label>
                <input
                  type="number"
                  min="0"
                  className="input"
                  value={form.monthly_consumption_kwh}
                  onChange={(e) => set("monthly_consumption_kwh", e.target.value)}
                />
              </div>
              <div>
                <label className="label">Roof area (m²)</label>
                <input
                  type="number"
                  min="0"
                  className="input"
                  value={form.roof_area_sqm}
                  onChange={(e) => set("roof_area_sqm", e.target.value)}
                />
              </div>
              <div>
                <label className="label">Roof type</label>
                <select
                  className="input"
                  value={form.roof_type}
                  onChange={(e) => set("roof_type", e.target.value)}
                >
                  <option>RCC flat</option>
                  <option>Metal sheet</option>
                  <option>Tiled</option>
                </select>
              </div>
              <div>
                <label className="label">Shading</label>
                <select
                  className="input"
                  value={form.shading_level}
                  onChange={(e) => set("shading_level", e.target.value)}
                >
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                </select>
              </div>
            </div>
          </div>

          {/* ---- Technical ---- */}
          <div className="card space-y-4">
            <h2 className="text-sm font-semibold text-slate-200">
              Solar capacity and grid connection point
            </h2>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label">Existing solar (kW)</label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  className="input"
                  value={form.existing_pv_kw}
                  onChange={(e) => set("existing_pv_kw", e.target.value)}
                />
              </div>
              <div>
                <label className="label">Requested new solar (kW)</label>
                <input
                  type="number"
                  min="0.1"
                  step="0.1"
                  required
                  className="input"
                  value={form.new_pv_kw}
                  onChange={(e) => set("new_pv_kw", e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="label">
                Grid connection point ({buses?.length ?? "…"} eligible LV buses)
              </label>
              <input
                className="input mb-2"
                placeholder="Search by bus, transformer or section…"
                value={busQuery}
                onChange={(e) => setBusQuery(e.target.value)}
              />
              <select
                required
                size={8}
                className="input font-mono text-xs"
                value={form.pv_bus}
                onChange={(e) => set("pv_bus", e.target.value)}
              >
                <option value="" disabled>
                  Select a connection point
                </option>
                {filteredBuses.map((b) => (
                  <option key={b.bus_id} value={b.bus_id}>
                    Bus {b.bus_id} · {b.vn_kv} kV · {b.transformer_association} ·{" "}
                    {b.feeder_section}
                  </option>
                ))}
              </select>
            </div>

            {selectedBus && (
              <div className="grid gap-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-xs sm:grid-cols-4">
                <div>
                  <div className="metric-label">Transformer</div>
                  <div className="text-slate-300">
                    {selectedBus.transformer_association} ·{" "}
                    {selectedBus.transformer_sn_kva} kVA
                  </div>
                </div>
                <div>
                  <div className="metric-label">Existing load</div>
                  <div className="text-slate-300">
                    {selectedBus.existing_load_kw} kW
                  </div>
                </div>
                <div>
                  <div className="metric-label">Distance from source</div>
                  <div className="text-slate-300">
                    {selectedBus.feeder_distance_km.toFixed(2)} km
                  </div>
                </div>
                <div>
                  <div className="metric-label">Upstream impedance</div>
                  <div className="text-slate-300">
                    {selectedBus.upstream_z_ohm.toFixed(2)} Ω
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ---- Right column: preview + submit ---- */}
        <div className="space-y-4 lg:col-span-2">
          <div className="card">
            <h2 className="text-sm font-semibold text-slate-200">
              Check the grid first
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Runs the real assessment — ML pre-screen followed by a power-flow
              simulation — without saving anything.
            </p>
            <button
              type="button"
              onClick={runPreview}
              disabled={!canAssess || previewing}
              className="btn-ghost mt-3 w-full"
            >
              {previewing ? "Simulating…" : "Check the grid"}
            </button>

            <button
              type="submit"
              disabled={submitting || !canAssess || !form.applicant_name}
              className="btn-primary mt-2 w-full"
            >
              {submitting ? "Submitting…" : "Submit application"}
            </button>

            <p className="mt-3 text-[11px] leading-relaxed text-slate-600">
              Submitting records the request and its assessment for DISCOM
              review. This is a technical pre-screening, not an official
              approval.
            </p>
          </div>

          {preview && (
            <div className="rounded-xl border border-slate-800 p-1">
              <div className="mb-2 px-3 pt-2 text-xs uppercase tracking-wide text-slate-500">
                Preview — not saved
              </div>
              <div className="max-h-[60vh] overflow-y-auto px-1">
                <AssessmentResult result={preview} />
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
