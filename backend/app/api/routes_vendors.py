"""Vendor routes — registration, customer discovery, and DISCOM review.

Phase 8 scope: the minimum vendor backend plus customer-facing discovery. The
vendor's own dashboard is Phase 9 and is deliberately not here.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, get_current_user, require_discom
from app.db.service import db
from app.models.enums import VendorStatus
from app.services.routing import get_routing_service
from app.services.vendors import get_vendor_service

router = APIRouter(prefix="/api", tags=["vendors"])


class VendorRegistration(BaseModel):
    business_name: str = Field(min_length=2, max_length=200)
    representative_name: str | None = Field(default=None, max_length=200)
    email: str | None = None
    phone: str | None = Field(default=None, max_length=20)
    address_line: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = Field(default=None, max_length=10)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    registration_number: str | None = None
    gst_number: str | None = None
    service_areas: list[str] = Field(default_factory=list, max_length=50)
    installation_capacity_kw: float | None = Field(default=None, ge=0)
    years_experience: int | None = Field(default=None, ge=0, le=100)


class VendorReview(BaseModel):
    status: str = Field(description="APPROVED, REJECTED, UNDER_REVIEW or SUSPENDED")
    reason: str | None = Field(default=None, max_length=2000)


# ============================================================
#  Customer-facing discovery
# ============================================================
@router.get("/vendors")
def list_vendors(
    district: str | None = None,
    limit: int = 20,
    user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Vendors a customer may choose from.

    Only APPROVED and active vendors are returned. There is no query parameter
    that widens this — an unvetted vendor is not addressable here at all.
    """
    return get_vendor_service().discover(district=district, limit=limit)


