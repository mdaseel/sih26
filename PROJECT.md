# SolarGrid AI — Complete Project Documentation
### Smart India Hackathon 2026 | Problem Statement: Rooftop Solar Hosting Capacity Assessment

---

## 1. What Is This Project?

**SolarGrid AI** is a full-stack, production-grade web platform that solves one of the most critical barriers to India's PM Surya Ghar Muft Bijli Yojana scheme: **no homeowner or DISCOM knows in advance whether the local distribution grid can handle a new rooftop solar installation.**

Today, a citizen submits a solar connection request and waits weeks — sometimes months — for a manual engineering review. Approvals are inconsistent. Grid overloads from uncoordinated solar installations are already causing real problems in states with high adoption.

SolarGrid AI answers the question **in seconds**, using actual power-flow simulation backed by machine learning, and gives every stakeholder — citizen, installer, and DISCOM engineer — the right information at the right time.

---

## 2. The Problem We Are Solving

- India has a target of **500 GW** of renewable energy by 2032. A significant chunk depends on rooftop solar.
- PM Surya Ghar Yojana targets **1 crore households**. Each one needs a grid connection approval.
- DISCOMs are overwhelmed. Manual reviews delay approvals by weeks and lack technical rigor.
- Unscreened installations cause **voltage rise, reverse power flow, transformer overloading** — physical damage to the grid.
- Citizens have no transparency into why their application was rejected or approved.

**SolarGrid AI** automates the technical screening so DISCOMs can process applications in seconds, not weeks, with a defensible engineering record for every decision.

---

## 3. How the Assessment Engine Works (The Core Innovation)

This is not a simple rule-based check. The system runs a **dual-layer assessment pipeline** for every application:

### Layer 1 — ML Pre-Screen (milliseconds)

- Model: `suryagrid_model_v2.pkl` — a **RandomForest classifier** inside a scikit-learn `Pipeline` (OneHotEncoder + StandardScaler + RandomForest)
- **18 input features** assembled without running any simulation:

| Feature | Source |
|---|---|
| `pv_bus` | User input (encoded as int64 to match training) |
| `existing_pv_kw`, `new_pv_kw`, `total_pv_kw` | User input |
| `pv_bus_vn_kv` | Static bus database |
| `existing_load_at_bus_kw` | Static bus database |
| `transformer_association`, `feeder_section` | Static bus database |
| `transformer_sn_kva` | Static bus database |
| `base_voltage_pu` | Pre-computed from feeder (electrical_features.csv) |
| `feeder_distance_km` | Computed via shortest-path on networkx graph |
| `upstream_r_ohm`, `upstream_x_ohm`, `upstream_z_ohm` | Impedance along path |
| `pv_penetration_ratio` | total_pv_kw / load (or /1.0 if load=0) |
| `pv_to_transformer_ratio` | total_pv_kw / transformer_sn_kva |
| `new_pv_to_transformer_ratio` | new_pv_kw / transformer_sn_kva |
| `load_to_transformer_ratio` | load / transformer_sn_kva |

- Returns: `SAFE`, `CAUTION`, or `CONSTRAINED` with **per-class probabilities** (safe_probability, caution_probability, constrained_probability)
- Also returns: number of trees that voted, the exact feature vector used — so a citizen can see *what* the model was given

### Layer 2 — Deterministic Power Flow (the authoritative decision, ~50ms)

- Engine: **pandapower 2.14** with Newton-Raphson solver
- Network: **IEEE Comprehensive Test Feeder** (`feeder_network.json`) — 114 nodes, regulator taps fixed at validated values
- **Two cases are solved for every assessment:**
  - **BASE case**: the feeder with existing PV only
  - **PV case**: the feeder with existing + proposed new PV
- Delta is computed: `PV case − BASE case`

**Metrics extracted from the power flow:**

| Metric | Description |
|---|---|
| `voltage_rise_pu` | PV bus voltage (PV case) − PV bus voltage (BASE case) |
| `feeder_min_voltage_pu` | Minimum bus voltage across the whole feeder (PV case) |
| `feeder_max_voltage_pu` | Maximum bus voltage across the whole feeder (PV case) |
| `max_line_loading_pct` | Worst line utilisation (PV case) |
| `max_transformer_loading_pct` | Worst transformer utilisation (PV case) |
| `reverse_power_flow` | Detected by source export < 0 or line/trafo sign flip |
| `delta_losses_kw` | Change in feeder losses |
| `solar_penetration_pct` | Total PV injection as % of total feeder load |

### Layer 3 — Risk Assessment (the verdict)

Thresholds are loaded from `scenario_config.json` — **never hardcoded**. The rules are a verbatim port of `dataset_generation_phase2.py`, because these are the exact rules used to generate the training labels. Any drift between the service and the dataset generator would mean the model was trained on labels it can no longer reproduce.

**Hard rules — CONSTRAINED (first match wins, in this order):**
1. `feeder_max_voltage_pu > voltage_hard_high_pu` (1.05)
2. `feeder_min_voltage_pu < voltage_hard_low_pu` (0.90)
3. `|voltage_rise_pu| > voltage_rise_hard_pu` (0.05)
4. `max_line_loading_pct > line_loading_hard_pct` (100%)
5. `max_transformer_loading_pct > transformer_loading_hard_pct` (100%)

**Soft rules — CAUTION (any of):**
- max voltage > 1.03 pu
- min voltage < 0.93 pu
- voltage rise >= 0.03 pu
- line loading >= 80%
- transformer loading >= 95%
- reverse power flow detected

**Note:** Comparison operators are deliberately `>` for hard limits but `>=` for caution bands. This is not a typo — it matches the operators used when producing training labels.

