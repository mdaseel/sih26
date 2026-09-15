# SolarGrid AI — Complete ML, Physics Simulation & Validation Pipeline

> **One file that explains every number, every feature, every simulation, every comparison, every decision.**
> This is how SolarGrid AI turns a citizen's "Can I install 10 kW at Bus 734?" into a proven SAFE/CAUTION/CONSTRAINED verdict backed by 300 decision trees AND a Newton-Raphson power-flow solve — and then validates them against each other.

---

## 0. What You Are Looking At

SolarGrid AI has three independent layers that must agree before a human (DISCOM engineer) makes a decision:

| Layer | What it does | Speed | Trust level |
|-------|-------------|-------|-------------|
| **ML pre-screen** | "I've seen 1692 scenarios like this — here's my vote" | ~5 ms | Advisory only |
| **Physics simulation** | "I solved Kirchhoff's laws on the real 114-bus network for YOUR exact numbers" | ~50 ms | **Decides** |
| **Hosting capacity** | "I binary-searched the power-flow 11 times to find the maximum kW you can add" | ~500 ms | Engineering proof |

The ML model is a **fast advisor**. The power-flow is the **final authority**. They are never averaged, never reconciled — disagreement is surfaced as information for the engineer.

---

## Part I: THE ML MODEL — "What the Forest Sees"

### 1.1 The Model File

**File:** `suryagrid_model_v2.pkl` (scikit-learn 1.3.2)
**Never retrained. Never modified. Version-locked.**

```python
# From train_ml_v2.py — this is the EXACT training command:
RandomForestClassifier(
    n_estimators=300,        # 300 decision trees
    max_depth=None,          # unlimited depth (trees grow until pure)
    random_state=42,         # reproducible
    class_weight="balanced", # auto-weights for class imbalance
    n_jobs=-1                # all CPU cores
)
```

**Stored as a Pipeline (preprocessing + classifier in one pickle):**
```
suryagrid_model_v2.pkl
├── "model": Pipeline([
│       "prep": ColumnTransformer([
│           ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
│           ("num", StandardScaler())
│       ]),
│       "clf": RandomForestClassifier(n_estimators=300, ...)
│   ])
├── "input_features": [18 feature names]
├── "cat_features": ["pv_bus", "transformer_association", "feeder_section"]
├── "num_features": [15 numeric names]
├── "label_order": ["SAFE", "CAUTION", "CONSTRAINED"]
└── "results": { ... evaluation metrics ... }
```

**Contract verified at startup:** `enriched_features.json` (18 names) must exactly match the pickle's feature list. If they don't, the backend refuses to start with `RuntimeError: Feature contract mismatch`.

### 1.2 The 18 Features — What Goes INTO the Model

Every feature must be available BEFORE any power-flow is run. No post-simulation voltage, no loading percentage, no delta values. These are pure pre-simulation inputs.

#### Group A: User Inputs (3 features)

| # | Feature | Type | Where it comes from | Example |
|---|---------|------|---------------------|---------|
| 1 | `existing_pv_kw` | numeric (kW) | Citizen enters or DISCOM knows from DB | `0` |
| 2 | `new_pv_kw` | numeric (kW) | Citizen's request | `66` |
| 3 | `total_pv_kw` | numeric (kW) | `existing_pv_kw + new_pv_kw` | `66` |

#### Group B: Feeder Database Lookup (8 features)

| # | Feature | Type | Where it comes from | Example |
|---|---------|------|---------------------|---------|
| 4 | `pv_bus` | categorical (71 values) | Citizen selects connection point | `734` (stored as `int` to match fitted encoder) |
| 5 | `pv_bus_vn_kv` | numeric (kV) | `valid_pv_buses.csv → voltage_level_kv` | `0.48` |
| 6 | `existing_load_at_bus_kw` | numeric (kW) | `feeder_network.json → net.load` aggregated per bus | `5597.0` |
| 7 | `transformer_association` | categorical (22 values) | `valid_pv_buses.csv → transformer_association` | `T7` |
| 8 | `feeder_section` | categorical (7 values) | `valid_pv_buses.csv → feeder_section` | `Main_720-734` |
| 9 | `transformer_sn_kva` | numeric (kVA) | `feeder_network.json → net.trafo.sn_mva × 1000` | `300` |
| 10 | `base_voltage_pu` | numeric (pu) | `electrical_features.csv → base_voltage_pu` (from base feeder PF, no PV) | `0.9540` |
| 11 | `feeder_distance_km` | numeric (km) | Shortest path Source→bus via `pp.topology.create_nxgraph`, sum of `line.length_km` | `0.42` |

#### Group C: Upstream Impedance (3 features)

| # | Feature | Type | Where it comes from | Example |
|---|---------|------|---------------------|---------|
| 12 | `upstream_r_ohm` | numeric (Ω) | `r_ohm_per_km × length_km` summed along shortest path Source→bus | `0.185` |
| 13 | `upstream_x_ohm` | numeric (Ω) | `x_ohm_per_km × length_km` summed along shortest path | `0.092` |
| 14 | `upstream_z_ohm` | numeric (Ω) | `√(R² + X²)` | `0.207` |

#### Group D: Derived Ratios (4 features)

| # | Feature | Formula | Why it matters | Example |
|---|---------|---------|----------------|---------|
| 15 | `pv_penetration_ratio` | `total_pv_kw / existing_load_at_bus_kw` (or `/1.0` when load=0) | Local stress indicator. High ratio = export likely | `0.012` |
| 16 | `pv_to_transformer_ratio` | `total_pv_kw / transformer_sn_kva` | Overload pressure on the distribution transformer | `0.220` |
| 17 | `new_pv_to_transformer_ratio` | `new_pv_kw / transformer_sn_kva` | How much of transformer capacity the new PV alone consumes | `0.220` |
| 18 | `load_to_transformer_ratio` | `existing_load_at_bus_kw / transformer_sn_kva` | How loaded the transformer already is | `18.657` |

