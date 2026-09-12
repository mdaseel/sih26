# SolarGrid AI — Full Project Document

> One file describing the whole system: product, data, ML, backend, frontend,
> 3D twins, database, operations. Generated from the repo as built (includes
> all session work through vendor ratings + Render readiness). For day-to-day
> commands see `docs/RUNBOOK.md`; for endpoints `docs/API.md`.

---

## 1. What this is

**Rooftop-solar hosting-capacity screening for a distribution utility.**
A citizen requests a rooftop system → an ML model pre-screens in milliseconds →
a deterministic pandapower flow verifies against the real feeder model →
verdict `SAFE / CAUTION / CONSTRAINED`. **The power flow decides** — the model
is a fast opinion, never the answer.

```
citizen request → ML pre-screen → power-flow verification → verdict
                                        ↓
              2D twin · 3D twin · GIS map · DISCOM review · installer · CFA
                   → completion report → verification → ratings → VERIFIED
```

Three portals: **Citizen**, **DISCOM**, **Vendor (installer)**. Stack: Next.js 14
+ FastAPI + Supabase (Postgres/RLS/Auth/Storage). No separate ML service — the
model loads into the backend at startup.

### What's real, what's not

| Item | Status |
|---|---|
| Feeder topology, line lengths, impedances | Real — IEEE Comprehensive Test Feeder, validated vs published reference |
| Voltages, loadings, losses, hosting capacity | Real — pandapower per request; capacity by bisection, never estimated |
| Model + dataset | Real — 1692 simulated scenarios (+34 v4 expansion), reused |
| Bus coordinates | Synthetic — feeder ships none; inter-asset distances true, absolute placement illustrative |
| PM Surya Ghar rates | Unverified placeholders until checked vs official portal |
| Demo vendors/users | Fictional |

One feeder, one topology, one load profile. Never presented as live SCADA, a
real utility's data, or the government portal.

---

## 2. Architecture

```
Next.js (browser)              FastAPI (Python)                    Supabase
citizen/discom/vendor ──JWT──► MLPredictionService                 Postgres + RLS
                               PowerFlowService ──► pandapower      Auth
                               RiskAssessmentService               Storage
                               HostingCapacityService (bisection)
                               TopologyService / GridAssetService
                               ConnectionPoint / HouseMapping
                               CapacityLimits (category ceilings)
                               VendorPortal / Ratings / Scheme
```

Browser holds anon key only; every backend call carries the JWT, role re-read
from DB; service role never leaves the server. Engineering-truth tables
(`simulation_results`, `risk_assessments`) have **no client write policy**.
Single power-flow entry (`PowerFlowService._compute`) and single threshold
application shared by `/api/assess` and `/assess` (persisted variant).

Thresholds live only in `scenario_config.json` (Rule 8). Label rules verbatim
from the dataset generator: hard `>` first-match-wins
(V>1.05, V<0.90, |rise|>0.05, line>100%, trafo>100%) → CONSTRAINED; caution
`>=` bands (1.03, 0.03 rise, 80% line, 95% trafo, reverse flow) → CAUTION; else
SAFE. Reverse alone is CAUTION, never CONSTRAINED (policy).

Known research limits: 97.6% accuracy optimistic (test-set model selection,
random not bus-disjoint split); line-overload mode untrained (~57% dataset
max); feeder runs ~3–4% low (MAE 5.33%, thresholds calibrated to it);
`penetration = total/1.0` when bus load is 0 (documented bus-6231 artifact,
reproduced faithfully); `pv_bus` cast to int for the fitted encoder.

---

## 3. Data & ML (28 CSVs)

**Bus reference (114 buses):** `valid_pv_buses.csv` 71 eligible LV buses
(`pv_bus` = the only house/locality key in training data; locality proxy =
`feeder_section` + `transformer_association`); `excluded_buses.csv` 43
(source 700 + MV); `electrical_features.csv` 71 (sn_kVA, base voltage,
distance, R/X/Z).

**Scenarios:** `pv_dataset.csv` 1500 (seed 42: random bus, existing 0@70% else
3–15, new 5–250, dedup `(bus,exist,new)`, BASE+PV solves, threshold labels);
`pv_dataset_test.csv` 75; `pv_dataset_augmented.csv` 1692 (+192 near-threshold
sweep 0.035–0.065); `pv_dataset_enriched_augmented.csv` **1692 = production
`DATASET_CURRENT`**; **`pv_dataset_expand_v4.csv` 34 (all SAFE, thin buses to
min 18/bus) + `pv_dataset_enriched_v4_full.csv` 1726** (same Phase-2 method,
versioned, model untouched); `augmentation_candidates.csv` 206;
`residential_scenarios_generated.csv` 900.

