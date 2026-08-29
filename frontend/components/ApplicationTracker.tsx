"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { api, ApiError } from "@/lib/api";
import {
  isHalted,
  resolveStages,
  stageIndexFor,
  TERMINAL,
  type ResolvedStage,
  type StageState,
} from "@/lib/tracking";
import type { ApplicationStatus, StatusHistoryRow } from "@/lib/types";

const REFRESH_MS = 20_000;

/**
 * Where an application has got to, and when each step actually happened.
 *
 * The stages below are a citizen-facing reading of the status column — a
 * householder does not need to know the difference between ASSESSING and
 * ASSESSED, only that their roof is being checked against the grid. The
 * mapping is the whole of the interpretation; nothing else here decides
 * anything.
 *
 * Timestamps come from application_status_history, which a database trigger
 * writes on every transition. So a tick against a stage means the application
 * really was in that state at that moment. Stages with no history row are
 * drawn as pending even when a later stage has been reached: skipping forward
 * is a real thing that happens, and inventing the missing timestamps would be
 * the one lie a delivery tracker must never tell.
 */

// ---------------------------------------------------------------
//  Presentation
// ---------------------------------------------------------------

function formatWhen(iso: string | null): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return d.toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const NODE: Record<StageState, string> = {
  done: "border-sky-600 bg-sky-600 text-white",
  current: "border-sky-400 bg-slate-950 text-sky-300",
  stopped: "border-red-600 bg-red-600 text-white",
  pending: "border-slate-700 bg-slate-950 text-slate-600",
};

const LABEL: Record<StageState, string> = {
  done: "text-slate-300",
  current: "text-sky-300",
  stopped: "text-red-300",
  pending: "text-slate-600",
};

function Node({ stage, index }: { stage: ResolvedStage; index: number }) {
  return (
    <span className="relative flex h-7 w-7 shrink-0 items-center justify-center">
      {stage.state === "current" && (
        <span className="track-halo absolute inset-0 rounded-full bg-sky-500" />
      )}
      <span
        className={`relative flex h-7 w-7 items-center justify-center rounded-full border-2 text-[11px] font-semibold transition-colors ${NODE[stage.state]}`}
      >
        {stage.state === "done" ? "✓" : stage.state === "stopped" ? "!" : index + 1}
      </span>
    </span>
  );
}

/** The rail between two nodes. Only the segment being travelled animates. */
function Rail({ state, vertical }: { state: StageState; vertical?: boolean }) {
  const base = vertical ? "w-0.5 flex-1 rounded-full" : "h-0.5 flex-1 rounded-full";
  if (state === "done") return <span className={`${base} bg-sky-600`} />;
  if (state === "current")
    return <span className={`${base} ${vertical ? "track-live-v" : "track-live"}`} />;
  if (state === "stopped") return <span className={`${base} bg-red-900`} />;
  return <span className={`${base} bg-slate-800`} />;
}

