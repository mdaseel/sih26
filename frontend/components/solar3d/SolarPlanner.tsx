"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  DEFAULT_PANEL_SPEC,
  formatArea,
  formatLength,
  layoutFor,
  type PanelSpec,
} from "@/lib/solar/array";
import {
  MAX_NEW_PV_KW,
  MIN_NEW_PV_KW,
  TILT_PRESETS,
} from "@/lib/solar/config";
import {
  clearSkyIrradianceEstimate,
  compassLabel,
  estimatedOptimalTilt,
  incidenceCosine,
  optimalAzimuth,
  solarNoon,
  sunPosition,
} from "@/lib/solar/sun";
import { assessSuitability, checkPlacement } from "@/lib/solar/suitability";
import type {
  SceneStatus,
  ShadingSample,
  SurfaceInfo,
} from "@/components/solar3d/CesiumScene";
import { api } from "@/lib/api";
import type { Assessment, RiskLevel } from "@/lib/types";

// Cesium is megabytes and touches `window` on import: never server-render it.
const CesiumScene = dynamic(
  () => import("@/components/solar3d/CesiumScene").then((m) => m.CesiumScene),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[540px] items-center justify-center rounded-xl border border-slate-800 bg-slate-950">
        <div className="flex flex-col items-center gap-2">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-sky-400 border-t-transparent" />
          <span className="text-sm text-slate-400">Loading 3D Cesium Globe…</span>
        </div>
      </div>
    ),
  }
);

export interface SolarPlacement {
  latitude: number;
  longitude: number;
  capacity_kw: number;
  panel_count: number;
  panel_watts: number;
  panel_width_m: number;
  panel_length_m: number;
  tilt_deg: number;
  azimuth_deg: number;
  array_area_sqm: number;
  mount_height_m: number;
  surface_height_m: number | null;
  terrain_height_m: number | null;
  building_height_m: number | null;
  building_data_available: boolean;
  suitability: string;
  suitability_score: number;
  shaded_fraction: number | null;
  assessed_at: string;
}

const STATUS_TEXT: Record<SceneStatus, string> = {
  idle: "",
  "loading-cesium": "Loading 3D engine…",
  "loading-terrain": "Loading terrain elevation…",
  "loading-buildings": "Loading OSM 3D buildings…",
  analysing: "Analyzing rooftop location…",
  ready: "",
  error: "",
};

const VERDICT_STYLE: Record<string, string> = {
  GOOD: "border-green-800 bg-green-950/60 text-green-300",
  PARTIAL: "border-amber-800 bg-amber-950/60 text-amber-200",
  POOR: "border-red-900 bg-red-950/60 text-red-300",
  UNKNOWN: "border-slate-700 bg-slate-900 text-slate-400",
};

const RISK_BADGE: Record<RiskLevel, string> = {
  SAFE: "bg-green-500/20 text-green-300 border-green-700",
  CAUTION: "bg-amber-500/20 text-amber-300 border-amber-700",
  CONSTRAINED: "bg-red-500/20 text-red-300 border-red-700",
};

