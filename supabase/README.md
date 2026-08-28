# Supabase setup — SolarGrid AI

## 1. Create the project

Create a Supabase project, then copy `.env.example` to `.env` at the repo root and fill in:

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<anon key>
SUPABASE_SERVICE_ROLE_KEY=<service role key>
```

Both keys are in **Project Settings → API**.

> **Security.** The service-role key bypasses every Row Level Security policy.
> It belongs only in the backend `.env`, never in a `NEXT_PUBLIC_*` variable and
> never in frontend code. `.env` is git-ignored.

## 2. Apply the migrations

In order. Either paste each file into the Supabase **SQL Editor** and run it, or
use the CLI:

```bash
supabase db push
```

| File | What it does |
|---|---|
| `migrations/0001_init_schema.sql` | 8 enum types, 12 tables, indexes, `updated_at` triggers, auto-profile on signup, automatic status-history logging |
| `migrations/0002_rls_policies.sql` | Enables RLS on all 12 tables, 29 policies, role helper functions, column-level revokes |

## 3. Seed grid metadata from the existing feeder model

```bash
python backend/seed/seed_grid_assets.py --dry-run   # validate first
python backend/seed/seed_grid_assets.py             # write to Supabase
```

Produces 186 rows: 1 substation, 1 feeder, 114 buses (71 PV-eligible + 43 excluded),
30 transformers, 40 lines — read from `feeder_network.json`, `valid_pv_buses.csv`,
`excluded_buses.csv` and `electrical_features.csv`. No value is invented.

## 4. Verify

```bash
python backend/scripts/verify_phase1.py
```

Must report **OVERALL: PASS**, including the live Supabase round-trip once
credentials are set.

## Security model in one table

The rule that matters: **electrical results are not client-writable.** RLS denies
what it does not explicitly permit, so tables with only a `select` policy can be
written by the backend service role alone.

| Table | Client writes? |
|---|---|
| `simulation_results` | **No** — power-flow output, backend only |
| `risk_assessments` | **No** — ML + engineering verdict, backend only |
| `application_status_history` | **No** — written by trigger |
| `grid_assets`, `scheme_config`, `audit_logs` | **No** — reference/audit data |
| `solar_applications` | Yes, own rows, and only in `DRAFT`/`SUBMITTED`/`CANCELLED` |
| `vendors` | Yes, own row, always forced to `PENDING` — no self-approval |
| `installations` | Vendor may progress status but never to `VERIFIED`; the `discom_verified*` columns have `UPDATE` revoked from `authenticated` |
| `profiles` | Yes, own row; `UPDATE` on `role` revoked — no self-promotion |

## Data provenance

`grid_assets` is derived from the **IEEE Comprehensive Test Feeder**, a synthetic
research network. It is not a real DISCOM network, and it carries no geographic
coordinates — `latitude`/`longitude` are `NULL` and `geometry_source` defaults to
`SYNTHETIC_LAYOUT`. Any map placement added later is illustrative.
