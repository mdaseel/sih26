"use client";

import { useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import type { VendorProject } from "@/lib/types";

export default function VendorProjects() {
  const [rows, setRows] = useState<VendorProject[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    vendorApi
      .projects()
      .then(setRows)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Projects</h1>
        <p className="mt-1 text-sm text-slate-500">
          Every application you are engaged on, with its appointments and installation
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
      {rows === null && !error && <p className="text-sm text-slate-500">Loading…</p>}
      {rows?.length === 0 && (
        <div className="card text-sm text-slate-500">
          No projects yet. Accepting a lead starts one.
        </div>
      )}

      <div className="space-y-3">
        {rows?.map((p) => (
          <div key={p.application_id} className="card">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="font-mono font-semibold text-slate-100">
                  {p.application?.application_number ?? p.application_id.slice(0, 8)}
                </h3>
                <p className="mt-0.5 text-xs text-slate-500">
                  {p.application?.applicant_name ?? "Customer"} · Bus{" "}
                  {p.application?.pv_bus ?? "—"} ·{" "}
                  {p.application ? `${Number(p.application.new_pv_kw).toFixed(1)} kW` : ""}
                </p>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className="rounded border border-slate-700 px-2 py-0.5 text-[10px] text-slate-400">
                  installation: {p.installation.status.replace(/_/g, " ")}
                </span>
                {p.application && (
                  <span className="rounded border border-slate-700 px-2 py-0.5 text-[10px] text-slate-500">
                    application: {p.application.status.replace(/_/g, " ")}
                  </span>
                )}
              </div>
            </div>

            {p.appointments.length > 0 && (
              <div className="mt-3 space-y-1 border-t border-slate-800 pt-3 text-xs">
                {p.appointments.map((a) => (
                  <div key={a.id} className="flex justify-between text-slate-400">
                    <span>
                      {a.purpose.replace(/_/g, " ").toLowerCase()} ·{" "}
                      {new Date(a.scheduled_at).toLocaleString()}
                    </span>
                    <span className="text-slate-500">{a.status}</span>
                  </div>
                ))}
              </div>
            )}

            {p.installation.discom_verified && (
              <p className="mt-3 text-xs text-green-300">
                DISCOM verified
                {p.installation.discom_verified_at
                  ? ` on ${new Date(p.installation.discom_verified_at).toLocaleDateString()}`
                  : ""}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
