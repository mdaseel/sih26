"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import type { Lead, VendorSummary } from "@/lib/types";

export default function VendorDashboard() {
  const [summary, setSummary] = useState<VendorSummary | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([vendorApi.summary(), vendorApi.leads()])
      .then(([s, l]) => {
        setSummary(s);
        setLeads(l);
      })
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const newLeads = leads.filter((l) => ["REQUESTED", "RESCHEDULED"].includes(l.status));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">
          {summary?.vendor.business_name ?? "Dashboard"}
        </h1>
        <p className="mt-1 text-sm text-slate-500">Your leads, appointments and installations</p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {summary && !summary.vendor.visible_to_customers && (
        <div className="rounded-lg border border-amber-900 bg-amber-950/30 p-4 text-sm text-amber-200">
          Your business is <b>{summary.vendor.status}</b> and is not visible to
          customers yet. A DISCOM reviewer must approve it before you can receive
          leads.
        </div>
      )}

      {summary && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="New leads" value={summary.new_leads} accent="emerald" />
            <Stat label="Confirmed appointments" value={summary.confirmed_appointments} />
            <Stat label="Installations" value={summary.installations} />
            <Stat
              label="Awaiting DISCOM verification"
              value={summary.awaiting_discom_verification}
              accent="amber"
            />
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
            {summary.verification_note}
          </div>
        </>
      )}

      <div className="card">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200">New leads</h2>
          <Link href="/vendor/leads" className="text-xs text-sky-400 hover:underline">
            All leads →
          </Link>
        </div>

        {newLeads.length === 0 ? (
          <p className="text-sm text-slate-500">No new leads.</p>
        ) : (
          <div className="space-y-2">
            {newLeads.slice(0, 5).map((l) => (
              <Link
                key={l.id}
                href="/vendor/leads"
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/40 px-4 py-3 transition hover:border-slate-700"
              >
                <div>
                  <div className="font-mono text-sm text-slate-200">
                    {l.application?.application_number ?? l.application_id.slice(0, 8)}
                  </div>
                  <div className="text-xs text-slate-500">
                    {l.application?.applicant_name ?? "Customer"} ·{" "}
                    {l.application ? `${Number(l.application.new_pv_kw).toFixed(1)} kW` : ""} ·{" "}
                    {new Date(l.scheduled_at).toLocaleString()}
                  </div>
                </div>
                <span className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-400">
                  {l.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>

      {summary && Object.keys(summary.installations_by_status).length > 0 && (
        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-slate-200">Installations by stage</h2>
          <div className="flex flex-wrap gap-4 text-sm">
            {Object.entries(summary.installations_by_status).map(([k, v]) => (
              <span key={k} className="text-slate-300">
                {k.replace(/_/g, " ")}: <b className="font-mono">{v}</b>
              </span>
            ))}
          </div>
        </div>
      )}
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
  accent?: "emerald" | "amber";
}) {
  const tone =
    accent === "emerald"
      ? "text-emerald-300"
      : accent === "amber"
        ? "text-amber-300"
        : "text-slate-100";
  return (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className={`font-mono text-2xl tabular-nums ${tone}`}>{value}</div>
    </div>
  );
}
