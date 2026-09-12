"""HouseMappingService — bus -> locality -> houses, synthetic but stable.

Why this exists
---------------
Training datasets identify a rooftop only by `pv_bus` (71 LV buses in
valid_pv_buses.csv). There is no house_id, no street, no lat/lon in any
training CSV. Live applications add lat/lon, resolved to a provisional
`pv_bus` by ConnectionPointService (nearest mapped BUS, haversine).

For a demo the user wants: select bus -> see particular house(s)/locality ->
see power flowing + ML SAFE/CAUTION/CONSTRAINED on the 3D twin.

What is real / synthetic here
------------------------------
- Real: bus_id, transformer_association, feeder_section, existing_load_kw,
  base_voltage_pu, feeder_distance_km, upstream R/X/Z (from feeder model);
  electrical path source->bus from TopologyService (respect_switches=True);
  OSM footprints where SiteContextService finds them.
- Synthetic: house lat/lon offsets (20-60m N/S of bus synthetic coord),
  house_id {bus}-{A,B,C}. Distances along feeder real, absolute placement
  illustrative (same caveat as TopologyService.geo_positions).
- Nothing here is an ML or power-flow input beyond pv_bus. ML working
  untouched: this service never predicts, never thresholds, never retrains.

Determinism: same bus always yields same houses (no random, no seed drift).
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

from app.services.grid_assets import get_grid_asset_service
from app.services.topology import get_topology_service

# Same illustrative anchor as backend/scripts/precompute_grid_map.py
DEFAULT_ANCHOR_LAT = 12.9716
DEFAULT_ANCHOR_LON = 77.5946

# House offsets (metres N/S of bus point). 2 houses default, 3rd for
# high-load / commercial-ish buses so dense localities read denser.
OFFSET_SET_A = [25.0, -35.0]
OFFSET_SET_B = [25.0, -35.0, 60.0]


def _houses_for_bus(bus_id: str, lat: float, lon: float, n: int) -> list[dict[str, Any]]:
    offsets = OFFSET_SET_B if n >= 3 else OFFSET_SET_A
    out: list[dict[str, Any]] = []
    for i, dn in enumerate(offsets[:n]):
        suffix = "ABC"[i]
        dlat = dn / 111_320.0
        # small east jog so A/B/C don't sit on one vertical line
        deast = (12.0 if i % 2 == 0 else -12.0)
        dlon = deast / (111_320.0 * max(math.cos(math.radians(lat)), 1e-6))
        out.append(
            {
                "house_id": f"{bus_id}-{suffix}",
                "pv_bus": str(bus_id),
                "latitude": round(lat + dlat, 7),
                "longitude": round(lon + dlon, 7),
                "offset_m_north": dn,
                "offset_m_east": deast,
                "geometry_source": "SYNTHETIC_HOUSE_OFFSET",
                "note": (
                    "Illustrative house offset from synthetic bus coord. "
                    "Electrical screening uses pv_bus only."
                ),
            }
        )
    return out


class HouseMappingService:
    def houses_for_bus(self, bus_id: str) -> dict[str, Any]:
        grid = get_grid_asset_service()
        bus = grid.get(str(bus_id))  # raises Unknown/Ineligible, mapped to 404/422 upstream
        topo = get_topology_service()
        geo = topo.geo_positions(DEFAULT_ANCHOR_LAT, DEFAULT_ANCHOR_LON)
        pos = geo.get(str(bus_id))
        if pos is None:
            raise RuntimeError(f"No synthetic position for bus {bus_id}")
        # 3 houses for buses with meaningful load (>=40kW) else 2
        n = 3 if (bus.existing_load_kw or 0) >= 40.0 else 2
        houses = _houses_for_bus(str(bus_id), pos["latitude"], pos["longitude"], n)
        path = topo.path_to(str(bus_id))
        return {
            "pv_bus": str(bus_id),
            "locality": {
                "feeder_section": bus.feeder_section,
                "transformer_association": bus.transformer_association,
                "transformer_sn_kva": bus.transformer_sn_kva,
                "voltage_level_kv": bus.vn_kv,
                "voltage_level_label": bus.voltage_level_label,
                "phase_configuration": bus.phase_configuration,
                "existing_load_kw": bus.existing_load_kw,
                "base_voltage_pu": bus.base_voltage_pu,
                "feeder_distance_km": bus.feeder_distance_km,
            },
            "bus_position": pos,
            "houses": houses,
            "path": path,
            "path_length": len(path),
            "provisional": True,
            "data_class": "Prototype • Synthetic Grid Data",
        }

    def all_localities(self) -> list[dict[str, Any]]:
        grid = get_grid_asset_service()
        topo = get_topology_service()
        geo = topo.geo_positions(DEFAULT_ANCHOR_LAT, DEFAULT_ANCHOR_LON)
        out: list[dict[str, Any]] = []
        for b in grid.eligible_bus_ids():
            bus = grid.get(b)
            pos = geo.get(b, {})
            out.append(
                {
                    "pv_bus": b,
                    "feeder_section": bus.feeder_section,
                    "transformer_association": bus.transformer_association,
                    "existing_load_kw": bus.existing_load_kw,
                    "house_count": 3 if (bus.existing_load_kw or 0) >= 40.0 else 2,
                    "latitude": pos.get("latitude"),
                    "longitude": pos.get("longitude"),
                    "distance_km": pos.get("distance_km"),
                }
            )
        return out


@lru_cache
def get_house_mapping_service() -> HouseMappingService:
    return HouseMappingService()
