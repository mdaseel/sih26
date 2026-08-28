"use client";

import { useEffect, useState } from "react";

import { api, ApiError } from "@/lib/api";
import type { CFAEstimate, SchemeOverview } from "@/lib/types";

/**
 * PM Surya Ghar information and an indicative CFA estimate.
 *
 * Every figure and every sentence of policy on this page comes from the
 * scheme_config table, not from code. Where that configuration has not been
 * checked against the official portal, the page says so loudly rather than
 * letting a placeholder pass as policy.
 */
export default function SchemePage() {
  const [scheme, setScheme] = useState<SchemeOverview | null>(null);
  const [capacity, setCapacity] = useState(3);
  const [estimate, setEstimate] = useState<CFAEstimate | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .scheme()
      .then(setScheme)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  useEffect(() => {
    if (capacity <= 0) return;
    api
      .cfaEstimate(capacity)
      .then(setEstimate)
      .catch(() => setEstimate(null));
  }, [capacity]);

  const money = (n: number, currency: string) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(n);

  if (error) {
    return (
      <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
        {error}
      </p>
    );
  }
  if (!scheme) return <p className="text-sm text-slate-500">Loading…</p>;

  const unverified = scheme.cfa_rules.verification_required;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">{scheme.overview.title}</h1>
        <p className="mt-1 text-sm text-slate-500">{scheme.overview.summary}</p>
      </div>

      {/* This must be impossible to miss. */}
      <div className="rounded-lg border border-amber-800 bg-amber-950/40 p-4 text-sm text-amber-100">
        <b>SolarGrid AI is not the government portal.</b>{" "}
        {scheme.not_official_portal.replace("SolarGrid AI is not the official PM Surya Ghar portal and cannot", "It cannot")}{" "}
        <a
          href={scheme.overview.official_portal_url}
          target="_blank"
          rel="noreferrer noopener"
          className="underline hover:text-white"
        >
          Go to the official portal →
        </a>
      </div>

      {unverified && (
        <div className="rounded-lg border border-red-900 bg-red-950/40 p-4 text-sm text-red-200">
          <b>Subsidy figures are unverified placeholders.</b>{" "}
          {scheme.cfa_rules.verification_note} Do not quote these numbers to anyone
          until they have been checked against the official portal.
        </div>
      )}

      {/* ---- what it covers ---- */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">What the scheme covers</h2>
        <ul className="space-y-1.5 text-sm text-slate-300">
          {scheme.overview.what_it_covers.map((item) => (
            <li key={item} className="flex gap-2">
              <span className="text-sky-500">•</span>
              {item}
            </li>
          ))}
        </ul>
      </div>

      {/* ---- eligibility ---- */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Eligibility</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {scheme.eligibility.map((e) => (
            <div key={e.code} className="rounded-lg border border-slate-800 bg-slate-950/40 p-3">
              <div className="text-sm font-medium text-slate-200">{e.label}</div>
              <div className="mt-1 text-xs text-slate-500">{e.detail}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ---- process ---- */}
      <div className="card">
        <h2 className="mb-1 text-sm font-semibold text-slate-200">How the process works</h2>
        <p className="mb-4 text-xs text-slate-500">
          Steps marked <span className="text-sky-400">in SolarGrid</span> happen here;
          the others happen on the official portal.
        </p>
        <ol className="space-y-3">
          {scheme.process_steps.map((s) => (
            <li key={s.step} className="flex gap-3">
              <span
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                  s.in_this_app
                    ? "bg-sky-900 text-sky-200"
                    : "bg-slate-800 text-slate-400"
                }`}
              >
                {s.step}
              </span>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-medium text-slate-200">{s.title}</span>
                  <span className="rounded border border-slate-700 px-1.5 py-0.5 text-[10px] text-slate-500">
                    {s.actor}
                  </span>
                  {s.in_this_app && (
                    <span className="rounded border border-sky-900 bg-sky-950/50 px-1.5 py-0.5 text-[10px] text-sky-300">
                      in SolarGrid
                    </span>
                  )}
                </div>
                <div className="mt-0.5 text-xs text-slate-500">{s.detail}</div>
              </div>
            </li>
          ))}
        </ol>
      </div>

      {/* ---- CFA estimate ---- */}
      <div className="card">
        <h2 className="mb-1 text-sm font-semibold text-slate-200">
          Central Financial Assistance estimate
        </h2>
        <p className="mb-4 text-xs text-slate-500">
          {scheme.cfa_rules.applies_to}
          {scheme.cfa_rules.max_eligible_capacity_kw != null && (
            <> · subsidy applies up to {scheme.cfa_rules.max_eligible_capacity_kw} kW</>
          )}
        </p>

        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label">System size (kW)</label>
            <input
              type="number"
              min={0.5}
              step={0.5}
              className="input !w-36"
              value={capacity}
              onChange={(e) => setCapacity(Number(e.target.value))}
            />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {[1, 2, 3, 5, 10].map((kw) => (
              <button
                key={kw}
                onClick={() => setCapacity(kw)}
                className={`rounded-md border px-2.5 py-1 text-xs transition ${
                  capacity === kw
                    ? "border-sky-600 bg-sky-950/60 text-sky-300"
                    : "border-slate-700 text-slate-400 hover:bg-slate-800"
                }`}
              >
                {kw} kW
              </button>
            ))}
          </div>
        </div>

        {estimate && (
          <div className="mt-4 space-y-3">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
              <div className="metric-label">Indicative subsidy</div>
              <div className="font-mono text-3xl tabular-nums text-slate-100">
                {money(estimate.amount, estimate.currency)}
              </div>
              {estimate.eligible_capacity_kw < estimate.capacity_kw && (
                <p className="mt-2 text-xs text-amber-300">
                  Subsidy is calculated on {estimate.eligible_capacity_kw} kW — the
                  configured eligible maximum — not on the full {estimate.capacity_kw} kW.
                </p>
              )}
              {estimate.capped && (
                <p className="mt-2 text-xs text-amber-300">
                  Capped at the configured maximum of{" "}
                  {money(estimate.max_subsidy ?? 0, estimate.currency)}.
                </p>
              )}
            </div>

            {estimate.breakdown.length > 0 && (
              <div className="overflow-x-auto rounded-lg border border-slate-800">
                <table className="w-full text-xs">
                  <thead className="border-b border-slate-800 text-left uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Band</th>
                      <th className="px-3 py-2 text-right">Capacity</th>
                      <th className="px-3 py-2 text-right">Rate per kW</th>
                      <th className="px-3 py-2 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {estimate.breakdown.map((b) => (
                      <tr key={`${b.from_kw}-${b.to_kw}`} className="border-b border-slate-900 last:border-0">
                        <td className="px-3 py-2 text-slate-400">
                          {b.from_kw} – {b.to_kw} kW
                        </td>
                        <td className="px-3 py-2 text-right font-mono tabular-nums text-slate-300">
                          {b.kw} kW
                        </td>
                        <td className="px-3 py-2 text-right font-mono tabular-nums text-slate-400">
                          {money(b.rate_per_kw, estimate.currency)}
                        </td>
                        <td className="px-3 py-2 text-right font-mono tabular-nums text-slate-200">
                          {money(b.amount, estimate.currency)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <p className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
              {estimate.disclaimer} {estimate.not_official_portal} The subsidy actually
              sanctioned depends on the capacity commissioned and the rules in force at
              the time, decided by the government.
            </p>
          </div>
        )}
      </div>

      {/* ---- official links ---- */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Official sources</h2>
        <div className="space-y-2">
          {scheme.official_links.map((l) => (
            <a
              key={l.url}
              href={l.url}
              target="_blank"
              rel="noreferrer noopener"
              className="block rounded-lg border border-slate-800 bg-slate-950/40 p-3 transition hover:border-slate-700"
            >
              <div className="text-sm text-sky-400">{l.label} ↗</div>
              <div className="mt-0.5 text-xs text-slate-500">{l.detail}</div>
            </a>
          ))}
        </div>
      </div>

      <p className="text-xs text-slate-600">
        Scheme information is configuration, editable in{" "}
        <code className="text-slate-500">{scheme.configuration.editable_at}</code> — no
        policy value is compiled into this application.
      </p>
    </div>
  );
}
