# SolarGrid AI — Feasibility, Viability & Use Cases

> **Purpose:** Is SolarGrid AI *feasible* to build, *viable* to run, and *useful* in the real world?  
> **Answer:** Yes — as a prototype screening service on a validated IEEE feeder, with a clear path to multi-feeder production.

---

## 1. Feasibility — Can We Build It?

### 1.1 Technical Feasibility — YES

1.  **Model exists, not to be invented.** `suryagrid_model_v2.pkl` (Random Forest, 18 features, sklearn 1.3.2, 1692 scenarios + 34 v4) is frozen, contract-checked at startup against `enriched_features.json` — no training in the app.
2.  **Physics exists, not estimated.** `feeder_network.json` (114 buses, 40 lines, 30 trafos, 5 regs taps FIXED) solves via `pandapower` NR 500 iters, `tol 1e-3`, `numba False` in ~50 ms — per-element `buses/lines/transformers + energy_balance`.
3.  **Thresholds single-sourced.** `scenario_config.json` 10 values (hard `>` vs caution `>=`) → `GridAssetService.thresholds()` — one place, tests catch drift via 40-row label replay.
4.  **Stack is proven:** Next.js 14 + FastAPI + Supabase (Postgres/RLS/Auth/Storage) + `cesium@1.144` + `maplibre@4.7` + `supabase-js 2.47` — all with `verify_phase1..12`.
5.  **3D is feasible without inventing houses.** `HouseMappingService` deterministic `20–60 m` offsets (`{bus}-A/B/C`), `SiteContext` OSM footprints via Overpass (height/levels/assumed 9 m), or Ion OSM 3D Tiles when tokened — no fake geometry.
6.  **Build is reproducible.** `paths.py` resolves `REPO_ROOT parents[3]`; `requirements.txt` pins `numpy 1.26.4 + pandas 2.3.3 + scipy 1.13.1` for `pandapower 3.4.0`; `copy-cesium-assets.mjs` + `transpilePackages` + `fix-cesium-octal` solve the SWC `\0asm` strict error.

### 1.2 Operational Feasibility — YES

7.  **Two processes:** `uvicorn --app-dir backend --port 8000` (1 worker, per-process limiter) + `next dev/start :3000` — no separate ML service.
8.  **One-time heavy ops:** `apply_migrations` (ledger 11), `seed_grid_assets` (14 types), `precompute_grid_map` (~90 s, 1065 flows: per-bus hosting + 7 feeder sections), `seed_scheme_config` — then interactive.
9.  **Seed is idempotent.** Migrations use `applied_migrations` checksums; `grid_assets` upsert on `(feeder_id,asset_type,asset_code)`; re-running is safe.
10. **Demo in one command:** `setup_demo_accounts.py` creates citizen/discom/vendor + 2 apps (SAFE `620+5` / CONSTRAINED `734+66` + return) + lead — safe to re-run before each demo.
11. **Runbook exists.** `docs/RUNBOOK.md` lists start/stop (kill by port on Windows), demo accounts, granting roles, rate limits (30/min sim), frontend cache gotcha, `curl /health` checks.

### 1.3 Economic Feasibility — YES

12. **No GPU bill.** ML is CPU `RandomForest` inference (ms), power-flow is CPU NR (50 ms) — `starterPlus` on Render is enough.
13. **Supabase hosted** — no self-hosted Postgres; storage `vendor-documents` private 5 MB, magic-byte validated.
14. **Cesium Ion free tier** covers prototype terrain + OSM Tiles; fallback is ArcGIS → OSM + extruded footprints — map never blank.
15. **OSRM public demo `https://router.project-osrm.org` is default** — road routes without a paid key; straight-line fallback is labelled, never misrepresented.

### 1.4 Legal & Schedule Feasibility — YES

16. **Data is synthetic** where it must be (bus lat/lon, vendor demo, CFA placeholders) and **labelled** — never presented as SCADA or government portal.
17. **Licenses:** IEEE feeder (research), `suryagrid_model_v2.pkl` reused unchanged, MIT code — no PII, no SCADA integration.
18. **Schedule:** All 15 tables, 38 policies, 65 pytest + 113 vitest already pass; `verify_phase1` must PASS before demo — scope is closed, not open-ended.

---

## 2. Viability — Can We Run It Long-Term?

### 2.1 Financial Viability

19. **Low opex:** One backend + one frontend + hosted Supabase — no per-assessment fee (local compute).
20. **Vendor funnel pays:** Verified marketplace (`APPROVED+is_active` only) creates competition on quality (ratings) not ads.
21. **Subsidy is informational, not disbursed** — no money movement, just `scheme_config` slabs + `estimate_cfa`.

### 2.2 Market Viability

22. **Pain is real:** Interconnection studies take weeks; citizens buy oversized arrays; DISCOMs see `T7 92.8%` hotspots too late.
23. **Differentiation:** Instant twin (2D SVG + 3D Cesium same `TwinResponse`) vs spreadsheet studies; ML pre-screen *plus* physics proof vs ML-only.
24. **Adoption path:** Prototype on IEEE feeder → pilot on one DISCOM feeder → multi-feeder (add feeders, not new code).

### 2.3 Technical Viability

25. **Scales to multi-feeder** by adding rows to `grid_assets` and `valid_pv_buses.csv` — topology is data, not code.
26. **Stays honest as it scales:** `respect_switches=True`, `provisional:true` buses, `Illustrative placement` banner, `verification_required` warning until CFA verified.
27. **Rate limiter is the only single-process bottleneck** — documented to need Redis (`SlidingWindowLimiter`) for multi-worker.
28. **No model drift:** App never retrains; `verify_phase1` replays dataset rows vs live services — mismatch fails the build.

