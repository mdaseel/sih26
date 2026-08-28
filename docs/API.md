# API

Base URL `http://localhost:8000`. Interactive docs at `/docs` while the backend
is running.

## Authentication

Every route except `/health` needs a Supabase JWT:

```
Authorization: Bearer <access_token>
```

The browser obtains it from Supabase Auth with the anon key. The backend
validates it, then re-reads the caller's role from `profiles` on every request —
a role claim in the token is never trusted on its own.

**Role column below** means the role the *server* requires. A citizen calling a
DISCOM route gets 403 regardless of what the UI shows.

## Rate limits

| Scope | Limit |
|---|---|
| Simulation-backed routes (`/api/assess`, `/api/twin`, `…/assess`, what-if, hosting capacity) | 30 / minute |
| Other authenticated routes | 240 / minute |
| Unauthenticated | 60 / minute |
| `/health` | never limited |

A 429 carries `Retry-After` and explains the limit. Counters are per-process —
see `docs/DEPLOYMENT.md`.

## Errors

| Status | Meaning |
|---|---|
| 401 | missing, malformed or invalid token |
| 403 | authenticated but not permitted |
| 404 | not found, or a malformed identifier |
| 409 | conflicts with current state (already decided, already answered) |
| 413 | upload too large |
| 422 | validation failed, or an engineering refusal (ineligible bus, no power-flow solution) |
| 429 | rate limited |
| 500 | unexpected; returns a `reference` to quote, never internals |

---

## Meta

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/health` | none | Liveness, subsystem state, rate-limit policy |
| GET | `/api/me` | any | Caller identity and role |

## Grid reference

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/api/grid/buses` | any | The 71 eligible connection points |
| GET | `/api/grid/summary` | none | Network summary, thresholds, provenance |
| GET | `/api/grid/topology` | none | Full graph (114 nodes) |
| GET | `/api/grid/topology/{bus_id}` | none | Source → bus path plus premises |
| GET | `/api/grid/hosting-capacity` | any | Precomputed capacity for every bus |
| GET | `/api/grid/hosting-capacity/{bus_id}` | any | Capacity for one bus, computed on demand |

## Assessment

| Method | Path | Role | Purpose |
|---|---|---|---|
| POST | `/api/assess` | any | Full pipeline, nothing persisted |
| POST | `/api/twin` | any | Assessment plus per-element before/after |
| POST | `/api/applications` | any | Create an application |
| GET | `/api/applications` | any | The caller's applications (RLS-scoped) |
| GET | `/api/applications/{id}` | owner / DISCOM | One application |
| POST | `/api/applications/{id}/assess` | owner / DISCOM | Run and **persist** an assessment |
| GET | `/api/applications/{id}/assessment` | owner / DISCOM | Read the stored result — does not re-simulate |
| GET | `/api/simulations/{id}` | owner / DISCOM | One stored simulation |

```bash
curl -X POST http://localhost:8000/api/assess \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"pv_bus":"734","existing_pv_kw":0,"new_pv_kw":66}'
```

```jsonc
{
  "ml": { "prediction": "CONSTRAINED", "safe_probability": 0.02, "…": "…" },
  "engineering": {
    "engineering_risk": "CONSTRAINED",
    "constraint_type": "voltage_rise",
    "constraint_reason": "Voltage rise at PV bus 734 0.0575 pu exceeds 0.05",
    "thresholds_snapshot": { "…": "…" }
  },
  "metrics": {
    "base_voltage_pu": 0.9059, "pv_voltage_pu": 0.9634, "voltage_rise_pu": 0.05751,
    "max_transformer_loading_pct": 92.56, "reverse_power_flow": true, "…": "…"
  },
  "ml_agrees_with_engineering": true,
  "authority": "power_flow"
}
```

`authority` is always `power_flow`. When `ml_agrees_with_engineering` is false,
the engineering verdict stands and the disagreement is shown to the DISCOM.

## Map

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/api/map` | any | Assets and application pins (RLS decides which pins) |

Carries `anchor_note` (what geometry is real) and `liveness` (not SCADA). Do not
strip either from a UI.

## DISCOM

All require **DISCOM** or **ADMIN**.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/discom/summary` | Dashboard metrics |
| GET | `/api/discom/applications` | Every application with its verdict |
| GET | `/api/discom/applications/{id}` | Review packet |
| POST | `/api/discom/applications/{id}/decision` | `APPROVED` / `ENGINEERING_REVIEW` / `REJECTED` |
| GET | `/api/discom/transformers` | Measured loading per transformer |
| GET | `/api/discom/feeders` | Per-section summary |
| GET | `/api/discom/hosting-capacity/feeders` | Section capacity, simultaneous injection |
| POST | `/api/discom/what-if` | Capacity sweep, one power flow per point |
| GET | `/api/discom/vendors` | Vendor queue, all statuses |
| POST | `/api/discom/vendors/{id}/review` | Approve, reject, suspend |
| GET | `/api/discom/installations` | All installations |
| POST | `/api/discom/installations/{id}/verify` | **The only route that sets VERIFIED** |

Approving a CONSTRAINED application is permitted and returns
`override_of_engineering_objection: true`; the objection is copied into the
audit log.

## Vendors — customer facing

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/api/vendors` | any | **APPROVED and active only** |
| GET | `/api/applications/{id}/vendors` | owner | Nearest first, where a distance exists |
| POST | `/api/vendors/register` | any | Always created `PENDING` |
| GET | `/api/vendors/me` | owner | Own vendor record |
| GET | `/api/routing/status` | any | What the distances actually mean |

Distances carry `is_route`. When false the figure is straight-line and must not
be described as travel distance or drive time.

## Vendor portal

Requires a vendor profile owned by the caller.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/vendor/summary` | Dashboard |
| GET | `/api/vendor/leads` | Requests, with the application behind each |
| POST | `/api/vendor/leads/{id}/respond` | Accept or decline; accepting opens an installation |
| GET/PATCH | `/api/vendor/appointments[/{id}]` | Manage site visits |
| GET | `/api/vendor/installations` | Own installations |
| POST | `/api/vendor/installations/{id}/status` | Advance — **`VERIFIED` returns 403** |
| GET | `/api/vendor/projects` | Engaged applications |
| GET/PATCH | `/api/vendor/profile` | Business profile; status and rating are not writable |
| POST | `/api/vendor/documents` | Attach by reference |
| POST | `/api/vendor/documents/upload` | Upload a file (multipart) |
| GET | `/api/vendor/documents/{id}/url` | 5-minute signed URL |
| GET | `/api/storage/policy` | Upload rules |

Uploads: PDF, PNG, JPEG, ≤ 5 MB. Type is decided by **magic bytes**, not the
declared `Content-Type`. The object key is server-generated.

## Scheme

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/api/scheme` | any | PM Surya Ghar information, entirely from configuration |
| GET | `/api/scheme/estimate?capacity_kw=` | any | Indicative CFA |
| GET | `/api/scheme/estimate/application/{id}` | owner | Estimate for a request |

Every response carries `indicative: true`, the disclaimer, and
`configuration_verified`. **While that is false the rates are unverified
placeholders** and the UI says so.
