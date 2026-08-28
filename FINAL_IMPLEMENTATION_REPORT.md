# SolarGrid AI — Final Implementation Report

A full-stack application built around existing rooftop-solar grid-screening
research. The research was reused unchanged; no model was retrained, no dataset
regenerated, no threshold redefined.

**Status: all suites passing.** 34/34 audit checks, 39 pytest, 16 vitest, 428
acceptance checks across twelve phase suites.

---

## 1. Architecture

```
Next.js 14 (browser)              FastAPI (Python 3.12)            Supabase
────────────────────              ─────────────────────            ────────
citizen / DISCOM / vendor  ─JWT─► MLPredictionService              Postgres + RLS
                                  PowerFlowService ──► pandapower  Auth
                                  RiskAssessmentService            Storage
                                  HostingCapacityService
                                  TopologyService · VendorService
                                  VendorPortal · SchemeService
```

The browser holds the **anon key only**. Every backend request carries the
user's JWT; the server re-reads their role from the database and then acts
either as that user (so RLS applies) or as the service role for writes clients
must never make. The service-role key never leaves the server — verified by
scanning both source and the built bundle.

**Scale:** 6,086 lines of backend application code, 8,287 frontend, 991 SQL
across 6 migrations, 12,196 lines of scripts and tests.

### The decision boundary

The ML model is a **pre-screen**; the power flow is the **decision**. There is
exactly one place a power flow is solved (`PowerFlowService._compute`) and one
place thresholds are applied (`RiskAssessmentService`). `/api/assess` and
`/api/applications/{id}/assess` share that path — only persistence differs, so
the two cannot drift.

When the model and the power flow disagree, the disagreement is **surfaced to
the DISCOM, never reconciled**. Every response carries `authority:
"power_flow"`.

---

## 2. Implemented features

| Area | Delivered |
|---|---|
| Citizen | register, apply, live pre-submission grid check, assessment detail, 2D twin, map, installer discovery, PM Surya Ghar |
| DISCOM | dashboard, application queue and review, approve / engineering-review / reject, map, grid twin, feeders, transformers, hosting capacity, what-if, vendor verification, installation verification |
| Vendor | register, dashboard, leads, appointments, installations, projects, profile, documents |
| Engineering | ML pre-screen, power flow, risk verdict, hosting capacity (per bus and per feeder), digital twin, what-if sweeps |
| Platform | 51 API routes, 28 pages, 6 migrations, RLS on 13 tables, audit logging, rate limiting, file uploads |

---

## 3. ML integration

`suryagrid_model_v2.pkl` is loaded once and used unchanged: a scikit-learn
pipeline over 18 features, reproducing its documented predictions exactly
(bus 734 → CONSTRAINED, bus 6231 → CONSTRAINED).

Feature assembly needs **no simulation** — 11 features come from
`valid_pv_buses.csv` and `electrical_features.csv`, the rest from the request
and arithmetic. Verified: `existing_load_at_bus_kw` matches the dataset to
0.0 kW across all 71 buses.

**Two findings preserved rather than "fixed":**

- `pv_bus` is encoded as **int64**, because `train_ml_v2.py` reads the CSV
  without `dtype=str`. Passing a string makes `handle_unknown="ignore"` emit an
  all-zero block with no error. Measured: class predictions identical either
  way, probabilities materially different (0.98 vs 0.833 at bus 734). We feed
  int64, matching the fitted encoder, and document the discrepancy.
- The **zero-load penetration artifact** (`total/1.0`) is reproduced exactly.
  The model was trained on it; "correcting" it would move every prediction away
  from validated behaviour.

---

## 4. Power-flow integration

A verbatim port of `run_case()` / `extract_metrics()` from
`dataset_generation_phase2.py`, including the asymmetric comparisons (`>` hard,
`>=` caution) that produced the training labels.

**The guarantee:** rows from `pv_dataset_enriched_augmented.csv` replayed
through the live services reproduce the stored labels **exactly** — checked in
pytest and in every phase suite, at every sample size tried (40–120 rows).

Base state matches the validated figures: source 4.1784 MW, min voltage
0.9059 pu, T7 at 92.80%. A power flow takes ~50 ms, which is why assessment is
synchronous and hosting-capacity bisection is viable.

**Hosting capacity** did not exist in the dataset — every row there is one PV
size, not a maximum. It is bisected on the real power flow (~11 solves per bus;
1065 solves for the feeder in 66 s). Feeder-section capacity uses **simultaneous
injection**, because summing per-bus capacities overstates the limit by up to
**23×** on this feeder. Both numbers are returned; the sum is labelled "for
comparison, not for use".

---

## 5. Database

13 tables, RLS on every one, 29 policies, 6 migrations.

The governing rule: `simulation_results` and `risk_assessments` have **no client
write policy at all**. RLS denies what it does not permit, so a citizen cannot
alter their own verdict even with a valid token and direct database access.

Three protections RLS cannot express are column grants:
`profiles.role`, `installations.discom_verified*`, and the vendor status
columns.

| Migration | Purpose |
|---|---|
| 0001 | 12 tables, 8 enums, triggers |
| 0002 | RLS, 29 policies |
| 0003 | Migration ledger not client-readable |
| 0004 | **Security fix** — column REVOKE under a table GRANT is a no-op |
| 0005 | Approved vendors could not edit their own profile |
| 0006 | Audit attribution survived deleting the actor |

