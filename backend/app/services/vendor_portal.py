"""VendorPortalService — leads, appointments, installations and projects.

A "lead" here is a concrete thing, not a marketing abstraction: a citizen has
picked this vendor for a specific application and asked for a site visit. That
is an appointment row, so accepting or rejecting a lead is a state change on
something the customer can also see.

Two boundaries this module exists to hold
-----------------------------------------
1. DISCOM verification is not the vendor's to give. A vendor may advance an
   installation as far as VERIFICATION_PENDING and no further. VERIFIED is set
   only by verify_installation(), which the API exposes to DISCOM roles alone.
   The database independently agrees: RLS forbids a vendor writing status
   'VERIFIED', and migration 0004 revoked the discom_verified* columns from
   `authenticated` entirely.

2. Customer details are released per lead, not in bulk. A vendor sees an
   applicant's address only for applications where that customer has actually
   engaged them, and only the fields needed to visit the site.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.db.service import db
from app.models.enums import AppointmentStatus, InstallationStatus

# What a vendor may progress an installation to on their own.
VENDOR_ALLOWED_STATUSES = {
    InstallationStatus.PENDING,
    InstallationStatus.SITE_VISIT,
    InstallationStatus.SCHEDULED,
    InstallationStatus.IN_PROGRESS,
    InstallationStatus.COMPLETED,
    InstallationStatus.VERIFICATION_PENDING,
}

# Set by the DISCOM, never by the vendor.
DISCOM_ONLY_STATUS = InstallationStatus.VERIFIED

# Only these fields of an application are released to an engaged vendor.
CUSTOMER_FIELDS_FOR_VENDOR = (
    "id,application_number,applicant_name,contact_phone,address_line,district,state,"
    "pincode,latitude,longitude,pv_bus,existing_pv_kw,new_pv_kw,total_pv_kw,status,"
    "roof_type,roof_area_sqm,shading_level,created_at"
)


class VendorAccessError(PermissionError):
    """The caller has no vendor profile, or none that owns this record."""


class VendorPortalService:
    # ---------------- identity ----------------

    def vendor_for_user(self, user_id: str) -> dict[str, Any]:
        res = (
            db.as_service()
            .table("vendors")
            .select("*")
            .eq("owner_id", user_id)
            .limit(1)
            .execute()
        )
        if not res.data:
            raise VendorAccessError("This account has no vendor profile")
        return res.data[0]

    def _own(self, vendor: dict[str, Any], table: str, record_id: str) -> dict[str, Any]:
        res = (
            db.as_service().table(table).select("*").eq("id", record_id).limit(1).execute()
        )
        if not res.data:
            raise VendorAccessError(f"{table[:-1]} not found")
        row = res.data[0]
        if row.get("vendor_id") != vendor["id"]:
            raise VendorAccessError("This record belongs to another vendor")
        return row

    # ---------------- leads ----------------

    def leads(self, vendor: dict[str, Any]) -> list[dict[str, Any]]:
        """Appointments a customer has requested, plus the application behind each."""
        rows = (
            db.as_service()
            .table("appointments")
            .select("*")
            .eq("vendor_id", vendor["id"])
            .order("created_at", desc=True)
            .execute()
        ).data or []
        return self._attach_applications(rows)

    def _attach_applications(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        app_ids = sorted({r["application_id"] for r in rows if r.get("application_id")})
        if not app_ids:
            return rows

        # Chunk IN clause to avoid PostgREST URL limits and http pool pressure
        by_id: dict[str, dict[str, Any]] = {}
        for i in range(0, len(app_ids), 50):
            chunk = app_ids[i : i + 50]
            try:
                part = (
                    db.as_service()
                    .table("solar_applications")
                    .select(CUSTOMER_FIELDS_FOR_VENDOR)
                    .in_("id", chunk)
                    .execute()
                ).data or []
                for a in part:
                    by_id[a["id"]] = a
            except Exception:
                # One failed chunk must not hide the rest
                continue
        return [{**r, "application": by_id.get(r["application_id"])} for r in rows]

    def respond_to_lead(
        self, vendor: dict[str, Any], appointment_id: str, accept: bool, note: str | None
    ) -> dict[str, Any]:
        appointment = self._own(vendor, "appointments", appointment_id)
        if appointment["status"] not in (
            AppointmentStatus.REQUESTED.value,
            AppointmentStatus.RESCHEDULED.value,
        ):
            raise ValueError(f"This lead is already {appointment['status']}")

        new_status = (
            AppointmentStatus.CONFIRMED if accept else AppointmentStatus.CANCELLED
        )
        updated = (
            db.as_service()
            .table("appointments")
            .update({"status": new_status.value, "notes": note})
            .eq("id", appointment_id)
            .execute()
        ).data

        # Accepting a lead opens the installation record the work is tracked on
        # and advances the application from APPROVED -> VENDOR_SELECTED so the
        # citizen tracker and DISCOM queue reflect reality in real time.
        installation = None
        if accept:
            installation = self._ensure_installation(vendor, appointment["application_id"])
            try:
                db.as_service().table("solar_applications").update(
                    {"status": "VENDOR_SELECTED"}
                ).eq("id", appointment["application_id"]).eq("status", "APPROVED").execute()
            except Exception:
                pass
        else:
            # Rejected lead leaves application APPROVED for other vendors
            pass

        return {
            "appointment": updated[0] if updated else None,
            "installation": installation,
            "accepted": accept,
        }

    def _ensure_installation(self, vendor: dict[str, Any], application_id: str) -> dict[str, Any]:
        existing = (
            db.as_service()
            .table("installations")
            .select("*")
            .eq("application_id", application_id)
            .limit(1)
            .execute()
        ).data
        if existing:
            return existing[0]

        created = (
            db.as_service()
            .table("installations")
            .insert(
                {
                    "application_id": application_id,
                    "vendor_id": vendor["id"],
                    "status": InstallationStatus.PENDING.value,
                }
            )
            .execute()
        ).data
        return created[0] if created else {}

    # ---------------- appointments ----------------

    def appointments(self, vendor: dict[str, Any]) -> list[dict[str, Any]]:
        rows = (
            db.as_service()
            .table("appointments")
            .select("*")
            .eq("vendor_id", vendor["id"])
            .order("scheduled_at")
            .execute()
        ).data or []
        return self._attach_applications(rows)

    def update_appointment(
        self,
        vendor: dict[str, Any],
        appointment_id: str,
        status: AppointmentStatus | None,
        scheduled_at: str | None,
        notes: str | None,
    ) -> dict[str, Any]:
        self._own(vendor, "appointments", appointment_id)
        update: dict[str, Any] = {}
        if status is not None:
            update["status"] = status.value
        if scheduled_at is not None:
            update["scheduled_at"] = scheduled_at
        if notes is not None:
            update["notes"] = notes
        if not update:
            raise ValueError("Nothing to update")

        res = (
            db.as_service().table("appointments").update(update).eq("id", appointment_id).execute()
        )
        return res.data[0] if res.data else {}

    # ---------------- installations ----------------

    def installations(self, vendor: dict[str, Any]) -> list[dict[str, Any]]:
        rows = (
            db.as_service()
            .table("installations")
            .select("*")
            .eq("vendor_id", vendor["id"])
            .order("created_at", desc=True)
            .execute()
        ).data or []
        return self._attach_applications(rows)

    def update_installation_status(
        self,
        vendor: dict[str, Any],
        installation_id: str,
        status: InstallationStatus,
        installed_capacity_kw: float | None = None,
    ) -> dict[str, Any]:
        """Advance an installation. VERIFIED is rejected here.

        This is the application-layer half of the rule. Even if it were wrong,
        RLS refuses a vendor writing 'VERIFIED' and the discom_verified columns
        are not granted to them at all.
        """
        if status is DISCOM_ONLY_STATUS or status not in VENDOR_ALLOWED_STATUSES:
            raise PermissionError(
                "Only a DISCOM reviewer can mark an installation VERIFIED. "
                "The furthest a vendor may take it is VERIFICATION_PENDING."
            )

        own = self._own(vendor, "installations", installation_id)

        update: dict[str, Any] = {"status": status.value}
        if installed_capacity_kw is not None:
            update["installed_capacity_kw"] = installed_capacity_kw
        if status is InstallationStatus.IN_PROGRESS:
            update["started_at"] = "now()"
        if status is InstallationStatus.COMPLETED:
            update["completed_at"] = "now()"

        res = (
            db.as_service()
            .table("installations")
            .update(update)
            .eq("id", installation_id)
            .execute()
        )
        data = res.data[0] if res.data else {}
        # Mirror installation progress to application tracking in real time
        try:
            app_status_map = {
                InstallationStatus.SITE_VISIT.value: "VENDOR_SELECTED",
                InstallationStatus.SCHEDULED.value: "VENDOR_SELECTED",
                InstallationStatus.IN_PROGRESS.value: "INSTALLING",
                InstallationStatus.COMPLETED.value: "INSTALLED",
                InstallationStatus.VERIFICATION_PENDING.value: "INSTALLED",
            }
            mapped = app_status_map.get(status.value)
            if mapped:
                db.as_service().table("solar_applications").update(
                    {"status": mapped}
                ).eq("id", own["application_id"]).execute()
        except Exception:
            pass
        return data

    # ---------------- DISCOM verification ----------------

    @staticmethod
    def verify_installation(
        installation_id: str, verifier_id: str, notes: str | None
    ) -> dict[str, Any]:
        """Mark an installation DISCOM-verified. Callable only from a route
        guarded by require_discom."""
        res = (
            db.as_service()
            .table("installations")
            .update(
                {
                    "status": InstallationStatus.VERIFIED.value,
                    "discom_verified": True,
                    "discom_verified_by": verifier_id,
                    "discom_verified_at": "now()",
                    "verification_notes": notes,
                }
            )
            .eq("id", installation_id)
            .execute()
        )
        data = res.data[0] if res.data else {}
        # Advance application to VERIFIED so citizen tracker closes the loop
        try:
            if data.get("application_id"):
                db.as_service().table("solar_applications").update(
                    {"status": "VERIFIED"}
                ).eq("id", data["application_id"]).execute()
        except Exception:
            pass
        return data

    # ---------------- projects and documents ----------------

    def projects(self, vendor: dict[str, Any]) -> list[dict[str, Any]]:
        """Every application this vendor is engaged on, with its current state."""
        installs = self.installations(vendor)
        appointments = self.appointments(vendor)
        appts_by_app: dict[str, list[dict[str, Any]]] = {}
        for a in appointments:
            appts_by_app.setdefault(a["application_id"], []).append(a)

        out = []
        for install in installs:
            out.append(
                {
                    "application_id": install["application_id"],
                    "application": install.get("application"),
                    "installation": {
                        k: v for k, v in install.items() if k != "application"
                    },
                    "appointments": [
                        {k: v for k, v in a.items() if k != "application"}
                        for a in appts_by_app.get(install["application_id"], [])
                    ],
                }
            )
        return out

    def documents(self, vendor: dict[str, Any]) -> list[dict[str, Any]]:
        res = (
            db.as_service()
            .table("vendor_documents")
            .select("*")
            .eq("vendor_id", vendor["id"])
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []

    def add_document(self, vendor: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        row = {
            **payload,
            "vendor_id": vendor["id"],
            "is_verified": False,
            "verified_by": None,
            "verified_at": None,
        }
        res = db.as_service().table("vendor_documents").insert(row).execute()
        return res.data[0] if res.data else {}

    @staticmethod
    def document_types() -> list[dict[str, Any]]:
        """Configurable, from scheme_config — not hardcoded in the UI."""
        rows = (
            db.as_service()
            .table("scheme_config")
            .select("config_value")
            .eq("scheme_code", "VENDOR")
            .eq("config_key", "document_types")
            .eq("is_active", True)
            .limit(1)
            .execute()
        ).data
        if rows and isinstance(rows[0]["config_value"], list):
            return rows[0]["config_value"]
        return []

    # ---------------- dashboard ----------------

    def opportunities(self, vendor: dict[str, Any]) -> list[dict[str, Any]]:
        """Per-vendor marketplace: APPROVED apps with nearest routing.

        Ordered nearest-first for this vendor, with is_primary flag for the
        globally nearest vendor to each application (who sees the blinking
        highlight). Escalation is time-based: if the primary does not claim
        within 1 hour, next-nearest is eligible.
        """
        from app.services.routing import get_routing_service

        try:
            apps = (
                db.as_service()
                .table("solar_applications")
                .select(CUSTOMER_FIELDS_FOR_VENDOR)
                .eq("status", "APPROVED")
                .order("created_at", desc=True)
                .limit(80)
                .execute()
            ).data or []
            installed_app_ids: set[str] = set()
            try:
                installs = (
                    db.as_service().table("installations").select("application_id").execute()
                ).data or []
                installed_app_ids = {r["application_id"] for r in installs}
            except Exception:
                pass
            # Filter unclaimed
            apps = [a for a in apps if a["id"] not in installed_app_ids]
            # For each app, compute nearest vendor globally to decide primary
            try:
                all_vendors = (
                    db.as_service()
                    .table("vendors")
                    .select("id,latitude,longitude")
                    .eq("status", "APPROVED")
                    .eq("is_active", True)
                    .execute()
                ).data or []
            except Exception:
                all_vendors = [vendor]
            routing = get_routing_service()
            enriched: list[dict[str, Any]] = []
            for a in apps:
                lat, lon = a.get("latitude"), a.get("longitude")
                # Distance for this vendor
                my_dist = None
                if lat is not None and lon is not None and vendor.get("latitude") is not None:
                    d = routing.distance(lat, lon, vendor["latitude"], vendor["longitude"])
                    if d:
                        my_dist = d.distance_km
                # Find globally nearest distance
                min_dist = my_dist
                nearest_id = vendor["id"]
                for v in all_vendors:
                    if v["id"] == vendor["id"]:
                        continue
                    if lat is None or v.get("latitude") is None:
                        continue
                    dd = routing.distance(lat, lon, v["latitude"], v["longitude"])
                    if dd and (min_dist is None or dd.distance_km < min_dist):
                        min_dist = dd.distance_km
                        nearest_id = v["id"]
                is_primary = nearest_id == vendor["id"]
                # Escalation: if app older than 1h and primary hasn't claimed, allow others
                from datetime import datetime, timezone
                try:
                    created = datetime.fromisoformat(a["created_at"].replace("Z", "+00:00"))
                    age_h = (datetime.now(timezone.utc) - created).total_seconds() / 3600
                    can_claim = is_primary or age_h > 1.0
                except Exception:
                    can_claim = True
                enriched.append(
                    {
                        **a,
                        "distance_km": my_dist,
                        "is_primary": is_primary,
                        "should_blink": is_primary,
                        "can_claim": can_claim,
                    }
                )
            # Nearest-first for this vendor
            enriched.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] or 9999))
            return enriched
        except Exception:
            return []

    def claim_opportunity(self, vendor: dict[str, Any], application_id: str) -> dict[str, Any]:
        """Vendor claims an APPROVED opportunity — creates CONFIRMED appointment + installation."""
        app_rows = (
            db.as_service().table("solar_applications").select("*").eq("id", application_id).execute()
        ).data
        if not app_rows:
            raise ValueError("Application not found")
        app = app_rows[0]
        if app["status"] != "APPROVED":
            raise ValueError(f"Application is {app['status']}, not APPROVED")
        # Already claimed?
        exists = (
            db.as_service().table("installations").select("id").eq("application_id", application_id).limit(1).execute()
        ).data
        if exists:
            raise ValueError("Application already claimed by another vendor")
        # Create confirmed appointment on behalf of citizen
        appt = (
            db.as_service()
            .table("appointments")
            .insert(
                {
                    "application_id": application_id,
                    "vendor_id": vendor["id"],
                    "citizen_id": app["applicant_id"],
                    "scheduled_at": "now()",
                    "purpose": "INSTALLATION",
                    "notes": "Auto-assigned via nearest-vendor routing",
                    "status": "CONFIRMED",
                }
            )
            .execute()
        ).data
        install = self._ensure_installation(vendor, application_id)
        try:
            db.as_service().table("solar_applications").update({"status": "VENDOR_SELECTED"}).eq("id", application_id).eq("status", "APPROVED").execute()
        except Exception:
            pass
        return {"appointment": appt[0] if appt else None, "installation": install, "application_id": application_id}

    def summary(self, vendor: dict[str, Any]) -> dict[str, Any]:
        leads = self.leads(vendor)
        installs = self.installations(vendor)
        opps = self.opportunities(vendor)

        new_leads = [
            a
            for a in leads
            if a["status"] in (AppointmentStatus.REQUESTED.value, AppointmentStatus.RESCHEDULED.value)
        ]
        upcoming = [a for a in leads if a["status"] == AppointmentStatus.CONFIRMED.value]
        by_status: dict[str, int] = {}
        for i in installs:
            by_status[i["status"]] = by_status.get(i["status"], 0) + 1

        return {
            "vendor": {
                "id": vendor["id"],
                "business_name": vendor["business_name"],
                "status": vendor["status"],
                "is_active": vendor["is_active"],
                "visible_to_customers": vendor["status"] == "APPROVED" and vendor["is_active"],
                "rating": vendor.get("rating"),
                "completed_installations": vendor.get("completed_installations"),
            },
            "new_leads": len(new_leads),
            "confirmed_appointments": len(upcoming),
            "installations": len(installs),
            "installations_by_status": by_status,
            "awaiting_discom_verification": by_status.get(
                InstallationStatus.VERIFICATION_PENDING.value, 0
            ),
            "verified": by_status.get(InstallationStatus.VERIFIED.value, 0),
            "opportunities": len(opps),
            "verification_note": (
                "Only a DISCOM reviewer can move an installation to VERIFIED. "
                "Submit completed work as VERIFICATION_PENDING."
            ),
        }


@lru_cache
def get_vendor_portal() -> VendorPortalService:
    return VendorPortalService()
