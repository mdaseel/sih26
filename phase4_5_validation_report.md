# Phase 4.5 Validation Report — Electrical Feature Enrichment

**Goal:** Improve ML without changing electrical ground truth.
**Old model:** `suryagrid_model.pkl` — 9 strict features, 1500 rows, RF Acc 0.924, F1 0.925, false SAFE 2/85=2.4%
**New model:** `suryagrid_model_v2.pkl` — 18 features (enriched + ratios + distance/impedance + base voltage) + 206 near-threshold augmentations, 1692 rows → 1184/254/254 split, RF Acc 0.976, F1 0.976, false SAFE 0/97

## 10 Questions

### 1. Did enriched features improve the model?
**YES — substantially.**
- Accuracy 0.924 → 0.976 (+5.2pp)
- F1-macro 0.925 → 0.976
- CONSTRAINED recall 0.906 → 1.000
- CAUTION recall 0.915 → 0.960, SAFE 0.966 → 0.966
- ROC-AUC 0.98 → 0.999 (RF). Feature importances now top `new_pv_kw` 0.124, `total_pv_kw` 0.119, `pv_to_trafo_ratio` 0.117, `penetration` 0.112, `new_to_trafo` 0.098, then `upstream_z` 0.049, `distance` 0.045, `base_voltage` 0.028 — electrical physics now captured.

### 2. Did False SAFE decrease?
**YES — from 2 to 0.**
- Old test (225): 2 false SAFE /85 CONSTRAINED =2.4% (734 66kW prob 0.40 SAFE, 6231 53kW prob 0.755 SAFE)
- New test (254, enriched+aug): **0 false SAFE /97 =0%** — best threshold 0.2-0.6 all 0. False CONSTRAINED (SAFE→CONSTR) also 0/58 vs old 0/58.

### 3. Does Bus 734 now predict CONSTRAINED?
**YES.**
- Old: SAFE (prob CONSTR 0.26) — wrong.
- **New: CONSTRAINED** prob 0.833 (CAUTION 0.146, SAFE 0.02) — correct, high confidence.
- Physics: Δ 0.05751>0.05, max 1.006 <1.05, trafo 92.56% <100 — rise-only violation. New features: `pv_to_trafo 0.013` (small, not overload), but `distance 17.08km`, `z 14.51Ω`, `base 0.9059` weak → model now learns distance+impedance drives rise, not just penetration.

### 4. Does Bus 6231 now predict CONSTRAINED?
**YES.**
- Old: SAFE prob 0.755 CONSTR 0.06 — high-confidence wrong (penetration 53 artifact, load 0).
- **New: CONSTRAINED prob 0.74** (CAUTION 0.243, SAFE 0.016) — correct.
- New features: `pv_to_trafo 0.177` (53/300), `new_to_trafo 0.177`, `base 0.994`, `distance 7.23km`, `z 5.09Ω` — trafo ratio + base voltage now correctly indicate spare secondary but still rise, penetration artifact mitigated by proper ratio.

### 5. Did accuracy improve or decrease?
**Improve:** 0.924 → 0.976 test, val 0.947 → 0.984. No trade-off.

### 6. Did CONSTRAINED recall improve?
**YES:** 0.906 → **1.000** (77/85 → 97/97 caught). Precision 0.963 → 0.970. No CONSTRAINED missed.

### 7. Did any data leakage occur?
**NO — verified in `feature_leakage_audit.md`.**
- New features derived from feeder DB/topology/base PF only: `transformer_sn_kva` (nameplate), ratios total/load divided by sn, `base_voltage_pu` (base feeder PF, not PV), `distance`/`r`/`x`/`z` (sum line lengths/r/x), `feeder_section`/`transformer_association` (topology).
- None contain `pv_pv_bus_voltage_pu`, `delta`, `pv_max_loading`, `label`, `constraint_reason`, `reverse` final. Base voltage is base-case, not PV answer — task explicitly allows as prediction-time lookup (precomputed). All 13 features safe per audit.
- Encoders fitted on train only, test not leaked.
- Labels remain from validated power-flow (`dataset_generation_phase2.py` logic), not changed.