**ML splits:** strict 1050/225/225; enriched-18f v1 same; **v2 1184/254/254
(test-v2 = `ML_TEST_SET`)**; v3 1770/411/411. Model `suryagrid_model_v2.pkl`
(sklearn 1.3.2 → numpy<2 → pandapower 3.4.0 pins, non-negotiable), 18 features
(`enriched_features.json` contract-checked at startup), `tree_count` read live.
`pv_dataset_CURRENT.csv` mirrors production; `ml_train_strict.csv` strict-9f
baseline. Generation scripts: `dataset_generation*.py`,
`generate_augmentation_full.py`, `augment_near_threshold.py`,
`enrich*.py`, `generate_expand_v4.py`, `train_ml*.py`, `build_feeder.py`,
`compute_electrical_features.py`, `generate_valid_buses.py`.

---

## 4. Backend (`backend/app/`)

**Services:** `ml_prediction` (18f assembly, int-cast bus, artifact notes),
`power_flow` (BASE/PV, per-element buses/lines/transformers + `energy_balance`
grid/solar/consumption/self-consumed/export; consumption = modelled bus load,
0 on spare sub-buses — full export, risk still from rise+loadings),
`risk_assessment`, `hosting_capacity` (per-bus + simultaneous-section
bisection, overstatement factor), `topology` (networkx, respect_switches=True,
electrical-schematic layout + illustrative `geo_positions`: east = true route
km, anchor 12.9716,77.5946), `grid_assets` (71+43+elec CSVs),
`connection_point` (lat/lon → nearest eligible bus, haversine, provisional),
**`house_mapping` (bus → locality + deterministic houses `{bus}-A/B[/C]`,
20–60 m offsets; screening still uses `pv_bus` only)**,
**`capacity_limits` (Residential 1–10, Commercial/Institutional/Industrial
1–500 kW; PM Surya Ghar ≤10 kW, 2026 net-metering cap 500 kW; unknown→
Residential; assessments/what-if stay 0–5000 for DISCOM studies)**,
`vendor_portal` (sequential statuses, report save/submit guards, return,
verify), **`ratings`** (engagement-gated, 7-day edit, flags), `site_context`
(OSM footprints via Overpass, height/levels/assumed), `vendors`, `scheme`,
`routing`, `storage`.

