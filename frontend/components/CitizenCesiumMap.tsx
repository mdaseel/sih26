"use client";

import { useEffect, useRef, useState } from "react";
import type { CitizenMapData } from "@/lib/types";

const CESIUM_BASE_URL = "/cesium";
const HOME = "#38bdf8";
const ENGAGED = "#4ade80";
const REQUESTED = "#facc15";
const VERIFIED = "#94a3b8";

/**
 * Citizen map on Cesium — real satellite (Ion World Imagery when tokened,
 * else ArcGIS World Imagery), pin billboards for sites/vendors, and
 * road-following routes (Google-like shortest path via OSRM, dashed only
 * when routing falls back).
 */
export function CitizenCesiumMap({ data }: { data: CitizenMapData }) {
  const container = useRef<HTMLDivElement>(null);
  const viewer = useRef<any>(null);
  const cesiumRef = useRef<any>(null);
  const [ready, setReady] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<{ title: string; html: string } | null>(null);
  const token = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN;

  const sites = data.applications.filter((a) => a.latitude != null && a.longitude != null);
  const vendors = data.vendors.filter((v) => v.latitude != null && v.longitude != null);
  const hasGeo = sites.length > 0 || vendors.length > 0;
  const isRoute = data.routing.returns_real_routes;

  // create viewer
  useEffect(() => {
    let cancelled = false;
    if (!container.current || viewer.current || !hasGeo) return;
    (async () => {
      try {
        (window as any).CESIUM_BASE_URL = CESIUM_BASE_URL;
        const Cesium = await import("cesium");
        if (cancelled) return;
        cesiumRef.current = Cesium;
        if (token) Cesium.Ion.defaultAccessToken = token;
        let imagery: any = null;
        let terrain: any = null;
        try {
          if (token) terrain = await Cesium.createWorldTerrainAsync({ requestVertexNormals: true });
        } catch {}
        try {
          if (token) imagery = await Cesium.createWorldImageryAsync();
        } catch {}
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
        });
        if (cancelled) { v.destroy(); return; }
        viewer.current = v;
        v.scene.globe.enableLighting = false;
        v.clock.shouldAnimate = false;
        setReady((n) => n + 1);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Cesium failed.");
      }
    })();
    return () => {
      cancelled = true;
      try { viewer.current?.destroy(); } catch {}
      viewer.current = null;
    };
  }, [hasGeo, token]);

  // draw pins + routes
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesiumRef.current;
    if (!ready || !v || !Cesium) return;

    // clear
    v.entities.removeAll();

    // pin helper — colored dot with white outline + label
    const pin = (lon: number, lat: number, color: string, label: string, size: number, props: any) => {
      const ent: any = v.entities.add({
        position: Cesium.Cartesian3.fromDegrees(lon, lat),
        point: { pixelSize: size, color: Cesium.Color.fromCssColorString(color), outlineColor: Cesium.Color.WHITE, outlineWidth: 2, heightReference: Cesium.HeightReference.CLAMP_TO_GROUND, disableDepthTestDistance: Number.POSITIVE_INFINITY },
        label: { text: label, font: "11px sans-serif", pixelOffset: new Cesium.Cartesian2(0, -18), fillColor: Cesium.Color.WHITE, outlineColor: Cesium.Color.fromCssColorString("#0f172a"), outlineWidth: 3, style: Cesium.LabelStyle.FILL_AND_OUTLINE, heightReference: Cesium.HeightReference.CLAMP_TO_GROUND, disableDepthTestDistance: Number.POSITIVE_INFINITY },
        properties: props,
      });
      return ent;
    };

    const allLons = [...sites.map((s) => s.longitude as number), ...vendors.map((vv) => vv.longitude as number)];
    const allLats = [...sites.map((s) => s.latitude as number), ...vendors.map((vv) => vv.latitude as number)];

    sites.forEach((s) => {
      pin(s.longitude as number, s.latitude as number, HOME, s.application_number, 12, { kind: "site", ...s });
    });
    vendors.forEach((vv) => {
      const col = vv.engaged ? ENGAGED : vv.requested ? REQUESTED : VERIFIED;
      const sz = vv.engaged ? 10 : vv.requested ? 8 : 6;
      pin(vv.longitude as number, vv.latitude as number, col, vv.business_name, sz, { kind: "vendor", ...vv });
    });

    // routes — Google-like polyline following road geometry
    data.routes.forEach((r) => {
      const geom = r.geometry as number[][] | null;
      if (!geom || geom.length < 2) return;
      const positions = geom.map(([lon, lat]) => Cesium.Cartesian3.fromDegrees(lon, lat));
      if (r.is_route) {
        v.entities.add({
          polyline: { positions, width: 4, material: Cesium.Color.fromCssColorString(ENGAGED).withAlpha(0.95), clampToGround: true, arcType: Cesium.ArcType.GEODESIC },
          properties: { kind: "route", ...r },
        });
        // glow under
        v.entities.add({
          polyline: { positions, width: 8, material: Cesium.Color.fromCssColorString(ENGAGED).withAlpha(0.18), clampToGround: true },
        });
      } else {
        v.entities.add({
          polyline: { positions, width: 2, material: new Cesium.PolylineDashMaterialProperty({ color: Cesium.Color.fromCssColorString(ENGAGED).withAlpha(0.6), dashLength: 12 }), clampToGround: true },
          properties: { kind: "route", ...r },
        });
      }
    });

    // fit
    if (allLons.length > 0) {
      const rect = Cesium.Rectangle.fromDegrees(Math.min(...allLons) - 0.02, Math.min(...allLats) - 0.02, Math.max(...allLons) + 0.02, Math.max(...allLats) + 0.02);
      v.camera.flyTo({ destination: rect, duration: 1.2 });
    }
    v.scene.requestRender?.();

    // click
    const handler = new Cesium.ScreenSpaceEventHandler(v.scene.canvas);
    handler.setInputAction((movement: any) => {
      const picked = v.scene.pick(movement.position);
      const ent = picked?.id;
      const p = ent?.properties?.getValue ? (() => {
        const vals: any = {};
        for (const k of ent.properties.propertyNames) vals[k] = ent.properties[k].getValue();
        return vals;
      })() : ent?.properties;
      if (!ent || !p) { setSelected(null); return; }
      if (p.kind === "site") {
        setSelected({ title: p.application_number, html: `<div style="line-height:1.6"><div style="color:#38bdf8;font-weight:700">${p.application_number}</div><div>Your site</div><div>${p.new_pv_kw?.toFixed?.(1) ?? p.new_pv_kw} kW · ${p.status}</div></div>` });
      } else if (p.kind === "vendor") {
        setSelected({ title: p.business_name, html: `<div style="line-height:1.6"><div style="font-weight:700">${p.business_name}</div><div>${p.engaged ? '<span style="color:#4ade80">Accepted your booking</span>' : p.requested ? '<span style="color:#facc15">Awaiting response</span>' : 'Verified'}</div><div>Rating: ${p.rating ?? '—'} ${p.completed_installations ?? ''}</div></div>` });
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    // Assistant → focus vendor/site/route
    const assistantHandler = (e: Event) => {
      const detail = (e as CustomEvent).detail as { type: string; payload: Record<string, unknown> };
      if (!detail) return;
      if (detail.type === "FOCUS_BUS" && detail.payload.busId) {
        const s = sites.find((x) => String(x.application_number).includes(String(detail.payload.busId)) || String((x as any).pv_bus) === String(detail.payload.busId));
        if (s?.longitude && s?.latitude) v.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(s.longitude as number, s.latitude as number, 800), duration: 1.2 });
      } else if (detail.type === "FOCUS_APPLICATION" && detail.payload.applicationId) {
        const s2 = sites.find((x) => x.id === detail.payload.applicationId);
        if (s2?.longitude && s2?.latitude) v.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(s2.longitude as number, s2.latitude as number, 600), duration: 1.2 });
      }
    };
    window.addEventListener("solargrid:assistant-action", assistantHandler as EventListener);
    return () => { try { handler.destroy(); } catch {} window.removeEventListener("solargrid:assistant-action", assistantHandler as EventListener); };
  }, [ready, data, sites, vendors]);

  if (!hasGeo) {
    return (
      <div className="card text-center">
        <p className="text-sm text-slate-400">There is nothing to place on a map yet.</p>
        <p className="mx-auto mt-2 max-w-md text-xs text-slate-500">Add coordinates to an application to see it here.</p>
      </div>
    );
  }
  if (error) return <div className="rounded-xl border border-red-900 bg-red-950/30 p-4 text-sm text-red-200">{error}</div>;

  return (
    <>
      {/* eslint-disable-next-line @next/next/no-css-tags */}
      <link rel="stylesheet" href={`${CESIUM_BASE_URL}/Widgets/widgets.css`} />
      <div className="relative overflow-hidden rounded-xl border border-slate-800">
        <div ref={container} className="h-[560px] w-full bg-slate-950" />
        <div className="pointer-events-none absolute left-3 top-3 rounded-md border border-slate-700 bg-slate-950/85 px-2.5 py-1 text-[11px] text-slate-200">
          Cesium satellite · {vendors.length} installers · {sites.length} site(s) · {isRoute ? "road routes (OSRM)" : "straight-line (no routing)"}
        </div>
        <div className="pointer-events-none absolute bottom-3 right-3 rounded bg-slate-950/85 px-2 py-0.5 text-[10px] text-slate-400">Imagery © <a href="https://cesium.com/platform/cesium-ion/" className="underline" target="_blank" rel="noreferrer">Cesium ion</a> / Esri · OpenStreetMap</div>
        {selected && (
          <div className="absolute right-3 top-12 z-10 w-64 rounded-lg border border-slate-700 bg-slate-950/95 p-3 shadow-xl">
            <div className="mb-1 flex items-center justify-between"><div className="text-xs font-bold text-slate-100">{selected.title}</div><button onClick={() => setSelected(null)} className="text-xs text-slate-500 hover:text-slate-200">✕</button></div>
            <div className="text-xs text-slate-300" dangerouslySetInnerHTML={{ __html: selected.html }} />
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-3 text-xs text-slate-500 mt-2">
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full" style={{ background: HOME }} />Your site</span>
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full" style={{ background: ENGAGED }} />Accepted</span>
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full" style={{ background: REQUESTED }} />Awaiting</span>
        <span className="flex items-center gap-1.5"><span className="h-0.5 w-6" style={{ background: ENGAGED }} />Road route — click pin for details</span>
      </div>
    </>
  );
}
