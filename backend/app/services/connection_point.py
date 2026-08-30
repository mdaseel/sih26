"""Working out which connection point serves an address.

Why this exists
---------------
A householder knows their address, their roof and their electricity bill. They
do not know which LV bus, transformer or feeder section serves them — that is a
DISCOM record, held in the DISCOM's GIS. Asking a citizen to pick one from a
list of 71 was asking them to guess at engineering input that then drove a
power flow, and a guess there is worse than no answer: it produces a confident
assessment of the wrong part of the network.

What this can and cannot claim
------------------------------
The feeder is the IEEE Comprehensive Test Feeder, a synthetic research network.
Its buses were given map coordinates by precompute_grid_map so the DISCOM map
has something to draw, anchored at an arbitrary point — the map itself says so.

So "the bus nearest your house" is a real computation over a layout that is not
where any of this physically is. It gives a stable, explainable, evenly spread
assignment, and it is emphatically **provisional**: the DISCOM confirms the
actual connection point, exactly as it would for a real application. Every
response here carries that qualification, and the UI must show it.

What it does not do is invent electrical values. Once a bus is chosen, every
number attached to it — voltage level, transformer rating, connected load,
impedance — is read from the feeder model, the same source the power flow uses.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

from app.db.service import db
from app.services.grid_assets import get_grid_asset_service

EARTH_RADIUS_KM = 6371.0088

ASSIGNMENT_NOTE = (
    "Assigned automatically from the location on this application. The feeder "
    "model is a synthetic research network, so this is a provisional connection "
    "point for screening — the DISCOM confirms the actual one on review."
)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


class ConnectionPointService:
    """Resolves an applicant's coordinates to a connection point."""

    def _located_buses(self) -> list[dict[str, Any]]:
        """PV-eligible buses that carry map coordinates.

        Read through the service role: grid_assets is reference data with no
        client write policy, and every caller here has already been
        authenticated by the route.
        """
        rows = (
            db.as_service()
            .table("grid_assets")
            .select("asset_code,latitude,longitude")
            .eq("asset_type", "BUS")
            .eq("pv_eligible", True)
            .execute()
        ).data or []
        return [
            r
            for r in rows
            if r.get("latitude") is not None and r.get("longitude") is not None
        ]

    def resolve(self, latitude: float, longitude: float) -> dict[str, Any]:
        """The connection point that will screen this address, and its grid data.

        Falls back to the lowest-numbered eligible bus when no bus carries
        coordinates — that happens only before precompute_grid_map has been
        run, and returning something deterministic beats refusing the whole
        application over missing reference data. The response says which
        happened.
        """
        grid = get_grid_asset_service()
        located = self._located_buses()

        if located:
            nearest = min(
                located,
                key=lambda b: _haversine_km(
                    latitude, longitude, float(b["latitude"]), float(b["longitude"])
                ),
            )
            bus_id = str(nearest["asset_code"])
            separation_km = round(
                _haversine_km(
                    latitude,
                    longitude,
                    float(nearest["latitude"]),
                    float(nearest["longitude"]),
                ),
                3,
            )
            method = "NEAREST_MAPPED_BUS"
        else:
            eligible = grid.eligible_bus_ids()
            if not eligible:
                raise RuntimeError("The feeder model exposes no PV-eligible buses.")
            bus_id = eligible[0]
            separation_km = None
            method = "FALLBACK_FIRST_ELIGIBLE"

        bus = grid.get(bus_id)

        return {
            "pv_bus": bus.bus_id,
            "assignment_method": method,
            "separation_km": separation_km,
            "provisional": True,
            "note": ASSIGNMENT_NOTE,
            # Everything below is read from the feeder model, not inferred.
            "voltage_level_kv": bus.vn_kv,
            "voltage_level_label": bus.voltage_level_label,
            "phase_configuration": bus.phase_configuration,
            "transformer": bus.transformer_association,
            "transformer_sn_kva": bus.transformer_sn_kva,
            "feeder_section": bus.feeder_section,
            "connected_load_kw": bus.existing_load_kw,
            "base_voltage_pu": bus.base_voltage_pu,
            "feeder_distance_km": bus.feeder_distance_km,
            "upstream_r_ohm": bus.upstream_r_ohm,
            "upstream_x_ohm": bus.upstream_x_ohm,
            "upstream_z_ohm": bus.upstream_z_ohm,
            "data_source": "feeder_network.json (IEEE Comprehensive Test Feeder)",
        }


@lru_cache
def get_connection_point_service() -> ConnectionPointService:
    return ConnectionPointService()
