# Architecture

## The shape of it

```
Next.js (browser)                    FastAPI (Python 3.12)              Supabase
─────────────────                    ──────────────────────             ────────
citizen / DISCOM / vendor  ──JWT──►  MLPredictionService                Postgres + RLS
                                     PowerFlowService  ──► pandapower   Auth
                                     RiskAssessmentService              Storage
                                     HostingCapacityService
                                     TopologyService
                                     VendorService / VendorPortal
                                     SchemeService
```

The browser holds the **anon key only** and authenticates against Supabase Auth.
Every request to the backend carries that JWT; the backend resolves the user,
re-reads their role from the database, and uses either the caller's own token
(so RLS applies to them) or the service role (for writes clients must never
make). The service-role key never leaves the server.

## The two layers, and which one decides

This is the product's central claim, so it is worth being exact.

**MLPredictionService** loads `suryagrid_model_v2.pkl` — a scikit-learn
pipeline over 18 features — and answers in milliseconds without simulating
anything. It is a pre-screen.

**PowerFlowService** runs the real thing: a BASE case (existing PV) and a PV
case (existing + new) on `feeder_network.json`, then diffs them. About 50 ms.

**RiskAssessmentService** applies the thresholds from `scenario_config.json` to
the power-flow output and returns the verdict. **This is the decision.** The
model's opinion is recorded alongside it and any disagreement is surfaced to the
DISCOM rather than reconciled away.

There is exactly one place a power flow is solved (`PowerFlowService._compute`)
and one place thresholds are applied. `/api/assess` and
`/api/applications/{id}/assess` share that path; the only difference is whether
the result is written down.

### Fidelity to the original research

The threshold logic is a verbatim port of `dataset_generation_phase2.py`,
including its asymmetric comparisons (`>` for hard limits, `>=` for caution
bands). That is not stylistic — it is how the training labels were produced.

A test replays rows from `pv_dataset_enriched_augmented.csv` through the live
services and requires the recomputed label to equal the stored one. If the port
ever drifts, the labels the model learned would no longer describe the system
the application simulates, and that test fails.

## Data flow for one assessment

```
POST /api/applications          RLS: applicant_id = auth.uid()
  └─ POST …/assess
       ├─ GridAssetService      11 static features from CSV (no simulation)
       ├─ MLPredictionService   18-feature vector → SAFE / CAUTION / CONSTRAINED
       ├─ PowerFlowService      BASE + PV power flows
       ├─ RiskAssessmentService thresholds → the verdict
       └─ writes (service role) simulation_results, risk_assessments
                                ↑ neither table has a client write policy
```

## Security model

Authorization is enforced twice, because either layer alone is a single point of
failure:

1. **In the API** — `require_discom` and per-route ownership checks.
2. **In Postgres** — RLS policies plus column-level grants.

The tables that hold engineering truth (`simulation_results`,
`risk_assessments`) have **no client write policy at all**. RLS denies what it
does not explicitly permit, so a citizen cannot alter their own risk verdict
even with a valid token and direct database access.

Two protections RLS cannot express are column grants instead:

- `profiles.role` — `UPDATE` revoked, so nobody self-promotes to DISCOM.
- `installations.discom_verified*` — revoked, so a vendor cannot certify its own
  work.

Both were found by testing rather than assumed: migration 0004 exists because a
column-level `REVOKE` under a table-level `GRANT` is a no-op, and a citizen
really did promote themselves to DISCOM in a test before it was fixed.

## The digital twin and the map

`TopologyService` builds the graph from `feeder_network.json` — the same file
the power flow solves — so the drawing cannot show a topology the simulation
does not have. `respect_switches=True` is required, not preferred: with it
false, paths traverse **open** tie switches and route through connections that
do not exist.

The feeder carries no coordinates. Rather than inventing geography, the layout
places a bus east of the substation by its **true route distance in km**, so the
scale bar measures something real while absolute placement stays illustrative
and is labelled as such.

## Hosting capacity

Not in the original dataset — every row there is one PV size, not a maximum. It
is computed by **bisection on the power flow**: the largest capacity that trips
no hard threshold, roughly 11 solves per bus.

Feeder-section capacity is bisected with every connection in the section
energised **together**. Summing per-bus capacities overstates the limit — on
this feeder by up to **23×**, because each per-bus figure assumes that bus is
the only new connection. Both numbers are returned so the difference is visible;
the sum is labelled "for comparison, not for use".

## Known limitations

Inherited from the research, and worth knowing before quoting any accuracy
number:

- **The 97.6% test accuracy is optimistic.** Model selection was done on the
  test set (`train_ml_v2.py` picks the best by test F1), and the split is random
  rather than bus-disjoint — 83 of 254 test rows have a train row at the same
  bus within 5 kW.
- **The line-overload mode is untrained.** Maximum line loading across the whole
  dataset is ~57%, so no row is labelled by the line rule. The power flow still
  computes it correctly, which is why the power flow decides.
- **The base feeder model runs ~3–4% low** against the IEEE reference (voltage
  MAE 5.33%), and the thresholds were calibrated to that offset. Labels are
  self-consistent but tuned to the model, not to the physical feeder.
- **One feeder, one topology, one load profile.** No time series, no seasonal
  variation, no multi-feeder support.
- **Rate limiting is per-process.** Multiple workers multiply the effective
  limit.

## Repository layout

```
backend/app/services/     the engineering and domain layer
backend/app/api/          routes, grouped by audience
backend/app/core/         config, paths, Supabase clients, security
backend/scripts/          migrations, precompute, verification, demo
backend/tests/            pytest
frontend/app/             citizen, discom and vendor areas
frontend/components/      twin, map, shared UI
frontend/lib/             API client, types, risk thresholds
supabase/migrations/      6 migrations
docs/                     this documentation
*.py, *.csv, *.pkl (root) the original research, unmodified
```