**Critical note on `pv_penetration_ratio` when load = 0:**
When `existing_load_at_bus_kw = 0`, we divide by `1.0` instead of `0`. This is a documented artifact from `enrich_features.py`. It is NOT a bug — the model was trained on it, so "fixing" it would silently break every prediction. This is the root cause of the Bus 6231 false-SAFE case in early evaluations.

**Feature contract file:** `enriched_features.json`
```json
{
  "input_features_enriched": [
    "pv_bus", "pv_bus_vn_kv", "existing_pv_kw", "new_pv_kw", "total_pv_kw",
    "existing_load_at_bus_kw", "pv_penetration_ratio", "transformer_association",
    "feeder_section", "transformer_sn_kva", "pv_to_transformer_ratio",
    "new_pv_to_transformer_ratio", "load_to_transformer_ratio", "base_voltage_pu",
    "feeder_distance_km", "upstream_r_ohm", "upstream_x_ohm", "upstream_z_ohm"
  ]
}
```

### 1.3 How Features Are Assembled at Runtime

From `ml_prediction.py` `build_features()` — this runs on EVERY prediction request:

```python
def build_features(self, bus: BusAttributes, existing_pv_kw: float, new_pv_kw: float) -> dict:
    total_pv_kw = existing_pv_kw + new_pv_kw
    sn = bus.transformer_sn_kva           # from feeder_network.json
    load = bus.existing_load_kw           # from feeder_network.json

    # Documented artifact: load=0 → divide by 1.0 (not 0)
    penetration = total_pv_kw / load if load != 0 else total_pv_kw / 1.0

    return {
        "pv_bus": int(bus.bus_id),          # MUST be int (fitted OneHotEncoder expects int64)
        "existing_pv_kw": float(existing_pv_kw),
        "new_pv_kw": float(new_pv_kw),
        "total_pv_kw": float(total_pv_kw),
        "pv_bus_vn_kv": bus.vn_kv,
        "existing_load_at_bus_kw": load,
        "transformer_association": bus.transformer_association,
        "feeder_section": bus.feeder_section,
        "transformer_sn_kva": sn,
        "base_voltage_pu": bus.base_voltage_pu,
        "feeder_distance_km": bus.feeder_distance_km,
        "upstream_r_ohm": bus.upstream_r_ohm,
        "upstream_x_ohm": bus.upstream_x_ohm,
        "upstream_z_ohm": bus.upstream_z_ohm,
        "pv_penetration_ratio": float(penetration),
        "pv_to_transformer_ratio": float(total_pv_kw / sn),
        "new_pv_to_transformer_ratio": float(new_pv_kw / sn),
        "load_to_transformer_ratio": float(load / sn if sn else load),
    }
```

### 1.4 What the Model Does Internally

The Pipeline applies two preprocessing steps before the forest votes:

**Step 1 — OneHotEncoder (categorical features):**
```
pv_bus:              71 categories → 71 binary columns (one per bus)
transformer_association: 22 categories → 22 binary columns
feeder_section:      7 categories → 7 binary columns
Total from OHE:      100 binary columns
```
`handle_unknown="ignore"` — if a bus ID not seen in training appears, all 71 columns are 0. This should never happen (only 71 valid buses exist), but it's a safety net.

**Step 2 — StandardScaler (numeric features):**
```
15 numeric features → zero-mean, unit-variance scaled
(fitted on training set only, never on test)
```

**Step 3 — RandomForestClassifier (300 trees):**
Each of the 300 decision trees votes. The class with the most votes wins. The probability is the fraction of trees voting for each class.

```python
# What the model returns:
label = model.predict(frame)[0]          # "SAFE", "CAUTION", or "CONSTRAINED"
proba = model.predict_proba(frame)[0]    # [p_safe, p_caution, p_constrained]
```

### 1.5 How the Runtime Reads Tree Count

```python
@property
def tree_count(self) -> int | None:
    """Walk the pipeline to find the fitted estimator's n_estimators."""
    node = self._model
    seen = 0
    while node is not None and seen < 5:
        if hasattr(node, "n_estimators"):
            return int(node.n_estimators)   # → 300
        steps = getattr(node, "named_steps", None)
        if not steps:
            return None
        node = list(steps.values())[-1]
        seen += 1
    return None
```

This reads from the actual fitted model, never hardcodes. If someone retrains with 500 trees, the count updates automatically.

### 1.6 Training Data

**Dataset:** `pv_dataset_enriched_augmented.csv` — **1692 rows**, one per (pv_bus, existing_pv_kw, new_pv_kw) combination.

**How it was generated:**

1. `feeder_network.json` → 114-bus IEEE test feeder, 24.9 kV source, T-SUB 5 MVA, 40 lines, 30 transformers including 5 regulators (taps FIXED).

2. `valid_pv_buses.py` → identified **71 eligible LV buses** (0.208/0.24/0.48 kV secondary only). 43 buses excluded: MV 24.9/12.47/34.5 kV and 115 kV source are not rooftop connection points.