### 8. Is model now sufficiently reliable for next stage?
**YES, conditionally.** False SAFE 0, CONSTRAINED recall 1.0, high accuracy, both previously failing buses now correct with high confidence. Remaining risk is near-threshold generalization — augmentation added 206 samples 0.035-0.065 (124 CAUTION, 82 CONSTRAINED) densifying boundary, which helped. Bus coverage all 71 still, no missing values, 1692 rows.

### 9. What is still limiting the model?
- **Impedance approximation:** Upstream Z is sum of line r/x along shortest path ignoring mutuals and trafo impedance detailed; true Thevenin may differ slightly.
- **Transformer_sn for “-” buses:** 734 etc use T-SUB 5000kVA fallback; true limit for Main_720-734 is not local trafo but feeder headroom — ratio not informative, relies on distance/Z. More precise would be upstream branch rating.
- **Base voltage requires base PF:** If strict “no PF at all”, base_voltage would be leakage; but task allows it as DB lookup. Without it, accuracy would drop slightly.
- **Class imbalance still mild SAFE 23%** — but stratified handles.
- **Line loading never violated** in data (max 57%) — model not tested on line overload, but feeder not stressed there.

### 10. Should we proceed to dashboard/deployment?
**GO — with caveats.**
- Proceed only if dataset has no missing/invalid: **PASS** (1692 rows 0 NaN/Inf, 0 dups, 100% converged)
- No leakage: **PASS**
- Labels from power-flow: **PASS** (augmentation reran PF, same thresholds)
- Test independent (254 unseen, stratified): **PASS**
- False SAFE reduced: **PASS** (2→0) and demonstrably understood (feature + augmentation fix)
- CONSTRAINED recall acceptable: **PASS** 1.0
- Buses 734/6231 explicitly correct: **PASS**
- Threshold investigation: default argmax already 0 false SAFE; lowering CONSTR threshold to 0.30-0.40 keeps 0 false SAFE without inflating false CONSTR (0) — **no threshold change needed**, but recommend keeping threshold at 0.35-0.40 for conservatism; trade-off table shows stable.

**Decision: GO to Phase 5 dashboard** with new model `suryagrid_model_v2.pkl` (18 features). Keep old model as backup. Monitor false SAFE in production and trigger retrain if new topology added. Do not deploy old model.

---

## Comparison Table

| Metric | Old Model (9 feats, 1500) | New Model V2 (18 feats, 1692) |
|--------|---------------------------|-------------------------------|
| Accuracy | 0.924 | **0.976** |
| False SAFE (CONSTR→SAFE) | 2/85 (2.4%) | **0/97 (0%)** |
| False CONSTRAINED (SAFE→CONSTR) | 0/58 (0%) | 0/58 (0%) |
| SAFE F1 | 0.933 | 0.974 |
| CAUTION F1 | 0.909 | 0.969 |
| CONSTRAINED F1 | 0.933 | 0.985 |
| Macro F1 | 0.925 | **0.976** |
| CONSTR recall | 0.906 | **1.000** |
| CONSTR precision | 0.963 | 0.970 |
| 734 66kW: actual CONSTR, pred | SAFE (0.40) | **CONSTR (0.833)** |
| 6231 53kW: actual CONSTR, pred | SAFE (0.755) | **CONSTR (0.74)** |
| Features | 9 strict | 18 enriched (+sn, ratios, base, distance, r/x/z) |
| Augmentation | none | +206 near Δ 0.035-0.065 (124 CAUTION/82 CONSTR) |
| Dataset size | 1500 | 1692 (1184/254/254) |
| Leakage | none | none (audit PASS) |

Threshold trade-off: Old false SAFE 1-3 across 0.2-0.6 thr; New 0 across all thr — robust.

**Files:** `pv_dataset_enriched_augmented.csv`, `ml_dataset_*_enriched_v2.csv`, `electrical_features.csv`, `feature_leakage_audit.md`, `suryagrid_model_v2.pkl`, this report.
