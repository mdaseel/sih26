"use client";

import { useMemo, useState } from "react";

import {
  fillFor,
  strokeFor,
  transformerRisk,
  voltageRiseRisk,
  voltageRisk,
  worstRisk,
} from "@/lib/risk";
import type { TwinResponse } from "@/lib/types";

/**
 * 2D digital twin — a single-line diagram of the electrical path from the
 * substation to the customer.
 *
 * Everything drawn here comes from the backend: the nodes and edges are the
 * feeder model's own topology, and every voltage, loading and flow direction
 * is a power-flow result. This component decides colour and position; it never
 * decides a number.
 *
 * Asset colouring applies the same thresholds the engineering verdict used —
 * they arrive in the response as thresholds_snapshot — to each asset's own
 * measured value. That is why an unaffected upstream bus stays green while the
 * connection point turns red: they are judged individually, not painted with
 * the overall verdict.
 */

type Mode = "before" | "after";

const RISK_FILL = {
  SAFE: "#052e16",
  CAUTION: "#3b2f05",
  CONSTRAINED: "#450a0a",
} as const;

const RISK_STROKE = {
  SAFE: "#22c55e",
  CAUTION: "#eab308",
  CONSTRAINED: "#ef4444",
} as const;

type Risk = keyof typeof RISK_FILL;

const NODE_W = 150;
const ROW_Y = 150;

