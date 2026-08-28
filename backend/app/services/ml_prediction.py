"""MLPredictionService — the pre-screening layer.

Loads the EXISTING trained model (suryagrid_model_v2.pkl) once and serves
predictions. Nothing is retrained and no dataset is regenerated.

The model is a fitted sklearn Pipeline (OneHotEncoder + StandardScaler +
RandomForest), so it takes the raw 18-column frame directly — there is no
separate preprocessing step to reimplement, and therefore no way for this
service to drift from how the model was trained.

Feature assembly mirrors enrich_features.py exactly:

    pv_to_transformer_ratio     = total_pv_kw / transformer_sn_kva
    new_pv_to_transformer_ratio = new_pv_kw   / transformer_sn_kva
    load_to_transformer_ratio   = existing_load_at_bus_kw / transformer_sn_kva
    pv_penetration_ratio        = total_pv_kw / existing_load_at_bus_kw,
                                  and total_pv_kw / 1.0 when the load is zero

That last line is the documented artifact behind the original bus-6231
false-SAFE case (false_safe_case_analysis.md). It is reproduced faithfully
rather than "fixed", because the model was trained on it — changing it here
would silently move every prediction away from the validated behaviour.

pv_bus dtype
------------
The fitted OneHotEncoder holds pv_bus categories as int64, because
train_ml_v2.py reads the training CSV without dtype=str. Passing a string
would make handle_unknown="ignore" emit an all-zero block with NO error and
quietly drop the feature. We therefore cast to int, matching training.
Measured on the 254-row test set: class predictions are identical either way
(97.64% accuracy, 0 false-SAFE in both), but probabilities differ — bus 734
reads 0.98 as int versus the 0.833 recorded in phase4_5_validation_report.md,
which was produced through the string path.
"""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import pandas as pd

from app.core import paths
from app.models.enums import RiskLevel
from app.services.grid_assets import BusAttributes, GridAssetService, get_grid_asset_service


@dataclass(frozen=True)
class MLPrediction:
    prediction: RiskLevel
    safe_probability: float
    caution_probability: float
    constrained_probability: float
    model_file: str
    model_version: str
    feature_count: int
    features_used: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "prediction": self.prediction.value,
            "safe_probability": self.safe_probability,
            "caution_probability": self.caution_probability,
            "constrained_probability": self.constrained_probability,
            "model_file": self.model_file,
            "model_version": self.model_version,
            "feature_count": self.feature_count,
        }


class MLPredictionService:
    MODEL_VERSION = "v2.0"

    def __init__(self, grid: GridAssetService | None = None) -> None:
        with open(paths.MODEL_V2, "rb") as fh:
            bundle = pickle.load(fh)

        self._model = bundle["model"]
        self._features: list[str] = list(bundle["input_features"])
        self._grid = grid or get_grid_asset_service()

        declared = json.loads(paths.MODEL_FEATURES.read_text(encoding="utf-8"))
        expected = list(declared["input_features_enriched"])
        if expected != self._features:
            raise RuntimeError(
                "Feature contract mismatch: enriched_features.json does not match "
                f"the pickle. json={expected} pickle={self._features}"
            )
        if len(self._features) != 18:
            raise RuntimeError(f"Expected the 18-feature V2 model, got {len(self._features)}")

    # ---------------- feature assembly ----------------

    def build_features(
        self, bus: BusAttributes, existing_pv_kw: float, new_pv_kw: float
    ) -> dict[str, Any]:
        """Assemble the 18 model inputs. No power flow, no simulation output."""
        total_pv_kw = existing_pv_kw + new_pv_kw
        sn = bus.transformer_sn_kva
        load = bus.existing_load_kw

        # enrich_features.py divides by a load of 1.0 when the bus load is zero.
        penetration = total_pv_kw / load if load != 0 else total_pv_kw / 1.0

        return {
            # user inputs
            "pv_bus": int(bus.bus_id),  # int64 to match the fitted encoder
            "existing_pv_kw": float(existing_pv_kw),
            "new_pv_kw": float(new_pv_kw),
            "total_pv_kw": float(total_pv_kw),
            # feeder database
            "pv_bus_vn_kv": bus.vn_kv,
            "existing_load_at_bus_kw": load,
            "transformer_association": bus.transformer_association,
            "feeder_section": bus.feeder_section,
            "transformer_sn_kva": sn,
            "base_voltage_pu": bus.base_voltage_pu,
            "feeder_distance_km": bus.feeder_distance_km,
            "upstream_r_ohm": bus.upstream_r_ohm,
            "upstream_x_ohm": bus.upstream_x_ohm,
            "upstream_z_ohm": bus.upstream_z_ohm,
            # derived
            "pv_penetration_ratio": float(penetration),
            "pv_to_transformer_ratio": float(total_pv_kw / sn),
            "new_pv_to_transformer_ratio": float(new_pv_kw / sn),
            "load_to_transformer_ratio": float(load / sn if sn else load),
        }

    # ---------------- prediction ----------------

    def predict(self, bus_id: str, existing_pv_kw: float, new_pv_kw: float) -> MLPrediction:
        bus = self._grid.get(bus_id)
        feats = self.build_features(bus, existing_pv_kw, new_pv_kw)

        frame = pd.DataFrame([feats])[self._features]
        label = str(self._model.predict(frame)[0])
        proba = self._model.predict_proba(frame)[0]
        by_class = {str(c): float(p) for c, p in zip(self._model.classes_, proba)}

        return MLPrediction(
            prediction=RiskLevel(label),
            safe_probability=by_class.get("SAFE", 0.0),
            caution_probability=by_class.get("CAUTION", 0.0),
            constrained_probability=by_class.get("CONSTRAINED", 0.0),
            model_file=paths.MODEL_V2.name,
            model_version=self.MODEL_VERSION,
            feature_count=len(self._features),
            features_used=feats,
        )

    @property
    def feature_names(self) -> list[str]:
        return list(self._features)


@lru_cache
def get_ml_service() -> MLPredictionService:
    return MLPredictionService()
