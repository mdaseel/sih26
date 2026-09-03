"use client";

import maplibregl, { Map as MapLibreMap, Popup } from "maplibre-gl";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  NEUTRAL,
  RISK_COLOURS,
  transformerRisk,
  voltageRisk,
} from "@/lib/risk";
import type { MapData, MapLayerId } from "@/lib/types";

/**
 * 2D geographic map of the feeder.
 *
 * What is real here: the network itself. Buses, lines and transformers come
 * from feeder_network.json, and the spacing between them is true route
 * distance in km, so the scale bar measures something meaningful.
 *
 * What is not real: where it sits on Earth. The IEEE test feeder ships no
 * coordinates, so the anchor point is arbitrary. The street basemap is
 * therefore context for reading distances, never a claim that this network is
 * physically in that place — hence the standing caveat over the canvas and the
 * toggle to switch the streets off entirely.
 *
 * Every colour on this map is driven by a value the backend computed.
 */

export const LAYERS: { id: MapLayerId; label: string; unit: string; hint: string }[] = [
  { id: "risk", label: "Risk", unit: "", hint: "assessment outcome per application" },
  { id: "voltage", label: "Voltage", unit: "pu", hint: "base power flow, no new PV" },
  { id: "transformer_loading", label: "Transformer loading", unit: "%", hint: "base power flow" },
  { id: "line_loading", label: "Line loading", unit: "%", hint: "base power flow" },
  { id: "solar_penetration", label: "Solar penetration", unit: "%", hint: "pending PV vs transformer rating" },
  { id: "hosting_capacity", label: "Hosting capacity", unit: "kW", hint: "bisection on the power flow" },
];

// Shared with the digital twin via lib/risk.ts, so the map and the twin cannot
// disagree about what counts as a violation.
const GREEN = RISK_COLOURS.SAFE.stroke;
const YELLOW = RISK_COLOURS.CAUTION.stroke;
const RED = RISK_COLOURS.CONSTRAINED.stroke;
const GREY = NEUTRAL;

const TONE = { SAFE: GREEN, CAUTION: YELLOW, CONSTRAINED: RED } as const;

