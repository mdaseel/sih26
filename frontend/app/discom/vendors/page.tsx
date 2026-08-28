"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, discomApi } from "@/lib/api";
import type { VendorReviewList, VendorStatusValue } from "@/lib/types";

const STATUS_TONE: Record<VendorStatusValue, string> = {
  PENDING: "border-slate-700 text-slate-300",
  UNDER_REVIEW: "border-sky-800 bg-sky-950/40 text-sky-300",
  APPROVED: "border-green-800 bg-green-950/40 text-green-300",
  REJECTED: "border-red-900 bg-red-950/40 text-red-300",
  SUSPENDED: "border-amber-900 bg-amber-950/40 text-amber-300",
};

/**
 * Vendor verification queue.
 *
 * Approving here is what makes a business visible to customers, so each row
 * states plainly whether it is currently visible rather than leaving the
 * reviewer to infer it from the status name.
 */
export default function DiscomVendors() {
  const [data, setData] = useState<VendorReviewList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [reason, setReason] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      setData(await discomApi.vendors());
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function review(id: string, status: VendorStatusValue) {
    setBusyId(id);
    setError(null);
    try {
      await discomApi.reviewVendor(id, status, reason[id]);
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
        <h1 className="text-xl font-semibold text-slate-100">Vendor verification</h1>
        <p className="mt-1 text-sm text-slate-500">
          Only approved and active businesses are shown to customers.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {data && (
        <div className="grid gap-4 sm:grid-cols-4">
          <Stat label="Registered" value={data.vendors.length} />
          <Stat label="Awaiting review" value={data.counts.PENDING ?? 0} accent="amber" />
          <Stat label="Approved" value={data.counts.APPROVED ?? 0} accent="green" />
          <Stat label="Visible to customers" value={data.visible_to_customers} />
        </div>
      )}

      {data === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      <div className="space-y-3">
        {data?.vendors.map((v) => {
          const visible = v.status === "APPROVED" && v.is_active;
          return (
            <div key={v.id} className="card">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-slate-100">{v.business_name}</h3>
                    <span
                      className={`rounded-full border px-2 py-0.5 text-[10px] font-medium ${STATUS_TONE[v.status]}`}
                    >
                      {v.status.replace(/_/g, " ")}
                    </span>
                    <span
                      className={`text-[11px] ${visible ? "text-green-400" : "text-slate-500"}`}
                    >
                      {visible ? "visible to customers" : "not visible to customers"}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {v.representative_name ?? "—"} · {v.district ?? "—"}, {v.state ?? "—"} ·{" "}
                    {v.email ?? "no email"}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {v.years_experience ?? "—"} years · capacity{" "}
                    {v.installation_capacity_kw ?? "—"} kW · {v.completed_installations}{" "}
                    completed · areas: {v.service_areas.join(", ") || "—"}
                  </p>
                  {v.rejection_reason && (
                    <p className="mt-1 text-xs text-red-300">Reason: {v.rejection_reason}</p>
                  )}
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                <input
                  className="input !w-64 !py-1.5 text-xs"
                  placeholder="Reason (recorded in the audit log)"
                  value={reason[v.id] ?? ""}
                  onChange={(e) => setReason((r) => ({ ...r, [v.id]: e.target.value }))}
                />
                <button
                  onClick={() => review(v.id, "APPROVED")}
                  disabled={busyId === v.id || v.status === "APPROVED"}
                  className="btn-primary !py-1.5 !text-xs"
                >
                  Approve
                </button>
                <button
                  onClick={() => review(v.id, "UNDER_REVIEW")}
                  disabled={busyId === v.id}
                  className="btn-ghost !py-1.5 !text-xs"
                >
                  Under review
                </button>
                <button
                  onClick={() => review(v.id, "SUSPENDED")}
                  disabled={busyId === v.id}
                  className="btn-ghost !border-amber-900 !py-1.5 !text-xs !text-amber-300"
                >
                  Suspend
                </button>
                <button
                  onClick={() => review(v.id, "REJECTED")}
                  disabled={busyId === v.id}
                  className="btn-ghost !border-red-900 !py-1.5 !text-xs !text-red-300"
                >
                  Reject
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: "green" | "amber";
}) {
  const tone =
    accent === "green" ? "text-green-300" : accent === "amber" ? "text-amber-300" : "text-slate-100";
  return (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className={`font-mono text-2xl tabular-nums ${tone}`}>{value}</div>
    </div>
  );
}
