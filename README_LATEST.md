# SuryaGrid AI — CURRENT PRODUCTION

**DO NOT USE V1 FOR APPLICATION PREDICTIONS**

## CURRENT PRODUCTION MODEL
**File:** `suryagrid_model_v2.pkl`
- Also available as: `suryagrid_model_CURRENT.pkl` and `suryagrid_model.pkl` (now points to V2)
- Input features: **18 enriched electrical** (see below)
- Test accuracy: **97.6%**, False SAFE **0/97**, CONSTRAINED recall **1.00**
- Validation: Phase 4.5 PASS

## CURRENT DATASET
**File:** `pv_dataset_enriched_augmented.csv`
- Also: `pv_dataset_CURRENT.csv` (same, 782940 bytes, 1692 rows)
- **Note:** `pv_dataset.csv` is locked by OS (529501 bytes old v1) — logical current is `pv_dataset_CURRENT.csv`/`pv_dataset_enriched_augmented.csv`. Code must use CURRENT, not old v1 path (see verification).
- Rows: 1692 (1500 original +206 near-threshold Δ 0.035-0.065 augmentation, seed 42)
- Splits: `ml_dataset_train_enriched_v2.csv` (1184) / `val` (254) / `test` (254)

## FEATURES — 18 enriched electrical
```
pv_bus, pv_bus_vn_kv, existing_pv_kw, new_pv_kw, total_pv_kw,
existing_load_at_bus_kw, pv_penetration_ratio,
transformer_association, feeder_section,
transformer_sn_kva, pv_to_transformer_ratio, new_pv_to_transformer_ratio,
load_to_transformer_ratio, base_voltage_pu, feeder_distance_km,
upstream_r_ohm, upstream_x_ohm, upstream_z_ohm
```
- Derived from feeder DB/topology + base PF only (see `feature_leakage_audit.md` — no label leakage)
- Old 9-feature list is **DEPRECATED**

## TEST ACCURACY
- **97.6%** overall, macro F1 0.976, ROC-AUC 0.999
- **FALSE SAFE 0** (vs v1 2)
- 734 66kW: CONSTRAINED (prob 0.833) ✓
- 6231 53kW: CONSTRAINED (prob 0.74) ✓

## OLD V1 — BACKUP ONLY
- `suryagrid_model_v1_backup.pkl` (6.5 MB)
- `pv_dataset_v1_backup.csv` (529501 bytes)
- 9 features, 1500 rows, 92.4% accuracy, 2 false SAFE — **DO NOT USE FOR APPLICATION**

## FOR TEAMMATES CLONING
1. Use `suryagrid_model_v2.pkl` / `suryagrid_model_CURRENT.pkl`
2. Use `pv_dataset_enriched_augmented.csv` / `pv_dataset_CURRENT.csv` and `ml_dataset_*_enriched_v2.csv`
3. Features: load `enriched_features.json` (18) — old 9 will fail
4. Run `python verify_production_model.py` — must be PASS
5. Do not retrain, do not change feeder/labels, do not hard-code predictions

## VERIFICATION
Run `python verify_production_model.py` and check 734/6231 predictions.

