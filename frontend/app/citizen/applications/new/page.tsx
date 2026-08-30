"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { api, ApiError } from "@/lib/api";
import type { ConnectionPoint } from "@/lib/types";
import { SolarPlanner, type SolarPlacement } from "@/components/solar3d/SolarPlanner";

/**
 * New application form.
 *
 * Two things this form deliberately does not do.
 *
 * It does not ask for sanctioned load. That is a DISCOM-side record of the
 * load sanctioned on the service connection; an applicant rarely has it to
 * hand, and asking invites a guess that would then travel onward looking like
 * a declaration. The backend fills it from the connection point instead.
 *
 * It does not offer a grid pre-check. Screening capacity against the network
 * is the DISCOM's instrument, and a citizen who sees SAFE before submitting
 * reads it as permission. The assessment still runs the moment the application
 * is submitted — it just is not presented as a green light beforehand.
 */

const REQUIRED_NOTE = "Required";

/** Marks a field the form will not submit without. */
function Required() {
  return (
    <span className="ml-1 text-red-400" title={REQUIRED_NOTE} aria-hidden="true">
      *
    </span>
  );
}

export default function NewApplicationPage() {
  const router = useRouter();

  const [locating, setLocating] = useState(false);
  const [locationNote, setLocationNote] = useState<string | null>(null);

  const [form, setForm] = useState({
    applicant_name: "",
    contact_phone: "",
    address_line: "",
    district: "",
    state: "",
    pincode: "",
    latitude: "",
    longitude: "",
    consumer_number: "",
    connection_type: "Residential",
    monthly_consumption_kwh: "",
    roof_area_sqm: "",
    roof_type: "RCC flat",
    shading_level: "Low",
    existing_pv_kw: "0",
    new_pv_kw: "5",
  });

  const [solarPlacement, setSolarPlacement] = useState<SolarPlacement | null>(null);
  const [connectionPoint, setConnectionPoint] = useState<ConnectionPoint | null>(null);
  const [resolvingPoint, setResolvingPoint] = useState(false);
  const [pointError, setPointError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const latNumber = Number(form.latitude);
  const lonNumber = Number(form.longitude);
  const hasCoordinates =
    form.latitude.trim() !== "" &&
    form.longitude.trim() !== "" &&
    Number.isFinite(latNumber) &&
    Number.isFinite(lonNumber) &&
    Math.abs(latNumber) <= 90 &&
    Math.abs(lonNumber) <= 180;

  // Resolve the connection point from the location, debounced so that typing a
  // coordinate does not fire a request per keystroke.
  useEffect(() => {
    if (!hasCoordinates) {
      setConnectionPoint(null);
      setPointError(null);
      return;
    }
    let cancelled = false;
    setResolvingPoint(true);
    const timer = window.setTimeout(() => {
      api
        .connectionPoint(latNumber, lonNumber)
        .then((point) => {
          if (cancelled) return;
          setConnectionPoint(point);
          setPointError(null);
        })
        .catch((e: ApiError) => {
          if (cancelled) return;
          setConnectionPoint(null);
          setPointError(
            `Could not work out your connection point: ${e.message}. You can still submit — the DISCOM assigns it on review.`
          );
        })
        .finally(() => {
          if (!cancelled) setResolvingPoint(false);
        });
    }, 500);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      setResolvingPoint(false);
    };
  }, [hasCoordinates, latNumber, lonNumber]);

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  /** Fills the coordinates from the browser, with the user's permission. */
  function useMyLocation() {
    if (!navigator.geolocation) {
      setLocationNote("This browser cannot report a location. Enter the coordinates by hand.");
      return;
    }
    setLocating(true);
    setLocationNote(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm((f) => ({
          ...f,
          latitude: pos.coords.latitude.toFixed(6),
          longitude: pos.coords.longitude.toFixed(6),
        }));
        setLocationNote(
          `Filled from your device (accurate to about ${Math.round(pos.coords.accuracy)} m). Correct it if this is not the installation site.`
        );
        setLocating(false);
      },
      (err) => {
        setLocationNote(
          err.code === err.PERMISSION_DENIED
            ? "Location permission was declined. Enter the coordinates by hand."
            : "Could not read a location from this device. Enter the coordinates by hand."
        );
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10_000 }
    );
  }

  const complete =
    form.applicant_name.trim() !== "" &&
    form.contact_phone.trim() !== "" &&
    form.address_line.trim() !== "" &&
    form.district.trim() !== "" &&
    form.state.trim() !== "" &&
    form.pincode.trim() !== "" &&
    form.latitude.trim() !== "" &&
    form.longitude.trim() !== "" &&
    form.connection_type !== "" &&
    form.monthly_consumption_kwh.trim() !== "" &&
    form.roof_area_sqm.trim() !== "" &&
    form.roof_type !== "" &&
    form.shading_level !== "" &&
    Number(form.new_pv_kw) > 0 &&
    !Number.isNaN(Number(form.new_pv_kw));

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const numeric = (v: string) => (v === "" ? null : Number(v));

    try {
      const created = await api.createApplication({
        applicant_name: form.applicant_name.trim(),
        contact_phone: form.contact_phone.trim(),
        address_line: form.address_line.trim(),
        district: form.district.trim(),
        state: form.state.trim(),
        pincode: form.pincode.trim(),
        latitude: numeric(form.latitude),
        longitude: numeric(form.longitude),
        consumer_number: form.consumer_number.trim() || null,
        connection_type: form.connection_type,
        monthly_consumption_kwh: numeric(form.monthly_consumption_kwh),
        roof_area_sqm: numeric(form.roof_area_sqm),
        roof_type: form.roof_type,
        shading_level: form.shading_level,
        existing_pv_kw: Number(form.existing_pv_kw) || 0,
        new_pv_kw: Number(form.new_pv_kw),
        solar_placement: solarPlacement,
        submit: true,
      });

      // Screen it straight away so the DISCOM receives an assessed application.
      // A failure here is not fatal: the application exists and can be assessed
      // again, so the applicant is not made to fill the form twice.
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
          Your request is screened against the distribution network before it reaches
          the DISCOM. Fields marked <span className="text-red-400">*</span> are required.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      <form onSubmit={onSubmit} className="space-y-6">
        {/* ---- Applicant ---- */}
        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Your details</h2>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="applicant_name">
                Full name
                <Required />
              </label>
              <input
                id="applicant_name"
                required
                className="input"
                value={form.applicant_name}
                onChange={(e) => set("applicant_name", e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="contact_phone">
                Phone
                <Required />
              </label>
              <input
                id="contact_phone"
                required
                inputMode="tel"
                pattern="[0-9+\-\s]{6,20}"
                title="Digits, spaces, + and - only"
                className="input"
                value={form.contact_phone}
                onChange={(e) => set("contact_phone", e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="label" htmlFor="consumer_number">
              Consumer number
            </label>
            <input
              id="consumer_number"
              className="input"
              placeholder="From your electricity bill, if you have it to hand"
              value={form.consumer_number}
              onChange={(e) => set("consumer_number", e.target.value)}
            />
          </div>
        </div>

        {/* ---- Site ---- */}
        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Installation site</h2>

          <div>
            <label className="label" htmlFor="address_line">
              Address
              <Required />
            </label>
            <input
              id="address_line"
              required
              className="input"
              value={form.address_line}
              onChange={(e) => set("address_line", e.target.value)}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="label" htmlFor="district">
                District
                <Required />
              </label>
              <input
                id="district"
                required
                className="input"
                value={form.district}
                onChange={(e) => set("district", e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="state">
                State
                <Required />
              </label>
              <input
                id="state"
                required
                className="input"
                value={form.state}
                onChange={(e) => set("state", e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="pincode">
                PIN code
                <Required />
              </label>
              <input
                id="pincode"
                required
                inputMode="numeric"
                pattern="[0-9]{6}"
                title="Six digits"
                maxLength={6}
                className="input"
                value={form.pincode}
                onChange={(e) => set("pincode", e.target.value)}
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="label" htmlFor="latitude">
                Latitude
                <Required />
              </label>
              <input
                id="latitude"
                required
                type="number"
                step="any"
                min={-90}
                max={90}
                placeholder="e.g. 11.01684"
                className="input"
                value={form.latitude}
                onChange={(e) => set("latitude", e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="longitude">
                Longitude
                <Required />
              </label>
              <input
                id="longitude"
                required
                type="number"
                step="any"
                min={-180}
                max={180}
                placeholder="e.g. 76.95584"
                className="input"
                value={form.longitude}
                onChange={(e) => set("longitude", e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <button
                type="button"
                onClick={useMyLocation}
                disabled={locating}
                className="btn-ghost w-full"
              >
                {locating ? "Locating…" : "Use my location"}
              </button>
            </div>
          </div>

          <p className="text-xs text-slate-500">
            {locationNote ??
              "Coordinates place your site on the map and are what installers are measured from. Without them, no installer can be sorted by distance."}
          </p>
        </div>

        {/* ---- Technical ---- */}
        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">
            Solar capacity and grid connection point
          </h2>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="existing_pv_kw">
                Existing solar (kW)
                <Required />
              </label>
              <input
                id="existing_pv_kw"
                required
                type="number"
                min="0"
                step="0.1"
                className="input"
                value={form.existing_pv_kw}
                onChange={(e) => set("existing_pv_kw", e.target.value)}
              />
              <p className="mt-1 text-xs text-slate-600">
                Enter 0 if you have no solar installed today.
              </p>
            </div>
            <div>
              <label className="label" htmlFor="new_pv_kw">
                Requested new solar (kW)
                <Required />
              </label>
              <input
                id="new_pv_kw"
                required
                type="number"
                min="0.1"
                step="0.1"
                className="input"
                value={form.new_pv_kw}
                onChange={(e) => set("new_pv_kw", e.target.value)}
              />
            </div>
          </div>

          {/* ---- connection point, resolved not asked ---- */}
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-medium text-slate-200">
                Your grid connection point
              </h3>
              {connectionPoint && (
                <span className="rounded border border-amber-900 bg-amber-950/40 px-2 py-0.5 text-[11px] text-amber-200">
                  Provisional — DISCOM confirms
                </span>
              )}
            </div>

            {!hasCoordinates && (
              <p className="mt-2 text-xs text-slate-500">
                Enter the site location above and this is filled in for you. You are
                not expected to know which bus or transformer serves your address —
                that is the DISCOM&apos;s record, not something on your bill.
              </p>
            )}

            {hasCoordinates && resolvingPoint && (
              <p className="mt-2 text-xs text-slate-500">Looking up your connection point…</p>
            )}

            {hasCoordinates && pointError && (
              <p className="mt-2 text-xs text-amber-400">{pointError}</p>
            )}

            {connectionPoint && (
              <>
                <div className="mt-3 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
                  <div>
                    <div className="metric-label">Connection point</div>
                    <div className="font-mono text-sm text-slate-200">
                      Bus {connectionPoint.pv_bus}
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Voltage level</div>
                    <div className="text-slate-300">{connectionPoint.voltage_level_kv} kV</div>
                  </div>
                  <div>
                    <div className="metric-label">Transformer</div>
                    <div className="text-slate-300">
                      {connectionPoint.transformer} · {connectionPoint.transformer_sn_kva} kVA
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Feeder section</div>
                    <div className="text-slate-300">{connectionPoint.feeder_section}</div>
                  </div>
                  <div>
                    <div className="metric-label">Connected load</div>
                    <div className="text-slate-300">
                      {connectionPoint.connected_load_kw} kW
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Base voltage</div>
                    <div className="text-slate-300">
                      {connectionPoint.base_voltage_pu.toFixed(4)} pu
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Distance from source</div>
                    <div className="text-slate-300">
                      {connectionPoint.feeder_distance_km.toFixed(2)} km
                    </div>
                  </div>
                  <div>
                    <div className="metric-label">Upstream impedance</div>
                    <div className="text-slate-300">
                      {connectionPoint.upstream_z_ohm.toFixed(2)} Ω
                    </div>
                  </div>
                </div>

                <p className="mt-3 text-[11px] leading-relaxed text-slate-600">
                  {connectionPoint.note}
                </p>

                {connectionPoint.separation_km != null &&
                  connectionPoint.separation_km > 25 && (
                    <p className="mt-2 text-[11px] leading-relaxed text-amber-400">
                      The nearest modelled connection point is{" "}
                      {connectionPoint.separation_km.toFixed(0)} km from your site. The
                      feeder in this prototype is a synthetic research network placed at
                      a fixed anchor, so it does not cover your area — the screening
                      still runs, but treat the electrical result as illustrative.
                    </p>
                  )}
              </>
            )}
          </div>
        </div>

        {/* ---- Connection and roof ---- */}
        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Consumption and roof</h2>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="connection_type">
                Connection type
                <Required />
              </label>
              <select
                id="connection_type"
                required
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
              <label className="label" htmlFor="monthly_consumption_kwh">
                Monthly consumption (kWh)
                <Required />
              </label>
              <input
                id="monthly_consumption_kwh"
                required
                type="number"
                min="0"
                step="1"
                placeholder="From a recent electricity bill"
                className="input"
                value={form.monthly_consumption_kwh}
                onChange={(e) => set("monthly_consumption_kwh", e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="roof_area_sqm">
                Roof area (m²)
                <Required />
              </label>
              <input
                id="roof_area_sqm"
                required
                type="number"
                min="1"
                step="0.5"
                className="input"
                value={form.roof_area_sqm}
                onChange={(e) => set("roof_area_sqm", e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="roof_type">
                Roof type
                <Required />
              </label>
              <select
                id="roof_type"
                required
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
              <label className="label" htmlFor="shading_level">
                Shading
                <Required />
              </label>
              <select
                id="shading_level"
                required
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


        {/* ---- 3D Rooftop Solar Placement & Real-Time Sunlight Analysis ---- */}
        <div className="card space-y-4">
          <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <span>🛰️</span> 3D Rooftop Solar Placement & Real-Time Sunlight Analysis
          </h2>

          <SolarPlanner
            latitude={Number(form.latitude) || 18.5204}
            longitude={Number(form.longitude) || 73.8567}
            initialCapacityKw={Number(form.new_pv_kw) || 5}
            pvBus={connectionPoint?.pv_bus ?? "734"}
            roofAreaSqm={Number(form.roof_area_sqm) || null}
            onCapacityChange={(kw) => set("new_pv_kw", kw.toFixed(1))}
            onUsePlacement={(placement) => {
              setSolarPlacement(placement);
              setForm((f) => ({
                ...f,
                latitude: placement.latitude.toFixed(6),
                longitude: placement.longitude.toFixed(6),
                new_pv_kw: placement.capacity_kw.toFixed(1),
                roof_area_sqm: placement.array_area_sqm.toFixed(1),
                shading_level: placement.suitability === "GOOD" ? "Low" : placement.suitability === "PARTIAL" ? "Medium" : "High",
              }));
            }}
          />
        </div>

        {/* ---- Submit ---- */}
        <div className="card">
          <button
            type="submit"
            disabled={submitting || !complete}
            className="btn-primary w-full sm:w-auto"
          >
            {submitting ? "Submitting…" : "Submit application"}
          </button>
          {!complete && (
            <p className="mt-2 text-xs text-amber-400">
              Fill every required field to submit.
            </p>
          )}
          <p className="mt-3 text-xs leading-relaxed text-slate-600">
            Submitting records your request, screens it against the distribution network,
            and sends it to the DISCOM for review. This is a technical pre-screening, not
            an official approval — the DISCOM decides.
          </p>
        </div>
      </form>
    </div>
  );
}
