# Environment variables

Copy `.env.example` to `.env` and fill it in. `.env` is git-ignored; never commit it.

## Supabase

| Variable | Required | Notes |
|---|---|---|
| `SUPABASE_URL` | yes | The **project URL**, `https://<ref>.supabase.co`. Not the REST endpoint, not the database string. |
| `SUPABASE_ANON_KEY` | yes | Public key. Safe in the browser — Row Level Security constrains it. |
| `SUPABASE_SERVICE_ROLE_KEY` | yes | **Bypasses all RLS. Backend only.** Never prefix with `NEXT_PUBLIC_`. |
| `SUPABASE_DB_URL` | for migrations | `postgresql://…` connection string. Contains your database password; treat it as a key. |
| `SUPABASE_REST_API` | optional | Only used to derive the project URL if `SUPABASE_URL` is unavailable. |

The config layer normalises all three URL shapes, so a mixed-up `.env` still
works — but set them correctly anyway.

## Backend

| Variable | Default | Notes |
|---|---|---|
| `APP_ENV` | `development` | Label only. |
| `API_HOST` | `127.0.0.1` | Use `0.0.0.0` in a container. |
| `API_PORT` | `8000` | |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated. Set to your real frontend origin in production. |
| `ARTIFACTS_DIR` | repository root | Where the model, feeder and CSVs live. |

## Routing (optional)

| Variable | Default | Notes |
|---|---|---|
| `ROUTING_PROVIDER` | unset | `osrm` enables real road routing. |
| `ROUTING_BASE_URL` | unset | Any OSRM-compatible service. |

Without these, vendor distances are **straight-line** and are labelled as such
everywhere. They are never presented as travel distance. Do not remove that
labelling if you leave routing unconfigured.

## Frontend

Only `NEXT_PUBLIC_*` reaches the browser, and these are **inlined at build
time** — rebuild after changing them.

| Variable | Notes |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Project URL. |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public key only. |
| `NEXT_PUBLIC_API_BASE_URL` | Where the backend is reachable from the browser. |

There is deliberately no `NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY` and no
`NEXT_PUBLIC_` database URL. Adding either would ship a full-privilege
credential to every visitor. A test scans both the source and the built bundle
for these values.
