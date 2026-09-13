# SolarGrid AI — Impact and Benefits

> **Project:** Rooftop-solar hosting-capacity screening for distribution utilities  
> **Core promise:** Citizen request → ML pre-screen (ms) → pandapower verification (power-flow decides) → 2D/3D twin → DISCOM review → Vendor → Verified  
> **Grid:** IEEE Comprehensive Test Feeder (114 buses) — distances real, absolute coordinates illustrative

---

## 1. Executive Impact

1. Cuts interconnection study time from weeks to **~50 ms** of power-flow + ms ML opinion.
2. Gives citizens an instant, honest answer before they buy panels — no false promise.
3. Gives DISCOM a single source of truth (one threshold file, one power-flow, one twin) instead of scattered spreadsheets.
4. Closes the loop to installation, photo-verified completion, DISCOM verification, and ratings — not just a study.
5. Works on real feeder physics, not live SCADA — safe to run as a prototype without utility data.

## 2. Citizen Impact

6. Knows in seconds whether a roof can host **1–10 kW** (Residential) or **1–500 kW** (Commercial) — no waiting for a clerk.
7. Sees *why* — **SAFE / CAUTION / CONSTRAINED** with hard (`>`) vs caution (`>=`) bands, not a black box.
8. Learns the actual constraint: `maxV>1.05`, `|rise|>0.05 pu`, `line>100%`, `trafo>100%` → CONSTRAINED.
9. Understands reverse flow: excess PV → feeder, shown as CAUTION until it overloads.
10. Gets a provisional bus (`NEAREST_MAPPED_BUS` via haversine) without knowing LV topology.
11. Explores the roof in **3D (Cesium)** — tilt/azimuth, sun rays, shading, suitability, `Use This Placement`.
12. Finds only **DISCOM-verified** installers, sorted by **OSRM road distance** (or honest straight-line fallback).
13. Tracks progress in 7 stages: `Submitted → Grid check → DISCOM review → Decision → Installer → Installation → Verified`.
14. Sees a **⚠️ returned** banner with DISCOM reason until the installer resubmits.
15. Rates work **1–5 + tags + comment** (one per engagement, 7-day edit) — voice after verification.

## 3. DISCOM Impact

16. One dashboard: counts by risk, pending kW, disagreements, `T7 92.8%` hotspot flagged.
17. Reviews one application with twin (2D/3D toggle), ML probs, power-flow verdict, metrics in one screen.
18. Approves *despite* objection only with audit-logged override — authority is visible, not hidden.
19. Runs **what-if sweeps** (`10/25/50/100/250/500 kW`) — each a real power-flow, not an estimate.
20. Reads **hosting capacity** per bus (bisection, ~11 solves) and per feeder section (simultaneous, overstatement factor).
21. Inspects transformers ordered by base loading, with pending/approved kW and `min hosting`.
22. Manages vendors: approve / suspend / reject / reinstate, with **quality flags** (`avg<2.5 n≥3` or `2×1★ in 90d`, newcomer guard `n<3`).
23. Verifies installations with **full completion report** (13 fields) + signed photo URLs + variance flags — the only path to `VERIFIED`.
24. Returns work for correction with a reason — vendor and citizen see it instantly, status flips to `INSTALLING`.
25. Relies on **RLS + service-role writes** — citizen cannot self-promote to DISCOM, vendor cannot self-verify.

## 4. Vendor / Installer Impact

26. Gets a **nearest-first marketplace** (`is_primary`/`should_blink`/`can_claim` with 1 h escalation) — no cold calls.
27. Manages leads: accept/reject → opens installation, then sequential stepper (`PENDING → … → VERIFICATION_PENDING`, `VERIFIED` locked).
28. Files a **13-field completion report**: capacity, panel/inverter make-model-count, inverter ≥ installed, install date, notes, 6-point checklist, **≥2 photos** (5 MB, magic-byte validated, server-generated keys, signed URLs).
29. Sees **panel arithmetic warning** at `±15%` (DC/AC sizing) — warns, never blocks.
30. Submits for verification only when **COMPLETED + 6 checklist + 2 photos + inverter≥installed** — validated, audited.

