"""RoutingService — distance between two points, behind an interface.

Why this is not just a haversine call
-------------------------------------
Straight-line distance is not travel distance. A vendor 4 km away as the crow
flies may be a 15 km drive across a river. Presenting one as the other would
mislead a customer choosing an installer, so this module keeps them strictly
distinguished:

    method = "STRAIGHT_LINE"  ->  is_route = False
    method = "OSRM"           ->  is_route = True

Callers must surface `is_route`. A straight-line result is never described as
a route, a drive, or a travel time anywhere in the API or the UI.

Configuring a real provider
---------------------------
Set these in .env and the OSRM provider takes over automatically:

    ROUTING_PROVIDER=osrm
    ROUTING_BASE_URL=https://router.project-osrm.org

Any routing service with an OSRM-compatible interface works. To add a
different one (Google Directions, Mapbox, OpenRouteService), implement
RoutingProvider and register it in get_routing_service — that is the whole
integration point.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol

import httpx


@dataclass(frozen=True)
class RouteResult:
    """A measured separation between two points.

    distance_km means different things depending on `is_route`, which is why
    the flag travels with the number instead of being inferred later.

    `geometry` is [[lon, lat], ...] for drawing. It follows the same rule as
    the distance: with a real provider it is the road the vehicle would take,
    and without one it is just the two endpoints joined -- a connector, not a
    path anything could drive. `is_route` says which, and any map drawing this
    must label it accordingly.
    """

    distance_km: float
    duration_minutes: float | None
    method: str
    is_route: bool
    note: str
    geometry: list[list[float]] | None = None

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


class RoutingProvider(Protocol):
    name: str
    is_route: bool

    def distance(
        self, from_lat: float, from_lon: float, to_lat: float, to_lon: float
    ) -> RouteResult: ...


class StraightLineProvider:
    """Great-circle distance. A lower bound on travel distance, never a route."""

    name = "STRAIGHT_LINE"
    is_route = False

    def distance(
        self, from_lat: float, from_lon: float, to_lat: float, to_lon: float
    ) -> RouteResult:
        radius_km = 6371.0088
        p1, p2 = math.radians(from_lat), math.radians(to_lat)
        dp = math.radians(to_lat - from_lat)
        dl = math.radians(to_lon - from_lon)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        km = 2 * radius_km * math.asin(math.sqrt(a))

        return RouteResult(
            distance_km=round(km, 3),
            duration_minutes=None,
            method=self.name,
            is_route=False,
            note=(
                "Straight-line distance. Actual travel distance is longer and is not "
                "known — no routing provider is configured."
            ),
            geometry=[[from_lon, from_lat], [to_lon, to_lat]],
        )


class OSRMProvider:
    """Road distance and drive time from an OSRM-compatible service."""

    name = "OSRM"
    is_route = True

    def __init__(self, base_url: str, timeout_s: float = 8.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_s
        self._fallback = StraightLineProvider()

    def distance(
        self, from_lat: float, from_lon: float, to_lat: float, to_lon: float
    ) -> RouteResult:
        url = (
            f"{self._base}/route/v1/driving/"
            f"{from_lon},{from_lat};{to_lon},{to_lat}"
            "?overview=simplified&geometries=geojson&alternatives=false"
        )
        try:
            response = httpx.get(url, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()
            route = payload["routes"][0]
            coordinates = (route.get("geometry") or {}).get("coordinates")
            return RouteResult(
                distance_km=round(route["distance"] / 1000.0, 3),
                duration_minutes=round(route["duration"] / 60.0, 1),
                method=self.name,
                is_route=True,
                note="Road distance and drive time from the configured routing service.",
                geometry=coordinates if coordinates else None,
            )
        except Exception as exc:  # noqa: BLE001 - any failure degrades, never crashes
            # Degrade to straight line, but say so. Silently substituting a
            # different measurement would be worse than an honest downgrade.
            fallback = self._fallback.distance(from_lat, from_lon, to_lat, to_lon)
            return RouteResult(
                distance_km=fallback.distance_km,
                duration_minutes=None,
                method="STRAIGHT_LINE_FALLBACK",
                is_route=False,
                note=(
                    "Routing service unavailable, so this is straight-line distance, "
                    f"not a route ({type(exc).__name__})."
                ),
                geometry=fallback.geometry,
            )


class RoutingService:
    def __init__(self, provider: RoutingProvider) -> None:
        self.provider = provider

    @property
    def routing_available(self) -> bool:
        """True only when distances are real routes."""
        return self.provider.is_route

    def distance(
        self,
        from_lat: float | None,
        from_lon: float | None,
        to_lat: float | None,
        to_lon: float | None,
    ) -> RouteResult | None:
        """None when either endpoint has no usable location.

        Returning None rather than a placeholder matters: a fabricated distance
        would rank vendors on a number nobody measured.
        """
        if None in (from_lat, from_lon, to_lat, to_lon):
            return None
        return self.provider.distance(
            float(from_lat), float(from_lon), float(to_lat), float(to_lon)
        )

    def describe(self) -> dict[str, Any]:
        return {
            "provider": self.provider.name,
            "returns_real_routes": self.provider.is_route,
            "integration_point": (
                "Set ROUTING_PROVIDER=osrm and ROUTING_BASE_URL in .env, or implement "
                "RoutingProvider in backend/app/services/routing.py."
            ),
        }


@lru_cache
def get_routing_service() -> RoutingService:
    provider_name = (os.environ.get("ROUTING_PROVIDER") or "").strip().lower()
    base_url = (os.environ.get("ROUTING_BASE_URL") or "").strip()

    if provider_name == "osrm" and base_url:
        return RoutingService(OSRMProvider(base_url))
    # Default to public OSRM demo for citizen/vendor road routing
    # (Google-like shortest path). If unreachable, OSRMProvider degrades
    # to straight line with a note — never fails the request.
    if not provider_name and not base_url:
        return RoutingService(OSRMProvider("https://router.project-osrm.org"))
    return RoutingService(StraightLineProvider())
