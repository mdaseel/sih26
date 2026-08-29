"use client";

import type { PublicVendor, VendorDiscovery } from "@/lib/types";

/**
 * Customer-facing vendor list.
 *
 * Two things this component is careful about:
 *
 *  1. Distance is only ever labelled for what it is. When no routing provider
 *     is configured the figure is straight-line, and it says so on every row —
 *     it is never called a drive, a route, or a travel time.
 *  2. A vendor with no measurable distance shows "—", not a guess, and sorts
 *     after the ones that could be measured.
 */
export function VendorList({ data }: { data: VendorDiscovery }) {
  const routed = data.routing.returns_real_routes;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-slate-400">
          <b className="text-slate-200">{data.total}</b> verified installer
          {data.total === 1 ? "" : "s"} available
          {data.with_distance > 0 && (
            <>
              {" · "}
              {data.with_distance} with a measured distance
            </>
          )}
        </p>
        <span
          className={`rounded-md border px-2.5 py-1 text-[11px] ${
            routed
              ? "border-green-900 bg-green-950/40 text-green-300"
              : "border-amber-900 bg-amber-950/30 text-amber-200"
          }`}
        >
          {routed ? "Road distances" : "Straight-line distances — not travel distance"}
        </span>
      </div>

      {data.vendors.length === 0 && (
        <div className="card text-sm text-slate-400">
          No verified installers are listed yet. Vendors appear here once a DISCOM
          reviewer has approved them.
        </div>
      )}

      {/* Capped: the list grows with every approved installer, and an
          unbounded one would push the notes below it off the page entirely. */}
      <div className="scroll-pane grid max-h-[42rem] gap-3 lg:grid-cols-2">
        {data.vendors.map((v) => (
          <VendorCard key={v.id} vendor={v} routed={routed} />
        ))}
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
        <p>{data.distance_note}</p>
        <p className="mt-2">{data.location_note}</p>
        <p className="mt-2 text-slate-600">
          Only vendors verified by the DISCOM are shown. Listing is not an
          endorsement of price or workmanship.
        </p>
      </div>
    </div>
  );
}

function VendorCard({ vendor: v, routed }: { vendor: PublicVendor; routed: boolean }) {
  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-slate-100">{v.business_name}</h3>
            {v.verified && (
              <span className="rounded-full border border-green-800 bg-green-950/60 px-2 py-0.5 text-[10px] font-medium text-green-300">
                DISCOM verified
              </span>
            )}
          </div>
          {v.representative_name && (
            <p className="mt-0.5 text-xs text-slate-500">{v.representative_name}</p>
          )}
        </div>

        <div className="text-right">
          {v.distance ? (
            <>
              <div className="font-mono text-lg tabular-nums text-slate-100">
                {v.distance.distance_km.toFixed(1)}
                <span className="ml-1 text-xs text-slate-500">km</span>
              </div>
              <div className="text-[10px] text-slate-500">
                {routed && v.distance.duration_minutes != null
                  ? `${v.distance.duration_minutes.toFixed(0)} min drive`
                  : "straight line"}
              </div>
            </>
          ) : (
            <div className="text-xs text-slate-600">distance —</div>
          )}
        </div>
      </div>

      <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
        <Row label="Rating" value={v.rating != null ? `${v.rating.toFixed(1)} / 5` : null} />
        <Row
          label="Completed installations"
          value={v.completed_installations != null ? String(v.completed_installations) : null}
        />
        <Row
          label="Experience"
          value={v.years_experience != null ? `${v.years_experience} years` : null}
        />
        <Row
          label="Capacity"
          value={
            v.installation_capacity_kw != null ? `${v.installation_capacity_kw} kW` : null
          }
        />
        <Row label="Service areas" value={v.service_areas.join(", ") || null} />
        <Row label="Location" value={[v.district, v.state].filter(Boolean).join(", ") || null} />
      </div>

      <div className="mt-3 flex flex-wrap gap-3 border-t border-slate-800 pt-3 text-xs">
        {v.phone && (
          <a href={`tel:${v.phone}`} className="text-sky-400 hover:underline">
            {v.phone}
          </a>
        )}
        {v.email && (
          <a href={`mailto:${v.email}`} className="text-sky-400 hover:underline">
            {v.email}
          </a>
        )}
        {!v.serves_this_district && (
          <span className="text-amber-400">may not serve your district</span>
        )}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="flex justify-between gap-2">
      <span className="text-slate-500">{label}</span>
      <span className="text-slate-300">{value ?? "—"}</span>
    </div>
  );
}
