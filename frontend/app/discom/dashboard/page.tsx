"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { RiskBadge } from "@/components/RiskBadge";
import { ApiError, discomApi } from "@/lib/api";
import type { DiscomApplication, DiscomSummary } from "@/lib/types";

export default function DiscomDashboard() {
  const [summary, setSummary] = useState<DiscomSummary | null>(null);
  const [apps, setApps] = useState<DiscomApplication[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { Promise.all([discomApi.summary(), discomApi.applications()]).then(([s, a]) => { setSummary(s); setApps(a); }).catch((e: ApiError) => setError(e.message)); }, []);
  const queue = apps.filter((a) => ["SUBMITTED","ASSESSED","UNDER_DISCOM_REVIEW","ENGINEERING_REVIEW"].includes(a.status)).slice(0, 8);
  return (
    <div className="space-y-6">
      <div className="animate-slide-up">
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: "rgb(var(--ink))" }}>Network overview</h1>
        <p className="mt-1 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Connection requests and their effect on the distribution network</p>
      </div>
      {error && <p className="rounded-xl border p-3 text-sm" style={{ borderColor: "rgb(220 38 38 / 0.3)", background: "rgb(254 226 226)", color: "rgb(153 27 27)" }}>{error}</p>}
      {summary ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 stagger">
            <Stat label="Total applications" value={summary.total_applications} icon="⬡" />
            <Stat label="Pending review" value={summary.pending_review} accent="amber" icon="◷" />
            <Stat label="Approved capacity" value={summary.approved_solar_kw.toFixed(1)} unit="kW" icon="⚡" />
            <Stat label="Pending capacity" value={summary.pending_solar_kw.toFixed(1)} unit="kW" accent="amber" icon="◐" />
          </div>
          <div className="grid gap-4 sm:grid-cols-3 stagger">
            <Stat label="SAFE" value={summary.by_risk.SAFE} accent="green" />
            <Stat label="CAUTION" value={summary.by_risk.CAUTION} accent="yellow" />
            <Stat label="CONSTRAINED" value={summary.by_risk.CONSTRAINED} accent="red" />
          </div>
          {summary.ml_engineering_disagreements > 0 && (
            <div className="rounded-xl border p-4 text-sm animate-slide-up" style={{ borderColor: "rgb(245 158 11 / 0.3)", background: "rgb(254 243 199)", color: "rgb(146 64 14)" }}>
              <b>{summary.ml_engineering_disagreements}</b> application{summary.ml_engineering_disagreements === 1 ? "" : "s"} where ML and power flow disagree. Power-flow result stands; flagged for engineering attention.
            </div>
          )}
          <p className="text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>{summary.capacity_note}</p>
        </>
      ) : !error && <div className="grid gap-4 sm:grid-cols-4">{[1,2,3,4].map(i => <div key={i} className="h-24 rounded-2xl shimmer" />)}</div>}

      <div className="card">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>Awaiting decision</h2>
          <Link href="/discom/applications" className="text-xs font-semibold hover:underline" style={{ color: "rgb(var(--accent-strong))" }}>All applications →</Link>
        </div>
        {queue.length === 0 ? <p className="py-6 text-center text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Nothing awaiting review. 🎉</p> : (
          <div className="space-y-2 stagger">
            {queue.map((a) => (
              <Link key={a.id} href={`/discom/applications/${a.id}`} className="group flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3 transition-all hover:scale-[1.01] active:scale-[0.99]" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))" }}>
                <div><div className="font-mono text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>{a.application_number}</div><div className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>{a.applicant_name} · Bus {a.pv_bus} · {Number(a.new_pv_kw).toFixed(1)} kW</div></div>
                <div className="flex items-center gap-3">{a.engineering_risk ? <RiskBadge risk={a.engineering_risk} size="sm" /> : <span className="text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>not assessed</span>}<span className="rounded-full border px-2.5 py-1 text-xs font-medium" style={{ borderColor: "rgb(var(--line))", color: "rgb(var(--ink-faint))" }}>{a.status.replace(/_/g, " ")}</span></div>
              </Link>
            ))}
          </div>
        )}
      </div>
      {summary && (
        <div className="card">
          <h2 className="mb-3 text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>Network model</h2>
          <div className="grid gap-3 text-sm sm:grid-cols-5">
            <Field label="Engine" value={`${summary.network.engine} ${summary.network.engine_version}`} />
            <Field label="Buses" value={summary.network.buses} />
            <Field label="Lines" value={summary.network.lines} />
            <Field label="Transformers" value={summary.network.transformers} />
            <Field label="Regulators" value={summary.network.regulator_handling} />
          </div>
          <p className="mt-3 text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>{summary.data_class}</p>
        </div>
      )}
    </div>
  );
}
function Stat({ label, value, unit, accent, icon }: { label: string; value: number | string; unit?: string; accent?: string; icon?: string }) {
  const tone = accent === "green" ? "text-emerald-600 dark:text-emerald-300" : accent === "yellow" ? "text-amber-600 dark:text-amber-300" : accent === "red" ? "text-red-600 dark:text-red-300" : accent === "amber" ? "text-amber-600 dark:text-amber-300" : "";
  return (
    <div className="card-interactive">
      {icon && <div className="mb-2 flex h-7 w-7 items-center justify-center rounded-lg text-xs" style={{ background: "rgb(var(--panel-raised))" }}>{icon}</div>}
      <div className="metric-label">{label}</div>
      <div className={`font-mono text-2xl font-bold tabular-nums ${tone}`} style={!tone ? { color: "rgb(var(--ink))" } : undefined}>{value}{unit && <span className="ml-1 text-xs font-normal" style={{ color: "rgb(var(--ink-ghost))" }}>{unit}</span>}</div>
    </div>
  );
}
function Field({ label, value }: { label: string; value: string | number }) { return (<div><div className="metric-label">{label}</div><div className="text-sm font-medium" style={{ color: "rgb(var(--ink))" }}>{value}</div></div>); }
