"""Prepare a clean, reproducible demo across all three portals.

Creates (or resets) three accounts with fixed passwords, grants their roles,
and seeds enough real data that every screen has something to show:

    citizen  one application awaiting DISCOM review, plus one already approved
    DISCOM   that pending application in its queue, vendors to verify
    vendor   an approved business with a live lead

Every electrical value is produced by a power flow during this run — the
applications are genuinely assessed, not inserted with made-up numbers.

Usage:
    python backend/scripts/setup_demo_accounts.py            # set up
    python backend/scripts/setup_demo_accounts.py --status   # show what exists
    python backend/scripts/setup_demo_accounts.py --remove    # tear down
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402

BASE = "http://127.0.0.1:8000"

ACCOUNTS = [
    ("demo.citizen@solargrid.test", "DemoCitizen!2026", "CITIZEN", "Demo Citizen"),
    ("demo.discom@solargrid.test", "DemoDiscom!2026", "DISCOM", "Demo DISCOM Officer"),
    ("demo.vendor@solargrid.test", "DemoVendor!2026", "VENDOR", "Demo Installer Rep"),
]

# Bus 732: a real connection point with 25.4 kW of load on transformer T4.
PENDING_APPLICATION = {
    "applicant_name": "Demo Citizen",
    "pv_bus": "732",
    "existing_pv_kw": 0,
    "new_pv_kw": 5,
    "address_line": "House H-024, Demo Colony",
    "district": "Demo District",
    "state": "Demo State",
    "contact_phone": "+91-90000-00024",
    "monthly_consumption_kwh": 320,
    "roof_type": "RCC flat",
    "roof_area_sqm": 45,
    "shading_level": "Low",
    "latitude": 12.9716,
    "longitude": 77.5946,
}

# Bus 734 at 66 kW: the historically false-SAFE case. Useful for a demo because
# the verdict is CONSTRAINED and the twin lights up.
CONSTRAINED_APPLICATION = {
    **PENDING_APPLICATION,
    "applicant_name": "Demo Citizen",
    "pv_bus": "734",
    "new_pv_kw": 66,
    "address_line": "House H-091, Demo Colony",
}


def line(label: str, value: object) -> None:
    print(f"    {label:<32} {value}")


def sign_in(email: str, password: str) -> dict[str, str]:
    token = get_anon_client().auth.sign_in_with_password(
        {"email": email, "password": password}
    ).session.access_token
    return {"Authorization": f"Bearer {token}"}


def remove(svc) -> int:
    removed = 0
    apps = (svc.table("solar_applications").select("id,applicant_name").execute()).data or []
    for a in apps:
        if a["applicant_name"].startswith("Demo "):
            svc.table("solar_applications").delete().eq("id", a["id"]).execute()
            removed += 1

    for u in svc.auth.admin.list_users():
        if u.email and u.email in {e for e, *_ in ACCOUNTS}:
            vendors = (svc.table("vendors").select("id").eq("owner_id", u.id).execute()).data or []
            for v in vendors:
                svc.table("vendors").delete().eq("id", v["id"]).execute()
            svc.auth.admin.delete_user(u.id)
            removed += 1
    return removed


def status(svc) -> None:
    print("\n=== demo accounts ===")
    emails = {u.email: u.id for u in svc.auth.admin.list_users() if u.email}
    for email, password, role, _ in ACCOUNTS:
        if email in emails:
            profile = (
                svc.table("profiles").select("role").eq("id", emails[email]).execute()
            ).data
            actual = profile[0]["role"] if profile else "?"
            mark = "ok" if actual == role else f"ROLE IS {actual}, EXPECTED {role}"
            print(f"    {email:38} {password:20} {actual:8} {mark}")
        else:
            print(f"    {email:38} {'—':20} MISSING")

    print("\n=== demo data ===")
    apps = (
        svc.table("solar_applications")
        .select("application_number,pv_bus,new_pv_kw,status")
        .execute()
    ).data or []
    for a in apps:
        print(f"    {a['application_number']}  bus {a['pv_bus']:>5}  "
              f"{float(a['new_pv_kw']):>6.1f} kW  {a['status']}")
    vendors = (svc.table("vendors").select("business_name,status,is_active").execute()).data or []
    visible = sum(1 for v in vendors if v["status"] == "APPROVED" and v["is_active"])
    print(f"    vendors: {len(vendors)} ({visible} visible to customers)")
    leads = (svc.table("appointments").select("status").execute()).data or []
    print(f"    appointments: {len(leads)}")
    installs = (svc.table("installations").select("status").execute()).data or []
    print(f"    installations: {len(installs)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    svc = get_service_client()

    if args.status:
        status(svc)
        return 0

    if args.remove:
        print(f"removed {remove(svc)} demo records")
        return 0

    try:
        httpx.get(f"{BASE}/health", timeout=10)
    except Exception:
        print(f"Backend is not running at {BASE}. Start it first:")
        print("  .venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --port 8000")
        return 1

    print("=" * 72)
    print("  Preparing the demo")
    print("=" * 72)

    remove(svc)

    # ---- accounts ----
    print("\n1. Accounts")
    headers: dict[str, dict[str, str]] = {}
    for email, password, role, full_name in ACCOUNTS:
        user = svc.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,  # skips the confirmation email
                "user_metadata": {"full_name": full_name},
            }
        )
        # The signup trigger always creates a CITIZEN profile; elevating a role
        # is an administrative action, never self-service.
        if role != "CITIZEN":
            svc.table("profiles").update({"role": role, "full_name": full_name}).eq(
                "id", user.user.id
            ).execute()
        headers[role] = sign_in(email, password)
        line(f"{role}", f"{email}  /  {password}")

    # ---- a pending application for the DISCOM to review ----
    print("\n2. Citizen application awaiting review")
    created = httpx.post(
        f"{BASE}/api/applications", headers=headers["CITIZEN"], json=PENDING_APPLICATION, timeout=60
    ).json()
    assessed = httpx.post(
        f"{BASE}/api/applications/{created['id']}/assess", headers=headers["CITIZEN"], timeout=300
    ).json()
    line("Application", created["application_number"])
    line("Connection point", f"bus {created['pv_bus']} · 5.0 kW")
    line("Verdict", assessed["engineering"]["engineering_risk"])
    line("Voltage rise", f"{assessed['metrics']['voltage_rise_pu']:.5f} pu")
    pending_id = created["id"]

    # ---- a constrained application, so CONSTRAINED is visible somewhere ----
    print("\n3. A constrained application, for contrast")
    constrained = httpx.post(
        f"{BASE}/api/applications",
        headers=headers["CITIZEN"],
        json=CONSTRAINED_APPLICATION,
        timeout=60,
    ).json()
    c_result = httpx.post(
        f"{BASE}/api/applications/{constrained['id']}/assess",
        headers=headers["CITIZEN"],
        timeout=300,
    ).json()
    line("Application", constrained["application_number"])
    line("Connection point", f"bus {constrained['pv_bus']} · 66.0 kW")
    line("Verdict", c_result["engineering"]["engineering_risk"])
    line("Reason", c_result["engineering"]["constraint_reason"])

    # ---- vendor, approved, with a live lead ----
    print("\n4. Vendor with a live lead")
    vendor = httpx.post(
        f"{BASE}/api/vendors/register",
        headers=headers["VENDOR"],
        json={
            "business_name": "Demo Installer Co",
            "representative_name": "Demo Installer Rep",
            "district": "Demo District",
            "state": "Demo State",
            "latitude": 12.9750,
            "longitude": 77.6050,
            "service_areas": ["Demo District"],
            "years_experience": 6,
            "installation_capacity_kw": 400,
            "phone": "+91-90000-11111",
        },
        timeout=60,
    ).json()["vendor"]
    line("Registered as", vendor["status"])

    httpx.post(
        f"{BASE}/api/discom/vendors/{vendor['id']}/review",
        headers=headers["DISCOM"],
        json={"status": "APPROVED", "reason": "Documents verified."},
        timeout=60,
    )
    line("After DISCOM review", "APPROVED — now visible to customers")

    when = (datetime.now(timezone.utc) + timedelta(days=4)).replace(microsecond=0)
    booking = httpx.post(
        f"{BASE}/api/applications/{pending_id}/select-vendor",
        headers=headers["CITIZEN"],
        json={
            "vendor_id": vendor["id"],
            "scheduled_at": when.isoformat(),
            "notes": "Weekend morning preferred.",
        },
        timeout=60,
    )
    line("Site visit requested", when.strftime("%Y-%m-%d %H:%M UTC"))
    line("Vendor lead", "REQUESTED — waiting for the vendor to accept")

    # ---- what to do next ----
    print("\n" + "=" * 72)
    print("  Ready. Open http://localhost:3000")
    print("=" * 72)
    print("""
  CITIZEN   demo.citizen@solargrid.test / DemoCitizen!2026
            /citizen/dashboard   two applications, one SAFE and one CONSTRAINED
            /citizen/twin        pick a bus, try 5 / 66 / 250 kW
            /citizen/map         six layers, streets toggle
            /citizen/vendors     four approved installers, nearest first
            /citizen/scheme      PM Surya Ghar and the CFA estimate

  DISCOM    demo.discom@solargrid.test / DemoDiscom!2026
            /discom/dashboard        two applications awaiting review
            /discom/applications     open one and approve it
            /discom/what-if          sweep capacities at a bus
            /discom/hosting-capacity per-bus and per-section limits
            /discom/vendors          approve or suspend an installer
            /discom/installations    verify finished work

  VENDOR    demo.vendor@solargrid.test / DemoVendor!2026
            /vendor/login        sign in here, not at /login
            /vendor/leads        one lead waiting — accept it
            /vendor/installations advance the work; VERIFIED is locked

  Sign out between portals: sessions are per-browser, and the citizen
  account is refused at /discom (which is the point).
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
