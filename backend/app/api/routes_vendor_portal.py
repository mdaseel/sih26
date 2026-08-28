"""Vendor portal routes, plus the two endpoints that bracket it:
the citizen engaging a vendor, and the DISCOM verifying finished work.

The verification boundary appears twice on purpose. A vendor calling the
installation-status endpoint with VERIFIED gets a 403 from the service, and the
only route that can set it — /api/discom/installations/{id}/verify — is guarded
by require_discom.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, get_current_user, require_discom
from app.db.service import db
from app.models.enums import AppointmentStatus, InstallationStatus
from app.services.storage import MAX_FILE_BYTES, UploadRejected, get_storage_service
from app.services.vendor_portal import VendorAccessError, get_vendor_portal

router = APIRouter(prefix="/api", tags=["vendor-portal"])


def _vendor(user: CurrentUser) -> dict[str, Any]:
    try:
        return get_vendor_portal().vendor_for_user(user.id)
    except VendorAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


# ============================================================
#  Citizen engages a vendor  (creates the lead)
# ============================================================
class VendorSelection(BaseModel):
    vendor_id: str
    scheduled_at: str = Field(description="ISO timestamp for the requested site visit")
    purpose: str = Field(default="SITE_VISIT", max_length=50)
    notes: str | None = Field(default=None, max_length=2000)


@router.post("/applications/{application_id}/select-vendor", status_code=201)
def select_vendor(
    application_id: str, payload: VendorSelection, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Choose an installer and request a site visit.

    Written with the caller's own token so RLS enforces all three conditions at
    once: the application is theirs, the citizen_id is themselves, and the
    vendor is APPROVED and active. An unapproved vendor cannot be engaged even
    if its id is known.
    """
    application = db.get_application(user.access_token, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    row = {
        "application_id": application_id,
        "vendor_id": payload.vendor_id,
        "citizen_id": user.id,
        "scheduled_at": payload.scheduled_at,
        "purpose": payload.purpose,
        "notes": payload.notes,
        "status": AppointmentStatus.REQUESTED.value,
    }

    try:
        created = db.as_user(user.access_token).table("appointments").insert(row).execute()
    except Exception as exc:  # noqa: BLE001 - RLS refusal is the expected failure
        raise HTTPException(
            status_code=403,
            detail=(
                "Could not book this vendor. Only approved, active vendors can be "
                "engaged, and only for your own application."
            ),
        ) from exc

    if not created.data:
        raise HTTPException(status_code=403, detail="Booking refused")

    db.audit(
        action="application.select_vendor",
        entity_type="appointments",
        entity_id=created.data[0]["id"],
        actor_id=user.id,
        actor_role=user.role.value,
        after_state={"application_id": application_id, "vendor_id": payload.vendor_id},
    )
    return {"appointment": created.data[0]}


@router.get("/applications/{application_id}/appointments")
def application_appointments(
    application_id: str, user: CurrentUser = Depends(get_current_user)
) -> list[dict[str, Any]]:
    """A citizen's own bookings for an application. RLS scopes the rows."""
    res = (
        db.as_user(user.access_token)
        .table("appointments")
        .select("*")
        .eq("application_id", application_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


# ============================================================
#  Vendor portal
# ============================================================
@router.get("/vendor/summary")
def vendor_summary(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    return get_vendor_portal().summary(_vendor(user))


@router.get("/vendor/leads")
def vendor_leads(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    """Requests from customers, with the application each refers to."""
    return get_vendor_portal().leads(_vendor(user))


class LeadResponse(BaseModel):
    accept: bool
    note: str | None = Field(default=None, max_length=2000)


@router.post("/vendor/leads/{appointment_id}/respond")
def respond_to_lead(
    appointment_id: str, payload: LeadResponse, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    portal = get_vendor_portal()
    try:
        result = portal.respond_to_lead(_vendor(user), appointment_id, payload.accept, payload.note)
    except VendorAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    db.audit(
        action=f"vendor.lead.{'accept' if payload.accept else 'reject'}",
        entity_type="appointments",
        entity_id=appointment_id,
        actor_id=user.id,
        actor_role=user.role.value,
    )
    return result


@router.get("/vendor/appointments")
def vendor_appointments(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    return get_vendor_portal().appointments(_vendor(user))


class AppointmentUpdate(BaseModel):
    status: str | None = None
    scheduled_at: str | None = None
    notes: str | None = Field(default=None, max_length=2000)


@router.patch("/vendor/appointments/{appointment_id}")
def update_appointment(
    appointment_id: str, payload: AppointmentUpdate, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    status = None
    if payload.status:
        try:
            status = AppointmentStatus(payload.status)
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"status must be one of {[s.value for s in AppointmentStatus]}",
            ) from exc

    try:
        return get_vendor_portal().update_appointment(
            _vendor(user), appointment_id, status, payload.scheduled_at, payload.notes
        )
    except VendorAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/vendor/installations")
def vendor_installations(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    return get_vendor_portal().installations(_vendor(user))


class InstallationUpdate(BaseModel):
    status: str
    installed_capacity_kw: float | None = Field(default=None, ge=0, le=5000)


@router.post("/vendor/installations/{installation_id}/status")
def update_installation(
    installation_id: str,
    payload: InstallationUpdate,
    user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Advance an installation.

    VERIFIED is refused with 403: DISCOM verification is not the installer's to
    assert about their own work.
    """
    try:
        status = InstallationStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of {[s.value for s in InstallationStatus]}",
        ) from exc

    portal = get_vendor_portal()
    try:
        updated = portal.update_installation_status(
            _vendor(user), installation_id, status, payload.installed_capacity_kw
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except VendorAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    db.audit(
        action=f"vendor.installation.{status.value.lower()}",
        entity_type="installations",
        entity_id=installation_id,
        actor_id=user.id,
        actor_role=user.role.value,
        after_state={"status": status.value},
    )
    return updated


@router.get("/vendor/projects")
def vendor_projects(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    return get_vendor_portal().projects(_vendor(user))


@router.get("/vendor/profile")
def vendor_profile(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    vendor = _vendor(user)
    portal = get_vendor_portal()
    return {
        "vendor": vendor,
        "documents": portal.documents(vendor),
        "document_types": portal.document_types(),
        "visible_to_customers": vendor["status"] == "APPROVED" and vendor["is_active"],
    }


class VendorProfileUpdate(BaseModel):
    representative_name: str | None = None
    phone: str | None = Field(default=None, max_length=20)
    address_line: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = Field(default=None, max_length=10)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    service_areas: list[str] | None = Field(default=None, max_length=50)
    installation_capacity_kw: float | None = Field(default=None, ge=0)
    years_experience: int | None = Field(default=None, ge=0, le=100)


@router.patch("/vendor/profile")
def update_profile(
    payload: VendorProfileUpdate, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Edit the business profile.

    Written with the vendor's own token, so the column grants from migration
    0004 apply: status, is_active, rating, verified_by and verified_at are not
    reachable from here at all.
    """
    vendor = _vendor(user)
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=422, detail="Nothing to update")

    try:
        res = (
            db.as_user(user.access_token)
            .table("vendors")
            .update(update)
            .eq("id", vendor["id"])
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=403, detail=f"Update refused: {exc}") from exc
    return res.data[0] if res.data else {}


class DocumentPayload(BaseModel):
    document_type: str = Field(min_length=1, max_length=100)
    file_path: str = Field(min_length=1, max_length=500)
    file_name: str | None = Field(default=None, max_length=255)
    mime_type: str | None = Field(default=None, max_length=100)
    file_size_bytes: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


@router.post("/vendor/documents", status_code=201)
def add_document(
    payload: DocumentPayload, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Attach a document. It is always unverified — only a DISCOM marks one verified."""
    portal = get_vendor_portal()
    vendor = _vendor(user)

    allowed = {d["code"] for d in portal.document_types()} if portal.document_types() else set()
    if allowed and payload.document_type not in allowed:
        raise HTTPException(
            status_code=422,
            detail=f"document_type must be one of {sorted(allowed)}",
        )

    return portal.add_document(vendor, payload.model_dump())


@router.post("/vendor/documents/upload", status_code=201)
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    notes: str | None = Form(default=None),
    user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Upload a document file.

    The file is validated by its content before it is stored anywhere: size
    bounds, an allow-list of types, and a magic-byte check that the bytes match
    what the request claimed. The object key is generated server-side, so a
    crafted filename cannot escape the vendor's own folder.
    """
    portal = get_vendor_portal()
    vendor = _vendor(user)

    allowed = {d["code"] for d in portal.document_types()}
    if allowed and document_type not in allowed:
        raise HTTPException(status_code=422, detail=f"document_type must be one of {sorted(allowed)}")

    # Read with a hard ceiling so an oversized upload cannot exhaust memory
    # before the size check runs.
    content = await file.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_FILE_BYTES // 1_048_576} MB limit.",
        )

    storage = get_storage_service()
    try:
        stored = storage.upload_vendor_document(
            vendor["id"], content, file.content_type or "", file.filename or "document"
        )
    except UploadRejected as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail="Storage is unavailable.") from exc

    record = portal.add_document(
        vendor,
        {
            "document_type": document_type,
            "file_path": stored.path,
            "file_name": stored.file_name,
            "mime_type": stored.mime_type,
            "file_size_bytes": stored.size_bytes,
            "notes": notes,
        },
    )

    db.audit(
        action="vendor.document.upload",
        entity_type="vendor_documents",
        entity_id=record.get("id"),
        actor_id=user.id,
        actor_role=user.role.value,
        after_state={"document_type": document_type, "size_bytes": stored.size_bytes},
    )
    return {"document": record, "storage": stored.as_dict()}


@router.get("/vendor/documents/{document_id}/url")
def document_url(document_id: str, user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """A short-lived link to one of this vendor's own documents."""
    vendor = _vendor(user)
    rows = (
        db.as_service().table("vendor_documents").select("*").eq("id", document_id).execute()
    ).data
    if not rows:
        raise HTTPException(status_code=404, detail="Document not found")
    if rows[0]["vendor_id"] != vendor["id"]:
        raise HTTPException(status_code=403, detail="This document belongs to another vendor")

    url = get_storage_service().signed_url(rows[0]["file_path"])
    return {"url": url, "expires_in_seconds": 300}


@router.get("/storage/policy")
def storage_policy(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """What the upload rules actually are."""
    return get_storage_service().describe()


# ============================================================
#  DISCOM verification — the only path to VERIFIED
# ============================================================
class VerificationPayload(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


@router.get("/discom/installations")
def discom_installations(user: CurrentUser = Depends(require_discom)) -> list[dict[str, Any]]:
    rows = (
        db.as_service()
        .table("installations")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    ).data or []
    return get_vendor_portal()._attach_applications(rows)  # noqa: SLF001


@router.post("/discom/installations/{installation_id}/verify")
def verify_installation(
    installation_id: str,
    payload: VerificationPayload,
    user: CurrentUser = Depends(require_discom),
) -> dict[str, Any]:
    """Confirm an installation has been inspected and is verified.

    This is the sole route that can set VERIFIED, and it requires a DISCOM or
    ADMIN role.
    """
    existing = (
        db.as_service().table("installations").select("*").eq("id", installation_id).execute()
    ).data
    if not existing:
        raise HTTPException(status_code=404, detail="Installation not found")

    updated = get_vendor_portal().verify_installation(installation_id, user.id, payload.notes)

    db.audit(
        action="installation.discom_verified",
        entity_type="installations",
        entity_id=installation_id,
        actor_id=user.id,
        actor_role=user.role.value,
        before_state={"status": existing[0]["status"]},
        after_state={"status": "VERIFIED", "notes": payload.notes},
    )
    return {"installation": updated, "verified_by": user.id}
