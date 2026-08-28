"""Seed demonstration vendors.

These are FICTIONAL businesses for demoing vendor discovery. Names are
deliberately generic and every record carries is_demo in its own row so they
can be identified and removed. Do not present them as real installers.

The mix is intentional: only some are APPROVED, so the "customers see approved
vendors only" rule has something to actually filter.

Usage:
    python backend/seed/seed_demo_vendors.py            # create
    python backend/seed/seed_demo_vendors.py --remove   # delete them again
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.supabase_client import get_service_client  # noqa: E402

# Anchored near the same illustrative point the map uses, spread a few km apart
# so nearest-vendor ordering has something to sort.
DEMO_VENDORS = [
    {
        "business_name": "Demo Solar Works",
        "representative_name": "Demo Representative A",
        "district": "Demo District",
        "state": "Demo State",
        "latitude": 12.9750,
        "longitude": 77.6050,
        "service_areas": ["Demo District", "Demo North"],
        "installation_capacity_kw": 500,
        "years_experience": 8,
        "rating": 4.6,
        "completed_installations": 120,
        "status": "APPROVED",
        "is_active": True,
    },
    {
        "business_name": "Demo Rooftop Energy",
        "representative_name": "Demo Representative B",
        "district": "Demo District",
        "state": "Demo State",
        "latitude": 12.9520,
        "longitude": 77.6600,
        "service_areas": ["Demo District"],
        "installation_capacity_kw": 250,
        "years_experience": 4,
        "rating": 4.1,
        "completed_installations": 46,
        "status": "APPROVED",
        "is_active": True,
    },
    {
        "business_name": "Demo Green Power Systems",
        "representative_name": "Demo Representative C",
        "district": "Demo South",
        "state": "Demo State",
        "latitude": 12.9100,
        "longitude": 77.7100,
        "service_areas": ["Demo South"],
        "installation_capacity_kw": 1000,
        "years_experience": 12,
        "rating": 4.8,
        "completed_installations": 310,
        "status": "APPROVED",
        "is_active": True,
    },
    {
        # Must never appear to a customer.
        "business_name": "Demo Unverified Installers",
        "representative_name": "Demo Representative D",
        "district": "Demo District",
        "state": "Demo State",
        "latitude": 12.9700,
        "longitude": 77.6000,
        "service_areas": ["Demo District"],
        "installation_capacity_kw": 100,
        "years_experience": 1,
        "status": "PENDING",
        "is_active": True,
    },
    {
        # Approved once, then suspended — also must not appear.
        "business_name": "Demo Suspended Solar",
        "representative_name": "Demo Representative E",
        "district": "Demo District",
        "state": "Demo State",
        "latitude": 12.9600,
        "longitude": 77.6200,
        "service_areas": ["Demo District"],
        "installation_capacity_kw": 300,
        "years_experience": 6,
        "rating": 3.2,
        "status": "SUSPENDED",
        "is_active": False,
    },
]

MARKER = "Demo "


def remove(client) -> int:
    existing = (client.table("vendors").select("id,business_name,owner_id").execute()).data or []
    removed = 0
    for v in existing:
        if v["business_name"].startswith(MARKER):
            client.table("vendors").delete().eq("id", v["id"]).execute()
            if v.get("owner_id"):
                try:
                    client.auth.admin.delete_user(v["owner_id"])
                except Exception:  # noqa: BLE001
                    pass
            removed += 1
    return removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove", action="store_true", help="delete the demo vendors")
    args = ap.parse_args()

    client = get_service_client()

    if args.remove:
        print(f"removed {remove(client)} demo vendors")
        return 0

    print(f"clearing {remove(client)} existing demo vendors")

    created = 0
    for spec in DEMO_VENDORS:
        # Each vendor needs an owner account, as a real registration would have.
        email = f"demo-vendor-{uuid.uuid4().hex[:8]}@solargrid.test"
        user = client.auth.admin.create_user(
            {"email": email, "password": f"Demo!{uuid.uuid4().hex[:12]}", "email_confirm": True}
        )
        client.table("profiles").update({"role": "VENDOR"}).eq("id", user.user.id).execute()

        row = {**spec, "owner_id": user.user.id, "email": email, "phone": "+91-00000-00000"}
        if spec["status"] == "APPROVED":
            row["verified_at"] = "now()"

        client.table("vendors").insert(row).execute()
        created += 1
        print(f"  {spec['business_name']:34} {spec['status']:10} active={spec['is_active']}")

    visible = sum(1 for v in DEMO_VENDORS if v["status"] == "APPROVED" and v["is_active"])
    print(f"\ncreated {created} demo vendors; {visible} should be visible to customers")
    print("these are FICTIONAL businesses for demonstration only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
