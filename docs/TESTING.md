# Testing

Two kinds of check, deliberately kept separate.

## pytest — behaviour that must not drift

```bash
.venv/Scripts/python.exe -m pytest
```

`backend/tests/test_scenarios.py` covers the twelve required scenarios:

| # | Scenario | Case |
|---|---|---|
| 1 | SAFE | bus 620 @ 5 kW |
| 2 | CAUTION | bus 621 @ 100 kW |
| 3 | CONSTRAINED | bus 734 @ 66 kW |
| 4 | High solar / low load | bus 6231 (zero load) @ 53 kW |
| 5 | Existing + new solar | bus 734, 10 kW existing + 56 kW new |
| 6 | Reverse power flow | bus 734 @ 66 kW |
| 7 | Voltage rise | bus 734 @ 66 kW |
| 8 | Transformer loading | bus 716 @ 44 kW |
| 9 | Invalid bus | unknown vs ineligible, distinguished |
| 10 | Invalid capacity | zero, negative, absurd |
| 11 | Unauthorized role | citizen → DISCOM route |
| 12 | Unapproved vendor | pending vendor is not discoverable |

Plus the regression cases. **Bus 734 @ 66 kW and bus 6231 @ 53 kW were the
original model's two false-SAFE predictions.** Both must stay CONSTRAINED. If
those tests fail, do not adjust the expectation — find out what changed in the
model, the thresholds, or the feeder.

`test_integration.py` covers the ML contract, the power-flow layer, the API and
RLS. The most important test there is the **label replay**: rows from the
original dataset are pushed back through the running services, and the
recomputed label must equal the stored one.

## verify_phase*.py — acceptance checks

```bash
.venv/Scripts/python.exe backend/scripts/verify_phase12.py
```

One script per build phase, each asserting what that phase claimed. They run
against live Supabase with temporary users and clean up after themselves. They
are noisier than pytest and better at showing *why* something holds — the
security ones print each attack and its refusal.

| Script | Covers |
|---|---|
| `verify_phase1` | environment pins, artifacts, model fidelity, database round-trip |
| `verify_phase2` / `_live` | services, label replay, persistence, nine attacks |
| `verify_phase4` | topology, per-element deltas, flow direction |
| `verify_phase5` | coordinates, hosting capacity, map API |
| `verify_phase6` | DISCOM authorization and approval override auditing |
| `verify_phase7` | multi-bus injection, feeder capacity |
| `verify_phase8` | vendor visibility, routing honesty |
| `verify_phase9` | the DISCOM-verification boundary, attacked four ways |
| `verify_phase10` | no hardcoded scheme values |
| `verify_phase11` | the end-to-end demo is genuinely computed |
| `verify_phase12` | secrets, authentication, validation, uploads, rate limits |

## Frontend

```bash
cd frontend && npm test        # vitest
cd frontend && npm run typecheck
cd frontend && npm run lint
```

`lib/risk.test.ts` covers the threshold comparison logic — including the
asymmetry the backend uses (`>` for hard limits, `>=` for caution bands) and
that a missing threshold falls back to the documented value rather than
comparing false and painting everything green.

## Before a release

```bash
.venv/Scripts/python.exe -m pytest && cd frontend && npm test && npm run build
```
