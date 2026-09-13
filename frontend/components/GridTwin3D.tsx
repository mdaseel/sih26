"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import {
  strokeFor,
  transformerRisk,
  voltageRisk,
  voltageRiseRisk,
  worstRisk,
  lineRisk,
} from "@/lib/risk";
import type { BuildingFootprint, TwinResponse } from "@/lib/types";

export interface GridHouse {
  house_id: string;
  pv_bus: string;
  latitude: number;
  longitude: number;
}

const CESIUM_BASE_URL = "/cesium";
const RISK_CSS: Record<string, string> = {
  SAFE: "#22c55e",
  CAUTION: "#eab308",
  CONSTRAINED: "#ef4444",
};
const FLOW_FWD = "#fbbf24"; // grid -> house (normal supply)
const FLOW_REV = "#38bdf8"; // house -> grid (solar export)

/**
 * 3D grid twin — anchored on the APPLICATION's real coordinates.
 *
 * - Anchor = application lat/lon when valid, else synthetic bus position.
 *   The target house + PV array sit exactly on the anchor, so the twin is
 *   never "in a different place" from the application pin / rooftop twin.
 * - Real OSM context buildings (via /api/site-context) are extruded around
 *   the site; the site building is highlighted in the verdict colour. This
 *   restores the 3D blocks (previous revision drew only the schematic row).
 * - The electrical row (GRID substation -> buses -> TRANSFORMER -> PV bus)
 *   runs ~150 m west of the house as a grounded schematic, clearly labelled
 *   illustrative; the service wire joins the PV bus to the real house.
 * - Flow pulses + all numbers come from TwinResponse. No mocks.
 */
