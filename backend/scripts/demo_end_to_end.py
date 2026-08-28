"""End-to-end demonstration of the whole SolarGrid workflow.

Drives the complete journey through the real HTTP API — no shortcuts, no
direct database writes to fake a state, no precomputed answers. Every
electrical figure printed here is produced by a power flow during the run.

    citizen registers
      -> submits an application
      -> grid connection point identified
      -> ML pre-screen
      -> power-flow verification
      -> risk recorded
      -> digital twin reflects the change
      -> map marker appears
      -> DISCOM reviews and approves
      -> citizen sees approved installers
      -> citizen books a site visit
      -> vendor receives the lead and accepts
      -> vendor progresses the installation
      -> DISCOM verifies the finished work
      -> indicative CFA shown

A note on the scenario
----------------------
The brief describes a customer with 1.2 kW of existing load. This feeder has
no such bus: its LV buses are distribution secondaries serving many premises,
and the smallest modelled load is 15.85 kW. Rather than invent a 1.2 kW bus,
the demo connects at a real one (bus 732, 25.4 kW aggregate load) and prints
what is actually there. The requested 5 kW is the customer's own system.

Usage:
    python backend/scripts/demo_end_to_end.py
    python backend/scripts/demo_end_to_end.py --reset   # remove demo data
"""

from __future__ import annotations

import argparse
import sys
import uuid
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402

BASE = "http://127.0.0.1:8000"
TAG = "demo-e2e"

