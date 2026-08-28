# False SAFE Case Analysis — SuryaGrid AI

**Model:** `suryagrid_model.pkl` (RandomForest, strict pre-simulation features, 1050 train)
**Test set:** `ml_dataset_test.csv` 225 rows, 5 false SAFE (CONSTRAINED→SAFE =2.4%)
**Investigated:** The 2 cases requested — Bus 734 66kW and Bus 6231 53kW — plus context from other 3 false SAFE (734 overlap, 6231 overlap). Diagnosis uses **exact same power-flow logic** as `dataset_generation_phase2.py` (pandapower NR, fixed taps, unity PF sgen, thresholds from `scenario_config.json`).

Limits from `scenario_config.json:39`:
- V low hard 0.90, high hard 1.05, caution high 1.03, rise hard 0.05, rise caution 0.03, line 100/80%, trafo 100/95%.

---

## 1. Per-Case Electrical Diagnosis (re-run with existing feeder model)

### CASE 1 — Bus 734, existing 0 kW, new 66 kW, total 66 kW, scenario S00786

**Bus description:** 734 = LV 0.24kV secondary at far end Main_720-734, load 15.85 kW, base voltage 0.90593 pu (feeder global minimum, validated feeder min 0.9059). Transformer association “-” (direct LV, no dedicated trafo listed, fed via T7/T1 upstream). Sub-bus cluster 734/735 etc.

**Power-flow rerun (same as dataset):**

| Case | Bus | New PV | Metric | Before PV | After PV | Limit | Violated? |
|------|-----|--------|--------|-----------|----------|-------|-----------|
| 734 | 734 | 66 kW | **PV bus voltage (pu)** | 0.90593 | **0.96344** | delta 0.05751 | - |
| 734 | - | - | Feeder min voltage (pu) | 0.90593 at 734 | 0.92478 at 735 | 0.90 low hard | **NO** (improves) |
| 734 | - | - | Feeder max voltage (pu) | 1.00536 at 702 | 1.00600 at 702 | 1.05 high hard | **NO** |
| 734 | - | - | **Voltage rise Δ at PV bus** | - | **0.05751** | **0.05 hard** | **YES** |
| 734 | - | - | Max line loading | 8.77% OH-1 | 12.82% SEC-8 | 100% | NO |
| 734 | - | - | Max trafo loading | 92.80% T7 | 92.56% T7 | 100% | NO |
| 734 | - | - | Source P | 4178.4 kW | 4100.9 kW (Δ -77.5 kW) | export <0 | NO |
| 734 | - | - | Source Q | 1690.2 kvar | 1663.9 kvar | - | - |
| 734 | - | - | Losses | 442.4 kW | 430.8 kW (Δ -11.6) | - | - |
| 734 | - | - | Reverse power flow | 0 | 1 (line 38 0.016→-0.048 MW reversed) | flag | YES (CAUTION level) |

**All trafo loadings after PV (top 5):** T7 92.56%, T1 92.50%, T-SUB 88.51%, Reg1 84.45%, T24 65.87% — no trafo >100%. **Line loadings top:** SEC-8 12.82% — no line >100%.

**Exact constraint per generation logic (hard priority: maxV>1.05 → minV<0.90 → Δ>0.05 → line>100 → trafo>100):**

> **voltage_rise | Rise 0.0575 exceeds 0.05**

Dataset `pv_dataset.csv S00786` records: `label=CONSTRAINED`, `constraint_type=voltage_rise`, `constraint_reason="Voltage rise at PV bus 734 0.0575 pu exceeds 0.05"`, `delta 0.05751`, `pv_max 1.006`, `pv_max_trafo 92.56% T7`. **Rerun matches dataset exactly (delta 0.05751 vs 0.05751).**

**Conclusion for 734:** Correctly labelled CONSTRAINED, but **only by voltage-rise hard threshold**, marginally above limit (0.0075 pu = 0.75% over). No absolute voltage violation, no overload.

