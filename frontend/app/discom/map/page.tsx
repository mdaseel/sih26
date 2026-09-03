"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import { useEffect, useState } from "react";

import { GridMap } from "@/components/GridMap";
import { SolarPlanner } from "@/components/solar3d/SolarPlanner";
import { DigitalTwinView } from "@/components/twin/DigitalTwinView";
import { api, ApiError } from "@/lib/api";
import type { MapData, TwinResponse } from "@/lib/types";

export default function DiscomMapPage() {
  const [data, setData] = useState<MapData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mapMode, setMapMode] = useState<"2D" | "3D">("2D");
  const [twin, setTwin] = useState<TwinResponse | null>(null);
  const [busId, setBusId] = useState("734");

  useEffect(() => {
    api.map().then(setData).catch((e: ApiError) => setError(e.message));
  }, []);

  useEffect(() => {
    if (mapMode === "3D" && !twin) {
      api.twin({ pv_bus: busId, existing_pv_kw: 0, new_pv_kw: 25 }).then(setTwin).catch(() => {});
    }
  }, [mapMode, twin, busId]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Network map</h1>
          <p className="mt-1 text-sm text-slate-500">
            All connection points and every application on the feeder with 3D digital twin visualization.
          </p>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 p-0.5">
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
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {data ? (
        mapMode === "2D" ? (
          <GridMap data={data} />
        ) : (
          <div className="space-y-6">
            <DigitalTwinView
              twin={twin}
              busId={busId}
              onSelectBus={(b) => {
                setBusId(b);
                api.twin({ pv_bus: b, existing_pv_kw: 0, new_pv_kw: 25 }).then(setTwin).catch(() => {});
              }}
              title="Feeder 3D Digital Twin"
              subtitle="Interactive 3D network topology & power flow schematic"
            />
            <div className="card space-y-4">
              <h2 className="text-sm font-semibold text-slate-200">
                Rooftop 3D Solar Assessment
              </h2>
              <SolarPlanner
                latitude={18.5204}
                longitude={73.8567}
                initialCapacityKw={5}
                pvBus={busId}
                roofAreaSqm={75}
              />
            </div>
          </div>
        )
      ) : (
        !error && <p className="text-sm text-slate-500">Loading…</p>
      )}
    </div>
  );
}