**Reverse power flow** is CAUTION, never CONSTRAINED — `scenario_config.json` explicitly designates this as a DISCOM policy decision ("may allow with protection"), not a hard engineering block.

### Authority Rule

**The power flow always wins.** The ML result is displayed alongside the engineering verdict. When they disagree, the disagreement is flagged to the DISCOM for engineering attention. No averaging, no reconciliation. The engineering authority is explicit in every API response (`"authority": "power_flow"`).

---

## 4. The ML Model — Research, Training, and Known Limitations

### Training Data

The dataset was generated by running pandapower simulations across the IEEE feeder:
- **1,692 scenarios** (various buses × various PV sizes)
- Features engineered in `enrich_features.py` and `enrich_augmented.py`
- Near-threshold samples augmented in `augment_near_threshold.py`
- Training: `train_ml_v2.py` (1050 rows), Test: 254 rows

### Model Performance

- **97.6% test accuracy** on the 254-row test set
- **0 false-SAFE predictions** after feature enrichment to 18 features (v2 model)
- The v1 model (9 features) had **2 known false-SAFE cases** that were thoroughly investigated

### The False-SAFE Case Analysis (Historic, Fixed in V2)

This is a critical part of the research. The two known failures are:

**Case 1 — Bus 734, 66 kW:**
- Actual result: CONSTRAINED (voltage rise = 0.0575 pu, just 0.0075 pu over the 0.05 threshold)
- V1 prediction: SAFE (confidence only 0.40 — the model was uncertain)
- Root cause: Missing impedance features. The model could not infer voltage rise from the bus ID alone (sparse — only ~20 training examples at bus 734). The `pv_penetration_ratio` of 4.16 was insufficient to capture the Thevenin impedance to source.

**Case 2 — Bus 6231, 53 kW:**
- Actual result: CONSTRAINED (voltage rise = 0.0519 pu, just 0.0019 pu over threshold)
- V1 prediction: SAFE (high confidence: 0.755 — the model was confidently wrong)
- Root cause: Bus 6231 has **zero load**. The penetration ratio becomes 53.0 (53 kW / 1.0 due to divide-by-zero guard), which is an artifact. The model learned that T2 secondaries with high penetration are usually safe (strong bus, 0.9946 pu base voltage). It did not know the local secondary impedance still produced a rise of 0.052 pu.

**Fix in V2:** Added `upstream_r_ohm`, `upstream_x_ohm`, `upstream_z_ohm`, `feeder_distance_km`, `base_voltage_pu` as explicit features. This gives the model the electrical path information it was missing. Result: 0 false-SAFE predictions on the test set.

The v2 model's feature vector exactly matches `enriched_features.json`. If there is ever a mismatch at startup, the backend raises a `RuntimeError` and refuses to start.

### Accuracy Caveat (Important for SIH)

The documented 97.6% is optimistic for two reasons that are honestly disclosed:
1. **Model selection was done on the test set** — `train_ml_v2.py` picks the best model by test-set F1, not a held-out validation set
2. **The train/test split is random, not bus-disjoint** — 83 of 254 test rows have a training row at the same bus within 5 kW, so the model has seen similar scenarios

This does not invalidate the system — the power flow makes the final decision regardless. But it means the 97.6% number should not be cited without these caveats.

---

## 5. The Power Flow Engine — Technical Details

### Network Model

The IEEE Comprehensive Test Feeder is a real, validated distribution network used in power systems research:
- **114 buses**, spanning MV (24.9 kV, 12.47 kV) and LV (0.24 kV)
- **71 eligible PV connection buses** (LV customer secondaries, validated in `valid_pv_buses.csv`)
- Voltage regulators with taps **fixed at validated values** — the `feeder_network_ldc.json` (LDC experiment) is never loaded because its tap direction was wrong (documented in `engineering_audit.md`)
- Total feeder load: ~3.9 MW

### Solver Configuration

```python
pp.runpp(
    net,
    algorithm="nr",          # Newton-Raphson
    max_iteration=500,
    numba=False,
    tolerance_mva=1e-3,
    enforce_q_limits=False,
)
```

Unity power factor for all PV injections (`q_mvar=0`), per `scenario_config.json`.

### BASE vs PV Convention

This is exactly how the training labels were generated in `dataset_generation_phase2.py`:
- **BASE** = feeder + `existing_pv_kw` only
- **PV** = feeder + `existing_pv_kw` + `new_pv_kw`
- Delta = PV − BASE

**Subtlety:** The `base_voltage_pu` ML feature comes from `electrical_features.csv`, which was computed with NO PV at all. The BASE case in the power flow includes existing PV. These differ when `existing_pv_kw > 0`. This asymmetry exists in the original pipeline and is preserved deliberately — changing it would break the feature contract.

### BASE Case Caching

The BASE case for a given `(bus_id, existing_pv_kw)` is cached in memory. Multiple requests for the same bus reuse the cached BASE and only run the PV case fresh. This halves the simulation time for busy buses.

### ZIP Load Compatibility

The feeder was built with pandapower 3.4 which uses split ZIP columns (`const_z_p_percent`, etc.). pandapower 2.14 (what we pin) uses unified `const_z_percent`. A normalisation shim (`_normalize_zip_loads`) translates between the two column formats in-place so the same feeder file works with either engine version. Without this shim, the `/api/twin` endpoint was returning 422 errors in production.

### Non-Convergence Handling

At very large PV injections on weak LV buses, the Newton-Raphson solver has no solution — this is a real engineering outcome, not a server bug. When `pandapower.runpp()` raises `LoadflowNotConverged`, the backend normalises it to a `PowerFlowError` and returns HTTP 422 with a human-readable explanation.