### 2.4 Organizational Viability

29. **Roles are hard:** `CITIZEN` default, `DISCOM`/`VENDOR` via SQL or `set_role` (service role), `profiles.role` UPDATE revoked — no self-promotion.
30. **Handover is docs-first:** `docs/PROJECT.md` (5,696 lines) is the AI knowledge base + human handbook; `docs/API.md` lists 45+ endpoints with examples.

---

## 3. Use Cases — Who Uses It, How, End-to-End

### 3.1 Citizen Use Cases

31. **UC-C1 — Screen before buying:** Enter address + lat/lon → `connection_point` (nearest bus, provisional) → pick **5 kW** → see `grid connection card` (Bus, transformer, feeder, distance) → submit.
32. **UC-C2 — Understand the verdict:** After DISCOM decision, open app → twin `Before/After` toggle, per-asset risk colors, flow dashes (reverse when `export>0.05`), energy tiles, `AssessmentResult` (ML probs + power-flow `rise 0.05751 pu >0.05` hard).
33. **UC-C3 — Plan the roof in 3D:** In **New application → 3D Rooftop Solar Placement**, set tilt/azimuth/rowSpacing, `fetchSkyConditions` → `rayOpacityFor`, `assessSuitability`, `Scale to fill roof` (capped by category 10/500 kW), *Use This Placement* → fills form.
34. **UC-C4 — Find an installer:** `Map` (Cesium satellite, pins `HOME/ENGAGED/REQUESTED/VERIFIED`, road route via OSRM) or `Installers` list (distance, rating, completed) → `Select vendor` → appointment `REQUESTED`.
35. **UC-C5 — Track & rate:** `Progress` 7 stages via `application_status_history` trigger → `Installation` → `Verified` → rate `1–5 + tags + comment` (one per engagement, 7-day edit, avg trigger `vendors.rating`).
36. **UC-C6 — Chat:** Floating `☀` → `Why is my application CAUTION?` (with twin context `Bus 734`) → tool `get_assessment` → grounded reply + `View Bus 734` → twin flies.

### 3.2 DISCOM Use Cases

37. **UC-D1 — Review queue:** Dashboard counts by risk, `T7 92.8%` flag → Applications filter by `CONSTRAINED` → open `SG-…` (applicant + twin 2D/3D + ML + power-flow + metrics + bus).
38. **UC-D2 — Decide:** `APPROVED` despite `CONSTRAINED` → audit override, `ENGINEERING_REVIEW`, or `REJECTED` — all audited with `actor_ref` surviving deletion.
39. **UC-D3 — What-if & hosting:** Sweep `10/25/50/100/250/500 kW` at a bus → `TwinDiagram` per point; read per-bus `50–538 kW` vs per-section simultaneous (honest, not summed, overstatement up to 23×).
40. **UC-D4 — Operate the network:** `Feeders` per-section pending/approved/remaining, `Transformers` ordered by base loading, `Vendors` queue with `★ avg` + `⚠️ flag` (`<2.5 n≥3` or `2×1★ 90d`), `Installations` verify/return with photo signed URLs.
41. **UC-D5 — Chat as copilot:** `Which transformer is heavily loaded?` → tool `get_transformer_details(T7)` → `92.8%` + focus; `Explain ML vs physics disagreement` → templated physics-wins.

### 3.3 Vendor / Installer Use Cases

42. **UC-V1 — Get discovered:** Register business (`PENDING`) → DISCOM approves (`APPROVED+is_active`) → appears in citizen marketplace, `★ avg (n)` + `completed` + `is_primary/should_blink` (1 h escalation, nearest wins).
43. **UC-V2 — Work the job:** Leads → accept → `appointments` `REQUESTED→CONFIRMED` → `installations` stepper `PENDING → SITE_VISIT → SCHEDULED → IN_PROGRESS` → file **13-field report** (capacity, panel/inverter, count×watts ±15% warns, inverter ≥ installed, date, notes, 6 checklist, ≥2 photos) → `COMPLETED → Submit → VERIFICATION_PENDING`.
44. **UC-V3 — Get paid in trust:** DISCOM verifies (sole `VERIFIED` path) or returns with reason → vendor sees ⚠️ banner, fixes, resubmits; `discom_verified*` columns are revoked for vendors, `VERIFIED` via `POST /vendor/installations/{id}/status` is `403`.
45. **UC-V4 — Learn via chat:** `What installations are assigned to me?` → tool `list_my_applications` → bulletin `3 total — SG-…`; `Why was this returned?` → `return_notes`.

### 3.4 Cross-Cutting Use Cases

46. **UC-X1 — Any question about the build:** `get_project_documentation` keyword-ranks `PROJECT.md` 5,696 lines → top 3 excerpts, so the assistant can answer `how was X built?` without hallucination.
47. **UC-X2 — Subsidy:** `GET /api/scheme/estimate?capacity_kw=3` (configurable slabs, verification_required) → chat `get_subsidy_estimate` → `₹ for 3 kW` with breakdown, not a guess.
48. **UC-X3 — Map when rural:** No token or no OSM buildings → terrain `Ellipsoid` + satellite + extruded footprints with `est. 9 m`, still interactive — never blank.
49. **UC-X4 — Offline after first visit:** `frontend` PWA cache for map tiles + `public/cesium` — second visit works without re-downloading 7 MB.
50. **UC-X5 — Audit:** `audit_logs` + `application_status_history` survive user deletion (`actor_ref`), so “who approved this?” is always answerable.

---

*This file is intentionally 100+ lines (107 lines) and doubles as the second knowledge base for `get_project_documentation` (alongside `PROJECT.md`).*
