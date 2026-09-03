"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import { useEffect, useState } from "react";
import Link from "next/link";

import { VendorMap } from "@/components/VendorMap";
import { vendorApi, ApiError } from "@/lib/api";
import type { CitizenMapData } from "@/lib/types";

export default function VendorMapPage() {
  const [data, setData] = useState<CitizenMapData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Vendor sees same citizen map data (their coverage area) — reuse citizen endpoint via vendor summary routes
    // Fallback to citizen map if vendor-specific not available
    vendorApi
      .summary()
      .then(async () => {
        // fetch citizen map as proxy — backend serves same geo for vendors via /citizen/map
        const { api } = await import("@/lib/api");
        return api.citizenMap();
      })
      .then(setData)
      .catch(async (e: ApiError) => {
        // try direct citizen map
        try {
          const { api } = await import("@/lib/api");
          const d = await api.citizenMap();
          setData(d);
        } catch (err) {
          setError((err as ApiError).message ?? e.message);
        }
      });
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Your territory — 3D map</h1>
          <p className="mt-1 text-sm text-slate-500">
            Sites that requested you, nearby verified coverage, and 3D building context for roof assessment.
          </p>
        </div>
        <Link href="/vendor/leads" className="btn-ghost">
          Back to leads
        </Link>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">{error}</p>
      )}

      {data ? <VendorMap data={data} /> : !error && <p className="text-sm text-slate-500">Loading 3D map…</p>}
    </div>
  );
}
