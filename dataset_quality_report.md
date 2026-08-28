# Dataset Quality Report — Phase 1 (pv_dataset_test.csv)

Source: `dataset_generation.py` + `scenario_config.json` + `feeder_network.json`
Generated: Phase 1 small test — 75 scenarios

## Summary

| Metric | Value |
|--------|-------|
| Total scenarios attempted | 75 |
| Successful (converged BASE+PV) | 75 |
| Failed (BASE or PV no-converge) | 0 |
| Convergence rate | 100% |
| Rows in pv_dataset_test.csv | 75 |
| Duplicate scenarios | 0 |
| Scenarios with NaN | 0 |
| Scenarios with Inf | 0 |
| Missing values (empty required field) | 0 |
| Impossible electrical values (flagged) | 0 |

Impossible-value check: vm in [0.7,1.2], loading in [0,500%], losses plausible. None flagged (max trafo 289%, max vm 1.009 — explained as overload stress test).

## Label distribution

| Label | Count | % |
|-------|-------|---|
| SAFE | 50 | 66.7% |
| CAUTION | 19 | 25.3% |
| CONSTRAINED | 6 | 8.0% |

Constraint breakdown (PV case, hard):

| Constraint type | Count |
|-----------------|-------|
| transformer_loading | 6 |
| voltage | 0 |
| voltage_rise | 0 |
| line_loading | 0 |
| none (CAUTION reason) | 19 (18 reverse flow, 1 rise 0.03-0.05) |
| none (SAFE) | 50 |

All CONSTRAINED have reason: “Transformer T* loading *% exceeds 100%” with 250 kW on undersized LV trafos (e.g., T3 75kVA 289%, T8 150kVA 121%). All labels deterministic from `scenario_config.json` thresholds.

## Duplicate / leakage check

Key = (pv_bus, existing_pv_kw, new_pv_kw). All 75 unique. No duplicate rows in full CSV either.

## Convergence

- Solver: pandapower NR, max 500 iter, tol 1e-3 MVA
- BASE converged: 75/75
- PV converged: 75/75
- Regulators: FIXED taps (Reg1 7.7, Reg2 12.7, Reg3 5.1, Reg4 3.0, Reg5 -5.8) — no stepping, per engineering_audit.md
- No silent discard; failures would be recorded with `converged=False` and `fail_reason`.

## Column completeness

All 41 columns present per spec; required minima verified:
- scenario_id, feeder_id, pv_bus, existing/new/total, base/pv/delta pv_bus voltage, base/pv min/max, max_voltage_rise, worst bus, base/pv max line/trafo loading, worst line/trafo, totals p/q, losses, reverse, constraint_type/reason, label.
- Extras for traceability: base/pv min/max bus, delta line/trafo, existing_load, vn, base worst, reverse_reason, converged flags.

No missing values in required columns. 0 empty strings.

## Feature ranges (sanity)

| Feature | Min | Max | Mean | Notes |
|---------|-----|-----|------|-------|
| new_pv_kw | 5 | 250 | 68.4 | Residential 5 to stress 250 |
| total_pv_kw | 5 | 250 | 70.1 | |
| base_pv_bus_voltage_pu | 0.913 | 0.994 | 0.962 | LV buses |
| pv_pv_bus_voltage_pu | 0.913 | 0.999 | 0.970 | |
| delta_pv_bus_voltage_pu | 0.00012 | 0.04518 | 0.00785 | All >0 — PV raises voltage |
| base_min_voltage_pu | 0.90593 | 0.90593 | 0.90593 | BASE identical across buses (fixed base, no existing except 3 cases) |
| pv_min_voltage_pu | 0.90596 | 0.9176 | 0.9095 | PV lifts weak bus 734 |
| pv_max_voltage_pu | 1.00539 | 1.00915 | 1.0062 | |
| max_voltage_rise_pu | 0.00003 | 0.00416 | — | System-wide max rise smaller than local |
| pv_max_line_loading | 8.63 | 8.77 | 8.70 | Low, never >100% in Phase1 |
| pv_max_trafo_loading | 92.19 | 289.6 | 98.1 | Stress hits LV trafos |
| delta_total_p_kw | -275 | -5.2 | -68 | All negative — source offload |
| delta_losses_kw | -10.2 | -0.24 | -2.8 | All negative — loss reduction |
| reverse_power_flow | 0/1 (22 flagged) | — | — | 22 with local line/trafo reversal |

All within physical plausible bounds. Max trafo 289% is intentional overload branch (75kVA trafo with 250kW PV export).

## Notes

- BASE case = validated feeder + existing_pv only. PV case = BASE + new_pv. Correctly separated (verified for S076/S077/S078 where base voltage includes existing).
- ΔV = PV - BASE retained with sign, no normalization to TXT.
- No TXT values used for PV labels; TXT used only for base validation per CRITICAL RULE.

