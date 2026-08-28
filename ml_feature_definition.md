# ML Feature Definition — Phase 3

**Dataset:** `pv_dataset.csv` (1500 rows, seed 42) + `pv_dataset_test.csv` (75 rows Phase1)
**Goal:** Predict `label` (SAFE/CAUTION/CONSTRAINED) and optionally hosting metrics before expensive PV power-flow.
**Principle:** No target leakage — features must be available at DISCOM prediction time (before PV PF).

## 1. Column taxonomy from pv_dataset.csv

| Category | Columns | Availability | Use in ML |
|----------|---------|--------------|-----------|
| **Identifiers** | scenario_id, feeder_id | Pre | Keep feeder_id as constant (future multi-feeder), scenario_id drop |
| **Proposed PV (inputs)** | pv_bus, existing_pv_kw, new_pv_kw, total_pv_kw | Pre (engineer inputs) | **INPUT FEATURES** |
| **Feeder static attributes** | pv_bus_vn_kv, existing_load_at_bus_kw, pp_bus_idx, transformer_association*, feeder_section*, base_voltage_pu* | Pre (from feeder DB, no PV PF) | **INPUT** if from DB, not from simulation |
| **BASE simulation outputs** | base_pv_bus_voltage_pu, base_min/max_voltage_pu, base_max_line/trafo_loading, base_total_p/q, base_losses | Post (requires BASE PF) | **EXCLUDE** — simulation leakage. Would require BASE PF at inference; defeats “predict before simulation”. |
| **PV simulation outputs** | pv_pv_bus_voltage_pu, pv_min/max, max_voltage_rise, worst_voltage_bus, pv_max_line/trafo, worst_line/transformer, pv_total_p/q, pv_losses | Post (PV PF) | **TARGETS / EXCLUDE as inputs** |
| **Deltas (derived targets)** | delta_pv_bus_voltage_pu, delta_total_p/q, delta_losses, delta_line/trafo | Post | **TARGETS** |
| **Condition flag** | reverse_power_flow, reverse_reason | Post | **TARGET** (predictable condition) |
| **Ground-truth label** | label (SAFE/CAUTION/CONSTRAINED), constraint_type, constraint_reason | Post (deterministic from PV outputs vs thresholds) | **LABEL** (constraint_type/reason drop, label keep) |

\* transformer_association, feeder_section, base_voltage_pu not in pv_dataset.csv but joinable from `valid_pv_buses.csv` (static feeder DB). Base_voltage_pu in valid_pv_buses is base feeder voltage (0.90-0.99) from `feeder_network.json` without PV — technically from BASE PF, so strictly leakage if used. For strict pre-simulation we treat it as **excluded**; for augmented experiment we could include as “base-conditioned” feature with leakage note.

## 2. Selected INPUT FEATURES (strict pre-simulation)

| Feature | Type | Unit | Source | Reason / Availability |
|---------|------|------|--------|------------------------|
| pv_bus | categorical 71 | bus_id | engineer input (location) | DISCOM selects connection point from valid list. Encode via one-hot / target encoding / embedding. |
| pv_bus_vn_kv | numeric | kV | feeder DB (`valid_pv_buses.csv:voltage_level_kv`) | Voltage level of secondary (0.208/0.24/0.48). Known without PF. Proxy for transformer type. |
| existing_pv_kw | numeric | kW | engineer input | Existing rooftop stock, known. |
| new_pv_kw | numeric | kW | engineer input (request) | New capacity requested. |
| total_pv_kw | numeric | kW | derived existing+new | Total injection used in PF. Keep (redundant but useful). |
| existing_load_at_bus_kw | numeric | kW | feeder DB (net.load per bus aggregated) | Historical load at that LV bus. Available from billing/DB. If zero, indicates spare secondary. |
| pv_penetration_ratio | numeric | ratio | derived total / max(1, existing_load) | Local penetration pressure. High >1 indicates export. Available pre-simulation (engineer can compute). |
| transformer_association | categorical | name (T1..T22, T16 etc) | feeder DB join (`valid_pv_buses:transformer_association`) | Which distribution trafo feeds bus. Encodes rating indirectly. Available without PF (topology). |
| feeder_section | categorical | section label | feeder DB join | Branch grouping (LV_secondary_T2_T4, Main_720-734, etc.). Captures distance from source. |

