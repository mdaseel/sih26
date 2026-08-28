"""HostingCapacityService — how much more PV a bus can take.

The dataset never contained this. model_evaluation.md records that hosting
capacity was deferred because every row holds one PV size, not a maximum. So
it is computed here the only honest way available: by binary-searching the
real power flow for the largest capacity that trips no hard threshold.

    capacity = max new_pv_kw such that the engineering verdict is not CONSTRAINED

Nothing is estimated, curve-fitted, or read off the ML model. Every value is
the outcome of simulations, using the same thresholds from scenario_config.json
that decide a normal assessment.

Monotonicity
------------
Bisection assumes that adding PV never turns a CONSTRAINED case back into a
safe one. Voltage rise grows with injected power and transformer loading
eventually does too, so this holds for this feeder — but it is an assumption,
not a theorem, so `verify_monotonic()` exists to spot-check it and the result
carries a `method` field saying how it was obtained.

Cost
----
About 11 power flows per bus at ~40 ms each. Fine for one bus on demand;
precompute the full feeder with scripts/precompute_hosting_capacity.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from app.models.enums import RiskLevel
from app.services.grid_assets import GridAssetService, get_grid_asset_service
from app.services.power_flow import PowerFlowError, PowerFlowService, get_power_flow_service
from app.services.risk_assessment import RiskAssessmentService, get_risk_service

# kW. The feeder's total load is ~3.9 MW, so a single LV bus hosting more than
# this is far outside anything the model or the dataset ever described.
SEARCH_CEILING_KW = 2000.0
RESOLUTION_KW = 1.0


@dataclass
class HostingCapacity:
    bus_id: str
    existing_pv_kw: float
    hosting_capacity_kw: float
    limiting_constraint: str
    limiting_reason: str
    risk_at_capacity: str
    power_flows_run: int
    method: str = "bisection on the deterministic power flow"
    resolution_kw: float = RESOLUTION_KW
    ceiling_kw: float = SEARCH_CEILING_KW
    saturated: bool = False
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


class HostingCapacityService:
    def __init__(
        self,
        pf: PowerFlowService | None = None,
        risk: RiskAssessmentService | None = None,
        grid: GridAssetService | None = None,
    ) -> None:
        self._pf = pf or get_power_flow_service()
        self._risk = risk or get_risk_service()
        self._grid = grid or get_grid_asset_service()
        self._cache: dict[tuple[str, float], HostingCapacity] = {}

    # ---------------- primitives ----------------

    def _verdict(self, bus_id: str, existing_pv_kw: float, new_pv_kw: float) -> RiskLevel:
        metrics = self._pf.simulate(bus_id, existing_pv_kw, new_pv_kw)
        return self._risk.evaluate(metrics).engineering_risk

    def _is_constrained(self, bus_id: str, existing_pv_kw: float, new_pv_kw: float) -> bool:
        """True when this capacity is not acceptable.

        Non-convergence counts as not acceptable. At very large injections the
        power flow has no solution at all, which is emphatically not spare
        capacity — treating a failed solve as "fine" would report a hosting
        capacity the network cannot physically deliver.
        """
        try:
            return self._verdict(bus_id, existing_pv_kw, new_pv_kw) is RiskLevel.CONSTRAINED
        except PowerFlowError:
            return True

    # ---------------- capacity ----------------

    def capacity_for(self, bus_id: str, existing_pv_kw: float = 0.0) -> HostingCapacity:
        key = (str(bus_id), float(existing_pv_kw))
        if key in self._cache:
            return self._cache[key]

        self._grid.get(bus_id)  # raises for unknown or ineligible buses
        runs = 0
        notes: list[str] = []

        # Does even the smallest meaningful system already violate a limit?
        smallest = 1.0
        runs += 1
        if self._is_constrained(bus_id, existing_pv_kw, smallest):
            metrics = self._pf.simulate(bus_id, existing_pv_kw, smallest)
            verdict = self._risk.evaluate(metrics)
            result = HostingCapacity(
                bus_id=str(bus_id),
                existing_pv_kw=existing_pv_kw,
                hosting_capacity_kw=0.0,
                limiting_constraint=verdict.constraint_type.value,
                limiting_reason=verdict.constraint_reason,
                risk_at_capacity=verdict.engineering_risk.value,
                power_flows_run=runs + 1,
                notes=["No additional capacity: even 1 kW breaches a hard limit."],
            )
            self._cache[key] = result
            return result

        # Is the ceiling itself still acceptable? Then capacity is unbounded
        # within the range we are willing to search, and saying "2000 kW" would
        # overstate what was actually tested.
        runs += 1
        if not self._is_constrained(bus_id, existing_pv_kw, SEARCH_CEILING_KW):
            result = HostingCapacity(
                bus_id=str(bus_id),
                existing_pv_kw=existing_pv_kw,
                hosting_capacity_kw=SEARCH_CEILING_KW,
                limiting_constraint="none",
                limiting_reason=(
                    f"No hard limit reached up to the {SEARCH_CEILING_KW:.0f} kW search ceiling"
                ),
                risk_at_capacity=self._verdict(bus_id, existing_pv_kw, SEARCH_CEILING_KW).value,
                power_flows_run=runs + 1,
                saturated=True,
                notes=[
                    "Capacity is at or above the search ceiling; the true limit was not located.",
                ],
            )
            self._cache[key] = result
            return result

        # Bisect: lo is always acceptable, hi is always constrained.
        lo, hi = smallest, SEARCH_CEILING_KW
        while hi - lo > RESOLUTION_KW:
            mid = (lo + hi) / 2.0
            runs += 1
            if self._is_constrained(bus_id, existing_pv_kw, mid):
                hi = mid
            else:
                lo = mid

        capacity = float(int(lo))  # whole kW, rounded down — never overstate

        # Describe what actually binds, measured just past the limit.
        metrics = self._pf.simulate(bus_id, existing_pv_kw, hi)
        verdict = self._risk.evaluate(metrics)
        runs += 1

        at_capacity = self._verdict(bus_id, existing_pv_kw, capacity) if capacity > 0 else RiskLevel.SAFE
        runs += 1

        result = HostingCapacity(
            bus_id=str(bus_id),
            existing_pv_kw=existing_pv_kw,
            hosting_capacity_kw=capacity,
            limiting_constraint=verdict.constraint_type.value,
            limiting_reason=verdict.constraint_reason,
            risk_at_capacity=at_capacity.value,
            power_flows_run=runs,
            notes=notes,
        )
        self._cache[key] = result
        return result

    # ---------------- feeder-level capacity ----------------

    def feeder_capacity(
        self, feeder_section: str, existing_by_bus: dict[str, float] | None = None
    ) -> dict[str, Any]:
        """Total capacity a feeder section can host, all connections energised together.

        This is deliberately NOT the sum of the section's per-bus capacities.
        Each per-bus figure assumes that bus is the only new connection; adding
        them implies every customer can have their maximum simultaneously,
        which the physics does not allow. Summing overstates the limit, often
        badly.

        Instead the total is bisected while spreading capacity evenly across
        the section's eligible buses and solving the whole feeder each time, so
        the interaction between connections is part of the answer.

        The even split is a stated modelling choice: real uptake is uneven, and
        a different distribution gives a different total. It is reported in
        `distribution` so nobody reads the number as the only possible answer.
        """
        buses = [
            b
            for b in self._grid.eligible_bus_ids()
            if self._grid.get(b).feeder_section == feeder_section
        ]
        if not buses:
            raise ValueError(f"No eligible buses in feeder section {feeder_section}")

        existing = existing_by_bus or {}
        base_injections = {b: float(existing.get(b, 0.0)) for b in buses}

        def constrained_at(total_kw: float) -> tuple[bool, Any]:
            per_bus = total_kw / len(buses)
            pv_injections = {b: base_injections[b] + per_bus for b in buses}
            try:
                result = self._pf.simulate_group(feeder_section, base_injections, pv_injections)
            except PowerFlowError:
                return True, None
            verdict = self._risk.evaluate(result)
            return verdict.engineering_risk is RiskLevel.CONSTRAINED, verdict

        runs = 0
        smallest = float(len(buses))  # 1 kW per bus
        runs += 1
        blocked, verdict = constrained_at(smallest)
        if blocked:
            return {
                "feeder_section": feeder_section,
                "buses": len(buses),
                "hosting_capacity_kw": 0.0,
                "per_bus_kw": 0.0,
                "limiting_constraint": verdict.constraint_type.value if verdict else "infeasible",
                "limiting_reason": verdict.constraint_reason if verdict else "power flow did not converge",
                "risk_at_capacity": "CONSTRAINED",
                "power_flows_run": runs * 2,
                "method": "bisection on simultaneous injection across the section",
                "distribution": "even split across eligible buses",
                "saturated": False,
            }

        ceiling = SEARCH_CEILING_KW * 2
        runs += 1
        blocked, _ = constrained_at(ceiling)
        if not blocked:
            return {
                "feeder_section": feeder_section,
                "buses": len(buses),
                "hosting_capacity_kw": ceiling,
                "per_bus_kw": round(ceiling / len(buses), 1),
                "limiting_constraint": "none",
                "limiting_reason": f"No hard limit reached up to {ceiling:.0f} kW",
                "risk_at_capacity": "UNKNOWN",
                "power_flows_run": runs * 2,
                "method": "bisection on simultaneous injection across the section",
                "distribution": "even split across eligible buses",
                "saturated": True,
            }

        lo, hi = smallest, ceiling
        while hi - lo > max(RESOLUTION_KW, len(buses) * 0.5):
            mid = (lo + hi) / 2.0
            runs += 1
            blocked, _ = constrained_at(mid)
            if blocked:
                hi = mid
            else:
                lo = mid

        capacity = float(int(lo))
        runs += 1
        _, binding = constrained_at(hi)
        runs += 1
        _, at_capacity = constrained_at(capacity)

        return {
            "feeder_section": feeder_section,
            "buses": len(buses),
            "hosting_capacity_kw": capacity,
            "per_bus_kw": round(capacity / len(buses), 1),
            "limiting_constraint": binding.constraint_type.value if binding else "unknown",
            "limiting_reason": binding.constraint_reason if binding else "",
            "risk_at_capacity": at_capacity.engineering_risk.value if at_capacity else "UNKNOWN",
            "power_flows_run": runs * 2,
            "method": "bisection on simultaneous injection across the section",
            "distribution": "even split across eligible buses",
            "saturated": False,
        }

    def verify_monotonic(self, bus_id: str, existing_pv_kw: float = 0.0, steps: int = 12) -> dict[str, Any]:
        """Spot-check the assumption bisection rests on.

        Sweeps capacity linearly and confirms that once a case is CONSTRAINED
        it never becomes acceptable again at a larger size.
        """
        seen: list[tuple[float, str]] = []
        first_constrained: float | None = None
        violations: list[float] = []

        for i in range(1, steps + 1):
            kw = SEARCH_CEILING_KW * i / steps
            try:
                verdict = self._verdict(bus_id, existing_pv_kw, kw)
            except PowerFlowError:
                continue
            seen.append((kw, verdict.value))
            if verdict is RiskLevel.CONSTRAINED and first_constrained is None:
                first_constrained = kw
            elif first_constrained is not None and verdict is not RiskLevel.CONSTRAINED:
                violations.append(kw)

        return {
            "bus_id": str(bus_id),
            "monotonic": not violations,
            "first_constrained_kw": first_constrained,
            "non_monotonic_at_kw": violations,
            "sweep": seen,
        }


@lru_cache
def get_hosting_capacity_service() -> HostingCapacityService:
    return HostingCapacityService()
