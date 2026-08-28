"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { RiskBadge } from "@/components/RiskBadge";
import { ApiError, discomApi } from "@/lib/api";
import type { DiscomApplication, RiskLevel } from "@/lib/types";

type Filter = "ALL" | "PENDING" | RiskLevel;

export default function DiscomApplications() {
  const [apps, setApps] = useState<DiscomApplication[] | null>(null);
  const [filter, setFilter] = useState<Filter>("PENDING");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    discomApi
      .applications()
      .then(setApps)
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const shown = useMemo(() => {
    if (!apps) return [];
    if (filter === "ALL") return apps;
    if (filter === "PENDING")
      return apps.filter((a) =>
        ["SUBMITTED", "ASSESSED", "UNDER_DISCOM_REVIEW", "ENGINEERING_REVIEW"].includes(a.status)
      );
    return apps.filter((a) => a.engineering_risk === filter);
  }, [apps, filter]);

  const counts = useMemo(() => {
    if (!apps) return null;
    return {
      ALL: apps.length,
      PENDING: apps.filter((a) =>
        ["SUBMITTED", "ASSESSED", "UNDER_DISCOM_REVIEW", "ENGINEERING_REVIEW"].includes(a.status)
      ).length,
      SAFE: apps.filter((a) => a.engineering_risk === "SAFE").length,
      CAUTION: apps.filter((a) => a.engineering_risk === "CAUTION").length,
      CONSTRAINED: apps.filter((a) => a.engineering_risk === "CONSTRAINED").length,
    };
  }, [apps]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Applications</h1>
        <p className="mt-1 text-sm text-slate-500">
          Every connection request, with its engineering verdict
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {counts && (
        <div className="flex flex-wrap gap-1.5">
          {(["PENDING", "ALL", "SAFE", "CAUTION", "CONSTRAINED"] as Filter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-md border px-3 py-1.5 text-xs transition ${
                filter === f
                  ? "border-sky-600 bg-sky-950/60 text-sky-300"
                  : "border-slate-700 text-slate-400 hover:bg-slate-800"
              }`}
            >
              {f.replace("_", " ")}{" "}
              <span className="ml-1 text-slate-500">{counts[f as keyof typeof counts]}</span>
            </button>
          ))}
        </div>
      )}

      {apps === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {apps && shown.length === 0 && (
        <div className="card text-sm text-slate-500">No applications in this view.</div>
      )}

      {shown.length > 0 && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Application</th>
                <th className="px-4 py-3">Applicant</th>
                <th className="px-4 py-3">Bus</th>
                <th className="px-4 py-3 text-right">Requested</th>
                <th className="px-4 py-3">Engineering</th>
                <th className="px-4 py-3">ML</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {shown.map((a) => (
                <tr
                  key={a.id}
                  className="border-b border-slate-900 last:border-0 hover:bg-slate-900/40"
                >
                  <td className="px-4 py-3 font-mono text-slate-200">{a.application_number}</td>
                  <td className="px-4 py-3 text-slate-400">{a.applicant_name}</td>
                  <td className="px-4 py-3 text-slate-400">{a.pv_bus}</td>
                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-200">
                    {Number(a.new_pv_kw).toFixed(1)} kW
                  </td>
                  <td className="px-4 py-3">
                    {a.engineering_risk ? (
                      <RiskBadge risk={a.engineering_risk} size="sm" />
                    ) : (
                      <span className="text-xs text-slate-600">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {a.ml_prediction ? (
                      <span
                        className={`text-xs ${
                          a.ml_agrees_with_engineering === false
                            ? "text-amber-400"
                            : "text-slate-500"
                        }`}
                      >
                        {a.ml_prediction}
                        {a.ml_agrees_with_engineering === false && " ⚠"}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-600">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-400">
                      {a.status.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/discom/applications/${a.id}`}
                      className="text-sky-400 hover:underline"
                    >
                      Review
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
