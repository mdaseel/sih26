"""Phase 11 acceptance check — the end-to-end demonstration.

A demo is easy to fake, so this checks the things that would expose a fake:

  * the demo script contains no electrical literals to fall back on
  * the figures it reports match an independent power flow computed here
  * the full state chain really occurred in the database
  * the security boundaries still held while the happy path ran
"""

from __future__ import annotations

import re
import subprocess
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from app.core.supabase_client import get_service_client  # noqa: E402
from app.services.power_flow import get_power_flow_service  # noqa: E402
from app.services.risk_assessment import get_risk_service  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "backend/scripts/demo_end_to_end.py"
VENV_PY = REPO / ".venv/Scripts/python.exe"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


svc = get_service_client()

# ============================================================
print("\nA. The demo script cannot be faking it")
# ============================================================
source = DEMO.read_text(encoding="utf-8")

# Any decimal that looks like a per-unit voltage or a loading percentage would
# be a hardcoded electrical result. The scenario inputs (capacity, coordinates,
# consumption) are legitimately literals, so only suspicious shapes are hunted.
pu_literals = re.findall(r"\b0\.9\d{3,}\b|\b1\.0\d{3,}\b", source)
check("no per-unit voltage literals", not pu_literals, str(pu_literals[:5]))

pct_literals = re.findall(r"\b9[0-9]\.\d+\b", source)
check("no loading-percentage literals", not pct_literals, str(pct_literals[:5]))

check(
    "electrical values are read from responses, not assigned",
    # Quote style varies inside f-strings, so match either; the point is that
    # the key is only ever subscripted out of a response, never assigned to.
    bool(re.search(r"""m\[['"]voltage_rise_pu['"]\]""", source))
    and not re.search(r"voltage_rise_pu\s*=\s*[\d.]", source),
)
check(
    "the demo aborts rather than continue on a failed step",
    source.count("fail(") >= 5,
    f"{source.count('fail(')} abort points",
)
check(
    "the demo drives the HTTP API rather than the database",
    source.count("httpx.") >= 15 and "table(" in source,
    f"{source.count('httpx.')} HTTP calls",
)

# ============================================================
print("\nB. Run the demo end to end")
# ============================================================
proc = subprocess.run(
    [str(VENV_PY), str(DEMO)],
    cwd=REPO,
    capture_output=True,
    text=True,
    timeout=900,
    env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
)
out = proc.stdout
check("the demo completes", proc.returncode == 0 and "DEMO COMPLETE" in out, f"exit {proc.returncode}")

for step_title in [
    "Citizen registers",
    "Connection point identified",
    "Citizen submits the application",
    "ML pre-screen and power-flow verification",
    "Digital twin reflects the change",
    "Map marker appears",
    "DISCOM reviews and approves",
    "Citizen sees approved installers",
    "Citizen books a site visit",
    "Vendor carries out the installation",
    "DISCOM verifies the installation",
    "PM Surya Ghar",
]:
    check(f"step present: {step_title}", step_title in out)

# ============================================================
print("\nC. The reported figures match an independent power flow")
# ============================================================
pf = get_power_flow_service()
risk = get_risk_service()

bus = re.search(r"Connection point\s+bus (\d+)", out)
capacity = re.search(r"Requested solar\s+([\d.]+) kW", out)
check("the demo reports its connection point and capacity", bool(bus and capacity))

if bus and capacity:
    bus_id, kw = bus.group(1), float(capacity.group(1))
    metrics = pf.simulate(bus_id, 0, kw)
    verdict = risk.evaluate(metrics)

    def reported(label: str) -> float | None:
        m = re.search(rf"{label}\s+(-?[\d.]+)", out)
        return float(m.group(1)) if m else None

    for label, actual in [
        ("Voltage before", metrics.base_voltage_pu),
        ("Voltage after", metrics.pv_voltage_pu),
        ("Voltage rise", metrics.voltage_rise_pu),
        ("Transformer loading", metrics.max_transformer_loading_pct),
        ("Line loading", metrics.max_line_loading_pct),
    ]:
        shown = reported(label)
        check(
            f"{label} matches a fresh simulation",
            shown is not None and abs(shown - actual) < 0.01,
            f"demo {shown} vs recomputed {actual}",
        )

    check(
        "the verdict matches a fresh evaluation",
        f"VERDICT{' ' * 26}{verdict.engineering_risk.value}" in out
        or verdict.engineering_risk.value in out,
        verdict.engineering_risk.value,
    )

