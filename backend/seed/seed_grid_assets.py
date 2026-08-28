"""Seed public.grid_assets from the EXISTING feeder model.

Sources (all read-only, none are modified):
    feeder_network.json     -- topology: buses, lines, transformers, ext_grid
    valid_pv_buses.csv      -- the 71 PV-eligible LV buses + static attributes
    excluded_buses.csv      -- the 43 ineligible buses + the reason why
    electrical_features.csv -- transformer kVA, base voltage, distance, R/X/Z

No electrical value is invented here. Every number is copied from a file the
research pipeline produced.

Geography: the IEEE feeder ships no coordinates (verified — feeder_network.json
has no bus_geodata). latitude/longitude are therefore left NULL and
geometry_source is 'SYNTHETIC_LAYOUT'. Phase 5 must assign illustrative
placements and label them as such.

Usage:
    python backend/seed/seed_grid_assets.py --dry-run    # build + validate only
    python backend/seed/seed_grid_assets.py              # upsert into Supabase
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app.core import paths  # noqa: E402

FEEDER_ID = "IEEE_CompTestFeeder"


def _clean(value: Any) -> Any:
    """JSON/Postgres-safe scalar. NaN becomes None."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if pd.api.types.is_scalar(value) and pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def build_rows() -> list[dict[str, Any]]:
    import pandapower as pp

    net = pp.from_json(str(paths.FEEDER_NETWORK))

    valid = pd.read_csv(paths.VALID_PV_BUSES, dtype={"bus_id": str})
    excluded = pd.read_csv(paths.EXCLUDED_BUSES, dtype={"bus_id": str})
    elec = pd.read_csv(paths.ELECTRICAL_FEATURES, dtype={"bus_id": str}).set_index("bus_id")

    rows: list[dict[str, Any]] = []

    # ---- substation + feeder ------------------------------------------
    slack_bus = str(net.bus.name.iloc[int(net.ext_grid.bus.iloc[0])])
    rows.append(
        {
            "asset_type": "SUBSTATION",
            "asset_code": "SUB-700",
            "name": "Source substation (115 kV)",
            "feeder_id": FEEDER_ID,
            "parent_asset_code": None,
            "vn_kv": float(net.bus.vn_kv.iloc[int(net.ext_grid.bus.iloc[0])]),
            "pv_eligible": False,
            "attributes": {"slack_bus": slack_bus, "source": "feeder_network.json:ext_grid"},
        }
    )
    rows.append(
        {
            "asset_type": "FEEDER",
            "asset_code": FEEDER_ID,
            "name": "IEEE Comprehensive Test Feeder (24.9 kV)",
            "feeder_id": FEEDER_ID,
            "parent_asset_code": "SUB-700",
            "vn_kv": 24.9,
            "pv_eligible": False,
            "attributes": {
                "bus_count": int(len(net.bus)),
                "line_count": int(len(net.line)),
                "transformer_count": int(len(net.trafo)),
                "load_count": int(len(net.load)),
                "regulator_handling": "taps FIXED at validated values",
                "data_class": "SYNTHETIC — IEEE test feeder, not a real DISCOM network",
            },
        }
    )

    # ---- buses ---------------------------------------------------------
    bus_frames = [(valid, True), (excluded, False)]
    for frame, eligible in bus_frames:
        for _, r in frame.iterrows():
            code = str(r["bus_id"])
            e = elec.loc[code] if code in elec.index else None
            rows.append(
                {
                    "asset_type": "BUS",
                    "asset_code": code,
                    "name": str(r.get("bus_name", code)),
                    "feeder_id": FEEDER_ID,
                    "parent_asset_code": _clean(r.get("transformer_association")),
                    "vn_kv": _clean(r.get("voltage_level_kv")),
                    "sn_kva": _clean(e["transformer_sn_kva"]) if e is not None else None,
                    "transformer_association": _clean(r.get("transformer_association")),
                    "feeder_section": _clean(r.get("feeder_section")),
                    "existing_load_kw": _clean(r.get("existing_load_kw")),
                    "existing_q_kvar": _clean(r.get("existing_q_kvar")),
                    "base_voltage_pu": _clean(
                        e["base_voltage_pu"] if e is not None else r.get("base_voltage_pu")
                    ),
                    "feeder_distance_km": _clean(e["feeder_distance_km"]) if e is not None else None,
                    "upstream_r_ohm": _clean(e["upstream_r_ohm"]) if e is not None else None,
                    "upstream_x_ohm": _clean(e["upstream_x_ohm"]) if e is not None else None,
                    "upstream_z_ohm": _clean(e["upstream_z_ohm"]) if e is not None else None,
                    "phase_configuration": _clean(r.get("phase_configuration")),
                    "pv_eligible": eligible,
                    "eligibility_reason": _clean(r.get("eligibility_reason")),
                    "attributes": {
                        "voltage_level_label": _clean(r.get("voltage_level_label")),
                        "pp_bus_idx": _clean(r.get("pp_bus_idx")),
                    },
                }
            )

    # ---- transformers --------------------------------------------------
    bus_name = {int(i): str(net.bus.name.iloc[int(i)]) for i in net.bus.index}
    for i, t in net.trafo.iterrows():
        rows.append(
            {
                "asset_type": "TRANSFORMER",
                "asset_code": str(t["name"]),
                "name": str(t["name"]),
                "feeder_id": FEEDER_ID,
                "parent_asset_code": bus_name.get(int(t["hv_bus"])),
                "vn_kv": float(t["vn_lv_kv"]),
                "sn_kva": float(t["sn_mva"]) * 1000.0,
                "pv_eligible": False,
                "attributes": {
                    "hv_bus": bus_name.get(int(t["hv_bus"])),
                    "lv_bus": bus_name.get(int(t["lv_bus"])),
                    "vn_hv_kv": float(t["vn_hv_kv"]),
                    "vn_lv_kv": float(t["vn_lv_kv"]),
                    "pp_trafo_idx": int(i),
                },
            }
        )

    # ---- lines ---------------------------------------------------------
    for i, ln in net.line.iterrows():
        rows.append(
            {
                "asset_type": "LINE",
                "asset_code": str(ln["name"]),
                "name": str(ln["name"]),
                "feeder_id": FEEDER_ID,
                "parent_asset_code": bus_name.get(int(ln["from_bus"])),
                "pv_eligible": False,
                "attributes": {
                    "from_bus": bus_name.get(int(ln["from_bus"])),
                    "to_bus": bus_name.get(int(ln["to_bus"])),
                    "length_km": float(ln["length_km"]),
                    "std_type": _clean(ln.get("std_type")),
                    "pp_line_idx": int(i),
                },
            }
        )

    return rows