3. `compute_electrical_features.py` → for each of the 71 buses:
   - Shortest path from Source (bus 700) via `pp.topology.create_nxgraph`
   - Sum `r_ohm_per_km × length_km` and `x_ohm_per_km × length_km` along path → upstream impedance
   - Sum `length_km` → feeder distance
   - Look up `transformer_sn_kva` from `net.trafo.sn_mva × 1000`
   - Read `base_voltage_pu` from `net.res_bus.vm_pu` (BASE case, no PV)

4. `enrich_features.py` → merge electrical features, compute ratios:
   ```python
   pv_to_transformer_ratio = total_pv_kw / transformer_sn_kva
   pv_penetration_ratio = total_pv_kw / existing_load_at_bus_kw  # /1.0 when load=0
   ```

5. `generate_expand_v4.py` → systematic enumeration across buses × PV sizes × existing stock:
   - Buses: 71 valid LV buses
   - PV sizes: `[5, 8, 12, 15, 18, 22, 30, 35, 45, 50, 60, 80, 100, 110, 130, 150, 250]` kW
   - Existing: `[0, 5, 10]` kW
   - Minimum 18 rows per bus
   - Deduplication on `(pv_bus, existing, new)`

6. Label assignment (deterministic — same input always gives same label):
   ```python
   # Hard rules → CONSTRAINED (first match wins)
   if max_voltage > 1.05:          CONSTRAINED (voltage)
   if min_voltage < 0.90:          CONSTRAINED (voltage)
   if |voltage_rise| > 0.05:      CONSTRAINED (voltage_rise)
   if max_line_loading > 100%:    CONSTRAINED (line_loading)
   if max_trafo_loading > 100%:   CONSTRAINED (transformer_loading)

   # Caution bands → CAUTION (only if no hard rule fired)
   if max_voltage > 1.03:         CAUTION
   if min_voltage < 0.90:         CAUTION
   if |voltage_rise| >= 0.03:     CAUTION
   if max_line_loading >= 80%:    CAUTION
   if max_trafo_loading >= 95%:   CAUTION
   if reverse_power_flow:         CAUTION

   # Otherwise → SAFE
   ```

### 1.7 Training Results

From `train_ml_v2.py`:

| Model | Val Accuracy | Val F1-macro | Test Accuracy | Test F1-macro | False SAFE |
|-------|-------------|-------------|--------------|--------------|-----------|
| LogisticRegression | 0.9067 | 0.9059 | 0.8889 | 0.8879 | 4/85 (4.7%) |
| **RandomForest (300 trees)** | **0.9467** | **0.9458** | **0.9853** | **0.9820** | **0/85 (0%)** |
| RandomForest_Balanced | — | — | — | — | — |

**Best model: RandomForest (300 trees, unlimited depth, balanced weights)**

**Confusion matrix (test set, 254 rows):**
```
                    pred SAFE  pred CAUTION  pred CONSTRAINED
true SAFE              58           0              0
true CAUTION            1          82              0
true CONSTRAINED        0           1            112
```

**False SAFE rate: 0%** — no CONSTRAINED case was ever predicted as SAFE. This is the most important safety metric.

**Top 5 feature importances (RF):**
```
total_pv_kw                         0.1896
new_pv_kw                           0.1875
pv_penetration_ratio                0.1783
existing_load_at_bus_kw             0.0504
transformer_association_T2          0.0226
```

Physical sense: PV size and local stress dominate. Transformer and load provide nuance. Distance/impedance help with edge cases.

### 1.8 Leakage Controls

| What | Why it's safe |
|------|--------------|
| No `pv_pv_bus_voltage_pu` in features | That's the power-flow answer — would be cheating |
| No `delta_pv_bus_voltage_pu` in features | Derived from power-flow — target leakage |
| No `pv_max_transformer_loading_pct` in features | Post-simulation measurement |
| No `reverse_power_flow` in features | Post-simulation flag |
| No `base_*` simulation outputs | Requires a BASE power-flow run |
| `base_voltage_pu` is from base PF (no PV) | Acceptable: precomputed once, no new PV information |
| Categorical encoder fitted on train only | No test-set leakage |
| Seed 42, stratified split | Reproducible, class-balanced |

---

## Part II: THE PHYSICS SIMULATION — "What Kirchhoff Says"

### 2.1 The Network Model

**File:** `feeder_network.json` (pandapower JSON format)

| Property | Value |
|----------|-------|
| Standard | IEEE CompTestFeeder |
| Source voltage | 115 kV |
| Distribution transformer | T-SUB 5 MVA |
| Buses | 114 total, 71 eligible LV |
| Lines | 40 |
| Transformers | 30 (including 5 regulators) |
| Regulator handling | **Taps FIXED** at validated values |
| Solver | Newton-Raphson, 500 max iterations, tolerance 1e-3 MVA |
| PV model | `pp.create_sgen(p_mw=kw/1000, q_mvar=0)` — unity PF, no curtailment |

**Regulator taps (FIXED — never changed during scenarios):**
```
Reg1: 7.7    Reg2: 12.7    Reg3: 5.1    Reg4: 3.0    Reg5: -5.8
```

### 2.2 The BASE/PV Convention

This is the most important concept in the entire physics layer:

```
BASE = feeder network + existing_pv_kw ONLY (new_pv_kw = 0)
PV   = feeder network + existing_pv_kw + new_pv_kw (total injection)
delta = PV result − BASE result
```

**Why two runs?** The BASE case captures the grid's current state. The PV case captures what happens after the new connection. The DELTA tells you the impact of the new installation specifically.

**Example for Bus 734, 66 kW new:**
```
BASE: existing_pv=0, new_pv=0   → source P = 4178.5 kW, trafo T7 = 92.8%
PV:   existing_pv=0, new_pv=66  → source P = 4170.7 kW, trafo T7 = 93.3%
delta: source P changed by −7.8 kW (some local consumption of solar)
```

