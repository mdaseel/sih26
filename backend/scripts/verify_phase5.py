"""Phase 5 acceptance check — GIS map and hosting capacity.

The claims worth testing here are about honesty as much as correctness:

  * the geometry that IS real (distance along the feeder) really is real
  * the geometry that is NOT real is labelled as such everywhere
  * hosting capacity is simulated, and agrees with known constrained cases
  * map pins are scoped by Row Level Security, not by frontend filtering
  * nothing claims to be live SCADA
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from app.models.enums import RiskLevel, UserRole  # noqa: E402
from app.services.grid_assets import get_grid_asset_service  # noqa: E402
from app.services.hosting_capacity import (  # noqa: E402
    SEARCH_CEILING_KW,
    get_hosting_capacity_service,
)
from app.services.power_flow import PowerFlowError, get_power_flow_service  # noqa: E402
from app.services.risk_assessment import get_risk_service  # noqa: E402
from app.services.topology import get_topology_service  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


topo = get_topology_service()
grid = get_grid_asset_service()
hc = get_hosting_capacity_service()
pf = get_power_flow_service()
risk = get_risk_service()

# ============================================================
print("\nA. Distances are real; placement is not")
# ============================================================
distances = topo.distances_km()
check("every bus has a route distance", len(distances) == 114, f"{len(distances)} buses")
check("the source is at zero distance", distances["700"] == 0.0, str(distances["700"]))

# The distances must match the feature the model was trained on.
mismatches = []
for bus_id in grid.eligible_bus_ids():
    feature = grid.get(bus_id).feeder_distance_km
    computed = distances.get(bus_id)
    if computed is None or abs(computed - feature) > 1e-3:
        mismatches.append((bus_id, feature, computed))
check(
    "distances agree with electrical_features.csv",
    not mismatches,
    f"{len(mismatches)} mismatches" if mismatches else "all 71 buses match feeder_distance_km",
)

geo = topo.geo_positions(12.9716, 77.5946)
check("every bus is placed", len(geo) == len(distances), f"{len(geo)} placed")
check(
    "placement is deterministic",
    topo.geo_positions(12.9716, 77.5946) == geo,
    "same anchor gives the same map",
)

# Longitude offset should track real distance: bus 734 is 17 km out, 620 is 7.
far, near = geo["734"], geo["620"]
check(
    "a more distant bus is placed further east",
    far["longitude"] > near["longitude"] and far["distance_km"] > near["distance_km"],
    f"734 at {far['distance_km']} km, 620 at {near['distance_km']} km",
)

# ============================================================
print("\nB. Hosting capacity is simulated, not estimated")
# ============================================================
cap734 = hc.capacity_for("734")
check(
    "bus 734 capacity is below its known CONSTRAINED size (66 kW)",
    cap734.hosting_capacity_kw < 66,
    f"{cap734.hosting_capacity_kw:.0f} kW, limited by {cap734.limiting_constraint}",
)
cap6231 = hc.capacity_for("6231")
check(
    "bus 6231 capacity is below its known CONSTRAINED size (53 kW)",
    cap6231.hosting_capacity_kw < 53,
    f"{cap6231.hosting_capacity_kw:.0f} kW, limited by {cap6231.limiting_constraint}",
)
check(
    "method is recorded on the result",
    "bisection" in cap734.method and cap734.power_flows_run > 5,
    f"{cap734.power_flows_run} power flows",
)

# The capacity itself must be acceptable, and one step past it must not be.
verdict_at = risk.evaluate(pf.simulate("734", 0, cap734.hosting_capacity_kw)).engineering_risk
check(
    "the reported capacity is itself acceptable",
    verdict_at is not RiskLevel.CONSTRAINED,
    f"verdict at {cap734.hosting_capacity_kw:.0f} kW is {verdict_at.value}",
)
try:
    over = risk.evaluate(
        pf.simulate("734", 0, cap734.hosting_capacity_kw + 2)
    ).engineering_risk
    over_is_bad = over is RiskLevel.CONSTRAINED
except PowerFlowError:
    over_is_bad = True
check(
    "just above the capacity is constrained",
    over_is_bad,
    "the boundary is where the simulation says it is",
)

check(
    "capacity never silently exceeds the search ceiling",
    cap734.hosting_capacity_kw <= SEARCH_CEILING_KW,
)

mono = hc.verify_monotonic("734", steps=8)
check(
    "the monotonicity assumption bisection relies on holds",
    mono["monotonic"],
    f"first CONSTRAINED at {mono['first_constrained_kw']} kW",
)

# ============================================================
print("\nC. Non-convergence is an engineering answer, not a crash")
# ============================================================
try:
    pf.simulate("734", 0, 100000)
    check("an absurd injection is rejected cleanly", False, "it converged, unexpectedly")
except PowerFlowError as exc:
    check("an absurd injection raises PowerFlowError", True, str(exc)[:70])
except Exception as exc:  # noqa: BLE001
    check("an absurd injection raises PowerFlowError", False, f"raised {type(exc).__name__}")

check(
    "a failed solve is never counted as spare capacity",
    hc._is_constrained("734", 0, 100000),  # noqa: SLF001 - testing the guard directly
    "non-convergence is treated as constrained",
)

# ============================================================
print("\nD. Map API")
# ============================================================
temp_user_id: str | None = None
try:
    import uuid

    from fastapi.testclient import TestClient

    from app.api.deps import CurrentUser, get_current_user
    from app.core.supabase_client import get_anon_client, get_service_client
    from app.main import app

    # /api/map reads applications through the caller's own token so that RLS
    # decides which pins appear. A stub token cannot exercise that, so a real
    # (temporary) user is created and removed at the end.
    svc = get_service_client()
    email = f"solargrid-map-{uuid.uuid4().hex[:8]}@example.com"
    password = f"Verify!{uuid.uuid4().hex[:12]}"
    created = svc.auth.admin.create_user(
        {"email": email, "password": password, "email_confirm": True}
    )
    temp_user_id = created.user.id
    token = (
        get_anon_client()
        .auth.sign_in_with_password({"email": email, "password": password})
        .session.access_token
    )

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=temp_user_id,
        email=email,
        role=UserRole.CITIZEN,
        access_token=token,
    )
    client = TestClient(app)

    r = client.get("/api/map")
    body = r.json()
    check("GET /api/map", r.status_code == 200, f"{len(body.get('assets', []))} assets")

    buses = [a for a in body["assets"] if a["asset_type"] == "BUS"]
    placed = [b for b in buses if b["latitude"] is not None]
    check("all buses carry coordinates", len(placed) == 114, f"{len(placed)}/114")
    check(
        "coordinates are labelled synthetic",
        all(b["geometry_source"] == "SYNTHETIC_LAYOUT" for b in placed),
    )
    with_cap = [
        b for b in buses if (b.get("attributes") or {}).get("hosting_capacity_kw") is not None
    ]
    check("hosting capacity stored for the 71 eligible buses", len(with_cap) == 71, str(len(with_cap)))

    check(
        "the response states what is real and what is not",
        "Distances along the feeder are real" in body["anchor_note"]
        and "no geographic coordinates" in body["anchor_note"],
    )
    check(
        "the response does not claim live SCADA",
        "not a live SCADA feed" in body["liveness"]
        and "Real-time-like" in body["liveness"],
        body["liveness"][:60],
    )
    check("provenance is declared", "Synthetic" in body["data_class"], body["data_class"])

    r = client.get("/api/grid/hosting-capacity")
    check(
        "GET /api/grid/hosting-capacity",
        r.status_code == 200 and r.json()["count"] == 71,
        f"{r.json().get('count')} buses",
    )
    every_has_reason = all(
        b["limiting_constraint"] and b["limiting_reason"] for b in r.json()["buses"]
    )
    check("every capacity says what limits it", every_has_reason)

    r = client.get("/api/grid/hosting-capacity/734")
    check(
        "GET /api/grid/hosting-capacity/{bus}",
        r.status_code == 200 and r.json()["hosting_capacity_kw"] < 66,
        f"{r.json().get('hosting_capacity_kw')} kW",
    )

    r = client.get("/api/grid/hosting-capacity/701")
    check("an ineligible MV bus is rejected", r.status_code == 422)

    r = client.get("/api/grid/hosting-capacity/99999")
    check("an unknown bus is rejected", r.status_code == 404)

    # A brand-new user owns no applications, so RLS must show them no pins even
    # though other users' applications exist in the same table.
    r = client.get("/api/map")
    total_apps = (
        len((svc.table("solar_applications").select("id").execute()).data or [])
    )
    check(
        "map pins are scoped by RLS, not filtered in the frontend",
        r.json()["applications"] == [] and total_apps > 0,
        f"new user sees 0 of {total_apps} applications in the table",
    )

    app.dependency_overrides.clear()
    r = client.get("/api/map")
    check("unauthenticated /api/map refused", r.status_code in (401, 403, 503), f"status {r.status_code}")
except Exception as exc:  # noqa: BLE001
    check("map API", False, repr(exc)[:200])
finally:
    if temp_user_id:
        try:
            from app.core.supabase_client import get_service_client

            get_service_client().auth.admin.delete_user(temp_user_id)
        except Exception:  # noqa: BLE001
            pass

# ============================================================
print("\nE. Layer values come from the power flow")
# ============================================================
try:
    from app.db.service import db

    rows = (
        db.as_service()
        .table("grid_assets")
        .select("asset_code,attributes")
        .eq("asset_type", "TRANSFORMER")
        .execute()
    ).data or []
    with_loading = [r for r in rows if (r.get("attributes") or {}).get("base_loading_pct") is not None]
    check(
        "transformers carry a measured base loading",
        len(with_loading) == 30,
        f"{len(with_loading)}/30",
    )

    t7 = next((r for r in rows if r["asset_code"] == "T7"), None)
    check(
        "T7 base loading matches the validated 92.8%",
        t7 is not None and abs(t7["attributes"]["base_loading_pct"] - 92.8) < 0.2,
        f"{t7['attributes']['base_loading_pct']}%" if t7 else "T7 missing",
    )
except Exception as exc:  # noqa: BLE001
    check("layer values", False, repr(exc)[:160])

# ============================================================
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 5 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
