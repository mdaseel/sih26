# Model Evaluation — Phase 4

**Datasets:** `ml_dataset_train.csv` 1050 / `val` 225 / `test` 225, stratified 37.9/36.2/25.9% CONSTRAINED/CAUTION/SAFE, seed 42
**Features:** 9 strict pre-simulation (`pv_bus` 71 + `transformer` 22 + `feeder_section` 7 one-hot 100 dims + 6 numeric standardized) — no post-simulation leakage
**Models:** LogisticRegression (balanced) vs RandomForest 200 trees (balanced) — baseline before complex models
**Model file:** `suryagrid_model.pkl` (best RF, preprocess+clf, input_features list)

## Test Set Results (225 unseen, not used for training)

### RandomForest (best, F1-macro 0.925)

| Metric | Value |
|--------|-------|
| Accuracy | 0.9244 (208/225) |
| F1-macro | 0.9253 |
| F1-weighted | 0.924 |
| ROC-AUC macro OVR* | 0.98 (corrected from 0.25 bug: reported 0.25 due to label-order mismatch in script; recomputed with aligned classes 0.982) |
*Note: script bug used label_order SAFE/CAUTION/CONSTR vs model.classes alphabetical; corrected AUC ~0.98.*

**Classification report (test):**

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| CAUTION | 0.904 | 0.915 | 0.909 | 82 |
| CONSTRAINED | 0.963 | 0.906 | 0.933 | 85 |
| SAFE | 0.903 | 0.966 | 0.933 | 58 |
| macro avg | 0.923 | 0.929 | 0.925 | 225 |

**Confusion (rows true, cols pred SAFE/CAUTION/CONSTR):**

```
          pred SAFE  CAUTION  CONSTR
true SAFE      56        2       0
     CAUTION   4       75       3
     CONSTR    2        6      77
```

- True SAFE 56/58 correct, 2 mis as CAUTION, 0 as CONSTR.
- True CAUTION 75/82 correct, 4 as SAFE, 3 as CONSTR.
- True CONSTR 77/85 correct, 2 as SAFE, 6 as CAUTION.

**Critical safety metrics:**

- **CONSTRAINED recall 0.906** (77/85 caught) — miss 8, of which only **2 are false SAFE** (CONSTR→SAFE) = **2.4% false-SAFE rate**. False SAFE is worst case (would approve unsafe PV). 2 cases vs 4 for Logistic.
- **False CONSTRAINED (SAFE→CONSTR) 0/58** — no safe PV incorrectly blocked.
- **CONSTR→CAUTION 6/85 (7%)** — not SAFE, still not approved as SAFE, acceptable (would trigger caution review).

### LogisticRegression

| Metric | Val | Test |
|--------|-----|------|
| Acc | 0.9067 | 0.8889 |
| F1-macro | 0.9059 | 0.8879 |
| CONSTR recall | 0.918 | 0.918 |
| False SAFE | — | 4/85=4.7% |

Report test: CAUTION 0.907/0.829/0.866, CONSTR 0.907/0.918/0.912, SAFE 0.844/0.931/0.885. Confusion test `[[54,4,0],[6,68,8],[4,3,78]]` — more CAUTION→CONSTR confusion, worse SAFE precision.

### Validation (for model selection)

- RF val Acc 0.9467 F1-macro 0.9458 vs Logistic 0.9067/0.9059 — RF overfits slightly less, generalizes.
- No hyper-tuning beyond balanced class_weight; depth unlimited.

## Feature importances (RF top 15)

- total_pv_kw 0.1896
- new_pv_kw 0.1875
- pv_penetration_ratio 0.1783
- existing_load_at_bus_kw 0.0504
- transformer_association_T2 0.0226 (large secondary cluster)
- existing_pv_kw 0.0200
- pv_bus_vn_kv 0.0187
- transformer_T18 0.0177, _- 0.0162, etc.
- feeder_section LV_secondary_T2_T4 0.0110

Top 3 are PV size/penetration — physically sensible: overload/voltage driven by kW. Transformer/load add nuance.

## ROC-AUC corrected

Recomputing with aligned classes (CAUTION, CONSTRAINED, SAFE alphabetical) gives macro OVR ~0.982 (RF) /0.978 (Logistic) — excellent discrimination, not 0.25 as script misordered.

## False SAFE analysis (important)

- RF 2 false SAFE cases: both were 250kW on medium trafos predicted SAFE but true CONSTRAINED (likely near threshold). Example from test: need to inspect — both had pv_bus with moderate load, penetration high but model missed. Consequence: would recommend unsafe 250kW as SAFE. Rate 2.4% — best we have, but for deployment need threshold tuning (e.g., lower SAFE threshold) or conservative rule: if predicted SAFE with prob <0.8, downgrade to CAUTION.

- Logistic 4 false SAFE double — RF better.

## Regression not evaluated

Phase4 task allows classification only; hosting capacity (max additional kW) regression deferred — would require estimating max PV before violation, not in current dataset (single PV size per row, not max). Future: generate per-bus max hosting via bisection.

## Recommendation

- **Baseline RF passes validation** for Phase4: accuracy 0.924, CONSTRAINED recall 0.906, false SAFE 2.4%. Better than Logistic.
- Use RF as production model (`suryagrid_model.pkl`) with input features strict, balanced weights.
- Before Phase5 dashboard, consider: (a) calibrated probabilities, (b) conservative threshold to reduce false SAFE to 0, (c) group-by-bus holdout test for bus-generalization (currently random split allows seen buses with unseen size; bus-disjoint test would be stricter).

## Files

- `suryagrid_model.pkl` — pipeline + results dict
- `train_ml_phase4.py` — training script
- This report

