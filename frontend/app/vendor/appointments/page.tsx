"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import type { AppointmentStatusValue, Lead } from "@/lib/types";

const STATUSES: AppointmentStatusValue[] = [
  "REQUESTED",
  "CONFIRMED",
  "RESCHEDULED",
  "COMPLETED",
  "CANCELLED",
];

export default function VendorAppointments() {
  const [rows, setRows] = useState<Lead[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [when, setWhen] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      setRows(await vendorApi.appointments());
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function update(id: string, body: Record<string, unknown>) {
    setBusyId(id);
    setError(null);
    try {
      await vendorApi.updateAppointment(id, body);
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
        <h1 className="text-xl font-semibold text-slate-100">Appointments</h1>
        <p className="mt-1 text-sm text-slate-500">Site visits and customer meetings</p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
      {rows === null && !error && <p className="text-sm text-slate-500">Loading…</p>}
      {rows?.length === 0 && (
        <div className="card text-sm text-slate-500">No appointments yet.</div>
      )}

      <div className="space-y-3">
        {rows?.map((r) => (
          <div key={r.id} className="card">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="font-mono font-semibold text-slate-100">
                  {r.application?.application_number ?? r.application_id.slice(0, 8)}
                </h3>
                <p className="mt-0.5 text-xs text-slate-500">
                  {r.application?.applicant_name ?? "Customer"} ·{" "}
                  {[r.application?.address_line, r.application?.district]
                    .filter(Boolean)
                    .join(", ") || "no address"}
                </p>
                {r.application?.contact_phone && (
                  <a
                    href={`tel:${r.application.contact_phone}`}
                    className="text-xs text-sky-400 hover:underline"
                  >
                    {r.application.contact_phone}
                  </a>
                )}
              </div>
              <div className="text-right">
                <div className="text-sm text-slate-200">
                  {new Date(r.scheduled_at).toLocaleString()}
                </div>
                <span className="mt-1 inline-block rounded border border-slate-700 px-2 py-0.5 text-[10px] text-slate-400">
                  {r.status}
                </span>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              <input
                type="datetime-local"
                className="input !w-56 !py-1.5 text-xs"
                value={when[r.id] ?? ""}
                onChange={(e) => setWhen((w) => ({ ...w, [r.id]: e.target.value }))}
              />
              <button
                onClick={() =>
                  update(r.id, {
                    scheduled_at: new Date(when[r.id]).toISOString(),
                    status: "RESCHEDULED",
                  })
                }
                disabled={busyId === r.id || !when[r.id]}
                className="btn-ghost !py-1.5 !text-xs"
              >
                Reschedule
              </button>
              {STATUSES.filter((s) => s !== r.status && s !== "REQUESTED").map((s) => (
                <button
                  key={s}
                  onClick={() => update(r.id, { status: s })}
                  disabled={busyId === r.id}
                  className="btn-ghost !px-2.5 !py-1.5 !text-[11px]"
                >
                  {s.toLowerCase()}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
