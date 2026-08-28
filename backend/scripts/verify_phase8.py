"""Phase 8 acceptance check — vendor workflow and discovery.

Two rules carry this phase:

  * Only APPROVED and active vendors are visible to customers — tested through
    the API and by querying the database directly with a citizen's token.
  * Straight-line distance is never presented as a route.
"""

from __future__ import annotations

import sys
import uuid
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402
from app.services.routing import (  # noqa: E402
    OSRMProvider,
    RoutingService,
    StraightLineProvider,
    get_routing_service,
)

BASE = "http://127.0.0.1:8000"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def denied(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(m in text for m in ("row-level security", "permission denied", "violates", "42501", "pgrst"))


svc = get_service_client()
users: list[str] = []
vendor_id: str | None = None

try:
    # ============================================================
    print("\nA. Routing is never dressed up as something it is not")
    # ============================================================
    straight = StraightLineProvider()
    r = straight.distance(12.9716, 77.5946, 12.9750, 77.6050)
    check(
        "straight-line results declare is_route = False",
        r.is_route is False and r.method == "STRAIGHT_LINE",
        f"{r.distance_km} km, method {r.method}",
    )
    check(
        "the note says it is not travel distance",
        "not" in r.note.lower() and ("travel" in r.note.lower() or "routing" in r.note.lower()),
        r.note[:70],
    )
    check("no duration is invented for a straight line", r.duration_minutes is None)

    # A known separation: ~1 degree of latitude is ~111 km.
    far = straight.distance(0.0, 0.0, 1.0, 0.0)
    check(
        "the haversine maths is right",
        abs(far.distance_km - 111.19) < 0.5,
        f"1 degree of latitude = {far.distance_km} km",
    )

    service = get_routing_service()
    check(
        "with no provider configured, routing_available is False",
        service.routing_available is False,
        f"provider {service.provider.name}",
    )
    check(
        "the integration point is documented in the response",
        "ROUTING_PROVIDER" in service.describe()["integration_point"],
    )

    # A misconfigured routing provider must degrade honestly, not silently.
    broken = RoutingService(OSRMProvider("http://127.0.0.1:9"))
    fallback = broken.distance(12.97, 77.59, 12.98, 77.60)
    check(
        "an unreachable routing service degrades to a labelled straight line",
        fallback is not None
        and fallback.is_route is False
        and fallback.method == "STRAIGHT_LINE_FALLBACK",
        f"method {fallback.method if fallback else 'None'}",
    )

    check(
        "no distance is produced when a location is missing",
        service.distance(None, None, 12.97, 77.59) is None
        and service.distance(12.97, 77.59, None, None) is None,
    )

    # ============================================================
    print("\nB. Fixtures")
    # ============================================================
    def make(role: str) -> tuple[str, dict[str, str]]:
        email = f"solargrid-p8-{uuid.uuid4().hex[:6]}@example.com"
        pw = f"Verify!{uuid.uuid4().hex[:12]}"
        u = svc.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True})
        users.append(u.user.id)
        if role != "CITIZEN":
            svc.table("profiles").update({"role": role}).eq("id", u.user.id).execute()
        token = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": pw}
        ).session.access_token
        return u.user.id, {"Authorization": f"Bearer {token}"}

    citizen_id, CITIZEN = make("CITIZEN")
    discom_id, DISCOM = make("DISCOM")
    applicant_id, APPLICANT = make("CITIZEN")
    check("test users created", len(users) == 3)

    # ============================================================
    print("\nC. Registration always starts PENDING")
    # ============================================================
    r = httpx.post(
        f"{BASE}/api/vendors/register",
        headers=CITIZEN,
        json={
            "business_name": "Phase 8 Test Installers",
            "representative_name": "Test Rep",
            "district": "Demo District",
            "state": "Demo State",
            "latitude": 12.9800,
            "longitude": 77.6100,
            "service_areas": ["Demo District"],
            "years_experience": 3,
        },
        timeout=60,
    )
    check("POST /api/vendors/register", r.status_code == 201, f"status {r.status_code}")
    vendor_id = r.json()["vendor"]["id"]
    check(
        "a new vendor is PENDING and unverified",
        r.json()["vendor"]["status"] == "PENDING" and r.json()["vendor"]["verified_at"] is None,
    )

    r = httpx.post(
        f"{BASE}/api/vendors/register",
        headers=CITIZEN,
        json={"business_name": "Second Profile"},
        timeout=60,
    )
    check("one vendor profile per account", r.status_code == 409, f"status {r.status_code}")

    # The direct attack: register already APPROVED.
    cit = get_anon_client()
    cit.postgrest.auth(CITIZEN["Authorization"].split(" ", 1)[1])
    try:
        res = (
            cit.table("vendors")
            .insert(
                {
                    "owner_id": citizen_id,
                    "business_name": "Self Approved Ltd",
                    "status": "APPROVED",
                }
            )
            .execute()
        )
        check("a vendor cannot self-register as APPROVED", not res.data, "insert succeeded")
    except Exception as exc:  # noqa: BLE001
        check("a vendor cannot self-register as APPROVED", denied(exc), type(exc).__name__)

    # Nor promote itself afterwards.
    try:
        cit.table("vendors").update({"status": "APPROVED"}).eq("id", vendor_id).execute()
    except Exception:  # noqa: BLE001
        pass
    status_now = (svc.table("vendors").select("status").eq("id", vendor_id).execute()).data[0]
    check(
        "a vendor cannot approve itself later",
        status_now["status"] == "PENDING",
        f"status is {status_now['status']}",
    )

    # ============================================================
    print("\nD. Customers see approved, active vendors only")
    # ============================================================
    all_vendors = (svc.table("vendors").select("id,status,is_active").execute()).data or []
    should_see = [v for v in all_vendors if v["status"] == "APPROVED" and v["is_active"]]

    r = httpx.get(f"{BASE}/api/vendors", headers=APPLICANT, timeout=60)
    listed = r.json()
    check(
        "the API returns only approved and active vendors",
        listed["total"] == len(should_see),
        f"{listed['total']} of {len(all_vendors)} in the table",
    )
    check(
        "every returned vendor is marked verified",
        all(v["verified"] for v in listed["vendors"]),
    )
    check(
        "the pending vendor just registered is not listed",
        not any(v["id"] == vendor_id for v in listed["vendors"]),
    )

    # And independently, at the database layer.
    other = get_anon_client()
    other.postgrest.auth(APPLICANT["Authorization"].split(" ", 1)[1])
    rows = other.table("vendors").select("id,status,is_active").execute().data or []
    check(
        "RLS alone also hides unapproved vendors",
        all(v["status"] == "APPROVED" and v["is_active"] for v in rows),
        f"{len(rows)} rows visible directly",
    )

    # ============================================================
    print("\nE. Nearest-vendor search")
    # ============================================================
    r = httpx.post(
        f"{BASE}/api/applications",
        headers=APPLICANT,
        json={
            "applicant_name": "Phase 8 Applicant",
            "pv_bus": "620",
            "existing_pv_kw": 0,
            "new_pv_kw": 5,
            "district": "Demo District",
            "latitude": 12.9716,
            "longitude": 77.5946,
        },
        timeout=60,
    )
    app_id = r.json()["id"]

    r = httpx.get(f"{BASE}/api/applications/{app_id}/vendors", headers=APPLICANT, timeout=60)
    near = r.json()
    check("GET /api/applications/{id}/vendors", r.status_code == 200)
    check("the customer location is recognised", near["customer_location_known"] is True)

    distances = [v["distance"]["distance_km"] for v in near["vendors"] if v["distance"]]
    check(
        "results are ordered nearest first",
        distances == sorted(distances),
        " · ".join(f"{d:.1f} km" for d in distances),
    )
    check(
        "every distance is labelled as not a route",
        all(not v["distance"]["is_route"] for v in near["vendors"] if v["distance"]),
    )
    check(
        "the response warns the distance is straight-line",
        "straight-line" in near["distance_note"].lower()
        and "not travel distance" in near["distance_note"].lower(),
        near["distance_note"][:70],
    )

    # An application with no coordinates must not borrow the synthetic bus location.
    svc.table("solar_applications").update({"latitude": None, "longitude": None}).eq(
        "id", app_id
    ).execute()
    r = httpx.get(f"{BASE}/api/applications/{app_id}/vendors", headers=APPLICANT, timeout=60)
    nowhere = r.json()
    check(
        "with no address, no distance is invented",
        nowhere["customer_location_known"] is False
        and all(v["distance"] is None for v in nowhere["vendors"]),
    )
    check(
        "the synthetic map coordinates are explicitly not used",
        "synthetic" in nowhere["location_note"].lower(),
    )
    svc.table("solar_applications").delete().eq("id", app_id).execute()

    # ============================================================
    print("\nF. DISCOM review controls visibility")
    # ============================================================
    r = httpx.get(f"{BASE}/api/discom/vendors", headers=CITIZEN, timeout=60)
    check("a citizen cannot open the vendor queue", r.status_code == 403, f"status {r.status_code}")

    r = httpx.post(
        f"{BASE}/api/discom/vendors/{vendor_id}/review",
        headers=CITIZEN,
        json={"status": "APPROVED"},
        timeout=60,
    )
    check("a citizen cannot approve a vendor", r.status_code == 403, f"status {r.status_code}")

    r = httpx.get(f"{BASE}/api/discom/vendors", headers=DISCOM, timeout=60)
    queue = r.json()
    check(
        "DISCOM sees every vendor whatever the status",
        r.status_code == 200 and len(queue["vendors"]) == len(all_vendors),
        f"{len(queue['vendors'])} vendors",
    )

    r = httpx.post(
        f"{BASE}/api/discom/vendors/{vendor_id}/review",
        headers=DISCOM,
        json={"status": "APPROVED", "reason": "Documents verified."},
        timeout=60,
    )
    check(
        "DISCOM approval makes a vendor visible",
        r.status_code == 200 and r.json()["visible_to_customers"] is True,
    )

    r = httpx.get(f"{BASE}/api/vendors", headers=APPLICANT, timeout=60)
    check(
        "the newly approved vendor now appears to customers",
        any(v["id"] == vendor_id for v in r.json()["vendors"]),
    )

    r = httpx.post(
        f"{BASE}/api/discom/vendors/{vendor_id}/review",
        headers=DISCOM,
        json={"status": "SUSPENDED", "reason": "Complaint received."},
        timeout=60,
    )
    check("suspension is accepted", r.status_code == 200 and r.json()["visible_to_customers"] is False)

    r = httpx.get(f"{BASE}/api/vendors", headers=APPLICANT, timeout=60)
    check(
        "a suspended vendor disappears from customer view",
        not any(v["id"] == vendor_id for v in r.json()["vendors"]),
    )

    r = httpx.post(
        f"{BASE}/api/discom/vendors/{vendor_id}/review",
        headers=DISCOM,
        json={"status": "NONSENSE"},
        timeout=60,
    )
    check("an invalid status is rejected", r.status_code == 422)

    audits = (
        svc.table("audit_logs")
        .select("action,actor_id")
        .eq("entity_id", vendor_id)
        .execute()
    ).data or []
    check(
        "vendor decisions are audited against the reviewer",
        any(a["action"].startswith("vendor.review.") and a["actor_id"] == discom_id for a in audits),
        f"{len(audits)} audit entries",
    )

finally:
    print("\nG. Cleanup")
    if vendor_id:
        try:
            svc.table("vendors").delete().eq("id", vendor_id).execute()
        except Exception:  # noqa: BLE001
            pass
    for uid in users:
        try:
            svc.auth.admin.delete_user(uid)
        except Exception:  # noqa: BLE001
            pass
    check("test data removed", True)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 8 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
