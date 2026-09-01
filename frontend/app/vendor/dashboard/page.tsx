"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ApiError, clearApiCache, vendorApi } from "@/lib/api";
import type { Lead, SolarApplication, VendorSummary } from "@/lib/types";
type Opp = SolarApplication & { distance_km?: number | null; is_primary?: boolean; should_blink?: boolean; can_claim?: boolean };
export default function VendorDashboard() {
  const [summary, setSummary] = useState<VendorSummary | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [opps, setOpps] = useState<Opp[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const load = useCallback(async () => {
    const [s, l, o] = await Promise.allSettled([vendorApi.summary(), vendorApi.leads(), vendorApi.opportunities().catch(() => [] as Opp[])]);
    if (s.status === "fulfilled") setSummary(s.value as VendorSummary); else setError((s.reason as ApiError).message);
    if (l.status === "fulfilled") setLeads(l.value as Lead[]);
    if (o.status === "fulfilled") setOpps(o.value as Opp[]);
  }, []);
  useEffect(() => { load(); const id = setInterval(load, 15000); return () => clearInterval(id); }, [load]);
  const newLeads = leads.filter((l) => ["REQUESTED","RESCHEDULED"].includes(l.status));
  async function claim(id: string) {
    try { await vendorApi.claimOpportunity(id); clearApiCache(); setNotice("Claimed — check Projects & Installations"); await load(); } catch (e) { setError((e as ApiError).message); }
  }
  return (
    <div className="space-y-6">
      <div className="animate-slide-up"><h1 className="text-2xl font-bold tracking-tight" style={{ color: "rgb(var(--ink))" }}>{summary?.vendor.business_name ?? "Dashboard"}</h1><p className="mt-1 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Per-vendor feed — nearest opportunities blink. Auto-refreshed every 15s.</p></div>
      {notice && <div className="rounded-xl border p-3 text-sm" style={{ borderColor: "rgb(34 197 94 / 0.3)", background: "rgb(220 252 231)", color: "rgb(22 101 52)" }}>{notice}</div>}
      {error && <p className="rounded-xl border p-3 text-sm" style={{ borderColor: "rgb(220 38 38 / 0.3)", background: "rgb(254 226 226)", color: "rgb(153 27 27)" }}>{error}</p>}
      {summary && !summary.vendor.visible_to_customers && <div className="rounded-xl border p-4 text-sm" style={{ borderColor: "rgb(245 158 11 / 0.3)", background: "rgb(254 243 199)", color: "rgb(146 64 14)" }}>Your business is <b>{summary.vendor.status}</b> and is not visible to customers yet.</div>}
      {summary ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5 stagger">
            <Stat label="New leads" value={summary.new_leads} accent="emerald" />
            <Stat label="Opportunities" value={(summary as unknown as { opportunities?: number }).opportunities ?? opps.length} accent="sky" />
            <Stat label="Confirmed" value={summary.confirmed_appointments} />
            <Stat label="Installations" value={summary.installations} />
            <Stat label="Awaiting verification" value={summary.awaiting_discom_verification} accent="amber" />
          </div>
          <div className="rounded-xl border p-3 text-xs" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel-raised))", color: "rgb(var(--ink-faint))" }}>{summary.verification_note}</div>
        </>
      ) : !error && <div className="grid gap-4 sm:grid-cols-5">{[1,2,3,4,5].map(i => <div key={i} className="h-24 rounded-2xl shimmer" />)}</div>}

      <div className="card">
        <div className="mb-3 flex items-center justify-between"><h2 className="text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>Marketplace — per-vendor, nearest-first</h2><span className="rounded-full bg-emerald-500 px-2 py-0.5 text-xs font-bold text-white">{opps.length} live</span></div>
        <p className="mb-3 text-xs" style={{ color: "rgb(var(--ink-faint))" }}>DISCOM-approved & unassigned. <b style={{ color: "rgb(var(--ink))" }}>Blinking = you are nearest</b>. Others see it after 1h escalation or if primary declines.</p>
        {opps.length === 0 ? <p className="py-6 text-center text-sm" style={{ color: "rgb(var(--ink-faint))" }}>No live opportunities. Approved apps appear here instantly after DISCOM approves.</p> : (
          <div className="space-y-2 stagger">
            {opps.slice(0, 12).map((a) => (
              <div key={a.id} className={`flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3 ${a.should_blink ? "animate-pulse" : ""}`} style={{ borderColor: a.should_blink ? "rgb(34 197 94)" : "rgb(var(--line))", background: a.should_blink ? "rgb(220 252 231)" : "rgb(var(--panel))", boxShadow: a.should_blink ? "0 0 0 3px rgb(34 197 94 / 0.2)" : undefined }}>
                <div><div className="flex items-center gap-2"><span className="font-mono text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>{a.application_number}</span>{a.should_blink && <span className="rounded-full bg-emerald-600 px-2 py-0.5 text-[10px] font-bold text-white">● NEAREST — YOU</span>}{!a.should_blink && a.distance_km != null && <span className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>{a.distance_km.toFixed(1)} km</span>}</div><div className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>{a.applicant_name} · Bus {a.pv_bus} · {Number(a.new_pv_kw).toFixed(1)} kW · {[a.district, a.state].filter(Boolean).join(", ")}{a.distance_km != null ? ` · ${a.distance_km.toFixed(1)} km away` : ""}</div></div>
                <div className="flex items-center gap-2"><span className="rounded-full border px-2.5 py-1 text-xs font-bold" style={{ borderColor: "rgb(34 197 94 / 0.3)", background: "rgb(34 197 94 / 0.1)", color: "rgb(34 197 94)" }}>APPROVED</span>{a.can_claim ? <button onClick={() => claim(a.id)} className="btn-primary !py-1.5 !text-xs">Accept & Claim</button> : <span className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>Nearest has priority (1h)</span>}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <div className="mb-3 flex items-center justify-between"><h2 className="text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>New leads (citizen-selected)</h2><Link href="/vendor/leads" className="text-xs font-semibold hover:underline" style={{ color: "rgb(var(--accent-strong))" }}>All leads →</Link></div>
        {newLeads.length === 0 ? <p className="py-4 text-center text-sm" style={{ color: "rgb(var(--ink-faint))" }}>No citizen-selected leads.</p> : (
          <div className="space-y-2 stagger">
            {newLeads.slice(0, 5).map((l) => (
              <Link key={l.id} href="/vendor/leads" className="flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3 transition hover:scale-[1.01]" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))" }}>
                <div><div className="font-mono text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>{l.application?.application_number ?? l.application_id.slice(0, 8)}</div><div className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>{l.application?.applicant_name ?? "Customer"} · {l.application ? `${Number(l.application.new_pv_kw).toFixed(1)} kW` : ""} · {new Date(l.scheduled_at).toLocaleString()}</div></div>
                <span className="rounded-full border px-2 py-0.5 text-xs" style={{ borderColor: "rgb(var(--line))", color: "rgb(var(--ink-faint))" }}>{l.status}</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
function Stat({ label, value, accent }: { label: string; value: number; accent?: string }) {
  const tone = accent === "emerald" ? "text-emerald-600 dark:text-emerald-300" : accent === "amber" ? "text-amber-600 dark:text-amber-300" : accent === "sky" ? "text-sky-600 dark:text-sky-300" : "";
  return (<div className="card-interactive"><div className="metric-label">{label}</div><div className={`font-mono text-2xl font-bold tabular-nums ${tone}`} style={!tone ? { color: "rgb(var(--ink))" } : undefined}>{value}</div></div>);
}