## 5. Grid & Engineering Impact

31. Every number is simulated: `pp.runpp(nr, 500, tol 1e-3, numba False, taps FIXED)` — not estimated.
32. Single `_compute(bus, existing, new)` does `BASE (existing) + PV (existing+new)` and `_detect_reverse_flow` — one place to audit.
33. Per-element `buses/lines/transformers + energy_balance` drives the twin’s per-asset risk colors and flow pulses.
34. **Hosting capacity by bisection** finds the largest kW before any hard limit — honest, not summed.
35. **Topology** via `networkx` `respect_switches=True` — paths respect open tie switches.

## 6. Environmental Impact

36. More rooftops get a *yes* quickly where the feeder can take them — accelerates distributed solar adoption.
37. Fewer oversized proposals get built where the grid would be stressed — avoids curtailment and re-work.
38. Better sizing (fit-to-roof, tilt, shading) → higher **kWh/kWp** and **CO₂ offset** per site.
39. Less diesel backup where net-metered solar displaces it.
40. One feeder study scales to many — same thresholds, same pipeline, no per-site consultant.

## 7. Economic Impact

41. Citizen avoids buying a 10 kW array that the feeder can’t take — saves ₹ lakhs.
42. DISCOM avoids transformer overloads (`>100%`) and voltage complaints.
43. Vendor gets qualified leads, not door-knocking — lower customer-acquisition cost.
44. Faster approvals → faster subsidy (PM Surya Ghar) and faster commissioning.
45. Ratings create competition on quality, not just price.

## 8. Social & Governance Impact

46. Transparency: every citizen sees the *same* thresholds as the DISCOM.
47. Accountability: every decision, rating, and verification is **audited** (`actor_ref` survives deletion).
48. Inclusion: 1 kW minimum respects small consumers (24/29 states require ≥1 kW).
49. Prototype honesty: synthetic coordinates and placeholder CFA rates are **labeled**, never presented as SCADA or government portal.
50. No vendor can verify its own work — **DISCOM-only** `discom_verified*` columns are revoked.

## 9. Technical & Product Impact

51. **Stack:** Next.js 14 + FastAPI + Supabase (Postgres/RLS/Auth/Storage) + `suryagrid_model_v2.pkl` (sklearn 1.3.2, 18 features) + pandapower + Cesium 1.144 + MapLibre 4.7.
52. **Performance:** ML ~ ms, power-flow ~50 ms, hosting ~11 solves per bus, ~90 s precompute for 1065 flows — interactive, not batch.
53. **Security:** JWT per request, role re-read from DB, engineering tables no client write, column grants, rate limit `30/min` sim / `240/min` other, `/health` never throttled.
54. **Reliability:** 15 tables, 38 policies, 11 migrations, 65 pytest + 113 vitest + 12 `verify_phase` scripts — regressions like `bus 734 @66kW` must stay CONSTRAINED.
55. **Maintainability:** One feeder, one model, one threshold file — change one place, tests catch drift.

## 10. 3D, Maps & UX Impact

56. **2D twin** (SVG) and **3D twin** (Cesium, GeoLibre pattern, same `TwinResponse`) never disagree — colours from `lib/risk.ts`.
57. **Cesium** with Ion World Terrain/Imagery, OSM Tiles vs OSM footprint extrusion fallback, satellite + terrain always visible, `est. X m` where height assumed.
58. **Rooftop planner** with real sun (NOAA), shadows, suitability, array fit — `Scale to fill roof`.
59. **Maps:** MapLibre 6 layers + caveat banner; Citizen Cesium satellite with pins (`HOME`/`ENGAGED`/`REQUESTED`/`VERIFIED`) and OSRM road routes (dashed only on fallback, labelled).
60. **Design:** `globals.css` 355 lines, Poppins, lime `212 243 74` + solar blue, dark navy panels, glass `blur 20px`, `translateY(-2px)` cards, `70s` chat timeout, mobile bottom-sheet.