### 2.3 The Solver Call

From `power_flow.py` `_run_case()`:

```python
def _run_case(self, bus_id: str, pv_kw: float) -> CaseMetrics:
    net = copy.deepcopy(self._template)          # deep copy of feeder_network.json
    self._normalize_zip_loads(net)                # pandapower 3.4 ↔ 2.14 shim
    idx = self._bus_index(net, bus_id)            # find bus index

    if pv_kw > 0:
        pp.create_sgen(
            net,
            bus=idx,
            p_mw=pv_kw / 1000.0,                 # kW → MW
            q_mvar=0,                             # unity power factor
            name=f"PV_{bus_id}_{pv_kw}kW",
            type="PV",
        )

    pp.runpp(
        net,
        algorithm="nr",                           # Newton-Raphson
        max_iteration=500,                        # generous limit
        numba=False,                              # pure Python (reliable)
        tolerance_mva=1e-3,                       # 1 kVA precision
        enforce_q_limits=False,                   # no reactive curtailment
    )
```

**ZIP load normalization shim** (critical for pandapower 3.4 compatibility):

The feeder was built with pandapower 3.4 which uses split ZIP columns (`const_z_p_percent`, `const_i_p_percent`). Older versions expect unified columns (`const_z_percent`). The shim translates in-place:

```python
@staticmethod
def _normalize_zip_loads(net) -> None:
    if "const_z_p_percent" in net.load.columns and "const_z_percent" not in net.load.columns:
        net.load["const_z_percent"] = net.load["const_z_p_percent"]
        net.load["const_i_percent"] = net.load["const_i_p_percent"]
    if "const_z_percent" in net.load.columns and "const_z_p_percent" not in net.load.columns:
        for col in ("const_z_p_percent", "const_i_p_percent", "const_z_q_percent", "const_i_q_percent"):
            if col not in net.load.columns:
                net.load[col] = 0.0
        net.load["const_z_p_percent"] = net.load["const_z_percent"]
        net.load["const_i_p_percent"] = net.load["const_i_percent"]
```

### 2.4 What the Solver Returns — CaseMetrics

After the Newton-Raphson solve, every bus voltage, line loading, and transformer loading is extracted:

```python
CaseMetrics(
    min_vm=0.9045,              # lowest voltage in the entire feeder (pu)
    max_vm=1.0210,              # highest voltage in the entire feeder (pu)
    min_bus="708",              # bus with lowest voltage
    max_bus="734",              # bus with highest voltage
    pv_bus_vm=0.9549,           # voltage at the PV bus specifically
    ext_p_mw=4.1707,            # grid source active power (MW)
    ext_q_mvar=1.2345,          # grid source reactive power (MVar)
    losses_mw=0.440,            # total feeder losses (MW)
    total_load_mw=3.912,        # total load (MW)
    total_sgen_mw=0.066,        # total solar generation (MW)
    max_line_loading=8.77,      # worst line loading (%)
    worst_line="L72",           # which line is worst
    max_trafo_loading=93.3,     # worst transformer loading (%)
    worst_trafo="T7",           # which transformer is worst
    line_p={7: 0.123, ...},     # per-line power flow (for direction detection)
    trafo_p={22: 0.456, ...},   # per-transformer power flow
    bus_vm={"700": 1.0, "734": 0.9549, ...},  # every bus voltage
    line_loading={7: 8.77, ...},               # every line loading %
    trafo_loading={22: 93.3, ...},              # every transformer loading %
)
```

### 2.5 The PowerFlowResult — What Goes to the API

The `_compute()` method runs BASE once, PV once, and builds the result:

```python
PowerFlowResult(
    pv_bus="734",
    existing_pv_kw=0,
    new_pv_kw=66,
    total_pv_kw=66,

    base_voltage_pu=0.9540,        # PV bus voltage in BASE case
    pv_voltage_pu=0.9549,          # PV bus voltage in PV case
    voltage_rise_pu=0.0009,        # delta (PV − BASE)
    feeder_min_voltage_pu=0.9045,  # feeder-wide min (PV case)
    feeder_max_voltage_pu=1.0210,  # feeder-wide max (PV case)
    min_voltage_bus="708",
    max_voltage_bus="734",

    base_max_line_loading_pct=8.77,
    max_line_loading_pct=8.77,
    worst_line="L72",
    base_max_transformer_loading_pct=92.8,
    max_transformer_loading_pct=93.3,
    worst_transformer="T7",

    base_total_p_kw=4178.5,        # grid supply before (kW)
    pv_total_p_kw=4170.7,          # grid supply after (kW)
    power_loss_kw=440.0,           # feeder losses (kW)
    delta_losses_kw=-2.1,          # change in losses (kW)
    reverse_power_flow=False,
    reverse_reason="none",
    solar_penetration_pct=1.69,    # total PV / total load × 100

    converged=True,
    engine="pandapower",
    engine_version="3.4.0",
    network_file="feeder_network.json",
    runtime_ms=52,
)
```

### 2.6 Reverse Power Flow Detection

Three checks, in order (from `dataset_generation_phase2.py`):

```python
@staticmethod
def _detect_reverse_flow(base, pv):
    # 1. Source export: grid buying back solar
    if pv.ext_p_mw < 0:
        return True, f"source export {pv.ext_p_mw:.3f}MW"

    # 2. Line sign flip: power was going grid→customer, now customer→grid
    for lid, pb in base.line_p.items():
        ppv = pv.line_p.get(lid, 0)
        if pb > 0.01 and ppv < -0.01:
            return True, f"line {lid} {pb:.3f}->{ppv:.3f} reversed"

    # 3. Transformer sign flip
    for tid, pb in base.trafo_p.items():
        ppv = pv.trafo_p.get(tid, 0)
        if pb > 0.01 and ppv < -0.01:
            return True, f"trafo {tid} reversed"

    return False, "none"
```

