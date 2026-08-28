"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { api, ApiError } from "@/lib/api";
import type { SolarApplication } from "@/lib/types";

export default function ApplicationsPage() {
  const [apps, setApps] = useState<SolarApplication[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listApplications()
      .then(setApps)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">My applications</h1>
          <p className="mt-1 text-sm text-slate-500">
            Every request you have submitted
          </p>
        </div>
        <Link href="/citizen/applications/new" className="btn-primary">
          New application
        </Link>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {apps === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {apps?.length === 0 && (
        <div className="card text-center">
          <p className="text-sm text-slate-400">You have no applications yet.</p>
          <Link href="/citizen/applications/new" className="btn-primary mt-4">
            Create your first application
          </Link>
        </div>
      )}

      {apps && apps.length > 0 && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Application</th>
                <th className="px-4 py-3">Connection point</th>
                <th className="px-4 py-3 text-right">Existing</th>
                <th className="px-4 py-3 text-right">Requested</th>
                <th className="px-4 py-3 text-right">Total</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {apps.map((a) => (
                <tr
                  key={a.id}
                  className="border-b border-slate-900 last:border-0 hover:bg-slate-900/40"
                >
                  <td className="px-4 py-3 font-mono text-slate-200">
                    {a.application_number}
                  </td>
                  <td className="px-4 py-3 text-slate-400">Bus {a.pv_bus}</td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                    {Number(a.existing_pv_kw).toFixed(1)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-200">
                    {Number(a.new_pv_kw).toFixed(1)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-400">
                    {Number(a.total_pv_kw).toFixed(1)}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-400">
                      {a.status.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/citizen/applications/${a.id}`}
                      className="text-sky-400 hover:underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
