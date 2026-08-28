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

        apps = (
            db.as_service()
            .table("solar_applications")
            .select(CUSTOMER_FIELDS_FOR_VENDOR)
            .in_("id", app_ids)
            .execute()
        ).data or []
        by_id = {a["id"]: a for a in apps}
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

        # Accepting a lead opens the installation record the work is tracked on.
        installation = None
        if accept:
            installation = self._ensure_installation(vendor, appointment["application_id"])

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

        self._own(vendor, "installations", installation_id)

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
        return res.data[0] if res.data else {}

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
        return res.data[0] if res.data else {}

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

    def summary(self, vendor: dict[str, Any]) -> dict[str, Any]:
        leads = self.leads(vendor)
        installs = self.installations(vendor)

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
            "verification_note": (
                "Only a DISCOM reviewer can move an installation to VERIFIED. "
                "Submit completed work as VERIFICATION_PENDING."
            ),
        }


@lru_cache
def get_vendor_portal() -> VendorPortalService:
    return VendorPortalService()
