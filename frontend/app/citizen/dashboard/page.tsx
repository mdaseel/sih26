"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { ApplicationStatus, SolarApplication } from "@/lib/types";

const AWAITING: ApplicationStatus[] = ["SUBMITTED","ASSESSING","ASSESSED","UNDER_DISCOM_REVIEW","ENGINEERING_REVIEW"];
const DECIDED: ApplicationStatus[] = ["APPROVED","VENDOR_SELECTED","INSTALLING","INSTALLED","VERIFIED"];
function statusTone(status: ApplicationStatus): string {
  if (status === "REJECTED" || status === "CANCELLED") return "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300";
  if (status === "VERIFIED") return "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-green-900 dark:bg-green-950/40 dark:text-green-300";
  if (DECIDED.includes(status)) return "border-sky-200 bg-sky-50 text-sky-700 dark:border-sky-900 dark:bg-sky-950/40 dark:text-sky-300";
  return "border-slate-200 bg-white text-slate-600 dark:border-slate-700 dark:bg-slate-900/60 dark:text-slate-400";
}
function friendlyStatus(status: ApplicationStatus): string {
  switch (status) { case "SUBMITTED": return "In progress"; case "ASSESSING": return "Grid check running"; case "ASSESSED": case "UNDER_DISCOM_REVIEW": case "ENGINEERING_REVIEW": return "With the DISCOM"; default: return status.replace(/_/g, " ").toLowerCase().replace(/^\w/, (c) => c.toUpperCase()); }
}
function formatDate(iso: string): string { const d = new Date(iso); return Number.isNaN(d.getTime()) ? "—" : d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }); }

export default function DashboardPage() {
  const [apps, setApps] = useState<SolarApplication[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api.listApplications().then(setApps).catch((e: ApiError) => setError(e.message)); }, []);
  const stats = useMemo(() => {
    if (!apps) return null;
    return { total: apps.length, awaiting: apps.filter((a) => AWAITING.includes(a.status)).length, approved: apps.filter((a) => DECIDED.includes(a.status)).length, requestedKw: apps.reduce((s, a) => s + Number(a.new_pv_kw), 0) };
  }, [apps]);
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4 animate-slide-up">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "rgb(var(--ink))" }}>Dashboard</h1>
          <p className="mt-1 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Your rooftop solar connection requests</p>
        </div>
        <Link href="/citizen/applications/new" className="btn-primary">＋ New application</Link>
      </div>
      {error && <p className="rounded-xl border p-3 text-sm" style={{ borderColor: "rgb(220 38 38 / 0.3)", background: "rgb(254 226 226)", color: "rgb(153 27 27)" }}>{error}</p>}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 stagger">
        <div className="card-interactive"><div className="flex h-8 w-8 items-center justify-center rounded-xl text-sm" style={{ background: "rgb(var(--accent) / 0.12)", color: "rgb(var(--accent))" }}>⬡</div><div className="metric-label mt-3">Applications</div><div className="metric-value">{stats?.total ?? "—"}</div><div className="text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>Total submitted</div></div>
        <div className="card-interactive"><div className="flex h-8 w-8 items-center justify-center rounded-xl text-sm" style={{ background: "rgb(var(--caution) / 0.12)", color: "rgb(var(--caution))" }}>◷</div><div className="metric-label mt-3">Awaiting a decision</div><div className="metric-value">{stats?.awaiting ?? "—"}</div><div className="text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>With DISCOM</div></div>
        <div className="card-interactive"><div className="flex h-8 w-8 items-center justify-center rounded-xl text-sm" style={{ background: "rgb(var(--safe) / 0.12)", color: "rgb(var(--safe))" }}>✓</div><div className="metric-label mt-3">Approved</div><div className="metric-value">{stats?.approved ?? "—"}</div><div className="text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>Ready for install</div></div>
        <div className="card-interactive" style={{ background: "linear-gradient(135deg, rgb(var(--brand) / 0.14), rgb(var(--accent) / 0.08))" }}><div className="metric-label">Total capacity requested</div><div className="metric-value">{stats ? stats.requestedKw.toFixed(1) : "—"}<span className="ml-1 text-xs font-normal" style={{ color: "rgb(var(--ink-faint))" }}>kW</span></div><div className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>Across all applications</div></div>
      </div>

      <div className="card">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div><h2 className="text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>Recent applications</h2><p className="mt-0.5 text-xs" style={{ color: "rgb(var(--ink-faint))" }}>{apps?.length ? `${apps.length} ${apps.length === 1 ? "application" : "applications"}, newest first` : "Everything you have submitted"}</p></div>
          {apps && apps.length > 0 && <Link href="/citizen/applications" className="text-xs font-semibold hover:underline" style={{ color: "rgb(var(--accent-strong))" }}>View all →</Link>}
        </div>
        {apps === null && !error && <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-24 rounded-xl shimmer" />)}</div>}
        {apps?.length === 0 && <div className="rounded-xl border border-dashed py-12 text-center" style={{ borderColor: "rgb(var(--line))" }}><div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl text-xl" style={{ background: "rgb(var(--panel-raised))" }}>⬡</div><p className="mt-3 text-sm font-medium" style={{ color: "rgb(var(--ink))" }}>No applications yet</p><p className="mx-auto mt-1 max-w-xs text-xs" style={{ color: "rgb(var(--ink-faint))" }}>Start your first request — it takes two minutes and screens instantly.</p><Link href="/citizen/applications/new" className="btn-primary mt-4">Start your first application</Link></div>}
        {apps && apps.length > 0 && (
          <div className="scroll-pane max-h-[30rem] space-y-3 stagger">
            {apps.map((a) => (
              <Link key={a.id} href={`/citizen/applications/${a.id}`} className="group block rounded-2xl border p-4 transition-all hover:scale-[1.01] active:scale-[0.99]" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))" }}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0"><div className="font-mono text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>{a.application_number}</div><div className="mt-0.5 truncate text-xs" style={{ color: "rgb(var(--ink-faint))" }}>{[a.address_line, a.district, a.state].filter(Boolean).join(", ") || "No address on file"}</div></div>
                  <span className={`shrink-0 rounded-full border px-3 py-1 text-xs font-bold ${statusTone(a.status)}`}>{friendlyStatus(a.status)}</span>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <div><div className="metric-label">Requested</div><div className="font-mono text-sm font-bold tabular-nums" style={{ color: "rgb(var(--ink))" }}>{Number(a.new_pv_kw).toFixed(1)} kW</div></div>
                  <div><div className="metric-label">Existing</div><div className="font-mono text-sm tabular-nums" style={{ color: "rgb(var(--ink-faint))" }}>{Number(a.existing_pv_kw).toFixed(1)} kW</div></div>
                  <div><div className="metric-label">Total after install</div><div className="font-mono text-sm tabular-nums" style={{ color: "rgb(var(--ink-faint))" }}>{Number(a.total_pv_kw).toFixed(1)} kW</div></div>
                  <div><div className="metric-label">Submitted</div><div className="text-sm" style={{ color: "rgb(var(--ink-faint))" }}>{formatDate(a.created_at)}</div></div>
                </div>
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs" style={{ color: "rgb(var(--ink-ghost))" }}><span>Bus {a.pv_bus}</span>{a.roof_type && <span>{a.roof_type}</span>}{a.roof_area_sqm != null && <span>{a.roof_area_sqm} m²</span>}{a.monthly_consumption_kwh != null && <span>{a.monthly_consumption_kwh} kWh/mo</span>}<span className="ml-auto font-semibold opacity-0 transition-all group-hover:opacity-100" style={{ color: "rgb(var(--accent-strong))" }}>View →</span></div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
