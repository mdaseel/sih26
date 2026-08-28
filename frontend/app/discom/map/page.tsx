"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import { useEffect, useState } from "react";

import { GridMap } from "@/components/GridMap";
import { api, ApiError } from "@/lib/api";
import type { MapData } from "@/lib/types";

export default function DiscomMapPage() {
  const [data, setData] = useState<MapData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.map().then(setData).catch((e: ApiError) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Network map</h1>
        <p className="mt-1 text-sm text-slate-500">
          All connection points and every application on the feeder. Row Level
          Security shows a DISCOM account the full set.
        </p>
      </div>
      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
      {data ? <GridMap data={data} /> : !error && <p className="text-sm text-slate-500">Loading…</p>}
    </div>
  );
}
