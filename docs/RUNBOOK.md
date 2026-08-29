# Runbook — running and testing SolarGrid AI

Everything below was run on this machine. Paths use the Windows venv
(`.venv/Scripts/python.exe`); on Linux or macOS use `.venv/bin/python`.

---
## C:\sih26\suryaghar\.claude\worktrees\project-code-analysis-109c04
## 1. Start everything

Two processes. There is **no separate ML service** — the model is loaded into
the backend at startup, so starting the backend starts the ML layer, the power
flow and the API together.


.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --port 8000
```

**Frontend** (port 3000), in a second terminal:

```bash
cd frontend && npm run dev
```C:\sih26\suryaghar\.claude\worktrees\project-code-analysis-109c04

Use `npm run dev` while testing — `npm start` serves a **pre-built** bundle and
will keep showing old code until you re-run `npm run build`.

Check both are alive:

```bash
curl http://127.0.0.1:8000/health
```

Then open <http://localhost:3000>.

### Stopping and restarting on Windows

`pkill` does **not** work here. It silently does nothing, and you end up testing
a server that is still running the old code. Kill by port:

```bash
netstat -ano | grep ":8000" | grep LISTENING | awk '{print $NF}' | sort -u | while read p; do taskkill //PID $p //F; done
```

Change `8000` to `3000` for the frontend.

---

## 2. Prepare the demo

One command sets up all three portals with real, assessed data:

```bash
.venv/Scripts/python.exe backend/scripts/setup_demo_accounts.py
```

It creates the three accounts, grants their roles, submits two applications
(genuinely assessed by the power flow), registers and approves a vendor, and
books a site visit so the vendor has a lead.

```bash
.venv/Scripts/python.exe backend/scripts/setup_demo_accounts.py --status
```

```bash
.venv/Scripts/python.exe backend/scripts/setup_demo_accounts.py --remove
```

Re-running the setup resets everything to the same clean state, so it is safe to
run before each demo.

---

## 3. Demo accounts

| Portal | Sign in at | Email | Password |
|---|---|---|---|
| Citizen | `/login` | `demo.citizen@solargrid.test` | `DemoCitizen!2026` |
| DISCOM | `/login` | `demo.discom@solargrid.test` | `DemoDiscom!2026` |
| Vendor | **`/vendor/login`** | `demo.vendor@solargrid.test` | `DemoVendor!2026` |

**Sign out between portals.** The session lives in browser storage, so one
account at a time. Signing in as the citizen and visiting `/discom/dashboard`
shows *"DISCOM access required"* — that is the access control working, not a
bug. Use a private window to have two portals open at once.

---

## 4. Walkthrough for each portal

### Citizen

1. **`/citizen/dashboard`** — two applications: one **SAFE** (bus 732, 5 kW) and
   one **CONSTRAINED** (bus 734, 66 kW).
2. **`/citizen/applications/new`** — fill in a name, pick a connection point,
   set a capacity, then press **"Check the grid"**. That runs a real power flow
   and shows the result *before* you submit anything.
   - Try **bus 734 with 5 kW** → SAFE, then **66 kW** → CONSTRAINED.
3. **Open an application** — the 2D twin appears above the metrics. Toggle
   **Before / After** and watch bus 734 turn red while upstream buses stay
   green, and the flow arrows reverse.
4. **`/citizen/twin`** — pick any bus and use the 5 / 15 / 30 / 66 / 100 / 250 kW
   presets. Each is a fresh simulation.
5. **`/citizen/map`** — six layers. Switch to **Hosting capacity** to see which
   connection points are tight. Click a bus for its detail; click a large ringed
   pin for an application. **Streets on/off** toggles the basemap.
6. **`/citizen/vendors`** — four approved installers. Pick an application in the
   dropdown to sort by distance.
7. **`/citizen/scheme`** — PM Surya Ghar, eligibility, process, and the CFA
   calculator.

### DISCOM

1. **`/discom/dashboard`** — totals, pending review, and the risk breakdown.
2. **`/discom/applications`** — filter by risk. Open the **CONSTRAINED** one:
   applicant details, the 2D twin, the ML probabilities, the power-flow verdict,
   the electrical metrics, then the decision controls.
   - The approve button reads **"Approve despite objection"** and warns you.
     Approving anyway is allowed and recorded in the audit log as an override.
3. **`/discom/what-if`** — sweep 10/25/50/100/250/500 kW at a bus. Each row is a
   real power flow. Click **View twin** on any row.
4. **`/discom/hosting-capacity`** — per-section limits (measured with all
   connections energised together) and per-bus limits.
5. **`/discom/transformers`** — ordered by measured base loading; T7 sits at
   92.8%.
6. **`/discom/vendors`** — approve, suspend or reject. Suspend one, then check
   the citizen's installer list: it disappears.
7. **`/discom/installations`** — the only place an installation can be marked
   verified.

### Vendor

1. **`/vendor/login`** — not `/login`.
2. **`/vendor/leads`** — one lead waiting. **Accept** it; an installation opens.
3. **`/vendor/installations`** — advance through SITE_VISIT → SCHEDULED →
   IN_PROGRESS → COMPLETED → VERIFICATION_PENDING.
   - **VERIFIED has no button.** It shows as a locked chip (🔒) because only a
     DISCOM can set it. Try it via the API and you get a 403.
4. Sign back in as the DISCOM and verify it at `/discom/installations` to close
   the loop.

---

## 5. Granting roles

New signups are **always** CITIZEN. A user cannot change their own role — the
`role` column is not writable by them, by design. Elevating someone is an
administrative action.

**Option A — SQL in the Supabase dashboard** (SQL Editor):

```sql
update public.profiles
set role = 'DISCOM'
where id = (select id from auth.users where email = 'someone@example.com');
```

Valid roles: `CITIZEN`, `DISCOM`, `VENDOR`, `ADMIN`. `DISCOM` and `ADMIN` both
pass the DISCOM checks.

**Option B — from Python**, using the service role:

```bash
.venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'backend'); from app.db.service import db; from app.models.enums import UserRole; from app.core.supabase_client import get_service_client; u=[x for x in get_service_client().auth.admin.list_users() if x.email=='someone@example.com'][0]; print(db.set_role(u.id, UserRole.DISCOM))"
```

**Creating a confirmed account without the email step:**

```bash
.venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'backend'); from app.core.supabase_client import get_service_client; print(get_service_client().auth.admin.create_user({'email':'you@example.com','password':'Str0ng!Password','email_confirm':True}).user.id)"
```

Becoming a vendor is different: register a **business** at `/vendor/register`,
then a DISCOM approves it at `/discom/vendors`. Until then the business is
invisible to customers.

---

## 6. Things worth knowing before you test

**Email confirmation is on.** Registering through `/register` sends a
confirmation email and you cannot sign in until it is clicked. That is why the
demo accounts are created with `email_confirm: True`. To make live signup
frictionless for a demo, turn it off in Supabase → Authentication → Providers →
Email.

**Rate limits.** Simulation endpoints allow **30 requests per minute**. Clicking
"Check the grid" repeatedly, or reloading the what-if page in a loop, will
return **429** with a `Retry-After`. Wait a minute; nothing is broken. Other
endpoints allow 240/min.

**The frontend caches its build.** After changing frontend code, `npm run dev`
picks it up automatically; `npm start` does not until you `npm run build`. If a
change "isn't showing", this is usually why. Hard-refresh the browser too.

**Assessments are stored, not recomputed.** Opening an application reads the
saved result. Use **"Re-run assessment"** to run a fresh power flow, which
records a new row.

**Approving a CONSTRAINED application is allowed.** The DISCOM has that
authority. It is recorded as an override with the engineering objection copied
into the audit log — that is deliberate, not a loophole.

**What the numbers mean.**
- Voltages, loadings, losses, reverse flow: real, computed per request.
- Hosting capacity: real, found by bisection on the power flow.
- Map coordinates: **synthetic**. Distances between assets are true; the
  location on Earth is not. The map says so.
- Vendor distances: **straight-line**, not driving distance, until a routing
  provider is configured. Labelled on every row.
- CFA subsidy figures: **unverified placeholders** until you check them against
  the official portal. Shown as a red warning.

**Good buses to demonstrate with:**

| Bus | Load | What it shows |
|---|---|---|
| 732 | 25.4 kW | SAFE at 5 kW; a clean happy path |
| 734 | 15.85 kW | CONSTRAINED at 66 kW by voltage rise; the historic false-SAFE case |
| 6231 | 0 kW | CONSTRAINED at 53 kW; the zero-load case that fooled the old model |
| 716 | 15.85 kW | CONSTRAINED at 44 kW by **transformer** loading, not voltage |
| 621 | 0 kW | CAUTION at 100 kW, with reverse power flow |

**If something looks wrong**, check in this order:

```bash
curl http://127.0.0.1:8000/health
```

```bash
.venv/Scripts/python.exe backend/scripts/verify_phase1.py
```

The first shows whether artifacts and Supabase are wired up; the second proves
the model still reproduces its documented predictions.

---

## 7. Re-running the full pipeline

Only needed if the feeder model or thresholds change:

```bash
.venv/Scripts/python.exe backend/seed/seed_grid_assets.py
```

```bash
.venv/Scripts/python.exe backend/scripts/precompute_grid_map.py
```

The precompute takes about 90 seconds — 1065 power flows for per-bus hosting
capacity plus 7 feeder sections. **The ML model is never retrained**; it is
loaded as-is from `suryagrid_model_v2.pkl`.

---

## 8. The scripted demo

If you want the whole journey narrated in a terminal rather than clicked:

```bash
.venv/Scripts/python.exe backend/scripts/demo_end_to_end.py
```

Twelve steps from registration to CFA, printing every value it computes.
`--reset` removes what it created. Note it clears the setup script's data too,
so run `setup_demo_accounts.py` again afterwards.
