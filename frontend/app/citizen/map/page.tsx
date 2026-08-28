"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import { useEffect, useMemo, useState } from "react";

import { GridMap } from "@/components/GridMap";
import { api, ApiError } from "@/lib/api";
import type { MapData } from "@/lib/types";

export default function MapPage() {
  const [data, setData] = useState<MapData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .map()
      .then(setData)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const stats = useMemo(() => {
    if (!data) return null;
    const buses = data.assets.filter((a) => a.asset_type === "BUS" && a.pv_eligible);
    const caps = buses
      .map((b) => (b.attributes as Record<string, number>)?.hosting_capacity_kw)
      .filter((v): v is number => typeof v === "number");
    const pending = Object.values(data.pending_pv_by_bus).reduce((s, v) => s + v, 0);
    return {
      connectionPoints: buses.length,
      applications: data.applications.length,
      pendingKw: pending,
      medianCapacity: caps.length ? caps.slice().sort((a, b) => a - b)[Math.floor(caps.length / 2)] : null,
    };
  }, [data]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Network map</h1>
        <p className="mt-1 text-sm text-slate-500">
          Connection points, feeder assets and applications, coloured by the layer
          you choose.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {stats && (
        <div className="grid gap-4 sm:grid-cols-4">
          <div className="card">
            <div className="metric-label">Connection points</div>
            <div className="metric-value">{stats.connectionPoints}</div>
          </div>
          <div className="card">
            <div className="metric-label">Applications shown</div>
            <div className="metric-value">{stats.applications}</div>
          </div>
          <div className="card">
            <div className="metric-label">Pending solar</div>
            <div className="metric-value">
              {stats.pendingKw.toFixed(1)}
              <span className="ml-1 text-xs text-slate-500">kW</span>
            </div>
          </div>
          <div className="card">
            <div className="metric-label">Median hosting capacity</div>
            <div className="metric-value">
              {stats.medianCapacity?.toFixed(0) ?? "—"}
              <span className="ml-1 text-xs text-slate-500">kW</span>
            </div>
          </div>
        </div>
      )}

      {data ? (
        <GridMap data={data} />
      ) : (
        !error && <p className="text-sm text-slate-500">Loading the network…</p>
      )}
    </div>
  );
}