CUSTOMER = {
    "premises": "House H-024",
    "applicant_name": "Demo Customer H-024",
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

STEP = 0


def step(title: str) -> None:
    global STEP
    STEP += 1
    print(f"\n{'─' * 74}\n  STEP {STEP}  {title}\n{'─' * 74}")


def line(label: str, value: Any, unit: str = "") -> None:
    print(f"    {label:<34} {value}{(' ' + unit) if unit else ''}")


def fail(message: str) -> None:
    print(f"\n  DEMO FAILED: {message}")
    raise SystemExit(1)


def reset(svc) -> int:
    """Remove everything this demo created."""
    removed = 0
    apps = (svc.table("solar_applications").select("id,applicant_name").execute()).data or []
    for a in apps:
        if a["applicant_name"].startswith("Demo Customer H-"):
            svc.table("solar_applications").delete().eq("id", a["id"]).execute()
            removed += 1

    vendors = (svc.table("vendors").select("id,business_name,owner_id").execute()).data or []
    for v in vendors:
        if v["business_name"].startswith("Demo E2E"):
            svc.table("vendors").delete().eq("id", v["id"]).execute()
            removed += 1

    try:
        for u in svc.auth.admin.list_users():
            if u.email and TAG in u.email:
                svc.auth.admin.delete_user(u.id)
                removed += 1
    except Exception:  # noqa: BLE001
        pass
    return removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="remove demo data and exit")
    args = ap.parse_args()

    svc = get_service_client()

    if args.reset:
        print(f"removed {reset(svc)} demo records")
        return 0

    try:
        httpx.get(f"{BASE}/health", timeout=10)
    except Exception:
        fail(f"backend not reachable at {BASE}")

    print("=" * 74)
    print("  SolarGrid AI — end-to-end demonstration")
    print("  Every electrical value below is produced by a power flow during this run.")
    print("=" * 74)

    reset(svc)

    def account(role: str, label: str) -> dict[str, str]:
        email = f"{TAG}-{label}-{uuid.uuid4().hex[:6]}@solargrid.test"
        pw = f"Demo!{uuid.uuid4().hex[:12]}"
        u = svc.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True})
        if role != "CITIZEN":
            svc.table("profiles").update({"role": role}).eq("id", u.user.id).execute()
        token = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": pw}
        ).session.access_token
        return {"Authorization": f"Bearer {token}"}

    # ============================================================
    step("Citizen registers")
    CITIZEN = account("CITIZEN", "citizen")
    DISCOM = account("DISCOM", "discom")
    VENDOR = account("VENDOR", "vendor")
    line("Premises", CUSTOMER["premises"])
    line("Applicant", CUSTOMER["applicant_name"])
    line("Roles created", "CITIZEN, DISCOM, VENDOR")

    # ============================================================
    step("Connection point identified from the feeder model")
    buses = httpx.get(f"{BASE}/api/grid/buses", headers=CITIZEN, timeout=60).json()
    bus = next(b for b in buses if b["bus_id"] == CUSTOMER["pv_bus"])
    line("Connection point", f"bus {bus['bus_id']}")
    line("Voltage level", bus["vn_kv"], "kV")
    line("Serving transformer", f"{bus['transformer_association']} ({bus['transformer_sn_kva']:.0f} kVA)")
    line("Feeder section", bus["feeder_section"])
    line("Existing load at this bus", f"{bus['existing_load_kw']:.2f}", "kW")
    line("Distance from substation", f"{bus['feeder_distance_km']:.2f}", "km")
    line("Upstream impedance", f"{bus['upstream_z_ohm']:.2f}", "ohm")

    # ============================================================
    step("Citizen submits the application")
    payload = {k: v for k, v in CUSTOMER.items() if k != "premises"}
    r = httpx.post(f"{BASE}/api/applications", headers=CITIZEN, json=payload, timeout=60)
    if r.status_code != 201:
        fail(f"application not created: {r.status_code} {r.text[:200]}")
    application = r.json()
    app_id = application["id"]
    line("Application number", application["application_number"])
    line("Existing solar", f"{float(application['existing_pv_kw']):.1f}", "kW")
    line("Requested solar", f"{float(application['new_pv_kw']):.1f}", "kW")
    line("Total after install", f"{float(application['total_pv_kw']):.1f}", "kW")
    line("Status", application["status"])

    # ============================================================
    step("ML pre-screen and power-flow verification")
    r = httpx.post(f"{BASE}/api/applications/{app_id}/assess", headers=CITIZEN, timeout=300)
    if r.status_code != 200:
        fail(f"assessment failed: {r.status_code} {r.text[:200]}")
    result = r.json()
    ml, eng, m = result["ml"], result["engineering"], result["metrics"]

    print("    ML pre-screen")
    line("  Model", f"{ml['model_file']} ({ml['feature_count']} features)")
    line("  Prediction", ml["prediction"])
    line(
        "  Probabilities",
        f"SAFE {ml['safe_probability']:.3f} · CAUTION {ml['caution_probability']:.3f} · "
        f"CONSTRAINED {ml['constrained_probability']:.3f}",
    )
    print("    Power-flow verification (the decision)")
    line("  Engine", f"{m['engine']} {m['engine_version']} on {m['network_file']}")
    line("  Voltage before", f"{m['base_voltage_pu']:.5f}", "pu")
    line("  Voltage after", f"{m['pv_voltage_pu']:.5f}", "pu")
    line("  Voltage rise", f"{m['voltage_rise_pu']:.5f}", "pu")
    line("  Feeder min / max", f"{m['feeder_min_voltage_pu']:.4f} / {m['feeder_max_voltage_pu']:.4f}", "pu")
    line("  Transformer loading", f"{m['max_transformer_loading_pct']:.2f}", "%")
    line("  Line loading", f"{m['max_line_loading_pct']:.2f}", "%")
    line("  Reverse power flow", "Yes" if m["reverse_power_flow"] else "No")
    line("  Feeder losses", f"{m['power_loss_kw']:.2f}", "kW")
    line("  Solve time", m["runtime_ms"], "ms")
    line("  VERDICT", eng["engineering_risk"])
    line("  Reason", eng["constraint_reason"])
    line("  ML agrees", result["ml_agrees_with_engineering"])

    if eng["engineering_risk"] == "CONSTRAINED":
        fail("demo scenario is CONSTRAINED; pick a different bus or capacity")

    # ============================================================
    step("Digital twin reflects the change")
    twin = httpx.post(
        f"{BASE}/api/twin",
        headers=CITIZEN,
        json={
            "pv_bus": CUSTOMER["pv_bus"],
            "existing_pv_kw": CUSTOMER["existing_pv_kw"],
            "new_pv_kw": CUSTOMER["new_pv_kw"],
        },
        timeout=120,
    ).json()
    path = twin["topology"]["path"]
    eb = twin["elements"]["energy_balance"]
    line("Electrical path", " → ".join(path))
    line("Serving transformer", twin["topology"]["serving_transformer"]["name"])
    moved = [
        (b, v["delta_pu"]) for b, v in twin["elements"]["buses"].items() if abs(v["delta_pu"]) >= 1e-5
    ]
    line("Buses whose voltage moved", f"{len(moved)} of {len(twin['elements']['buses'])}")
    for b, d in moved[-3:]:
        line(f"  bus {b}", f"{d:+.5f}", "pu")
    line("Grid supply before", f"{eb['grid_supply_before_kw']:.1f}", "kW")
    line("Grid supply after", f"{eb['grid_supply_after_kw']:.1f}", "kW")
    line("Solar generation", f"{eb['solar_generation_kw']:.1f}", "kW")
    line("Local consumption", f"{eb['local_consumption_kw']:.2f}", "kW")
    line("Exported to grid", f"{eb['local_export_kw']:.1f}", "kW")

    # ============================================================
    step("Map marker appears for the application")
    mapdata = httpx.get(f"{BASE}/api/map", headers=CITIZEN, timeout=120).json()
    pin = next((a for a in mapdata["applications"] if a["id"] == app_id), None)
    if pin is None:
        fail("application did not appear on the map")
    line("Marker", f"{pin['application_number']} at bus {pin['pv_bus']}")
    line("Risk colour", pin["engineering_risk"])
    line("Voltage at marker", f"{pin['pv_voltage_pu']:.5f}", "pu")
    line("Placement", mapdata["assets"][0]["geometry_source"])
    line("Liveness", mapdata["liveness"][:60] + "…")

    # ============================================================
    step("DISCOM reviews and approves")
    packet = httpx.get(f"{BASE}/api/discom/applications/{app_id}", headers=DISCOM, timeout=60).json()
    line("Reviewer sees", packet["application"]["application_number"])
    line("Stored verdict", packet["assessment"]["engineering_risk"])
    line("Stored voltage rise", f"{float(packet['simulation']['voltage_rise_pu']):.5f}", "pu")
    line("History entries", len(packet["history"]))

    r = httpx.post(
        f"{BASE}/api/discom/applications/{app_id}/decision",
        headers=DISCOM,
        json={"decision": "APPROVED", "notes": "Within hosting capacity; no violation."},
        timeout=60,
    )
    decision = r.json()
    line("Decision", decision["decision"])
    line("Override of an objection", decision["override_of_engineering_objection"])

    # ============================================================
    step("Citizen sees approved installers")
    vendor_email_hint = "Demo E2E Installers"
    r = httpx.post(
        f"{BASE}/api/vendors/register",
        headers=VENDOR,
        json={
            "business_name": vendor_email_hint,
            "representative_name": "Demo Installer Rep",
            "district": CUSTOMER["district"],
            "state": CUSTOMER["state"],
            "latitude": 12.9800,
            "longitude": 77.6100,
            "service_areas": [CUSTOMER["district"]],
            "years_experience": 9,
            "installation_capacity_kw": 500,
        },
        timeout=60,
    )
    vendor_id = r.json()["vendor"]["id"]
    line("Vendor registers as", r.json()["vendor"]["status"])

    before = httpx.get(f"{BASE}/api/applications/{app_id}/vendors", headers=CITIZEN, timeout=60).json()
    visible_before = any(v["id"] == vendor_id for v in before["vendors"])
    line("Visible to customer before approval", visible_before)

    httpx.post(
        f"{BASE}/api/discom/vendors/{vendor_id}/review",
        headers=DISCOM,
        json={"status": "APPROVED", "reason": "Documents verified."},
        timeout=60,
    )
    after = httpx.get(f"{BASE}/api/applications/{app_id}/vendors", headers=CITIZEN, timeout=60).json()
    listed = next((v for v in after["vendors"] if v["id"] == vendor_id), None)
    if listed is None:
        fail("approved vendor did not become visible")
    line("Visible after DISCOM approval", True)
    line("Installers offered", after["total"])
    line("Nearest", f"{listed['business_name']} — {listed['distance']['distance_km']:.2f} km")
    line("Distance basis", f"{listed['distance']['method']} (is_route={listed['distance']['is_route']})")

    # ============================================================
    step("Citizen books a site visit; the vendor receives the lead")
    when = (datetime.now(timezone.utc) + timedelta(days=5)).replace(microsecond=0)
    r = httpx.post(
        f"{BASE}/api/applications/{app_id}/select-vendor",
        headers=CITIZEN,
        json={
            "vendor_id": vendor_id,
            "scheduled_at": when.isoformat(),
            "notes": "Weekend morning preferred.",
        },
        timeout=60,
    )
    if r.status_code != 201:
        fail(f"booking failed: {r.status_code} {r.text[:200]}")
    appointment_id = r.json()["appointment"]["id"]
    line("Site visit requested", when.strftime("%Y-%m-%d %H:%M UTC"))

    leads = httpx.get(f"{BASE}/api/vendor/leads", headers=VENDOR, timeout=60).json()
    lead = next(l for l in leads if l["id"] == appointment_id)
    line("Vendor sees lead for", lead["application"]["application_number"])
    line("Customer address released", lead["application"]["address_line"])
    line("Requested capacity", f"{float(lead['application']['new_pv_kw']):.1f}", "kW")

    r = httpx.post(
        f"{BASE}/api/vendor/leads/{appointment_id}/respond",
        headers=VENDOR,
        json={"accept": True, "note": "Confirmed."},
        timeout=60,
    )
    installation_id = r.json()["installation"]["id"]
    line("Vendor accepts", r.json()["accepted"])
    line("Installation opened", r.json()["installation"]["status"])

    # ============================================================
    step("Vendor carries out the installation")
    for status in ["SITE_VISIT", "SCHEDULED", "IN_PROGRESS", "COMPLETED", "VERIFICATION_PENDING"]:
        r = httpx.post(
            f"{BASE}/api/vendor/installations/{installation_id}/status",
            headers=VENDOR,
            json={"status": status, "installed_capacity_kw": CUSTOMER["new_pv_kw"]},
            timeout=60,
        )
        if r.status_code != 200:
            fail(f"could not set {status}: {r.text[:120]}")
        line(f"  {status}", "recorded")

    r = httpx.post(
        f"{BASE}/api/vendor/installations/{installation_id}/status",
        headers=VENDOR,
        json={"status": "VERIFIED"},
        timeout=60,
    )
    line("Vendor attempts VERIFIED", f"refused ({r.status_code}) — only a DISCOM may verify")
    if r.status_code != 403:
        fail("a vendor was able to self-verify; this must never happen")

    # ============================================================
    step("DISCOM verifies the installation")
    r = httpx.post(
        f"{BASE}/api/discom/installations/{installation_id}/verify",
        headers=DISCOM,
        json={"notes": "Inspected on site; meter commissioned."},
        timeout=60,
    )
    verified = r.json()["installation"]
    line("Status", verified["status"])
    line("DISCOM verified", verified["discom_verified"])
    line("Installed capacity", f"{float(verified['installed_capacity_kw']):.1f}", "kW")

    # ============================================================
    step("PM Surya Ghar — indicative CFA")
    cfa = httpx.get(
        f"{BASE}/api/scheme/estimate/application/{app_id}", headers=CITIZEN, timeout=60
    ).json()
    est = cfa["estimate"]
    line("Requested capacity", f"{cfa['requested_capacity_kw']:.1f}", "kW")
    line("Indicative subsidy", f"{est['currency']} {est['amount']:,.0f}")
    for b in est["breakdown"]:
        line(f"  {b['from_kw']}–{b['to_kw']} kW", f"{b['kw']:g} kW x {b['rate_per_kw']:,.0f} = {b['amount']:,.0f}")
    line("Indicative", est["indicative"])
    line("Configuration verified", est["configuration_verified"])
    if not est["configuration_verified"]:
        line("  WARNING", "subsidy rates are unverified placeholders")

    # ============================================================
    print(f"\n{'=' * 74}")
    print("  DEMO COMPLETE")
    print(f"{'=' * 74}")
    line("Application", application["application_number"])
    final = (svc.table("solar_applications").select("status").eq("id", app_id).execute()).data[0]
    line("Application status", final["status"])
    line("Installation", verified["status"])
    line("Connection point", f"bus {CUSTOMER['pv_bus']} ({bus['transformer_association']})")
    line("Engineering verdict", eng["engineering_risk"])
    line("Measured voltage rise", f"{m['voltage_rise_pu']:.5f} pu")
    print()
    print("  Every electrical figure above came from a power flow run during this")
    print("  demonstration. Nothing was hardcoded or replayed from a fixture.")
    print(f"\n  To remove the demo data:  python {Path(__file__).name} --reset")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