---

## 6. Security

Enforced twice — in the API and in Postgres — because either alone is a single
point of failure.

**Four bugs were found by testing, not by inspection:**

1. **Privilege escalation.** A citizen set their own `profiles.role` to
   `DISCOM`. A column-level `REVOKE` under a table-level `GRANT` does nothing,
   and Supabase grants table-level UPDATE by default. Fixed in 0004.
2. **Approved vendors locked out.** The self-update policy required the row to
   *remain* `PENDING`, blocking every legitimate edit after approval. Fixed in
   0005.
3. **Audit log forgetting the actor.** `ON DELETE SET NULL` meant deleting an
   account erased who did what — 25 of 25 recent rows had a null actor. Fixed in
   0006 with a durable `actor_ref`.
4. **500 on a malformed identifier.** A non-UUID path parameter surfaced as a
   server fault; now a clean 404.

**Verified boundaries:**

```
citizen → DISCOM routes                    403
citizen writes risk / simulation directly  refused by RLS
citizen self-approves an application       0 rows changed
citizen self-promotes to DISCOM            role unchanged
vendor sets VERIFIED (4 attack paths)      all refused
vendor self-registers as APPROVED          forced PENDING
unapproved vendor discoverable             no
service-role key in bundle                 absent
```

Rate limiting: 30/min on simulation routes, 240/min authenticated, 60/min
anonymous; `/health` never limited. **Counters are per-process** — disclosed in
`/health` rather than hidden.

File uploads: type decided by **magic bytes**, not the declared `Content-Type`.
Private bucket, server-generated paths, 5-minute signed URLs. Executables
renamed as PDFs, mismatched types, oversized and undersized files all rejected.

Errors return a reference; no traceback, SQL, driver text or hostname crosses
the boundary.

---

## 7. Testing

| Suite | Result | Covers |
|---|---|---|
| `pytest` | **39 passed** | 12 required scenarios, regressions, ML/PF/API/RLS integration |
| `vitest` | **16 passed** | threshold logic, including the backend's asymmetric comparisons |
| `verify_phase1–12` | **428 checks, all PASS** | one acceptance suite per build phase |
| `final_audit` | **34/34** | credentials, fabricated values, thresholds, dead code, dependencies, API contract, database state |
| `demo_end_to_end` | 12 steps | the whole journey through the real API |

The regression tests carry an explicit instruction: if bus 734 or bus 6231 stops
being CONSTRAINED, find out what changed — do not adjust the expectation.

**Roughly a dozen failures during development were my tests being wrong, not the
code** — `git grep` silently skipping untracked files, a quote-style mismatch,
an illegal HTTP header the client refused to send, a rate-limit block poisoning
later checks, and an assumption that bus 6231 had load when it has none. Each
was corrected in the test rather than worked around in the code.

---

## 8. Known limitations

**Inherited from the research** — these bound what any accuracy claim means:

- **97.6% test accuracy is optimistic.** Model selection was done on the test
  set (`train_ml_v2.py` picks by test F1), and the split is random rather than
  bus-disjoint — 83 of 254 test rows have a train row at the same bus within
  5 kW.
- **Line overload is untrained.** Max line loading across the dataset is ~57%,
  so no row is labelled by that rule. The power flow still computes it, which is
  why the power flow decides.
- **The base model runs 3–4% low** against the IEEE reference (voltage MAE
  5.33%); thresholds were calibrated to that offset.
- **One feeder, one topology, one load profile.** No time series, no seasonality.

**Introduced by this application, and disclosed in the product:**

- **Coordinates are synthetic.** Distances between assets are real; absolute
  placement is not. Labelled on every asset and on the map.
- **CFA rates are unverified placeholders**, flagged red until checked against
  the official portal.
- **Vendor distances are straight-line** until a routing provider is configured,
  and are never described as travel distance.
- **Feeder capacity assumes an even split** across a section's buses; a
  different distribution gives a different total.
- **Rate limiting is per-process.**
- **Demo vendors are fictional.**

---

## 9. Future work

**Before production**

1. Rotate the Supabase database password.
2. Verify the CFA rates and clear `verification_required`.
3. Move rate limiting to Redis, then scale workers.
4. Remove demo data and accounts.
5. Set `CORS_ORIGINS` to the real origin.

**Engineering**

6. Re-train with model selection on validation and a **bus-disjoint** test split
   — the honest accuracy number is probably lower than 97.6% and worth knowing.
7. Generate line-overload scenarios so that failure mode is represented.
8. Support multiple feeders; `feeder_id` is already carried throughout.
9. Time-series load profiles, so capacity reflects worst-case hours.
10. Reconcile the 3–4% base-model offset against the IEEE reference.

**Product**

11. Wire the document UI to `POST /api/vendor/documents/upload` (the validated
    endpoint exists; the form still records a reference).
12. Configure a routing provider for real travel distances.
13. Notifications on status changes.
14. Real coordinates from a DISCOM GIS export, replacing the synthetic layout.

---

## Closing note

The most valuable outcome was not the feature count. It was that **testing found
four security bugs and three engineering bugs** that inspection had missed — a
privilege escalation, a topology graph routing through open switches, a
precompute clobbering line connectivity, and an audit log quietly forgetting who
acted.

Where a number could not be computed honestly, it is absent or labelled rather
than estimated: no distance without a location, no capacity from a summed
approximation, no subsidy figure without its unverified flag.
