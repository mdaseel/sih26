# Phase 2 Dataset Quality Report — pv_dataset.csv

**Generated:** dataset_generation_phase2.py (seed 42, continuous 5-250kW, cached BASE)
**Config:** scenario_config.json thresholds V 0.90/1.05 Δ 0.05/0.03 line 100/80 trafo 100/95
**Output:** pv_dataset.csv

## Summary

| Metric | Value |
|--------|-------|
| Target scenarios | 1500 |
| Unique generated | 1500 (seen 1500, attempts 1539) |
| Rows saved | 1500 |
| Converged BASE+PV | 1500 (100%) |
| Failed | 0 |
| Duplicates (pv_bus,existing,new) | 0 |
| NaN / Inf | 0 |
| Empty required field | 0 |

## Generation method (reproducible)

- Seed 42 (random + numpy)
- Valid buses 71 LV sampled uniformly → per-bus 11–30 mean 21.1
- Existing PV: 70% zero, else randint 3–15 kW → zeros 1062, non-zero 438 (dist 3-15 uniform)
- New PV: randint 5–250 kW uniform integer → flat across range (252 in 5-50, 333 in 50-100, 303 in 100-150, etc.)
- Deduped by (bus,existing,new); order S00001…S01500
- BASE caching: per (bus,existing) unique 419 bases computed, zero not shared across buses (fixed bug from Phase1 to keep pv_bus voltage correct)
- PV model: sgen unity PF at LV bus, balanced, fixed taps
- Runtime: ~600s, 1900 PF runs (419 bases +1500 PV) via cache; without cache 3000 runs

## Label distribution

| Label | Count | % |
|-------|-------|---|
| SAFE | 389 | 25.9% |
| CAUTION | 543 | 36.2% |
| CONSTRAINED | 568 | 37.9% |

Constraint type (hard):

| Type | Count |
|------|-------|
| transformer_loading | 322 |
| voltage (>1.05) | 246 |
| voltage_rise (>0.05) | 0 (≈Δ max 0.207 but voltage hard hits first) |
| line_loading | 0 |
| voltage_low (<0.90) | 0 |

CAUTION reasons (no hard): reverse flow dominates ~1045 flagged; also rise 0.03-0.05, trafo 95-100, max 1.03-1.05. CAUTION includes 543 cases.

## Feature ranges

- new_pv_kw 5–250 (uniform), total 8–265
- base_pv_bus 0.913–0.994, pv_pv 0.914–1.16, delta **0.00017–0.20793 all positive** (fixed)
- base_min 0.90593, pv_min 0.90599–0.93, pv_max 1.005–1.20808 (max 1.208 on weak secondary 623 with 250kW)
- base_max_line 8.77% → pv_max_line 8.63–57.86% (max 57% on OH-1 with large PV, <100)
- base_max_trafo 92.8% T7 → pv_max_trafo 92–689% (max 689% T7 with 250kW at 620-626 secondary cluster)
- delta_total_p  -338 to -5 kW all negative (source offload)
- delta_losses -32 to -0.1 kW all negative
- existing_load_at_bus 0–450 kW (770 largest)
- reverse 1045/1500 (69.7%) — local line/trafo export

## Bus coverage

- All 71 valid LV buses appear 11–30 times, mean 21.1 — systematic.
- LV secondaries 620-626 etc appear, far branches 770/772 appear, head 708/712 appear.
- Sections: LV_secondary_T2_T4, Branch_701-708, Main_720-734, Main_735-750, Branch_752-765, Delta_766-772 all represented.

## Checks

- No duplicate scenarios, no missing, power flow 100% — PASS
- ΔV calculation verified (pv - base) all >0 — PASS
- Physical sanity: source Δ negative, local Δ positive, losses negative — PASS
- Worst transformer T7 345 CONSTRAINED cases (global), T4 62, T1 27 — reflects small trafos overload plus T7 headroom
- Worst voltage bus 623/625/626 — secondary weak nodes, correct

## Notes vs Phase1

- Phase1 75 scenarios 66% SAFE now 25.9% SAFE because continuous 5-250 uniform pushes more large-PV stress; intentionally diverse for ML.
- Same electrical model, same thresholds — only sampling expanded, no model change.
- No TXT used for labels; TXT only for base validation per rule.

