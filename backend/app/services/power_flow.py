"""PowerFlowService — deterministic engineering verification.

This is a faithful port of run_case() / extract_metrics() from
dataset_generation_phase2.py. The solver call, the BASE/PV convention, the
metric definitions and the reverse-flow detection are byte-for-byte the same
logic that produced the training labels. If this file and the dataset
generator ever disagree, the labels the model learned would no longer describe
the system the application simulates.

BASE vs PV convention (dataset_generation_phase2.py):
    BASE = feeder + existing_pv_kw only
    PV   = feeder + existing_pv_kw + new_pv_kw
    delta = PV - BASE

Note on base_voltage_pu: the ML feature of that name comes from
electrical_features.csv, which was computed with NO PV at all. The BASE case
here includes existing PV. The two therefore differ when existing_pv_kw > 0.
That asymmetry exists in the original pipeline and is preserved deliberately.

The network is feeder_network.json — regulator taps FIXED at the validated
values. feeder_network_ldc.json is the abandoned LDC experiment (wrong tap
direction per engineering_audit.md) and is never loaded.
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import pandapower as pp

from app.core import paths


class PowerFlowError(RuntimeError):
    """Raised when a power flow fails to converge."""


@dataclass
class CaseMetrics:
    """Raw output of one power-flow run — mirrors extract_metrics()."""

    min_vm: float
    max_vm: float
    min_bus: str
    max_bus: str
    pv_bus_vm: float
    ext_p_mw: float
    ext_q_mvar: float
    losses_mw: float
    total_load_mw: float
    total_sgen_mw: float
    max_line_loading: float
    worst_line: str
    max_trafo_loading: float
    worst_trafo: str
    line_p: dict[int, float] = field(default_factory=dict)
    trafo_p: dict[int, float] = field(default_factory=dict)

    # Per-element series, needed by the digital twin to show which specific
    # assets moved. Same solved power flow — no extra simulation.
    bus_vm: dict[str, float] = field(default_factory=dict)
    line_loading: dict[int, float] = field(default_factory=dict)
    trafo_loading: dict[int, float] = field(default_factory=dict)
    trafo_p_lv: dict[int, float] = field(default_factory=dict)


@dataclass
class PowerFlowResult:
    """Engineering metrics for one assessment, named per the API contract."""

    pv_bus: str
    existing_pv_kw: float
    new_pv_kw: float
    total_pv_kw: float

    base_voltage_pu: float
    pv_voltage_pu: float
    voltage_rise_pu: float
    feeder_min_voltage_pu: float
    feeder_max_voltage_pu: float
    min_voltage_bus: str
    max_voltage_bus: str

    base_max_line_loading_pct: float
    max_line_loading_pct: float
    worst_line: str
    base_max_transformer_loading_pct: float
    max_transformer_loading_pct: float
    worst_transformer: str

    base_total_p_kw: float
    pv_total_p_kw: float
    power_loss_kw: float
    delta_losses_kw: float
    reverse_power_flow: bool
    reverse_reason: str
    solar_penetration_pct: float

    converged: bool
    engine: str
    engine_version: str
    network_file: str
    runtime_ms: int

    def as_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


class PowerFlowService:
    def __init__(self) -> None:
        self._template = pp.from_json(str(paths.FEEDER_NETWORK))
        self._engine_version = pp.__version__
        # (bus_id, kw) -> CaseMetrics. The BASE case for a bus repeats across
        # every request for that bus, exactly as base_cache did in the dataset
        # generator.
        self._cache: dict[tuple[str, float], CaseMetrics] = {}

    # ---------------- primitives ----------------

    def _bus_index(self, net, bus_id: str) -> int:
        hits = net.bus.index[net.bus.name == str(bus_id)].tolist()
        if not hits:
            raise PowerFlowError(f"Bus {bus_id} not present in the network model")
        return int(hits[0])

    def _run_case(self, bus_id: str, pv_kw: float) -> CaseMetrics:
        """One power flow with pv_kw injected at bus_id. Verbatim solver call."""
        net = copy.deepcopy(self._template)
        idx = self._bus_index(net, bus_id)

        if pv_kw > 0:
            pp.create_sgen(
                net,
                bus=idx,
                p_mw=pv_kw / 1000.0,
                q_mvar=0,  # unity power factor, per scenario_config.json
                name=f"PV_{bus_id}_{pv_kw}kW",
                type="PV",
            )

        # pandapower signals non-convergence by RAISING LoadflowNotConverged,
        # not by setting net.converged=False, so the flag alone is not enough.
        # A very large injection at a weak LV bus genuinely has no solution —
        # that is an engineering answer, not a server fault, so it is
        # normalised into PowerFlowError for the caller to turn into a 422.
        try:
            pp.runpp(
                net,
                algorithm="nr",
                max_iteration=500,
                numba=False,
                tolerance_mva=1e-3,
                enforce_q_limits=False,
            )
        except Exception as exc:  # noqa: BLE001 - pandapower raises several types
            raise PowerFlowError(
                f"Power flow did not converge for bus {bus_id} at {pv_kw} kW: {exc}"
            ) from exc

        if not net.converged:
            raise PowerFlowError(f"Power flow did not converge for bus {bus_id} at {pv_kw} kW")

        vm = net.res_bus.vm_pu
        ext_p = float(net.res_ext_grid.p_mw.iloc[0])
        ext_q = float(net.res_ext_grid.q_mvar.iloc[0])
        total_load = float(net.load.p_mw.sum()) if len(net.load) else 0.0
        total_sgen = float(net.sgen.p_mw.sum()) if len(net.sgen) else 0.0

        return CaseMetrics(
            min_vm=float(vm.min()),
            max_vm=float(vm.max()),
            min_bus=str(net.bus.name.iloc[vm.idxmin()]),
            max_bus=str(net.bus.name.iloc[vm.idxmax()]),
            pv_bus_vm=float(vm.iloc[idx]),
            ext_p_mw=ext_p,
            ext_q_mvar=ext_q,
            # losses = source + generation - load, as in extract_metrics()
            losses_mw=ext_p + total_sgen - total_load,
            total_load_mw=total_load,
            total_sgen_mw=total_sgen,
            max_line_loading=float(net.res_line.loading_percent.max()) if len(net.res_line) else 0.0,
            worst_line=str(net.line.name.iloc[net.res_line.loading_percent.idxmax()])
            if len(net.res_line)
            else "none",
            max_trafo_loading=float(net.res_trafo.loading_percent.max()) if len(net.res_trafo) else 0.0,
            worst_trafo=str(net.trafo.name.iloc[net.res_trafo.loading_percent.idxmax()])
            if len(net.res_trafo)
            else "none",
            line_p=net.res_line.p_from_mw.to_dict() if len(net.res_line) else {},
            trafo_p=net.res_trafo.p_hv_mw.to_dict()
            if len(net.res_trafo) and "p_hv_mw" in net.res_trafo.columns
            else {},
            bus_vm={str(net.bus.name.iloc[i]): float(vm.iloc[i]) for i in range(len(net.bus))},
            line_loading=net.res_line.loading_percent.to_dict() if len(net.res_line) else {},
            trafo_loading=net.res_trafo.loading_percent.to_dict() if len(net.res_trafo) else {},
            trafo_p_lv=net.res_trafo.p_lv_mw.to_dict()
            if len(net.res_trafo) and "p_lv_mw" in net.res_trafo.columns
            else {},
        )

    def _run_group_case(self, injections: dict[str, float]) -> CaseMetrics:
        """One power flow with PV injected at several buses at once.

        Same solver settings and same metric definitions as the single-bus
        case — only the number of sgens differs. This exists because a feeder's
        hosting capacity is NOT the sum of its buses' individual capacities:
        connections interact, and the only way to know the real limit is to
        energise them together and solve.
        """
        net = copy.deepcopy(self._template)

        first_idx = None
        for bus_id, kw in injections.items():
            idx = self._bus_index(net, bus_id)
            if first_idx is None:
                first_idx = idx
            if kw > 0:
                pp.create_sgen(
                    net,
                    bus=idx,
                    p_mw=kw / 1000.0,
                    q_mvar=0,
                    name=f"PV_{bus_id}_{kw}kW",
                    type="PV",
                )

        try:
            pp.runpp(
                net,
                algorithm="nr",
                max_iteration=500,
                numba=False,
                tolerance_mva=1e-3,
                enforce_q_limits=False,
            )
        except Exception as exc:  # noqa: BLE001
            raise PowerFlowError(
                f"Power flow did not converge for a group of {len(injections)} buses: {exc}"
            ) from exc

        if not net.converged:
            raise PowerFlowError(f"Power flow did not converge for a group of {len(injections)} buses")

        vm = net.res_bus.vm_pu
        ext_p = float(net.res_ext_grid.p_mw.iloc[0])
        total_load = float(net.load.p_mw.sum()) if len(net.load) else 0.0
        total_sgen = float(net.sgen.p_mw.sum()) if len(net.sgen) else 0.0

        return CaseMetrics(
            min_vm=float(vm.min()),
            max_vm=float(vm.max()),
            min_bus=str(net.bus.name.iloc[vm.idxmin()]),
            max_bus=str(net.bus.name.iloc[vm.idxmax()]),
            pv_bus_vm=float(vm.iloc[first_idx]) if first_idx is not None else float("nan"),
            ext_p_mw=ext_p,
            ext_q_mvar=float(net.res_ext_grid.q_mvar.iloc[0]),
            losses_mw=ext_p + total_sgen - total_load,
            total_load_mw=total_load,
            total_sgen_mw=total_sgen,
            max_line_loading=float(net.res_line.loading_percent.max()) if len(net.res_line) else 0.0,
            worst_line=str(net.line.name.iloc[net.res_line.loading_percent.idxmax()])
            if len(net.res_line)
            else "none",
            max_trafo_loading=float(net.res_trafo.loading_percent.max()) if len(net.res_trafo) else 0.0,
            worst_trafo=str(net.trafo.name.iloc[net.res_trafo.loading_percent.idxmax()])
            if len(net.res_trafo)
            else "none",
            line_p=net.res_line.p_from_mw.to_dict() if len(net.res_line) else {},
            trafo_p=net.res_trafo.p_hv_mw.to_dict()
            if len(net.res_trafo) and "p_hv_mw" in net.res_trafo.columns
            else {},
            bus_vm={str(net.bus.name.iloc[i]): float(vm.iloc[i]) for i in range(len(net.bus))},
            line_loading=net.res_line.loading_percent.to_dict() if len(net.res_line) else {},
            trafo_loading=net.res_trafo.loading_percent.to_dict() if len(net.res_trafo) else {},
            trafo_p_lv=net.res_trafo.p_lv_mw.to_dict()
            if len(net.res_trafo) and "p_lv_mw" in net.res_trafo.columns
            else {},
        )

    def simulate_group(
        self,
        label: str,
        base_injections: dict[str, float],
        pv_injections: dict[str, float],
    ) -> PowerFlowResult:
        """Assess many connections energised simultaneously.

        The result is shaped exactly like a single-bus assessment so that
        RiskAssessmentService can evaluate it with the same rule code and the
        same thresholds. Two fields are group interpretations, and are named
        here so the choice is visible rather than buried:

          * voltage_rise_pu is the WORST rise across the injected buses, so the
            group is judged by its most affected connection point.
          * base/pv_voltage_pu are that same worst bus, before and after.

        Every other metric is already feeder-wide and needs no interpretation.
        """
        started = time.perf_counter()

        base = self._run_group_case(base_injections)
        pv = self._run_group_case(pv_injections)

        worst_bus, worst_rise = None, 0.0
        for bus_id in pv_injections:
            before = base.bus_vm.get(str(bus_id))
            after = pv.bus_vm.get(str(bus_id))
            if before is None or after is None:
                continue
            if abs(after - before) >= abs(worst_rise):
                worst_bus, worst_rise = str(bus_id), after - before

        reverse, reverse_reason = self._detect_reverse_flow(base, pv)
        total_new_kw = sum(pv_injections.values()) - sum(base_injections.values())
        total_pv_kw = sum(pv_injections.values())
        penetration = (
            (total_pv_kw / (base.total_load_mw * 1000.0)) * 100.0 if base.total_load_mw > 0 else 0.0
        )

        return PowerFlowResult(
            pv_bus=worst_bus or label,
            existing_pv_kw=round(sum(base_injections.values()), 3),
            new_pv_kw=round(total_new_kw, 3),
            total_pv_kw=round(total_pv_kw, 3),
            base_voltage_pu=round(base.bus_vm.get(worst_bus or "", float("nan")), 5),
            pv_voltage_pu=round(pv.bus_vm.get(worst_bus or "", float("nan")), 5),
            voltage_rise_pu=round(worst_rise, 5),
            feeder_min_voltage_pu=round(pv.min_vm, 5),
            feeder_max_voltage_pu=round(pv.max_vm, 5),
            min_voltage_bus=pv.min_bus,
            max_voltage_bus=pv.max_bus,
            base_max_line_loading_pct=round(base.max_line_loading, 2),
            max_line_loading_pct=round(pv.max_line_loading, 2),
            worst_line=pv.worst_line,
            base_max_transformer_loading_pct=round(base.max_trafo_loading, 2),
            max_transformer_loading_pct=round(pv.max_trafo_loading, 2),
            worst_transformer=pv.worst_trafo,
            base_total_p_kw=round(base.ext_p_mw * 1000.0, 2),
            pv_total_p_kw=round(pv.ext_p_mw * 1000.0, 2),
            power_loss_kw=round(pv.losses_mw * 1000.0, 2),
            delta_losses_kw=round((pv.losses_mw - base.losses_mw) * 1000.0, 2),
            reverse_power_flow=reverse,
            reverse_reason=reverse_reason,
            solar_penetration_pct=round(penetration, 3),
            converged=True,
            engine="pandapower",
            engine_version=self._engine_version,
            network_file=paths.FEEDER_NETWORK.name,
            runtime_ms=int((time.perf_counter() - started) * 1000),
        )

    def _cached_case(self, bus_id: str, pv_kw: float) -> CaseMetrics:
        key = (str(bus_id), float(pv_kw))
        if key not in self._cache:
            self._cache[key] = self._run_case(bus_id, pv_kw)
        return self._cache[key]

    @staticmethod
    def _detect_reverse_flow(base: CaseMetrics, pv: CaseMetrics) -> tuple[bool, str]:
        """Verbatim from dataset_generation_phase2.py: source export first, then
        a line sign flip, then a transformer sign flip."""
        if pv.ext_p_mw < 0:
            return True, f"source export {pv.ext_p_mw:.3f}MW"

        for lid, pb in base.line_p.items():
            ppv = pv.line_p.get(lid, 0)
            if pb > 0.01 and ppv < -0.01:
                return True, f"line {lid} {pb:.3f}->{ppv:.3f} reversed"

        for tid, pb in base.trafo_p.items():
            ppv = pv.trafo_p.get(tid, 0)
            if pb > 0.01 and ppv < -0.01:
                return True, f"trafo {tid} reversed"

        return False, "none"

    # ---------------- public API ----------------

    def _compute(
        self, bus_id: str, existing_pv_kw: float, new_pv_kw: float
    ) -> tuple[PowerFlowResult, CaseMetrics, CaseMetrics]:
        """One BASE run and one PV run. Every public entry point goes through
        here, so there is exactly one place a power flow is solved."""
        started = time.perf_counter()

        total_pv_kw = existing_pv_kw + new_pv_kw
        base = self._cached_case(bus_id, existing_pv_kw)
        pv = self._run_case(bus_id, total_pv_kw)

        reverse, reverse_reason = self._detect_reverse_flow(base, pv)

        # solar_penetration_pct is a reporting quantity, not a threshold input:
        # total PV injection as a percentage of total feeder load. Both terms
        # come from the simulated network, nothing is assumed.
        penetration = (
            (total_pv_kw / (base.total_load_mw * 1000.0)) * 100.0
            if base.total_load_mw > 0
            else 0.0
        )

        result = PowerFlowResult(
            pv_bus=str(bus_id),
            existing_pv_kw=existing_pv_kw,
            new_pv_kw=new_pv_kw,
            total_pv_kw=total_pv_kw,
            base_voltage_pu=round(base.pv_bus_vm, 5),
            pv_voltage_pu=round(pv.pv_bus_vm, 5),
            voltage_rise_pu=round(pv.pv_bus_vm - base.pv_bus_vm, 5),
            feeder_min_voltage_pu=round(pv.min_vm, 5),
            feeder_max_voltage_pu=round(pv.max_vm, 5),
            min_voltage_bus=pv.min_bus,
            max_voltage_bus=pv.max_bus,
            base_max_line_loading_pct=round(base.max_line_loading, 2),
            max_line_loading_pct=round(pv.max_line_loading, 2),
            worst_line=pv.worst_line,
            base_max_transformer_loading_pct=round(base.max_trafo_loading, 2),
            max_transformer_loading_pct=round(pv.max_trafo_loading, 2),
            worst_transformer=pv.worst_trafo,
            base_total_p_kw=round(base.ext_p_mw * 1000.0, 2),
            pv_total_p_kw=round(pv.ext_p_mw * 1000.0, 2),
            power_loss_kw=round(pv.losses_mw * 1000.0, 2),
            delta_losses_kw=round((pv.losses_mw - base.losses_mw) * 1000.0, 2),
            reverse_power_flow=reverse,
            reverse_reason=reverse_reason,
            solar_penetration_pct=round(penetration, 3),
            converged=True,
            engine="pandapower",
            engine_version=self._engine_version,
            network_file=paths.FEEDER_NETWORK.name,
            runtime_ms=int((time.perf_counter() - started) * 1000),
        )
        return result, base, pv

    def simulate(self, bus_id: str, existing_pv_kw: float, new_pv_kw: float) -> PowerFlowResult:
        """Engineering metrics for one proposed connection."""
        return self._compute(bus_id, existing_pv_kw, new_pv_kw)[0]

    def simulate_with_elements(
        self, bus_id: str, existing_pv_kw: float, new_pv_kw: float
    ) -> tuple[PowerFlowResult, dict[str, Any]]:
        """The same single pair of power flows, plus per-element before/after.

        Used by the digital twin so it can colour only the assets that actually
        moved. No additional simulation is performed.
        """
        result, base, pv = self._compute(bus_id, existing_pv_kw, new_pv_kw)
        return result, self._element_detail(bus_id, existing_pv_kw, new_pv_kw, base, pv)

    def _element_detail(
        self,
        bus_id: str,
        existing_pv_kw: float,
        new_pv_kw: float,
        base: CaseMetrics,
        pv: CaseMetrics,
    ) -> dict[str, Any]:
        from app.services.topology import get_topology_service

        topo = get_topology_service()
        path = topo.path_to(str(bus_id))

        buses = {
            name: {
                "before_pu": round(base.bus_vm.get(name, float("nan")), 5),
                "after_pu": round(pv.bus_vm.get(name, float("nan")), 5),
                "delta_pu": round(pv.bus_vm.get(name, 0.0) - base.bus_vm.get(name, 0.0), 5),
            }
            for name in path
            if name in base.bus_vm and name in pv.bus_vm
        }

        lines = {}
        for line in topo.lines_on_path(path):
            i = line["index"]
            p_before = float(base.line_p.get(i, 0.0))
            p_after = float(pv.line_p.get(i, 0.0))
            lines[f"line:{i}"] = {
                "name": line["name"],
                "before_pct": round(float(base.line_loading.get(i, 0.0)), 3),
                "after_pct": round(float(pv.line_loading.get(i, 0.0)), 3),
                "p_before_kw": round(p_before * 1000.0, 2),
                "p_after_kw": round(p_after * 1000.0, 2),
                # Direction is the sign of real power at the sending end:
                # FORWARD means grid → customer, REVERSE means export upstream.
                "direction_before": "FORWARD" if p_before >= 0 else "REVERSE",
                "direction_after": "FORWARD" if p_after >= 0 else "REVERSE",
                "reversed_by_pv": p_before >= 0 > p_after,
            }

        transformers = {}
        trafo = topo.transformer_for_path(path)
        if trafo is not None:
            i = trafo["index"]
            p_before = float(base.trafo_p_lv.get(i, 0.0))
            p_after = float(pv.trafo_p_lv.get(i, 0.0))
            transformers[f"trafo:{i}"] = {
                "name": trafo["name"],
                "sn_kva": trafo["sn_kva"],
                "before_pct": round(float(base.trafo_loading.get(i, 0.0)), 3),
                "after_pct": round(float(pv.trafo_loading.get(i, 0.0)), 3),
                "p_before_kw": round(p_before * 1000.0, 2),
                "p_after_kw": round(p_after * 1000.0, 2),
                "direction_before": "FORWARD" if p_before <= 0 else "REVERSE",
                "direction_after": "FORWARD" if p_after <= 0 else "REVERSE",
                "reversed_by_pv": p_before <= 0 < p_after,
            }

        # Energy balance at the connection point. Generation and consumption are
        # modelled quantities; export is what generation exceeds local load by.
        total_pv_kw = existing_pv_kw + new_pv_kw
        local_load_kw = 0.0
        try:
            from app.services.grid_assets import get_grid_asset_service

            local_load_kw = get_grid_asset_service().get(str(bus_id)).existing_load_kw
        except Exception:  # noqa: BLE001 - an ineligible bus has no modelled load
            local_load_kw = 0.0

        local_export_kw = max(0.0, total_pv_kw - local_load_kw)
        self_consumed_kw = min(total_pv_kw, local_load_kw)

        return {
            "path": path,
            "buses": buses,
            "lines": lines,
            "transformers": transformers,
            "energy_balance": {
                "grid_supply_before_kw": round(base.ext_p_mw * 1000.0, 2),
                "grid_supply_after_kw": round(pv.ext_p_mw * 1000.0, 2),
                "solar_generation_kw": round(total_pv_kw, 2),
                "local_consumption_kw": round(local_load_kw, 2),
                "self_consumed_kw": round(self_consumed_kw, 2),
                "local_export_kw": round(local_export_kw, 2),
                "feeder_load_kw": round(base.total_load_mw * 1000.0, 2),
                "note": (
                    "Grid supply is the measured source infeed. Local consumption is "
                    "the modelled load at this bus; export is generation beyond it."
                ),
            },
        }

    def network_summary(self) -> dict[str, Any]:
        n = self._template
        return {
            "network_file": paths.FEEDER_NETWORK.name,
            "engine": "pandapower",
            "engine_version": self._engine_version,
            "buses": int(len(n.bus)),
            "lines": int(len(n.line)),
            "transformers": int(len(n.trafo)),
            "loads": int(len(n.load)),
            "regulator_handling": "taps FIXED at validated values",
        }


@lru_cache
def get_power_flow_service() -> PowerFlowService:
    return PowerFlowService()
