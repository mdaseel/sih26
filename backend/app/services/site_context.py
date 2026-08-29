"""SiteContextService — building footprints around a site, from OpenStreetMap.

Why footprints rather than photogrammetry
-----------------------------------------
Photorealistic 3D tiles are a captured surface: accurate, heavy, and from most
angles indistinguishable from an aerial photograph. They also carry no notion
of "this polygon is a building" — the mesh is one continuous skin, so there is
nothing to select, highlight, or measure a roof against.

A footprint is the opposite trade. It is a polygon with an identity: it can be
extruded to a block, coloured, picked, and asked how big its roof is. That is
what a planning tool actually needs, and it renders as clean low-poly geometry
instead of a photograph.

What is real here, and what is not
----------------------------------
The outline is real: it is the mapped footprint, in its true position.

The height usually is not. OSM carries `height` on a minority of buildings and
`building:levels` on rather more; where both are missing this service says so
via `height_source` rather than quietly emitting a default that looks like a
survey. The caller must present an assumed height as assumed.

Nothing here is an engineering input. The power flow reads pv_bus and the kW
columns, exactly as before.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Metres either side of the site to fetch. Big enough to give a street of
# context and something to cast a shadow; small enough to stay a polite query
# and a scene a laptop can draw.
DEFAULT_RADIUS_M = 160
MAX_RADIUS_M = 400

# Storeys to metres where only the storey count is mapped. A residential floor
# is about three metres including the slab.
METRES_PER_LEVEL = 3.0

# Used only when nothing at all is mapped, and always reported as assumed.
ASSUMED_HEIGHT_M = 9.0

_UNIT = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(m|metres?|meters?)?\s*$", re.I)


@dataclass
class Building:
    osm_id: str
    """[[lon, lat], ...] closed ring, outer boundary only."""
    footprint: list[list[float]] = field(default_factory=list)
    height_m: float = ASSUMED_HEIGHT_M
    levels: int | None = None
    """'height' | 'levels' | 'assumed' — how height_m was arrived at."""
    height_source: str = "assumed"
    name: str | None = None
    building_type: str | None = None
    """True for the building the requested point falls inside."""
    is_site: bool = False
    area_sqm: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _parse_height(tags: dict[str, str]) -> tuple[float, int | None, str]:
    """Metres, storeys, and which tag we believed."""
    raw = tags.get("height") or tags.get("building:height")
    if raw:
        match = _UNIT.match(raw)
        if match:
            try:
                metres = float(match.group(1))
                if 1.0 <= metres <= 500.0:
                    return metres, None, "height"
            except ValueError:
                pass

    levels_raw = tags.get("building:levels") or tags.get("levels")
    if levels_raw:
        try:
            levels = int(float(levels_raw))
            if 1 <= levels <= 160:
                return levels * METRES_PER_LEVEL, levels, "levels"
        except ValueError:
            pass

    return ASSUMED_HEIGHT_M, None, "assumed"


def _ring_area_sqm(ring: list[list[float]], latitude: float) -> float:
    """Shoelace on a local equirectangular projection.

    Over a building-sized polygon the distortion is far below the accuracy of
    the footprint itself, and it avoids pulling in a projection library for one
    number.
    """
    if len(ring) < 4:
        return 0.0
    lon_scale = 111_320.0 * math.cos(math.radians(latitude))
    lat_scale = 111_320.0

    total = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i][0] * lon_scale, ring[i][1] * lat_scale
        x2, y2 = ring[i + 1][0] * lon_scale, ring[i + 1][1] * lat_scale
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def _point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
    """Ray casting. Used to find which mapped building the applicant is in."""
    inside = False
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        if (y1 > lat) != (y2 > lat):
            x_at = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < x_at:
                inside = not inside
    return inside


class SiteContextService:
    def __init__(self, url: str = OVERPASS_URL, timeout_s: float = 25.0) -> None:
        self._url = url
        self._timeout = timeout_s

    def buildings(
        self, latitude: float, longitude: float, radius_m: int = DEFAULT_RADIUS_M
    ) -> dict[str, Any]:
        radius = max(40, min(int(radius_m), MAX_RADIUS_M))
        # Rounded to ~11 m so nearby requests share a cache entry. Two people on
        # the same street should not each cost Overpass a query.
        key = (round(latitude, 4), round(longitude, 4), radius)
        return _cached_buildings(self, key)

    # -- the uncached worker, called through the lru_cache above --
    def _fetch(
        self, latitude: float, longitude: float, radius_m: int
    ) -> dict[str, Any]:
        query = (
            f"[out:json][timeout:{int(self._timeout)}];"
            f'(way["building"](around:{radius_m},{latitude},{longitude});'
            f'relation["building"](around:{radius_m},{latitude},{longitude}););'
            "out geom;"
        )
        try:
            response = httpx.post(
                self._url,
                data={"data": query},
                timeout=self._timeout,
                headers={"User-Agent": "SolarGrid-AI/0.3 (rooftop solar screening)"},
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # noqa: BLE001 - degraded context, never a 500
            return {
                "buildings": [],
                "available": False,
                "note": (
                    "OpenStreetMap building data could not be fetched, so the scene "
                    f"shows terrain only ({type(exc).__name__})."
                ),
                "source": "OpenStreetMap via Overpass",
                "radius_m": radius_m,
            }

        buildings: list[Building] = []
        for element in payload.get("elements", []):
            ring = self._outer_ring(element)
            if len(ring) < 4:
                continue

            tags = element.get("tags") or {}
            height_m, levels, source = _parse_height(tags)
            building = Building(
                osm_id=f"{element.get('type')}/{element.get('id')}",
                footprint=ring,
                height_m=round(height_m, 2),
                levels=levels,
                height_source=source,
                name=tags.get("name"),
                building_type=tags.get("building"),
                area_sqm=round(_ring_area_sqm(ring, latitude), 1),
            )
            building.is_site = _point_in_ring(longitude, latitude, ring)
            buildings.append(building)

        # Nothing contains the point — pick the nearest footprint instead, so a
        # coordinate dropped in the yard still selects the right house.
        if buildings and not any(b.is_site for b in buildings):
            nearest = min(
                buildings,
                key=lambda b: min(
                    (p[0] - longitude) ** 2 + (p[1] - latitude) ** 2 for p in b.footprint
                ),
            )
            nearest.is_site = True

        # Largest first: the big ones are the landmarks, and if a scene has to be
        # trimmed it should keep them.
        buildings.sort(key=lambda b: b.area_sqm, reverse=True)

        mapped = sum(1 for b in buildings if b.height_source != "assumed")
        return {
            "buildings": [b.as_dict() for b in buildings[:240]],
            "available": bool(buildings),
            "count": len(buildings),
            "with_mapped_height": mapped,
            "source": "OpenStreetMap via Overpass",
            "radius_m": radius_m,
            "note": (
                "Outlines are mapped footprints in their true positions. Heights "
                f"are mapped for {mapped} of {len(buildings)}; the rest are drawn at "
                f"an assumed {ASSUMED_HEIGHT_M:g} m and are marked as assumed."
                if buildings
                else "No buildings are mapped in OpenStreetMap around this point."
            ),
        }

    @staticmethod
    def _outer_ring(element: dict[str, Any]) -> list[list[float]]:
        """[[lon, lat], ...] closed. Relations contribute their outer way only."""
        if element.get("type") == "way":
            geometry = element.get("geometry") or []
            ring = [[p["lon"], p["lat"]] for p in geometry if "lon" in p and "lat" in p]
        else:
            ring = []
            for member in element.get("members") or []:
                if member.get("role") != "outer":
                    continue
                geometry = member.get("geometry") or []
                ring = [
                    [p["lon"], p["lat"]] for p in geometry if "lon" in p and "lat" in p
                ]
                if len(ring) >= 4:
                    break

        if len(ring) >= 3 and ring[0] != ring[-1]:
            ring.append(ring[0])
        return ring


# The cache lives outside the class so the service itself stays a plain object.
@lru_cache(maxsize=256)
def _cached_buildings(
    service: SiteContextService, key: tuple[float, float, int]
) -> dict[str, Any]:
    latitude, longitude, radius = key
    return service._fetch(latitude, longitude, radius)


@lru_cache
def get_site_context_service() -> SiteContextService:
    return SiteContextService()
