# SolarGrid AI

Rooftop-solar hosting-capacity screening for a distribution utility.

A citizen asks to connect a rooftop system. A machine-learning model pre-screens
the request in milliseconds; a deterministic power flow then verifies it against
the actual feeder. **The power flow decides** — the model is a fast opinion, not
the answer.

```
citizen request → ML pre-screen → power-flow verification → SAFE / CAUTION / CONSTRAINED
                                          ↓
                    2D digital twin · GIS map · DISCOM review · installer · CFA
```

---

## What is real, and what is not

This matters more than any feature list, so it comes first.

| | Status |
|---|---|
| Feeder model, topology, line lengths, impedances | **Real** — IEEE Comprehensive Test Feeder, validated against the published reference |
| Power-flow results, voltages, loadings, losses | **Real** — computed by pandapower on every request |
| Hosting capacity | **Real** — found by bisection on the power flow, never estimated |
| The trained model and its dataset | **Real** — 1692 simulated scenarios, reused unchanged |
| Geographic coordinates | **Synthetic** — the feeder ships none; distances between assets are true, absolute placement is illustrative |
| PM Surya Ghar subsidy rates | **Unverified placeholders** — flagged in the API and on screen until checked against the official portal |
| Vendors in the demo seed | **Fictional** |

The feeder is a research network, not a DISCOM's. It is one feeder with one
topology and one load profile. Nothing here should be presented as a live SCADA
feed, as a real utility's data, or as the government's PM Surya Ghar portal.

---

## Quick start

Prerequisites: **Python 3.12**, **Node 20+**, and a Supabase project.

```bash
cp .env.example .env          # then fill in the Supabase values
```

```bash
python -m venv .venv && .venv/Scripts/python.exe -m pip install -r requirements.txt
```

Apply the schema and load the grid data:

```bash
.venv/Scripts/python.exe backend/scripts/apply_migrations.py
```

```bash
.venv/Scripts/python.exe backend/seed/seed_grid_assets.py
```

```bash
.venv/Scripts/python.exe backend/scripts/precompute_grid_map.py
```

```bash
.venv/Scripts/python.exe backend/seed/seed_scheme_config.py
```

Run it:

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --port 8000
```

```bash
cd frontend && npm install && npm run dev
```

Or with Docker:

```bash
docker compose up --build
```

---

## Verify the install

```bash
.venv/Scripts/python.exe backend/scripts/verify_phase1.py
```

That must report **PASS**. It checks the dependency pins, that the model loads,
and that it reproduces its documented predictions. If it fails, stop — the
pins matter (see below).

The full test suite:

```bash
.venv/Scripts/python.exe -m pytest
```

```bash
cd frontend && npm test
```

See [`docs/TESTING.md`](docs/TESTING.md) for what each suite covers.

---

## The dependency pins are not negotiable

`suryagrid_model_v2.pkl` was serialized by **scikit-learn 1.3.2**. Under
scikit-learn ≥ 1.4 it unpickles successfully and then fails at predict time:

```
AttributeError: 'DecisionTreeClassifier' object has no attribute 'monotonic_cst'
```

scikit-learn 1.3.2 requires numpy < 2, which caps scipy, which caps pandapower.
**pandapower 3.4.0** is the newest release that still resolves. Changing any one
of these breaks the chain. `requirements.txt` explains it at the point of use.

---

## Documentation

| Document | Contents |
|---|---|
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | **Start here** — running it, demo accounts, granting roles, gotchas |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the layers fit together and why |
| [`docs/API.md`](docs/API.md) | Every endpoint, with roles and examples |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Deploying, and what to do before going live |
| [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md) | Every environment variable |
| [`docs/TESTING.md`](docs/TESTING.md) | Test suites and what they prove |
| [`supabase/README.md`](supabase/README.md) | Schema, RLS, and the security model |

---

## The original research

The engineering and ML work predates this application and is **reused
unchanged**. Those files were not modified:

- `build_feeder.py` → `feeder_network.json` — the validated feeder model
- `dataset_generation_phase2.py` — 1500 simulated scenarios and their labels
- `train_ml_v2.py` → `suryagrid_model_v2.pkl` — the 18-feature model
- `scenario_config.json` — every threshold, with its justification
- The validation reports in the repository root

The application loads these; it never retrains or regenerates them. A test
replays rows from the original dataset through the running services and requires
the recomputed label to match the stored one, so drift is caught rather than
discovered.

Known limitations of the underlying research — a random rather than
bus-disjoint split, model selection on the test set, an untested line-overload
mode — are recorded in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Demo

```bash
.venv/Scripts/python.exe backend/scripts/demo_end_to_end.py
```

Drives the whole journey through the real API and prints every value it
computes: registration, assessment, twin, map, DISCOM approval, installer,
installation, DISCOM verification, indicative CFA. `--reset` removes the data.

---

## Licence and provenance

The IEEE Comprehensive Test Feeder data is published by the IEEE PES
Distribution Systems Analysis Subcommittee. This application is a prototype
built for demonstration.
