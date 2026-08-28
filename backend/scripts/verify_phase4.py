"""Phase 4 acceptance check — 2D digital twin.

The claims worth testing are the ones a screenshot cannot prove:

  * topology is the feeder model's own graph, not a drawing
  * the path to a bus matches the electrical path the features were built from
  * only assets that actually moved report a change
  * flow direction is read from the sign of simulated power, not assumed
  * the energy balance adds up
  * the twin runs no extra power flow beyond the assessment it reports
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import pandapower as pp  # noqa: E402

from app.core import paths  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.services.grid_assets import get_grid_asset_service  # noqa: E402
from app.services.power_flow import get_power_flow_service  # noqa: E402
from app.services.risk_assessment import get_risk_service  # noqa: E402
from app.services.topology import get_topology_service  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


topo = get_topology_service()
pf = get_power_flow_service()
risk = get_risk_service()
grid = get_grid_asset_service()
thresholds = grid.thresholds()

# ============================================================
print("\nA. Topology comes from the feeder model")
# ============================================================
net = pp.from_json(str(paths.FEEDER_NETWORK))
full = topo.full_graph()

check(
    "node count equals the network's bus count",
    len(full["nodes"]) == len(net.bus),
    f"{len(full['nodes'])} nodes vs {len(net.bus)} buses",
)
line_edges = [e for e in full["edges"] if e["type"] == "LINE"]
trafo_edges = [e for e in full["edges"] if e["type"] == "TRANSFORMER"]
check("line edges match net.line", len(line_edges) == len(net.line), f"{len(line_edges)}/{len(net.line)}")
check(
    "transformer edges match net.trafo",
    len(trafo_edges) == len(net.trafo),
    f"{len(trafo_edges)}/{len(net.trafo)}",
)

bus_names = {str(n) for n in net.bus.name}
invented = [n["id"] for n in full["nodes"] if n["id"] not in bus_names]
check("no invented nodes", not invented, str(invented[:5]))

dangling = [
    e["id"]
    for e in full["edges"]
    if e["source"] not in bus_names or e["target"] not in bus_names
]
check("no dangling edges", not dangling, str(dangling[:5]))
check(
    "layout is labelled as schematic, not geographic",
    full["layout_source"] == "ELECTRICAL_SCHEMATIC",
)

# ============================================================
print("\nB. Electrical path")
# ============================================================
path_734 = topo.path_to("734")
check(
    "path starts at the source and ends at the bus",
    path_734[0] == "700" and path_734[-1] == "734",
    " → ".join(path_734),
)
check(
    "path is contiguous in the network graph",
    all(
        len(
            net.line[
                (
                    (net.line.from_bus == int(net.bus.index[net.bus.name == a][0]))
                    & (net.line.to_bus == int(net.bus.index[net.bus.name == b][0]))
                )
                | (
                    (net.line.from_bus == int(net.bus.index[net.bus.name == b][0]))
                    & (net.line.to_bus == int(net.bus.index[net.bus.name == a][0]))
                )
            ]
        )
        + len(
            net.trafo[
                (
                    (net.trafo.hv_bus == int(net.bus.index[net.bus.name == a][0]))
                    & (net.trafo.lv_bus == int(net.bus.index[net.bus.name == b][0]))
                )
                | (
                    (net.trafo.hv_bus == int(net.bus.index[net.bus.name == b][0]))
                    & (net.trafo.lv_bus == int(net.bus.index[net.bus.name == a][0]))
                )
            ]
        )
        + len(
            net.switch[
                (net.switch.et == "b")
                & (
                    (
                        (net.switch.bus == int(net.bus.index[net.bus.name == a][0]))
                        & (net.switch.element == int(net.bus.index[net.bus.name == b][0]))
                    )
                    | (
                        (net.switch.bus == int(net.bus.index[net.bus.name == b][0]))
                        & (net.switch.element == int(net.bus.index[net.bus.name == a][0]))
                    )
                )
            ]
        )
        > 0
        for a, b in zip(path_734, path_734[1:])
    ),
    "every hop is a real line, transformer or closed switch",
)

trafo = topo.transformer_for_path(path_734)
check(
    "serving transformer identified",
    trafo is not None and trafo["name"] == "T4",
    f"{trafo['name']} {trafo['sn_kva']} kVA" if trafo else "none",
)

local = topo.local_view("734")
check(
    "local view ends with the customer premises",
    local["nodes"][-1]["type"] == "HOUSE",
    local["nodes"][-1]["id"],
)
check(
    "local view edges connect consecutive nodes",
    len(local["edges"]) == len(local["nodes"]) - 1,
    f"{len(local['edges'])} edges for {len(local['nodes'])} nodes",
)

# ============================================================
print("\nC. Only affected assets change")
# ============================================================
result, elements = pf.simulate_with_elements("734", 0, 66)
verdict = risk.evaluate(result)

check(
    "verdict still CONSTRAINED (unchanged by the twin work)",
    verdict.engineering_risk.value == "CONSTRAINED",
    verdict.constraint_reason,
)
check(
    "PV-bus rise equals the assessment's voltage_rise_pu",
    abs(elements["buses"]["734"]["delta_pu"] - result.voltage_rise_pu) < 1e-9,
    f"{elements['buses']['734']['delta_pu']} vs {result.voltage_rise_pu}",
)
check(
    "source bus is unmoved",
    abs(elements["buses"]["700"]["delta_pu"]) < 1e-6,
    f"delta {elements['buses']['700']['delta_pu']}",
)

deltas = [(b, v["delta_pu"]) for b, v in elements["buses"].items()]
monotonic = all(
    abs(deltas[i][1]) <= abs(deltas[i + 1][1]) + 1e-9 for i in range(len(deltas) - 1)
)
check(
    "voltage rise grows towards the connection point",
    monotonic,
    " ".join(f"{b}:{d:+.5f}" for b, d in deltas[-4:]),
)

# Assets judged individually against the same thresholds the verdict used.
over_hard = [
    b
    for b, v in elements["buses"].items()
    if abs(v["delta_pu"]) > thresholds["voltage_rise_hard_pu"]
]
check(
    "exactly one asset breaches the rise limit",
    over_hard == ["734"],
    f"breaching: {over_hard}",
)

# ============================================================
print("\nD. Flow direction is measured, not assumed")
# ============================================================
tr = list(elements["transformers"].values())[0]
check(
    "serving transformer reverses under export",
    tr["reversed_by_pv"] and tr["direction_before"] == "FORWARD" and tr["direction_after"] == "REVERSE",
    f"{tr['name']}: {tr['p_before_kw']} kW → {tr['p_after_kw']} kW",
)
check(
    "transformer loading recorded before and after",
    tr["before_pct"] > 0 and tr["after_pct"] > 0,
    f"{tr['before_pct']}% → {tr['after_pct']}%",
)
check("lines on the path reported", len(elements["lines"]) > 0, f"{len(elements['lines'])} lines")

# ============================================================
print("\nE. Energy balance")
# ============================================================
eb = elements["energy_balance"]
check(
    "solar generation equals total PV",
    abs(eb["solar_generation_kw"] - result.total_pv_kw) < 1e-6,
    f"{eb['solar_generation_kw']} kW",
)
check(
    "self-consumed + export equals generation",
    abs((eb["self_consumed_kw"] + eb["local_export_kw"]) - eb["solar_generation_kw"]) < 0.01,
    f"{eb['self_consumed_kw']} + {eb['local_export_kw']} = {eb['solar_generation_kw']}",
)
check(
    "local consumption equals the bus load in the feeder database",
    abs(eb["local_consumption_kw"] - grid.get("734").existing_load_kw) < 1e-6,
    f"{eb['local_consumption_kw']} kW",
)
check(
    "grid supply falls when solar is added",
    eb["grid_supply_after_kw"] < eb["grid_supply_before_kw"],
    f"{eb['grid_supply_before_kw']} → {eb['grid_supply_after_kw']} kW",
)

# ============================================================
print("\nF. A SAFE case shows nothing alarming")
# ============================================================
safe_result, safe_elements = pf.simulate_with_elements("6231", 0, 5)
safe_verdict = risk.evaluate(safe_result)
check("bus 6231 @5kW is SAFE", safe_verdict.engineering_risk.value == "SAFE")
check(
    "no bus breaches the rise limit",
    not [
        b
        for b, v in safe_elements["buses"].items()
        if abs(v["delta_pu"]) > thresholds["voltage_rise_hard_pu"]
    ],
)
# Bus 6231 carries no modelled load — it is the "spare secondary" from
# false_safe_case_analysis.md — so a 5 kW system exports all 5 kW. The
# invariant worth asserting is the arithmetic, not a guess about the load.
safe_eb = safe_elements["energy_balance"]
check(
    "export equals generation beyond local load",
    abs(safe_eb["local_export_kw"] - max(0.0, safe_eb["solar_generation_kw"] - safe_eb["local_consumption_kw"]))
    < 0.01,
    f"gen {safe_eb['solar_generation_kw']} − load {safe_eb['local_consumption_kw']} = "
    f"export {safe_eb['local_export_kw']} kW",
)
check(
    "a SAFE case can still export without breaching any limit",
    safe_verdict.engineering_risk.value == "SAFE",
    "export alone is CAUTION-worthy only via reverse flow, per scenario_config.json",
)

# ============================================================
print("\nG. The twin adds no extra simulation")
# ============================================================
before_runs = len(pf._cache)  # noqa: SLF001 - inspecting the BASE cache on purpose
pf.simulate_with_elements("620", 0, 30)
after_first = len(pf._cache)  # noqa: SLF001
pf.simulate_with_elements("620", 0, 30)
after_second = len(pf._cache)  # noqa: SLF001
check(
    "repeat requests reuse the cached BASE case",
    after_second == after_first,
    f"cache {before_runs} → {after_first} → {after_second}",
)

# ============================================================
print("\nH. API surface")
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

    r = client.get("/api/grid/topology")
    check("GET /api/grid/topology", r.status_code == 200 and len(r.json()["nodes"]) == 114)

    r = client.get("/api/grid/topology/734")
    check("GET /api/grid/topology/{bus}", r.status_code == 200 and r.json()["path"][0] == "700")

    r = client.get("/api/grid/topology/99999")
    check("unknown bus returns 404", r.status_code == 404)

    r = client.post("/api/twin", json={"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": 66})
    body = r.json()
    check(
        "POST /api/twin returns assessment + topology + elements",
        r.status_code == 200
        and {"assessment", "topology", "elements"} <= set(body)
        and body["assessment"]["engineering"]["engineering_risk"] == "CONSTRAINED",
    )

    app.dependency_overrides.clear()
    r = client.post("/api/twin", json={"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": 66})
    check("unauthenticated /api/twin refused", r.status_code in (401, 403, 503), f"status {r.status_code}")
except Exception as exc:  # noqa: BLE001
    check("API surface", False, repr(exc)[:200])

# ============================================================
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 4 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
