"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";

import { DEFAULT_PANEL_SPEC, layoutFor, type PanelSpec } from "@/lib/solar/array";
import { estimatedOptimalTilt, optimalAzimuth, solarNoon } from "@/lib/solar/sun";
import { api } from "@/lib/api";
import type { BuildingFootprint, SolarApplication, Assessment } from "@/lib/types";
import type { SceneStatus, ShadingSample, SurfaceInfo } from "./CesiumScene";

/**
 * The 3D digital twin of one application's site.
 *
 * Read-only, unlike the planner: this shows what was proposed and what the
 * grid assessment said about it. Every number on the panel comes from the
 * application row or the stored assessment — the twin measures nothing
 * electrical and invents nothing. Where the backend has no value, the field
 * reads "—" rather than a plausible substitute.
 *
 * The array geometry is derived, not stored: capacity and module rating give a
 * panel count, and tilt and azimuth come from the saved placement when the
 * applicant made one in the planner, or from the site's latitude when they did
 * not. That is a drawing of the proposal, and it is labelled as such.
 */

const CesiumScene = dynamic(
  () => import("./CesiumScene").then((m) => m.CesiumScene),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[520px] w-full items-center justify-center rounded-xl border border-slate-800 bg-slate-950 text-sm text-slate-500">
        Loading the 3D scene…
      </div>
    ),
  }
);

type Risk = "SAFE" | "CAUTION" | "CONSTRAINED";

const RISK_STYLE: Record<Risk, string> = {
  SAFE: "border-green-800 bg-green-950/50 text-green-300",
  CAUTION: "border-amber-800 bg-amber-950/50 text-amber-300",
  CONSTRAINED: "border-red-900 bg-red-950/50 text-red-300",
};

const RISK_DOT: Record<Risk, string> = {
  SAFE: "bg-green-400",
  CAUTION: "bg-amber-400",
  CONSTRAINED: "bg-red-400",
};

/** Placement the applicant saved in the planner, if any. */
interface SavedPlacement {
  tilt_deg?: number;
  azimuth_deg?: number;
  panel_count?: number;
  panel_watts?: number;
  panel_width_m?: number;
  panel_length_m?: number;
  mount_height_m?: number;
  suitability?: string;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-b border-slate-800/70 py-1.5 last:border-0">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="font-mono text-sm tabular-nums text-slate-200">{value}</span>
    </div>
  );
}