---

### CASE 2 — Bus 6231, existing 0 kW, new 53 kW, total 53 kW, scenario S00355

**Bus description:** 6231 = LV 0.24kV secondary sub-bus (ideal switch to parent 723 → T2 secondary 720). Load 0 kW (spare secondary), base voltage 0.99457 pu (strong near T2), feeder section LV_secondary_T2_T4, transformer T2 (300kVA via T2 24.94/0.24). Part of clustered secondaries 623/6231/6232.

**Power-flow rerun:**

| Case | Bus | New PV | Metric | Before PV | After PV | Limit | Violated? |
|------|-----|--------|--------|-----------|----------|-------|-----------|
| 6231 | 6231 | 53 kW | **PV bus voltage (pu)** | 0.99457 | **1.04647** | delta 0.05190 | - |
| 6231 | - | - | Feeder min voltage | 0.90593 at 734 | 0.90663 at 734 | 0.90 low hard | NO |
| 6231 | - | - | Feeder max voltage | 1.00536 at 702 | 1.04647 at **623 (PV bus cluster)** | 1.05 high hard | **NO** (just below 1.05) |
| 6231 | - | - | **Voltage rise Δ** | - | **0.05190** | **0.05 hard** | **YES** |
| 6231 | - | - | Max line loading | 8.77% OH-1 | 12.18% SEC-6 | 100% | NO |
| 6231 | - | - | Max trafo loading | 92.80% T7 | 92.73% T7 | 100% | NO |
| 6231 | - | - | Source P | 4178.4 kW | 4123.7 kW (Δ -54.7) | export <0 | NO |
| 6231 | - | - | Losses | 442.4 kW | 440.6 kW | - | - |
| 6231 | - | - | Reverse power flow | 0 | 0 (no line/trafo sign flip, local T2 absorbs) | flag | NO |

**All trafo loadings after PV:** T7 92.73%, T1 92.53%, T-SUB 89.04% — no overload. Max voltage after PV is **1.04647 at bus 623** (PV bus itself), just 0.0035 pu below 1.05 hard — would be CAUTION high if Δ not hard.

**Exact constraint:**

> **voltage_rise | Rise 0.0519 exceeds 0.05**

Dataset `S00355` records same: `CONSTRAINED`, `voltage_rise 0.0519 >0.05`, `delta 0.0519`, `pv_max 1.04647`, `trafo 92.73%`. **Rerun matches dataset.**

**Conclusion for 6231:** Correctly labelled CONSTRAINED, again **solely by Δ>0.05**, marginally over (0.0019 pu). No trafo/line overload, absolute voltage 1.046 <1.05 not violated.

---

## 2. Why ML predicted SAFE

**Model:** RandomForest, inputs strict 9 features (no post-simulation). Probabilities from `suryagrid_model.pkl`.

### Case 734 66kW
- **Actual reason:** CONSTRAINED via Δ 0.0575>0.05
- **Prediction:** SAFE (true CONSTRAINED)
- **Probabilities:** CAUTION 0.34, **CONSTRAINED 0.26**, **SAFE 0.40** — low confidence, borderline (SAFE only 0.06 above CAUTION, 0.14 above CONSTR). Model uncertain, not confident.
- **Input features (`ml_dataset_test.csv`):**
  ```
  pv_bus: 734
  pv_bus_vn_kv: 0.24
  existing_pv_kw: 0
  new_pv_kw: 66
  total_pv_kw: 66
  existing_load_at_bus_kw: 15.85
  pv_penetration_ratio: 4.164
  transformer_association: - (none)
  feeder_section: Main_720-734
  ```