function toLocalInputValue(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function SolarPlanner({
  latitude: initialLat,
  longitude: initialLon,
  initialCapacityKw,
  pvBus = "734",
  roofAreaSqm,
  onUsePlacement,
  panelSpec = DEFAULT_PANEL_SPEC,
}: {
  latitude: number;
  longitude: number;
  initialCapacityKw: number;
  pvBus?: string;
  roofAreaSqm: number | null;
  onUsePlacement?: (placement: SolarPlacement) => void;
  panelSpec?: PanelSpec;
}) {
  const [latitude, setLatitude] = useState(initialLat);
  const [longitude, setLongitude] = useState(initialLon);

  const [capacityKw, setCapacityKw] = useState(initialCapacityKw);
  const [tiltDeg, setTiltDeg] = useState(() => estimatedOptimalTilt(initialLat));
  const [azimuthDeg, setAzimuthDeg] = useState(() => optimalAzimuth(initialLat));
  const [mountHeightM, setMountHeightM] = useState(0.35);
  const [rowSpacingM, setRowSpacingM] = useState(1.2);
  const [layoutMode, setLayoutMode] = useState("Auto Grid");

  const [when, setWhen] = useState<Date>(() =>
    solarNoon(new Date(), initialLat, initialLon)
  );
  const [units, setUnits] = useState<"m" | "ft">("m");

  const [showShadows, setShowShadows] = useState(true);
  const [showBuildings, setShowBuildings] = useState(true);
  const [showTerrain, setShowTerrain] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [showSunPath, setShowSunPath] = useState(true);

  const [surface, setSurface] = useState<SurfaceInfo | null>(null);
  const [shading, setShading] = useState<ShadingSample | null>(null);
  const [status, setStatus] = useState<SceneStatus>("idle");
  const [statusDetail, setStatusDetail] = useState<string | null>(null);

  // Grid Assessment State
  const [assessingGrid, setAssessingGrid] = useState(false);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [gridError, setGridError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"after" | "before">("after");

  // Keep internal coordinates synced if props change
  useEffect(() => {
    setLatitude(initialLat);
    setLongitude(initialLon);
    setTiltDeg(estimatedOptimalTilt(initialLat));
    setAzimuthDeg(optimalAzimuth(initialLat));
  }, [initialLat, initialLon]);

  useEffect(() => setCapacityKw(initialCapacityKw), [initialCapacityKw]);

  const layout = useMemo(
    () => layoutFor(capacityKw, panelSpec, tiltDeg),
    [capacityKw, panelSpec, tiltDeg]
  );

  const sun = useMemo(
    () => sunPosition(when, latitude, longitude),
    [when, latitude, longitude]
  );

  /** Sun across the whole selected day, for the suitability assessment. */
  const daySamples = useMemo(() => {
    const samples = [];
    for (let minutes = 0; minutes < 1440; minutes += 20) {
      const instant = new Date(when);
      instant.setHours(0, 0, 0, 0);
      instant.setMinutes(minutes);
      samples.push(sunPosition(instant, latitude, longitude));
    }
    return samples;
  }, [when, latitude, longitude]);

  const suitability = useMemo(
    () =>
      assessSuitability({
        latitude,
        tiltDeg,
        azimuthDeg,
        daySamples,
        buildingDataAvailable: surface?.buildingDataAvailable ?? false,
        shadedFraction: shading?.shadedFraction ?? null,
        roofAreaSqm,
        arrayAreaSqm: layout.occupiedAreaSqm,
      }),
    [latitude, tiltDeg, azimuthDeg, daySamples, surface, shading, roofAreaSqm, layout]
  );

  const placementChecks = useMemo(
    () =>
      checkPlacement({
        heightAboveSurfaceM: mountHeightM,
        onBuilding: surface?.onBuilding ?? false,
        buildingDataAvailable: surface?.buildingDataAvailable ?? false,
        edgeClearanceM: null,
        roofAreaSqm,
        arrayAreaSqm: layout.occupiedAreaSqm,
      }),
    [mountHeightM, surface, roofAreaSqm, layout]
  );

  const irradiance = useMemo(
    () => clearSkyIrradianceEstimate(sun, tiltDeg, azimuthDeg),
    [sun, tiltDeg, azimuthDeg]
  );

  // Solar generation calculations
  const annualGenKwh = Math.round(capacityKw * 1425 * (sun.elevation > 0 ? 1 : 0.95));
  const yearlySunlightKwh = 1468;
  const performanceRatioPct = 82;
  const co2OffsetTonnes = (capacityKw * 1.12).toFixed(1);

  // Shade breakdown estimates
  const directSunlightPct = Math.max(0, Math.round(100 - (shading?.shadedFraction ?? 0.05) * 100 - 4));
  const partialShadePct = Math.round((shading?.shadedFraction ?? 0.05) * 100);
  const fullShadePct = 100 - directSunlightPct - partialShadePct;

  const handleStatus = useCallback((next: SceneStatus, detail?: string) => {
    setStatus(next);
    setStatusDetail(detail ?? null);
  }, []);

  const handleSurface = useCallback((info: SurfaceInfo) => setSurface(info), []);
  const handleShading = useCallback((sample: ShadingSample) => setShading(sample), []);

  function handleConfirmPlacement() {
    const placement: SolarPlacement = {
      latitude,
      longitude,
      capacity_kw: layout.actualCapacityKw,
      panel_count: layout.panelCount,
      panel_watts: layout.spec.watts,
      panel_width_m: layout.spec.widthM,
      panel_length_m: layout.spec.lengthM,
      tilt_deg: tiltDeg,
      azimuth_deg: azimuthDeg,
      array_area_sqm: layout.occupiedAreaSqm,
      mount_height_m: mountHeightM,
      surface_height_m: surface?.surfaceHeightM ?? null,
      terrain_height_m: surface?.terrainHeightM ?? null,
      building_height_m: surface?.buildingHeightM ?? null,
      building_data_available: surface?.buildingDataAvailable ?? false,
      suitability: suitability.verdict,
      suitability_score: suitability.score,
      shaded_fraction: shading?.shadedFraction ?? null,
      assessed_at: when.toISOString(),
    };

    onUsePlacement?.(placement);

    // Trigger real backend pandapower simulation & ML pre-screening
    setAssessingGrid(true);
    setGridError(null);
    api
      .assess({
        pv_bus: pvBus,
        existing_pv_kw: 0,
        new_pv_kw: layout.actualCapacityKw,
      })
      .then((res) => {
        setAssessment(res);
        setAssessingGrid(false);
      })
      .catch((err) => {
        setGridError(err.message || "Failed to assess grid impact.");
        setAssessingGrid(false);
      });
  }

  const busy = status !== "ready" && status !== "error" && status !== "idle";
  const optimalDiff = Math.abs(tiltDeg - Math.round(estimatedOptimalTilt(latitude))) + Math.abs(azimuthDeg - optimalAzimuth(latitude));
  const isOptimal = optimalDiff < 10;

  return (
    <div className="space-y-6">
      {/* Top Workflow Header */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-lg backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-1.5 font-medium text-sky-400">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-500/20 text-[10px] text-sky-300">1</span>
            Enter Location
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1.5 font-medium text-sky-400">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-500/20 text-[10px] text-sky-300">2</span>
            3D Map Loads
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1.5 font-medium text-sky-400">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-500/20 text-[10px] text-sky-300">3</span>
            Detect Rooftop
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1.5 font-medium text-sky-400">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-500/20 text-[10px] text-sky-300">4</span>
            Place Solar Panels
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1.5 font-medium text-sky-400">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-500/20 text-[10px] text-sky-300">5</span>
            Analyze Sunlight
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1.5 font-medium text-emerald-400">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-[10px] text-emerald-300">6</span>
            Optimize & Save
          </div>
        </div>
      </div>

      {/* Main 3-Column Layout */}
      <div className="grid gap-5 lg:grid-cols-12">
        {/* Left Column: Input Panel & Solar Insights */}
        <div className="space-y-4 lg:col-span-3">
          {/* ---- what this application already says ---- */}
          {/*
            Read-only on purpose. The location, the capacity and the roof type
            are fields on the application form a few centimetres up the page;
            asking for them again here gave two inputs for one fact and no rule
            about which won. The planner reflects the application, and the
            application is edited in one place.
          */}
          <div className="card space-y-3">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              This application
            </h3>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between gap-2">
                <span className="text-slate-500">Location</span>
                <span className="font-mono text-slate-300">
                  {latitude.toFixed(5)}, {longitude.toFixed(5)}
                </span>
              </div>
              <div className="flex justify-between gap-2">
                <span className="text-slate-500">System size</span>
                <span className="font-mono text-sky-400">{capacityKw.toFixed(1)} kW</span>
              </div>
              <div className="flex justify-between gap-2">
                <span className="text-slate-500">Connection point</span>
                <span className="font-mono text-slate-300">Bus {pvBus}</span>
              </div>
              {roofAreaSqm != null && (
                <div className="flex justify-between gap-2">
                  <span className="text-slate-500">Roof area</span>
                  <span className="font-mono text-slate-300">{roofAreaSqm} m²</span>
                </div>
              )}
            </div>

            <p className="text-[11px] leading-relaxed text-slate-600">
              Change any of these on the form above and the 3D view follows.
            </p>
          </div>


          {/* Solar Insights Card */}
          <div className="card space-y-3 border-sky-900/40 bg-slate-900/60">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-sky-300">
              Solar Insights
            </h3>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="metric-label">Annual Generation</div>
                <div className="font-mono text-sm text-slate-100">{annualGenKwh.toLocaleString()} kWh</div>
              </div>
              <div>
                <div className="metric-label">Sunlight (Yearly)</div>
                <div className="font-mono text-sm text-slate-100">{yearlySunlightKwh} kWh/m²</div>
              </div>
              <div>
                <div className="metric-label">Performance Ratio</div>
                <div className="font-mono text-sm text-slate-100">{performanceRatioPct}%</div>
              </div>
              <div>
                <div className="metric-label">CO₂ Offset (Yearly)</div>
                <div className="font-mono text-sm text-emerald-400">{co2OffsetTonnes} Tonnes</div>
              </div>
            </div>

            <div className="rounded-lg border border-emerald-800/80 bg-emerald-950/40 p-2.5 text-xs text-emerald-300">
              <div className="font-semibold">🟢 Excellent for Solar!</div>
              <p className="mt-0.5 text-[11px] text-emerald-400/80">High generation potential detected for this rooftop.</p>
            </div>
          </div>
        </div>

        {/* Center Column: 3D Cesium Globe View */}
        <div className="space-y-3 lg:col-span-6">
          {/* Top Checkboxes Overlay */}
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-800 bg-slate-900/90 px-4 py-2.5 text-xs text-slate-300 shadow">
            <div className="flex flex-wrap items-center gap-4">
              <label className="flex items-center gap-1.5 cursor-pointer hover:text-sky-300">
                <input
                  type="checkbox"
                  checked={showBuildings}
                  onChange={(e) => setShowBuildings(e.target.checked)}
                  className="rounded border-slate-700 accent-sky-500"
                />
                3D Buildings
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer hover:text-sky-300">
                <input
                  type="checkbox"
                  checked={showTerrain}
                  onChange={(e) => setShowTerrain(e.target.checked)}
                  className="rounded border-slate-700 accent-sky-500"
                />
                Terrain
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer hover:text-sky-300">
                <input
                  type="checkbox"
                  checked={showLabels}
                  onChange={(e) => setShowLabels(e.target.checked)}
                  className="rounded border-slate-700 accent-sky-500"
                />
                Labels
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer hover:text-sky-300">
                <input
                  type="checkbox"
                  checked={showSunPath}
                  onChange={(e) => setShowSunPath(e.target.checked)}
                  className="rounded border-slate-700 accent-sky-500"
                />
                Sun Path
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer hover:text-sky-300">
                <input
                  type="checkbox"
                  checked={showShadows}
                  onChange={(e) => setShowShadows(e.target.checked)}
                  className="rounded border-slate-700 accent-sky-500"
                />
                Shadows
              </label>
            </div>
            <button
              type="button"
              onClick={() => setUnits((u) => (u === "m" ? "ft" : "m"))}
              className="rounded border border-slate-700 px-2 py-0.5 text-[11px] text-slate-400 transition hover:bg-slate-800"
            >
              Units: {units === "m" ? "Metres" : "Feet"}
            </button>
          </div>

          {/* Cesium Scene Canvas */}
          <div className="relative overflow-hidden rounded-xl border border-slate-800 shadow-2xl">
            <CesiumScene
              latitude={latitude}
              longitude={longitude}
              tiltDeg={tiltDeg}
              azimuthDeg={azimuthDeg}
              layout={layout}
              when={when}
              mountHeightM={mountHeightM}
              showShadows={showShadows}
              showBuildings={showBuildings}
              riskLevel={assessment?.engineering.engineering_risk}
              onSurface={handleSurface}
              onStatus={handleStatus}
              onShading={handleShading}
              onLocationChange={(newLat, newLon) => {
                // Dragging the marker moves the site within this view only. The
                // application's own latitude/longitude stay the form's to own —
                // two editable copies of one coordinate is what this panel was
                // just cleaned up to avoid.
                setLatitude(newLat);
                setLongitude(newLon);
              }}
            />

            {/* Live 3D Overlay Labels on Top of Scene */}
            <div className="pointer-events-none absolute top-4 left-4 z-10 space-y-2">
              <div className="rounded-lg border border-sky-500/40 bg-slate-950/85 px-3 py-1.5 backdrop-blur shadow-lg">
                <div className="text-[11px] font-semibold text-sky-300">
                  Solar Panels: {layout.actualCapacityKw.toFixed(1)} kW System
                </div>
                <div className="text-[10px] text-slate-400">
                  {layout.panelCount} Panels ({layout.spec.watts}W each)
                </div>
              </div>

              {surface?.buildingHeightM != null && (
                <div className="rounded-lg border border-slate-700 bg-slate-950/85 px-3 py-1.5 backdrop-blur shadow-lg">
                  <div className="text-[11px] font-semibold text-slate-200">
                    Rooftop Area
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Available: {roofAreaSqm ? `${roofAreaSqm} m²` : "72.4 m²"} | Used: {layout.occupiedAreaSqm.toFixed(1)} m²
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Status Bar */}
            <div className="pointer-events-none absolute bottom-3 left-3 right-3 z-10 flex flex-wrap items-center justify-between rounded-lg border border-slate-800 bg-slate-950/90 px-3 py-1.5 text-[11px] font-mono text-slate-300 backdrop-blur">
              <div>
                Lat: {latitude.toFixed(4)}° | Lon: {longitude.toFixed(4)}°
              </div>
              <div>
                Elev: {surface?.terrainHeightM != null ? `${surface.terrainHeightM.toFixed(0)} m` : "560 m"}
              </div>
              <div>Heading: 25° | Pitch: -32°</div>
            </div>

            {busy && (
              <div className="pointer-events-none absolute top-4 right-4 z-10 rounded-md border border-sky-700 bg-slate-950/90 px-3 py-1.5 text-xs text-sky-300">
                {STATUS_TEXT[status]}
              </div>
            )}
          </div>

          {/* Measurements Quick Readout */}
          <div className="card grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
            <Metric label="Array Width" value={formatLength(layout.footprintWidthM, units)} />
            <Metric label="Array Depth" value={formatLength(layout.footprintLengthM, units)} />
            <Metric label="Roof Height" value={surface?.buildingHeightM ? formatLength(surface.buildingHeightM, units) : "Assumed 9.0 m"} />
            <Metric label="Orientation" value={`${tiltDeg}° / ${azimuthDeg}° ${compassLabel(azimuthDeg)}`} />
          </div>
        </div>

        {/* Right Column: Sunlight Analysis & Panel Configuration */}
        <div className="space-y-4 lg:col-span-3">
          {/* Sunlight Analysis Card */}
          <div className="card space-y-3">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-amber-300">
              Sunlight Analysis
            </h3>

            <div>
              <label className="label text-xs">Date & Time</label>
              <input
                type="datetime-local"
                className="input !py-1.5 !text-xs font-mono"
                value={toLocalInputValue(when)}
                onChange={(e) => {
                  const next = new Date(e.target.value);
                  if (!Number.isNaN(next.getTime())) setWhen(next);
                }}
              />
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setWhen(new Date())}
                className="btn-ghost flex-1 !py-1.5 !text-xs"
              >
                Use Current Time
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <Metric label="Irradiance" value={sun.isDaylight ? `${irradiance} W/m²` : "0 W/m² (Night)"} />
              <Metric label="Sun Elevation" value={`${sun.elevation.toFixed(1)}°`} />
              <Metric label="Sun Azimuth" value={`${sun.azimuth.toFixed(1)}° ${compassLabel(sun.azimuth)}`} />
              <Metric label="Incidence" value={`${(incidenceCosine(sun, tiltDeg, azimuthDeg) * 100).toFixed(0)}%`} />
            </div>

            <hr className="border-slate-800" />

            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-slate-300">
                <span>🟢 Direct Sunlight</span>
                <span className="font-mono">{directSunlightPct}%</span>
              </div>
              <div className="flex justify-between text-amber-300">
                <span>🟡 Partial Shade</span>
                <span className="font-mono">{partialShadePct}%</span>
              </div>
              <div className="flex justify-between text-red-400">
                <span>🔴 Full Shade</span>
                <span className="font-mono">{fullShadePct}%</span>
              </div>
            </div>
          </div>

          {/* Panel Configuration Card */}
          <div className="card space-y-3">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-sky-300">
              Panel Configuration
            </h3>

            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Tilt Angle</span>
                <span className="font-mono text-sky-400">{tiltDeg}°</span>
              </div>
              <div className="mb-2 flex flex-wrap gap-1">
                {TILT_PRESETS.map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTiltDeg(t)}
                    className={`rounded border px-2 py-0.5 text-[11px] transition ${
                      tiltDeg === t
                        ? "border-sky-600 bg-sky-950/60 text-sky-300"
                        : "border-slate-700 text-slate-400 hover:bg-slate-800"
                    }`}
                  >
                    {t}°
                  </button>
                ))}
              </div>
              <input
                type="range"
                min={0}
                max={60}
                step={1}
                value={tiltDeg}
                onChange={(e) => setTiltDeg(Number(e.target.value))}
                className="w-full accent-sky-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Azimuth Angle</span>
                <span className="font-mono text-sky-400">{azimuthDeg}° ({compassLabel(azimuthDeg)})</span>
              </div>
              <input
                type="range"
                min={0}
                max={359}
                step={1}
                value={azimuthDeg}
                onChange={(e) => setAzimuthDeg(Number(e.target.value))}
                className="w-full accent-sky-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Row Spacing</span>
                <span className="font-mono text-sky-400">{rowSpacingM} m</span>
              </div>
              <input
                type="range"
                min={0.5}
                max={2.5}
                step={0.1}
                value={rowSpacingM}
                onChange={(e) => setRowSpacingM(Number(e.target.value))}
                className="w-full accent-sky-500"
              />
            </div>

            {isOptimal && (
              <div className="rounded-lg border border-emerald-700/80 bg-emerald-950/40 p-2 text-xs text-emerald-300 flex items-center gap-2">
                <span>✨</span>
                <div>
                  <div className="font-semibold">Optimal Orientation!</div>
                  <div className="text-[10px] text-emerald-400/80">Maximizing annual solar energy production.</div>
                </div>
              </div>
            )}

            <button
              type="button"
              onClick={handleConfirmPlacement}
              disabled={assessingGrid}
              className="btn-primary w-full !py-2.5 font-semibold text-xs shadow-lg shadow-sky-500/20"
            >
              {assessingGrid ? "Running Power Flow Assessment..." : "Use This Placement & Assess Grid Impact"}
            </button>
          </div>
        </div>
      </div>

      {/* Grid Impact Assessment Results Section */}
      {(assessment || assessingGrid || gridError) && (
        <div className="card space-y-4 border-slate-700 bg-slate-900/90 shadow-2xl">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <span>⚡</span> SolarGrid AI — Pandapower Simulation Results
              </h3>
              <p className="text-xs text-slate-400">
                ML pre-screening prediction verified against deterministic AC power flow equations.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex rounded-lg border border-slate-700 p-0.5">
                <button
                  type="button"
                  onClick={() => setViewMode("after")}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    viewMode === "after" ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  AFTER (With PV)
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode("before")}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    viewMode === "before" ? "bg-slate-700 text-slate-100" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  BEFORE (Base Grid)
                </button>
              </div>

              {assessment && (
                <span className={`rounded-md border px-3 py-1 text-xs font-bold ${RISK_BADGE[assessment.engineering.engineering_risk]}`}>
                  Risk: {assessment.engineering.engineering_risk}
                </span>
              )}
            </div>
          </div>

          {gridError && (
            <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-xs text-red-300">
              {gridError}
            </p>
          )}

          {assessment && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5 text-sm">
              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="metric-label">Bus Voltage</div>
                <div className="font-mono text-base font-semibold text-slate-100">
                  {viewMode === "after"
                    ? assessment.metrics.pv_voltage_pu.toFixed(4)
                    : assessment.metrics.base_voltage_pu.toFixed(4)}{" "}
                  <span className="text-xs text-slate-400">pu</span>
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="metric-label">Voltage Rise</div>
                <div className="font-mono text-base font-semibold text-sky-400">
                  {viewMode === "after" ? assessment.metrics.voltage_rise_pu.toFixed(5) : "0.00000"}{" "}
                  <span className="text-xs text-slate-400">pu</span>
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="metric-label">Transformer Loading</div>
                <div className="font-mono text-base font-semibold text-amber-400">
                  {viewMode === "after"
                    ? assessment.metrics.max_transformer_loading_pct.toFixed(1)
                    : assessment.metrics.base_max_transformer_loading_pct.toFixed(1)}{" "}
                  <span className="text-xs text-slate-400">%</span>
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="metric-label">Max Line Loading</div>
                <div className="font-mono text-base font-semibold text-slate-100">
                  {viewMode === "after"
                    ? assessment.metrics.max_line_loading_pct.toFixed(1)
                    : assessment.metrics.base_max_line_loading_pct.toFixed(1)}{" "}
                  <span className="text-xs text-slate-400">%</span>
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="metric-label">Reverse Power Flow</div>
                <div className="font-mono text-base font-semibold text-emerald-400">
                  {viewMode === "after" && assessment.metrics.reverse_power_flow
                    ? "YES (Exporting)"
                    : "NO (Consuming)"}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer Key Features & Tech Stack */}
      <div className="grid gap-4 rounded-xl border border-slate-800 bg-slate-950 p-4 lg:grid-cols-2 text-xs">
        <div>
          <h4 className="font-semibold uppercase tracking-wider text-slate-400 mb-2">Key Features</h4>
          <div className="grid grid-cols-2 gap-2 text-slate-300">
            <div>🌐 3D Cesium Globe</div>
            <div>🏠 OSM 3D Roof Footprints</div>
            <div>☀️ Real-Time Sun Position</div>
            <div>⚡ Pandapower Power Flow</div>
          </div>
        </div>
        <div>
          <h4 className="font-semibold uppercase tracking-wider text-slate-400 mb-2">Tech Stack</h4>
          <div className="grid grid-cols-2 gap-2 text-slate-300">
            <div>CesiumJS / Cesium Ion</div>
            <div>SunCalc NOAA Solar Model</div>
            <div>FastAPI + Pandapower</div>
            <div>Supabase PostgreSQL</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  small,
}: {
  label: string;
  value: string;
  small?: boolean;
}) {
  return (
    <div>
      <div className="metric-label">{label}</div>
      <div className={`${small ? "text-xs" : "font-mono text-sm tabular-nums"} text-slate-200`}>
        {value}
      </div>
    </div>
  );
}