export function RooftopTwin({
  application,
  assessment,
}: {
  application: SolarApplication;
  assessment: Assessment | null;
}) {
  const [status, setStatus] = useState<SceneStatus>("idle");
  const [statusDetail, setStatusDetail] = useState<string | null>(null);
  const [surface, setSurface] = useState<SurfaceInfo | null>(null);
  const [resetToken, setResetToken] = useState(0);
  const [panelOpen, setPanelOpen] = useState(true);
  const [siteBuildings, setSiteBuildings] = useState<BuildingFootprint[] | null>(null);
  const [contextNote, setContextNote] = useState<string | null>(null);

  const latitude = Number(application.latitude);
  const longitude = Number(application.longitude);
  const located = Number.isFinite(latitude) && Number.isFinite(longitude);

  const placement = (application.solar_placement ?? null) as SavedPlacement | null;

  // Module spec: what the applicant actually planned with, falling back to the
  // configured default when this application predates the planner.
  const spec: PanelSpec = useMemo(
    () => ({
      watts: placement?.panel_watts ?? DEFAULT_PANEL_SPEC.watts,
      widthM: placement?.panel_width_m ?? DEFAULT_PANEL_SPEC.widthM,
      lengthM: placement?.panel_length_m ?? DEFAULT_PANEL_SPEC.lengthM,
      gapM: DEFAULT_PANEL_SPEC.gapM,
    }),
    [placement]
  );

  const capacityKw = Number(application.new_pv_kw);
  const layout = useMemo(
    () => layoutFor(capacityKw, spec, placement?.tilt_deg ?? 0),
    [capacityKw, spec, placement]
  );

  const tiltDeg = placement?.tilt_deg ?? (located ? estimatedOptimalTilt(latitude) : 15);
  const azimuthDeg = placement?.azimuth_deg ?? (located ? optimalAzimuth(latitude) : 180);
  const mountHeightM = placement?.mount_height_m ?? 0.35;

  // Lit, so the roof and the array are actually visible.
  const when = useMemo(
    () => (located ? solarNoon(new Date(), latitude, longitude) : new Date()),
    [located, latitude, longitude]
  );

  // Mapped footprints around the site. Fetched through the backend so the
  // result is cached across viewers rather than each one querying Overpass.
  useEffect(() => {
    if (!located) return;
    let live = true;
    api
      .siteBuildings(latitude, longitude)
      .then((context) => {
        if (!live) return;
        setSiteBuildings(context.buildings);
        setContextNote(context.available ? null : (context.note ?? null));
      })
      .catch(() => {
        if (live) {
          setSiteBuildings([]);
          setContextNote("Building outlines could not be loaded for this site.");
        }
      });
    return () => {
      live = false;
    };
  }, [located, latitude, longitude]);

  const siteBuilding = useMemo(
    () => siteBuildings?.find((b) => b.is_site) ?? null,
    [siteBuildings]
  );

  const risk = (assessment?.engineering.engineering_risk ?? null) as Risk | null;
  const metrics = assessment?.metrics ?? null;

  if (!located) {
    return (
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-200">Rooftop digital twin</h2>
        <p className="mt-2 text-sm text-slate-400">
          This application has no site coordinates, so there is nowhere to place a
          twin. Coordinates are captured on the application form.
        </p>
      </div>
    );
  }

  const num = (v: number | null | undefined, digits: number, unit = "") =>
    v === null || v === undefined || !Number.isFinite(Number(v))
      ? "—"
      : `${Number(v).toFixed(digits)}${unit}`;

  return (
    <div className="card space-y-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">Rooftop digital twin</h2>
          <p className="mt-0.5 text-xs text-slate-500">
            The proposed array on the real site. Drag to rotate, scroll to zoom,
            right-drag or ctrl-drag to tilt.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {risk && (
            <span
              className={`flex items-center gap-1.5 rounded border px-2 py-1 text-xs ${RISK_STYLE[risk]}`}
            >
              <span className={`h-2 w-2 rounded-full ${RISK_DOT[risk]}`} />
              {risk}
            </span>
          )}
          <button
            onClick={() => setResetToken((n) => n + 1)}
            className="btn-ghost !px-3 !py-1.5 !text-xs"
          >
            Reset view
          </button>
          <button
            onClick={() => setPanelOpen((o) => !o)}
            className="btn-ghost !px-3 !py-1.5 !text-xs"
          >
            {panelOpen ? "Hide details" : "Show details"}
          </button>
        </div>
      </div>

      <div className="relative">
        <CesiumScene
          latitude={latitude}
          longitude={longitude}
          tiltDeg={tiltDeg}
          azimuthDeg={azimuthDeg}
          layout={layout}
          when={when}
          mountHeightM={mountHeightM}
          showShadows
          showBuildings
          riskLevel={risk}
          resetToken={resetToken}
          siteBuildings={siteBuildings}
          onSelectSite={() => setPanelOpen(true)}
          onSurface={setSurface}
          onShading={(_: ShadingSample) => undefined}
          onStatus={(next, detail) => {
            setStatus(next);
            setStatusDetail(detail ?? null);
          }}
        />

        {panelOpen && (
          <div className="pointer-events-auto absolute right-3 top-3 z-10 w-64 rounded-lg border border-slate-700 bg-slate-950/92 p-3 shadow-xl backdrop-blur">
            <div className="mb-2 flex items-center justify-between">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                Rooftop digital twin
              </div>
              <button
                onClick={() => setPanelOpen(false)}
                className="text-xs text-slate-500 hover:text-slate-300"
                aria-label="Close details"
              >
                ✕
              </button>
            </div>

            <div className="font-mono text-xs text-slate-300">
              {application.application_number}
            </div>
            <div className="mb-2 text-[11px] text-slate-500">
              {latitude.toFixed(5)}, {longitude.toFixed(5)}
            </div>

            <Row label="PV capacity" value={`${capacityKw.toFixed(1)} kW`} />
            <Row
              label="Panels"
              value={`${layout.panelCount} × ${spec.watts} W`}
            />
            <Row label="Modules deliver" value={`${layout.actualCapacityKw.toFixed(2)} kW`} />
            <Row label="Tilt / azimuth" value={`${Math.round(tiltDeg)}° / ${Math.round(azimuthDeg)}°`} />
            <Row
              label="Roof height"
              value={
                siteBuilding
                  ? `${siteBuilding.height_m.toFixed(1)} m${
                      siteBuilding.height_source === "assumed" ? " (assumed)" : ""
                    }`
                  : surface?.buildingHeightM != null && surface.onBuilding
                    ? `${surface.buildingHeightM.toFixed(1)} m`
                    : "—"
              }
            />
            <Row
              label="Roof footprint"
              value={siteBuilding ? `${siteBuilding.area_sqm.toFixed(0)} m²` : "—"}
            />

            <div className="mt-3 mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Grid assessment
            </div>
            <Row label="Risk" value={risk ?? "—"} />
            <Row label="Voltage" value={num(metrics?.pv_voltage_pu, 4, " pu")} />
            <Row label="Voltage rise" value={num(metrics?.voltage_rise_pu, 5, " pu")} />
            <Row
              label="Transformer"
              value={num(metrics?.max_transformer_loading_pct, 1, " %")}
            />
            <Row label="Line" value={num(metrics?.max_line_loading_pct, 1, " %")} />
            <Row
              label="Reverse flow"
              value={metrics ? (metrics.reverse_power_flow ? "Yes" : "No") : "—"}
            />

            <p className="mt-2 text-[10px] leading-relaxed text-slate-600">
              {assessment
                ? "Electrical values are from the backend power flow. The array is a drawing of the proposal."
                : "No assessment is on record, so no electrical values are shown."}
            </p>
          </div>
        )}

        {status !== "ready" && status !== "idle" && (
          <div className="pointer-events-none absolute left-3 top-3 z-10 rounded-md border border-slate-700 bg-slate-950/85 px-2.5 py-1 text-[11px] text-slate-300">
            {status === "loading-cesium" && "Loading the 3D engine…"}
            {status === "loading-terrain" && "Loading terrain…"}
            {status === "loading-buildings" && "Loading buildings…"}
            {status === "analysing" && "Locating the site…"}
            {status === "error" && (statusDetail ?? "The scene could not be loaded.")}
          </div>
        )}
      </div>

      {statusDetail && status === "ready" && (
        <p className="text-xs text-amber-400">{statusDetail}</p>
      )}

      {contextNote && (
        <p className="text-xs text-amber-400">
          {contextNote} The array is drawn on the terrain instead.
        </p>
      )}

      <p className="text-[11px] leading-relaxed text-slate-600">
        Building outlines are mapped footprints from OpenStreetMap, extruded to
        their mapped height where one exists and to an assumed height where none
        does — those are labelled. This is a model of the site, not a photograph
        of it.
      </p>
    </div>
  );
}
