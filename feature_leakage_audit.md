# Feature Leakage Audit — Phase 4.5

**Dataset:** `pv_dataset.csv` 1500 rows, `electrical_features.csv` 71 buses, `ml_feature_definition.md` strict 9 inputs
**New enriched features proposed:** 13 listed in task, derived from feeder/model data only.

## 1. Current strict features (from Phase 3)

| Feature | Source | Available at prediction time? | Leakage? |
|---------|--------|-------------------------------|----------|
| pv_bus | engineer selects from valid_pv_buses.csv | Yes | No |
| pv_bus_vn_kv | feeder DB valid_pv_buses.csv | Yes | No |
| existing_pv_kw, new_pv_kw, total_pv_kw | engineer input (request) | Yes | No |
| existing_load_at_bus_kw | feeder DB net.load aggregation | Yes | No |
| pv_penetration_ratio (=total / max(1,load)) | derived from above | Yes | No (but artifact when load 0 → 53) |
| transformer_association | feeder DB valid_pv_buses | Yes | No |
| feeder_section | feeder DB valid_pv_buses | Yes | No |

**Result:** No post-simulation voltage/loading in inputs — PASS.

## 2. Proposed enriched features — leakage assessment

| # | Feature | Calculation from | Uses final PV simulation? | Available at prediction? | Verdict |
|---|---------|------------------|---------------------------|--------------------------|---------|
|1| transformer_sn_kva | `feeder_network.json` trafo sn_mva*1000 via `valid_pv_buses:transformer_association` or path search; for “-” buses uses T-SUB 5000 or nearest upstream trafo | No — rating is nameplate, not flow result | Yes — topology DB | **SAFE** |
|2| pv_to_transformer_ratio = total_pv_kw / transformer_sn_kva | derived from 1 + total_pv (input) | No | Yes (both inputs) | **SAFE** — indicates overload pressure, not actual loading |
|3| new_pv_to_transformer_ratio = new_pv_kw / sn | derived | No | Yes | **SAFE** |
|4| load_to_transformer_ratio = existing_load / sn | derived | No | Yes | **SAFE** |
|5| total_pv_kw | existing+new | No | Yes | **SAFE** (already) |
|6| pv_penetration_ratio | total / load | No | Yes | **SAFE** but keep for comparison; not alone |
|7| base_voltage_pu | `electrical_features.csv:base_voltage_pu` from **BASE feeder PF** (no PV) via `feeder_network.json` res_bus | **Requires BASE PF** (existing PV only, not new PV). Not final PV voltage or Δ. | **Conditional SAFE**: base PF is cheap (one run for base feeder) and could be precomputed for all buses offline; at prediction time engineer could look up base voltage from DB without running PV PF. Does NOT contain new PV answer, so not leakage of final label. If strict “no PF at all”, then exclude. Task explicitly requests it, so include with note. | **SAFE per task, with disclosure** |
|8| feeder_distance_from_source (km) | sum `net.line.length_km` along shortest path 700→pv_bus via `pp.topology.create_nxgraph` | No — topology + length only | Yes — topology | **SAFE** |
|9| upstream_impedance (r_ohm, x_ohm, z_ohm) | sum `r_ohm_per_km * length` and `x*length` along same path; uses `net.std_types` | No — line parameters, not flow | Yes | **SAFE** — captures Thevenin impedance, drives ΔV = I*Z |
|10| feeder_section | valid_pv_buses | No | Yes | **SAFE** |
|11| transformer_association | valid_pv_buses | No | Yes | **SAFE** |
|12| existing_load_at_bus_kw | feeder DB | No | Yes | **SAFE** |
|13| new_pv_kw / pv_bus_vn_kv | inputs / DB | No | Yes | **SAFE** |
|14| pv_bus | categorical | No | Yes | **SAFE** |

**Single leakage risk:** If we mistakenly added `pv_pv_bus_voltage_pu`, `delta_pv_bus_voltage_pu`, `pv_max_...`, `reverse_power_flow`, `constraint_type` as inputs, that would be **direct label leakage** (answer). None of the 13 proposed are those; they are all pre-PV.

**Indirect leakage check:** Could `base_voltage_pu` indirectly encode final voltage? Base voltage correlates with distance/impedance (weak bus 0.905 vs strong 0.994) but not with new PV size, so not leaking final Δ. It helps model learn that weak bus + large PV → higher Δ, without seeing Δ. Acceptable.

**Transformer ratios:** Ratios use `total_pv` and `sn`, not actual `pv_max_transformer_loading_pct` (which is flow result). So not leakage. Overload pressure proxy is legitimate.

**Distance/impedance:** Uses line lengths and r/x, not flow — safe.

**Conclusion:** All 13, when calculated as described from feeder DB / base PF, are **safe for prediction-time use**. No feature contains `label`, `constraint_reason`, `pv_*` final voltage, `delta`, or `pv_max_loading`. Task rule “never derive from final label” satisfied.

## 3. Implementation note

- Features 1-6,10-14 computed from `valid_pv_buses.csv` + `electrical_features.csv` without PF.
- Features 7-9 computed from `feeder_network.json` topology + base PF (one precompute) — documented as base-conditioned.
- Generation pipeline will read `electrical_features.csv` and join on `pv_bus` at dataset creation, not from simulation outputs.

## 4. Leakage control for training

- Fit encoders/scalers on train only, apply to val/test.
- No `pv_dataset.csv` post columns in X.
- Seed 42 deterministic.

