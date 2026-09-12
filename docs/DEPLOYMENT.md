# Deployment

## Before you deploy anything

These are not polish items. Each one is a way the system can mislead someone.

- [ ] **Rotate the Supabase database password** if the connection string has
      ever been pasted into a terminal, a log, a chat, or a screenshot.
- [ ] **Verify the PM Surya Ghar rates** against the official portal, then clear
      `verification_required` in `scheme_config`. Until you do, the app displays
      a red warning that the figures are placeholders — which is correct, so do
      not remove the warning instead of doing the check.
- [ ] **Check the official links resolve** (`pmsuryaghar.gov.in`, `mnre.gov.in`).
- [ ] **Remove the demo data**: `demo_end_to_end.py --reset`,
      `seed_demo_vendors.py --remove`, and delete the `demo.*@solargrid.test`
      accounts.
- [ ] **Set `CORS_ORIGINS`** to your real frontend origin, not `localhost`.
- [ ] **Confirm no `NEXT_PUBLIC_` variable holds a service-role key or database
      URL.** `verify_phase12.py` scans the source and the built bundle.
- [ ] **Decide about the map basemap.** Street tiles under synthetic coordinates
      imply the feeder is physically there. The caveat badge is on by default —
      keep it, or turn the basemap off.

## Environments

| Piece | Runs on |
|---|---|
| Backend | Python 3.12, one uvicorn worker (see below) |
| Frontend | Node 20+, `next start`, or any Next.js host |
| Database, auth, storage | Supabase (hosted) |

## Render (blueprint)

`render.yaml` at the repo root defines both services (Docker; Supabase stays
hosted — Render runs only the apps):

1. Push this repo to GitHub; in Render: **New → Blueprint**, point at it.
2. Set secrets (both services, all `sync: false` in the blueprint):
   backend — `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`;
   frontend — `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`,
   `NEXT_PUBLIC_API_BASE_URL` (= backend URL), optionally
   `NEXT_PUBLIC_CESIUM_ION_TOKEN`.
3. Deploy backend first; then set frontend's `NEXT_PUBLIC_API_BASE_URL` to the
   live backend URL and backend's `CORS_ORIGINS` to the live frontend URL, and
   redeploy both (Next.js inlines `NEXT_PUBLIC_*` at build time, so the
   frontend must rebuild after the URL is set).
4. One-time data load, in backend **Shell** (needs `SUPABASE_DB_URL` set just
   for this step — migrations only; it is never needed at runtime):
   ```bash
   python backend/scripts/apply_migrations.py
   python backend/seed/seed_grid_assets.py
   python backend/scripts/precompute_grid_map.py   # ~90 s, 1000+ power flows
   python backend/seed/seed_scheme_config.py
   ```
5. Check `https://<backend>/health`, then
   `verify_phase1.py` / `verify_phase12.py` against the live URLs.

Keep one backend instance (free/starter): the rate limiter is per-process, and
`precompute_grid_map` is run once, not per deploy. Re-run it only when the
feeder model changes.

## Docker

```bash
docker compose up --build
```

Backend on `:8000`, frontend on `:3000`. Both read the root `.env`.

Supabase is deliberately **not** in the compose file. It holds the live schema
and your grid data; pointing a container at a throwaway database would give you
a system that starts and knows nothing.

The backend image copies the engineering artifacts (model, feeder network,
threshold config, feature CSVs) into `/app` and sets `ARTIFACTS_DIR`. Without
them the API refuses to start rather than serving empty answers.

## Manual deployment

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python backend/scripts/apply_migrations.py
```

```bash
.venv/bin/python backend/seed/seed_grid_assets.py && .venv/bin/python backend/scripts/precompute_grid_map.py
```

```bash
.venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

```bash
cd frontend && npm ci && npm run build && npm run start
```

`precompute_grid_map.py` takes about 90 seconds: 1065 power flows for per-bus
hosting capacity, plus 7 feeder sections. Re-run it whenever the feeder model
changes.

## Scaling, honestly

**Run one backend worker until the rate limiter is replaced.** Counters live in
process memory, so N workers allow roughly N times the configured limit, and a
restart clears them. `/health` reports this. To scale out, back
`SlidingWindowLimiter` with Redis — the interface is already isolated in
`backend/app/core/security.py`.

Each assessment costs one or two power flows (~50 ms of CPU). That is fine for
interactive use and will not survive a scraper, which is why the simulation
routes have their own tighter bucket.

`GET /api/discom/hosting-capacity/{bus}` computes on demand (~11 solves). The
map and the DISCOM pages read precomputed values instead.

## Migrations

Applied in order, transactionally, with a checksummed ledger:

```bash
.venv/bin/python backend/scripts/apply_migrations.py --status
```

| Migration | Purpose |
|---|---|
| `0001_init_schema` | 12 tables, 8 enums, triggers |
| `0002_rls_policies` | RLS on every table, 29 policies |
| `0003_lock_migration_ledger` | Ledger not client-readable |
| `0004_fix_column_privileges` | **Security fix** — a column `REVOKE` under a table `GRANT` is a no-op; a citizen could set their own role to DISCOM |
| `0005_fix_vendor_self_update` | Approved vendors could not edit their own profile |
| `0006_audit_actor_survives_deletion` | Deleting a user erased who did what in the audit log |
| `0007_solar_placement_and_rooftop_limits` | Planner proposal column + residential 3–11 kW bounds |
| `0008_category_capacity_limits` | Category ceilings (Residential 1–10, others 1–500 kW) |
| `0009_installation_completion_report` | Vendor completion-report columns |
| `0010_vendor_reviews` | Citizen ratings + live average trigger |

Re-running is safe; applied migrations are skipped. A file edited after being
applied is flagged.

## Backups

Supabase provides database backups. Two things are **not** in the database and
must be kept with the code:

- the engineering artifacts (`suryagrid_model_v2.pkl`, `feeder_network.json`,
  `scenario_config.json`, the feature CSVs) — the application will not start
  without them;
- `.env`, which is git-ignored by design.

## Monitoring

`GET /health` reports whether artifacts are present, whether Supabase is
configured, and the rate-limit policy. It is never rate limited, so a monitor
under load sees the truth rather than a 429.

Unhandled errors log a reference and return only that reference to the caller.
When someone reports a problem, ask for the reference and grep the logs.

Audit entries carry `actor_ref`, which survives deletion of the account — so
"who approved this" is still answerable after someone leaves.

## After deploying

```bash
.venv/bin/python backend/scripts/verify_phase1.py
```

```bash
.venv/bin/python backend/scripts/verify_phase12.py
```

The first proves the model still reproduces its documented predictions; the
second re-runs the security checks against the live deployment.