---

## 6. Hosting Capacity — Bisection on the Power Flow

The dataset never contained hosting capacity data (every row describes one PV size, not a maximum). So it is computed by **binary search over the real power flow**.

### Per-Bus Algorithm

```
capacity = max new_pv_kw such that engineering verdict ≠ CONSTRAINED
```

- Search range: 1 kW to 2000 kW (the 2 MW ceiling is far above what any single LV bus on this 3.9 MW feeder can realistically host)
- Resolution: 1 kW (rounded down — never overstate)
- Iteration count: **~11 power flows per bus**
- Edge cases handled: 1 kW already CONSTRAINED (capacity = 0), ceiling not CONSTRAINED (saturated, capacity = ceiling with disclaimer)

### Feeder-Section Algorithm (Critical Engineering Insight)

Per-bus capacity **cannot be summed** to get feeder capacity. If bus A can host 50 kW and bus B can host 50 kW, that does **not** mean the section can host 100 kW. Every bus figure assumes it is the only new connection. Running all of them simultaneously at their individual maxima would overload the transformer serving the section.

On this feeder, summing per-bus figures overstates the feeder limit by **up to 23×**.

The correct method: bisect the total feeder capacity while spreading capacity **evenly** across all eligible buses in the section and solving the whole feeder at once. The interaction between simultaneous connections is part of the answer. The even-split assumption is explicitly reported in the API response so engineers know it is a modelling choice, not a claim.

### Monotonicity Verification

Bisection assumes adding more PV never removes a CONSTRAINED verdict (monotonic). A `verify_monotonic()` method sweeps capacity linearly at 12 points and confirms no non-monotonic behaviour exists at a given bus.

---

## 7. The Digital Twin

### What It Is

The digital twin is a **live network diagram** that shows voltage levels, line loadings, and flow directions before and after a proposed installation, for every element on the path from the substation to the PV bus.

**Critical implementation detail:** The topology service builds its graph from `feeder_network.json` — the **same file the power flow uses**. The diagram can never show a bus, line, or transformer that does not exist in the simulation. One data source, two representations.

### Topology Service

Uses **networkx** to build a directed graph from the pandapower network:
- `respect_switches=True` is required — with it False, the graph traverses open tie switches and invents electrical connections that do not exist, producing paths that are up to 8.8 km short and passing through switches that are open in the model
- Hop count from source bus 700 determines horizontal layout position
- Buses placed east of substation by **true route distance in km** (sum of `length_km` along the electrical path, the same formula used for the `feeder_distance_km` ML feature)

### Per-Element Before/After Data

The `simulate_with_elements()` method returns the same two power flows as a normal assessment, plus per-element deltas:

**Per bus:** `before_pu`, `after_pu`, `delta_pu`
**Per line:**
- `before_pct`, `after_pct` (% loading)
- `direction_before`, `direction_after` (FORWARD = grid→customer, REVERSE = export upstream)
- `reversed_by_pv` (True when the line changes direction due to solar)

**Per transformer:** loading before/after, power direction before/after

**Energy balance at the connection point:**
- `solar_generation_kw`, `local_consumption_kw`, `self_consumed_kw`, `local_export_kw`
- `grid_supply_before_kw` vs `grid_supply_after_kw`

### Geographic Layout

The IEEE feeder ships **no geographic coordinates**. The topology service computes illustrative positions:
- Horizontal (x): hop count from source × 180 px
- Vertical (y): spread branches to avoid overlap

For the map, buses get lat/lon by placing them east of an anchor coordinate by their route distance in km. The scale is honest (distances are real), but the absolute position is not. Every API response that returns coordinates carries an `anchor_note` and a disclaimer. The UI must display both.

---

## 8. Site Context — Real Buildings from OpenStreetMap

When a citizen opens the 3D rooftop planner, the system fetches **real building footprints** from OpenStreetMap via the Overpass API:

- Radius: 160 m (default), up to 400 m
- Returns: polygon outline (closed ring of [lon, lat] pairs), height, building type, area
- Height resolution: `height` tag > `building:levels × 3.0 m` > assumed 9.0 m
- `height_source` field on every building: `"height"` | `"levels"` | `"assumed"` — the UI must show assumed height as assumed, not as a measurement
- Ray-casting algorithm identifies which building the applicant's coordinate falls inside
- If no building contains the point, nearest building by vertex distance is selected
- Cache: 256 entries, keyed by `(round(lat, 4), round(lon, 4), radius)` — two people on the same street share a cache entry

---

## 9. 3D Rooftop Solar Planner (CesiumJS)

The solar planner is one of the most technically deep frontend features. It is built on **CesiumJS** with Cesium Ion for terrain and 3D buildings.

### What It Shows

- Real photorealistic terrain (Cesium World Terrain)
- 3D building footprints from Cesium Ion OSM Buildings
- Solar panel array rendered on the rooftop as 3D rectangles
- Live sun position and shadows cast by buildings
- Sun ray lines showing solar direction

### Solar Position — Real Astronomy (NOAA Algorithm)

The sun position is computed using the **NOAA Solar Calculator algorithm** (Astronomical Almanac / Jean Meeus), implemented from scratch in TypeScript in `frontend/lib/solar/sun.ts`. This is not a lookup table or a seasonal approximation.

