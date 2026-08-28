"""Precompute the map layers and write them into public.grid_assets.

Two things are computed here because neither can be done per-request:

  1. Illustrative coordinates. The feeder has none; see TopologyService.
     geo_positions for exactly what is real (distance) and what is not
     (absolute location).

  2. Hosting capacity for all 71 eligible buses, by bisection on the real
     power flow — roughly 11 solves per bus.

Also captured, from a single BASE power flow: per-bus voltage, per-line
loading and per-transformer loading, which back the Voltage / Line loading /
Transformer loading map layers.

Usage:
    python backend/scripts/precompute_grid_map.py --dry-run
    python backend/scripts/precompute_grid_map.py
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import time
import warnings
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import pandapower as pp  # noqa: E402

from app.core import paths  # noqa: E402
from app.services.grid_assets import get_grid_asset_service  # noqa: E402
from app.services.hosting_capacity import get_hosting_capacity_service  # noqa: E402
from app.services.topology import get_topology_service  # noqa: E402

# Illustrative anchor. Distances along the feeder are real; this point is not.
DEFAULT_ANCHOR_LAT = 12.9716
DEFAULT_ANCHOR_LON = 77.5946
FEEDER_ID = "IEEE_CompTestFeeder"


def base_state() -> dict[str, Any]:
    """One BASE power flow, no PV — the 'today' layer values."""
    net = copy.deepcopy(pp.from_json(str(paths.FEEDER_NETWORK)))
    pp.runpp(net, algorithm="nr", max_iteration=500, numba=False, tolerance_mva=1e-3)
    return {
        "bus_voltage": {
            str(net.bus.name.iloc[i]): round(float(net.res_bus.vm_pu.iloc[i]), 5)
            for i in range(len(net.bus))
        },
        "line_loading": {
            str(net.line.name.iloc[i]): round(float(net.res_line.loading_percent.iloc[i]), 3)
            for i in range(len(net.line))
        },
        "trafo_loading": {
            str(net.trafo.name.iloc[i]): round(float(net.res_trafo.loading_percent.iloc[i]), 3)
            for i in range(len(net.trafo))
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--anchor-lat", type=float, default=DEFAULT_ANCHOR_LAT)
    ap.add_argument("--anchor-lon", type=float, default=DEFAULT_ANCHOR_LON)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    topo = get_topology_service()
    grid = get_grid_asset_service()
    hc = get_hosting_capacity_service()

    print("=== base power flow ===")
    base = base_state()
    print(f"  {len(base['bus_voltage'])} buses, {len(base['line_loading'])} lines, "
          f"{len(base['trafo_loading'])} transformers")

    print("\n=== coordinates ===")
    geo = topo.geo_positions(args.anchor_lat, args.anchor_lon)
    print(f"  {len(geo)} buses placed, anchor ({args.anchor_lat}, {args.anchor_lon})")
    print("  NOTE: distances along the feeder are real; absolute placement is illustrative")

    print("\n=== hosting capacity (bisection on the real power flow) ===")
    eligible = grid.eligible_bus_ids()
    started = time.perf_counter()
    capacities: dict[str, dict[str, Any]] = {}
    total_runs = 0
    for n, bus in enumerate(eligible, 1):
        cap = hc.capacity_for(bus, 0.0)
        capacities[bus] = cap.as_dict()
        total_runs += cap.power_flows_run
        if n % 10 == 0 or n == len(eligible):
            print(
                f"  {n:3}/{len(eligible)} buses · {total_runs} power flows · "
                f"{time.perf_counter() - started:.1f}s"
            )

    values = [c["hosting_capacity_kw"] for c in capacities.values()]
    saturated = [b for b, c in capacities.items() if c["saturated"]]
    binding: dict[str, int] = {}
    for c in capacities.values():
        binding[c["limiting_constraint"]] = binding.get(c["limiting_constraint"], 0) + 1

    print(f"\n  min {min(values):.0f} kW · median {sorted(values)[len(values) // 2]:.0f} kW · "
          f"max {max(values):.0f} kW")
    print(f"  limiting constraint: {binding}")
    print(f"  at/above search ceiling: {len(saturated)} buses {saturated[:5]}")

    payload = {
        "anchor": {"latitude": args.anchor_lat, "longitude": args.anchor_lon},
        "geo": geo,
        "base": base,
        "hosting_capacity": capacities,
    }

    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\n  payload written to {args.out}")

    if args.dry_run:
        print("\ndry run — nothing written to Supabase")
        return 0

    # ---- write into grid_assets ----
    from app.db.service import db

    print("\n=== writing to Supabase ===")
    client = db.as_service()
    updated = 0

    for bus, pos in geo.items():
        attrs: dict[str, Any] = {
            "base_voltage_pu_measured": base["bus_voltage"].get(bus),
            "distance_km": pos["distance_km"],
        }
        if bus in capacities:
            cap = capacities[bus]
            attrs["hosting_capacity_kw"] = cap["hosting_capacity_kw"]
            attrs["hosting_capacity_limiting_constraint"] = cap["limiting_constraint"]
            attrs["hosting_capacity_reason"] = cap["limiting_reason"]
            attrs["hosting_capacity_method"] = cap["method"]
            attrs["hosting_capacity_saturated"] = cap["saturated"]

        res = (
            client.table("grid_assets")
            .update(
                {
                    "latitude": pos["latitude"],
                    "longitude": pos["longitude"],
                    "geometry_source": "SYNTHETIC_LAYOUT",
                    "attributes": attrs,
                }
            )
            .eq("asset_type", "BUS")
            .eq("asset_code", bus)
            .execute()
        )
        updated += len(res.data or [])

    # Loading on the line and transformer assets.
    #
    # These MUST merge, not replace. attributes already holds the connectivity
    # the seed wrote (from_bus/to_bus on lines, hv_bus/lv_bus on transformers),
    # and the map draws its edges from exactly those fields. Overwriting the
    # object wipes them and the map degrades to unconnected dots.
    def merge_attributes(asset_type: str, loading_by_name: dict[str, float]) -> int:
        existing = (
            client.table("grid_assets")
            .select("asset_code,attributes")
            .eq("asset_type", asset_type)
            .execute()
        ).data or []
        by_code = {r["asset_code"]: (r.get("attributes") or {}) for r in existing}

        written = 0
        for name, loading in loading_by_name.items():
            merged = {**by_code.get(name, {}), "base_loading_pct": loading}
            res = (
                client.table("grid_assets")
                .update({"attributes": merged})
                .eq("asset_type", asset_type)
                .eq("asset_code", name)
                .execute()
            )
            written += len(res.data or [])
        return written

    n_trafo = merge_attributes("TRANSFORMER", base["trafo_loading"])
    n_line = merge_attributes("LINE", base["line_loading"])

    # ---- feeder-section hosting capacity ----
    # Stored as FEEDER rows, one per section, because this is far too slow to
    # compute per request (~10 s a section) and far too misleading to skip.
    print("\n=== feeder-section hosting capacity (simultaneous injection) ===")
    sections: dict[str, list[str]] = {}
    for bus_id in grid.eligible_bus_ids():
        sections.setdefault(grid.get(bus_id).feeder_section, []).append(bus_id)

    section_rows = []
    for name in sorted(sections):
        started_s = time.perf_counter()
        result = hc.feeder_capacity(name)
        naive = sum(capacities[b]["hosting_capacity_kw"] for b in sections[name])
        result["sum_of_per_bus_kw"] = round(naive, 1)
        result["overstatement_factor"] = (
            round(naive / result["hosting_capacity_kw"], 1)
            if result["hosting_capacity_kw"]
            else None
        )
        section_rows.append(result)
        print(
            f"  {name:26} {result['hosting_capacity_kw']:>7.0f} kW "
            f"(sum of per-bus would say {naive:>7.0f}) "
            f"· {result['limiting_constraint']} · {time.perf_counter() - started_s:.1f}s"
        )

        client.table("grid_assets").upsert(
            {
                "asset_type": "FEEDER",
                "asset_code": name,
                "name": f"Feeder section {name}",
                "feeder_id": FEEDER_ID,
                "parent_asset_code": FEEDER_ID,
                "pv_eligible": False,
                "attributes": result,
            },
            on_conflict="feeder_id,asset_type,asset_code",
        ).execute()

    print(f"  updated {updated} bus rows with coordinates and hosting capacity")
    print(f"  updated {n_trafo} transformers, {n_line} lines (attributes merged, connectivity preserved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