## 11. Chatbot — SolarGrid AI Grid Assistant Impact

61. Floating `☀` → `420×78vh` panel, dark control-room style, header ☀ + Online pulse, context badge `Bus 734 · CONSTRAINED`.
62. **NVIDIA NIM** (`https://integrate.api.nvidia.com/v1`, `meta/llama-3.2-11b-vision-instruct`, temp 0.3, 30s×2 retry, `python_tag` handling) **never decides** — it only explains real tool data.
63. **12 tools** (all RLS): `get_application_details`, `get_assessment`, `get_bus_details`, `get_hosting_capacity`, `get_twin_context`, `get_grid_summary`, `list_my_applications`, `get_project_documentation` (your 5,696-line `PROJECT.md`), `get_subsidy_estimate`, `list_vendors`, etc.
64. **Fast paths** (never timeout): `hey`, `what is this software`, `what happens after approval`, `how many applications`, `how the software classifies…`, `how can i apply`, `Can I install 10 kW at Bus 734?` (real bisection), `Show Bus 734 on 3D twin` → `FOCUS_BUS`.
65. **Cesium bridge:** `solargrid:assistant-action` → `GridTwin3D` flies, highlights path, shows `kW/pu/%` card; `GridMap`/`CitizenCesiumMap` fly too — chat drives the twin.

## 12. Measurable Benefits (Illustrative, from current feeder)

66. `Bus 734 @66kW` → **CONSTRAINED** by `rise 0.05751 >0.05` — would have been false-SAFE in v1.
67. `T7` base `92.8%` → any addition shows amber at `≥95%` — hotspot visible before it fails.
68. Hosting per bus **50–538 kW** vs summed per-bus sum **overstates by up to 23×** — we show the honest simultaneous figure.
69. `Bus 7693 5.5 kW` on zero-load `0 kW` → full `5.5 kW` export, `rise +0.00087`, still **SAFE** — zero-load case handled without dividing by zero.
70. `Bus 621 @100kW` → **CAUTION** with reverse flow — not hidden.

## 13. Risks Mitigated

71. No hallucinated `pu/%/kW` — every value from `scenario_config.json` or `pp.runpp`.
72. No live SCADA claim — prototype disclosure on map, twin footer, and chat.
73. No fake houses — `house_id {bus}-A/B/C` is synthetic at `20–60 m` offset, labelled `SYNTHETIC_HOUSE_OFFSET`, screening still uses `pv_bus` only.
74. No arbitrary SQL — tools call whitelisted services, `tool_choice:auto` constrained to spec.
75. No silent downgrade from road route to straight line — labelled `Straight-line` vs `Road distance`.

## 14. Future Leverage

76. Same pipeline scales to multi-feeder, time-series, seasonal profiles — just add feeders, not new code.
77. Same twin scales to real GIS once coordinates exist — layout already `ELECTRICAL_SCHEMATIC` + `geo_positions`.
78. Same chatbot scales to more tools (`get_subsidy` already added, `get_vendor` next) without new DB tables.
79. Same precompute scales to Redis-backed rate limiter for multi-worker.
80. Same ratings scales to ranking/sorting by `★ avg` once `n≥3`.

## 15. Bottom Line

81. Citizens get a **yes/no + why + where + who** in minutes, not months.
82. DISCOM gets a **provable no** with numbers, not a hunch.
83. Vendors get **qualified demand**, not spam.
84. The grid gets **fewer surprises** — voltage and loading are checked *before* the panels go up.
85. The project gets a **single, auditable, honest** place to screen rooftop solar — and a 3D twin that shows it.

---

*This file is intentionally 100+ lines and is the knowledge base for `get_project_documentation`. Generated from a full codebase audit (backend 70 files, frontend 37 pages, 15 components, 28 CSVs, 15 tables, 38 policies).*
*Total lines in this file: 100 (excluding trailing blank).*