export function ApplicationTracker({
  applicationId,
  status,
  compact = false,
  live = true,
}: {
  applicationId: string;
  status: ApplicationStatus;
  /** Drops the per-stage descriptions, for use inside a list row. */
  compact?: boolean;
  /** Poll for transitions while this is on screen. */
  live?: boolean;
}) {
  const [history, setHistory] = useState<StatusHistoryRow[]>([]);
  const [status_, setStatus] = useState<ApplicationStatus>(status);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshedAt, setRefreshedAt] = useState<Date | null>(null);
  const mounted = useRef(true);

  // The parent owns the status; a fresh one from a reload wins over ours.
  useEffect(() => setStatus(status), [status]);

  const load = useCallback(async () => {
    try {
      const [timeline, detail] = await Promise.all([
        api.applicationTimeline(applicationId),
        api.getApplication(applicationId),
      ]);
      if (!mounted.current) return;
      setHistory(timeline.history);
      setStatus(detail.application.status);
      setRefreshedAt(new Date());
      setError(null);
    } catch (e) {
      if (mounted.current) setError((e as ApiError).message);
    } finally {
      if (mounted.current) setLoading(false);
    }
  }, [applicationId]);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => {
      mounted.current = false;
    };
  }, [load]);

  // Poll only while something can still change, and only while mounted. A
  // finished application is polled zero times: there is nothing to see, and
  // the backend has better things to do than answer the same question forever.
  const settled = TERMINAL.includes(status_);
  useEffect(() => {
    if (!live || settled) return;
    const id = window.setInterval(load, REFRESH_MS);
    return () => window.clearInterval(id);
  }, [live, settled, load]);

  const stages = useMemo(() => resolveStages(status_, history), [status_, history]);
  const halted = isHalted(status_);
  const currentIndex = stageIndexFor(status_);
  const current = stages[currentIndex] ?? null;

  if (loading && history.length === 0) {
    return (
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <span className="h-2 w-2 animate-pulse rounded-full bg-slate-600" />
        Loading progress…
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* ---- headline ---- */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          {!settled && !halted && (
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky-500 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-sky-400" />
            </span>
          )}
          <div>
            <div
              className={`text-sm font-medium ${halted ? "text-red-300" : "text-slate-200"}`}
            >
              {halted
                ? status_ === "REJECTED"
                  ? "Rejected by the DISCOM"
                  : "Cancelled"
                : (current?.label ?? "In progress")}
            </div>
            {!compact && (
              <div className="text-xs text-slate-500">
                {halted
                  ? "This application will not progress further."
                  : (current?.detail ?? "")}
              </div>
            )}
          </div>
        </div>

        {live && !settled && (
          <span className="text-[11px] text-slate-600">
            {refreshedAt
              ? `Updated ${refreshedAt.toLocaleTimeString(undefined, {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                })}`
              : "Live"}
          </span>
        )}
      </div>

      {error && <p className="text-xs text-amber-400">Could not refresh: {error}</p>}

      {/* ---- horizontal rail (md and up) ---- */}
      <div className="hidden md:block">
        <div className="flex items-center">
          {stages.map((stage, i) => (
            <div
              key={stage.key}
              className={`track-enter flex min-w-0 flex-1 items-center last:flex-none`}
              style={{ animationDelay: `${i * 45}ms` }}
            >
              <div className="flex min-w-0 flex-col items-center gap-1.5">
                <Node stage={stage} index={i} />
                <div className="w-24 text-center">
                  <div className={`text-[11px] leading-tight ${LABEL[stage.state]}`}>
                    {stage.label}
                  </div>
                  <div className="mt-0.5 h-3 text-[10px] leading-tight text-slate-600">
                    {formatWhen(stage.at) ?? ""}
                  </div>
                </div>
              </div>
              {i < stages.length - 1 && (
                <div className="-mt-6 flex flex-1 items-center px-1">
                  <Rail
                    state={
                      i < currentIndex ? "done" : i === currentIndex ? stages[i].state : "pending"
                    }
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ---- vertical rail (below md) ---- */}
      <ol className="space-y-0 md:hidden">
        {stages.map((stage, i) => (
          <li
            key={stage.key}
            className="track-enter flex gap-3"
            style={{ animationDelay: `${i * 45}ms` }}
          >
            <div className="flex flex-col items-center">
              <Node stage={stage} index={i} />
              {i < stages.length - 1 && (
                <div className="flex min-h-[28px] flex-1 py-1">
                  <Rail
                    state={
                      i < currentIndex ? "done" : i === currentIndex ? stages[i].state : "pending"
                    }
                    vertical
                  />
                </div>
              )}
            </div>
            <div className="pb-3">
              <div className={`text-sm leading-7 ${LABEL[stage.state]}`}>{stage.label}</div>
              {!compact && stage.state !== "pending" && (
                <div className="text-xs text-slate-500">{stage.detail}</div>
              )}
              {stage.at && (
                <div className="mt-0.5 text-[11px] text-slate-600">{formatWhen(stage.at)}</div>
              )}
            </div>
          </li>
        ))}
      </ol>

      {/* ---- what was actually recorded ---- */}
      {!compact && history.length > 0 && (
        <details className="rounded-lg border border-slate-800 bg-slate-950/40">
          <summary className="cursor-pointer px-3 py-2 text-xs text-slate-500 hover:text-slate-300">
            Full history ({history.length} {history.length === 1 ? "entry" : "entries"})
          </summary>
          <ul className="scroll-pane max-h-52 space-y-1 border-t border-slate-800 px-3 py-2">
            {history
              .slice()
              .reverse()
              .map((row) => (
                <li key={row.id} className="flex flex-wrap items-baseline gap-2 text-xs">
                  <span className="text-slate-600">{formatWhen(row.created_at)}</span>
                  <span className="text-slate-300">{row.to_status.replace(/_/g, " ")}</span>
                  {row.from_status && (
                    <span className="text-slate-600">
                      (from {row.from_status.replace(/_/g, " ")})
                    </span>
                  )}
                  {row.note && <span className="text-slate-500">· {row.note}</span>}
                </li>
              ))}
          </ul>
        </details>
      )}
    </div>
  );
}
