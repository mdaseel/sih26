"""Phase 9 acceptance check — vendor dashboard.

The rule this phase lives or dies on: a vendor must never be able to mark
DISCOM verification complete. It is attacked here four ways — through the
status endpoint, by writing the status column directly, by writing the
discom_verified flags directly, and by a vendor calling the DISCOM route.
"""

from __future__ import annotations

import sys
import uuid
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402

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
app_id: str | None = None

try:
    # ============================================================
    print("\nA. Fixtures")
    # ============================================================
    def make(role: str) -> tuple[str, dict[str, str], str]:
        email = f"solargrid-p9-{uuid.uuid4().hex[:6]}@example.com"
        pw = f"Verify!{uuid.uuid4().hex[:12]}"
        u = svc.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True})
        users.append(u.user.id)
        if role != "CITIZEN":
            svc.table("profiles").update({"role": role}).eq("id", u.user.id).execute()
        token = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": pw}
        ).session.access_token
        return u.user.id, {"Authorization": f"Bearer {token}"}, token

    citizen_id, CITIZEN, citizen_token = make("CITIZEN")
    vendor_user_id, VENDOR, vendor_token = make("VENDOR")
    other_vendor_id, OTHER_VENDOR, _ = make("VENDOR")
    discom_id, DISCOM, _ = make("DISCOM")
    check("test users created", len(users) == 4)

    # A vendor, approved so a customer can engage it.
    r = httpx.post(
        f"{BASE}/api/vendors/register",
        headers=VENDOR,
        json={
            "business_name": "Phase 9 Installers",
            "representative_name": "Rep Nine",
            "district": "Demo District",
            "latitude": 12.98,
            "longitude": 77.61,
            "service_areas": ["Demo District"],
        },
        timeout=60,
    )
    vendor_id = r.json()["vendor"]["id"]
    httpx.post(
        f"{BASE}/api/discom/vendors/{vendor_id}/review",
        headers=DISCOM,
        json={"status": "APPROVED"},
        timeout=60,
    )
    check("vendor registered and approved", r.status_code == 201)

    # A second vendor, to prove cross-vendor isolation.
    r = httpx.post(
        f"{BASE}/api/vendors/register",
        headers=OTHER_VENDOR,
        json={"business_name": "Phase 9 Rival Installers", "district": "Demo District"},
        timeout=60,
    )
    other_vendor_row_id = r.json()["vendor"]["id"]
    httpx.post(
        f"{BASE}/api/discom/vendors/{other_vendor_row_id}/review",
        headers=DISCOM,
        json={"status": "APPROVED"},
        timeout=60,
    )

    r = httpx.post(
        f"{BASE}/api/applications",
        headers=CITIZEN,
        json={
            "applicant_name": "Phase 9 Applicant",
            "pv_bus": "620",
            "existing_pv_kw": 0,
            "new_pv_kw": 5,
            "district": "Demo District",
            "address_line": "12 Test Street",
            "contact_phone": "+91-99999-00000",
        },
        timeout=60,
    )
    app_id = r.json()["id"]
    httpx.post(f"{BASE}/api/applications/{app_id}/assess", headers=CITIZEN, timeout=180)
    check("application created and assessed", r.status_code == 201)

    # ============================================================
    print("\nB. A citizen engages a vendor, creating a lead")
    # ============================================================
    when = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    r = httpx.post(
        f"{BASE}/api/applications/{app_id}/select-vendor",
        headers=CITIZEN,
        json={"vendor_id": vendor_id, "scheduled_at": when, "notes": "Weekend preferred"},
        timeout=60,
    )
    check("POST select-vendor", r.status_code == 201, f"status {r.status_code}")
    appointment_id = r.json()["appointment"]["id"]
    check("the lead starts as REQUESTED", r.json()["appointment"]["status"] == "REQUESTED")

    # An unapproved vendor must not be engageable.
    pending = svc.table("vendors").insert(
        {"business_name": "Phase 9 Unapproved", "status": "PENDING"}
    ).execute().data[0]
    r = httpx.post(
        f"{BASE}/api/applications/{app_id}/select-vendor",
        headers=CITIZEN,
        json={"vendor_id": pending["id"], "scheduled_at": when},
        timeout=60,
    )
    check("an unapproved vendor cannot be engaged", r.status_code == 403, f"status {r.status_code}")
    svc.table("vendors").delete().eq("id", pending["id"]).execute()

    # ============================================================
    print("\nC. The vendor dashboard")
    # ============================================================
    r = httpx.get(f"{BASE}/api/vendor/summary", headers=VENDOR, timeout=60)
    summary = r.json()
    check("GET /api/vendor/summary", r.status_code == 200 and summary["new_leads"] == 1, f"{summary.get('new_leads')} new leads")
    check(
        "the summary states who may verify",
        "Only a DISCOM reviewer" in summary["verification_note"],
    )

    r = httpx.get(f"{BASE}/api/vendor/leads", headers=VENDOR, timeout=60)
    leads = r.json()
    check("the lead carries the application behind it", leads[0]["application"] is not None)
    check(
        "the customer's address is released for an engaged lead",
        leads[0]["application"]["address_line"] == "12 Test Street",
    )

    # A different vendor must see nothing of it.
    r = httpx.get(f"{BASE}/api/vendor/leads", headers=OTHER_VENDOR, timeout=60)
    check("another vendor sees no leads of ours", r.json() == [], f"{len(r.json())} leads")

    r = httpx.post(
        f"{BASE}/api/vendor/leads/{appointment_id}/respond",
        headers=OTHER_VENDOR,
        json={"accept": True},
        timeout=60,
    )
    check("another vendor cannot accept our lead", r.status_code == 403, f"status {r.status_code}")

    r = httpx.post(
        f"{BASE}/api/vendor/leads/{appointment_id}/respond",
        headers=VENDOR,
        json={"accept": True, "note": "Confirmed for Saturday"},
        timeout=60,
    )
    body = r.json()
    check("the vendor accepts the lead", r.status_code == 200 and body["accepted"] is True)
    check("accepting opens an installation record", body["installation"] is not None)
    installation_id = body["installation"]["id"]
    check("the installation starts PENDING", body["installation"]["status"] == "PENDING")

    r = httpx.post(
        f"{BASE}/api/vendor/leads/{appointment_id}/respond",
        headers=VENDOR,
        json={"accept": True},
        timeout=60,
    )
    check("a lead cannot be answered twice", r.status_code == 409, f"status {r.status_code}")

    # ============================================================
    print("\nD. Installation progress, up to but not including VERIFIED")
    # ============================================================
    for status in ["SITE_VISIT", "SCHEDULED", "IN_PROGRESS", "COMPLETED", "VERIFICATION_PENDING"]:
        r = httpx.post(
            f"{BASE}/api/vendor/installations/{installation_id}/status",
            headers=VENDOR,
            json={"status": status, "installed_capacity_kw": 5},
            timeout=60,
        )
        check(f"vendor may set {status}", r.status_code == 200, f"status {r.status_code}")

    # ---- the boundary, attacked four ways ----
    r = httpx.post(
        f"{BASE}/api/vendor/installations/{installation_id}/status",
        headers=VENDOR,
        json={"status": "VERIFIED"},
        timeout=60,
    )
    check(
        "1/4 API: a vendor cannot set VERIFIED",
        r.status_code == 403 and "DISCOM" in r.json()["detail"],
        r.json().get("detail", "")[:70],
    )

    ven = get_anon_client()
    ven.postgrest.auth(vendor_token)
    try:
        res = ven.table("installations").update({"status": "VERIFIED"}).eq("id", installation_id).execute()
        check("2/4 DB: a vendor cannot write status=VERIFIED", not res.data, f"{len(res.data)} rows")
    except Exception as exc:  # noqa: BLE001
        check("2/4 DB: a vendor cannot write status=VERIFIED", denied(exc), type(exc).__name__)

    try:
        res = (
            ven.table("installations")
            .update({"discom_verified": True, "discom_verified_by": vendor_user_id})
            .eq("id", installation_id)
            .execute()
        )
        check("3/4 DB: a vendor cannot set the discom_verified flags", not res.data, f"{len(res.data)} rows")
    except Exception as exc:  # noqa: BLE001
        check("3/4 DB: a vendor cannot set the discom_verified flags", denied(exc), type(exc).__name__)

    r = httpx.post(
        f"{BASE}/api/discom/installations/{installation_id}/verify",
        headers=VENDOR,
        json={"notes": "self-verified"},
        timeout=60,
    )
    check("4/4 route: a vendor cannot call the DISCOM verify endpoint", r.status_code == 403)

    state = (svc.table("installations").select("*").eq("id", installation_id).execute()).data[0]
    check(
        "after all four attempts the installation is still unverified",
        state["status"] == "VERIFICATION_PENDING" and state["discom_verified"] is False,
        f"status {state['status']}, discom_verified {state['discom_verified']}",
    )

    r = httpx.post(
        f"{BASE}/api/applications/{app_id}/select-vendor",
        headers=CITIZEN,
        json={"vendor_id": vendor_id, "scheduled_at": when},
        timeout=60,
    )
    citizen_client = get_anon_client()
    citizen_client.postgrest.auth(citizen_token)
    try:
        res = (
            citizen_client.table("installations")
            .update({"status": "VERIFIED", "discom_verified": True})
            .eq("id", installation_id)
            .execute()
        )
        check("a citizen cannot verify their own installation", not res.data, f"{len(res.data)} rows")
    except Exception as exc:  # noqa: BLE001
        check("a citizen cannot verify their own installation", denied(exc), type(exc).__name__)

    # ============================================================
    print("\nE. Only DISCOM can verify")
    # ============================================================
    r = httpx.post(
        f"{BASE}/api/discom/installations/{installation_id}/verify",
        headers=DISCOM,
        json={"notes": "Inspected on site."},
        timeout=60,
    )
    check("DISCOM can verify", r.status_code == 200, f"status {r.status_code}")

    final = (svc.table("installations").select("*").eq("id", installation_id).execute()).data[0]
    check(
        "the installation is VERIFIED and attributed",
        final["status"] == "VERIFIED"
        and final["discom_verified"] is True
        and final["discom_verified_by"] == discom_id,
    )

    audits = (
        svc.table("audit_logs").select("action,actor_id").eq("entity_id", installation_id).execute()
    ).data or []
    check(
        "verification is audited against the DISCOM officer",
        any(a["action"] == "installation.discom_verified" and a["actor_id"] == discom_id for a in audits),
        f"{len(audits)} audit entries",
    )

    # ============================================================
    print("\nF. Profile and documents")
    # ============================================================
    r = httpx.get(f"{BASE}/api/vendor/profile", headers=VENDOR, timeout=60)
    profile = r.json()
    check("GET /api/vendor/profile", r.status_code == 200)
    check(
        "document types come from configuration, not code",
        len(profile["document_types"]) >= 3
        and all("code" in d and "label" in d for d in profile["document_types"]),
        f"{len(profile['document_types'])} types",
    )

    r = httpx.patch(
        f"{BASE}/api/vendor/profile",
        headers=VENDOR,
        json={"years_experience": 7, "phone": "+91-88888-00000"},
        timeout=60,
    )
    check("a vendor can edit its own profile", r.status_code == 200 and r.json()["years_experience"] == 7)

    try:
        ven.table("vendors").update({"status": "APPROVED", "rating": 5.0}).eq("id", vendor_id).execute()
    except Exception:  # noqa: BLE001
        pass
    after = (svc.table("vendors").select("rating").eq("id", vendor_id).execute()).data[0]
    check("a vendor cannot award itself a rating", after["rating"] is None, f"rating {after['rating']}")

    r = httpx.post(
        f"{BASE}/api/vendor/documents",
        headers=VENDOR,
        json={"document_type": "GST_CERTIFICATE", "file_path": "vendors/p9/gst.pdf", "file_name": "gst.pdf"},
        timeout=60,
    )
    check("a document can be attached", r.status_code == 201 and r.json()["is_verified"] is False)

    r = httpx.post(
        f"{BASE}/api/vendor/documents",
        headers=VENDOR,
        json={"document_type": "NOT_A_TYPE", "file_path": "x.pdf"},
        timeout=60,
    )
    check("an unconfigured document type is rejected", r.status_code == 422)

    r = httpx.get(f"{BASE}/api/vendor/summary", headers=CITIZEN, timeout=60)
    check("a citizen has no vendor portal", r.status_code == 403, f"status {r.status_code}")

    r = httpx.get(f"{BASE}/api/vendor/projects", headers=VENDOR, timeout=60)
    check("projects list the engaged application", r.status_code == 200 and len(r.json()) >= 1)

finally:
    print("\nG. Cleanup")
    if app_id:
        try:
            svc.table("solar_applications").delete().eq("id", app_id).execute()
        except Exception:  # noqa: BLE001
            pass
    for vid in [vendor_id, locals().get("other_vendor_row_id")]:
        if vid:
            try:
                svc.table("vendors").delete().eq("id", vid).execute()
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
print(f"\n{'=' * 60}\nPHASE 9 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
