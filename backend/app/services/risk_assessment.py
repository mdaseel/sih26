"""RiskAssessmentService — the final engineering authority.

The label rules are a verbatim port of dataset_generation_phase2.py. Order
matters and is preserved exactly, because constraint_type records the FIRST
rule violated:

    CONSTRAINED (hard, in this order)
        1. feeder max voltage  > voltage_hard_high_pu
        2. feeder min voltage  < voltage_hard_low_pu
        3. |voltage rise|      > voltage_rise_hard_pu
        4. max line loading    > line_loading_hard_pct
        5. max trafo loading   > transformer_loading_hard_pct

    CAUTION (any of, only when no hard rule fired)
        max voltage > voltage_caution_high_pu
        min voltage < voltage_caution_low_pu
        |voltage rise| >= voltage_rise_caution_pu
        max line loading  >= line_loading_caution_pct
        max trafo loading >= transformer_loading_caution_pct
        reverse power flow detected

    SAFE otherwise

Note the mixed comparison operators (> for hard, >= for caution on the rise
and loading bands). That is how the training labels were produced, so it is
how they are reproduced here.

Reverse power flow alone is CAUTION, never CONSTRAINED — scenario_config.json
states this explicitly as a policy choice ("DISCOM may allow with protection").

No threshold is defined in this file. Every value is read from
scenario_config.json through GridAssetService (Rule 8).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.models.enums import ConstraintKind, RiskLevel
from app.services.grid_assets import GridAssetService, get_grid_asset_service
from app.services.ml_prediction import MLPrediction
from app.services.power_flow import PowerFlowResult


@dataclass(frozen=True)
class EngineeringVerdict:
    engineering_risk: RiskLevel
    constraint_type: ConstraintKind
    constraint_reason: str
    thresholds_snapshot: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "engineering_risk": self.engineering_risk.value,
            "constraint_type": self.constraint_type.value,
            "constraint_reason": self.constraint_reason,
            "thresholds_snapshot": self.thresholds_snapshot,
        }


class RiskAssessmentService:
    def __init__(self, grid: GridAssetService | None = None) -> None:
        self._grid = grid or get_grid_asset_service()

    def evaluate(self, pf: PowerFlowResult) -> EngineeringVerdict:
        t = self._grid.thresholds()

        max_v = pf.feeder_max_voltage_pu
        min_v = pf.feeder_min_voltage_pu
        rise = abs(pf.voltage_rise_pu)
        line = pf.max_line_loading_pct
        trafo = pf.max_transformer_loading_pct

        # ---- hard rules, first match wins ----
        ctype = ConstraintKind.NONE
        reason = "No violation"

        if max_v > t["voltage_hard_high_pu"]:
            ctype = ConstraintKind.VOLTAGE
            reason = (
                f"Max voltage {max_v:.4f} pu at bus {pf.max_voltage_bus} "
                f"exceeds {t['voltage_hard_high_pu']}"
            )
        elif min_v < t["voltage_hard_low_pu"]:
            ctype = ConstraintKind.VOLTAGE
            reason = (
                f"Min voltage {min_v:.4f} pu at bus {pf.min_voltage_bus} "
                f"below {t['voltage_hard_low_pu']}"
            )
        elif rise > t["voltage_rise_hard_pu"]:
            ctype = ConstraintKind.VOLTAGE_RISE
            reason = (
                f"Voltage rise at PV bus {pf.pv_bus} {pf.voltage_rise_pu:.4f} pu "
                f"exceeds {t['voltage_rise_hard_pu']}"
            )
        elif line > t["line_loading_hard_pct"]:
            ctype = ConstraintKind.LINE_LOADING
            reason = (
                f"Line {pf.worst_line} loading {line:.1f}% "
                f"exceeds {t['line_loading_hard_pct']}%"
            )
        elif trafo > t["transformer_loading_hard_pct"]:
            ctype = ConstraintKind.TRANSFORMER_LOADING
            reason = (
                f"Transformer {pf.worst_transformer} loading {trafo:.1f}% "
                f"exceeds {t['transformer_loading_hard_pct']}%"
            )

        if ctype is not ConstraintKind.NONE:
            return EngineeringVerdict(RiskLevel.CONSTRAINED, ctype, reason, t)

        # ---- caution bands ----
        reasons: list[str] = []
        if max_v > t["voltage_caution_high_pu"]:
            reasons.append(f"max {max_v:.4f}>{t['voltage_caution_high_pu']}")
        if min_v < t["voltage_caution_low_pu"]:
            reasons.append(f"min {min_v:.4f}<{t['voltage_caution_low_pu']}")
        if rise >= t["voltage_rise_caution_pu"]:
            reasons.append(f"rise {pf.voltage_rise_pu:.4f}>={t['voltage_rise_caution_pu']}")
        if line >= t["line_loading_caution_pct"]:
            reasons.append(f"line {line:.1f}>={t['line_loading_caution_pct']}%")
        if trafo >= t["transformer_loading_caution_pct"]:
            reasons.append(f"trafo {trafo:.1f}>={t['transformer_loading_caution_pct']}%")
        if pf.reverse_power_flow:
            reasons.append("reverse flow")

        if reasons:
            return EngineeringVerdict(
                RiskLevel.CAUTION, ConstraintKind.CAUTION, "; ".join(reasons), t
            )

        return EngineeringVerdict(RiskLevel.SAFE, ConstraintKind.NONE, "No violation", t)

    @staticmethod
    def combine(ml: MLPrediction, verdict: EngineeringVerdict) -> dict[str, Any]:
        """Assemble the two layers for storage and display.

        The engineering verdict is the decision (Rule 4/6). The ML prediction is
        reported alongside it as the pre-screen, and any disagreement is
        surfaced rather than reconciled — a mismatch is information for the
        DISCOM engineer, not something to average away.
        """
        return {
            "ml_prediction": ml.prediction.value,
            "safe_probability": round(ml.safe_probability, 5),
            "caution_probability": round(ml.caution_probability, 5),
            "constrained_probability": round(ml.constrained_probability, 5),
            "model_file": ml.model_file,
            "model_version": ml.model_version,
            "feature_count": ml.feature_count,
            "engineering_risk": verdict.engineering_risk.value,
            "constraint_type": verdict.constraint_type.value,
            "constraint_reason": verdict.constraint_reason,
            "thresholds_snapshot": verdict.thresholds_snapshot,
            "config_file": "scenario_config.json",
        }


@lru_cache
def get_risk_service() -> RiskAssessmentService:
    return RiskAssessmentService()