**Dropped:** feeder_id (constant), scenario_id, pp_bus_idx (internal).

**Total strict inputs: 9 (3 numeric PV + 1 load + 1 vn + 1 penetration + 2 categorical + pv_bus).** Optionally add `total_pv_kw` vs `existing_load` interaction already via penetration.

**Excluded leakage features (must NOT be inputs for “predict before simulation”):**
- All `base_*`, `pv_*`, `delta_*`, `max_voltage_rise`, `worst_*`, `*_loading_pct`, `*_total_p/q`, `*_losses`, `reverse_power_flow`. Including them would be target leakage: model would cheat by seeing post-simulation voltage.

**Variant for analysis (documented):**
- *Base-augmented features:* include `base_pv_bus_voltage_pu`, `base_max_trafo_loading` etc. These require BASE PF (cheap vs PV PF) but still simulation. If DISCOM runs BASE once, they could be available. For strictest hosting prediction (no PF at all), exclude. Report both; Phase4 baseline uses strict.

## 3. TARGETS and LABELS

| Target | Column | Type | Notes |
|--------|--------|------|-------|
| Primary classification | label | SAFE/CAUTION/CONSTRAINED | Deterministic from PV outputs vs thresholds `scenario_config.json`. Ground truth. |
| Secondary (optional) | constraint_type, reverse_power_flow, delta_pv_bus_voltage_pu, pv_max_voltage_pu, pv_max_trafo_loading_pct | mixed | Regression / multi-task; but leakage-gated. For Phase4 start with label only. |

`constraint_reason` is free text — drop for ML (use constraint_type as auxiliary).

## 4. Data leakage controls

- **No TXT:** Thresholds from `scenario_config.json` only; TXT not used for PV dataset generation.
- **No post-simulation inputs:** Strict feature set contains zero columns that require PV PF. Verified via column list above.
- **No label leakage:** `label` not in inputs; `constraint_*` not in inputs.
- **No future info:** Existing/new PV available at request time; load and topology available from DB.
- **Categorical encoding:** Fit encoder on train only, apply to val/test (no test leakage).

## 5. Train / Validation / Test preparation

- **Source:** `pv_dataset.csv` 1500 rows (Phase2) + optionally `pv_dataset_test.csv` 75 for final holdout? Phase3 uses `pv_dataset.csv` alone for train/val/test; Phase1 75 kept as sanity holdout not in splits.
- **Split strategy:** Stratified random by `label` (preserves 25.9/36.2/37.9% dist), seed 42, 70% train /15% val /15% test → 1050 /225 /225 rows. Not group-disjoint by bus (bus overlap allowed) — standard for diverse sampling. **Leakage check:** report bus overlap across splits; if strict bus-generalization required, alternative group split by `pv_bus` would be 71 groups disjoint, but reduces data and is noted as optional experiment.
- **Scenarios from same (pv_bus, total_pv) leaked?** All combos unique per `dataset_quality_report`, so no exact duplicate across splits (verified).
- **Class imbalance:** CONSTRAINED 37.9% not rare, but SAFE minority 25.9% — stratification preserves. For Phase4, recommend class_weight or balanced sampling.
- **Files to create:** `ml_dataset_train.csv`, `ml_dataset_val.csv`, `ml_dataset_test.csv` with only input features + label (and optionally targets for evaluation). Full `pv_dataset.csv` retained for reference.

## 6. Feature availability at prediction time (DISCOM workflow)

Engineer provides: feeder_id, pv_bus (dropdown of 71 valid), existing_pv_kw (DB), new_pv_kw (request). System looks up from feeder DB: pv_bus_vn_kv, existing_load, transformer, feeder_section, computes total and penetration — no PF needed. Model outputs label + reason + hosting estimate. PV PF only for ground-truth training, not for inference.

## 7. Version

Strict inputs v1 — for Phase4 baseline classification SAFE/CAUTION/CONSTRAINED.

