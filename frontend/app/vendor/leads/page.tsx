"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import type { Lead } from "@/lib/types";

/**
 * Lead queue.
 *
 * A lead is a customer who has chosen this vendor for a specific application
 * and asked for a site visit. Accepting one opens the installation record the
 * work is tracked on.
 */
export default function VendorLeads() {
  const [leads, setLeads] = useState<Lead[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      setLeads(await vendorApi.leads());
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function respond(id: string, accept: boolean) {
    setBusyId(id);
    setError(null);
    try {
      await vendorApi.respondToLead(id, accept, notes[id]);
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusyId(null);
    }
  }

  const open = leads?.filter((l) => ["REQUESTED", "RESCHEDULED"].includes(l.status)) ?? [];
  const answered = leads?.filter((l) => !["REQUESTED", "RESCHEDULED"].includes(l.status)) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Leads</h1>
        <p className="mt-1 text-sm text-slate-500">
          Customers who have chosen your business for a connection
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
      {leads === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {leads && open.length === 0 && answered.length === 0 && (
        <div className="card text-sm text-slate-500">
          No leads yet. Customers can find you once your business is approved.
        </div>
      )}

      {open.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-200">Awaiting your response</h2>
          {open.map((l) => (
            <LeadCard
              key={l.id}
              lead={l}
              busy={busyId === l.id}
              note={notes[l.id] ?? ""}
              onNote={(v) => setNotes((n) => ({ ...n, [l.id]: v }))}
              onRespond={(accept) => respond(l.id, accept)}
            />
          ))}
        </div>
      )}

      {answered.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-200">Answered</h2>
          {answered.map((l) => (
            <LeadCard key={l.id} lead={l} busy={false} />
          ))}
        </div>
      )}
    </div>
  );
}

function LeadCard({
  lead: l,
  busy,
  note,
  onNote,
  onRespond,
}: {
  lead: Lead;
  busy: boolean;
  note?: string;
  onNote?: (v: string) => void;
  onRespond?: (accept: boolean) => void;
}) {
  const a = l.application;
  const actionable = onRespond && ["REQUESTED", "RESCHEDULED"].includes(l.status);

  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-mono font-semibold text-slate-100">
              {a?.application_number ?? l.application_id.slice(0, 8)}
            </h3>
            <span className="rounded border border-slate-700 px-2 py-0.5 text-[10px] text-slate-400">
              {l.status}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-300">{a?.applicant_name ?? "Customer"}</p>
        </div>
        <div className="text-right text-xs text-slate-400">
          <div>{new Date(l.scheduled_at).toLocaleString()}</div>
          <div className="text-slate-600">{l.purpose.replace(/_/g, " ").toLowerCase()}</div>
        </div>
      </div>

      {a && (
        <div className="mt-3 grid gap-2 rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-xs sm:grid-cols-3">
          <Field label="Requested capacity" value={`${Number(a.new_pv_kw).toFixed(1)} kW`} />
          <Field label="Existing solar" value={`${Number(a.existing_pv_kw).toFixed(1)} kW`} />
          <Field label="Connection point" value={`Bus ${a.pv_bus}`} />
          <Field label="Roof" value={[a.roof_type, a.shading_level && `${a.shading_level} shading`].filter(Boolean).join(" · ") || null} />
          <Field
            label="Address"
            value={[a.address_line, a.district, a.state].filter(Boolean).join(", ") || null}
          />
          <Field label="Phone" value={a.contact_phone} />
        </div>
      )}

      {l.notes && <p className="mt-2 text-xs text-slate-500">Note: {l.notes}</p>}

      {actionable && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <input
            className="input !w-72 !py-1.5 text-xs"
            placeholder="Message to the customer (optional)"
            value={note}
            onChange={(e) => onNote?.(e.target.value)}
          />
          <button
            onClick={() => onRespond?.(true)}
            disabled={busy}
            className="btn-primary !py-1.5 !text-xs"
          >
            Accept lead
          </button>
          <button
            onClick={() => onRespond?.(false)}
            disabled={busy}
            className="btn-ghost !border-red-900 !py-1.5 !text-xs !text-red-300"
          >
            Decline
          </button>
        </div>
      )}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <div className="metric-label">{label}</div>
      <div className="text-slate-300">{value ?? "—"}</div>
    </div>
  );
}
