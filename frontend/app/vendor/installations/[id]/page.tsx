"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import type { Installation } from "@/lib/types";

/**
 * Installation workspace: progress the job step by step, file the completion
 * report (equipment, capacity, dates, photos, checklist, remarks), then submit
 * it for DISCOM verification. VERIFIED stays 🔒 — only a DISCOM reviewer sets it.
 */

const ORDER = [
  "PENDING",
  "SITE_VISIT",
  "SCHEDULED",
  "IN_PROGRESS",
  "COMPLETED",
  "VERIFICATION_PENDING",
  "VERIFIED",
] as const;

const CHECKS: { key: string; label: string }[] = [
  { key: "modules_torqued", label: "Modules torqued to spec" },
  { key: "wiring_mcb", label: "Wiring + MCB protection done" },
  { key: "earthing", label: "Earthing done" },
  { key: "net_meter_paperwork", label: "Net-meter paperwork filed" },
  { key: "generation_test", label: "Generation test passed" },
  { key: "customer_demo", label: "Customer demo given" },
];

export default function VendorInstallationWorkspace() {
  const { id } = useParams<{ id: string }>();
  const [row, setRow] = useState<Installation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({});
  const [checks, setChecks] = useState<Record<string, boolean>>({});
  const [photos, setPhotos] = useState<string[]>([]);
  const [photoMeta, setPhotoMeta] = useState<Record<string, { name: string; kind: string; preview?: string }>>({});
  const [uploadingKey, setUploadingKey] = useState<string | null>(null);

  const enrichPhotos = useCallback(async (ids: string[]) => {
    // Filenames from the vendor profile documents; thumbnails via signed URLs.
    try {
      const profile = await vendorApi.profile();
      const byId = new Map((profile.documents ?? []).map((d) => [d.id, d]));
      const metas: Record<string, { name: string; kind: string; preview?: string }> = {};
      await Promise.all(
        ids.map(async (pid) => {
          const doc = byId.get(pid) as { file_name?: string | null } | undefined;
          let preview: string | undefined;
          try {
            preview = (await vendorApi.documentUrl(pid)).url;
          } catch { preview = undefined; }
          metas[pid] = { name: doc?.file_name ?? "site photo", kind: "", preview };
        })
      );
      setPhotoMeta((m) => ({ ...metas, ...m }));
    } catch { /* previews are advisory — ids alone still submit */ }
  }, []);

  const load = useCallback(async () => {
    try {
      const rows = await vendorApi.installations();
      const found = rows.find((r) => r.id === id) ?? null;
      setRow(found);
      if (!found) setError("Installation not found on your account.");
      else {
        const ids = found.photo_document_ids ?? [];
        setPhotos(ids);
        // Drop previews for photos removed elsewhere; fetch the rest.
        setPhotoMeta((m) => Object.fromEntries(Object.entries(m).filter(([k]) => ids.includes(k))));
        if (ids.length > 0) void enrichPhotos(ids);
        setForm({
          installed_capacity_kw: found.installed_capacity_kw?.toString() ?? "",
          panel_make: found.panel_make ?? "",
          panel_model: found.panel_model ?? "",
          panel_count: found.panel_count?.toString() ?? "",
          panel_watts_each: found.panel_watts_each?.toString() ?? "",
          inverter_make: found.inverter_make ?? "",
          inverter_model: found.inverter_model ?? "",
          inverter_capacity_kw: found.inverter_capacity_kw?.toString() ?? "",
          install_date: found.install_date ?? "",
          completion_notes: found.completion_notes ?? "",
        });
        setChecks(found.checklist ?? {});
        setPhotos(found.photo_document_ids ?? []);
      }
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const idx = row ? ORDER.indexOf(row.status as (typeof ORDER)[number]) : -1;
  const next = row && idx >= 0 && idx < ORDER.length - 1 ? ORDER[idx + 1] : null;
  const editable =
    row && !row.discom_verified && (row.status === "IN_PROGRESS" || row.status === "COMPLETED");
  const verified = row?.status === "VERIFIED";

  const impliedKw = useMemo(() => {
    const c = Number(form.panel_count), w = Number(form.panel_watts_each);
    return c > 0 && w > 0 ? (c * w) / 1000 : null;
  }, [form.panel_count, form.panel_watts_each]);
  const reportedKw = Number(form.installed_capacity_kw);
  const crossWarn =
    impliedKw != null && reportedKw > 0 && Math.abs(impliedKw - reportedKw) / reportedKw > 0.15
      ? `Panel arithmetic (${impliedKw.toFixed(1)} kW) differs from reported ${reportedKw.toFixed(1)} kW by over 15% — DC/AC sizing can explain this; it warns, never blocks.`
      : null;

  async function advance(to: string) {
    setBusy(true); setError(null);
    try {
      const kw = form.installed_capacity_kw ? Number(form.installed_capacity_kw) : undefined;
      await vendorApi.updateInstallation(id, to as never, kw);
      await load();
    } catch (e) { setError((e as ApiError).message); }
    finally { setBusy(false); }
  }

  async function save() {
    setBusy(true); setError(null);
    try {
      const body: Record<string, unknown> = {
        installed_capacity_kw: form.installed_capacity_kw ? Number(form.installed_capacity_kw) : undefined,
        panel_make: form.panel_make || undefined,
        panel_model: form.panel_model || undefined,
        panel_count: form.panel_count ? Number(form.panel_count) : undefined,
        panel_watts_each: form.panel_watts_each ? Number(form.panel_watts_each) : undefined,
        inverter_make: form.inverter_make || undefined,
        inverter_model: form.inverter_model || undefined,
        inverter_capacity_kw: form.inverter_capacity_kw ? Number(form.inverter_capacity_kw) : undefined,
        install_date: form.install_date || undefined,
        completion_notes: form.completion_notes || undefined,
        checklist: checks,
        photo_document_ids: photos,
      };
      await vendorApi.saveInstallationReport(id, body);
      await load();
    } catch (e) { setError((e as ApiError).message); }
    finally { setBusy(false); }
  }

  async function submit() {
    setBusy(true); setError(null);
    try {
      await save();
      await vendorApi.submitInstallation(id);
      await load();
    } catch (e) { setError((e as ApiError).message); }
    finally { setBusy(false); }
  }

  async function upload(key: string, file: File, kind: string, label: string) {
    // Instant local preview first, so the clicked button shows progress and
    // the thumbnail appears immediately — the server id follows on success.
    const preview = URL.createObjectURL(file);
    const tempId = `pending-${Date.now()}`;
    setUploadingKey(key); setUploading(true); setError(null);
    setPhotoMeta((m) => ({ ...m, [tempId]: { name: file.name, kind: label, preview } }));
    try {
      const { document } = await vendorApi.uploadInstallationPhoto(file, kind);
      setPhotos((p) => [...p, document.id]);
      setPhotoMeta((m) => {
        const { [tempId]: _drop, ...rest } = m;
        return {
          ...rest,
          [document.id]: { name: document.file_name ?? file.name, kind: label, preview },
        };
      });
    } catch (e) {
      setPhotoMeta((m) => {
        const { [tempId]: _drop, ...rest } = m;
        return rest;
      });
      setError((e as ApiError).message);
    }
    finally { setUploading(false); setUploadingKey(null); }
  }

  function removePhoto(pid: string) {
    setPhotos((p) => p.filter((x) => x !== pid));
    setPhotoMeta((m) => {
      const { [pid]: _drop, ...rest } = m;
      return rest;
    });
  }

  if (!row && !error) return <p className="text-sm text-slate-500">Loading…</p>;
  if (!row) {
    return (
      <div className="space-y-4">
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">{error}</p>
        <Link href="/vendor/installations" className="btn-ghost">Back to installations</Link>
      </div>
    );
  }

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div className="space-y-6">
      <div>
        <Link href="/vendor/installations" className="text-xs text-slate-500 hover:text-slate-300">← All installations</Link>
        <h1 className="mt-1 font-mono text-xl font-semibold text-slate-100">
          {row.application?.application_number ?? row.application_id.slice(0, 8)}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {row.application?.applicant_name ?? "Customer"} · Bus {row.application?.pv_bus ?? "—"} ·{" "}
          {row.application ? `${Number(row.application.new_pv_kw).toFixed(1)} kW approved` : ""}
        </p>
      </div>

      {error && <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">{error}</p>}

      {row.return_notes && !verified && (
        <p className="rounded-lg border border-amber-900 bg-amber-950/40 p-3 text-sm text-amber-200">
          ⚠️ Returned by DISCOM for correction: {row.return_notes} — update the report below and resubmit.
        </p>
      )}

      {/* stepper */}
      <div className="card">
        <div className="flex flex-wrap items-center gap-1">
          {ORDER.map((s, i) => (
            <div key={s} className="flex items-center gap-1">
              <span className={`rounded px-2 py-0.5 text-[10px] ${i < idx ? "bg-slate-700 text-slate-100" : i === idx ? "bg-sky-800 text-sky-100" : "bg-slate-900 text-slate-600"}`}>
                {s.replace(/_/g, " ")}{s === "VERIFIED" && " 🔒"}
              </span>
              {i < ORDER.length - 1 && <span className="text-slate-700">›</span>}
            </div>
          ))}
        </div>
        {next && next !== "VERIFIED" && (
          <button onClick={() => advance(next)} disabled={busy} className="btn-ghost mt-3 !py-1.5 !text-xs">
            {busy ? "Working…" : `Advance to ${next.replace(/_/g, " ")}`}
          </button>
        )}
      </div>

      {/* completion report */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-slate-200">Completion report</h2>
        {!editable && !verified && (
          <p className="text-xs text-slate-500">The report opens once work starts (IN_PROGRESS).</p>
        )}
        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Installed capacity (kW)" v={form.installed_capacity_kw} onChange={set("installed_capacity_kw")} type="number" step="0.1" disabled={!editable} />
          <Field label="Panel make" v={form.panel_make} onChange={set("panel_make")} disabled={!editable} />
          <Field label="Panel model" v={form.panel_model} onChange={set("panel_model")} disabled={!editable} />
          <Field label="Panel count" v={form.panel_count} onChange={set("panel_count")} type="number" disabled={!editable} />
          <Field label="Panel watts each" v={form.panel_watts_each} onChange={set("panel_watts_each")} type="number" disabled={!editable} />
          <Field label="Inverter make" v={form.inverter_make} onChange={set("inverter_make")} disabled={!editable} />
          <Field label="Inverter model" v={form.inverter_model} onChange={set("inverter_model")} disabled={!editable} />
          <Field label="Inverter capacity (kW)" v={form.inverter_capacity_kw} onChange={set("inverter_capacity_kw")} type="number" step="0.1" disabled={!editable} />
          <Field label="Install date" v={form.install_date} onChange={set("install_date")} type="date" disabled={!editable} />
        </div>
        {crossWarn && <p className="rounded-lg border border-amber-900 bg-amber-950/30 p-2.5 text-xs text-amber-200">{crossWarn}</p>}
        <div>
          <label className="label">Remarks</label>
          <textarea className="input min-h-[60px]" value={form.completion_notes} onChange={set("completion_notes")} disabled={!editable} placeholder="Deviations, roof issues, anything DISCOM should know…" />
        </div>
        <div>
          <div className="label">Commissioning checklist (all six to submit)</div>
          <div className="grid gap-2 sm:grid-cols-2">
            {CHECKS.map((c) => (
              <label key={c.key} className="flex items-center gap-2 text-xs text-slate-300">
                <input type="checkbox" checked={!!checks[c.key]} disabled={!editable}
                  onChange={(e) => setChecks((s) => ({ ...s, [c.key]: e.target.checked }))}
                  className="accent-sky-500" />
                {c.label}
              </label>
            ))}
          </div>
        </div>
        <div>
          <div className="label">Site photos (min 2: rooftop/panels + meter)</div>
          <p className="text-xs text-slate-500">{photos.length} attached{photos.length < 2 ? " — need 2 to submit" : " ✓"}</p>
          {(photos.length > 0 || Object.keys(photoMeta).length > 0) && (
            <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {[...photos, ...Object.keys(photoMeta).filter((k) => k.startsWith("pending-") && !photos.includes(k))].map((pid) => {
                const meta = photoMeta[pid];
                const pending = pid.startsWith("pending-");
                return (
                  <div key={pid} className="relative overflow-hidden rounded-lg border border-slate-700 bg-slate-950">
                    {meta?.preview ? (
                      /* eslint-disable-next-line @next/next/no-img-element */
                      <img src={meta.preview} alt={meta.name} className="h-24 w-full object-cover" />
                    ) : (
                      <div className="flex h-24 items-center justify-center text-[11px] text-slate-500">
                        {pending ? "Uploading…" : "Attached ✓"}
                      </div>
                    )}
                    <div className="truncate px-1.5 py-1 text-[10px] text-slate-300" title={meta?.name ?? pid}>
                      {pending ? "Uploading…" : (meta?.name ?? `${pid.slice(0, 8)}…`)}
                    </div>
                    {meta?.kind && <div className="px-1.5 pb-1 text-[10px] text-slate-500">{meta.kind}</div>}
                    {editable && !pending && (
                      <button onClick={() => removePhoto(pid)} aria-label="Remove photo"
                        className="absolute right-1 top-1 rounded-full bg-slate-950/85 px-1.5 py-0.5 text-[11px] text-slate-400 hover:text-red-300">
                        ✕
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
          {editable && (
            <div className="mt-2 flex flex-wrap gap-2">
              {([
                ["roof", "COMPLETION_PHOTO", "Rooftop / panels", "+ Rooftop / panels photo"],
                ["meter", "COMMISSIONING_TEST", "Meter / electrical", "+ Meter / electrical photo"],
                ["extra", "COMPLETION_PHOTO", "Extra", "+ Another photo"],
              ] as const).map(([key, kind, label, btn]) => (
                <label key={key} className="btn-ghost cursor-pointer !py-1.5 !text-xs">
                  {uploadingKey === key ? (
                    <span className="flex items-center gap-1.5">
                      <span className="h-3 w-3 animate-spin rounded-full border border-sky-400 border-t-transparent" />
                      Uploading…
                    </span>
                  ) : btn}
                  <input type="file" accept="image/*" className="hidden" disabled={uploading}
                    onChange={(e) => { const f = e.target.files?.[0]; if (f) void upload(key, f, kind, label); e.target.value = ""; }} />
                </label>
              ))}
            </div>
          )}
        </div>
        {editable && (
          <div className="flex flex-wrap gap-2">
            <button onClick={save} disabled={busy} className="btn-ghost">Save draft</button>
            {row.status === "COMPLETED" && (
              <button onClick={submit} disabled={busy} className="btn-primary !py-2 !text-xs">
                {busy ? "Submitting…" : "Submit for DISCOM verification"}
              </button>
            )}
          </div>
        )}
        {row.status === "VERIFICATION_PENDING" && (
          <p className="rounded-lg border border-amber-900 bg-amber-950/30 p-2.5 text-xs text-amber-200">
            Submitted for DISCOM verification. Only a DISCOM reviewer can mark this VERIFIED.
          </p>
        )}
        {verified && <p className="rounded-lg border border-green-900 bg-green-950/30 p-2.5 text-xs text-green-200">Verified by the DISCOM — read-only.</p>}
      </div>
    </div>
  );
}

function Field({ label, v, onChange, type = "text", step, disabled }: {
  label: string; v: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string; step?: string; disabled?: boolean;
}) {
  return (
    <div>
      <label className="label">{label}</label>
      <input type={type} step={step} className="input !py-1.5 !text-xs" value={v} onChange={onChange} disabled={disabled} />
    </div>
  );
}
