"""Phase 6 acceptance check — DISCOM dashboard and approval authority.

The requirement that matters: "A citizen must not be able to approve an
application by modifying frontend data." That is tested here from both angles —
through the API, and by writing directly to the database with a citizen's own
token, which is what an attacker would actually do.

Everything runs against real Supabase with temporary users, cleaned up at the end.
"""

from __future__ import annotations

import sys
import uuid
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402

BASE = "http://127.0.0.1:8000"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def denied(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(m in text for m in ("row-level security", "permission denied", "violates", "42501", "pgrst"))


settings = get_settings()
if not settings.service_role_configured:
    print("Supabase not configured.")
    raise SystemExit(1)

try:
    httpx.get(f"{BASE}/health", timeout=10)
except Exception:
    print(f"Backend is not running at {BASE}. Start it first.")
    raise SystemExit(1)

svc = get_service_client()
users: list[str] = []
app_id: str | None = None

try:
    # ============================================================
    print("\nA. Fixtures")
    # ============================================================
    def make(label: str, role: str) -> tuple[str, dict[str, str]]:
        email = f"solargrid-p6-{label}-{uuid.uuid4().hex[:6]}@example.com"
        pw = f"Verify!{uuid.uuid4().hex[:12]}"
        created = svc.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True})
        users.append(created.user.id)
        if role != "CITIZEN":
            svc.table("profiles").update({"role": role}).eq("id", created.user.id).execute()
        token = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": pw}
        ).session.access_token
        return created.user.id, {"Authorization": f"Bearer {token}"}

    citizen_id, CITIZEN = make("citizen", "CITIZEN")
    discom_id, DISCOM = make("discom", "DISCOM")
    check("citizen and DISCOM users created", len(users) == 2)

    r = httpx.get(f"{BASE}/api/me", headers=DISCOM, timeout=60)
    check("DISCOM role resolves server-side", r.json()["role"] == "DISCOM" and r.json()["is_discom"])
    r = httpx.get(f"{BASE}/api/me", headers=CITIZEN, timeout=60)
    check("citizen role resolves server-side", r.json()["role"] == "CITIZEN" and not r.json()["is_discom"])

    # An application to review.
    r = httpx.post(
        f"{BASE}/api/applications",
        headers=CITIZEN,
        json={
            "applicant_name": "Phase 6 Applicant",
            "pv_bus": "734",
            "existing_pv_kw": 0,
            "new_pv_kw": 66,
        },
        timeout=60,
    )
    app_id = r.json()["id"]
    check("application created", r.status_code == 201, r.json().get("application_number", ""))
    r = httpx.post(f"{BASE}/api/applications/{app_id}/assess", headers=CITIZEN, timeout=180)
    check(
        "assessed as CONSTRAINED",
        r.status_code == 200 and r.json()["engineering"]["engineering_risk"] == "CONSTRAINED",
    )

    # ============================================================
    print("\nB. A citizen cannot reach DISCOM functions")
    # ============================================================
    for path in ["/api/discom/summary", "/api/discom/applications", "/api/discom/transformers", "/api/discom/feeders"]:
        r = httpx.get(f"{BASE}{path}", headers=CITIZEN, timeout=60)
        check(f"citizen GET {path} refused", r.status_code == 403, f"status {r.status_code}")

    r = httpx.get(f"{BASE}/api/discom/applications/{app_id}", headers=CITIZEN, timeout=60)
    check("citizen cannot open the review packet", r.status_code == 403)

    r = httpx.post(
        f"{BASE}/api/discom/applications/{app_id}/decision",
        headers=CITIZEN,
        json={"decision": "APPROVED"},
        timeout=60,
    )
    check("citizen cannot approve via the API", r.status_code == 403, f"status {r.status_code}")

    r = httpx.post(
        f"{BASE}/api/discom/applications/{app_id}/decision",
        json={"decision": "APPROVED"},
        timeout=60,
    )
    check("unauthenticated cannot approve", r.status_code == 401)

    # The real attack: skip the API and write to the database directly.
    cit = get_anon_client()
    cit.postgrest.auth(CITIZEN["Authorization"].split(" ", 1)[1])
    try:
        res = cit.table("solar_applications").update({"status": "APPROVED"}).eq("id", app_id).execute()
        check("citizen cannot approve by writing to the database", not res.data, f"{len(res.data)} rows updated")
    except Exception as exc:  # noqa: BLE001
        check("citizen cannot approve by writing to the database", denied(exc), type(exc).__name__)

    after = (svc.table("solar_applications").select("status").eq("id", app_id).execute()).data[0]
    check(
        "the application is still not approved",
        after["status"] != "APPROVED",
        f"status is {after['status']}",
    )

    # Nor by promoting themselves first.
    try:
        cit.table("profiles").update({"role": "DISCOM"}).eq("id", citizen_id).execute()
    except Exception:  # noqa: BLE001
        pass
    role_now = (svc.table("profiles").select("role").eq("id", citizen_id).execute()).data[0]["role"]
    check("citizen cannot self-promote to DISCOM", role_now == "CITIZEN", f"role is {role_now}")

    # ============================================================
    print("\nC. The DISCOM console works")
    # ============================================================
    r = httpx.get(f"{BASE}/api/discom/summary", headers=DISCOM, timeout=60)
    s = r.json()
    check(
        "dashboard metrics",
        r.status_code == 200 and s["total_applications"] >= 1 and s["pending_review"] >= 1,
        f"{s['total_applications']} applications, {s['pending_review']} pending",
    )
    check(
        "risk breakdown counts the constrained application",
        s["by_risk"]["CONSTRAINED"] >= 1,
        str(s["by_risk"]),
    )
    check(
        "capacity figures are labelled for what they measure",
        "not a measurement of generation installed" in s["capacity_note"],
    )

    r = httpx.get(f"{BASE}/api/discom/applications", headers=DISCOM, timeout=60)
    apps = r.json()
    check("DISCOM sees every application", any(a["id"] == app_id for a in apps), f"{len(apps)} rows")

    r = httpx.get(f"{BASE}/api/discom/applications/{app_id}", headers=DISCOM, timeout=60)
    packet = r.json()
    check(
        "review packet has application, assessment, simulation and history",
        all(packet.get(k) for k in ("application", "assessment", "simulation", "history")),
    )
    check(
        "simulation carries the measured voltage rise",
        abs(float(packet["simulation"]["voltage_rise_pu"]) - 0.05751) < 1e-4,
        f"{packet['simulation']['voltage_rise_pu']} pu",
    )

    r = httpx.get(f"{BASE}/api/discom/transformers", headers=DISCOM, timeout=60)
    trafos = r.json()
    t7 = next((t for t in trafos if t["name"] == "T7"), None)
    check(
        "transformer loading is the measured base value",
        t7 is not None and abs(t7["base_loading_pct"] - 92.8) < 0.2,
        f"T7 {t7['base_loading_pct']}%" if t7 else "T7 missing",
    )
    check("transformers are ordered by loading", trafos[0]["base_loading_pct"] >= trafos[-1]["base_loading_pct"] if trafos[-1]["base_loading_pct"] is not None else True)

    r = httpx.get(f"{BASE}/api/discom/feeders", headers=DISCOM, timeout=60)
    feeders = r.json()
    check("feeder sections summarised", len(feeders) >= 5, f"{len(feeders)} sections")
    check(
        "section capacity carries its caveat",
        "true section limit is lower" in feeders[0]["capacity_note"],
    )

    # ============================================================
    print("\nD. Decisions are recorded, and overrides are attributable")
    # ============================================================
    r = httpx.post(
        f"{BASE}/api/discom/applications/{app_id}/decision",
        headers=DISCOM,
        json={"decision": "ENGINEERING_REVIEW", "notes": "Check the rise at 734."},
        timeout=60,
    )
    check("DISCOM can request engineering review", r.status_code == 200, r.json().get("decision", ""))

    r = httpx.post(
        f"{BASE}/api/discom/applications/{app_id}/decision",
        headers=DISCOM,
        json={"decision": "APPROVED", "notes": "Accepted with an inverter limit."},
        timeout=60,
    )
    body = r.json()
    check(
        "approving a CONSTRAINED case is flagged as an override",
        r.status_code == 200 and body["override_of_engineering_objection"] is True,
        body.get("note", ""),
    )

    audits = (
        svc.table("audit_logs")
        .select("action,actor_id,after_state")
        .eq("entity_id", app_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []
    override_audit = next((a for a in audits if a["action"] == "application.decision.approved"), None)
    check(
        "the override is in the audit log with the engineering objection",
        override_audit is not None
        and override_audit["after_state"]["override_of_engineering_objection"] is True
        and "exceeds" in (override_audit["after_state"].get("engineering_objection") or ""),
        (override_audit["after_state"].get("engineering_objection") or "")[:60] if override_audit else "",
    )
    check(
        "the audit names the deciding officer",
        override_audit is not None and override_audit["actor_id"] == discom_id,
    )

    final = (svc.table("solar_applications").select("*").eq("id", app_id).execute()).data[0]
    check("application is APPROVED with reviewer recorded", final["status"] == "APPROVED" and final["reviewed_by"] == discom_id)

    r = httpx.post(
        f"{BASE}/api/discom/applications/{app_id}/decision",
        headers=DISCOM,
        json={"decision": "NOT_A_DECISION"},
        timeout=60,
    )
    check("an invalid decision value is rejected", r.status_code == 422)

    # A fresh, unassessed application cannot be approved.
    r = httpx.post(
        f"{BASE}/api/applications",
        headers=CITIZEN,
        json={"applicant_name": "Unassessed", "pv_bus": "620", "existing_pv_kw": 0, "new_pv_kw": 5},
        timeout=60,
    )
    unassessed_id = r.json()["id"]
    r = httpx.post(
        f"{BASE}/api/discom/applications/{unassessed_id}/decision",
        headers=DISCOM,
        json={"decision": "APPROVED"},
        timeout=60,
    )
    check("an unassessed application cannot be approved", r.status_code == 409, f"status {r.status_code}")
    svc.table("solar_applications").delete().eq("id", unassessed_id).execute()

finally:
    print("\nE. Cleanup")
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
        svc.table("solar_applications").select("id").eq("id", app_id).execute().data if app_id else []
    )
    check("test data removed", not leftover)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 6 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
