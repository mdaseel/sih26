# Phase 3 Validation Report — Data Leakage Gate

**Datasets:** `pv_dataset.csv` 1500 rows → `ml_dataset_train.csv` 1050 / `ml_dataset_val.csv` 225 / `ml_dataset_test.csv` 225
**Feature definition:** `ml_feature_definition.md`
**Split:** stratified random by `label`, seed 42, 70/15/15

## Gate Checks

### 1. No target leakage
**PASS.** Label `label` not in inputs. Inputs are 9 strict pre-simulation: `pv_bus`, `pv_bus_vn_kv`, `existing_pv_kw`, `new_pv_kw`, `total_pv_kw`, `existing_load_at_bus_kw`, `pv_penetration_ratio`, `transformer_association`, `feeder_section`. Verified `ml_dataset_train.csv` columns = inputs + label + 5 aux targets for eval (delta, pv_max, reverse) not used as inputs. Aux targets are post-simulation and excluded from X. `constraint_type/reason` not in X (only label).

### 2. No post-simulation info as input
**PASS with note.** Strict inputs contain zero `base_*`, `pv_*` (voltage), `delta_*`, `worst_*`, `*_loading`, `*_total`, `*_losses`, `reverse`. Those 37 post columns excluded. Two feeder-DB columns (`transformer_association`, `feeder_section`) are topology, not simulation. `existing_load_at_bus_kw` is from DB (net.load sum), not PF. `pv_bus_vn_kv` from `valid_pv_buses.csv`. `base_voltage_pu` deliberately excluded (would be leakage though available in valid_pv_buses). Check: `post_cols` detection correctly excludes only true post; `pv_bus` false-positive in naive `startswith('pv_')` fixed by explicit allowlist.

### 3. Features available at prediction time
**PASS.** Engineer at DISCOM provides `pv_bus` (dropdown 71), `existing_pv_kw` (DB), `new_pv_kw` (request). System looks up `pv_bus_vn_kv`, `existing_load`, `transformer`, `feeder_section` from feeder DB, computes `total` and `penetration` — no power flow needed. Matches `ml_feature_definition.md:6`.

### 4. Train/validation/test separation valid
**PASS.**
- Sizes 1050/225/225 (70/15/15), seed 42, stratified: train 37.9/36.2/25.9%, val 37.7/36.0/26.2%, test 37.7/36.4/25.7% — distributions preserved.
- No exact duplicate scenario across splits: key (pv_bus,existing,new) overlap 0/0/0 (verified).
- Bus overlap: train 71 buses, val 66, test 69; train-val 66, train-test 69, val-test 64 — overlap expected for random split. This tests generalization to seen buses with unseen PV sizes, not unseen buses. Alternative group-by-bus split would be 71 groups disjoint (e.g., 50/10/11 buses) for bus-generalization test — documented as optional, not required for Phase3.

### 5. Class distribution acceptable
**PASS.** 37.9% CONSTRAINED, 36.2% CAUTION, 25.9% SAFE — stratified preserved. Minority SAFE still 272 train, 59 val, 58 test (enough for metrics). Imbalance mild; recommend `class_weight=balanced` in Phase4.

### 6. Feature distributions reasonable
**PASS.**
- `new_pv_kw` 5-250 uniform int, mean 132 train, 131 test — no shift.
- `existing_load` 0-450kW mean 30kW, many zeros (sparse secondaries) — correct.
- `pv_penetration` 0.04-260 mean 95 — high when load 0, indicates export; capped by total/load, correct.
- Categorical: `pv_bus` 71 levels train all covered; `transformer` 22 levels top T2 28%; `feeder_section` 7 levels top LV_secondary_T2_T4 55% — no missing level in val/test (all 7/22 appear).
- No leakage via `pp_bus_idx` (dropped).

### 7. Leakage via base voltage?
**PASS.** `valid_pv_buses.csv:base_voltage_pu` (0.90-0.99 from feeder_network) not included in strict inputs (would be base PF leakage). Documented in feature definition as excluded for strict prediction; base-augmented variant would include it as “base-conditioned” but not for baseline.

## Files

- `ml_dataset_train.csv` (1050), `ml_dataset_val.csv` (225), `ml_dataset_test.csv` (225) — strict inputs + label + aux targets for eval (aux not for training)
- `ml_train_strict.csv` — inputs+label only (for direct training)
- `ml_feature_definition.md`

## Declaration

**PHASE 3 = PASS**

No target leakage, post-simulation correctly excluded, features genuinely available pre-simulation, splits stratified and de-duplicated, bus overlap documented. Safe for Phase4 ML training.

**STOP** — do not train until explicit approval. Next Phase4 will baseline classifiers on `ml_dataset_train` evaluating CONSTRAINED recall and false-SAFE.

