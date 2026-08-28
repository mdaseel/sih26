# Scenario Examples — Phase 1

Thresholds from `scenario_config.json`:
- V hard low 0.90, high 1.05; caution high 1.03 (low caution disabled 0.90)
- ΔV hard 0.05, caution 0.03
- Line hard 100%, caution 80%
- Trafo hard 100%, caution 95%

All voltages pu on bus base (120V base for validation). PV as `sgen` unity PF, balanced.

---

## 5 SAFE examples (no hard, no caution)

### SAFE-1 S001 — small rooftop near head
- pv_bus 708 (0.24kV, T16), existing 0, new 5kW, total 5kW, load 75kW at bus
- base_pv 0.95802 → pv 0.95820 delta **+0.00019** (0.02%)
- base min/max 0.90593/1.00536 → pv 0.90596/1.00539 rise 0.00003
- base max line 8.77% (OH-1) → pv 8.77% delta 0, base max trafo 92.8% T7 → pv 92.80%
- source P 4178.44 → 4173.20 kW delta -5.24kW (load offset), losses 442.35→442.12 -0.24kW
- reverse 0, constraint none → **SAFE**
- Calculation: max 1.00539<1.03, min 0.90596>0.90, delta 0.00019<0.03, line 8.77<80, trafo 92.80<95, no reverse ⇒ SAFE.

### SAFE-2 S003 — 30kW small commercial
- pv_bus 708, 0/30kW total 30kW
- base 0.95802 → pv 0.95972 delta +0.00170
- source 4178.44→4146.?? (approx -31kW), trafo 92.78%
- No caution band hit → SAFE.

### SAFE-3 S011 — LV secondary 720 (T2)
- pv_bus 720 (0.24kV, T2, load 66kW), 0/5kW
- base 0.99457 → pv 0.99473 delta +0.00016
- pv trafo 92.80% <95, max 1.00540<1.03 → SAFE.

### SAFE-4 S026 — mid-feeder 739 (T6) 5kW
- pv_bus 739 (0.24kV, T6), 0/5kW
- delta +0.00042, source -5.3kW, losses -0.3kW, reverse 0 → SAFE.

### SAFE-5 S036 — far branch 756 LV 5kW
- pv_bus 756 (0.208kV, T11 300kVA), 5kW
- delta +0.00035, trafo 92.8% → SAFE. Demonstrates far LV still SAFE at low penetration.

---

## 5 CAUTION examples (no hard, but caution band)

### CAUTION-1 S004 — 708 with 100kW reverse onset
- pv_bus 708, 0/100kW delta +0.00371, pv trafo 92.73%
- max 1.005xx, but reverse_power_flow=1 (line/T6 reversal: local export > load) reason “line 12 reversed …”
- Rule: max<1.03, trafo<95, delta<0.03, but reverse=1 ⇒ **CAUTION** (reverse; constraint_reason “reverse flow”).

### CAUTION-2 S060 — 770 far end 250kW rise caution (not yet CONSTRAINED by trafo)
- pv_bus 770 (0.24kV, T15, load 450kW), 0/250kW delta **+0.03015** (3.01%), pv 0.951→0.981
- max voltage 1.007, trafo 92.19% <95, line 8.7% <80, but delta 0.03015 >=0.03 ⇒ **CAUTION** reason “rise 0.0301>=0.03”.
- Not CONSTRAINED because delta <0.05 and trafo <100 (large load absorbs). Shows hosting capacity headroom at 770.

### CAUTION-3 S018 — 728 with 50kW early reverse
- pv_bus 728 (0.24kV, T3 75kVA, load 38kW), 0/50kW delta +0.00977, local T3 loading would rise but global worst T7 92.67% <95
- reverse=1 ⇒ CAUTION. Demonstrates small trafo triggers reverse at 50kW.

### CAUTION-4 S044 — 759 100kW reverse
- pv_bus 759 (0.24kV, T12 150kVA), 0/100kW delta +0.0122, trafo global 92.42% but local T12 ~80%+ reverse ⇒ CAUTION.

### CAUTION-5 S076 — existing PV test (BASE 5 + NEW 50)
- pv_bus 770, existing 5kW, new 50kW total 55kW
- base_pv 0.95125 (base includes 5kW) → pv 0.95754 delta +0.00629 (BASE/PV separation correct)
- source base ~4173kW (with 5kW) → pv 4120kW delta -53kW, reverse 1 ⇒ CAUTION.
- Proves BASE includes existing and delta is incremental, not total.

Calculation for CAUTION: check hard first (max 1.005-1.008 <1.05, min >0.90, delta <0.05, loading <100) → no hard. Then see if any caution: reverse or rise≥0.03 or loading≥80/95 → if yes ⇒ CAUTION.

---

## 5 CONSTRAINED examples (hard violated)

### CONSTRAINED-1 S020 — 728 250kW overloads T3
- pv_bus 728 (T3 75kVA Y-Y 24.94/0.24kV, load 38kW), 0/250kW delta +0.04518 (!), pv_pv 0.95→0.997
- **pv_max_trafo_loading 289.6% at T3** (worst_trafo T3) exceeds 100%
- base T7 92.8% → pv local T3 reverse-export 212kW >> rating
- max voltage 1.008 <1.05, but trafo hard violated ⇒ **CONSTRAINED**, constraint_type transformer_loading, reason “Transformer T3 loading 289.6% exceeds 100.0%”.
- This is physical: 250kW on 75kVA LV trafo is ~3.3× overload — correct flag.

### CONSTRAINED-2 S025 — 739 250kW overloads T6
- pv_bus 739 (T6 150kVA), 250kW → pv_max_trafo 139.1% T6 ⇒ CONSTRAINED.

### CONSTRAINED-3 S035 — 748 250kW overloads T8
- pv_bus 748 (T8 150kVA, load 76kW), 250kW → 121.9% T8 ⇒ CONSTRAINED.

### CONSTRAINED-4 S045 — 759 250kW overloads T12
- pv_bus 759 (T12 150kVA), 250kW → 148.9% T12 ⇒ CONSTRAINED.

### CONSTRAINED-5 S050 — 764 250kW overloads T14
- pv_bus 764 (T14 150kVA), 250kW → 141.7% T14 ⇒ CONSTRAINED.

*6th CONSTRAINED S055 769/T22 similar omitted for brevity.*

All CONSTRAINED deltas are largest in dataset (0.02-0.045 pu), confirming stress test finds hosting limit. Voltage alone never hits 1.05; overload dominates — documented.

---

## Takeaway

- 5→30kW: SAFE (Δ 0.0001-0.0017, no violation)
- 50-100kW: CAUTION via reverse or Δ 0.01-0.02
- 250kW on small trafos: CONSTRAINED via trafo >100% — correct deterministic labeling.
- BASE/PV deltas always = pv - base with sign, retained.

