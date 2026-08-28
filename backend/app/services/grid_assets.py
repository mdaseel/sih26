"""GridAssetService — the static feeder database.

Loads the existing per-bus attribute tables once and serves them from memory.
No power flow is needed for any of this: every column here was precomputed by
the research pipeline.

    valid_pv_buses.csv      -> the 71 PV-eligible LV buses + topology attributes
    excluded_buses.csv      -> the 43 ineligible buses + the reason
    electrical_features.csv -> transformer kVA, base voltage, distance, R/X/Z

This is the source of 11 of the model's 18 features; the other 7 are the user's
inputs and arithmetic on them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import pandas as pd

from app.core import paths


class UnknownBusError(ValueError):
    """Raised for a bus that does not exist in the feeder model."""


class IneligibleBusError(ValueError):
    """Raised for a real bus that is not a valid PV connection point."""


@dataclass(frozen=True)
class BusAttributes:
    """Everything the feeder database knows about one bus."""

    bus_id: str
    vn_kv: float
    existing_load_kw: float
    transformer_association: str
    feeder_section: str
    transformer_sn_kva: float
    base_voltage_pu: float
    feeder_distance_km: float
    upstream_r_ohm: float
    upstream_x_ohm: float
    upstream_z_ohm: float
    phase_configuration: str | None = None
    voltage_level_label: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "bus_id": self.bus_id,
            "vn_kv": self.vn_kv,
            "existing_load_kw": self.existing_load_kw,
            "transformer_association": self.transformer_association,
            "feeder_section": self.feeder_section,
            "transformer_sn_kva": self.transformer_sn_kva,
            "base_voltage_pu": self.base_voltage_pu,
            "feeder_distance_km": self.feeder_distance_km,
            "upstream_r_ohm": self.upstream_r_ohm,
            "upstream_x_ohm": self.upstream_x_ohm,
            "upstream_z_ohm": self.upstream_z_ohm,
            "phase_configuration": self.phase_configuration,
            "voltage_level_label": self.voltage_level_label,
        }


class GridAssetService:
    def __init__(self) -> None:
        self._valid = pd.read_csv(paths.VALID_PV_BUSES, dtype={"bus_id": str}).set_index("bus_id")
        self._excluded = pd.read_csv(paths.EXCLUDED_BUSES, dtype={"bus_id": str}).set_index("bus_id")
        self._elec = pd.read_csv(paths.ELECTRICAL_FEATURES, dtype={"bus_id": str}).set_index("bus_id")
        self._config = json.loads(paths.SCENARIO_CONFIG.read_text(encoding="utf-8"))

    # ---------------- lookups ----------------

    @property
    def feeder_id(self) -> str:
        return str(self._config.get("feeder_id", "IEEE_CompTestFeeder"))

    def eligible_bus_ids(self) -> list[str]:
        return sorted(self._valid.index.tolist(), key=lambda b: (len(b), b))

    def is_eligible(self, bus_id: str) -> bool:
        return str(bus_id) in self._valid.index

    def exists(self, bus_id: str) -> bool:
        b = str(bus_id)
        return b in self._valid.index or b in self._excluded.index

    def get(self, bus_id: str) -> BusAttributes:
        """Attributes for a PV-eligible bus.

        Raises UnknownBusError for a bus that is not in the feeder at all, and
        IneligibleBusError for an MV/source bus that exists but cannot host
        rooftop PV. The two are distinguished so the API can return an accurate
        message instead of a generic 400.
        """
        b = str(bus_id)
        if b not in self._valid.index:
            if b in self._excluded.index:
                reason = str(self._excluded.loc[b].get("eligibility_reason", "not PV-eligible"))
                raise IneligibleBusError(f"Bus {b} is not a valid PV connection point: {reason}")
            raise UnknownBusError(f"Bus {b} does not exist in feeder {self.feeder_id}")

        v = self._valid.loc[b]
        e = self._elec.loc[b]
        return BusAttributes(
            bus_id=b,
            vn_kv=float(v["voltage_level_kv"]),
            existing_load_kw=float(v["existing_load_kw"]),
            transformer_association=str(v["transformer_association"]),
            feeder_section=str(v["feeder_section"]),
            transformer_sn_kva=float(e["transformer_sn_kva"]),
            base_voltage_pu=float(e["base_voltage_pu"]),
            feeder_distance_km=float(e["feeder_distance_km"]),
            upstream_r_ohm=float(e["upstream_r_ohm"]),
            upstream_x_ohm=float(e["upstream_x_ohm"]),
            upstream_z_ohm=float(e["upstream_z_ohm"]),
            phase_configuration=str(v.get("phase_configuration")) if "phase_configuration" in v else None,
            voltage_level_label=str(v.get("voltage_level_label")) if "voltage_level_label" in v else None,
        )

    def list_eligible(self) -> list[dict[str, Any]]:
        """All 71 connection points, for the citizen's bus selector."""
        return [self.get(b).as_dict() for b in self.eligible_bus_ids()]

    # ---------------- thresholds ----------------

    def thresholds(self) -> dict[str, float]:
        """The validated thresholds, read from scenario_config.json.

        These are never redefined in application code (Rule 8) — this is the
        single place they enter the system.
        """
        t = self._config["thresholds"]
        return {
            "voltage_hard_low_pu": float(t["voltage_hard_low_pu"]["value"]),
            "voltage_hard_high_pu": float(t["voltage_hard_high_pu"]["value"]),
            "voltage_caution_low_pu": float(t["voltage_caution_low_pu"]["value"]),
            "voltage_caution_high_pu": float(t["voltage_caution_high_pu"]["value"]),
            "voltage_rise_hard_pu": float(t["voltage_rise_hard_pu"]["value"]),
            "voltage_rise_caution_pu": float(t["voltage_rise_caution_pu"]["value"]),
            "line_loading_hard_pct": float(t["line_loading_hard_pct"]["value"]),
            "line_loading_caution_pct": float(t["line_loading_caution_pct"]["value"]),
            "transformer_loading_hard_pct": float(t["transformer_loading_hard_pct"]["value"]),
            "transformer_loading_caution_pct": float(t["transformer_loading_caution_pct"]["value"]),
        }


@lru_cache
def get_grid_asset_service() -> GridAssetService:
    return GridAssetService()
