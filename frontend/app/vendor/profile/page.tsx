"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import type { VendorProfile } from "@/lib/types";

/**
 * Business profile and documents.
 *
 * Status, rating and verification are read-only here — not as a UI courtesy,
 * but because those columns are not writable by a vendor at all (migration
 * 0004). Showing them as editable would promise something the database refuses.
 */
export default function VendorProfilePage() {
  const [data, setData] = useState<VendorProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  const [form, setForm] = useState({
    representative_name: "",
    phone: "",
    address_line: "",
    district: "",
    state: "",
    pincode: "",
    latitude: "",
    longitude: "",
    service_areas: "",
    installation_capacity_kw: "",
    years_experience: "",
  });

  const [doc, setDoc] = useState({ document_type: "", file_path: "", file_name: "" });

  const load = useCallback(async () => {
    try {
      const p = await vendorApi.profile();
      setData(p);
      setForm({
        representative_name: p.vendor.representative_name ?? "",
        phone: p.vendor.phone ?? "",
        address_line: (p.vendor as unknown as { address_line?: string }).address_line ?? "",
        district: p.vendor.district ?? "",
        state: p.vendor.state ?? "",
        pincode: (p.vendor as unknown as { pincode?: string }).pincode ?? "",
        latitude:
          (p.vendor as unknown as { latitude?: number }).latitude?.toString() ?? "",
        longitude:
          (p.vendor as unknown as { longitude?: number }).longitude?.toString() ?? "",
        service_areas: (p.vendor.service_areas ?? []).join(", "),
        installation_capacity_kw: p.vendor.installation_capacity_kw?.toString() ?? "",
        years_experience: p.vendor.years_experience?.toString() ?? "",
      });
    } catch (e) {
      setError((e as ApiError).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setSaved(false);
    try {
      await vendorApi.updateProfile({
        representative_name: form.representative_name || null,
        phone: form.phone || null,
        address_line: form.address_line || null,
        district: form.district || null,
        state: form.state || null,
        pincode: form.pincode || null,
        latitude: form.latitude ? Number(form.latitude) : null,
        longitude: form.longitude ? Number(form.longitude) : null,
        service_areas: form.service_areas
          ? form.service_areas.split(",").map((s) => s.trim()).filter(Boolean)
          : null,
        installation_capacity_kw: form.installation_capacity_kw
          ? Number(form.installation_capacity_kw)
          : null,
        years_experience: form.years_experience ? Number(form.years_experience) : null,
      });
      setSaved(true);
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusy(false);
    }
  }

  async function addDocument(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await vendorApi.addDocument({
        document_type: doc.document_type,
        file_path: doc.file_path,
        file_name: doc.file_name || null,
      });
      setDoc({ document_type: "", file_path: "", file_name: "" });
      await load();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusy(false);
    }
  }

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  if (!data && !error) return <p className="text-sm text-slate-500">Loading…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Profile</h1>
        <p className="mt-1 text-sm text-slate-500">Your business details and documents</p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {data && (
        <div className="card">
          <div className="grid gap-3 text-sm sm:grid-cols-4">
            <Read label="Business" value={data.vendor.business_name} />
            <Read label="Status" value={data.vendor.status} />
            <Read
              label="Visible to customers"
              value={data.visible_to_customers ? "Yes" : "No"}
            />
            <Read
              label="Rating"
              value={data.vendor.rating != null ? `${data.vendor.rating} / 5` : "not rated"}
            />
          </div>
          <p className="mt-3 text-xs text-slate-600">
            Status, rating and verification are set by the DISCOM and cannot be edited
            here.
          </p>
        </div>
      )}

      <form onSubmit={save} className="card space-y-4">
        <h2 className="text-sm font-semibold text-slate-200">Editable details</h2>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">
              Representative<Required />
            </label>
            <input
              required
              className="input"
              value={form.representative_name}
              onChange={(e) => set("representative_name", e.target.value)}
            />
          </div>
          <div>
            <label className="label">
              Phone<Required />
            </label>
            <input
              required
              inputMode="tel"
              className="input"
              value={form.phone}
              onChange={(e) => set("phone", e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="label">
            Address<Required />
          </label>
          <input
            required
            className="input"
            value={form.address_line}
            onChange={(e) => set("address_line", e.target.value)}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="label">
              District<Required />
            </label>
            <input
              required
              className="input"
              value={form.district}
              onChange={(e) => set("district", e.target.value)}
            />
          </div>
          <div>
            <label className="label">
              State<Required />
            </label>
            <input
              required
              className="input"
              value={form.state}
              onChange={(e) => set("state", e.target.value)}
            />
          </div>
          <div>
            <label className="label">
              PIN code<Required />
            </label>
            <input
              required
              inputMode="numeric"
              pattern="[0-9]{6}"
              title="Six digits"
              maxLength={6}
              className="input"
              value={form.pincode}
              onChange={(e) => set("pincode", e.target.value)}
            />
          </div>
        </div>

        {/* An installer with no coordinates cannot be placed on a customer's
            map or measured for distance, so the listing barely works. */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">
              Latitude<Required />
            </label>
            <input
              required
              type="number"
              step="any"
              min={-90}
              max={90}
              className="input"
              value={form.latitude}
              onChange={(e) => set("latitude", e.target.value)}
            />
          </div>
          <div>
            <label className="label">
              Longitude<Required />
            </label>
            <input
              required
              type="number"
              step="any"
              min={-180}
              max={180}
              className="input"
              value={form.longitude}
              onChange={(e) => set("longitude", e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="label">
            Service areas (comma separated)<Required />
          </label>
          <input
            required
            className="input"
            value={form.service_areas}
            onChange={(e) => set("service_areas", e.target.value)}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Installation capacity (kW)</label>
            <input
              type="number"
              min={0}
              className="input"
              value={form.installation_capacity_kw}
              onChange={(e) => set("installation_capacity_kw", e.target.value)}
            />
          </div>
          <div>
            <label className="label">Years of experience</label>
            <input
              type="number"
              min={0}
              className="input"
              value={form.years_experience}
              onChange={(e) => set("years_experience", e.target.value)}
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? "Saving…" : "Save changes"}
          </button>
          {saved && <span className="text-xs text-green-400">Saved</span>}
        </div>
      </form>

      {data && (
        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Documents</h2>

          {data.documents.length === 0 ? (
            <p className="text-sm text-slate-500">No documents attached yet.</p>
          ) : (
            <div className="space-y-2">
              {data.documents.map((d) => (
                <div
                  key={d.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-800 bg-slate-950/40 px-3 py-2 text-xs"
                >
                  <div>
                    <span className="text-slate-200">
                      {data.document_types.find((t) => t.code === d.document_type)?.label ??
                        d.document_type}
                    </span>
                    <span className="ml-2 text-slate-600">{d.file_name ?? d.file_path}</span>
                  </div>
                  <span className={d.is_verified ? "text-green-400" : "text-slate-500"}>
                    {d.is_verified ? "verified by DISCOM" : "awaiting verification"}
                  </span>
                </div>
              ))}
            </div>
          )}

          <form onSubmit={addDocument} className="flex flex-wrap items-end gap-2">
            <div>
              <label className="label">Type</label>
              <select
                required
                className="input !w-64"
                value={doc.document_type}
                onChange={(e) => setDoc((d) => ({ ...d, document_type: e.target.value }))}
              >
                <option value="">Select a document type</option>
                {data.document_types.map((t) => (
                  <option key={t.code} value={t.code}>
                    {t.label}
                    {t.required ? " (required)" : ""}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Reference / path</label>
              <input
                required
                className="input !w-64"
                placeholder="vendors/your-id/document.pdf"
                value={doc.file_path}
                onChange={(e) => setDoc((d) => ({ ...d, file_path: e.target.value }))}
              />
            </div>
            <button type="submit" disabled={busy} className="btn-ghost">
              Attach
            </button>
          </form>

          <p className="text-xs text-slate-600">
            Document types come from configuration, not from this page. Uploaded
            documents are always unverified until a DISCOM reviewer checks them. Binary
            file upload arrives with the secure-upload work in Phase 12; for now this
            records the reference.
          </p>
        </div>
      )}
    </div>
  );
}

/** Marks a field the form will not submit without. */
function Required() {
  return (
    <span className="ml-1 text-red-400" title="Required" aria-hidden="true">
      *
    </span>
  );
}

function Read({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="metric-label">{label}</div>
      <div className="text-slate-300">{value}</div>
    </div>
  );
}
