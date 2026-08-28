"""Phase 1 acceptance check.

Verifies, in order:
    A. Dependency pins (the model will not predict under the wrong sklearn).
    B. All required engineering artifacts are reachable via app.core.paths.
    C. The existing model loads and reproduces its documented predictions.
    D. pandapower loads the production network and reproduces documented metrics.
    E. Environment configuration (reports what is set; never prints key material).
    F. Supabase round-trip: schema reachable, insert + read back + clean up.
       Skipped with a clear message when credentials are absent.

Usage:
    python backend/scripts/verify_phase1.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from app.core import paths  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


# ============================================================
print("\nA. Dependency pins")
# ============================================================
EXPECTED = {
    "numpy": "1.26.4",
    "scipy": "1.16.3",
    "pandas": "2.3.3",
    "sklearn": "1.3.2",
    "pandapower": "3.4.0",
}
for mod_name, expected in EXPECTED.items():
    try:
        mod = __import__(mod_name)
        actual = mod.__version__
        check(f"{mod_name} == {expected}", actual == expected, f"found {actual}")
    except ImportError as exc:
        check(f"{mod_name} == {expected}", False, str(exc))

# ============================================================
print("\nB. Engineering artifacts")
# ============================================================
missing = paths.missing_artifacts()
check("all required artifacts present", not missing, f"artifacts dir: {paths.ARTIFACTS_DIR}")
for key, path in missing.items():
    check(f"  missing: {key}", False, str(path))

# ============================================================
print("\nC. Existing ML model")
# ============================================================
import json  # noqa: E402
import pickle  # noqa: E402

import pandas as pd  # noqa: E402

try:
    bundle = pickle.load(open(paths.MODEL_V2, "rb"))
    model = bundle["model"]
    feats = bundle["input_features"]
    check("model unpickles", True, f"{len(feats)} features")
    check("feature count is 18", len(feats) == 18)
    check(
        "classes are SAFE/CAUTION/CONSTRAINED",
        sorted(model.classes_) == ["CAUTION", "CONSTRAINED", "SAFE"],
        str(list(model.classes_)),
    )

    declared = json.loads(paths.MODEL_FEATURES.read_text())["input_features_enriched"]
    check("enriched_features.json matches pickle", declared == feats)

    # The two historically false-SAFE cases. phase4_5_validation_report.md
    # documents 734 -> 0.833 and 6231 -> 0.74. Regression here means the
    # environment has drifted and every downstream number is suspect.
    df = pd.read_csv(paths.DATASET_CURRENT, dtype={"pv_bus": str})
    for bus, new_kw, documented in [("734", 66, 0.833), ("6231", 53, 0.74)]:
        hit = df[
            (df.pv_bus == bus) & (df.new_pv_kw == new_kw) & (df.existing_pv_kw == 0)
        ].iloc[[0]]
        pred = model.predict(hit[feats])[0]
        probs = dict(zip(model.classes_, model.predict_proba(hit[feats])[0]))
        ok = pred == "CONSTRAINED" and abs(probs["CONSTRAINED"] - documented) < 0.005
        check(
            f"bus {bus} @{new_kw}kW predicts CONSTRAINED",
            ok,
            f"P(CONSTRAINED)={probs['CONSTRAINED']:.4f}, documented {documented}",
        )
except Exception as exc:  # noqa: BLE001
    check("model checks", False, repr(exc))

# ============================================================
print("\nD. Power-flow engine")
# ============================================================
try:
    import copy
    import time

    import pandapower as pp

    net0 = pp.from_json(str(paths.FEEDER_NETWORK))
    check(
        "production network loads",
        True,
        f"{len(net0.bus)} buses, {len(net0.line)} lines, {len(net0.trafo)} trafos",
    )

    def run(bus: str, kw: float):
        n = copy.deepcopy(net0)
        idx = int(n.bus.index[n.bus.name == str(bus)][0])
        if kw > 0:
            pp.create_sgen(n, bus=idx, p_mw=kw / 1000.0, q_mvar=0, name="PV")
        pp.runpp(
            n,
            algorithm="nr",
            max_iteration=500,
            numba=False,
            tolerance_mva=1e-3,
            enforce_q_limits=False,
        )
        return n, idx

    t0 = time.perf_counter()
    nb, i0 = run("734", 0)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    check("base power flow converges", bool(nb.converged), f"{elapsed_ms:.0f} ms")
    check(
        "base source P == 4.178 MW",
        abs(float(nb.res_ext_grid.p_mw.iloc[0]) - 4.178) < 0.002,
        f"{float(nb.res_ext_grid.p_mw.iloc[0]):.4f} MW",
    )
    check(
        "base min voltage == 0.9059 pu",
        abs(float(nb.res_bus.vm_pu.min()) - 0.9059) < 0.0002,
        f"{float(nb.res_bus.vm_pu.min()):.4f} pu",
    )

    base_v = float(nb.res_bus.vm_pu.iloc[i0])
    npv, i1 = run("734", 66)
    delta = float(npv.res_bus.vm_pu.iloc[i1]) - base_v
    check(
        "bus 734 @66kW voltage rise == 0.05751 pu",
        abs(delta - 0.05751) < 1e-4,
        f"{delta:.5f} pu (hard limit 0.05 -> CONSTRAINED)",
    )
except Exception as exc:  # noqa: BLE001
    check("power-flow checks", False, repr(exc))

# ============================================================
print("\nE. Environment configuration")
# ============================================================
try:
    from app.core.config import get_settings

    s = get_settings()
    desc = s.describe()
    check("settings load", True, str(desc))

    # The property that actually matters: no secret may appear in the config
    # summary, which is logged at startup and is the surface most likely to
    # leak into a terminal, a log aggregator, or a screenshot.
    secrets = [v for v in (s.supabase_service_role_key, s.supabase_anon_key, s.database_url) if v]
    blob = str(desc)
    check(
        "no key material or password in describe()",
        all(secret not in blob for secret in secrets),
        f"{len(secrets)} secret(s) checked",
    )

    example = paths.REPO_ROOT / ".env.example"
    if example.exists():
        text = example.read_text(encoding="utf-8")
        exposed = [
            line.split("=")[0]
            for line in text.splitlines()
            if line.startswith("NEXT_PUBLIC_")
            and ("SERVICE_ROLE" in line or line.split("=")[0].endswith("DB_URL"))
        ]
        check("no NEXT_PUBLIC_ service-role or DB variable in template", not exposed, str(exposed))
    else:
        check(".env.example template present", False, "template missing — teammates cannot set up")
except Exception as exc:  # noqa: BLE001
    check("settings load", False, repr(exc))

# ============================================================
print("\nF. Supabase round-trip")
# ============================================================
TABLES = [
    "profiles",
    "grid_assets",
    "solar_applications",
    "application_status_history",
    "simulation_results",
    "risk_assessments",
    "vendors",
    "vendor_documents",
    "appointments",
    "installations",
    "scheme_config",
    "audit_logs",
]

try:
    from app.core.config import get_settings

    s = get_settings()
    if not s.service_role_configured:
        print("  [SKIP] Supabase credentials not set in .env — cannot verify live database.")
        print("         Fill SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY, then re-run.")
    else:
        from app.db.service import db

        client = db.as_service()
        for table in TABLES:
            try:
                client.table(table).select("*").limit(1).execute()
                check(f"table {table} reachable", True)
            except Exception as exc:  # noqa: BLE001
                check(f"table {table} reachable", False, str(exc)[:120])

        # Insert -> read back -> delete, on a table with no client write policy.
        probe = {
            "scheme_code": "__VERIFY__",
            "config_key": "phase1_roundtrip",
            "config_value": {"ok": True},
            "description": "temporary row written by verify_phase1.py",
        }
        ins = client.table("scheme_config").insert(probe).execute()
        row_id = ins.data[0]["id"]
        got = client.table("scheme_config").select("*").eq("id", row_id).execute()
        check("insert + read back", bool(got.data) and got.data[0]["config_key"] == "phase1_roundtrip")
        client.table("scheme_config").delete().eq("id", row_id).execute()
        gone = client.table("scheme_config").select("*").eq("id", row_id).execute()
        check("cleanup", not gone.data)
except Exception as exc:  # noqa: BLE001
    check("Supabase round-trip", False, repr(exc)[:200])

# ============================================================
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 1 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