- **Feature sufficiency:** Features contain PV size (66kW moderate) and penetration 4.16 (>1 indicates export) and far-section (Main_720-734 indicates weak bus). However **electrical distance / impedance to source** not explicitly encoded (only section label). Rise Δ depends on Thevenin impedance seen from bus (R and X of path 734), which is not a direct feature. The model must infer from pv_bus one-hot (71 cats) but 734 has only 11-30 examples in train, with Δ near threshold sparse. For 734, train examples: 66kW at 734 may be rare; most 734 training sizes are random 5-250, some just above/below 0.05 — boundary learning difficult.

### Case 6231 53kW
- **Actual reason:** CONSTRAINED via Δ 0.0519>0.05
- **Prediction:** SAFE
- **Probabilities:** CAUTION 0.185, CONSTRAINED 0.06, **SAFE 0.755** — **high confidence wrong**.
- **Input features:**
  ```
  pv_bus: 6231
  pv_bus_vn_kv: 0.24
  existing_pv_kw: 0
  new_pv_kw: 53
  total_pv_kw: 53
  existing_load_at_bus_kw: 0.0
  pv_penetration_ratio: 53.0 (total/1 due to 0 load)
  transformer_association: T2
  feeder_section: LV_secondary_T2_T4
  ```
- **Feature sufficiency:** Load 0 → penetration 53 (artificially inflated because division by 1). This is outlier feature value (53 vs typical 4-5 for loaded buses). Model may have learned that T2 secondary with load 0 is strong (base 0.994) and tolerates PV, but Δ still violates due to local secondary impedance (small trafo T2). Feature `existing_load 0` masks that spare secondary still has high rise potential. The penetration ratio explosion (53) is not physically meaningful (should be total / trafo rating, not load). Model not given trafo rating or impedance, so cannot distinguish 53kW on strong vs weak secondary correctly. Also 6231 is sub-bus (6231/6232) with load 0 — training examples for T2 sub-buses with 53kW may be few, and many similar 53kW on other LV buses are SAFE (if load larger), so model generalizes to SAFE.

**General ML analysis across 5 false SAFE (test):**
- All 5 are Δ 0.051-0.057 just over 0.05 threshold — **boundary cases**.
- Their probabilities show low CONSTR confidence (0.06-0.26) vs SAFE 0.40-0.755.
- Feature importance top is total/new/penetration (0.18 each), but **impedance not encoded**, so Δ prediction relies on pv_bus memorization, which is sparse for 71 buses * 250 sizes.

### Classification of root cause (A-F)

| Case | A Dataset | B Feature | C Label-gen | D Insufficient examples | E Train/test dist | F Legit ML error |
|------|-----------|-----------|-------------|-------------------------|-------------------|------------------|
| 734 66kW | No — dataset correct, Δ 0.0575 genuine | **Partial B** — missing impedance / distance, penetration alone insufficient for rise | No — label correctly Δ>0.05 per `scenario_config.json:19` | **Yes D** — threshold-boundary cases rare, 734 has only ~20 train examples, ~2 near 0.05 | No — test bus 734 present in train (11-30 examples), distribution overlap | **Yes F** — legitimate generalization error near decision boundary, low confidence |
| 6231 53kW | No — dataset correct | **Yes B** — load 0 → penetration 53 artifact, missing trafo rating / secondary impedance; features insufficient to capture local rise | No | **Yes D** — 6231 sub-bus sparse (T2 cluster), 53kW near threshold underrepresented | No — bus present in train | **Yes F** — high-confidence error due to misleading penetration |

**Overall:** **Not dataset or label bug.** Diagnosis is **B + D + F**: feature insufficiency (no impedance/rating) plus sparse boundary training data cause legitimate ML boundary error. Not train/test shift (both buses in train) nor dataset corruption.

## 3. Bus eligibility check

| Bus | PV eligible | Eligibility reason | Feeder section | Transformer | Existing load | Base voltage |
|-----|-------------|--------------------|----------------|-------------|---------------|--------------|
| 734 | **YES** | LV customer secondary - eligible | Main_720-734 | - (direct LV) | 15.85 kW | 0.9059 pu (global min) |
| 6231 | **YES** | LV secondary sub-bus (ideal switch to parent) - eligible | LV_secondary_T2_T4 | T2 (300kVA) | 0.0 kW | 0.9946 pu |

