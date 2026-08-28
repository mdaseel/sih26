"""Phase 2 acceptance check — backend grid intelligence.

The important test is the replay: existing dataset rows are pushed back through
the new services, and the recomputed label must equal the label stored in the
dataset. If the port of the threshold logic had drifted at all, the model's
training labels would no longer describe what the application computes.

Auth is stubbed via FastAPI's dependency_overrides. That is a test seam, not a
production bypass — the real dependency still requires a valid Supabase JWT.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import pandas as pd  # noqa: E402

from app.core import paths  # noqa: E402
from app.models.enums import RiskLevel, UserRole  # noqa: E402
from app.services.grid_assets import (  # noqa: E402
    IneligibleBusError,
    UnknownBusError,
    get_grid_asset_service,
)
from app.services.ml_prediction import get_ml_service  # noqa: E402
from app.services.power_flow import get_power_flow_service  # noqa: E402
from app.services.risk_assessment import get_risk_service  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


grid = get_grid_asset_service()
ml = get_ml_service()
pf = get_power_flow_service()
risk = get_risk_service()

# ============================================================
print("\nA. GridAssetService")
# ============================================================
check("71 PV-eligible buses", len(grid.eligible_bus_ids()) == 71, str(len(grid.eligible_bus_ids())))
b734 = grid.get("734")
check(
    "bus 734 attributes match electrical_features.csv",
    abs(b734.upstream_z_ohm - 14.51) < 0.01 and abs(b734.feeder_distance_km - 17.08) < 0.01,
    f"z={b734.upstream_z_ohm} d={b734.feeder_distance_km} km",
)
try:
    grid.get("701")  # a real MV bus, but not a rooftop connection point
    check("MV bus 701 rejected as ineligible", False, "no error raised")
except IneligibleBusError:
    check("MV bus 701 rejected as ineligible", True)
except UnknownBusError:
    check("MV bus 701 rejected as ineligible", False, "reported as unknown instead")
try:
    grid.get("99999")
    check("unknown bus rejected", False, "no error raised")
except UnknownBusError:
    check("unknown bus rejected", True)

t = grid.thresholds()
check(
    "thresholds read from scenario_config.json",
    t["voltage_rise_hard_pu"] == 0.05
    and t["voltage_hard_high_pu"] == 1.05
    and t["transformer_loading_caution_pct"] == 95.0,
    f"rise_hard={t['voltage_rise_hard_pu']} v_high={t['voltage_hard_high_pu']}",
)

# ============================================================
print("\nB. MLPredictionService — feature assembly")
# ============================================================
feats = ml.build_features(b734, 0, 66)
check("18 features assembled", len(feats) == 18, str(len(feats)))
check("pv_bus cast to int for the fitted encoder", isinstance(feats["pv_bus"], int))
check(
    "ratios match enrich_features.py",
    abs(feats["pv_to_transformer_ratio"] - 66 / b734.transformer_sn_kva) < 1e-12
    and abs(feats["new_pv_to_transformer_ratio"] - 66 / b734.transformer_sn_kva) < 1e-12,
)

# Zero-load penetration artifact must be preserved, not "fixed".
b6231 = grid.get("6231")
f6231 = ml.build_features(b6231, 0, 53)
check(
    "zero-load penetration artifact preserved (total/1.0)",
    b6231.existing_load_kw == 0 and f6231["pv_penetration_ratio"] == 53.0,
    f"load={b6231.existing_load_kw} penetration={f6231['pv_penetration_ratio']}",
)

# Feature assembly from scratch must equal the stored dataset row.
df = pd.read_csv(paths.DATASET_CURRENT, dtype={"pv_bus": str})
stored = df[(df.pv_bus == "734") & (df.new_pv_kw == 66) & (df.existing_pv_kw == 0)].iloc[0]
mismatched = [
    f
    for f in ml.feature_names
    if f != "pv_bus"
    and isinstance(feats[f], (int, float))
    and abs(float(feats[f]) - float(stored[f])) > 1e-6
]
check(
    "assembled features equal the stored dataset row",
    not mismatched,
    f"mismatches: {mismatched}" if mismatched else "all numeric features identical",
)

# ============================================================
print("\nC. Known scenarios — the historical false-SAFE cases")
# ============================================================
for bus, new_kw in [("734", 66), ("6231", 53)]:
    pred = ml.predict(bus, 0, new_kw)
    metrics = pf.simulate(bus, 0, new_kw)
    verdict = risk.evaluate(metrics)
    check(
        f"bus {bus} @{new_kw}kW -> engineering CONSTRAINED",
        verdict.engineering_risk is RiskLevel.CONSTRAINED,
        f"{verdict.constraint_type.value}: {verdict.constraint_reason}",
    )
    check(
        f"bus {bus} @{new_kw}kW -> ML also flags CONSTRAINED",
        pred.prediction is RiskLevel.CONSTRAINED,
        f"P(CONSTRAINED)={pred.constrained_probability:.4f}",
    )

# ============================================================
print("\nD. Label replay against the existing dataset")
# ============================================================
sample = df.sample(120, random_state=42)
matched = 0
mismatches = []
for _, row in sample.iterrows():
    m = pf.simulate(row.pv_bus, float(row.existing_pv_kw), float(row.new_pv_kw))
    v = risk.evaluate(m)
    if v.engineering_risk.value == row.label:
        matched += 1
    else:
        mismatches.append(
            f"bus {row.pv_bus} ex={row.existing_pv_kw} new={row.new_pv_kw}: "
            f"stored={row.label} computed={v.engineering_risk.value}"
        )
check(
    f"recomputed labels match stored labels ({matched}/{len(sample)})",
    matched == len(sample),
    "; ".join(mismatches[:3]) if mismatches else "exact reproduction",
)

# Numeric agreement, not just the label.
worst_delta = 0.0
for _, row in sample.head(40).iterrows():
    m = pf.simulate(row.pv_bus, float(row.existing_pv_kw), float(row.new_pv_kw))
    worst_delta = max(worst_delta, abs(m.voltage_rise_pu - float(row.delta_pv_bus_voltage_pu)))
check("voltage rise matches stored delta", worst_delta < 1e-4, f"max deviation {worst_delta:.2e} pu")

# ============================================================
print("\nE. All three risk classes are reachable")
# ============================================================
seen: dict[str, str] = {}
for bus, kw in [("6231", 5), ("621", 100), ("734", 250), ("620", 15), ("734", 66)]:
    v = risk.evaluate(pf.simulate(bus, 0, kw))
    seen.setdefault(v.engineering_risk.value, f"bus {bus} @{kw}kW")
check(
    "SAFE / CAUTION / CONSTRAINED all produced",
    set(seen) == {"SAFE", "CAUTION", "CONSTRAINED"},
    str(seen),
)

# ============================================================
print("\nF. API layer")
# ============================================================
try:
    from fastapi.testclient import TestClient

    from app.api.deps import CurrentUser, get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="00000000-0000-0000-0000-000000000001",
        email="verify@example.com",
        role=UserRole.CITIZEN,
        access_token="test-token",
    )
    client = TestClient(app)

    r = client.get("/health")
    check("GET /health", r.status_code == 200, str(r.json()))

    r = client.get("/api/grid/buses")
    check("GET /api/grid/buses returns 71", r.status_code == 200 and len(r.json()) == 71)

    r = client.get("/api/grid/summary")
    body = r.json()
    check(
        "GET /api/grid/summary reports provenance",
        r.status_code == 200 and "Synthetic" in body["data_class"],
        body["data_class"],
    )

    r = client.post("/api/assess", json={"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": 66})
    body = r.json()
    check(
        "POST /api/assess -> CONSTRAINED",
        r.status_code == 200 and body["engineering"]["engineering_risk"] == "CONSTRAINED",
        f"ml={body['ml']['prediction']} eng={body['engineering']['engineering_risk']}",
    )
    check(
        "response carries full engineering metrics",
        all(
            k in body["metrics"]
            for k in (
                "base_voltage_pu",
                "pv_voltage_pu",
                "voltage_rise_pu",
                "feeder_min_voltage_pu",
                "feeder_max_voltage_pu",
                "max_line_loading_pct",
                "max_transformer_loading_pct",
                "reverse_power_flow",
                "power_loss_kw",
                "solar_penetration_pct",
            )
        ),
    )
    check("power flow named as the authority", body["authority"] == "power_flow")
    check("result not persisted without a database", body["persisted"] is False)

    r = client.post("/api/assess", json={"pv_bus": "701", "existing_pv_kw": 0, "new_pv_kw": 10})
    check("ineligible MV bus rejected with 422", r.status_code == 422, r.json().get("detail", ""))

    r = client.post("/api/assess", json={"pv_bus": "99999", "existing_pv_kw": 0, "new_pv_kw": 10})
    check("unknown bus rejected with 404", r.status_code == 404)

    r = client.post("/api/assess", json={"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": -5})
    check("negative capacity rejected with 422", r.status_code == 422)

    r = client.post("/api/assess", json={"pv_bus": "abc", "existing_pv_kw": 0, "new_pv_kw": 10})
    check("non-numeric bus rejected with 422", r.status_code == 422)

    # Unauthenticated access must still fail once the override is removed.
    app.dependency_overrides.clear()
    r = client.post("/api/assess", json={"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": 66})
    check(
        "unauthenticated request refused",
        r.status_code in (401, 503),
        f"status {r.status_code}",
    )
except Exception as exc:  # noqa: BLE001
    check("API layer", False, repr(exc)[:200])

# ============================================================
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 2 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