**API (`/api`, JWT; 429: 30/min sim, 240/min other):** grid
(`buses/summary/topology/topology/{bus}/connection-point/localities`,
`buses/{bus}/houses`, hosting-capacity ×2), assess/twin/applications(+timeline,
assessment, assess, simulations), map, site-context, discom (summary,
applications, decide, transformers, feeders, what-if, feeder capacity,
vendors+review, installations+verify/**return**, documents/url),
vendor-portal (summary/leads/appointments/installations/status/**report/submit**,
opportunities, projects, profile, documents+upload, **ratings**),
citizen reviews (`applications/{id}/reviews`, `…/reviews/eligibility`,
`vendors/{id}/reviews`), scheme+CFA, `/health` (never limited).

---

## 5. Frontend (`frontend/`, Next 14 + `cesium@1.144` + `maplibre@4.7`)

**Portals/pages:** citizen (dashboard, applications+new+`[id]`, map, vendors,
scheme) · discom (dashboard, applications+`[id]` review console, feeders,
transformers, hosting-capacity, what-if, vendors, installations) · vendor
(dashboard, leads, appointments, installations+`[id]` workspace, projects,
applications, profile, register/login). Shared: `AppShell`, `Nav`,
`RiskBadge`, `ApplicationTracker` (history-trigger stages → VERIFIED),
`AssessmentResult`, `TwinDiagram`, **`GridTwin3D`**, `GridMap`, `VendorMap/List`,
`solar3d/{SolarPlanner,RooftopTwin,CesiumScene}`, `lib/{api,types,risk,
tracking,supabase,solar/*}`.

**Twins:** `TwinDiagram` = SVG single-line schematic (before/after, per-asset
risk colors, flow dashes incl. reverse, energy tiles, role badges GRID /
TRANSFORMER / TARGET HOUSE / SOLAR / REVERSE). `GridMap` = MapLibre 2D
(risk/voltage/trafo/line/penetration/capacity layers, illustrative-placement
caveat). **`GridTwin3D`** (GeoLibre pattern: same `TwinResponse`, second
renderer, lazy Cesium chunk) = grounded site-anchored globe: real OSM context
blocks (solid tones + roof caps + `est.` tags) or Ion OSM 3D Tiles when tokened;
schematic pole row west of the real house; transformer boxes; PV modules sized
by actual kW; per-edge animated flow (yellow supply / sky export from real
`direction_after` + export flag); click any asset for live kW/pu/% card
(zero-load buses explained). `CesiumScene`/`SolarPlanner` = rooftop planner
(sun/shading/suitability/array fit, click-any-roof placement via pickPosition +
sampleHeight). DISCOM sidebar exposes twins per-application (standalone
Map/Grid-twin entries removed).

---

## 6. Vendor completion → verification → ratings (this session)

Flow: claim/accept → SITE_VISIT → SCHEDULED → IN_PROGRESS → **completion
report** (13 fields: capacity, panel/inverter make-model-count, inverter ≥
installed enforced, install date, notes, 6-item checklist, ≥2 photos via
validated upload, confirm) → COMPLETED → **submit** (validated) →
VERIFICATION_PENDING → DISCOM **verify** (sole VERIFIED path, app → VERIFIED,
tracker greens) or **return with reason** (→ IN_PROGRESS/INSTALLING, vendor +
citizen ⚠️ banners until resubmit). Sequential steps enforced (422 on skip),
vendor VERIFIED → 403 (service + RLS + revoked columns), panel ±15% warns only,
capacity rechecked vs category ceilings. **Ratings:** citizens rate post-
completion work 1–5 + fixed tags + comment (one per engagement, 7-day edit);
trigger maintains `vendors.rating`; averages on marketplace/profile/dashboard/
DISCOM queue; flags (avg<2.5 n≥3, or 2 recent 1★; newcomers never flagged)
feed existing suspend/reject/reinstate. Fake reviews blocked by engagement
proof + RLS + uniqueness.

---

## 7. Database (Supabase, 15 tables, 38 policies)

Migrations `0001` (schema: applications/history/simulations/risk/vendors/
vendors-docs/appointments/installations/scheme/audit/grid_assets) → `0002`
RLS everywhere → `0003` ledger lock → `0004` column-privilege fix → `0005`
vendor self-update → `0006` audit-actor survival → `0007` placement + 3–11 kW
bounds → **`0008` category ceilings** → **`0009` completion columns** →
**`0010` `vendor_reviews` + average trigger**. Service role bypasses RLS;
anon constrained; engineering/audit tables have no client write path.

---

## 8. Run / test / deploy

```powershell
Copy-Item .env.example .env   # fill Supabase keys + SUPABASE_DB_URL
.\venv\Scripts\pip install -r requirements.txt   # incl. psycopg[binary], pytest
.\venv\Scripts\python.exe backend/scripts/apply_migrations.py
.\venv\Scripts\python.exe backend/seed/seed_grid_assets.py
.\venv\Scripts\python.exe backend/scripts/precompute_grid_map.py  # ~90 s
.\venv\Scripts\python.exe backend/seed/seed_scheme_config.py
.\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --port 8000
cd frontend; npm install; npm run dev   # :3000
```

Checks: `verify_phase1.py` must PASS; `pytest` (60) + `npm test` (113) +
`tsc --noEmit` green; `verify_phase12.py` pre-release. Demo:
`setup_demo_accounts.py` (demo.citizen/discom/vendor@solargrid.test),
`demo_end_to_end.py`. **Render:** `render.yaml` blueprint (backend starterPlus
Docker + frontend starter Docker; Supabase hosted); Dockerfiles carry
artifacts + `ARTIFACTS_DIR`; frontend needs real `NEXT_PUBLIC_API_BASE_URL`
+ rebuild, backend `CORS_ORIGINS` = frontend URL; one-time seed/precompute in
backend Shell; single backend instance (per-process rate limiter). Native
alternative: backend `pip install -r requirements.txt` /
`uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT --workers 1`;
frontend root `frontend`, `npm ci && npm run build`, `npx next start -p $PORT`
(never a Static Site — dynamic routes need Node).

Env: `SUPABASE_URL/ANON_KEY/SERVICE_ROLE_KEY` (+`DB_URL` for migrations);
`APP_ENV/API_HOST/API_PORT/CORS_ORIGINS/ARTIFACTS_DIR`;
`NEXT_PUBLIC_SUPABASE_URL/ANON_KEY/API_BASE_URL[/CESIUM_ION_TOKEN]`;
optional OSRM routing (else straight-line, labelled). Pre-deploy checklist in
`docs/DEPLOYMENT.md` (rotate DB password, verify CFA rates, drop demo data,
CORS, no secret in `NEXT_PUBLIC_*`, keep map caveat).
