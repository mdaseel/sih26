"use client";

import { useEffect, useMemo, useState } from "react";

import { VendorList } from "@/components/VendorList";
import { api, ApiError } from "@/lib/api";
import type { SolarApplication, VendorDiscovery } from "@/lib/types";

export default function CitizenVendorsPage() {
  const [apps, setApps] = useState<SolarApplication[]>([]);
  const [applicationId, setApplicationId] = useState<string>("");
  const [data, setData] = useState<VendorDiscovery | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .listApplications()
      .then(setApps)
      .catch(() => setApps([]));
  }, []);

  useEffect(() => {
    setBusy(true);
    const load = applicationId
      ? api.vendorsForApplication(applicationId)
      : api.vendors();
    load
      .then(setData)
      .catch((e: ApiError) => setError(e.message))
      .finally(() => setBusy(false));
  }, [applicationId]);

  const selected = useMemo(
    () => apps.find((a) => a.id === applicationId) ?? null,
    [apps, applicationId]
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Find an installer</h1>
        <p className="mt-1 text-sm text-slate-500">
          Solar installers verified by the DISCOM. Choose an application to sort by
          distance from that address.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {apps.length > 0 && (
        <div className="card">
          <label className="label">Sort by distance from</label>
          <select
            className="input"
            value={applicationId}
            onChange={(e) => setApplicationId(e.target.value)}
          >
            <option value="">All installers (no distance)</option>
            {apps.map((a) => (
              <option key={a.id} value={a.id}>
                {a.application_number} · Bus {a.pv_bus} · {Number(a.new_pv_kw).toFixed(1)} kW
              </option>
            ))}
          </select>

          {selected && data?.customer_location_known === false && (
            <p className="mt-2 text-xs text-amber-300">
              This application has no address coordinates, so installers cannot be
              sorted by distance.
            </p>
          )}
        </div>
      )}

      {busy && !data && <p className="text-sm text-slate-500">Loading installers…</p>}
      {data && <VendorList data={data} />}
    </div>
  );
}
