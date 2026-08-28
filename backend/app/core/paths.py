"""Locations of the existing engineering artifacts.

Every script in the original research pipeline hardcodes
``C:\\Users\\ASUS\\Documents\\suryaghar\\...``, which means none of them run on
a clone. This module is the portable replacement. It does NOT modify or move
any existing file — it simply resolves the same filenames relative to the
repository root, so the application can load exactly the artifacts the
research pipeline produced.

Resolution order:
    1. ``ARTIFACTS_DIR`` environment variable, if set.
    2. The repository root (three levels up from this file).
"""

from __future__ import annotations

import os
from pathlib import Path

# backend/app/core/paths.py -> backend/app/core -> backend/app -> backend -> repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[3]

ARTIFACTS_DIR: Path = Path(os.environ.get("ARTIFACTS_DIR") or REPO_ROOT).resolve()


def artifact(name: str) -> Path:
    """Resolve an artifact filename inside the artifacts directory."""
    return ARTIFACTS_DIR / name


# --- Production model (README_LATEST.md: V2 is the only model for the app) ---
MODEL_V2 = artifact("suryagrid_model_v2.pkl")
MODEL_FEATURES = artifact("enriched_features.json")

# --- Power-flow network -------------------------------------------------
# feeder_network.json is the production network: regulator taps are FIXED at
# the validated values. feeder_network_ldc.json is the abandoned independent-LDC
# experiment (engineering_audit.md documents the wrong tap direction) and must
# NOT be used for assessments.
FEEDER_NETWORK = artifact("feeder_network.json")

# --- Static feature database (no power flow needed at inference) ---------
VALID_PV_BUSES = artifact("valid_pv_buses.csv")
EXCLUDED_BUSES = artifact("excluded_buses.csv")
ELECTRICAL_FEATURES = artifact("electrical_features.csv")

# --- Threshold configuration — the single source of truth for labels ----
SCENARIO_CONFIG = artifact("scenario_config.json")

# --- Datasets (reference / regression fixtures only; never retrained) ---
# NOTE: pv_dataset.csv is the STALE v1 (1500 rows). The current dataset is
# pv_dataset_enriched_augmented.csv (1692 rows). Always use the latter.
DATASET_CURRENT = artifact("pv_dataset_enriched_augmented.csv")
ML_TEST_SET = artifact("ml_dataset_test_enriched_v2.csv")


REQUIRED_ARTIFACTS = {
    "model": MODEL_V2,
    "model_features": MODEL_FEATURES,
    "feeder_network": FEEDER_NETWORK,
    "valid_pv_buses": VALID_PV_BUSES,
    "electrical_features": ELECTRICAL_FEATURES,
    "scenario_config": SCENARIO_CONFIG,
}


def missing_artifacts() -> dict[str, Path]:
    """Return the required artifacts that are not present on disk."""
    return {k: p for k, p in REQUIRED_ARTIFACTS.items() if not p.exists()}
