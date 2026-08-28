"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import type { Installation, InstallationStatusValue } from "@/lib/types";

/**
 * Installation tracking.
 *
 * The stage list stops at VERIFICATION_PENDING. VERIFIED is not offered here
 * because it is not the installer's to assert — a DISCOM reviewer sets it after
 * inspection, and the server refuses a vendor who tries.
 */
const VENDOR_STAGES: InstallationStatusValue[] = [
  "PENDING",
  "SITE_VISIT",
  "SCHEDULED",
  "IN_PROGRESS",
  "COMPLETED",
  "VERIFICATION_PENDING",
];

const ALL_STAGES: InstallationStatusValue[] = [...VENDOR_STAGES, "VERIFIED"];

export default function VendorInstallations() {
  const [rows, setRows] = useState<Installation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [capacity, setCapacity] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      setRows(await vendorApi.installations());
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function advance(row: Installation, status: InstallationStatusValue) {
    setBusyId(row.id);
    setError(null);
    try {
      const kw = capacity[row.id] ? Number(capacity[row.id]) : undefined;
      await vendorApi.updateInstallation(row.id, status, kw);
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Installations</h1>
        <p className="mt-1 text-sm text-slate-500">
          Track work through to submission for DISCOM verification
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
          No installations yet. Accepting a lead opens one.
        </div>
      )}

      <div className="space-y-3">
        {rows?.map((row) => {
          const idx = ALL_STAGES.indexOf(row.status);
          const verified = row.status === "VERIFIED";
          return (
            <div key={row.id} className="card">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="font-mono font-semibold text-slate-100">
                    {row.application?.application_number ?? row.application_id.slice(0, 8)}
                  </h3>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {row.application?.applicant_name ?? "Customer"} · Bus{" "}
                    {row.application?.pv_bus ?? "—"} ·{" "}
                    {row.application ? `${Number(row.application.new_pv_kw).toFixed(1)} kW` : ""}
                  </p>
                </div>
                <span
                  className={`rounded-full border px-2.5 py-0.5 text-[11px] ${
                    verified
                      ? "border-green-800 bg-green-950/60 text-green-300"
                      : row.status === "VERIFICATION_PENDING"
                        ? "border-amber-900 bg-amber-950/40 text-amber-300"
                        : "border-slate-700 text-slate-300"
                  }`}
                >
                  {row.status.replace(/_/g, " ")}
                </span>
              </div>

              {/* Progress rail */}
              <div className="mt-4 flex flex-wrap items-center gap-1">
                {ALL_STAGES.map((s, i) => (
                  <div key={s} className="flex items-center gap-1">
                    <span
                      className={`rounded px-2 py-0.5 text-[10px] ${
                        i <= idx
                          ? s === "VERIFIED"
                            ? "bg-green-900/60 text-green-200"
                            : "bg-slate-700 text-slate-100"
                          : "bg-slate-900 text-slate-600"
                      }`}
                      title={s === "VERIFIED" ? "Set by the DISCOM only" : undefined}
                    >
                      {s.replace(/_/g, " ")}
                      {s === "VERIFIED" && " 🔒"}
                    </span>
                    {i < ALL_STAGES.length - 1 && <span className="text-slate-700">›</span>}
                  </div>
                ))}
              </div>

              {!verified && (
                <div className="mt-4 flex flex-wrap items-center gap-2">
                  <input
                    type="number"
                    min={0}
                    step={0.1}
                    className="input !w-40 !py-1.5 text-xs"
                    placeholder="installed kW"
                    value={capacity[row.id] ?? ""}
                    onChange={(e) =>
                      setCapacity((c) => ({ ...c, [row.id]: e.target.value }))
                    }
                  />
                  {VENDOR_STAGES.filter((s) => s !== row.status).map((s) => (
                    <button
                      key={s}
                      onClick={() => advance(row, s)}
                      disabled={busyId === row.id}
                      className="btn-ghost !px-2.5 !py-1.5 !text-[11px]"
                    >
                      {s.replace(/_/g, " ")}
                    </button>
                  ))}
                </div>
              )}

              {row.status === "VERIFICATION_PENDING" && (
                <p className="mt-3 rounded-lg border border-amber-900 bg-amber-950/30 p-2.5 text-xs text-amber-200">
                  Submitted for DISCOM verification. Only a DISCOM reviewer can mark
                  this VERIFIED.
                </p>
              )}

              {verified && (
                <p className="mt-3 rounded-lg border border-green-900 bg-green-950/30 p-2.5 text-xs text-green-200">
                  Verified by the DISCOM
                  {row.discom_verified_at
                    ? ` on ${new Date(row.discom_verified_at).toLocaleDateString()}`
                    : ""}
                  {row.verification_notes ? ` — ${row.verification_notes}` : ""}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