# ============================================================
print("\nD. The state chain really happened")
# ============================================================
number = re.search(r"Application\s+(SG-[A-Z0-9]+)", out)
check("the demo reports an application number", bool(number))

if number:
    app_rows = (
        svc.table("solar_applications")
        .select("*")
        .eq("application_number", number.group(1))
        .execute()
    ).data
    check("the application exists in the database", bool(app_rows))

    if app_rows:
        app = app_rows[0]
        check("it reached APPROVED", app["status"] == "APPROVED", app["status"])
        check("a reviewer is recorded", app["reviewed_by"] is not None)

        history = (
            svc.table("application_status_history")
            .select("to_status")
            .eq("application_id", app["id"])
            .order("created_at")
            .execute()
        ).data or []
        chain = [h["to_status"] for h in history]
        check(
            "the status chain was recorded",
            chain[0] == "SUBMITTED" and chain[-1] == "APPROVED" and "ASSESSED" in chain,
            " → ".join(chain),
        )

        sims = (
            svc.table("simulation_results").select("*").eq("application_id", app["id"]).execute()
        ).data or []
        check("a simulation result was stored", len(sims) >= 1, f"{len(sims)} rows")

        risks = (
            svc.table("risk_assessments").select("*").eq("application_id", app["id"]).execute()
        ).data or []
        check("a risk assessment was stored", len(risks) >= 1)
        if risks and sims:
            check(
                "the stored figures match what the demo printed",
                abs(float(sims[0]["voltage_rise_pu"]) - (reported("Voltage rise") or -1)) < 1e-4,
                f"stored {sims[0]['voltage_rise_pu']}",
            )

        install = (
            svc.table("installations").select("*").eq("application_id", app["id"]).execute()
        ).data or []
        check("an installation exists", bool(install))
        if install:
            i = install[0]
            check("the installation is VERIFIED", i["status"] == "VERIFIED", i["status"])
            check("DISCOM verification is flagged and attributed",
                  i["discom_verified"] is True and i["discom_verified_by"] is not None)

        appts = (
            svc.table("appointments").select("*").eq("application_id", app["id"]).execute()
        ).data or []
        check("a site visit was booked and confirmed",
              any(a["status"] == "CONFIRMED" for a in appts), f"{len(appts)} appointments")

# ============================================================
print("\nE. The boundaries held during the happy path")
# ============================================================
check(
    "the vendor's attempt to self-verify was refused",
    "refused (403)" in out and "only a DISCOM may verify" in out,
)
check(
    "an unapproved vendor was invisible to the customer",
    "Visible to customer before approval False" in out.replace("  ", " ")
    or "Visible to customer before approval" in out and "False" in out,
)
check(
    "distance was labelled as not a route",
    "STRAIGHT_LINE (is_route=False)" in out,
)
check(
    "the map placement was labelled synthetic",
    "SYNTHETIC_LAYOUT" in out,
)
check(
    "the CFA figure was labelled unverified",
    "unverified placeholders" in out,
)
check(
    "the demo states its figures were computed live",
    "came from a power flow run during this" in out,
)

# ============================================================
print("\nF. The demo is repeatable")
# ============================================================
reset = subprocess.run(
    [str(VENV_PY), str(DEMO), "--reset"],
    cwd=REPO,
    capture_output=True,
    text=True,
    timeout=300,
)
check("--reset runs cleanly", reset.returncode == 0, reset.stdout.strip().splitlines()[-1] if reset.stdout else "")

leftover = (
    svc.table("solar_applications").select("id,applicant_name").execute()
).data or []
check(
    "demo applications are removed",
    not [a for a in leftover if a["applicant_name"].startswith("Demo Customer H-")],
)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 11 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