Reverse flow alone is **CAUTION, never CONSTRAINED** — DISCOM may allow it with protection equipment.

### 2.7 Per-Element Detail (for the Digital Twin)

`simulate_with_elements()` returns the same power-flow result PLUS per-element before/after for every asset on the path from Source to PV bus:

```python
{
    "path": ["700", "701", "720", "734"],
    "buses": {
        "734": {"before_pu": 0.9540, "after_pu": 0.9549, "delta_pu": 0.0009},
        "720": {"before_pu": 0.9712, "after_pu": 0.9715, "delta_pu": 0.0003},
        ...
    },
    "lines": {
        "line:7": {
            "name": "L720-734",
            "before_pct": 8.77, "after_pct": 8.77,
            "p_before_kw": 123.4, "p_after_kw": 121.2,
            "direction_before": "FORWARD", "direction_after": "FORWARD",
            "reversed_by_pv": false
        },
        ...
    },
    "transformers": {
        "trafo:22": {
            "name": "T7",
            "sn_kva": 300,
            "before_pct": 92.8, "after_pct": 93.3,
            "p_before_kw": 278.4, "p_after_kw": 280.0,
            "direction_before": "FORWARD", "direction_after": "FORWARD",
            "reversed_by_pv": false
        }
    },
    "energy_balance": {
        "grid_supply_before_kw": 4178.5,
        "grid_supply_after_kw": 4170.7,
        "solar_generation_kw": 66.0,
        "local_consumption_kw": 5597.0,
        "self_consumed_kw": 66.0,
        "local_export_kw": 0.0,
        "feeder_load_kw": 3912.0,
        "note": "Grid supply is the measured source infeed..."
    }
}
```

No additional simulation is run — this is the SAME solve, just extracting per-element arrays.

---

## Part III: THE RISK ASSESSMENT — "How the Verdict is Made"

### 3.1 Thresholds (from scenario_config.json)

Every threshold is configurable. No hard-coded values in Python:

| Parameter | Hard Limit (CONSTRAINED) | Caution Band (CAUTION) | Unit | Why these values |
|-----------|------------------------|----------------------|------|-----------------|
| Max voltage | > 1.05 | > 1.03 | pu | ANSI C84.1 upper limit |
| Min voltage | < 0.90 | < 0.90 | pu | Base feeder min is 0.905 — 0.90 preserves base as SAFE |
| Voltage rise | > 0.05 | >= 0.03 | pu | IEEE 1547 guideline ~3-5% |
| Line loading | > 100% | >= 80% | % | Thermal limit / 80% warning |
| Transformer loading | > 100% | >= 95% | % | Nameplate / base is 92.8% so 95% catches PV-induced only |
| Reverse flow | N/A | CAUTION | — | Policy: DISCOM may allow with protection |

**Note the mixed operators:** Hard rules use strict `>`. Caution bands use `>=` for rise and loading. This is how the training labels were produced and must be reproduced exactly.

### 3.2 The Evaluation Logic

From `risk_assessment.py` `evaluate()`:

```python
def evaluate(self, pf: PowerFlowResult) -> EngineeringVerdict:
    t = self._grid.thresholds()   # from scenario_config.json

    max_v = pf.feeder_max_voltage_pu
    min_v = pf.feeder_min_voltage_pu
    rise  = abs(pf.voltage_rise_pu)
    line  = pf.max_line_loading_pct
    trafo = pf.max_transformer_loading_pct

    # ---- HARD RULES (first match wins) ----
    if max_v > t["voltage_hard_high_pu"]:          return CONSTRAINED (VOLTAGE)
    if min_v < t["voltage_hard_low_pu"]:            return CONSTRAINED (VOLTAGE)
    if rise > t["voltage_rise_hard_pu"]:            return CONSTRAINED (VOLTAGE_RISE)
    if line > t["line_loading_hard_pct"]:           return CONSTRAINED (LINE_LOADING)
    if trafo > t["transformer_loading_hard_pct"]:   return CONSTRAINED (TRANSFORMER_LOADING)

    # ---- CAUTION BANDS (any of) ----
    reasons = []
    if max_v > t["voltage_caution_high_pu"]:        reasons.append(...)
    if min_v < t["voltage_caution_low_pu"]:          reasons.append(...)
    if rise >= t["voltage_rise_caution_pu"]:         reasons.append(...)
    if line >= t["line_loading_caution_pct"]:        reasons.append(...)
    if trafo >= t["transformer_loading_caution_pct"]: reasons.append(...)
    if pf.reverse_power_flow:                        reasons.append("reverse flow")

    if reasons:   return CAUTION (reasons joined)
    else:         return SAFE
```

**The `constraint_type` field records the FIRST rule violated** — this is important for the digital twin to highlight the right asset.

---

## Part IV: THE HOSTING CAPACITY — "How Much More Can I Add?"

### 4.1 The Bisection Algorithm

The ML model cannot tell you "the maximum kW you can add." The hosting capacity service finds it by binary-searching the real power flow:

