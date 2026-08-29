"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { VendorMap } from "@/components/VendorMap";
import { SolarPlanner } from "@/components/solar3d/SolarPlanner";
import { api, ApiError } from "@/lib/api";
import type { CitizenMapData } from "@/lib/types";

/**
 * The citizen's map.
 *
 * Rebuilt around the question a householder actually has — who can install
 * this, and how far away are they — rather than the DISCOM's. Buses,
 * transformers, line loadings and hosting capacity are gone from this view;
 * they remain in full on the DISCOM map, which is where someone reads them for
 * a living.
 */
export default function MapPage() {
  const [data, setData] = useState<CitizenMapData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mapMode, setMapMode] = useState<"2D" | "3D">("2D");

  useEffect(() => {
    api
      .citizenMap()
      .then(setData)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const stats = useMemo(() => {
    if (!data) return null;
    const engaged = data.vendors.filter((v) => v.engaged);
    const nearest = data.routes.reduce<number | null>(
      (best, r) => (best === null || r.distance_km < best ? r.distance_km : best),
      null
    );
    return {
      sites: data.located_applications,
      vendors: data.vendors.length,
      engaged: engaged.length,
      nearest,
    };
  }, [data]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Installers near you</h1>
          <p className="mt-1 text-sm text-slate-500">
            Your sites, the installers the DISCOM has verified, and 3D rooftop solar planning.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-slate-700 p-0.5 bg-slate-900">
            <button
              type="button"
              onClick={() => setMapMode("2D")}
              className={`rounded-md px-3 py-1.5 text-xs font-semibold transition ${
                mapMode === "2D" ? "bg-sky-600 text-white shadow" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              2D MAP
            </button>
            <button
              type="button"
              onClick={() => setMapMode("3D")}
              className={`rounded-md px-3 py-1.5 text-xs font-semibold transition ${
                mapMode === "3D" ? "bg-sky-600 text-white shadow" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              3D TWIN
            </button>
          </div>
          <Link href="/citizen/vendors" className="btn-ghost">
            Browse installers
          </Link>
        </div>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card">
            <div className="metric-label">Your sites on the map</div>
            <div className="metric-value">{stats.sites}</div>
          </div>
          <div className="card">
            <div className="metric-label">Verified installers</div>
            <div className="metric-value">{stats.vendors}</div>
          </div>
          <div className="card">
            <div className="metric-label">Working with you</div>
            <div className="metric-value">{stats.engaged}</div>
          </div>
          <div className="card">
            <div className="metric-label">
              {data?.routing.returns_real_routes ? "Nearest by road" : "Nearest, straight line"}
            </div>
            <div className="metric-value">
              {stats.nearest != null ? stats.nearest.toFixed(1) : "—"}
              <span className="ml-1 text-xs text-slate-500">km</span>
            </div>
          </div>
        </div>
      )}

      {data ? (
        mapMode === "2D" ? (
          <VendorMap data={data} />
        ) : (
          <div className="card space-y-4">
            <h2 className="text-sm font-semibold text-slate-200">
              3D Digital Twin & Rooftop Solar Planning
            </h2>
            <SolarPlanner
              latitude={18.5204}
              longitude={73.8567}
              initialCapacityKw={5}
              pvBus="734"
              roofAreaSqm={75}
            />
          </div>
        )
      ) : (
        !error && <p className="text-sm text-slate-500">Loading the map…</p>
      )}

      {data && data.applications.length > data.located_applications && (
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-200">
            Applications not on the map
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            These have no coordinates recorded, so they cannot be placed and no installer
            can be measured from them.
          </p>
          <ul className="scroll-pane mt-3 max-h-56 space-y-2">
            {data.applications
              .filter((a) => a.latitude == null || a.longitude == null)
              .map((a) => (
                <li key={a.id}>
                  <Link
                    href={`/citizen/applications/${a.id}`}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-800 bg-slate-950/40 px-3 py-2 text-sm transition hover:border-slate-700"
                  >
                    <span className="font-mono text-slate-300">{a.application_number}</span>
                    <span className="text-xs text-slate-500">
                      {[a.address_line, a.district].filter(Boolean).join(", ") ||
                        "No address"}
                    </span>
                  </Link>
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
}
