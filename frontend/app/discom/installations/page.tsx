"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, discomApi } from "@/lib/api";
import type { Installation } from "@/lib/types";

/**
 * DISCOM installation verification.
 *
 * This is the only place VERIFIED can be set. A vendor may take an
 * installation as far as VERIFICATION_PENDING and no further — the server
 * refuses them, so this screen is the whole of that authority.
 */
export default function DiscomInstallations() {
  const [rows, setRows] = useState<Installation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [photoUrls, setPhotoUrls] = useState<Record<string, string[]>>({});

  const load = useCallback(async () => {
    try {
      setRows(await discomApi.installations());
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function verify(id: string) {
    setBusyId(id);
    setError(null);
    try {
      await discomApi.verifyInstallation(id, notes[id]);
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusyId(null);
    }
  }

  async function returnForCorrection(id: string) {
    if (!reasons[id]?.trim()) {
      setError("A return reason is required so the vendor knows what to fix.");
      return;
    }
    setBusyId(id);
    setError(null);
    try {
      await discomApi.returnInstallation(id, reasons[id].trim());
      setReasons((r) => ({ ...r, [id]: "" }));
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusyId(null);
    }
  }

  async function showPhotos(row: Installation) {
    const ids = row.photo_document_ids ?? [];
    if (photoUrls[row.id]) return;
    try {
      const urls = await Promise.all(ids.map((d) => discomApi.installationPhotoUrl(d)));
      setPhotoUrls((p) => ({ ...p, [row.id]: urls.map((u) => u.url) }));
    } catch (e) {
      setError((e as ApiError).message);
    }
  }

  const awaiting = rows?.filter((r) => r.status === "VERIFICATION_PENDING") ?? [];
  const other = rows?.filter((r) => r.status !== "VERIFICATION_PENDING") ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Installations</h1>
        <p className="mt-1 text-sm text-slate-500">
          Completed work awaiting DISCOM verification. Only this console can mark
          an installation verified.
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
      {rows === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {rows && (
        <div className="grid gap-4 sm:grid-cols-3">
          <Stat label="Total" value={rows.length} />
          <Stat label="Awaiting verification" value={awaiting.length} accent="amber" />
          <Stat
            label="Verified"
            value={rows.filter((r) => r.discom_verified).length}
            accent="green"
          />
        </div>
      )}

      {awaiting.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-200">Awaiting verification</h2>
          {awaiting.map((r) => (
            <div key={r.id} className="card border-amber-900/60">
              <Header row={r} />
              <Report row={r} />
              {(r.photo_document_ids?.length ?? 0) > 0 && (
                <div className="mt-2">
                  <button onClick={() => showPhotos(r)} className="btn-ghost !py-1 !text-[11px]">
                    {photoUrls[r.id] ? "Hide site photos" : `Show site photos (${r.photo_document_ids!.length})`}
                  </button>
                  {photoUrls[r.id] && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {photoUrls[r.id].map((u) => (
                        <a key={u} href={u} target="_blank" rel="noreferrer">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src={u} alt="Completion site photo" className="h-24 w-32 rounded-lg border border-slate-700 object-cover" />
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              )}
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <input
                  className="input !w-80 !py-1.5 text-xs"
                  placeholder="Inspection notes (recorded in the audit log)"
                  value={notes[r.id] ?? ""}
                  onChange={(e) => setNotes((n) => ({ ...n, [r.id]: e.target.value }))}
                />
                <button
                  onClick={() => verify(r.id)}
                  disabled={busyId === r.id}
                  className="btn-primary !py-1.5 !text-xs"
                >
                  {busyId === r.id ? "Verifying…" : "Mark verified"}
                </button>
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <input
                  className="input !w-80 !py-1.5 text-xs"
                  placeholder="Return reason (required — vendor sees this)"
                  value={reasons[r.id] ?? ""}
                  onChange={(e) => setReasons((n) => ({ ...n, [r.id]: e.target.value }))}
                />
                <button
                  onClick={() => returnForCorrection(r.id)}
                  disabled={busyId === r.id}
                  className="btn-ghost !border-red-900 !py-1.5 !text-xs !text-red-300"
                >
                  Return for correction
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {other.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-200">All installations</h2>
          {other.map((r) => (
            <div key={r.id} className="card">
              <Header row={r} />
            </div>
          ))}
        </div>
      )}

      {rows?.length === 0 && (
        <div className="card text-sm text-slate-500">
          No installations yet. One opens when a vendor accepts a lead.
        </div>
      )}
    </div>
  );
}

function Header({ row }: { row: Installation }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h3 className="font-mono font-semibold text-slate-100">
          {row.application?.application_number ?? row.application_id.slice(0, 8)}
        </h3>
        <p className="mt-0.5 text-xs text-slate-500">
          {row.application?.applicant_name ?? "Customer"} · Bus{" "}
          {row.application?.pv_bus ?? "—"} ·{" "}
          {row.installed_capacity_kw != null
            ? `${Number(row.installed_capacity_kw).toFixed(1)} kW installed`
            : "capacity not reported"}
        </p>
        {row.application?.address_line && (
          <p className="mt-0.5 text-xs text-slate-600">{row.application.address_line}</p>
        )}
      </div>
      <div className="text-right">
        <span
          className={`rounded-full border px-2.5 py-0.5 text-[11px] ${
            row.discom_verified
              ? "border-green-800 bg-green-950/60 text-green-300"
              : row.status === "VERIFICATION_PENDING"
                ? "border-amber-900 bg-amber-950/40 text-amber-300"
                : "border-slate-700 text-slate-300"
          }`}
        >
          {row.status.replace(/_/g, " ")}
        </span>
        {row.discom_verified && row.discom_verified_at && (
          <div className="mt-1 text-[11px] text-slate-500">
            verified {new Date(row.discom_verified_at).toLocaleDateString()}
          </div>
        )}
      </div>
    </div>
  );
}

function Report({ row }: { row: Installation }) {
  const approved = row.application ? Number(row.application.new_pv_kw) : null;
  const installed = row.installed_capacity_kw != null ? Number(row.installed_capacity_kw) : null;
  const variance =
    approved != null && installed != null && approved > 0
      ? Math.abs(installed - approved) / approved
      : null;
  const implied =
    row.panel_count != null && row.panel_watts_each != null
      ? (row.panel_count * row.panel_watts_each) / 1000
      : null;
  const crossWarn =
    implied != null && installed != null && installed > 0 && Math.abs(implied - installed) / installed > 0.15;
  const rows: [string, string][] = [
    ["Installed", installed != null ? `${installed.toFixed(1)} kW (approved ${approved != null ? approved.toFixed(1) : "—"} kW)` : "—"],
    ["Panels", row.panel_count != null ? `${row.panel_count} × ${row.panel_watts_each ?? "?"} W ${row.panel_make ?? ""} ${row.panel_model ?? ""}`.trim() : "—"],
    ["Inverter", row.inverter_capacity_kw != null ? `${Number(row.inverter_capacity_kw).toFixed(1)} kW ${row.inverter_make ?? ""} ${row.inverter_model ?? ""}`.trim() : "—"],
    ["Install date", row.install_date ?? "—"],
    ["Checklist", row.checklist ? `${Object.values(row.checklist).filter(Boolean).length}/6 ticked` : "—"],
  ];
  return (
    <div className="mt-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-xs">
      {rows.map(([k, v]) => (
        <div key={k} className="flex items-baseline justify-between gap-2 border-b border-slate-800/60 py-1 last:border-0">
          <span className="text-slate-500">{k}</span>
          <span className="font-mono text-slate-200">{v}</span>
        </div>
      ))}
      {row.completion_notes && <p className="mt-1.5 text-slate-400">“{row.completion_notes}”</p>}
      {variance != null && variance >= 0.1 && (
        <p className="mt-1.5 text-amber-300">
          ⚠️ Installed capacity differs from approved by {(variance * 100).toFixed(0)}% — confirm before verifying.
        </p>
      )}
      {crossWarn && (
        <p className="mt-1 text-amber-300/80">
          Panel arithmetic ({implied!.toFixed(1)} kW) differs from reported {installed!.toFixed(1)} kW by over 15% — DC/AC sizing can explain this.
        </p>
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
  accent?: "amber" | "green";
}) {
  const tone =
    accent === "amber" ? "text-amber-300" : accent === "green" ? "text-green-300" : "text-slate-100";
  return (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className={`font-mono text-2xl tabular-nums ${tone}`}>{value}</div>
    </div>
  );
}