export function GridMap({ data }: { data: MapData }) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const popup = useRef<Popup | null>(null);
  const [layer, setLayer] = useState<MapLayerId>("risk");
  const [basemap, setBasemap] = useState(true);
  const [ready, setReady] = useState(false);
  // Bumped when the *current* map finishes its style, to re-run the draw effect.
  const [styleTick, setStyleTick] = useState(0);

  const t = data.thresholds;

  const buses = useMemo(
    () => data.assets.filter((a) => a.asset_type === "BUS" && a.latitude != null),
    [data.assets]
  );

  const trafoLoading = useMemo(() => {
    const out: Record<string, number> = {};
    for (const a of data.assets) {
      if (a.asset_type === "TRANSFORMER") {
        const v = (a.attributes as Record<string, unknown>)?.base_loading_pct;
        if (typeof v === "number") out[a.asset_code] = v;
      }
    }
    return out;
  }, [data.assets]);

  /** Colour for one bus under the active layer. Values come from the backend;
   *  thresholds come from scenario_config.json via the API. */
  function colourFor(bus: (typeof buses)[number]): string {
    const attrs = (bus.attributes ?? {}) as Record<string, unknown>;

    switch (layer) {
      case "voltage": {
        const v = (attrs.base_voltage_pu_measured as number) ?? bus.base_voltage_pu;
        const risk = voltageRisk(v, t);
        return risk ? TONE[risk] : GREY;
      }
      case "transformer_loading": {
        const risk = transformerRisk(trafoLoading[bus.transformer_association ?? ""], t);
        return risk ? TONE[risk] : GREY;
      }
      case "line_loading":
        // Loading belongs to a line, not to a bus. Under this layer the edges
        // carry the colour and the buses stay neutral, rather than every bus
        // inheriting the same feeder-wide maximum and saying nothing.
        return GREY;
      case "solar_penetration": {
        const pending = data.pending_pv_by_bus[bus.asset_code] ?? 0;
        const sn = bus.sn_kva ?? 0;
        if (!sn) return GREY;
        const pct = (pending / sn) * 100;
        if (pct === 0) return GREY;
        return pct > 50 ? RED : pct > 20 ? YELLOW : GREEN;
      }
      case "hosting_capacity": {
        const kw = attrs.hosting_capacity_kw as number | undefined;
        if (kw == null) return GREY;
        return kw < 60 ? RED : kw < 150 ? YELLOW : GREEN;
      }
      case "risk":
      default: {
        const app = data.applications.find((a) => a.pv_bus === bus.asset_code);
        if (!app?.engineering_risk) return GREY;
        return app.engineering_risk === "SAFE"
          ? GREEN
          : app.engineering_risk === "CAUTION"
            ? YELLOW
            : RED;
      }
    }
  }

  // ---- create the map once ----
  useEffect(() => {
    if (!container.current || map.current) return;

    const lats = buses.map((b) => b.latitude as number);
    const lons = buses.map((b) => b.longitude as number);
    const bounds = new maplibregl.LngLatBounds(
      [Math.min(...lons), Math.min(...lats)],
      [Math.max(...lons), Math.max(...lats)]
    );

    map.current = new maplibregl.Map({
      container: container.current,
      // The street basemap is declared here but hidden by default, so toggling
      // it never reloads the style and never has to re-add the data layers.
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            maxzoom: 19,
            attribution: "© OpenStreetMap contributors",
          },
        },
        layers: [
          { id: "bg", type: "background", paint: { "background-color": "#0b1120" } },
          {
            id: "osm-raster",
            type: "raster",
            source: "osm",
            layout: { visibility: "none" },
            // Dimmed so the network stays the subject of the picture.
            paint: { "raster-opacity": 0.55, "raster-saturation": -0.4 },
          },
        ],
      },
      bounds,
      fitBoundsOptions: { padding: 60 },
      attributionControl: false,
    });

    map.current.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.current.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
    map.current.addControl(
      new maplibregl.AttributionControl({ compact: true }),
      "bottom-right"
    );
    map.current.on("load", () => setReady(true));

    return () => {
      map.current?.remove();
      map.current = null;
      // Strict Mode tears this effect down and runs it again. Without clearing
      // the flag it stays true from the destroyed map, and the draw effect then
      // writes to a replacement whose style has not loaded.
      setReady(false);
    };
  }, [buses]);

  // ---- basemap visibility ----
  useEffect(() => {
    const m = map.current;
    if (!m || !m.isStyleLoaded() || !m.getLayer("osm-raster")) return;
    m.setLayoutProperty("osm-raster", "visibility", basemap ? "visible" : "none");
    m.setPaintProperty("bg", "background-color", basemap ? "#1e293b" : "#0b1120");
  }, [basemap, ready, styleTick]);

  // ---- (re)draw sources and layers ----
  useEffect(() => {
    const m = map.current;
    if (!m) return;

    // MapLibre throws "Style is not done loading" if a source is added before
    // the style is ready. Trusting the `ready` flag is not enough: it is React
    // state that can describe a previous map instance. Ask this map directly,
    // and if it is not ready yet, wait for its own load event.
    if (!m.isStyleLoaded()) {
      const onLoad = () => setStyleTick((t) => t + 1);
      m.once("load", onLoad);
      return () => {
        m.off("load", onLoad);
      };
    }

    const busById = new Map(buses.map((b) => [b.asset_code, b]));

    const lineFeatures = data.assets
      .filter((a) => a.asset_type === "LINE")
      .map((a) => {
        const attrs = (a.attributes ?? {}) as Record<string, unknown>;
        const from = busById.get(String(attrs.from_bus));
        const to = busById.get(String(attrs.to_bus));
        if (!from || !to) return null;
        return {
          type: "Feature" as const,
          properties: { name: a.asset_code, loading: attrs.base_loading_pct ?? null },
          geometry: {
            type: "LineString" as const,
            coordinates: [
              [from.longitude as number, from.latitude as number],
              [to.longitude as number, to.latitude as number],
            ],
          },
        };
      })
      .filter(Boolean);

    const busFeatures = buses.map((b) => {
      const attrs = (b.attributes ?? {}) as Record<string, unknown>;
      return {
        type: "Feature" as const,
        properties: {
          code: b.asset_code,
          colour: colourFor(b),
          eligible: b.pv_eligible,
          vn_kv: b.vn_kv,
          transformer: b.transformer_association,
          section: b.feeder_section,
          load_kw: b.existing_load_kw,
          voltage: attrs.base_voltage_pu_measured ?? b.base_voltage_pu,
          hosting_capacity_kw: attrs.hosting_capacity_kw ?? null,
          limiting: attrs.hosting_capacity_limiting_constraint ?? null,
          trafo_loading: trafoLoading[b.transformer_association ?? ""] ?? null,
          pending_kw: data.pending_pv_by_bus[b.asset_code] ?? 0,
        },
        geometry: {
          type: "Point" as const,
          coordinates: [b.longitude as number, b.latitude as number],
        },
      };
    });

    const appFeatures = data.applications.map((a) => ({
      type: "Feature" as const,
      properties: {
        ...a,
        colour:
          a.engineering_risk === "SAFE"
            ? GREEN
            : a.engineering_risk === "CAUTION"
              ? YELLOW
              : a.engineering_risk === "CONSTRAINED"
                ? RED
                : GREY,
      },
      geometry: { type: "Point" as const, coordinates: [a.longitude, a.latitude] },
    }));

    const set = (id: string, data_: object) => {
      const src = m.getSource(id) as maplibregl.GeoJSONSource | undefined;
      if (src) src.setData(data_ as never);
      else m.addSource(id, { type: "geojson", data: data_ as never });
    };

    set("lines", { type: "FeatureCollection", features: lineFeatures });
    set("buses", { type: "FeatureCollection", features: busFeatures });
    set("apps", { type: "FeatureCollection", features: appFeatures });

    if (!m.getLayer("lines-layer")) {
      m.addLayer({
        id: "lines-layer",
        type: "line",
        source: "lines",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": "#475569", "line-width": 2.5, "line-opacity": 0.9 },
      });
      // Bus labels, revealed as you zoom in rather than crowding the overview.
      m.addLayer({
        id: "bus-labels",
        type: "symbol",
        source: "buses",
        minzoom: 12,
        layout: {
          "text-field": ["get", "code"],
          "text-size": 10,
          "text-offset": [0, 1.1],
          "text-anchor": "top",
          "text-allow-overlap": false,
        },
        paint: {
          "text-color": "#cbd5e1",
          "text-halo-color": "#0f172a",
          "text-halo-width": 1.4,
        },
      });
      m.addLayer({
        id: "buses-layer",
        type: "circle",
        source: "buses",
        paint: {
          "circle-radius": ["case", ["get", "eligible"], 6, 4],
          "circle-color": ["get", "colour"],
          "circle-stroke-width": 1,
          "circle-stroke-color": "#0f172a",
          "circle-opacity": 0.9,
        },
      });
      m.addLayer({
        id: "apps-layer",
        type: "circle",
        source: "apps",
        paint: {
          "circle-radius": 11,
          "circle-color": ["get", "colour"],
          "circle-stroke-width": 2.5,
          "circle-stroke-color": "#e2e8f0",
        },
      });

      const show = (e: maplibregl.MapLayerMouseEvent, kind: "bus" | "app") => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as Record<string, unknown>;
        const num = (v: unknown, d = 2) =>
          v === null || v === undefined || v === "null" ? "—" : Number(v).toFixed(d);

        const html =
          kind === "app"
            ? `<div style="font-family:ui-sans-serif,system-ui;font-size:12px;line-height:1.6">
                 <div style="font-weight:700;margin-bottom:4px">${p.application_number}</div>
                 <div>Risk: <b style="color:${p.colour}">${p.engineering_risk ?? "not assessed"}</b></div>
                 <div>Solar requested: ${num(p.new_pv_kw, 1)} kW</div>
                 <div>Feeder: ${p.pv_bus} · ${data.assets.find((a) => a.asset_code === p.pv_bus)?.feeder_section ?? "—"}</div>
                 <div>Transformer: ${data.assets.find((a) => a.asset_code === p.pv_bus)?.transformer_association ?? "—"}</div>
                 <div>Voltage: ${num(p.pv_voltage_pu, 4)} pu (rise ${num(p.voltage_rise_pu, 5)})</div>
                 <div>Transformer loading: ${num(p.max_transformer_loading_pct)}%</div>
                 <div>Line loading: ${num(p.max_line_loading_pct)}%</div>
                 <div style="margin-top:4px;color:#64748b">${p.constraint_reason ?? ""}</div>
               </div>`
            : `<div style="font-family:ui-sans-serif,system-ui;font-size:12px;line-height:1.6">
                 <div style="font-weight:700;margin-bottom:4px">Bus ${p.code}</div>
                 <div>${p.vn_kv} kV · ${p.section ?? "—"}</div>
                 <div>Transformer: ${p.transformer ?? "—"} (${num(p.trafo_loading)}%)</div>
                 <div>Base voltage: ${num(p.voltage, 4)} pu</div>
                 <div>Existing load: ${num(p.load_kw)} kW</div>
                 <div>Hosting capacity: <b>${p.hosting_capacity_kw === null ? "—" : num(p.hosting_capacity_kw, 0) + " kW"}</b>${p.limiting ? ` (${p.limiting})` : ""}</div>
                 <div>Pending solar: ${num(p.pending_kw, 1)} kW</div>
               </div>`;

        popup.current?.remove();
        popup.current = new maplibregl.Popup({ closeButton: true, maxWidth: "320px" })
          .setLngLat(e.lngLat)
          .setHTML(html)
          .addTo(m);
      };

      m.on("click", "buses-layer", (e) => show(e, "bus"));
      m.on("click", "lines-layer", (e) => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as Record<string, unknown>;
        popup.current?.remove();
        popup.current = new maplibregl.Popup({ closeButton: true })
          .setLngLat(e.lngLat)
          .setHTML(
            `<div style="font-family:ui-sans-serif,system-ui;font-size:12px;line-height:1.6">
               <div style="font-weight:700">${p.name}</div>
               <div>Base loading: ${p.loading === null || p.loading === undefined ? "—" : Number(p.loading).toFixed(2) + "%"}</div>
             </div>`
          )
          .addTo(m);
      });
      m.on("click", "apps-layer", (e) => show(e, "app"));
      for (const id of ["buses-layer", "apps-layer"]) {
        m.on("mouseenter", id, () => (m.getCanvas().style.cursor = "pointer"));
        m.on("mouseleave", id, () => (m.getCanvas().style.cursor = ""));
      }
    }
    // Lines carry their own measured loading, so the line-loading layer
    // colours the edges themselves rather than approximating it on the buses.
    if (m.getLayer("lines-layer")) {
      m.setPaintProperty(
        "lines-layer",
        "line-color",
        layer === "line_loading"
          ? ([
              "case",
              ["==", ["get", "loading"], null],
              GREY,
              [">", ["get", "loading"], t.line_loading_hard_pct],
              RED,
              [">=", ["get", "loading"], t.line_loading_caution_pct],
              YELLOW,
              GREEN,
            ] as unknown as string)
          : "#475569"
      );
      m.setPaintProperty("lines-layer", "line-width", layer === "line_loading" ? 3.5 : 2.5);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, styleTick, layer, data, buses, trafoLoading]);

  const active = LAYERS.find((l) => l.id === layer)!;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-1.5">
        {LAYERS.map((l) => (
          <button
            key={l.id}
            onClick={() => setLayer(l.id)}
            className={`rounded-md border px-3 py-1.5 text-xs transition ${
              layer === l.id
                ? "border-sky-600 bg-sky-950/60 text-sky-300"
                : "border-slate-700 text-slate-400 hover:bg-slate-800"
            }`}
          >
            {l.label}
          </button>
        ))}

        <button
          onClick={() => setBasemap((b) => !b)}
          className={`ml-auto rounded-md border px-3 py-1.5 text-xs transition ${
            basemap
              ? "border-slate-600 bg-slate-800 text-slate-200"
              : "border-slate-700 text-slate-400 hover:bg-slate-800"
          }`}
          title="Street basemap is context only — the feeder is not physically located here"
        >
          {basemap ? "Streets on" : "Streets off"}
        </button>
      </div>

      <div className="relative rounded-xl border border-slate-800 bg-slate-950 p-1">
        <div ref={container} style={{ height: 520, borderRadius: 10, overflow: "hidden" }} />
        {basemap && (
          <>
            <div className="pointer-events-none absolute left-4 top-4 z-10 rounded-md border border-amber-900/70 bg-slate-950/85 px-2.5 py-1 text-[11px] text-amber-200">
              Illustrative placement — this feeder is not physically at this location
            </div>
            {/* Rendered here rather than left to MapLibre's attribution control,
                which starts collapsed and came back empty. OpenStreetMap's tile
                usage policy requires attribution to be visible, so it must not
                depend on a control that might not populate. */}
            <div className="absolute bottom-3 right-3 z-10 rounded bg-slate-950/85 px-2 py-0.5 text-[10px] text-slate-400">
              ©{" "}
              <a
                href="https://www.openstreetmap.org/copyright"
                target="_blank"
                rel="noreferrer noopener"
                className="underline hover:text-slate-200"
              >
                OpenStreetMap
              </a>{" "}
              contributors
            </div>
          </>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
        <div className="flex flex-wrap items-center gap-4">
          <span>
            <b className="text-slate-400">{active.label}</b> — {active.hint}
          </span>
          <span className="flex items-center gap-3">
            {[
              [GREEN, "safe / ample"],
              [YELLOW, "caution"],
              [RED, "constrained / limited"],
              [GREY, "no data"],
            ].map(([c, label]) => (
              <span key={label} className="flex items-center gap-1.5">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-full"
                  style={{ background: c }}
                />
                {label}
              </span>
            ))}
          </span>
        </div>
        <span>Large ringed pins are applications</span>
      </div>

      <p className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-[11px] leading-relaxed text-slate-500">
        {data.anchor_note} {data.liveness}
      </p>
    </div>
  );
}