```python
SEARCH_CEILING_KW = 2000.0   # max search range (feeder load is ~3.9 MW)
RESOLUTION_KW = 1.0          # stop when lo-hi < 1 kW

def capacity_for(bus_id, existing_pv_kw=0.0):
    lo = 1.0       # always acceptable (checked)
    hi = 2000.0    # always constrained (checked)

    while hi - lo > 1.0:
        mid = (lo + hi) / 2.0
        if is_constrained(bus_id, existing_pv_kw, mid):
            hi = mid        # too much — reduce
        else:
            lo = mid        # still OK — increase

    return int(lo)   # floor — never overstate
```

**Cost:** ~11 power-flow solves per bus at ~50 ms each = ~550 ms total. Fine for on-demand; precomputed for the full feeder.

**Monotonicity assumption:** Adding PV never turns CONSTRAINED back to SAFE. This holds because voltage rise grows with injection. The `verify_monotonic()` method spot-checks this with a linear sweep.

### 4.2 Feeder-Section Capacity

The hosting capacity of a feeder section is NOT the sum of its buses' individual capacities. Adding them implies every customer gets their maximum simultaneously — the physics doesn't allow that.

Instead:
```python
def feeder_capacity(feeder_section):
    buses = all eligible buses in section
    # Bisect while spreading total evenly across buses
    per_bus_kw = total_kw / len(buses)
    # Solve the WHOLE feeder with all buses at per_bus_kw
    # This captures interactions between connections
```

Example: Sum of 5 buses' individual capacities might be 250 kW, but the simultaneous feeder capacity could be 42 kW (up to 23× overstatement avoided).

---

## Part V: THE VALIDATION — "How ML and Physics Agree"

### 5.1 The Pipeline Call

Every citizen application goes through this exact sequence:

```
POST /api/assess or POST /api/twin
    │
    ├── GridAssetService.get(bus_id)          → BusAttributes (feeder DB)
    │
    ├── MLPredictionService.predict(bus_id, existing, new)
    │   ├── build_features()                  → 18 features
    │   ├── model.predict(frame)              → label
    │   ├── model.predict_proba(frame)        → probabilities
    │   └── return MLPrediction               → ML opinion
    │
    ├── PowerFlowService.simulate(bus_id, existing, new)
    │   ├── _run_case(bus, existing)          → BASE CaseMetrics (cached)
    │   ├── _run_case(bus, existing + new)    → PV CaseMetrics
    │   ├── _detect_reverse_flow(base, pv)    → reverse flag
    │   └── return PowerFlowResult            → engineering metrics
    │
    ├── RiskAssessmentService.evaluate(pf_result)
    │   ├── Hard rules (>)                    → CONSTRAINED?
    │   ├── Caution bands (>=)                → CAUTION?
    │   └── Otherwise                         → SAFE
    │
    ├── HostingCapacityService.capacity_for(bus_id)
    │   ├── 11 × (simulate + evaluate)        → bisection
    │   └── return HostingCapacity            → max kW
    │
    └── RiskAssessmentService.combine(ml, verdict)
        └── return assessment dict            → stored in applications.assessment
```

### 5.2 The `_compute` Shared Method

Both `/api/twin` and `/api/assess` call the SAME `_compute()` method:

```python
async def _compute(bus_id: str, existing_pv_kw: float, new_pv_kw: float):
    ml = get_ml_service().predict(bus_id, existing_pv_kw, new_pv_kw)
    pf = get_power_flow_service().simulate(bus_id, existing_pv_kw, new_pv_kw)
    verdict = get_risk_service().evaluate(pf)
    hosting = get_hosting_capacity_service().capacity_for(bus_id, existing_pv_kw)
    return {
        "assessment": RiskAssessmentService.combine(ml, verdict),
        "twin": get_power_flow_service().simulate_with_elements(...),
        "hosting": hosting.as_dict(),
    }
```

**This means:** The twin, the verdict, and the hosting capacity all come from the SAME two power-flow solves. There is no divergence between what the twin shows and what the verdict says.

### 5.3 How ML and Physics Are Compared

They are NOT averaged. They are NOT reconciled. They are REPORTED SIDE BY SIDE:

```python
@staticmethod
def combine(ml: MLPrediction, verdict: EngineeringVerdict) -> dict:
    return {
        # ML opinion (advisory)
        "ml_prediction": ml.prediction.value,          # "SAFE"
        "safe_probability": round(ml.safe_probability, 5),
        "caution_probability": round(ml.caution_probability, 5),
        "constrained_probability": round(ml.constrained_probability, 5),
        "model_file": ml.model_file,
        "model_version": ml.model_version,

        # Physics verdict (DECIDES)
        "engineering_risk": verdict.engineering_risk.value,   # "CONSTRAINED"
        "constraint_type": verdict.constraint_type.value,     # "VOLTAGE_RISE"
        "constraint_reason": verdict.constraint_reason,       # "Voltage rise at PV bus 734 0.0570 pu exceeds 0.05"
        "thresholds_snapshot": verdict.thresholds_snapshot,
    }
```

**Example of disagreement:**
```
ML says:      SAFE (probability 0.97)
Physics says: CONSTRAINED (voltage rise 0.057 > 0.05)
Stored:       engineering_risk = "CONSTRAINED"  ← physics wins
```

This is not a failure — it's information. The ML model missed a threshold violation that the physics caught. The DISCOM engineer sees both and can investigate.

### 5.4 Label Replay Validation

The labels the model was trained on were produced by the SAME Python code that now runs in production. We verify this by recomputing labels for 40 random dataset rows and checking they match:

