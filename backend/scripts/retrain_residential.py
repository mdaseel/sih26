"""Retrain the risk classifier so it covers the capacities the product serves.

Why this exists
---------------
The v2 model was trained on capacities from 5 to 250 kW with a median of
122.5 kW. The citizen form accepts 3 to 11 kW. Only 25 of 1184 training rows
(2.1%) fall inside that band, and across the whole of it the model returns SAFE
at 0.91-1.00 for every bus and every capacity: over the product's real input
domain it is a constant function.

That is not a presentation problem. A model whose headline accuracy was
measured on a distribution the product no longer sends does not describe live
performance, however good the number is.

Why it does not reuse the legacy scripts
----------------------------------------
dataset_generation_phase2.py, enrich_features.py and prepare_ml_splits.py all
hard-code absolute paths to a different machine, so they cannot run here. More
importantly, generating through them would build features with a second
implementation of the feature contract and label with a second copy of the
thresholds — two chances to drift from what the API actually does.

This script instead drives the *production services*:

    PowerFlowService.simulate   -> the same Newton-Raphson solve the API runs
    RiskAssessmentService       -> the same thresholds that classify live results
    MLPredictionService.build_features -> the same 18-feature contract

So a row generated here is labelled by exactly the physics a citizen's
application would meet, and described by exactly the features the served model
consumes. If the contract ever changes, this script changes with it for free.

What it does not do
-------------------
It does not overwrite the production model. It writes a candidate alongside it
and prints a comparison; promoting the candidate is a separate, deliberate step.

Usage
-----
    python backend/scripts/retrain_residential.py --residential 900
    python backend/scripts/retrain_residential.py --dry-run     # sample only
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.compose import ColumnTransformer  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # noqa: E402

from app.services.grid_assets import get_grid_asset_service  # noqa: E402
from app.services.ml_prediction import get_ml_service  # noqa: E402
from app.services.power_flow import PowerFlowError, get_power_flow_service  # noqa: E402
from app.services.risk_assessment import get_risk_service  # noqa: E402

SEED = 42
LABELS = ["SAFE", "CAUTION", "CONSTRAINED"]

# The name the existing v2 splits give the target column. Matching it matters:
# concatenating under a different name silently produces a column of NaN for
# every existing row, which sklearn reports only as "Input contains NaN".
LABEL_COL = "label"

# The band the citizen form accepts, from app.models.schemas.
RESIDENTIAL_MIN_KW = 3.0
RESIDENTIAL_MAX_KW = 11.0
# A little headroom either side, so the model sees where the band ends rather
# than treating its edge as the edge of the world.
SAMPLE_MIN_KW = 1.0
SAMPLE_MAX_KW = 20.0

EXISTING_V2 = {
    "train": ROOT / "ml_dataset_train_enriched_v2.csv",
    "val": ROOT / "ml_dataset_val_enriched_v2.csv",
    "test": ROOT / "ml_dataset_test_enriched_v2.csv",
}

PRODUCTION_MODEL = ROOT / "suryagrid_model_v2.pkl"
CANDIDATE_MODEL = ROOT / "suryagrid_model_v3.pkl"
GENERATED_ROWS = ROOT / "residential_scenarios_generated.csv"


# ============================================================
#  Scenario generation
# ============================================================
def sample_scenarios(n: int, buses: list[str], rng: random.Random) -> list[dict[str, Any]]:
    """Household-scale scenarios, spread over every eligible connection point.

    Capacity is drawn uniformly over a continuous range rather than from a
    handful of fixed sizes: the boundary this model has to learn is a smooth
    function of penetration, and five discrete sizes teach it five points on
    that curve.

    Existing PV matters more here than it does at feeder scale. A house with
    9 kW already installed asking for another 8 kW is the realistic path to a
    constrained residential case, so a third of the scenarios carry one.
    """
    seen: set[tuple[str, float, float]] = set()
    out: list[dict[str, Any]] = []
    attempts = 0

    while len(out) < n and attempts < n * 20:
        attempts += 1
        bus = rng.choice(buses)
        new_kw = round(rng.uniform(SAMPLE_MIN_KW, SAMPLE_MAX_KW), 1)
        existing_kw = 0.0 if rng.random() < 0.66 else round(rng.uniform(1.0, 10.0), 1)

        key = (bus, existing_kw, new_kw)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {"pv_bus": bus, "existing_pv_kw": existing_kw, "new_pv_kw": new_kw}
        )

    return out


def label_scenarios(scenarios: list[dict[str, Any]]) -> tuple[pd.DataFrame, int]:
    """Run each scenario through the real power flow and threshold logic."""
    ml = get_ml_service()
    grid = get_grid_asset_service()
    power_flow = get_power_flow_service()
    risk = get_risk_service()

    rows: list[dict[str, Any]] = []
    failures = 0
    started = time.time()

    for i, sc in enumerate(scenarios, start=1):
        bus_id = sc["pv_bus"]
        existing = float(sc["existing_pv_kw"])
        new = float(sc["new_pv_kw"])

        try:
            result = power_flow.simulate(bus_id, existing, new)
        except PowerFlowError:
            # A non-converging case is a property of the network, not a bug.
            # It carries no label, so it cannot be used for training.
            failures += 1
            continue

        verdict = risk.evaluate(result)
        features = ml.build_features(grid.get(bus_id), existing, new)
        rows.append({**features, LABEL_COL: verdict.engineering_risk.value})

        if i % 100 == 0:
            rate = i / max(time.time() - started, 1e-6)
            print(f"    {i}/{len(scenarios)} solved  ({rate:.1f}/s)", flush=True)

    return pd.DataFrame(rows), failures


# ============================================================
#  Training
# ============================================================
def build_pipeline(cat_features: list[str], num_features: list[str]) -> Pipeline:
    """The same shape as the production model, so the comparison is like for like."""
    return Pipeline(
        [
            (
                "prep",
                ColumnTransformer(
                    [
                        (
                            "cat",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                            cat_features,
                        ),
                        ("num", StandardScaler(), num_features),
                    ]
                ),
            ),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=300,
                    random_state=SEED,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def evaluate(pipe: Pipeline, X: pd.DataFrame, y: pd.Series, name: str) -> dict[str, Any]:
    """Score a fitted pipeline, with the safety metrics called out by name."""
    predicted = pipe.predict(X)
    proba = pipe.predict_proba(X)

    matrix = confusion_matrix(y, predicted, labels=LABELS)
    # Row CONSTRAINED, column SAFE: a genuinely constrained system called safe.
    # This is the error that would let an unsafe installation through, and it is
    # the number to read first.
    false_safe = int(matrix[LABELS.index("CONSTRAINED"), LABELS.index("SAFE")])
    constrained_row = matrix[LABELS.index("CONSTRAINED")]
    constrained_recall = (
        float(constrained_row[LABELS.index("CONSTRAINED")] / constrained_row.sum())
        if constrained_row.sum()
        else float("nan")
    )

    try:
        auc = float(
            roc_auc_score(
                y, proba, multi_class="ovr", average="macro", labels=list(pipe.classes_)
            )
        )
    except ValueError:
        # A split that happens to hold only one class cannot have an AUC.
        auc = float("nan")

    return {
        "split": name,
        "accuracy": float(accuracy_score(y, predicted)),
        "f1_macro": float(f1_score(y, predicted, average="macro")),
        "auc": auc,
        "false_safe": false_safe,
        "constrained_recall": constrained_recall,
        "confusion": matrix.tolist(),
        "report": classification_report(y, predicted, zero_division=0, output_dict=True),
    }


def show(scores: dict[str, Any]) -> None:
    print(f"  {scores['split']:<22} "
          f"acc {scores['accuracy']:.4f}   "
          f"F1 {scores['f1_macro']:.4f}   "
          f"AUC {scores['auc']:.4f}   "
          f"false-SAFE {scores['false_safe']}   "
          f"CONSTR recall {scores['constrained_recall']:.4f}")


# ============================================================
#  Main
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--residential", type=int, default=900,
                        help="How many household-scale scenarios to simulate.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Sample and report the scenario mix without solving.")
    args = parser.parse_args()

    rng = random.Random(SEED)
    np.random.seed(SEED)

    grid = get_grid_asset_service()
    buses = grid.eligible_bus_ids()
    print(f"Eligible connection points: {len(buses)}")

    print(f"\nSampling {args.residential} household-scale scenarios "
          f"({SAMPLE_MIN_KW:g}-{SAMPLE_MAX_KW:g} kW)…")
    scenarios = sample_scenarios(args.residential, buses, rng)
    sizes = [s["new_pv_kw"] for s in scenarios]
    in_band = sum(1 for s in sizes if RESIDENTIAL_MIN_KW <= s <= RESIDENTIAL_MAX_KW)
    print(f"  {len(scenarios)} unique scenarios")
    print(f"  new_pv_kw: min {min(sizes):.1f}  median {np.median(sizes):.1f}  max {max(sizes):.1f}")
    print(f"  inside the served 3-11 kW band: {in_band} ({100 * in_band / len(scenarios):.1f}%)")
    print(f"  carrying existing PV: {sum(1 for s in scenarios if s['existing_pv_kw'] > 0)}")

    if args.dry_run:
        print("\nDry run: no power flows solved, nothing written.")
        return 0

    print("\nSolving power flows through the production service…")
    generated, failures = label_scenarios(scenarios)
    print(f"  {len(generated)} labelled, {failures} did not converge")
    if generated.empty:
        print("No rows produced; aborting rather than writing an empty dataset.")
        return 1

    print("\n  label balance of the new rows:")
    for label, count in generated[LABEL_COL].value_counts().items():
        print(f"    {label:<12} {count:>5}  ({100 * count / len(generated):.1f}%)")

    generated.to_csv(GENERATED_ROWS, index=False)
    print(f"  written to {GENERATED_ROWS.name}")

    # ---- combine with the existing feeder-scale data ----
    print("\nCombining with the existing v2 splits…")
    existing = {k: pd.read_csv(v, dtype={"pv_bus": str}) for k, v in EXISTING_V2.items()}
    for name, frame in existing.items():
        print(f"  {name:<6} {len(frame):>5} existing rows")

    bundle = joblib.load(PRODUCTION_MODEL)
    features: list[str] = list(bundle["input_features"])
    cat_features: list[str] = list(bundle["cat_features"])
    num_features: list[str] = list(bundle["num_features"])

    generated["pv_bus"] = generated["pv_bus"].astype(str)

    # The new rows are split the same way the old ones were, so the residential
    # band is represented in train, val and test alike. Testing on a band the
    # model never trained on would measure the wrong thing; training on one it
    # is never tested on would hide the result.
    shuffled = generated.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    n_test = int(len(shuffled) * 0.175)
    n_val = int(len(shuffled) * 0.175)
    new_test = shuffled.iloc[:n_test]
    new_val = shuffled.iloc[n_test:n_test + n_val]
    new_train = shuffled.iloc[n_test + n_val:]

    combined = {
        "train": pd.concat([existing["train"], new_train], ignore_index=True),
        "val": pd.concat([existing["val"], new_val], ignore_index=True),
        "test": pd.concat([existing["test"], new_test], ignore_index=True),
    }
    for name, frame in combined.items():
        print(f"  {name:<6} {len(frame):>5} combined rows")

    for name, frame in combined.items():
        frame.to_csv(ROOT / f"ml_dataset_{name}_enriched_v3.csv", index=False)

    # ---- train ----
    print("\nTraining the candidate…")
    X = {k: v[features] for k, v in combined.items()}
    y = {k: v[LABEL_COL] for k, v in combined.items()}

    pipe = build_pipeline(cat_features, num_features)
    pipe.fit(X["train"], y["train"])

    candidate = {
        split: evaluate(pipe, X[split], y[split], f"candidate {split}")
        for split in ("val", "test")
    }

    # ---- the band that matters ----
    test = combined["test"]
    band_mask = (
        (test["new_pv_kw"] >= RESIDENTIAL_MIN_KW)
        & (test["new_pv_kw"] <= RESIDENTIAL_MAX_KW)
    )
    band_scores = None
    if band_mask.sum() >= 10:
        band_scores = evaluate(
            pipe, test.loc[band_mask, features], test.loc[band_mask, LABEL_COL],
            "candidate 3-11 kW",
        )

    # ---- the incumbent, on the same test set ----
    production = bundle["results"]["RandomForest"]["pipe"]
    incumbent_full = evaluate(pipe=production, X=X["test"], y=y["test"],
                              name="production test")
    incumbent_band = (
        evaluate(production, test.loc[band_mask, features],
                 test.loc[band_mask, LABEL_COL], "production 3-11 kW")
        if band_mask.sum() >= 10
        else None
    )

    print("\n" + "=" * 78)
    print("RESULTS")
    print("=" * 78)
    print("\nOn the combined test set (feeder-scale + residential):")
    show(incumbent_full)
    show(candidate["test"])
    if band_scores and incumbent_band:
        print("\nOn the residential band alone — the traffic the product actually sends:")
        show(incumbent_band)
        show(band_scores)
    print("\nCandidate validation split:")
    show(candidate["val"])

    print("\nCandidate confusion on the combined test set (rows true, cols predicted):")
    print(f"    {'':<14}" + "".join(f"{c:>14}" for c in LABELS))
    for label, row in zip(LABELS, candidate["test"]["confusion"]):
        print(f"    {label:<14}" + "".join(f"{v:>14}" for v in row))

    # ---- save the candidate, do not touch production ----
    joblib.dump(
        {
            "model": pipe,
            "input_features": features,
            "cat_features": cat_features,
            "num_features": num_features,
            "label_order": LABELS,
            "results": {
                "RandomForest": {
                    "val_acc": candidate["val"]["accuracy"],
                    "val_f1": candidate["val"]["f1_macro"],
                    "test_acc": candidate["test"]["accuracy"],
                    "test_f1": candidate["test"]["f1_macro"],
                    "auc": candidate["test"]["auc"],
                    "false_safe": candidate["test"]["false_safe"],
                    "cm": np.array(candidate["test"]["confusion"]),
                    "report": candidate["test"]["report"],
                    "constrained_recall": candidate["test"]["constrained_recall"],
                    "residential_band": band_scores,
                    "training_rows": int(len(combined["train"])),
                    "residential_rows_added": int(len(generated)),
                }
            },
        },
        CANDIDATE_MODEL,
    )
    print(f"\nCandidate written to {CANDIDATE_MODEL.name}. Production is untouched.")

    summary = {
        "generated_rows": int(len(generated)),
        "non_convergent": failures,
        "combined": {k: int(len(v)) for k, v in combined.items()},
        "candidate": {k: {m: v[m] for m in
                          ("accuracy", "f1_macro", "auc", "false_safe", "constrained_recall")}
                      for k, v in candidate.items()},
        "candidate_residential_band": band_scores and {
            m: band_scores[m] for m in
            ("accuracy", "f1_macro", "false_safe", "constrained_recall")
        },
        "production_on_same_test": {
            m: incumbent_full[m] for m in
            ("accuracy", "f1_macro", "false_safe", "constrained_recall")
        },
    }
    (ROOT / "retrain_residential_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print("Summary written to retrain_residential_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
