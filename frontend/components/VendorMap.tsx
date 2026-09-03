"use client";

import maplibregl, { Map as MapLibreMap, Popup } from "maplibre-gl";
import { useEffect, useMemo, useRef, useState } from "react";

import type { CitizenMapData } from "@/lib/types";

/**
 * The citizen's map: their sites, verified installers, and the way between.
 *
 * Two things are deliberately absent. There are no buses, transformers or line
 * loadings — that is the DISCOM's instrument panel and it answers questions a
 * householder is not asking. And there is no caveat about illustrative
 * placement, because unlike the feeder layout these coordinates are real: the
 * applicant gave their own, the installer gave theirs. The street basemap here
 * is a statement about where things are, so it is on by default.
 *
 * A drawn path is only as real as the routing provider behind it. With one
 * configured it is the road; without one it is a straight connector, drawn
 * dashed and labelled as such, because a straight line presented as a drive is
 * a lie about how far away someone is.
 */

const HOME = "#38bdf8"; // sky-400 — your site
const ENGAGED = "#4ade80"; // green-400 — installer who accepted
const REQUESTED = "#facc15"; // yellow-400 — asked, no answer yet
const VERIFIED = "#94a3b8"; // slate-400 — verified, not engaged

export function VendorMap({ data }: { data: CitizenMapData }) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const popup = useRef<Popup | null>(null);
  const [ready, setReady] = useState(false);
  const [styleTick, setStyleTick] = useState(0);
  const [showAll, setShowAll] = useState(true);

  const sites = useMemo(
    () => data.applications.filter((a) => a.latitude != null && a.longitude != null),
    [data.applications]
  );

  const vendors = useMemo(
    () => data.vendors.filter((v) => v.latitude != null && v.longitude != null),
    [data.vendors]
  );

  const visibleVendors = useMemo(
    () => (showAll ? vendors : vendors.filter((v) => v.engaged || v.requested)),
    [vendors, showAll]
  );

  const points = useMemo(
    () => [
      ...sites.map((s) => [s.longitude as number, s.latitude as number] as [number, number]),
      ...vendors.map((v) => [v.longitude as number, v.latitude as number] as [number, number]),
    ],
    [sites, vendors]
  );

  const hasGeography = points.length > 0;

  // ---- create the map once there is something to show ----
  useEffect(() => {
    if (!container.current || map.current || !hasGeography) return;

    const bounds = new maplibregl.LngLatBounds(points[0], points[0]);
    for (const p of points) bounds.extend(p);

    map.current = new maplibregl.Map({
      container: container.current,
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
            paint: { "raster-opacity": 0.6, "raster-saturation": -0.35 },
          },
        ],
      },
      bounds,
      fitBoundsOptions: { padding: 80, maxZoom: 13 },
      attributionControl: false,
    });

    map.current.addControl(
      new maplibregl.NavigationControl({ showCompass: false }),
      "top-right"
    );
    map.current.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
    map.current.on("load", () => setReady(true));

    return () => {
      map.current?.remove();
      map.current = null;
      // Strict Mode tears this down and runs it again; a stale flag would let
      // the draw effect write to a map whose style has not loaded.
      setReady(false);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasGeography]);

  // ---- (re)draw ----
  useEffect(() => {
    const m = map.current;
    if (!m) return;

    if (!m.isStyleLoaded()) {
      const onLoad = () => setStyleTick((t) => t + 1);
      m.once("load", onLoad);
      return () => {
        m.off("load", onLoad);
      };
    }

    const visibleIds = new Set(visibleVendors.map((v) => v.id));

    const siteFeatures = sites.map((s) => ({
      type: "Feature" as const,
      properties: {
        kind: "site",
        application_number: s.application_number,
        status: s.status.replace(/_/g, " "),
        address: [s.address_line, s.district, s.state, s.pincode].filter(Boolean).join(", "),
        new_pv_kw: s.new_pv_kw,
      },
      geometry: {
        type: "Point" as const,
        coordinates: [s.longitude as number, s.latitude as number],
      },
    }));

    const vendorFeatures = visibleVendors.map((v) => ({
      type: "Feature" as const,
      properties: {
        kind: "vendor",
        business_name: v.business_name,
        representative_name: v.representative_name ?? "",
        phone: v.phone ?? "",
        address: [v.address_line, v.district, v.state].filter(Boolean).join(", "),
        rating: v.rating,
        completed_installations: v.completed_installations,
        years_experience: v.years_experience,
        engaged: v.engaged,
        requested: v.requested,
        colour: v.engaged ? ENGAGED : v.requested ? REQUESTED : VERIFIED,
        radius: v.engaged ? 10 : v.requested ? 8 : 6,
      },
      geometry: {
        type: "Point" as const,
        coordinates: [v.longitude as number, v.latitude as number],
      },
    }));

    const routeFeatures = data.routes
      .filter((r) => r.geometry && r.geometry.length > 1 && visibleIds.has(r.vendor_id))
      .map((r) => ({
        type: "Feature" as const,
        properties: {
          vendor_name: r.vendor_name,
          application_number: r.application_number,
          distance_km: r.distance_km,
          duration_minutes: r.duration_minutes,
          is_route: r.is_route,
          method: r.method,
          note: r.note,
        },
        geometry: { type: "LineString" as const, coordinates: r.geometry as number[][] },
      }));

    const set = (id: string, value: object) => {
      const src = m.getSource(id) as maplibregl.GeoJSONSource | undefined;
      if (src) src.setData(value as never);
      else m.addSource(id, { type: "geojson", data: value as never });
    };

    set("routes", { type: "FeatureCollection", features: routeFeatures });
    set("vendors", { type: "FeatureCollection", features: vendorFeatures });
    set("sites", { type: "FeatureCollection", features: siteFeatures });

    if (!m.getLayer("routes-solid")) {
      // Routes sit under everything: they are context for the pins, not the
      // subject. Two layers rather than one because line-dasharray takes no
      // data-driven expression — and the distinction has to survive that, so a
      // straight connector is dashed and never reads as a road.
      m.addLayer({
        id: "routes-solid",
        type: "line",
        source: "routes",
        filter: ["==", ["get", "is_route"], true],
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": ENGAGED, "line-width": 3, "line-opacity": 0.8 },
      });

      m.addLayer({
        id: "routes-dashed",
        type: "line",
        source: "routes",
        filter: ["==", ["get", "is_route"], false],
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-color": ENGAGED,
          "line-width": 2.5,
          "line-opacity": 0.65,
          "line-dasharray": [2, 1.6],
        },
      });

      m.addLayer({
        id: "vendors-layer",
        type: "circle",
        source: "vendors",
        paint: {
          "circle-radius": ["get", "radius"],
          "circle-color": ["get", "colour"],
          "circle-stroke-width": ["case", ["get", "engaged"], 3, 1.5],
          "circle-stroke-color": "#0f172a",
          "circle-opacity": 0.95,
        },
      });

      m.addLayer({
        id: "vendor-labels",
        type: "symbol",
        source: "vendors",
        minzoom: 10,
        layout: {
          "text-field": ["get", "business_name"],
          "text-size": 11,
          "text-offset": [0, 1.3],
          "text-anchor": "top",
          "text-allow-overlap": false,
        },
        paint: {
          "text-color": "#e2e8f0",
          "text-halo-color": "#0f172a",
          "text-halo-width": 1.5,
        },
      });

      m.addLayer({
        id: "sites-layer",
        type: "circle",
        source: "sites",
        paint: {
          "circle-radius": 9,
          "circle-color": HOME,
          "circle-stroke-width": 3,
          "circle-stroke-color": "#e2e8f0",
        },
      });

      const esc = (v: unknown) =>
        String(v ?? "").replace(
          /[&<>"]/g,
          (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!
        );

      const open = (e: maplibregl.MapLayerMouseEvent, kind: "site" | "vendor") => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as Record<string, unknown>;

        // Routes to this vendor, if any, so distance appears where it is asked for.
        const legs =
          kind === "vendor"
            ? data.routes.filter((r) => r.vendor_name === p.business_name)
            : [];

        const html =
          kind === "site"
            ? `<div style="font-family:ui-sans-serif,system-ui;font-size:12px;line-height:1.6">
                 <div style="font-weight:700;margin-bottom:2px">${esc(p.application_number)}</div>
                 <div style="color:#64748b">Your site</div>
                 <div>${esc(p.address) || "—"}</div>
                 <div>Requested: ${Number(p.new_pv_kw).toFixed(1)} kW</div>
                 <div>Status: ${esc(p.status)}</div>
               </div>`
            : `<div style="font-family:ui-sans-serif,system-ui;font-size:12px;line-height:1.6">
                 <div style="font-weight:700;margin-bottom:2px">${esc(p.business_name)}</div>
                 <div style="color:#4ade80">✓ Verified by the DISCOM</div>
                 ${p.engaged ? '<div style="color:#4ade80">Accepted your booking</div>' : ""}
                 ${p.requested ? '<div style="color:#facc15">Awaiting their response</div>' : ""}
                 <div>${esc(p.address) || "—"}</div>
                 ${p.representative_name ? `<div>Contact: ${esc(p.representative_name)}</div>` : ""}
                 ${p.phone ? `<div>Phone: ${esc(p.phone)}</div>` : ""}
                 ${p.rating != null ? `<div>Rating: ${Number(p.rating).toFixed(1)} / 5</div>` : ""}
                 ${
                   p.completed_installations != null
                     ? `<div>Completed installations: ${esc(p.completed_installations)}</div>`
                     : ""
                 }
                 ${legs
                   .map(
                     (r) =>
                       `<div style="margin-top:4px;color:#94a3b8">${
                         r.is_route ? "Road distance" : "Straight-line distance"
                       } to ${esc(r.application_number)}: <b>${r.distance_km.toFixed(1)} km</b>${
                         r.duration_minutes != null ? ` · ${Math.round(r.duration_minutes)} min` : ""
                       }</div>`
                   )
                   .join("")}
               </div>`;

        popup.current?.remove();
        popup.current = new maplibregl.Popup({ closeButton: true, maxWidth: "300px" })
          .setLngLat(e.lngLat)
          .setHTML(html)
          .addTo(m);
      };

      m.on("click", "sites-layer", (e) => open(e, "site"));
      m.on("click", "vendors-layer", (e) => open(e, "vendor"));
      for (const id of ["sites-layer", "vendors-layer"]) {
        m.on("mouseenter", id, () => (m.getCanvas().style.cursor = "pointer"));
        m.on("mouseleave", id, () => (m.getCanvas().style.cursor = ""));
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, styleTick, data, sites, visibleVendors]);

  if (!hasGeography) {
    return (
      <div className="card text-center">
        <p className="text-sm text-slate-400">There is nothing to place on a map yet.</p>
        <p className="mx-auto mt-2 max-w-md text-xs text-slate-500">
          {data.applications.length === 0
            ? "Once you submit an application with its location, your site will appear here alongside verified installers."
            : "None of your applications carry coordinates, and no verified installer has published a location. Add the site location to an application to see it here."}
        </p>
      </div>
    );
  }

  const engagedCount = vendors.filter((v) => v.engaged).length;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={() => setShowAll(true)}
          className={`rounded-md border px-3 py-1.5 text-xs transition ${
            showAll
              ? "border-sky-600 bg-sky-950/60 text-sky-300"
              : "border-slate-700 text-slate-400 hover:bg-slate-800"
          }`}
        >
          All verified installers ({vendors.length})
        </button>
        <button
          onClick={() => setShowAll(false)}
          className={`rounded-md border px-3 py-1.5 text-xs transition ${
            !showAll
              ? "border-sky-600 bg-sky-950/60 text-sky-300"
              : "border-slate-700 text-slate-400 hover:bg-slate-800"
          }`}
        >
          Only mine ({vendors.filter((v) => v.engaged || v.requested).length})
        </button>
      </div>

      <div className="relative rounded-xl border border-slate-800 bg-slate-950 p-1">
        <div ref={container} style={{ height: 520, borderRadius: 10, overflow: "hidden" }} />
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
      </div>

      <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
        {[
          [HOME, "Your site"],
          [ENGAGED, "Installer who accepted"],
          [REQUESTED, "Awaiting their response"],
          [VERIFIED, "Verified installer"],
        ].map(([colour, label]) => (
          <span key={label} className="flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ background: colour }}
            />
            {label}
          </span>
        ))}
        {engagedCount > 0 && (
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-0.5 w-6" style={{ background: ENGAGED }} />
            {data.routing.returns_real_routes ? "Road route" : "Direct connector (dashed)"}
          </span>
        )}
      </div>

      <p className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-[11px] leading-relaxed text-slate-500">
        {data.distance_note} {data.location_note} Only installers the DISCOM has approved
        appear here.
      </p>
    </div>
  );
}
