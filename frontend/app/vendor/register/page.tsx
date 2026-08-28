"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import { supabase } from "@/lib/supabase";

/**
 * Vendor registration.
 *
 * Two steps in one page: create the account if the visitor has none, then the
 * business profile. The profile is always created PENDING — the form has no
 * status field, and the server would refuse one anyway.
 */
export default function VendorRegister() {
  const router = useRouter();
  const [signedIn, setSignedIn] = useState<boolean | null>(null);

  const [account, setAccount] = useState({ email: "", password: "" });
  const [form, setForm] = useState({
    business_name: "",
    representative_name: "",
    phone: "",
    address_line: "",
    district: "",
    state: "",
    pincode: "",
    registration_number: "",
    gst_number: "",
    service_areas: "",
    installation_capacity_kw: "",
    years_experience: "",
  });

  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSignedIn(Boolean(data.session)));
  }, []);

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setNotice(null);
    setBusy(true);

    try {
      if (!signedIn) {
        if (account.password.length < 8) {
          throw new Error("Password must be at least 8 characters.");
        }
        const { data, error } = await supabase.auth.signUp({
          email: account.email,
          password: account.password,
        });
        if (error) throw new Error(error.message);
        if (!data.session) {
          setNotice(
            "Account created. Confirm your email address, sign in, then complete your business profile."
          );
          setBusy(false);
          return;
        }
      }

      await vendorApi.register({
        business_name: form.business_name,
        representative_name: form.representative_name || null,
        phone: form.phone || null,
        address_line: form.address_line || null,
        district: form.district || null,
        state: form.state || null,
        pincode: form.pincode || null,
        registration_number: form.registration_number || null,
        gst_number: form.gst_number || null,
        service_areas: form.service_areas
          ? form.service_areas.split(",").map((s) => s.trim()).filter(Boolean)
          : [],
        installation_capacity_kw: form.installation_capacity_kw
          ? Number(form.installation_capacity_kw)
          : null,
        years_experience: form.years_experience ? Number(form.years_experience) : null,
      });

      router.replace("/vendor/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : (e as ApiError).message);
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-semibold text-slate-100">Register your business</h1>
        <p className="mt-2 text-sm text-slate-500">
          Your profile is reviewed by the DISCOM before customers can find you.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-6">
        {signedIn === false && (
          <div className="card space-y-4">
            <h2 className="text-sm font-semibold text-slate-200">Account</h2>
            <div>
              <label className="label">Email</label>
              <input
                type="email"
                required
                className="input"
                value={account.email}
                onChange={(e) => setAccount((a) => ({ ...a, email: e.target.value }))}
                autoComplete="email"
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                required
                minLength={8}
                className="input"
                value={account.password}
                onChange={(e) => setAccount((a) => ({ ...a, password: e.target.value }))}
                autoComplete="new-password"
              />
            </div>
          </div>
        )}

        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Business</h2>

          <div>
            <label className="label">Business name</label>
            <input
              required
              className="input"
              value={form.business_name}
              onChange={(e) => set("business_name", e.target.value)}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Representative</label>
              <input
                className="input"
                value={form.representative_name}
                onChange={(e) => set("representative_name", e.target.value)}
              />
            </div>
            <div>
              <label className="label">Phone</label>
              <input
                className="input"
                value={form.phone}
                onChange={(e) => set("phone", e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="label">Address</label>
            <input
              className="input"
              value={form.address_line}
              onChange={(e) => set("address_line", e.target.value)}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="label">District</label>
              <input
                className="input"
                value={form.district}
                onChange={(e) => set("district", e.target.value)}
              />
            </div>
            <div>
              <label className="label">State</label>
              <input
                className="input"
                value={form.state}
                onChange={(e) => set("state", e.target.value)}
              />
            </div>
            <div>
              <label className="label">PIN code</label>
              <input
                className="input"
                value={form.pincode}
                onChange={(e) => set("pincode", e.target.value)}
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Registration number</label>
              <input
                className="input"
                value={form.registration_number}
                onChange={(e) => set("registration_number", e.target.value)}
              />
            </div>
            <div>
              <label className="label">GST number</label>
              <input
                className="input"
                value={form.gst_number}
                onChange={(e) => set("gst_number", e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="label">Service areas (comma separated)</label>
            <input
              className="input"
              placeholder="Demo District, Demo North"
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
        </div>

        {error && (
          <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
            {error}
          </p>
        )}
        {notice && (
          <p className="rounded-lg border border-sky-900 bg-sky-950/40 p-3 text-sm text-sky-200">
            {notice}
          </p>
        )}

        <div className="flex items-center gap-3">
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? "Submitting…" : "Register"}
          </button>
          <Link href="/vendor/login" className="text-sm text-slate-400 hover:underline">
            Already registered? Sign in
          </Link>
        </div>

        <p className="text-xs text-slate-600">
          Registrations start as PENDING. Customers cannot see your business until a
          DISCOM reviewer approves it.
        </p>
      </form>
    </div>
  );
}