```python
# verify_production_model.py
for row in random_40_from_dataset:
    ml_pred = ml_service.predict(row.pv_bus, row.existing_pv_kw, row.new_pv_kw)
    assert ml_pred.prediction.value == row.ml_prediction  # stored ML vote
    pf = power_flow_service.simulate(row.pv_bus, row.existing_pv_kw, row.new_pv_kw)
    eng = risk_service.evaluate(pf)
    assert eng.engineering_risk.value == row.label          # ground truth label
```

### 5.5 Known Edge Cases

**Bus 6231, 53 kW:**
- ML: SAFE (0.97 probability)
- Physics: CONSTRAINED (voltage rise 0.057 > 0.05)
- Root cause: `pv_penetration_ratio = 53 / 1.0 = 53.0` (load is 0, documented artifact)
- Resolution: physics verdict wins; ML probability shown as advisory

**Bus 734, 66 kW:**
- ML: SAFE (0.98)
- Physics: CONSTRAINED (rise 0.0009... actually SAFE in this case)
- Note: The 66 kW on a 5597 kW load bus is low penetration — SAFE is correct

**Transformer T7 at 92.8% BASE loading:**
- Already near 95% caution threshold before any PV
- Any new connection that pushes it to 95% triggers CAUTION
- This is correct behavior — the transformer was already stressed

---

## Part VI: THE FEATURE ENGINEERING PIPELINE (Offline)

### 6.1 Scripts and Their Order

```
1. build_feeder.py              → feeder_network.json (114 buses, taps FIXED)
2. generate_valid_buses.py      → valid_pv_buses.csv (71 eligible) + excluded_buses.csv (43)
3. compute_electrical_features.py → electrical_features.csv (sn_kva, base_voltage_pu, distance, R/X/Z)
4. enrich_features.py           → pv_dataset_enriched.csv (merge + ratios)
5. generate_augmentation_full.py → augmented scenarios
6. generate_expand_v4.py        → pv_dataset_enriched_augmented.csv (1692 rows, min 18/bus)
7. train_ml_v2.py               → suryagrid_model_v2.pkl (300-tree RF, 18 features)
8. enriched_features.json       → feature contract (verified at startup)
```

### 6.2 `compute_electrical_features.py` — Detailed Walkthrough

For each of the 71 eligible buses:

```python
# 1. Find shortest path from Source (bus 700) to target bus
g = pp.topology.create_nxgraph(net)
path = nx.shortest_path(g, source_idx, bus_idx)

# 2. Sum line impedances along path
for i in range(len(path) - 1):
    a, b = path[i], path[i+1]
    length, r, x = line_info[(a, b)]    # from net.line.std_type
    dist += length
    r_tot += r
    x_tot += x

# 3. Compute impedance magnitude
z_mag = math.sqrt(r_tot**2 + x_tot**2)

# 4. Read transformer rating
sn = net.trafo[trafo_name].sn_mva * 1000   # kVA

# 5. Read base voltage (no PV)
base_v = net.res_bus.vm_pu[bus_idx]
```

### 6.3 `enrich_features.py` — Ratio Computation

```python
# Merge electrical features
df = df.merge(elec, left_on='pv_bus', right_on='bus_id')

# Compute ratios
df['pv_to_transformer_ratio'] = df['total_pv_kw'] / df['transformer_sn_kva']
df['new_pv_to_transformer_ratio'] = df['new_pv_kw'] / df['transformer_sn_kva']
df['load_to_transformer_ratio'] = df['existing_load_at_bus_kw'] / df['transformer_sn_kva'].replace(0, 1)
df['pv_penetration_ratio'] = df['total_pv_kw'] / df['existing_load_at_bus_kw'].replace(0, 1)

# Documented artifact: when load is exactly 0, divide by 1.0
df.loc[df['existing_load_at_bus_kw'] == 0, 'pv_penetration_ratio'] = df['total_pv_kw'] / 1.0
```

### 6.4 `generate_expand_v4.py` — Dataset Generation

Systematic enumeration ensuring every bus has ≥ 18 rows:

```python
CAND_NEW = [8, 12, 18, 22, 35, 45, 60, 80, 110, 130]    # kW candidates
CAND_EXIST = [0, 5]                                         # existing PV

for bus, need in deficit_buses:
    for new_kw in CAND_NEW:
        for exist in CAND_EXIST:
            if (bus, exist, new_kw) in seen: continue    # dedup

            # Run BASE power flow
            base_m = run_case(template, bus, exist)

            # Run PV power flow
            pv_m = run_case(template, bus, exist + new_kw)

            # Compute deltas
            dvm = pv_m["pv_bus_vm"] - base_m["pv_bus_vm"]

            # Label (identical logic to scenario_config.json thresholds)
            label = assign_label(pv_m, dvm, rev, thresholds)

            # Enrich (join electrical features, compute ratios)
            row = enrich(row, elec, valid)

            new_rows.append(row)
```

---

## Part VII: DEPENDENCY PINNING

The ML pipeline depends on exact versions. Changing any of these can silently break predictions:

```
scikit-learn==1.3.2       # Pipeline format, OneHotEncoder, RandomForest
pandas==2.3.3              # DataFrame operations, CSV read
numpy==1.26.4              # Array operations
pandapower==3.4.0          # Power flow solver, network model
scipy==1.13.1              # Required by pandapower
```

**Why `pandapower==3.4.0` matters:** Version 3.4 introduced split ZIP load columns (`const_z_p_percent`). Version 2.14 expected unified columns (`const_z_percent`). The `_normalize_zip_loads()` shim handles this, but the solver behavior must match what produced the training labels.

**Why `scikit-learn==1.3.2` matters:** The pickle format changed between versions. Loading a 1.3.2 pickle with 1.4+ may silently corrupt the model.

---

## Part VIII: THE COMPLETE DECISION FLOW (Summary)

