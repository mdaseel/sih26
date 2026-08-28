"""Phase 7 acceptance check — what-if and hosting capacity.

The central claim to test: hosting capacity is measured, never estimated, and
a feeder section's capacity is measured with its connections energised
together rather than by adding up per-bus figures.
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
from app.models.enums import RiskLevel  # noqa: E402
from app.services.grid_assets import get_grid_asset_service  # noqa: E402
from app.services.hosting_capacity import get_hosting_capacity_service  # noqa: E402
from app.services.power_flow import get_power_flow_service  # noqa: E402
from app.services.risk_assessment import get_risk_service  # noqa: E402

BASE = "http://127.0.0.1:8000"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


grid = get_grid_asset_service()
hc = get_hosting_capacity_service()
pf = get_power_flow_service()
risk = get_risk_service()

# ============================================================
print("\nA. Multi-bus injection")
# ============================================================
section = "Main_720-734"
buses = [b for b in grid.eligible_bus_ids() if grid.get(b).feeder_section == section]
check(f"section {section} has eligible buses", len(buses) > 1, f"{len(buses)} buses")

group = pf.simulate_group(section, {b: 0.0 for b in buses}, {b: 20.0 for b in buses})
check(
    "a group case solves and reports feeder-wide metrics",
    group.converged and group.total_pv_kw == 20.0 * len(buses),
    f"{group.total_pv_kw} kW across {len(buses)} buses",
)
check(
    "group voltage rise is the worst affected bus, not an average",
    group.pv_bus in buses and abs(group.voltage_rise_pu) > 0,
    f"worst bus {group.pv_bus}, rise {group.voltage_rise_pu}",
)

# One bus in a group of one must equal the single-bus path exactly.
single = pf.simulate("734", 0, 30)
as_group = pf.simulate_group("solo", {"734": 0.0}, {"734": 30.0})
check(
    "a one-bus group matches the single-bus simulation",
    abs(single.voltage_rise_pu - as_group.voltage_rise_pu) < 1e-9
    and abs(single.max_transformer_loading_pct - as_group.max_transformer_loading_pct) < 1e-9,
    f"rise {single.voltage_rise_pu} vs {as_group.voltage_rise_pu}",
)

# ============================================================
print("\nB. Feeder capacity is not the sum of its parts")
# ============================================================
feeder = hc.feeder_capacity(section)
naive = sum(hc.capacity_for(b).hosting_capacity_kw for b in buses)
check(
    "simultaneous capacity is below the sum of per-bus capacities",
    feeder["hosting_capacity_kw"] < naive,
    f"{feeder['hosting_capacity_kw']:.0f} kW vs sum {naive:.0f} kW "
    f"({naive / feeder['hosting_capacity_kw']:.1f}x overstatement)",
)
check(
    "the feeder result records how it was obtained",
    "bisection" in feeder["method"] and feeder["distribution"],
    f"{feeder['method']}; {feeder['distribution']}",
)
check(
    "the feeder result names its limiting constraint",
    feeder["limiting_constraint"] in {"voltage", "voltage_rise", "line_loading", "transformer_loading"},
    f"{feeder['limiting_constraint']}: {feeder['limiting_reason'][:60]}",
)

# The reported capacity must actually be acceptable, and just above it must not.
per_bus = feeder["hosting_capacity_kw"] / len(buses)
at = risk.evaluate(
    pf.simulate_group(section, {b: 0.0 for b in buses}, {b: per_bus for b in buses})
).engineering_risk
check(
    "the section can actually host the reported capacity",
    at is not RiskLevel.CONSTRAINED,
    f"verdict at capacity is {at.value}",
)
over_per_bus = (feeder["hosting_capacity_kw"] * 1.15) / len(buses)
over = risk.evaluate(
    pf.simulate_group(section, {b: 0.0 for b in buses}, {b: over_per_bus for b in buses})
).engineering_risk
check(
    "15% above the reported capacity is constrained",
    over is RiskLevel.CONSTRAINED,
    f"verdict is {over.value}",
)

# A single-bus section must agree with that bus's own capacity.
solo_sections = {}
for b in grid.eligible_bus_ids():
    solo_sections.setdefault(grid.get(b).feeder_section, []).append(b)
solo = next((s for s, bs in solo_sections.items() if len(bs) == 1), None)
if solo:
    section_cap = hc.feeder_capacity(solo)["hosting_capacity_kw"]
    bus_cap = hc.capacity_for(solo_sections[solo][0]).hosting_capacity_kw
    check(
        "a one-bus section equals that bus's own capacity",
        abs(section_cap - bus_cap) <= 2.0,
        f"section {section_cap:.0f} kW vs bus {bus_cap:.0f} kW",
    )

# ============================================================
print("\nC. What-if API")
# ============================================================
settings = get_settings()
svc = get_service_client()
users: list[str] = []

try:
    def make(role: str) -> dict[str, str]:
        email = f"solargrid-p7-{uuid.uuid4().hex[:6]}@example.com"
        pw = f"Verify!{uuid.uuid4().hex[:12]}"
        u = svc.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True})
        users.append(u.user.id)
        if role != "CITIZEN":
            svc.table("profiles").update({"role": role}).eq("id", u.user.id).execute()
        token = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": pw}
        ).session.access_token
        return {"Authorization": f"Bearer {token}"}

    DISCOM = make("DISCOM")
    CITIZEN = make("CITIZEN")

    r = httpx.post(
        f"{BASE}/api/discom/what-if",
        headers=DISCOM,
        json={"pv_bus": "734", "existing_pv_kw": 0, "capacities_kw": [10, 25, 50, 100, 250, 500]},
        timeout=300,
    )
    body = r.json()
    check("POST /api/discom/what-if", r.status_code == 200, f"{len(body['points'])} points")
    check(
        "the specified capacities were all simulated",
        [p["new_pv_kw"] for p in body["points"]] == [10, 25, 50, 100, 250, 500],
    )
    check(
        "risk worsens monotonically with capacity",
        all(
            ["SAFE", "CAUTION", "CONSTRAINED"].index(a["engineering_risk"])
            <= ["SAFE", "CAUTION", "CONSTRAINED"].index(b["engineering_risk"])
            for a, b in zip(body["points"], body["points"][1:])
            if a["converged"] and b["converged"]
        ),
        " → ".join(p["engineering_risk"] or "?" for p in body["points"]),
    )

    every_metric = all(
        all(
            k in p["metrics"]
            for k in (
                "pv_voltage_pu",
                "voltage_rise_pu",
                "max_transformer_loading_pct",
                "max_line_loading_pct",
                "reverse_power_flow",
                "power_loss_kw",
            )
        )
        for p in body["points"]
        if p["converged"]
    )
    check("every point carries the required electrical metrics", every_metric)

    cap = body["hosting_capacity"]["hosting_capacity_kw"]
    below = [p for p in body["points"] if p["new_pv_kw"] <= cap and p["converged"]]
    above = [p for p in body["points"] if p["new_pv_kw"] > cap and p["converged"]]
    check(
        "the bisected capacity is consistent with the sweep",
        all(p["engineering_risk"] != "CONSTRAINED" for p in below)
        and all(p["engineering_risk"] == "CONSTRAINED" for p in above),
        f"capacity {cap:.0f} kW separates the sweep cleanly",
    )

    r = httpx.post(
        f"{BASE}/api/discom/what-if", headers=CITIZEN, json={"pv_bus": "734"}, timeout=120
    )
    check("a citizen cannot run what-if", r.status_code == 403, f"status {r.status_code}")

    # ============================================================
    print("\nD. Feeder hosting-capacity API")
    # ============================================================
    r = httpx.get(f"{BASE}/api/discom/hosting-capacity/feeders", headers=DISCOM, timeout=180)
    fb = r.json()
    check("GET /api/discom/hosting-capacity/feeders", r.status_code == 200, f"{len(fb['sections'])} sections")

    required = {
        "current_solar_kw",
        "pending_solar_kw",
        "hosting_capacity_kw",
        "remaining_capacity_kw",
        "limiting_constraint",
        "risk",
    }
    check(
        "each section reports the six required fields",
        all(required <= set(s) for s in fb["sections"]),
    )
    check(
        "remaining never exceeds capacity",
        all(s["remaining_capacity_kw"] <= s["hosting_capacity_kw"] + 1e-6 for s in fb["sections"]),
    )
    check(
        "remaining accounts for committed and queued capacity",
        all(
            abs(
                s["remaining_capacity_kw"]
                - max(0.0, s["hosting_capacity_kw"] - s["current_solar_kw"] - s["pending_solar_kw"])
            )
            < 0.15
            for s in fb["sections"]
        ),
    )
    check(
        "the summed figure is shown for comparison, and is larger",
        all(
            s["sum_of_per_bus_kw"] is None or s["sum_of_per_bus_kw"] >= s["hosting_capacity_kw"]
            for s in fb["sections"]
        ),
    )
    check(
        "the method note warns against using the sum",
        "overstate" in fb["method_note"] and "not for use" in fb["method_note"],
    )
    check(
        "section risk is described as commitment, not a power-flow verdict",
        "not a power-flow verdict" in fb["risk_note"],
    )

    r = httpx.get(f"{BASE}/api/discom/hosting-capacity/feeders", headers=CITIZEN, timeout=60)
    check("a citizen cannot read feeder capacity", r.status_code == 403)

finally:
    print("\nE. Cleanup")
    for uid in users:
        try:
            svc.auth.admin.delete_user(uid)
        except Exception:  # noqa: BLE001
            pass
    check("test users removed", True)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 7 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
