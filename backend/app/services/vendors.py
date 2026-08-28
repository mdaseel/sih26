"""VendorService — registration, review, and customer-facing discovery.

Visibility rule (non-negotiable): only APPROVED and active vendors are ever
returned to a customer. That is enforced twice — by this service and by the
`vendors_public_approved` RLS policy — so a mistake in one layer does not
expose an unvetted installer to the public.

Where the customer is
---------------------
Vendor distance is computed ONLY from an application's own latitude/longitude,
which the applicant supplied. It is never computed from the connection point's
map coordinates: those are the synthetic layout described in TopologyService,
and measuring to them would produce a confident-looking number that means
nothing. When the applicant gave no location, distance comes back as null and
the API says why.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.db.service import db
from app.models.enums import VendorStatus
from app.services.routing import get_routing_service

# The only combination a customer may see.
PUBLIC_STATUS = VendorStatus.APPROVED.value

CUSTOMER_FIELDS = (
    "id,business_name,representative_name,email,phone,address_line,district,state,"
    "pincode,latitude,longitude,service_areas,installation_capacity_kw,"
    "years_experience,rating,completed_installations,status,is_active,verified_at"
)


class VendorService:
    # ---------------- registration ----------------

    def register(self, access_token: str, owner_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Self-registration. Always lands as PENDING.

        The status is set here rather than taken from the request, and the RLS
        insert policy independently requires status = 'PENDING' with no
        verifier — so a crafted payload cannot self-approve.
        """
        row = {
            **payload,
            "owner_id": owner_id,
            "status": VendorStatus.PENDING.value,
            "verified_by": None,
            "verified_at": None,
        }
        client = db.as_user(access_token)
        result = client.table("vendors").insert(row).execute()
        return result.data[0] if result.data else {}

    def for_owner(self, owner_id: str) -> dict[str, Any] | None:
        res = (
            db.as_service()
            .table("vendors")
            .select("*")
            .eq("owner_id", owner_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    # ---------------- customer-facing discovery ----------------

    def public_vendors(self) -> list[dict[str, Any]]:
        """APPROVED and active only."""
        res = (
            db.as_service()
            .table("vendors")
            .select(CUSTOMER_FIELDS)
            .eq("status", PUBLIC_STATUS)
            .eq("is_active", True)
            .order("business_name")
            .execute()
        )
        return res.data or []

    def discover(
        self,
        customer_lat: float | None = None,
        customer_lon: float | None = None,
        district: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Vendors a customer may choose from, nearest first when possible."""
        routing = get_routing_service()
        vendors = self.public_vendors()

        out: list[dict[str, Any]] = []
        for v in vendors:
            distance = routing.distance(customer_lat, customer_lon, v["latitude"], v["longitude"])
            serves = True
            if district and v.get("service_areas"):
                serves = district.strip().lower() in {
                    a.strip().lower() for a in v["service_areas"]
                }

            out.append(
                {
                    "id": v["id"],
                    "business_name": v["business_name"],
                    "representative_name": v["representative_name"],
                    "verified": v["status"] == PUBLIC_STATUS and bool(v["is_active"]),
                    "verified_at": v.get("verified_at"),
                    "email": v.get("email"),
                    "phone": v.get("phone"),
                    "address_line": v.get("address_line"),
                    "district": v.get("district"),
                    "state": v.get("state"),
                    "service_areas": v.get("service_areas") or [],
                    "serves_this_district": serves,
                    "rating": v.get("rating"),
                    "completed_installations": v.get("completed_installations"),
                    "installation_capacity_kw": v.get("installation_capacity_kw"),
                    "years_experience": v.get("years_experience"),
                    "distance": distance.as_dict() if distance else None,
                }
            )

        # Vendors with a measured distance sort first and nearest-first among
        # themselves; the rest keep alphabetical order rather than being ranked
        # on a number that was never measured.
        out.sort(
            key=lambda v: (
                v["distance"] is None,
                v["distance"]["distance_km"] if v["distance"] else 0.0,
                v["business_name"],
            )
        )

        located = sum(1 for v in out if v["distance"] is not None)
        return {
            "vendors": out[:limit],
            "total": len(out),
            "with_distance": located,
            "routing": routing.describe(),
            "distance_note": (
                "Distances are straight-line, not travel distance, until a routing "
                "provider is configured."
                if not routing.routing_available
                else "Distances are road routes from the configured routing provider."
            ),
            "location_note": (
                "Distance is measured from the address on the application. Applications "
                "without a location show no distance — the connection point's map "
                "coordinates are a synthetic layout and would give a meaningless figure."
            ),
        }

    # ---------------- DISCOM review ----------------

    def list_for_review(self) -> list[dict[str, Any]]:
        res = (
            db.as_service()
            .table("vendors")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []

    def review(
        self, vendor_id: str, status: VendorStatus, reviewer_id: str, reason: str | None = None
    ) -> dict[str, Any]:
        """Set a vendor's status. Privileged: performed with the service role
        after the caller's DISCOM role has been checked, because `status` is not
        a client-writable column (migration 0004)."""
        update: dict[str, Any] = {"status": status.value, "rejection_reason": reason}
        if status is VendorStatus.APPROVED:
            update |= {"verified_by": reviewer_id, "verified_at": "now()"}
        elif status in (VendorStatus.REJECTED, VendorStatus.SUSPENDED):
            update |= {"is_active": status is not VendorStatus.SUSPENDED}

        res = (
            db.as_service().table("vendors").update(update).eq("id", vendor_id).execute()
        )
        return res.data[0] if res.data else {}


@lru_cache
def get_vendor_service() -> VendorService:
    return VendorService()