Both are **genuinely valid rooftop candidates** per `valid_pv_buses.csv`. 734 is far weak end (eligible despite low voltage, needs PV rise). 6231 is spare secondary of T2 cluster (eligible as customer point, even though load 0 indicates future customer, not invalid). Not transformer internal, not source, not switch-only.

Dataset logic: `valid_pv_buses.csv` 71 LV buses, excludes MV 24.9/12.47 — correct. No invalidation of these two.

Eligibility logic is correct; no filtering needed.

## 4. Engineering Conclusion

1. **Is Bus 734 correctly labelled CONSTRAINED? YES.** Physics rerun gives Δ 0.05751 >0.05 hard limit (scenario_config.json). No trafo/line violation, no absolute voltage >1.05, but Δ hard is correctly violated. Label is not artificial; simulation independently produced Δ 0.0575.

2. **Is Bus 6231 correctly labelled CONSTRAINED? YES.** Δ 0.05190 >0.05 hard, just over threshold, absolute 1.046 <1.05 not violated, trafo 92.73% not violated. Label correct per deterministic rule.

3. **What exact constraint?** Both **voltage rise at PV bus >0.05 pu** (hard). 734: 0.0575, 6231: 0.0519. Not trafo, not line, not absolute voltage. This is the project’s Δ concern (IEEE 1547 3-5% rise).

4. **Are these buses valid PV candidates? YES.** Both LV secondary, eligible per `valid_pv_buses.csv`. 734 Main_720-734 far end, 6231 T2 secondary spare — legitimate rooftop points per topology.

5. **Is dataset generation logic correct? YES.** BASE/PV separation (existing 0 → total), Δ = PV-BASE, thresholds from JSON, power-flow NR, fixed taps — rerun matches csv delta to 1e-5, confirms no TXT tuning, no hard-coding.

6. **Is ML model the actual problem? YES, but as expected boundary error, not dataset bug.** Model misses marginal Δ violations because strict features lack electrical impedance / trafo rating, and boundary examples sparse. 734 low-confidence (0.40 SAFE vs 0.34 CAUTION) indicates uncertain region; 6231 high-confidence (0.755 SAFE) indicates misleading penetration feature due to 0 load. Both are legitimate ML generalization failures, not data corruption.

7. **What to fix FIRST, if anything?**
   - **Do NOT retrain yet** per instruction — analysis only.
   - **First fix: Feature enrichment, not label.** Add electrical distance / Thevenin impedance proxy and trafo rating to inputs: e.g., `upstream_R_ohm`, `distance_km` from source, `trafo_sn_kva`, `local short-circuit MVA`, `base_voltage_pu` (base-conditioned variant). Current `pv_penetration_ratio` with load 0 gives 53 artifact — replace with `total_pv / trafo_rating` and `total_pv / (load+1kW)` hybrid.
   - **Second: Threshold-aware training.** These cases are 0.0019-0.0075 pu over limit — near-boundary. Options: (a) lower decision threshold for CONSTRAINED (e.g., predict CONSTRAINED if prob >0.3, to catch 734's 0.26), (b) calibrated cost-sensitive loss penalizing false SAFE more, (c) augment training with synthetic near-threshold samples (active learning around Δ 0.04-0.06).
   - **Third: Data augmentation for sparse buses.** 6231/734 have ~20 examples each; oversample boundary sizes or add 50-70kW sweep per bus to densify threshold region.
   - **Do NOT change labels or feeder model.** Physics is correct; issue is feature/inference.
   - **No dataset regeneration needed now** — just feature fix then retrain.

---

**Files generated:** This `false_safe_case_analysis.md` via rerun of exact scenarios with tables.

