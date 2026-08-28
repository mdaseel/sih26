"""Database access layer.

Split by privilege on purpose:

  * Reads that belong to a user go through that user's own token, so Row Level
    Security decides what they can see.
  * Writes to engineering tables (simulation_results, risk_assessments,
    grid_assets, audit_logs) go through the service role, because those tables
    intentionally have no client write policy at all.

Nothing here decides authorization on its own — the database does. This class
only makes the correct client easy to reach.
"""

from __future__ import annotations

from typing import Any

from supabase import Client

from app.core.supabase_client import get_service_client, get_user_client
from app.models.enums import UserRole


class DatabaseService:
    """Thin, explicit wrapper over the Supabase tables."""

    # ---------------- client selection ----------------

    @staticmethod
    def as_user(access_token: str) -> Client:
        return get_user_client(access_token)

    @staticmethod
    def as_service() -> Client:
        return get_service_client()

    # ---------------- profiles ----------------

    def get_profile(self, user_id: str) -> dict[str, Any] | None:
        res = (
            self.as_service()
            .table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_role(self, user_id: str) -> UserRole | None:
        profile = self.get_profile(user_id)
        return UserRole(profile["role"]) if profile else None

    def set_role(self, user_id: str, role: UserRole) -> dict[str, Any]:
        """Privileged. Role changes are an administrative action, never a
        self-service one — clients have UPDATE on profiles.role revoked."""
        res = (
            self.as_service()
            .table("profiles")
            .update({"role": role.value})
            .eq("id", user_id)
            .execute()
        )
        return res.data[0] if res.data else {}

    # ---------------- grid assets ----------------

    def list_pv_eligible_buses(self) -> list[dict[str, Any]]:
        res = (
            self.as_service()
            .table("grid_assets")
            .select("*")
            .eq("asset_type", "BUS")
            .eq("pv_eligible", True)
            .order("asset_code")
            .execute()
        )
        return res.data or []

    def get_bus(self, asset_code: str) -> dict[str, Any] | None:
        res = (
            self.as_service()
            .table("grid_assets")
            .select("*")
            .eq("asset_type", "BUS")
            .eq("asset_code", asset_code)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def upsert_grid_assets(self, rows: list[dict[str, Any]]) -> int:
        """Privileged: grid_assets has no client write policy."""
        if not rows:
            return 0
        written = 0
        for i in range(0, len(rows), 200):  # chunked to stay under payload limits
            chunk = rows[i : i + 200]
            res = (
                self.as_service()
                .table("grid_assets")
                .upsert(chunk, on_conflict="feeder_id,asset_type,asset_code")
                .execute()
            )
            written += len(res.data or [])
        return written

    # ---------------- applications ----------------

    def create_application(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Created as the user, so RLS enforces applicant_id = auth.uid()."""
        res = self.as_user(access_token).table("solar_applications").insert(payload).execute()
        return res.data[0] if res.data else {}

    def get_application(self, access_token: str, application_id: str) -> dict[str, Any] | None:
        """Returns None for a missing OR malformed id.

        Postgres raises on a non-UUID value, which would surface as a 500 for
        what is really just a bad path parameter. Callers turn None into a 404.
        """
        try:
            res = (
                self.as_user(access_token)
                .table("solar_applications")
                .select("*")
                .eq("id", application_id)
                .limit(1)
                .execute()
            )
        except Exception:  # noqa: BLE001 - malformed id is a client error, not a fault
            return None
        return res.data[0] if res.data else None

    def list_applications_for_user(self, access_token: str) -> list[dict[str, Any]]:
        res = (
            self.as_user(access_token)
            .table("solar_applications")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []

    def set_application_status(self, application_id: str, status: str) -> dict[str, Any]:
        """Privileged: assessment-driven transitions are made by the backend,
        not by the client, so the citizen cannot self-advance an application."""
        res = (
            self.as_service()
            .table("solar_applications")
            .update({"status": status})
            .eq("id", application_id)
            .execute()
        )
        return res.data[0] if res.data else {}

    # ---------------- engineering results (service role only) ----------------

    def insert_simulation_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        res = self.as_service().table("simulation_results").insert(payload).execute()
        return res.data[0] if res.data else {}

    def insert_risk_assessment(self, payload: dict[str, Any]) -> dict[str, Any]:
        res = self.as_service().table("risk_assessments").insert(payload).execute()
        return res.data[0] if res.data else {}

    def get_latest_assessment(self, application_id: str) -> dict[str, Any] | None:
        res = (
            self.as_service()
            .table("risk_assessments")
            .select("*")
            .eq("application_id", application_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_simulation(self, simulation_id: str) -> dict[str, Any] | None:
        res = (
            self.as_service()
            .table("simulation_results")
            .select("*")
            .eq("id", simulation_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_latest_simulation(self, application_id: str) -> dict[str, Any] | None:
        res = (
            self.as_service()
            .table("simulation_results")
            .select("*")
            .eq("application_id", application_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    # ---------------- scheme config ----------------

    def get_scheme_config(self, scheme_code: str = "PM_SURYA_GHAR") -> list[dict[str, Any]]:
        res = (
            self.as_service()
            .table("scheme_config")
            .select("*")
            .eq("scheme_code", scheme_code)
            .eq("is_active", True)
            .execute()
        )
        return res.data or []

    def upsert_scheme_config(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        res = (
            self.as_service()
            .table("scheme_config")
            .upsert(rows, on_conflict="scheme_code,config_key,effective_from")
            .execute()
        )
        return len(res.data or [])

    # ---------------- audit ----------------

    def audit(
        self,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        actor_id: str | None = None,
        actor_role: str | None = None,
        actor_email: str | None = None,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
    ) -> None:
        """Append-only. Failures must never break the caller's request."""
        try:
            self.as_service().table("audit_logs").insert(
                {
                    "action": action,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "actor_id": actor_id,
                    # Durable copy: actor_id is nulled if the profile is ever
                    # deleted, which would erase attribution from the audit
                    # trail. See migration 0006.
                    "actor_ref": str(actor_id) if actor_id else None,
                    "actor_email": actor_email,
                    "actor_role": actor_role,
                    "before_state": before_state,
                    "after_state": after_state,
                }
            ).execute()
        except Exception:  # noqa: BLE001 - audit must not be load-bearing
            pass


db = DatabaseService()