def validate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["asset_type"]] = counts.get(r["asset_type"], 0) + 1

    eligible = [r for r in rows if r["pv_eligible"]]
    seen: set[tuple[str, str]] = set()
    dupes = []
    for r in rows:
        key = (r["asset_type"], r["asset_code"])
        if key in seen:
            dupes.append(key)
        seen.add(key)

    missing_elec = [
        r["asset_code"]
        for r in eligible
        if r.get("upstream_z_ohm") is None or r.get("transformer_association") is None
    ]

    return {
        "total_rows": len(rows),
        "by_type": counts,
        "pv_eligible_buses": len(eligible),
        "duplicate_keys": dupes,
        "eligible_missing_electrical_features": missing_elec,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="build and validate without writing")
    ap.add_argument("--out", default="", help="write the payload to this JSON file")
    args = ap.parse_args()

    rows = build_rows()
    report = validate(rows)

    print("=== grid_assets seed ===")
    print(json.dumps(report, indent=2))

    ok = (
        report["duplicate_keys"] == []
        and report["eligible_missing_electrical_features"] == []
        and report["pv_eligible_buses"] == 71
    )
    print(f"VALIDATION: {'PASS' if ok else 'FAIL'}")

    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"payload written to {args.out}")

    if args.dry_run:
        print("dry run — nothing written to Supabase")
        return 0 if ok else 1

    if not ok:
        print("refusing to seed: validation failed")
        return 1

    from app.db.service import db

    written = db.upsert_grid_assets(rows)
    print(f"upserted {written} grid_assets rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
