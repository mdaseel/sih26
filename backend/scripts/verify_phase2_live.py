"""Phase 2 live test — persistence and the security model, against real Supabase.

Creates two temporary users (emails prefixed solargrid-verify-), drives a full
application through the API, then attempts the attacks the RLS policies exist to
stop. Every test user and row is deleted at the end.

The attacks matter more than the happy path. If a citizen can write to
risk_assessments, the entire "backend is the source of truth" guarantee is
decorative.

Usage:
    python backend/scripts/verify_phase2_live.py
"""

from __future__ import annotations

import sys
import uuid
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from app.core.config import get_settings  # noqa: E402
from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def denied(exc: Exception) -> bool:
    """True when the error is an authorization refusal rather than a bug."""
    text = str(exc).lower()
    return any(
        marker in text
        for marker in ("row-level security", "permission denied", "violates", "42501", "pgrst")
    )


settings = get_settings()
if not settings.service_role_configured:
    print("Supabase not configured — cannot run the live test.")
    raise SystemExit(1)

svc = get_service_client()
tag = uuid.uuid4().hex[:8]
users: list[str] = []
app_id: str | None = None

try:
    # ============================================================
    print("\nA. Test fixtures")
    # ============================================================
    def make_user(label: str) -> tuple[str, str, str]:
        email = f"solargrid-verify-{label}-{tag}@example.com"
        password = f"Verify!{uuid.uuid4().hex[:12]}"
        created = svc.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        uid = created.user.id
        users.append(uid)
        return uid, email, password

    citizen_id, citizen_email, citizen_pw = make_user("citizen")
    other_id, other_email, other_pw = make_user("other")
    check("two test users created", len(users) == 2)

    # The on_auth_user_created trigger should have made profiles automatically.
    prof = svc.table("profiles").select("*").eq("id", citizen_id).execute()
    check(
        "profile auto-created by trigger with CITIZEN role",
        bool(prof.data) and prof.data[0]["role"] == "CITIZEN",
        prof.data[0]["role"] if prof.data else "no profile",
    )

    def sign_in(email: str, password: str) -> str:
        session = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return session.session.access_token

    citizen_token = sign_in(citizen_email, citizen_pw)
    other_token = sign_in(other_email, other_pw)
    check("citizen can sign in and receive a JWT", bool(citizen_token))

    # ============================================================
    print("\nB. Application lifecycle through the API")
    # ============================================================
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    auth = {"Authorization": f"Bearer {citizen_token}"}

    r = client.post(
        "/api/applications",
        headers=auth,
        json={
            "applicant_name": "Verify Citizen",
            "pv_bus": "734",
            "existing_pv_kw": 0,
            "new_pv_kw": 66,
            "address_line": "Test address",
            "monthly_consumption_kwh": 320,
        },
    )
    check("POST /api/applications", r.status_code == 201, f"status {r.status_code}")
    if r.status_code == 201:
        app_id = r.json()["id"]
        check("application_number generated", bool(r.json().get("application_number")))
        check(
            "total_pv_kw computed by the database",
            float(r.json()["total_pv_kw"]) == 66.0,
            str(r.json()["total_pv_kw"]),
        )

    # Status history should already have a row from the insert trigger.
    hist = (
        svc.table("application_status_history")
        .select("*")
        .eq("application_id", app_id)
        .execute()
    )
    check("status history written by trigger", len(hist.data) >= 1, f"{len(hist.data)} row(s)")

    r = client.post(f"/api/applications/{app_id}/assess", headers=auth)
    check("POST /api/applications/{id}/assess", r.status_code == 200, f"status {r.status_code}")
    body = r.json() if r.status_code == 200 else {}
    if body:
        check(
            "engineering verdict CONSTRAINED for bus 734 @66kW",
            body["engineering"]["engineering_risk"] == "CONSTRAINED",
            body["engineering"]["constraint_reason"],
        )
        check("result persisted", body["persisted"] is True)
        check("simulation_id returned", bool(body["simulation_id"]))
        check("assessment_id returned", bool(body["assessment_id"]))

        sim = svc.table("simulation_results").select("*").eq("id", body["simulation_id"]).execute()
        check(
            "simulation_results row stored with real metrics",
            bool(sim.data) and abs(float(sim.data[0]["voltage_rise_pu"]) - 0.05751) < 1e-4,
            f"voltage_rise_pu={sim.data[0]['voltage_rise_pu']}" if sim.data else "missing",
        )

        ra = svc.table("risk_assessments").select("*").eq("id", body["assessment_id"]).execute()
        check(
            "risk_assessments row stored",
            bool(ra.data) and ra.data[0]["engineering_risk"] == "CONSTRAINED",
        )
        check(
            "ml_agrees_with_engineering computed by the database",
            bool(ra.data) and ra.data[0]["ml_agrees_with_engineering"] is True,
        )
        check(
            "thresholds snapshot stored with the verdict",
            bool(ra.data) and ra.data[0]["thresholds_snapshot"].get("voltage_rise_hard_pu") == 0.05,
        )

    r = client.get(f"/api/applications/{app_id}", headers=auth)
    check(
        "GET /api/applications/{id} returns the assessment",
        r.status_code == 200 and r.json()["latest_assessment"] is not None,
    )

    r = client.get(f"/api/simulations/{body['simulation_id']}", headers=auth)
    check("GET /api/simulations/{id}", r.status_code == 200)

    # ============================================================
    print("\nC. Attacks that must fail")
    # ============================================================
    cit = get_anon_client()
    cit.postgrest.auth(citizen_token)

    # 1. Rewrite the engineering verdict.
    try:
        res = (
            cit.table("risk_assessments")
            .update({"engineering_risk": "SAFE"})
            .eq("application_id", app_id)
            .execute()
        )
        check("citizen CANNOT rewrite risk_assessments", not res.data, f"{len(res.data)} row(s) updated")
    except Exception as exc:  # noqa: BLE001
        check("citizen CANNOT rewrite risk_assessments", denied(exc), type(exc).__name__)

    # 2. Fabricate a simulation result.
    try:
        res = (
            cit.table("simulation_results")
            .insert(
                {
                    "application_id": app_id,
                    "pv_bus": "734",
                    "existing_pv_kw": 0,
                    "new_pv_kw": 66,
                    "total_pv_kw": 66,
                    "voltage_rise_pu": 0.001,
                }
            )
            .execute()
        )
        check("citizen CANNOT insert simulation_results", not res.data, "insert succeeded")
    except Exception as exc:  # noqa: BLE001
        check("citizen CANNOT insert simulation_results", denied(exc), type(exc).__name__)

    # 3. Self-approve the application.
    try:
        res = (
            cit.table("solar_applications")
            .update({"status": "APPROVED"})
            .eq("id", app_id)
            .execute()
        )
        check("citizen CANNOT self-approve", not res.data, f"{len(res.data)} row(s) updated")
    except Exception as exc:  # noqa: BLE001
        check("citizen CANNOT self-approve", denied(exc), type(exc).__name__)

    # 4. Promote self to DISCOM.
    try:
        res = cit.table("profiles").update({"role": "DISCOM"}).eq("id", citizen_id).execute()
        after = svc.table("profiles").select("role").eq("id", citizen_id).execute()
        check(
            "citizen CANNOT promote self to DISCOM",
            after.data[0]["role"] == "CITIZEN",
            f"role is {after.data[0]['role']}",
        )
    except Exception as exc:  # noqa: BLE001
        check("citizen CANNOT promote self to DISCOM", denied(exc), type(exc).__name__)

    # 5. Read someone else's application.
    oth = get_anon_client()
    oth.postgrest.auth(other_token)
    res = oth.table("solar_applications").select("*").eq("id", app_id).execute()
    check("other citizen CANNOT read the application", not res.data, f"{len(res.data)} row(s) visible")

    res = oth.table("risk_assessments").select("*").eq("application_id", app_id).execute()
    check("other citizen CANNOT read the assessment", not res.data, f"{len(res.data)} row(s) visible")

    # 6. Assess someone else's application through the API.
    r = client.post(
        f"/api/applications/{app_id}/assess",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    check("other citizen CANNOT assess it via the API", r.status_code in (403, 404), f"status {r.status_code}")

    # 7. Self-register as an APPROVED vendor.
    try:
        res = (
            cit.table("vendors")
            .insert({"owner_id": citizen_id, "business_name": "Fake Solar", "status": "APPROVED"})
            .execute()
        )
        check("vendor CANNOT self-register as APPROVED", not res.data, "insert succeeded")
    except Exception as exc:  # noqa: BLE001
        check("vendor CANNOT self-register as APPROVED", denied(exc), type(exc).__name__)

    # 8. Read the migration ledger with a user token.
    try:
        res = cit.table("applied_migrations").select("*").execute()
        check("migration ledger not client-readable", not res.data, f"{len(res.data)} row(s) visible")
    except Exception as exc:  # noqa: BLE001
        check("migration ledger not client-readable", denied(exc), type(exc).__name__)

    # ============================================================
    print("\nD. Reference data readable by a signed-in user")
    # ============================================================
    res = cit.table("grid_assets").select("*").eq("pv_eligible", True).execute()
    check("citizen can read the 71 eligible buses", len(res.data) == 71, f"{len(res.data)} rows")

finally:
    # ============================================================
    print("\nE. Cleanup")
    # ============================================================
    if app_id:
        try:
            svc.table("solar_applications").delete().eq("id", app_id).execute()
        except Exception:  # noqa: BLE001
            pass
    for uid in users:
        try:
            svc.auth.admin.delete_user(uid)
        except Exception:  # noqa: BLE001
            pass
    leftover = (
        svc.table("solar_applications").select("id").eq("id", app_id).execute().data
        if app_id
        else []
    )
    check("test data removed", not leftover)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 2 LIVE VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