export function TwinDiagram({ twin }: { twin: TwinResponse }) {
  const [mode, setMode] = useState<Mode>("after");
  const [selected, setSelected] = useState<string | null>(null);

  const t = twin.assessment.engineering.thresholds_snapshot;
  const elements = twin.elements;
  const path = twin.topology.path;
  const pvBus = twin.assessment.metrics.pv_bus;

  /** A bus is judged on its own voltage, and — if it is the connection point —
   *  on its own voltage rise. */
  const busRisk = useMemo(() => {
    const out: Record<string, Risk> = {};
    for (const [bus, v] of Object.entries(elements.buses)) {
      const pu = mode === "before" ? v.before_pu : v.after_pu;
      // Judged on its own voltage, and — if it is the connection point — on
      // its own rise. Shared with the map so both views agree.
      const own = voltageRisk(pu, t);
      const rise = mode === "after" && bus === pvBus ? voltageRiseRisk(v.delta_pu, t) : null;
      out[bus] = (worstRisk(own, rise) ?? "SAFE") as Risk;
    }
    return out;
  }, [elements.buses, mode, pvBus, t]);

  const nodes = twin.topology.nodes;
  const width = nodes.length * NODE_W + 80;
  const trafo = Object.values(elements.transformers)[0];

  const edgeFor = (a: string, b: string) =>
    twin.topology.edges.find(
      (e) => (e.source === a && e.target === b) || (e.source === b && e.target === a)
    );

  return (
    <div className="card">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">2D digital twin</h3>
          <p className="text-xs text-slate-500">
            Electrical path · substation → transformer → connection point → premises
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5 text-[10px] font-semibold uppercase tracking-wide">
            <span className="rounded border border-slate-700 bg-slate-900 px-2 py-0.5 text-slate-300">Grid · Substation</span>
            <span className="rounded border border-slate-700 bg-slate-900 px-2 py-0.5 text-slate-300">
              Transformer · {trafo?.name ?? "—"}
            </span>
            <span className="rounded border border-sky-800 bg-sky-950/60 px-2 py-0.5 text-sky-300">
              Target house · Bus {pvBus}
            </span>
            <span className="rounded border border-amber-800 bg-amber-950/50 px-2 py-0.5 text-amber-300">
              Solar · {elements.energy_balance.solar_generation_kw.toFixed(1)} kW
            </span>
            {mode === "after" && elements.energy_balance.local_export_kw > 0.05 ? (
              <span className="rounded border border-sky-700 bg-sky-950/60 px-2 py-0.5 text-sky-200">
                Reverse energy · export {elements.energy_balance.local_export_kw.toFixed(1)} kW → grid
              </span>
            ) : (
              <span className="rounded border border-slate-700 bg-slate-900 px-2 py-0.5 text-slate-400">
                Supply · grid → house
              </span>
            )}
          </div>
        </div>

        <div className="flex rounded-lg border border-slate-700 p-0.5">
          {(["before", "after"] as Mode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                mode === m ? "bg-slate-700 text-slate-100" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {m === "before" ? "Before (existing)" : "After (with proposed PV)"}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/70">
        <svg
          viewBox={`0 0 ${width} 260`}
          className="min-w-[860px]"
          style={{ width: "100%", height: 260 }}
          role="img"
          aria-label="Single-line diagram of the electrical path"
        >
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
            </marker>
            <style>{`
              .flow { stroke-dasharray: 7 9; animation: dash 1.1s linear infinite; }
              .flow-rev { animation-direction: reverse; }
              @keyframes dash { to { stroke-dashoffset: -16; } }
              @media (prefers-reduced-motion: reduce) { .flow { animation: none; } }
            `}</style>
          </defs>

          {/* ---- edges ---- */}
          {nodes.slice(0, -1).map((n, i) => {
            const next = nodes[i + 1];
            const x1 = i * NODE_W + 70;
            const x2 = (i + 1) * NODE_W + 30;
            const edge = edgeFor(n.id, next.id);
            const isTrafo = edge?.type === "TRANSFORMER";
            const isService = edge?.type === "SERVICE";

            const line = edge ? elements.lines[edge.id] : undefined;
            const dir = isService
              ? mode === "after" && elements.energy_balance.local_export_kw > 0
                ? "REVERSE"
                : "FORWARD"
              : isTrafo && trafo
                ? mode === "before"
                  ? trafo.direction_before
                  : trafo.direction_after
                : line
                  ? mode === "before"
                    ? line.direction_before
                    : line.direction_after
                  : "FORWARD";

            const reversed = dir === "REVERSE";
            const stroke = reversed ? "#38bdf8" : "#475569";

            return (
              <g key={`${n.id}-${next.id}`}>
                <line
                  x1={x1}
                  y1={ROW_Y}
                  x2={x2}
                  y2={ROW_Y}
                  stroke={stroke}
                  strokeWidth={isService ? 2 : 3}
                  strokeDasharray={isService ? "4 4" : undefined}
                />
                <line
                  x1={x1}
                  y1={ROW_Y}
                  x2={x2}
                  y2={ROW_Y}
                  stroke={reversed ? "#7dd3fc" : "#94a3b8"}
                  strokeWidth={2}
                  className={`flow ${reversed ? "flow-rev" : ""}`}
                />
                {isTrafo && (
                  <g>
                    <circle
                      cx={(x1 + x2) / 2 - 7}
                      cy={ROW_Y}
                      r="11"
                      fill="none"
                      stroke={strokeFor(
                        trafo
                          ? transformerRisk(
                              mode === "before" ? trafo.before_pct : trafo.after_pct,
                              t
                            )
                          : null
                      )}
                      strokeWidth="2"
                    />
                    <circle
                      cx={(x1 + x2) / 2 + 7}
                      cy={ROW_Y}
                      r="11"
                      fill="none"
                      stroke={strokeFor(
                        trafo
                          ? transformerRisk(
                              mode === "before" ? trafo.before_pct : trafo.after_pct,
                              t
                            )
                          : null
                      )}
                      strokeWidth="2"
                    />
                    <text
                      x={(x1 + x2) / 2}
                      y={ROW_Y - 26}
                      textAnchor="middle"
                      className="fill-slate-300"
                      style={{ fontSize: 11, fontWeight: 600 }}
                    >
                      {trafo?.name ?? edge?.label}
                    </text>
                    {trafo && (
                      <text
                        x={(x1 + x2) / 2}
                        y={ROW_Y + 34}
                        textAnchor="middle"
                        className="fill-slate-400"
                        style={{ fontSize: 10, fontFamily: "monospace" }}
                      >
                        {(mode === "before" ? trafo.before_pct : trafo.after_pct).toFixed(1)}%
                      </text>
                    )}
                  </g>
                )}
                {!isTrafo && line && (
                  <text
                    x={(x1 + x2) / 2}
                    y={ROW_Y - 12}
                    textAnchor="middle"
                    className="fill-slate-600"
                    style={{ fontSize: 9, fontFamily: "monospace" }}
                  >
                    {(mode === "before" ? line.before_pct : line.after_pct).toFixed(1)}%
                  </text>
                )}
              </g>
            );
          })}

          {/* ---- nodes ---- */}
          {nodes.map((n, i) => {
            const x = i * NODE_W + 30;
            const isHouse = n.type === "HOUSE";
            const isSub = n.type === "SUBSTATION";
            const v = elements.buses[n.id];
            const risk: Risk = isHouse
              ? busRisk[pvBus] ?? "SAFE"
              : (busRisk[n.id] ?? "SAFE");
            const isPv = n.id === pvBus;

            return (
              <g
                key={n.id}
                onClick={() => setSelected(selected === n.id ? null : n.id)}
                style={{ cursor: "pointer" }}
              >
                {isSub ? (
                  <rect
                    x={x}
                    y={ROW_Y - 24}
                    width="40"
                    height="48"
                    rx="4"
                    fill="#1e293b"
                    stroke="#94a3b8"
                    strokeWidth="2"
                  />
                ) : isHouse ? (
                  <g>
                    <path
                      d={`M ${x} ${ROW_Y + 16} L ${x} ${ROW_Y - 6} L ${x + 20} ${ROW_Y - 22} L ${x + 40} ${ROW_Y - 6} L ${x + 40} ${ROW_Y + 16} Z`}
                      fill={fillFor(risk)}
                      stroke={strokeFor(risk)}
                      strokeWidth="2"
                    />
                    {/* Solar array, drawn only when there is generation. */}
                    {mode === "after" && elements.energy_balance.solar_generation_kw > 0 && (
                      <rect
                        x={x + 6}
                        y={ROW_Y - 18}
                        width="18"
                        height="9"
                        rx="1"
                        fill="#0ea5e9"
                        stroke="#7dd3fc"
                        strokeWidth="1"
                        transform={`rotate(-38 ${x + 15} ${ROW_Y - 13})`}
                      />
                    )}
                  </g>
                ) : (
                  <rect
                    x={x}
                    y={ROW_Y - 18}
                    width="40"
                    height="36"
                    rx="4"
                    fill={fillFor(risk)}
                    stroke={strokeFor(risk)}
                    strokeWidth={isPv ? 3 : 2}
                  />
                )}

                <text
                  x={x + 20}
                  y={ROW_Y - 34}
                  textAnchor="middle"
                  className={isPv ? "fill-sky-300" : "fill-slate-400"}
                  style={{ fontSize: 11, fontWeight: isPv ? 700 : 500 }}
                >
                  {isSub ? "Substation" : isHouse ? "Premises" : n.label}
                </text>

                {v && !isHouse && (
                  <text
                    x={x + 20}
                    y={ROW_Y + 34}
                    textAnchor="middle"
                    className="fill-slate-300"
                    style={{ fontSize: 10, fontFamily: "monospace" }}
                  >
                    {(mode === "before" ? v.before_pu : v.after_pu).toFixed(4)}
                  </text>
                )}

                {v && !isHouse && mode === "after" && Math.abs(v.delta_pu) >= 0.0005 && (
                  <text
                    x={x + 20}
                    y={ROW_Y + 46}
                    textAnchor="middle"
                    className={
                      Math.abs(v.delta_pu) > (t.voltage_rise_hard_pu ?? 0.05)
                        ? "fill-red-400"
                        : "fill-sky-400"
                    }
                    style={{ fontSize: 9, fontFamily: "monospace" }}
                  >
                    {v.delta_pu >= 0 ? "+" : ""}
                    {v.delta_pu.toFixed(4)}
                  </text>
                )}
              </g>
            );
          })}

          {/* ---- direction legend ---- */}
          <g transform="translate(20, 226)">
            <line x1="0" y1="0" x2="26" y2="0" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrow)" />
            <text x="34" y="4" className="fill-slate-500" style={{ fontSize: 10 }}>
              grid → premises
            </text>
            <line x1="150" y1="0" x2="176" y2="0" stroke="#7dd3fc" strokeWidth="2" markerEnd="url(#arrow)" />
            <text x="184" y="4" className="fill-slate-500" style={{ fontSize: 10 }}>
              export → grid (reverse flow)
            </text>
          </g>
        </svg>
      </div>

      {/* ---- energy balance ---- */}
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Tile
          label="Grid supply"
          value={(mode === "before"
            ? elements.energy_balance.grid_supply_before_kw
            : elements.energy_balance.grid_supply_after_kw
          ).toFixed(0)}
          unit="kW"
          hint="measured at the source"
        />
        <Tile
          label="Solar generation"
          value={mode === "after" ? elements.energy_balance.solar_generation_kw.toFixed(1) : "0.0"}
          unit="kW"
          hint="at this connection point"
        />
        <Tile
          label="Local consumption"
          value={elements.energy_balance.local_consumption_kw.toFixed(2)}
          unit="kW"
          hint="modelled load at this bus"
        />
        <Tile
          label="Grid export"
          value={mode === "after" ? elements.energy_balance.local_export_kw.toFixed(1) : "0.0"}
          unit="kW"
          hint="generation beyond local load"
          highlight={mode === "after" && elements.energy_balance.local_export_kw > 0}
        />
      </div>

      {selected && elements.buses[selected] && (
        <div className="mt-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs">
          <span className="font-semibold text-slate-300">Bus {selected}</span>
          <span className="ml-3 font-mono text-slate-400">
            {elements.buses[selected].before_pu.toFixed(5)} →{" "}
            {elements.buses[selected].after_pu.toFixed(5)} pu (
            {elements.buses[selected].delta_pu >= 0 ? "+" : ""}
            {elements.buses[selected].delta_pu.toFixed(5)})
          </span>
        </div>
      )}

      <p className="mt-3 text-[11px] text-slate-600">
        Topology and every value come from the backend power flow on{" "}
        {twin.assessment.metrics.network_file}. Node positions are an electrical
        schematic — the feeder model carries no geographic coordinates.
      </p>
    </div>
  );
}

function Tile({
  label,
  value,
  unit,
  hint,
  highlight,
}: {
  label: string;
  value: string;
  unit: string;
  hint?: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-lg border p-3 ${
        highlight ? "border-sky-800 bg-sky-950/40" : "border-slate-800 bg-slate-900/40"
      }`}
    >
      <div className="metric-label">{label}</div>
      <div className={`font-mono text-lg tabular-nums ${highlight ? "text-sky-300" : "text-slate-100"}`}>
        {value}
        <span className="ml-1 text-xs text-slate-500">{unit}</span>
      </div>
      {hint && <div className="mt-1 text-[11px] text-slate-600">{hint}</div>}
    </div>
  );
}