The algorithm computes:
- Geometric mean longitude and mean anomaly of the Sun
- **Equation of centre**: corrects from circular orbit to the real elliptical orbit
- **Apparent longitude**: accounts for nutation (Earth's wobble) and aberration (light travel time)
- **Obliquity of the ecliptic**: the axial tilt that gives us seasons
- **Equation of time**: difference between apparent solar time and mean clock time
- **Atmospheric refraction**: the atmosphere bends light upward by ~0.5° at the horizon

Accuracy: well under 0.1° for dates within a few centuries of now — far finer than any rooftop placement decision requires.

CesiumJS computes its own sun position from the same Julian Date. Both implementations derive from the same standard so the sun rays in the 3D scene and the readout panel agree to within arcminutes.

### Solar Planner Calculations

**Optimal tilt estimation:**
```
latitude < 25° → tilt = latitude × 0.87
latitude >= 25° → tilt = latitude × 0.76 + 3.1
clamped to [5°, 40°]
```

**Clear-sky irradiance estimate** (labelled as estimate):
```
air_mass = 1 / sin(elevation)
direct_normal = 1353 × 0.7^(air_mass^0.678)  ← Haurwitz/Meinel attenuation
beam = direct_normal × cos(incidence_angle)
diffuse = 0.1 × direct_normal × (1 + cos(tilt)) / 2
```

**Incidence cosine** (how squarely the sun hits the panel):
```
cos = sin(sun_el)×cos(tilt) + cos(sun_el)×sin(tilt)×cos(sun_az - panel_az)
```

**Panel array layout:**
- Panels laid out in a grid with configurable row spacing
- `occupiedAreaSqm` calculated from panel dimensions × count × row spacing factor
- `fitCapacityKw`: computes the largest system that fits the declared roof area at the current tilt and row spacing, capped at the category limit (10 kW residential, 500 kW C&I)
- Changes in tilt and row spacing immediately update the array layout shown in the scene

**Live sky conditions** are fetched from **Open-Meteo** (cloud cover %, beam irradiance W/m², global horizontal W/m², temperature). The sun direction is drawn regardless of whether the weather API responds — it is computed, not forecast.

### Solar Noon Default

When the planner opens, it defaults to **solar noon** — the minute when the sun is highest at the given site. This is found by:
1. Coarse sweep: check every 20 minutes of the day
2. Fine sweep: check every 1 minute around the best 20-minute window

This default is chosen because opening to a wall-clock time after dark would show an unlit globe, and solar noon is the honest choice of default for a planning tool.

### Panel Suitability Assessment

Computed from:
- Latitude (hemisphere, optimal azimuth)
- Tilt and azimuth vs optimal
- Day-samples of sun position (72 samples across the day at 20-min intervals)
- Shading fraction from the Cesium scene
- Array area vs available roof area

Returns: `GOOD`, `PARTIAL`, `POOR`, or `UNKNOWN` with a numeric score.

### Grid Assessment Integration

When the user clicks "Use This Placement & Assess Grid Impact", the planner calls the real backend `POST /api/assess` endpoint with the capacity from the layout. This runs the full ML + power-flow pipeline and shows the risk result (SAFE/CAUTION/CONSTRAINED) overlaid on the 3D scene.

---

## 10. SolarGrid AI Assistant (Built-in Chat)

A floating chat widget is present on every page. It is role-aware:

- **Citizen context**: "Why is my application CAUTION?", "What does 0.032 pu voltage rise mean?", "What happens after approval?"
- **DISCOM context**: "Which buses have low hosting capacity?", "Explain the ML and physics disagreement", "Show me the affected line"
- **Vendor context**: "What installations are assigned to me?", "Why was this installation returned?"

The assistant:
- Uses actual SolarGrid API data (reads `application_id`, `pv_bus` from context)
- Accepts actions the UI can respond to: `FOCUS_BUS`, `FOCUS_TRANSFORMER`, `FOCUS_LINE`, `HIGHLIGHT_PATH`
- Renders Markdown (bold, bullets, code, blockquotes, headings)
- Carries the last 10 conversation turns as history to the backend
- Is explicitly described as using only SolarGrid data and never inventing electrical values

---

## 11. Vendor Distance & Routing

### Two Modes

**Straight-line (default):**
- Great-circle (haversine) distance
- `is_route: false`, `method: "STRAIGHT_LINE"`
- Returns just the two endpoints as geometry
- Note displayed: "Actual travel distance is longer and is not known"

**OSRM road routing (when configured):**
- Set `ROUTING_PROVIDER=osrm` and `ROUTING_BASE_URL` in `.env`
- Returns actual road distance, drive time in minutes, and the road geometry as `[[lon, lat], ...]` for drawing
- `is_route: true`
- On OSRM failure: degrades to straight-line with `method: "STRAIGHT_LINE_FALLBACK"` and an explicit note — never silently substitutes a different measurement

**Any vendor distance that is straight-line must be labelled as such in the UI.** Presenting a straight-line figure as a travel distance or drive time is a UI bug, not an acceptable approximation.

Default when no provider is configured: tries the public OSRM demo server (`router.project-osrm.org`). Falls back to straight-line if unreachable.

---

## 12. Security Architecture

### Authentication Flow

1. Browser authenticates via Supabase Auth (email/password)
2. Supabase issues a JWT (access token) using the anon key
3. Every backend request carries: `Authorization: Bearer <jwt>`
4. Backend validates the JWT cryptographically
5. Backend re-reads the user's `role` from the `profiles` table on every request — **the role claim in the JWT is never trusted alone**
6. Role-based checks happen in the route handler before any business logic runs

### Two-Layer Authorization

Authorization is enforced at two independent layers. Either alone is a single point of failure:

**Layer 1 — API layer:**
- `require_discom` dependency on DISCOM routes
- `require_vendor` dependency on vendor portal routes
- Ownership checks: `application.applicant_id == auth.uid()`

**Layer 2 — Database (Row Level Security on all 12 tables):**
- Citizens see only their own applications, assessments, simulations
- DISCOM sees everything
- Vendors see only their own leads, installations, documents

**Key write-policy decisions:**
- `simulation_results` — **no client write policy**. A citizen with a valid token and direct Postgres access cannot alter their own risk verdict.
- `risk_assessments` — **no client write policy**. Same reason.
- `profiles.role` — `UPDATE` revoked at column level. A citizen cannot promote themselves to DISCOM even with a direct Postgres connection. (Migration 0004 exists because a column-level `REVOKE` under a table-level `GRANT` is a no-op in Postgres, and a citizen actually did self-promote in a test before this was fixed.)
- `installations.discom_verified*` — `UPDATE` revoked. A vendor cannot certify their own installation.

### Rate Limiting

Custom in-process sliding window (no `slowapi` dependency):

| Route type | Limit |
|---|---|
| Simulation routes (`/api/assess`, `/api/twin`, `…/assess`, what-if, hosting capacity) | 30 req/min |
| Other authenticated routes | 240 req/min |
| Unauthenticated | 60 req/min |
| `/health` | Never limited |

Client key: bearer token hash (follows the account) or client IP (anonymous). CORS preflight requests are never charged.

**Limitation (honest):** Counters live in process memory. N workers allow roughly N × the configured limit. `/health` reports this. The interface is isolated in `security.py` — Redis can be plugged in without changing any route code.

### Secret Handling

- `SUPABASE_SERVICE_ROLE_KEY` is backend-only. It bypasses all RLS. It has no `NEXT_PUBLIC_` variable. It is never sent to the frontend.
- `verify_phase12.py` scans the source tree and the Next.js built bundle to confirm no key material appears in the frontend bundle.
- Error responses never include stack traces, SQL fragments, or internal state — only a reference UUID the admin can grep in server logs.

---

## 13. Database Schema (10 Migrations)

| Migration | What it does |
|---|---|
| `0001_init_schema` | 12 tables, 8 enums, audit triggers |
| `0002_rls_policies` | 29 RLS policies across all tables |
| `0003_lock_migration_ledger` | The migration ledger itself is not client-readable |
| `0004_fix_column_privileges` | **Security fix**: column REVOKE under table GRANT is a no-op; citizen self-promotion to DISCOM was possible |
| `0005_fix_vendor_self_update` | Approved vendors could not edit their own profile |
| `0006_audit_actor_survives_deletion` | Deleting a user previously erased who did what in the audit log |
| `0007_solar_placement_and_rooftop_limits` | Planner result storage column + residential 3–11 kW bounds |
| `0008_category_capacity_limits` | Residential 1–10 kW, C&I 1–500 kW category ceilings |
| `0009_installation_completion_report` | Vendor completion-report columns |
| `0010_vendor_reviews` | Citizen star ratings + live average trigger |

---

## 14. All Pages — Every Route Explained

### Public

| Route | Description |
|---|---|
| `/` | Landing page: hero with real accuracy numbers (97.6%, ~50ms solve, 11 bisection solves), feature cards, trust metrics, animated CTAs |
| `/login` | Supabase email/password sign-in with Supabase-configured message |
| `/register` | Citizen account creation (always creates CITIZEN role) |

---

### Citizen Portal `/citizen/`

All pages require authentication. RLS ensures citizens see only their own data.

| Route | What it shows / does |
|---|---|
| `/citizen/dashboard` | 4 stat cards (total applications, awaiting decision, approved, total kW requested), list of recent applications with status badges, direct link to new application |
| `/citizen/applications` | Full application list with status, bus, kW, date |
| `/citizen/applications/new` | Multi-step form: enter name/address, select PV bus from 71 eligible buses, declare existing and new capacity, choose roof type, roof area, monthly consumption. Live ML pre-screen fires on form change. On submit: full power-flow + risk assessment, result shown before final submission. |
| `/citizen/applications/[id]` | Full detail: risk badge, all power-flow metrics (voltage rise, min/max voltage, line loading, transformer loading, reverse flow, losses), ML probabilities, constraint reason, DISCOM decision, vendor selection, 3D rooftop planner embedded |
| `/citizen/map` | MapLibre 2D map with 6 layers: grid buses, application pins (citizen's own only, via RLS), hosting capacity heat, feeder sections. Click a bus for capacity; click an application pin for status. Basemap toggle. Caveat badge always visible. |
| `/citizen/vendors` | List of DISCOM-approved vendors sorted by distance. Dropdown to select an application and re-sort by distance from that site. Each card shows distance with `is_route` flag — straight-line labelled as such. |
| `/citizen/scheme` | PM Surya Ghar Muft Bijli Yojana: scheme overview, eligibility table (1–10 kW residential), CFA calculator (enter kW → indicative subsidy). Red warning if `configuration_verified = false` in scheme_config. Links to official portals. |

---

### DISCOM Portal `/discom/`

All pages require `DISCOM` or `ADMIN` role.

| Route | What it shows / does |
|---|---|
| `/discom/dashboard` | Network overview: total applications, pending review, approved capacity (kW), pending capacity (kW), risk distribution (SAFE/CAUTION/CONSTRAINED counts), ML-vs-engineering disagreement counter, network model info (engine, buses, lines, transformers) |
| `/discom/applications` | Every application across all citizens, filterable by risk and status. Risk badges colour-coded. |
| `/discom/applications/[id]` | Full review packet: applicant details, power-flow metrics, ML probabilities vs engineering verdict, constraint reason with specific values (e.g., "Voltage rise 0.0575 pu at bus 734 exceeds 0.05"). Decision controls: APPROVED / ENGINEERING_REVIEW / REJECTED. Approving a CONSTRAINED application shows "Approve despite objection" — override recorded in audit log with the engineering objection copied in. |
| `/discom/map` | MapLibre map with all applications across the network, all connection points, hosting capacity layer |
| `/discom/grid-twin` | Full network single-line diagram: all 114 buses, all lines, all transformers. Buses colour by voltage. Lines colour by loading %. Animated flow direction arrows. Select any bus + enter PV size → runs live assessment → diagram updates showing before/after for every element on the path. |
| `/discom/hosting-capacity` | Table of per-bus capacity (from bisection, 11 power flows per bus) and feeder-section capacity (from simultaneous injection bisection). Shows both the individual-bus sum (for comparison) and the simultaneous-injection result (for use). Discrepancy ratio visible — up to 23× on this feeder. |
| `/discom/feeders` | Per-feeder-section loading summary: total load, total PV, peak loading, limiting constraint |
| `/discom/transformers` | Every transformer ordered by base-case loading %. T7 at 92.8% is the most stressed. Transformer name, kVA rating, current loading, which section it serves. |
| `/discom/what-if` | Capacity sweep tool: select a bus, select a range and step size. System runs one power flow per point (e.g., 10/25/50/100/250/500 kW) and returns a table of results. Each row shows the risk level and the binding constraint. "View twin" on any row opens the full twin for that scenario. |
| `/discom/vendors` | Vendor management queue. Status: PENDING / APPROVED / SUSPENDED / REJECTED. Approve activates the vendor and makes them visible to citizens. Suspend removes them from citizen-visible lists immediately. |
| `/discom/installations` | All installations across all vendors. The only place the VERIFIED status button exists — vendors cannot see this button and the API returns 403 if they try. |

---

### Vendor Portal `/vendor/`

All pages require a vendor profile linked to the authenticated user and a status of APPROVED.

| Route | What it shows / does |
|---|---|
| `/vendor/login` | Separate login page (not `/login`) |
| `/vendor/register` | Business registration form (always creates PENDING status) |
| `/vendor/dashboard` | Live marketplace (approved, unassigned applications; **nearest vendor blinks with green glow and "NEAREST — YOU" badge**; 1-hour priority window before escalation to other vendors). New lead count, confirmed appointments, installations, awaiting DISCOM verification. My ratings (average ★ from citizen reviews). Auto-refreshes every 15 seconds. |
| `/vendor/leads` | Citizen-selected appointment requests. Accept (opens an installation record) or Decline. |
| `/vendor/appointments` | Scheduled site visits — manage date, time, status |
| `/vendor/applications` | Applications the vendor is currently engaged with |
| `/vendor/applications/[id]` | Application detail for a vendor-engaged application |
| `/vendor/projects` | All accepted projects from initial lead through to completion |
| `/vendor/installations` | All own installations. Status advancement: PENDING → SITE_VISIT_SCHEDULED → IN_PROGRESS → COMPLETED → VERIFICATION_PENDING. **VERIFIED has no button** — shown as a locked chip (🔒). API returns 403 if a vendor tries to set VERIFIED. |
| `/vendor/installations/[id]` | Individual installation with completion report fields |
| `/vendor/profile` | Business profile editor: name, description, service area, certifications. `status` and average `rating` fields are read-only — a vendor cannot approve themselves or inflate their rating. |

---

## 15. Test Coverage — The 12 Required Scenarios

`backend/tests/test_scenarios.py` verifies these specific cases:

| # | Scenario | Bus | kW | Expected |
|---|---|---|---|---|
| 1 | Clean happy path | 620 | 5 kW | SAFE |
| 2 | Caution with reverse flow | 621 | 100 kW | CAUTION |
| 3 | Constrained by voltage rise | 734 | 66 kW | CONSTRAINED |
| 4 | Zero-load edge case (former false-SAFE) | 6231 | 53 kW | CONSTRAINED |
| 5 | Existing + new solar | 734 | 10 kW existing + 56 kW new | CONSTRAINED |
| 6 | Reverse power flow detection | 734 | 66 kW | reverse_power_flow = True |
| 7 | Voltage rise measurement | 734 | 66 kW | voltage_rise ≈ 0.0575 pu |
| 8 | Transformer loading (not voltage) | 716 | 44 kW | CONSTRAINED by transformer |
| 9 | Invalid bus | unknown / ineligible | any | 404 vs 422, distinguished |
| 10 | Invalid capacity | 0 / negative / 2001 kW | any | 422 |
| 11 | Unauthorized role | citizen → DISCOM route | any | 403 |
| 12 | Unapproved vendor invisibility | PENDING vendor | any | Not in public list |

**Bus 734 @ 66 kW and Bus 6231 @ 53 kW are regression tests** — the original model's two false-SAFE cases. If either test fails, the fix is not to update the expectation; it means the model, thresholds, or feeder changed.

**Label replay test:** `test_integration.py` takes rows from the original `pv_dataset_enriched_augmented.csv`, pushes them through the running services, and requires the recomputed label to match the stored one. This is the most important correctness test in the suite — it proves the port of the research is faithful.

**Security test suite (`verify_phase12.py`):** Runs 9 attacks against a live deployment:
- Citizen accessing DISCOM route (403)
- Citizen reading another citizen's application (404 via RLS)
- Citizen patching their own risk verdict (403)
- Pending vendor appearing in public list (absent)
- Vendor setting VERIFIED on their own installation (403)
- Citizen promoting themselves to DISCOM (column-level grant blocks it)
- Service-role key appearing in frontend bundle (absent)
- Stack trace appearing in error response (absent)
- Rate limit enforcement (429 after threshold)

---

## 16. Demo Accounts and Key Demo Buses

### Demo Accounts

| Portal | URL | Email | Password |
|---|---|---|---|
| Citizen | `/login` | `demo.citizen@solargrid.test` | `DemoCitizen!2026` |
| DISCOM | `/login` | `demo.discom@solargrid.test` | `DemoDiscom!2026` |
| Vendor | `/vendor/login` | `demo.vendor@solargrid.test` | `DemoVendor!2026` |

Use a private window to have two portals open simultaneously (sessions live in browser storage).

### Key Buses for Demonstration

| Bus | Load | Base Voltage | What it demonstrates |
|---|---|---|---|
| 732 | 25.4 kW | ~0.92 pu | SAFE at 5 kW — clean happy path |
| 734 | 15.85 kW | 0.9059 pu (feeder minimum) | CONSTRAINED at 66 kW by voltage rise 0.0575 pu. The historic false-SAFE case. Marginally over 0.05 threshold by only 0.0075 pu. |
| 6231 | 0 kW | 0.9946 pu | CONSTRAINED at 53 kW — zero-load bus, former ML failure due to penetration ratio artifact |
| 716 | 15.85 kW | ~0.93 pu | CONSTRAINED at 44 kW by **transformer loading** (not voltage). Shows a different constraint pathway. |
| 621 | 0 kW | ~0.98 pu | CAUTION at 100 kW with reverse power flow |

---

## 17. Tech Stack — Full Inventory

### Backend Python
| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.115.12 | Web framework |
| `uvicorn[standard]` | 0.34.2 | ASGI server |
| `pydantic` | 2.11.4 | Data validation |
| `pydantic-settings` | 2.9.1 | Config from env vars |
| `supabase` | 2.15.2 | Database + auth + storage client |
| `httpx` | 0.28.1 | HTTP client (routing, Overpass) |
| `pandapower` | 2.14.11 | Power flow simulation |
| `networkx` | 3.4.2 | Graph topology |
| `pandas` | 2.2.3 | Data frames |
| `numpy` | 1.26.4 | Numerical (pinned for scikit-learn compatibility) |
| `scikit-learn` | 1.3.2 | ML model (pinned — model was serialized with this version) |
| `psycopg[binary]` | 3.2.6 | Direct Postgres (migrations only) |

### Frontend JavaScript
| Package | Version | Purpose |
|---|---|---|
| `next` | 14.2.18 | React framework (App Router) |
| `react` + `react-dom` | 18.3.1 | UI |
| `typescript` | 5.7.2 | Type safety |
| `tailwindcss` | 3.4.17 | Utility CSS |
| `@supabase/supabase-js` | 2.47.10 | Auth + database client |
| `cesium` | ^1.144.0 | 3D globe, terrain, buildings, shadows |
| `maplibre-gl` | ^4.7.1 | 2D interactive maps |
| `vitest` | ^2.1.8 | Frontend unit tests |

### Infrastructure
| Service | Purpose |
|---|---|
| Supabase (hosted) | Postgres 15 + RLS + Auth + Storage |
| Render | Deployment (blueprint `render.yaml`) |
| Docker Compose | Local development |
| Cesium Ion | Terrain tiles + OSM 3D buildings |
| Open-Meteo | Live weather (cloud cover, irradiance) |
| OSRM | Road routing (optional) |
| OpenStreetMap / Overpass | Building footprints |

---

## 18. Known Limitations (Honest Disclosure)

These are in the codebase documentation and must not be hidden in a demo:

| Limitation | Impact |
|---|---|
| 97.6% accuracy is optimistic (model selection on test set, random split not bus-disjoint) | The real accuracy on unseen buses is lower. The power flow makes the final decision regardless. |
| Line-overload mode is untrained (max line loading in dataset is ~57%) | The power flow computes line loading correctly and will detect overloads. The ML model will not. |
| Feeder runs ~3–4% low vs IEEE reference (voltage MAE 5.33%) | Thresholds were calibrated to this offset. Labels are self-consistent but tuned to the model, not the physical feeder. |
| One feeder, one topology | No time series, no seasonal variation, no multi-feeder support |
| Rate limiting is per-process | Multiple workers multiply the effective limit. Redis needed for scale-out. |
| Map coordinates are synthetic | Distances are real; absolute position on Earth is not. Always labelled. |
| Vendor distances may be straight-line | Until OSRM is configured. Always labelled. |
| PM Surya Ghar rates are unverified placeholders | Red warning shown until an admin verifies them against the official portal. |

---

## 19. Project File Structure

```
sih26/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py              ← citizen/assessment routes
│   │   │   ├── routes_discom.py       ← DISCOM routes
│   │   │   ├── routes_scheme.py       ← PM Surya Ghar scheme
│   │   │   ├── routes_vendors.py      ← public vendor routes
│   │   │   ├── routes_vendor_portal.py← vendor-auth routes
│   │   │   └── deps.py                ← auth dependencies
│   │   ├── core/
│   │   │   ├── config.py              ← settings (pydantic-settings)
│   │   │   ├── security.py            ← rate limiter, error handlers
│   │   │   ├── supabase_client.py     ← anon + service role clients
│   │   │   └── paths.py               ← artifact file paths
│   │   ├── db/
│   │   │   └── service.py             ← database access layer
│   │   ├── models/
│   │   │   ├── schemas.py             ← Pydantic request/response models
│   │   │   └── enums.py               ← RiskLevel, ApplicationStatus, etc.
│   │   └── services/
│   │       ├── power_flow.py          ← pandapower BASE+PV simulation
│   │       ├── ml_prediction.py       ← 18-feature RandomForest
│   │       ├── risk_assessment.py     ← threshold rules → verdict
│   │       ├── hosting_capacity.py    ← bisection search per bus + feeder
│   │       ├── topology.py            ← networkx graph + layout + distances
│   │       ├── site_context.py        ← OSM building footprints
│   │       ├── routing.py             ← OSRM / straight-line distances
│   │       ├── scheme.py              ← PM Surya Ghar data
│   │       ├── grid_assets.py         ← bus database + thresholds
│   │       ├── connection_point.py    ← nearest bus finder
│   │       ├── storage.py             ← Supabase Storage (vendor docs)
│   │       ├── vendors.py             ← public vendor list
│   │       └── vendor_portal.py       ← leads, appointments, installations
│   ├── scripts/
│   │   ├── apply_migrations.py        ← transactional migration runner
│   │   ├── precompute_grid_map.py     ← 1065 power flows → hosting capacity cache
│   │   ├── setup_demo_accounts.py     ← 3-portal demo setup
│   │   ├── demo_end_to_end.py         ← scripted 12-step journey
│   │   └── verify_phase1–12.py        ← acceptance tests per build phase
│   ├── seed/
│   │   ├── seed_grid_assets.py        ← loads bus data into Supabase
│   │   ├── seed_demo_vendors.py       ← demo vendor data
│   │   └── seed_scheme_config.py      ← PM Surya Ghar config
│   └── tests/
│       ├── test_scenarios.py          ← 12 required scenarios
│       ├── test_integration.py        ← ML contract, label replay, RLS attacks
│       ├── test_application_flow.py   ← end-to-end application workflow
│       └── test_rate_limit_cors.py    ← rate limit and CORS behaviour
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   ← landing page
│   │   ├── login/ register/           ← auth pages
│   │   ├── citizen/                   ← dashboard, applications, map, vendors, scheme
│   │   ├── discom/                    ← dashboard, applications, grid-twin,
│   │   │                                 hosting-capacity, feeders, transformers,
│   │   │                                 what-if, vendors, installations, map
│   │   └── vendor/                    ← dashboard, leads, appointments, projects,
│   │                                     installations, profile
│   ├── components/
│   │   ├── solar3d/
│   │   │   ├── CesiumScene.tsx        ← 3D globe, terrain, shadows, sun rays
│   │   │   ├── RooftopTwin.tsx        ← 3D panel array on rooftop
│   │   │   └── SolarPlanner.tsx       ← full planning UI with layout + assessment
│   │   ├── assistant/
│   │   │   └── SolarGridAssistant.tsx ← floating chat widget
│   │   ├── GridMap.tsx                ← MapLibre 2D map
│   │   ├── GridTwin3D.tsx             ← digital twin diagram
│   │   ├── TwinDiagram.tsx            ← before/after twin with flow arrows
│   │   ├── VendorList.tsx             ← vendor cards with distance
│   │   ├── ApplicationTracker.tsx     ← status timeline
│   │   ├── AssessmentResult.tsx       ← risk verdict display
│   │   └── RiskBadge.tsx              ← SAFE/CAUTION/CONSTRAINED badge
│   └── lib/
│       ├── api.ts                     ← typed API client for all endpoints
│       ├── supabase.ts                ← Supabase browser client
│       ├── types.ts                   ← TypeScript types for all API responses
│       ├── risk.ts                    ← threshold comparison (mirrors backend rules)
│       └── solar/
│           ├── sun.ts                 ← NOAA solar position algorithm
│           ├── array.ts               ← panel layout geometry
│           ├── suitability.ts         ← GOOD/PARTIAL/POOR assessment
│           ├── weather.ts             ← Open-Meteo sky conditions
│           └── config.ts              ← panel defaults (configurable via env)
│
├── supabase/migrations/               ← 0001_init_schema … 0010_vendor_reviews
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── TESTING.md
│   ├── ENVIRONMENT.md
│   └── RUNBOOK.md
│
├── suryagrid_model_v2.pkl             ← trained RandomForest pipeline
├── feeder_network.json                ← IEEE test feeder (pandapower)
├── scenario_config.json               ← voltage/loading thresholds
├── enriched_features.json             ← feature contract (18 features)
├── valid_pv_buses.csv                 ← 71 eligible LV buses
├── electrical_features.csv            ← static per-bus electrical features
├── pv_dataset_enriched_augmented.csv  ← 1,692 training scenarios
├── ml_dataset_test_enriched_v2.csv    ← 254 test rows
├── false_safe_case_analysis.md        ← v1 failure analysis
├── dataset_quality_report.md
├── engineering_audit.md
├── requirements.txt                   ← Python dependencies
├── docker-compose.yml
├── render.yaml                        ← Render deployment blueprint
├── .env                               ← backend secrets (never committed)
└── frontend/.env.local                ← frontend secrets (never committed)
```

---

## 20. Quick Command Reference

```bash
# Backend — first time
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
python backend/scripts/apply_migrations.py
python backend/seed/seed_grid_assets.py
python backend/scripts/precompute_grid_map.py   # ~90s, 1065 power flows
python backend/seed/seed_scheme_config.py

# Backend — run
.venv/Scripts/python -m uvicorn app.main:app --app-dir backend --port 8000

# Frontend — run
cd frontend && npm ci && npm run dev

# Demo setup
.venv/Scripts/python backend/scripts/setup_demo_accounts.py

# Tests
.venv/Scripts/python -m pytest
cd frontend && npm test && npm run typecheck

# Verify live deployment
.venv/Scripts/python backend/scripts/verify_phase1.py
.venv/Scripts/python backend/scripts/verify_phase12.py

# Docker
docker compose up --build
```
