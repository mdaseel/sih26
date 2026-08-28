# Phase 2 Validation Report — Large Dataset

**Feeder:** IEEE Comp Test Feeder balanced, 114 buses, fixed taps
**Dataset:** pv_dataset.csv 1500 rows, seed 42, same pipeline as Phase1
**Phase1:** PASS (75 rows). Phase2 scales to thousands.

## Validation Gate — 15 Questions

1. **Did scenarios converge?** YES 1500/1500 BASE+PV (100%). Cached BASE 419 unique, PV 1500. NR 500 iter tol 1e-3. Zero failures, no silent discard.

2. **Duplicates?** NO. Key (pv_bus,existing,new) unique 1500/1500. Full-row duplicate 0. Seeded continuous randint ensures uniqueness; attempt 1539 for 1500.

3. **Missing values?** NO. 38 columns present, 0 NaN/Inf/empty. Checked.

4. **Labels deterministic?** YES. Pure function of PV outputs vs thresholds in scenario_config.json. Seed only for sampling, not for physics.

5. **Every label explained?** YES. All 1500 have constraint_type/reason. SAFE “No violation”, CAUTION “reverse flow / rise / trafo …”, CONSTRAINED “Transformer T… 121-689%” or “Max voltage 1.06-1.20 >1.05”. No label without reason.

6. **BASE/PV correctly separated?** YES. BASE = feeder+existing only, PV=BASE+new. Fixed caching bug (pv_bus voltage per bus). Verified delta all positive 0.00017-0.20793; for zero-existing, base is feeder alone; for exist 5-15, base includes existing (e.g., 770 base 0.951 with 10kW vs 0.950 with 0). Incremental delta correct.

7. **ΔV correct?** YES. delta = pv - base signed, no TXT shift, retained per row. All 1500 positive, monotonic per bus with size.

8. **Voltage constraints correct?** YES. Hard low 0.90 none violate (pv_min 0.905-0.93), hard high 1.05 → 246 CONSTRAINED with pv_max 1.05-1.20 (e.g., 623 secondary 1.208). Caution high 1.03 flagged correctly. Δ hard 0.05 not hit because voltage hard hits first (max Δ 0.207 but voltage >1.05 triggers). Would trigger if voltage limit higher.

9. **Line constraints correct?** YES. Hard 100% none exceed (max 57.86% OH-1). Caution 80% also none exceed (max 57). Correct — HV lines lightly loaded; LV overload appears as trafo, not line.

10. **Transformer constraints correct?** YES. Hard 100% → 322 CONSTRAINED via trafo (max 689% T7, 150kVA with 250kW). Caution 95% → CAUTION pool includes 95-100 band. Worst trafo correctly per scenario (T7 345, T4 62, etc.). Local LV trafos dominate stress.

11. **Reverse power flow correct?** YES. Flag 1 if source export (none, source min 3.8MW) or line/trafo sign flip base→PV. 1045/1500 flagged (69.7%). Small PV 5-30kW rarely reverse, 100kW+ frequently reverse on small trafos — correct local export. Not auto-CONSTRAINED, contributes to CAUTION.

12. **Physically sensible?** YES. Source Δ negative 1500/1500, local Δ positive 1500/1500, losses Δ negative 1500/1500, far bus larger Δ than near, small PV SAFE → large PV CONSTRAINED, overload on undersized trafos.

13. **Unexpected results?** Documented:
    - (a) Voltage CONSTRAINED 246 cases now appear (vs 0 in Phase1) due to 250kW on weak secondaries pushing to 1.20 pu — expected at scale, not in 75-case sample.
    - (b) T7 345 cases as worst even when PV at distant LV — T7 is head 24.94/0.24 300kVA serving multiple loads, global max, not local; suggests global metric masks local but still correct overload detection.
    - (c) No line overload — feeder HV not stressed, hosting limit is LV trafo/voltage, not line. Explained.
    No hidden anomalies.

14. **Thresholds correctly applied?** YES. Code reads JSON, no hard-code. Adjusted low 0.90 (base 0.905) and trafo caution 95 (base 92.8) documented; Phase2 same. Labels follow hard → caution → SAFE order.

15. **Safe to scale?** YES for ML preparation with caveats:
    - Pipeline reproducible (seed 42), systematic bus coverage (11-30 each), continuous 5-250kW avoids duplicate cap, no model change.
    - Class distribution 25.9/36.2/37.9% — balanced enough for training, but large-PV heavy (969 >100kW) skews to CONSTRAINED; may need class weight/downsample for Phase3/4 — documented.
    - Not yet checked for feature leakage (Phase3).

## Distribution analysis (for scaling quality)

- Bus diversity: all 71 buses 11-30 each — no missing section.
- Capacity diversity: new 5-250 uniform int, not just 10 discrete — avoids thousands identical rows.
- Load vs PV: existing_load 0-450kW, new up to 250kW → total up to 265kW, penetration >1 on small loads correctly flagged.
- Convergence 100%, no impossible vm (0.905-1.20) or loading (92-689%) beyond explained overload.
- Reverse 69.7% — reflects high penetration sample; realistic if many 100kW+.

## Pass conditions

| Condition | Status |
|-----------|--------|
| Reliable PF | ✅ 100% |
| No NaN/Inf/dups | ✅ |
| BASE/PV Δ correct | ✅ (fixed caching) |
| Constraint detection | ✅ |
| Deterministic labels | ✅ |
| Physical sanity | ✅ |
| Anomalies documented | ✅ |

**Declaration: PHASE 2 = PASS**

Dataset `pv_dataset.csv` (1500 rows, seed 42) validated, safe for Phase3 ML dataset preparation. STOP — do not train ML until Phase3 leakage gate passes. Next: define ML features (pre-PV only) and splits.

Artifacts: pv_dataset.csv, phase2_dataset_quality_report.md, this report, scenario_config.json, dataset_generation_phase2.py