export function GridTwin3D({
  twin,
  houses,
  busPosition,
  siteLatitude,
  siteLongitude,
  siteLabel,
}: {
  twin: TwinResponse;
  houses: GridHouse[];
  busPosition: { latitude: number; longitude: number } | null;
  siteLatitude?: number | null;
  siteLongitude?: number | null;
  siteLabel?: string | null;
}) {
  const container = useRef<HTMLDivElement>(null);
  const viewer = useRef<any>(null);
  const cesiumRef = useRef<any>(null);
  const staticEntities = useRef<any[]>([]);
  const pulseEntities = useRef<any[]>([]);
  const ground = useRef<number>(0);
  const [ready, setReady] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [groundLabel, setGroundLabel] = useState<string>("ellipsoid");
  const [bldgNote, setBldgNote] = useState<string | null>(null);
  const [bldgCount, setBldgCount] = useState<number>(0);
  const [bldgSource, setBldgSource] = useState<string>("OSM footprints");
  const tilesOnRef = useRef<boolean>(false);
  const [selected, setSelected] = useState<{ title: string; rows: [string, string][]; hint?: string } | null>(null);
  const token = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN;

  const t = twin.assessment.engineering.thresholds_snapshot;
  const eng = twin.assessment.engineering;
  const risk = eng.engineering_risk as keyof typeof RISK_CSS;
  const m = twin.assessment.metrics;
  const pvBus = m.pv_bus;
  const elements = twin.elements as any;
  const path: string[] = twin.topology.path ?? [];
  const edges: any[] = (twin.topology.edges ?? []) as any[];
  const eb = elements.energy_balance;
  const exporting = (eb?.local_export_kw ?? 0) > 0.05;
  const solarKw = eb?.solar_generation_kw ?? m.new_pv_kw ?? 0;

  const siteValid =
    typeof siteLatitude === "number" &&
    typeof siteLongitude === "number" &&
    Number.isFinite(siteLatitude) &&
    Number.isFinite(siteLongitude);
  const anchor = siteValid
    ? { latitude: siteLatitude as number, longitude: siteLongitude as number }
    : busPosition;
  const anchorKind = siteValid ? "application site" : "synthetic bus position";

  // ---- viewer (once) ----
  useEffect(() => {
    let cancelled = false;
    if (!container.current || viewer.current) return;
    (async () => {
      try {
        (window as any).CESIUM_BASE_URL = CESIUM_BASE_URL;
        const Cesium = await import("cesium");
        if (cancelled) return;
        cesiumRef.current = Cesium;
        if (token) Cesium.Ion.defaultAccessToken = token;
        let terrain: any = null;
        let imagery: any = null;
        try {
          if (token) terrain = await Cesium.createWorldTerrainAsync({ requestVertexNormals: true });
        } catch { terrain = null; }
        try {
          if (token) imagery = await Cesium.createWorldImageryAsync();
        } catch { imagery = null; }
        if (!imagery) {
          try {
            imagery = await (Cesium.ArcGisMapServerImageryProvider as any).fromUrl(
              "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer"
            );
          } catch {
            try {
              imagery = await (Cesium.OpenStreetMapImageryProvider as any).fromUrl(
                "https://a.tile.openstreetmap.org/"
              );
            } catch { imagery = null; }
          }
        }
        const v = new Cesium.Viewer(container.current!, {
          baseLayer: imagery ? new Cesium.ImageryLayer(imagery) : undefined,
          terrainProvider: terrain ?? new Cesium.EllipsoidTerrainProvider(),
          animation: false, timeline: false, baseLayerPicker: false, geocoder: false,
          homeButton: false, sceneModePicker: false, navigationHelpButton: false,
          fullscreenButton: false, selectionIndicator: false, infoBox: false,
          shadows: true,
        });
        if (cancelled) { v.destroy(); return; }
        viewer.current = v;
        v.scene.globe.enableLighting = true;
        v.scene.globe.depthTestAgainstTerrain = true;
        v.scene.fog.enabled = true;
        v.clock.shouldAnimate = true;
        // Best-available 3D buildings first: real Ion OSM 3D Tiles where the
        // token allows; otherwise OSM footprint extrusion (below) carries the
        // scene. Terrain + satellite stay visible either way.
        try {
          if (token) {
            const tiles = await Cesium.createOsmBuildingsAsync();
            if (!cancelled) {
              v.scene.primitives.add(tiles);
              tilesOnRef.current = true;
              setBldgSource("Real 3D Tiles · Ion OSM Buildings");
            }
          }
        } catch { /* footprints remain the source */ }
        setReady((n) => n + 1);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Cesium failed to initialise.");
      }
    })();
    return () => {
      cancelled = true;
      try { viewer.current?.destroy(); } catch {}
      viewer.current = null;
      staticEntities.current = [];
      pulseEntities.current = [];
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // ---- build anchored scene ----
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesiumRef.current;
    if (!ready || !v || !Cesium || !anchor) return;
    let cancelled = false;

    for (const e of [...staticEntities.current, ...pulseEntities.current]) {
      try { v.entities.remove(e); } catch {}
    }
    staticEntities.current = [];
    pulseEntities.current = [];

    (async () => {
      // 1) ground at the anchor (real site) — everything relative to it
      let g = 0;
      try {
        const [s] = await Cesium.sampleTerrainMostDetailed(v.terrainProvider, [
          Cesium.Cartographic.fromDegrees(anchor.longitude, anchor.latitude),
        ]);
        if (s && Number.isFinite(s.height)) {
          g = s.height;
          if (!cancelled) setGroundLabel(`${g.toFixed(0)} m terrain`);
        }
      } catch { g = 0; }
      if (cancelled) return;
      ground.current = g;
      const add = (e: any) => { staticEntities.current.push(e); return e; };
      const tag = (ent: any, info: { title: string; rows: [string, string][]; hint?: string }) => {
        (ent as any).__twinInfo = info;
        return ent;
      };
      const siteCss = RISK_CSS[risk] ?? "#38bdf8";

      // 2) OSM footprint extrusion (fallback / overlay): real outline, real
      // height or building:levels where mapped, clearly-labelled estimate
      // otherwise. Never invented geometry. Skipped when real 3D Tiles cover
      // the scene, except the site building which stays highlighted.
      const tilesOn = tilesOnRef.current;
      try {
        const ctx = await api.siteBuildings(anchor.latitude, anchor.longitude);
        const list = (ctx.buildings ?? []).slice(0, 40);
        if (!cancelled) {
          setBldgCount(list.length);
          if (!ctx.available) {
            setBldgNote(ctx.note ?? "No mapped buildings here — terrain + satellite only.");
            setBldgSource("Terrain + satellite (no building data)");
          } else if (!tilesOn) {
            setBldgSource("OSM footprints · extruded (mapped heights)");
          } else {
            setBldgNote("Real 3D Tiles below; site building highlighted.");
          }
        }
        // wall tones so blocks read as buildings, not glass: solid concrete
        // palette varied per building + dark roof cap + parapet outline
        const WALLS = ["#8d8fa3", "#9aa0b4", "#7e8496", "#a8adbf", "#8b93a7"];
        const wallFor = (id: string) => {
          let h = 0;
          for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
          return WALLS[h % WALLS.length];
        };
        let estLabels = 0;
        for (const b of list as BuildingFootprint[]) {
          const ring = b.footprint;
          if (!ring || ring.length < 4) continue;
          if (tilesOn && !b.is_site) continue; // real tiles carry the context
          const flat = ring.flatMap(([lo, la]: [number, number]) => [lo, la]);
          const isSite = !!b.is_site;
          const hgt = Math.max(3, b.height_m || 9);
          const wall = isSite ? siteCss : wallFor(b.osm_id);
          const walls = add(v.entities.add({
            name: isSite ? `TARGET ${b.osm_id}` : b.osm_id,
            polygon: {
              hierarchy: Cesium.Cartesian3.fromDegreesArray(flat),
              height: g, extrudedHeight: g + hgt,
              material: Cesium.Color.fromCssColorString(wall).withAlpha(isSite ? 0.95 : 0.92),
              outline: true,
              outlineColor: isSite ? Cesium.Color.WHITE : Cesium.Color.fromCssColorString("#2b3446"),
            },
          }));
          tag(walls, {
            title: isSite ? `TARGET BUILDING · ${b.osm_id}` : `BUILDING · ${b.osm_id}`,
            rows: [
              ["Height", `${hgt.toFixed(1)} m${b.height_source === "assumed" ? " (assumed)" : ""}`],
              ["Footprint", `${(b.area_sqm ?? 0).toFixed(0)} m²`],
              ...(isSite ? [["Verdict", String(risk)], ["Solar on roof", `${solarKw.toFixed(1)} kW`]] as [string, string][] : []),
            ],
            hint: isSite ? "This is the mapped building under the application pin." : undefined,
          });
          // roof cap: thin dark slab + parapet outline = reads as a roof, not glass
          const cap = add(v.entities.add({
            name: `Roof ${b.osm_id}`,
            polygon: {
              hierarchy: Cesium.Cartesian3.fromDegreesArray(flat),
              height: g + hgt, extrudedHeight: g + hgt + 0.5,
              material: Cesium.Color.fromCssColorString(isSite ? siteCss : "#4a5265").withAlpha(0.98),
              outline: true, outlineColor: Cesium.Color.WHITE.withAlpha(0.85),
            },
          }));
          tag(cap, {
            title: `ROOF · ${b.osm_id}`,
            rows: [["Height", `${hgt.toFixed(1)} m${b.height_source === "assumed" ? " (estimated)" : ""}`], ["Surface", isSite ? "PV array mounted here" : "No array"]],
          });
          // Clearly-labelled estimate where OSM maps no height/levels.
          if (b.height_source === "assumed" && estLabels < 8) {
            estLabels++;
            const c = ring.reduce(([sx, sy], [lo, la]: [number, number]) => [sx + lo / ring.length, sy + la / ring.length], [0, 0]);
            add(v.entities.add({
              name: `Estimated height ${b.osm_id}`,
              position: Cesium.Cartesian3.fromDegrees(c[0], c[1], g + hgt + 2),
              label: {
                text: `est. ${hgt.toFixed(0)} m`,
                font: "10px sans-serif", pixelOffset: new Cesium.Cartesian2(0, -8),
                fillColor: Cesium.Color.fromCssColorString("#fcd34d"), outlineColor: Cesium.Color.fromCssColorString("#0f172a"),
                outlineWidth: 2, style: Cesium.LabelStyle.FILL_AND_OUTLINE, disableDepthTestDistance: Number.POSITIVE_INFINITY,
              },
            }));
          }
        }
      } catch {
        if (!cancelled) { setBldgCount(0); setBldgNote("Building outlines unavailable — schematic only."); }
      }
      if (cancelled) return;

      // 3) target house marker + PV array exactly on the anchor (always drawn)
      // Solid walls + dark roof slab so it reads as a house, not glass.
      const HOUSE_H = 8;
      const hw = 0.00011, hd = 0.000085;
      tag(add(v.entities.add({
        name: siteLabel ?? houses[0]?.house_id ?? `house:${pvBus}`,
        polygon: {
          hierarchy: Cesium.Cartesian3.fromDegreesArray([
            anchor.longitude - hw, anchor.latitude - hd, anchor.longitude + hw, anchor.latitude - hd,
            anchor.longitude + hw, anchor.latitude + hd, anchor.longitude - hw, anchor.latitude + hd,
          ]),
          height: g + 0.2, extrudedHeight: g + HOUSE_H,
          material: Cesium.Color.fromCssColorString("#9aa0b4").withAlpha(0.95),
          outline: true, outlineColor: Cesium.Color.WHITE,
        },
      })), {
        title: `TARGET HOUSE · ${siteLabel ?? houses[0]?.house_id ?? pvBus}`,
        rows: [
          ["Solar generation", `${solarKw.toFixed(1)} kW`],
          ["House consumption", `${eb.local_consumption_kw.toFixed(1)} kW`],
          exporting ? ["Energy OUT (reverse)", `${eb.local_export_kw.toFixed(1)} kW → grid`] : ["Energy OUT (reverse)", "0 kW — no reverse flow"],
          ["Energy IN (grid)", `${eb.grid_supply_after_kw.toFixed(1)} kW`],
          ["Verdict", String(risk)],
        ],
        hint: eb.local_consumption_kw === 0
          ? `Zero modelled load at this bus — the full ${solarKw.toFixed(1)} kW exports. Risk is judged on voltage rise + transformer/line loading, not on consumption (there is none to absorb it).`
          : exporting
            ? "Solar exceeds what the house uses — the surplus flows out to the grid."
            : `No energy flows out of the house — all ${solarKw.toFixed(1)} kW solar is consumed locally; the grid supplies ${eb.grid_supply_after_kw.toFixed(1)} kW.`,
      });
      tag(add(v.entities.add({
        name: "House roof",
        polygon: {
          hierarchy: Cesium.Cartesian3.fromDegreesArray([
            anchor.longitude - hw, anchor.latitude - hd, anchor.longitude + hw, anchor.latitude - hd,
            anchor.longitude + hw, anchor.latitude + hd, anchor.longitude - hw, anchor.latitude + hd,
          ]),
          height: g + HOUSE_H, extrudedHeight: g + HOUSE_H + 0.5,
          material: Cesium.Color.fromCssColorString("#4a5265").withAlpha(0.98),
          outline: true, outlineColor: Cesium.Color.WHITE.withAlpha(0.85),
        },
      })), { title: "HOUSE ROOF", rows: [["PV array", "mounted here"]] });
      const panelCount = Math.max(2, Math.min(12, Math.round((m.new_pv_kw ?? 5) / 5)));
      for (let k = 0; k < panelCount; k++) {
        const cx = anchor.longitude - hw / 2 + (k % 4) * (hw / 3.4);
        const cy = anchor.latitude - hd / 3 + Math.floor(k / 4) * (hd / 2.2);
        tag(add(v.entities.add({
          name: `SOLAR module ${k + 1}`,
          position: Cesium.Cartesian3.fromDegrees(cx, cy, g + HOUSE_H + 1.1),
          box: { dimensions: new Cesium.Cartesian3(2.4, 1.5, 0.15), material: Cesium.Color.fromCssColorString("#14315c").withAlpha(1), outline: true, outlineColor: Cesium.Color.fromCssColorString("#7dd3fc") },
        })), {
          title: `SOLAR ENERGY · module ${k + 1}/${panelCount}`,
          rows: [["Array total", `${solarKw.toFixed(1)} kW`], ["Requested", `${(m.new_pv_kw ?? 0).toFixed(1)} kW`], ["Verdict", String(risk)]],
        });
      }
      add(v.entities.add({
        name: "Target house",
        position: Cesium.Cartesian3.fromDegrees(anchor.longitude, anchor.latitude, g + HOUSE_H + 4),
        label: {
          text: `TARGET HOUSE · ${siteLabel ?? houses[0]?.house_id ?? pvBus}\nSOLAR ENERGY ${solarKw.toFixed(1)} kW · use ${eb.local_consumption_kw.toFixed(1)} kW`,
          font: "bold 13px sans-serif", pixelOffset: new Cesium.Cartesian2(0, -22),
          fillColor: Cesium.Color.fromCssColorString("#7dd3fc"), outlineColor: Cesium.Color.fromCssColorString("#0f172a"),
          outlineWidth: 3, style: Cesium.LabelStyle.FILL_AND_OUTLINE, disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
      }));

      // 4) schematic grid row ~180 m west of the house (grounded, labelled)
      const POLE_H = 13, WIRE_H = POLE_H - 1;
      const nPath = Math.max(path.length, 1);
      const stepLon = 0.00085;
      const rowLon0 = anchor.longitude - 0.0021 - (nPath - 1) * stepLon;
      const rowLat = anchor.latitude - 0.0004;
      const P = (i: number) => ({ lat: rowLat + (i % 2 === 0 ? 0.0001 : -0.0001), lon: rowLon0 + i * stepLon });
      const edgeFor = (a: string, b: string) =>
        edges.find((e: any) => (e.source === a && e.target === b) || (e.source === b && e.target === a));
      type Seg = { a: { lat: number; lon: number }; b: { lat: number; lon: number }; dir: "FORWARD" | "REVERSE"; label: string; colorCss: string; width: number };
      const segs: Seg[] = [];

      path.forEach((busId, i) => {
        const b = elements.buses?.[busId];
        const pu = b?.after_pu;
        const r = (worstRisk(voltageRisk(pu, t), busId === pvBus && b ? voltageRiseRisk(b.delta_pu, t) : null) ?? "SAFE") as string;
        const css = RISK_CSS[r] ?? "#94a3b8";
        const p = P(i);
        const isPv = busId === pvBus;
        const role = i === 0 ? "GRID · Substation" : isPv ? "TARGET BUS · PV connection" : "BUS";
        add(v.entities.add({
          name: `${role} ${busId}`,
          polyline: { positions: [Cesium.Cartesian3.fromDegrees(p.lon, p.lat, g), Cesium.Cartesian3.fromDegrees(p.lon, p.lat, g + POLE_H)], width: isPv ? 4 : 3, material: Cesium.Color.fromCssColorString(css).withAlpha(0.95) },
        }));
        tag(add(v.entities.add({
          name: `Bus ${busId}`,
          position: Cesium.Cartesian3.fromDegrees(p.lon, p.lat, g + POLE_H + 1),
          point: { pixelSize: isPv ? 15 : 10, color: Cesium.Color.fromCssColorString(css), outlineColor: Cesium.Color.WHITE, outlineWidth: 2, disableDepthTestDistance: Number.POSITIVE_INFINITY },
          label: {
            text: `${role}\n${busId}${isPv ? " (PV)" : ""}\n${pu != null ? pu.toFixed(4) + " pu" : ""}${isPv && b ? `\n${b.delta_pu >= 0 ? "+" : ""}${b.delta_pu.toFixed(4)}` : ""}`,
            font: "12px sans-serif", pixelOffset: new Cesium.Cartesian2(0, -34),
            fillColor: Cesium.Color.WHITE, outlineColor: Cesium.Color.fromCssColorString("#0f172a"),
            outlineWidth: 3, style: Cesium.LabelStyle.FILL_AND_OUTLINE, disableDepthTestDistance: Number.POSITIVE_INFINITY,
          },
        })), {
          title: i === 0 ? `GRID · Substation 700` : `${isPv ? "TARGET " : ""}BUS ${busId}`,
          rows: [
            ["Voltage after", pu != null ? `${pu.toFixed(4)} pu` : "—"],
            ...(b ? [["Voltage before", `${b.before_pu.toFixed(4)} pu`], ["Rise", `${b.delta_pu >= 0 ? "+" : ""}${b.delta_pu.toFixed(4)} pu`]] as [string, string][] : []),
            ["Risk", String(r)],
            ...(isPv ? [["Energy through", exporting ? `${eb.local_export_kw.toFixed(1)} kW OUT → grid` : `${eb.grid_supply_after_kw.toFixed(1)} kW IN from grid`]] as [string, string][] : []),
          ],
          hint: isPv ? "Click the house to see the full energy balance." : undefined,
        });
        if (i < path.length - 1) {
          const q = P(i + 1);
          const edge = edgeFor(busId, path[i + 1]);
          const isTrafo = edge?.type === "TRANSFORMER";
          let dir: "FORWARD" | "REVERSE" = "FORWARD";
          let css2 = "#64748b", w = 3;
          let lab = edge?.label ?? "line";
          if (isTrafo) {
            const tr = edge ? (elements.transformers as any)?.[edge.id] : Object.values((elements.transformers as any) ?? {})[0] as any;
            if (tr) { dir = tr.direction_after ?? "FORWARD"; css2 = strokeFor(transformerRisk(tr.after_pct, t)); lab = `${tr.name ?? edge?.label} ${tr.after_pct.toFixed(1)}%`; }
            w = 5;
            const mid = { lat: (p.lat + q.lat) / 2, lon: (p.lon + q.lon) / 2 };
            const trInfo = (() => {
              const tr = edge ? (elements.transformers as any)?.[edge.id] : Object.values((elements.transformers as any) ?? {})[0] as any;
              return tr;
            })();
            tag(add(v.entities.add({
              name: `Transformer ${lab}`,
              position: Cesium.Cartesian3.fromDegrees(mid.lon, mid.lat, g + 3),
              box: { dimensions: new Cesium.Cartesian3(7, 7, 6), material: Cesium.Color.fromCssColorString(css2).withAlpha(0.95), outline: true, outlineColor: Cesium.Color.WHITE },
              label: { text: `TRANSFORMER\n${lab}`, font: "11px sans-serif", pixelOffset: new Cesium.Cartesian2(0, -26), fillColor: Cesium.Color.WHITE, outlineColor: Cesium.Color.fromCssColorString("#0f172a"), outlineWidth: 3, style: Cesium.LabelStyle.FILL_AND_OUTLINE, disableDepthTestDistance: Number.POSITIVE_INFINITY },
            })), {
              title: `TRANSFORMER · ${lab}`,
              rows: [
                ["Loading after", trInfo ? `${trInfo.after_pct.toFixed(1)}%` : "—"],
                ...(trInfo ? [["Loading before", `${trInfo.before_pct.toFixed(1)}%`], ["Flow", trInfo.direction_after === "REVERSE" ? "REVERSE — solar pushing back to grid" : "FORWARD — grid feeding houses"]] as [string, string][] : []),
                ["Risk", String(transformerRisk(trInfo?.after_pct, t) ?? "—")],
              ],
            });
          } else if (edge) {
            const ln = (elements.lines as any)?.[edge.id];
            if (ln) { dir = ln.direction_after ?? "FORWARD"; css2 = strokeFor(lineRisk(ln.after_pct, t)); lab = `${ln.name ?? edge.label} ${ln.after_pct.toFixed(1)}%`; }
          }
          segs.push({ a: p, b: q, dir, label: lab, colorCss: css2, width: w });
          tag(add(v.entities.add({
            name: lab,
            polyline: { positions: [Cesium.Cartesian3.fromDegrees(p.lon, p.lat, g + WIRE_H), Cesium.Cartesian3.fromDegrees(q.lon, q.lat, g + WIRE_H)], width: w, material: Cesium.Color.fromCssColorString(css2).withAlpha(0.95) },
          })), {
            title: `${isTrafo ? "TRANSFORMER LINK" : "LINE"} · ${lab}`,
            rows: [
              ["Direction", dir === "REVERSE" ? "REVERSE — energy flowing back to grid" : "FORWARD — grid feeding toward house"],
              ["Energy", dir === "REVERSE" ? `${eb.local_export_kw.toFixed(1)} kW export` : `${eb.grid_supply_after_kw.toFixed(1)} kW supply`],
            ],
          });
        }
      });

      // 5) service wire: PV bus node -> real house
      const pvIdx = Math.max(path.indexOf(pvBus), path.length - 1);
      const pvP = P(pvIdx < 0 ? path.length - 1 : pvIdx);
      const svcDir: "FORWARD" | "REVERSE" = exporting ? "REVERSE" : "FORWARD";
      segs.push({ a: pvP, b: { lat: anchor.latitude, lon: anchor.longitude }, dir: svcDir, label: "service", colorCss: exporting ? FLOW_REV : "#94a3b8", width: 2 });
      tag(add(v.entities.add({
        name: "Service connection",
        polyline: {
          positions: [Cesium.Cartesian3.fromDegrees(pvP.lon, pvP.lat, g + WIRE_H), Cesium.Cartesian3.fromDegrees(anchor.longitude, anchor.latitude, g + 4)],
          width: 2, material: new Cesium.PolylineDashMaterialProperty({ color: Cesium.Color.fromCssColorString(exporting ? FLOW_REV : "#94a3b8"), dashLength: 8 }),
        },
      })), {
        title: exporting ? "SERVICE · REVERSE ENERGY → GRID" : "SERVICE · SUPPLY → HOUSE",
        rows: exporting
          ? [["Export", `${eb.local_export_kw.toFixed(1)} kW out of the house`], ["Solar", `${solarKw.toFixed(1)} kW`], ["House use", `${eb.local_consumption_kw.toFixed(1)} kW`]]
          : [["Export", "0 kW — no reverse flow"], ["Solar (all consumed)", `${solarKw.toFixed(1)} kW`], ["Grid supply in", `${eb.grid_supply_after_kw.toFixed(1)} kW`]],
        hint: exporting ? undefined : "No energy leaves the house — panels cover part of the load, the grid covers the rest.",
      });
      const svcMid = { lat: (pvP.lat + anchor.latitude) / 2, lon: (pvP.lon + anchor.longitude) / 2 };
      add(v.entities.add({
        name: "Service direction",
        position: Cesium.Cartesian3.fromDegrees(svcMid.lon, svcMid.lat, g + 8),
        label: {
          text: exporting ? `REVERSE ENERGY → GRID\n${eb.local_export_kw.toFixed(1)} kW export` : "SUPPLY ENERGY → HOUSE",
          font: "bold 11px sans-serif", pixelOffset: new Cesium.Cartesian2(0, -12),
          fillColor: Cesium.Color.fromCssColorString(exporting ? "#7dd3fc" : "#e2e8f0"),
          outlineColor: Cesium.Color.fromCssColorString("#0f172a"),
          outlineWidth: 3, style: Cesium.LabelStyle.FILL_AND_OUTLINE, disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
      }));
      add(v.entities.add({
        name: "Grid risk",
        position: Cesium.Cartesian3.fromDegrees(pvP.lon, pvP.lat, g + 0.4),
        ellipse: { semiMajorAxis: 42, semiMinorAxis: 42, height: g + 0.4, material: Cesium.Color.fromCssColorString(siteCss).withAlpha(0.16), outline: true, outlineColor: Cesium.Color.fromCssColorString(siteCss).withAlpha(0.9) },
      }));

      // 6) flow pulses along each segment in its actual direction
      const pulses: any[] = [];
      segs.forEach((s, si) => {
        for (let k = 0; k < 2; k++) {
          const phase = (si * 0.37 + k / 2) % 1;
          const kw = s.dir === "REVERSE" ? eb.local_export_kw : eb.grid_supply_after_kw;
          pulses.push(tag(v.entities.add({
            name: `Flow ${s.label}`,
            position: new Cesium.CallbackProperty(() => {
              const now = Date.now() / 1000;
              let f = (now * 0.22 + phase) % 1;
              if (s.dir === "REVERSE") f = 1 - f;
              return Cesium.Cartesian3.fromDegrees(s.a.lon + (s.b.lon - s.a.lon) * f, s.a.lat + (s.b.lat - s.a.lat) * f, g + WIRE_H + 0.6);
            }, false),
            point: { pixelSize: 9, color: Cesium.Color.fromCssColorString(s.dir === "REVERSE" ? FLOW_REV : FLOW_FWD), outlineColor: Cesium.Color.WHITE, outlineWidth: 1.5, disableDepthTestDistance: Number.POSITIVE_INFINITY },
          }), {
            title: s.dir === "REVERSE" ? `FLOW · REVERSE → GRID (${s.label})` : `FLOW · SUPPLY → HOUSE (${s.label})`,
            rows: [["Energy on this wire", `${kw.toFixed(1)} kW ${s.dir === "REVERSE" ? "export" : "supply"}`]],
          }));
        }
      });
      pulseEntities.current = pulses;

      v.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(anchor.longitude - 0.0011, anchor.latitude - 0.0016, g + 300),
        orientation: { heading: Cesium.Math.toRadians(12), pitch: Cesium.Math.toRadians(-38), roll: 0 },
      });
      v.scene.requestRender?.();
    })();

    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, twin, houses, busPosition, siteLatitude, siteLongitude]);

  // ---- emit twin context for assistant ----
  useEffect(() => {
    if (!ready || !anchor) return;
    window.dispatchEvent(
      new CustomEvent("solargrid:twin-context", {
        detail: { pv_bus: pvBus, application_id: siteLabel || null, risk: String(risk), latitude: anchor.latitude, longitude: anchor.longitude },
      })
    );
  }, [ready, anchor, pvBus, siteLabel, risk]);

  // ---- assistant actions: focus/highlight ----
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesiumRef.current;
    if (!ready || !v || !Cesium) return;
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail as { type: string; payload: Record<string, unknown> };
      if (!detail) return;
      if (detail.type === "FOCUS_BUS" && detail.payload.busId) {
        const busId = String(detail.payload.busId);
        const g = ground.current || 0;
        const idx = path.indexOf(busId);
        if (idx >= 0) {
          const nPath = Math.max(path.length, 1);
          const stepLon = 0.00085;
          const rowLon0 = anchor!.longitude - 0.0021 - (nPath - 1) * stepLon;
          const rowLat = anchor!.latitude - 0.0004;
          const lon = rowLon0 + idx * stepLon;
          const lat = rowLat + (idx % 2 === 0 ? 0.0001 : -0.0001);
          v.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(lon, lat, g + 120), orientation: { heading: Cesium.Math.toRadians(12), pitch: Cesium.Math.toRadians(-45), roll: 0 }, duration: 1.2 });
          const b = (elements.buses as any)?.[busId];
          if (b) setSelected({ title: `BUS ${busId}`, rows: [["Voltage after", `${b.after_pu?.toFixed?.(4) ?? "—"} pu`], ["Rise", `${b.delta_pu >= 0 ? "+" : ""}${b.delta_pu?.toFixed?.(4) ?? "—"} pu`]] });
        } else {
          // Bus not in current path (e.g., viewing SG-F402 but focusing 734) — fly to its real asset coordinate
          api.busHouses(busId).then((h) => {
            const pos = h.bus_position;
            if (pos?.latitude && pos?.longitude) {
              v.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(pos.longitude, pos.latitude, g + 300), orientation: { heading: Cesium.Math.toRadians(12), pitch: Cesium.Math.toRadians(-38), roll: 0 }, duration: 1.5 });
              setSelected({ title: `BUS ${busId}`, rows: [["Location", `${pos.latitude.toFixed(5)}, ${pos.longitude.toFixed(5)}`], ["Distance from source", `${pos.distance_km?.toFixed(2) ?? "—"} km`]] });
            }
          }).catch(() => {
            // Fallback: stay on current anchor but highlight
            v.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(anchor!.longitude, anchor!.latitude, g + 200), duration: 1.0 });
          });
        }
      } else if (detail.type === "HIGHLIGHT_PATH" && Array.isArray(detail.payload.assetIds)) {
        v.scene.requestRender?.();
      } else if (detail.type === "FOCUS_TRANSFORMER") {
        const g2 = ground.current || 0;
        v.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(anchor!.longitude - 0.0015, anchor!.latitude - 0.0004, g2 + 150), duration: 1.2 });
      }
    };
    window.addEventListener("solargrid:assistant-action", handler as EventListener);
    return () => window.removeEventListener("solargrid:assistant-action", handler as EventListener);
  }, [ready, anchor, path, elements]);

  // ---- click any bubble/point/wire/block -> live energy readout ----
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesiumRef.current;
    if (!ready || !v || !Cesium) return;
    const handler = new Cesium.ScreenSpaceEventHandler(v.scene.canvas);
    handler.setInputAction((movement: any) => {
      const picked = v.scene.pick(movement.position);
      const info = picked?.id ? (picked.id as any).__twinInfo : null;
      setSelected(info ?? null);
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    return () => { try { handler.destroy(); } catch {} };
  }, [ready]);

  // clear selection when the assessment changes
  useEffect(() => { setSelected(null); }, [twin]);

  if (error) {
    return <div className="rounded-xl border border-red-900 bg-red-950/30 p-6 text-sm text-red-200">3D grid unavailable: {error}</div>;
  }
  if (!anchor) {
    return <div className="rounded-xl border border-amber-900 bg-amber-950/30 p-6 text-sm text-amber-200">3D needs a site or bus position.</div>;
  }
  return (
    <>
      {/* eslint-disable-next-line @next/next/no-css-tags */}
      <link rel="stylesheet" href={`${CESIUM_BASE_URL}/Widgets/widgets.css`} />
      <div className="relative overflow-hidden rounded-xl border border-slate-800">
        <div ref={container} className="h-[520px] w-full bg-slate-950" />
        <div className="pointer-events-none absolute left-3 top-3 rounded-md border border-slate-700 bg-slate-950/85 px-2.5 py-1 text-[11px] text-slate-200">
          3D grid twin · <span style={{ color: RISK_CSS[risk] ?? "#38bdf8" }}>● {risk}</span> · anchored on {anchorKind} · ground {groundLabel} · {bldgSource}{bldgCount > 0 ? ` · ${bldgCount} buildings` : ""}
        </div>
        <div className="pointer-events-none absolute right-3 top-3 rounded-md border border-slate-700 bg-slate-950/85 px-2.5 py-1 text-[11px] text-slate-300">
          <span style={{ color: FLOW_FWD }}>●▶ grid → house</span>{"  "}
          <span style={{ color: FLOW_REV }}>●▶ export → grid</span>
          {exporting && <span className="ml-1 text-sky-300">· exporting {eb.local_export_kw.toFixed(1)} kW</span>}
        </div>
        {bldgNote && (
          <div className="pointer-events-none absolute left-3 top-12 max-w-xs rounded-md border border-amber-900/70 bg-slate-950/85 px-2.5 py-1 text-[10px] text-amber-200">{bldgNote}</div>
        )}
        {!selected && (
          <div className="pointer-events-none absolute left-1/2 top-3 -translate-x-1/2 rounded-md border border-slate-700 bg-slate-950/70 px-2.5 py-1 text-[10px] text-slate-400">
            Click any pole, wire, transformer, house or flow dot for live kW / pu / % values
          </div>
        )}
        {selected && (
          <div className="absolute right-3 top-12 z-10 w-64 rounded-lg border border-sky-700 bg-slate-950/95 p-3 shadow-xl">
            <div className="mb-1 flex items-center justify-between gap-2">
              <div className="text-[11px] font-bold uppercase tracking-wide text-sky-300">{selected.title}</div>
              <button onClick={() => setSelected(null)} aria-label="Close readout" className="text-xs text-slate-500 hover:text-slate-200">✕</button>
            </div>
            {selected.rows.map(([k, val]) => (
              <div key={k} className="flex items-baseline justify-between gap-2 border-b border-slate-800/70 py-1 text-xs last:border-0">
                <span className="text-slate-500">{k}</span>
                <span className="font-mono text-slate-100">{val}</span>
              </div>
            ))}
            {selected.hint && <p className="mt-1.5 text-[10px] leading-relaxed text-slate-400">{selected.hint}</p>}
          </div>
        )}
        <div className="pointer-events-none absolute bottom-3 left-3 right-3 flex flex-wrap gap-x-4 gap-y-1 rounded-lg border border-slate-800 bg-slate-950/90 px-3 py-1.5 font-mono text-[11px] text-slate-300">
          <span>PV <b className="text-slate-100">{m.pv_bus}</b> {m.pv_voltage_pu.toFixed(4)} pu ({m.voltage_rise_pu >= 0 ? "+" : ""}{m.voltage_rise_pu.toFixed(4)})</span>
          <span>trafo {m.worst_transformer} <b className="text-slate-100">{m.max_transformer_loading_pct.toFixed(1)}%</b></span>
          <span>line {m.worst_line} <b className="text-slate-100">{m.max_line_loading_pct.toFixed(1)}%</b></span>
          <span>solar {solarKw.toFixed(1)} kW · use {eb.local_consumption_kw.toFixed(1)} kW · grid {eb.grid_supply_after_kw.toFixed(0)} kW</span>
          <span className="text-slate-500">{eng.constraint_reason}</span>
        </div>
      </div>
    </>
  );
}