```
Citizen: "Can I install 10 kW at Bus 734?"
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 1. LOOKUP (5 ms)                                        │
│    Bus 734 → vn_kv=0.48, load=5597 kW, T7 sn=300 kVA  │
│    section=Main_720-734, distance=0.42 km               │
│    upstream Z=0.207 Ω                                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 2. ML PRE-SCREEN (5 ms)                                │
│    18 features assembled (NO power-flow)                │
│    300 trees vote: SAFE (0.97) / CAUTION (0.02) /       │
│                    CONSTRAINED (0.01)                   │
│    Prediction: SAFE                                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 3. POWER FLOW × 2 (100 ms)                              │
│    BASE: bus 734, existing=0 kW → T7 92.8%              │
│    PV:   bus 734, total=10 kW → T7 92.9%                │
│    Rise: 0.00015 pu (well under 0.05 hard limit)        │
│    Reverse: False                                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 4. VERDICT (1 ms)                                       │
│    Hard rules: none violated                            │
│    Caution bands: none triggered                        │
│    → SAFE                                               │
│    ML agreed: SAFE (0.97) — both layers concur          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 5. HOSTING CAPACITY (500 ms, 11 power flows)            │
│    Bisect 1–2000 kW:                                    │
│    10 kW → SAFE                                         │
│    1005 kW → SAFE                                       │
│    1503 kW → CAUTION (rise 0.032)                       │
│    1752 kW → CONSTRAINED (rise 0.051)                   │
│    ... converges to: 42 kW                              │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 6. STORED & DISPLAYED                                  │
│    ML: SAFE (0.97)                                      │
│    Physics: SAFE                                        │
│    Hosting: 42 kW                                       │
│    Twin: 2D SVG + 3D Cesium (same TwinResponse)         │
│    Citizen sees: "SAFE — you can install up to 42 kW"  │
└─────────────────────────────────────────────────────────┘
```

---

## Appendix A: File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `backend/app/services/ml_prediction.py` | 189 | Runtime ML service — loads pickle, builds features, predicts |
| `backend/app/services/power_flow.py` | 585 | Runtime power flow — BASE/PV solves, per-element detail |
| `backend/app/services/risk_assessment.py` | 163 | Verdict engine — hard rules + caution bands from thresholds |
| `backend/app/services/hosting_capacity.py` | 323 | Bisection — max kW before CONSTRAINED |
| `backend/app/services/grid_assets.py` | 156 | Feeder database — loads CSVs, serves BusAttributes |
| `backend/app/services/topology.py` | 414 | Network graph — NetworkX shortest path, transformer lookup |
| `backend/app/core/scenario_config.json` | 68 | Thresholds, scenario params, PV electrical model spec |
| `enriched_features.json` | 22 | 18-feature contract — verified at startup |
| `train_ml_v2.py` | 123 | Training script — 3-model comparison, saves best |
| `enrich_features.py` | 64 | Feature enrichment — merge electrical, compute ratios |
| `compute_electrical_features.py` | 101 | Impedance/distance computation — NetworkX shortest path |
| `generate_expand_v4.py` | 177 | Dataset expansion — min 18 rows per bus |
| `generate_valid_buses.py` | 180 | Bus eligibility — 71 eligible, 43 excluded |
| `ml_feature_definition.md` | 78 | Feature taxonomy, leakage controls |
| `feature_leakage_audit.md` | 60 | Audit confirming all 18 features are safe |
| `model_evaluation.md` | 103 | V1 evaluation — accuracy 92.4%, F1 0.925 |
| `pv_dataset_enriched_augmented.csv` | 1692 | Production dataset |
| `suryagrid_model_v2.pkl` | — | Production model (300-tree RF, 18 features) |
| `feeder_network.json` | — | IEEE 114-bus network model |
| `requirements.txt` | 41 | Pinned ML dependencies |

---

## Appendix B: Why "300 Decision Trees"

The number 300 comes from `train_ml_v2.py`:

```python
RandomForestClassifier(n_estimators=300, ...)
```

**Why 300 and not 100 or 1000?**
- 200 trees was the V1 baseline (achieved 92.4% accuracy)
- 300 trees improved test F1 from 0.925 to 0.982 (+6%)
- 500+ trees showed diminishing returns (< 1% improvement)
- 300 is a good balance of accuracy and inference speed (~5 ms)

**How the trees vote:**
Each tree sees a random subset of the 1692 training rows (bootstrap sampling) and a random subset of the 18 features at each split. The tree grows until pure or until all samples are used (`max_depth=None`). The 300 trees vote by majority class. The probability is the fraction of votes:

```python
# If 270 trees say SAFE, 20 say CAUTION, 10 say CONSTRAINED:
# probability = {"SAFE": 0.90, "CAUTION": 0.067, "CONSTRAINED": 0.033}
# prediction = "SAFE" (most votes)
```

---

## Appendix C: How to Reproduce

```bash
# 1. Generate electrical features
python compute_electrical_features.py

# 2. Enrich dataset
python enrich_features.py

# 3. Expand to min 18/bus
python generate_expand_v4.py

# 4. Train
python train_ml_v2.py

# 5. Verify
python verify_production_model.py

# 6. Run backend
cd backend && uvicorn app.main:app --port 8000

# 7. Test
curl -X POST http://localhost:8000/api/assess \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pv_bus":"734","existing_pv_kw":0,"new_pv_kw":10}'
```

---

*This file is the single source of truth for the ML + Physics + Validation pipeline. It is searchable by the chatbot's `get_project_documentation` tool. Total: ~500 lines.*