@router.get("/applications/{application_id}/vendors")
def vendors_for_application(
    application_id: str,
    limit: int = 20,
    user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Vendors near a specific application, nearest first where a distance
    could actually be measured.

    The application is read with the caller's own token, so Row Level Security
    decides whether they may see it before any vendor lookup happens.
    """
    application = db.get_application(user.access_token, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    lat, lon = application.get("latitude"), application.get("longitude")
    result = get_vendor_service().discover(
        customer_lat=lat,
        customer_lon=lon,
        district=application.get("district"),
        limit=limit,
    )
    result["application_id"] = application_id
    result["customer_location_known"] = lat is not None and lon is not None
    if not result["customer_location_known"]:
        result["distance_note"] = (
            "This application has no address coordinates, so no distance can be "
            "measured. Vendors are listed alphabetically."
        )
    return result


@router.get("/routing/status")
def routing_status(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """What the distance figures actually mean right now."""
    return get_routing_service().describe()


# ============================================================
#  Citizen map
# ============================================================
# An accepted booking. A requested one is a customer's intention, not an
# arrangement, so the map does not draw a route for it yet.
ENGAGED_APPOINTMENT_STATUSES = ("CONFIRMED", "RESCHEDULED", "COMPLETED")


@router.get("/citizen/map")
def citizen_map(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """What a citizen needs on a map: their sites, their installers, the way between.

    Deliberately not the feeder. Buses, transformers and line loadings are the
    DISCOM's instrument panel; to a householder they are noise around the one
    question they have, which is who is coming and from where. That view still
    exists in full at /api/map for the roles that need it.

    Only APPROVED and active vendors appear. A vendor whose application the
    citizen has actually engaged is marked, and the route is drawn only once
    that vendor has accepted -- an unanswered request is not an appointment.
    """
    applications = [
        {
            "id": a["id"],
            "application_number": a["application_number"],
            "address_line": a.get("address_line"),
            "district": a.get("district"),
            "state": a.get("state"),
            "pincode": a.get("pincode"),
            "latitude": a.get("latitude"),
            "longitude": a.get("longitude"),
            "status": a["status"],
            "new_pv_kw": float(a["new_pv_kw"]),
            "total_pv_kw": float(a["total_pv_kw"]),
            "created_at": a["created_at"],
        }
        for a in db.list_applications_for_user(user.access_token)
    ]
    located = [a for a in applications if a["latitude"] is not None and a["longitude"] is not None]

    # RLS scopes these to the caller's own bookings.
    appointments = (
        db.as_user(user.access_token)
        .table("appointments")
        .select("id,application_id,vendor_id,status,scheduled_at,purpose,created_at")
        .order("created_at", desc=True)
        .execute()
    ).data or []

    engaged_vendor_ids = {
        a["vendor_id"] for a in appointments if a["status"] in ENGAGED_APPOINTMENT_STATUSES
    }
    requested_vendor_ids = {a["vendor_id"] for a in appointments} - engaged_vendor_ids

    service = get_vendor_service()
    routing = get_routing_service()

    vendors: list[dict[str, Any]] = []
    for v in service.public_vendors():
        engaged = v["id"] in engaged_vendor_ids
        vendors.append(
            {
                "id": v["id"],
                "business_name": v["business_name"],
                "representative_name": v.get("representative_name"),
                "phone": v.get("phone"),
                "email": v.get("email"),
                "address_line": v.get("address_line"),
                "district": v.get("district"),
                "state": v.get("state"),
                "latitude": v.get("latitude"),
                "longitude": v.get("longitude"),
                "rating": v.get("rating"),
                "completed_installations": v.get("completed_installations"),
                "installation_capacity_kw": v.get("installation_capacity_kw"),
                "years_experience": v.get("years_experience"),
                "service_areas": v.get("service_areas") or [],
                "verified": True,  # public_vendors() returns APPROVED + active only
                "verified_at": v.get("verified_at"),
                "engaged": engaged,
                "requested": v["id"] in requested_vendor_ids,
            }
        )

    # One route per accepted booking whose two ends are both located.
    vendor_by_id = {v["id"]: v for v in vendors}
    app_by_id = {a["id"]: a for a in located}

    routes: list[dict[str, Any]] = []
    for appointment in appointments:
        if appointment["status"] not in ENGAGED_APPOINTMENT_STATUSES:
            continue
        application = app_by_id.get(appointment["application_id"])
        vendor = vendor_by_id.get(appointment["vendor_id"])
        if not application or not vendor:
            continue

        route = routing.distance(
            vendor["latitude"], vendor["longitude"],
            application["latitude"], application["longitude"],
        )
        if route is None:
            continue

        routes.append(
            {
                "appointment_id": appointment["id"],
                "application_id": application["id"],
                "application_number": application["application_number"],
                "vendor_id": vendor["id"],
                "vendor_name": vendor["business_name"],
                "appointment_status": appointment["status"],
                "scheduled_at": appointment["scheduled_at"],
                **route.as_dict(),
            }
        )

    return {
        "applications": applications,
        "located_applications": len(located),
        "vendors": vendors,
        "routes": routes,
        "routing": routing.describe(),
        "distance_note": (
            "Distances and drawn paths are road routes from the configured routing "
            "provider."
            if routing.routing_available
            else "No routing provider is configured, so a drawn path is a direct "
            "connector and its distance is straight-line — the real journey is longer."
        ),
        "location_note": (
            "Your sites are placed from the coordinates on each application. An "
            "application without coordinates cannot be placed and is listed instead."
        ),
    }


# ============================================================
#  Vendor self-registration
# ============================================================
@router.post("/vendors/register", status_code=201)
def register_vendor(
    payload: VendorRegistration, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Register a business. It is created PENDING and is invisible to customers
    until a DISCOM approves it."""
    service = get_vendor_service()
    if service.for_owner(user.id) is not None:
        raise HTTPException(status_code=409, detail="This account already has a vendor profile")

    created = service.register(user.access_token, user.id, payload.model_dump())
    if not created:
        raise HTTPException(status_code=400, detail="Vendor profile could not be created")

    db.audit(
        action="vendor.register",
        entity_type="vendors",
        entity_id=created.get("id"),
        actor_id=user.id,
        actor_role=user.role.value,
        after_state={"business_name": created.get("business_name"), "status": created.get("status")},
    )
    return {
        "vendor": created,
        "note": (
            "Registered as PENDING. Customers cannot see this business until a DISCOM "
            "reviewer approves it."
        ),
    }


@router.get("/vendors/me")
def my_vendor(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    vendor = get_vendor_service().for_owner(user.id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="No vendor profile for this account")
    return vendor


# ============================================================
#  DISCOM review
# ============================================================
@router.get("/discom/vendors")
def vendors_for_review(user: CurrentUser = Depends(require_discom)) -> dict[str, Any]:
    """Every vendor, whatever their status, for the review queue."""
    vendors = get_vendor_service().list_for_review()
    counts: dict[str, int] = {}
    for v in vendors:
        counts[v["status"]] = counts.get(v["status"], 0) + 1
    return {
        "vendors": vendors,
        "counts": counts,
        "visible_to_customers": sum(
            1 for v in vendors if v["status"] == "APPROVED" and v["is_active"]
        ),
    }


@router.post("/discom/vendors/{vendor_id}/review")
def review_vendor(
    vendor_id: str, payload: VendorReview, user: CurrentUser = Depends(require_discom)
) -> dict[str, Any]:
    """Approve, reject, suspend, or move a vendor into review.

    Approving is what makes a business visible to customers, so it is a DISCOM
    action performed by the backend and written to the audit log.
    """
    try:
        status = VendorStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of {[s.value for s in VendorStatus]}",
        ) from exc

    if status is VendorStatus.PENDING:
        raise HTTPException(status_code=422, detail="A vendor cannot be moved back to PENDING")

    service = get_vendor_service()
    existing = (
        db.as_service().table("vendors").select("*").eq("id", vendor_id).execute()
    ).data
    if not existing:
        raise HTTPException(status_code=404, detail="Vendor not found")

    before = existing[0]
    updated = service.review(vendor_id, status, user.id, payload.reason)

    db.audit(
        action=f"vendor.review.{status.value.lower()}",
        entity_type="vendors",
        entity_id=vendor_id,
        actor_id=user.id,
        actor_role=user.role.value,
        before_state={"status": before["status"], "is_active": before["is_active"]},
        after_state={"status": status.value, "reason": payload.reason},
    )

    return {
        "vendor": updated,
        "status": status.value,
        "visible_to_customers": status is VendorStatus.APPROVED and bool(updated.get("is_active")),
    }
