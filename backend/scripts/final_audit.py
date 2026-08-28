"""Final audit — mechanical checks over the whole codebase.

Written to find problems, not to confirm the absence of them. Each section
looks for a specific class of defect the build plan asks about: leaked
credentials, fabricated electrical values, threshold drift, dead code,
unused dependencies, broken API contracts, and inconsistent database state.

Usage:
    python backend/scripts/final_audit.py
"""

from __future__ import annotations

import ast
import json
import re
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
BACKEND = REPO / "backend"
FRONTEND = REPO / "frontend"
BASE = "http://127.0.0.1:8000"

findings: list[tuple[str, str, str]] = []  # (severity, area, message)
checks: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def finding(severity: str, area: str, message: str) -> None:
    findings.append((severity, area, message))
    print(f"  [{severity}] {area}: {message}")


def app_sources(*roots: Path) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".ts", ".tsx"} or not path.is_file():
                continue
            parts = set(path.parts)
            if "node_modules" in parts or ".next" in parts or ".venv" in parts:
                continue
            out.append(path)
    return out


BACKEND_APP = app_sources(BACKEND / "app")
FRONTEND_APP = app_sources(FRONTEND / "app", FRONTEND / "components", FRONTEND / "lib")
ALL_APP = BACKEND_APP + FRONTEND_APP

print("=" * 70)
print("  SolarGrid AI — final audit")
print(f"  {len(BACKEND_APP)} backend + {len(FRONTEND_APP)} frontend application files")
print("=" * 70)

# ============================================================
print("\n1. Hardcoded credentials")
# ============================================================
CREDENTIAL_PATTERNS = [
    (r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}", "a JWT"),
    (r"postgres(?:ql)?://[^\s\"']*:[^\s\"'@]+@", "a database URL with a password"),
    (r"(?i)(service_role_key|secret_key|api_key)\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']", "an inline key"),
    (r"(?i)password\s*[:=]\s*[\"'](?!.*\{)[^\"']{8,}[\"']", "an inline password"),
]
credential_hits: list[str] = []
for path in ALL_APP:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern, label in CREDENTIAL_PATTERNS:
        if re.search(pattern, text):
            credential_hits.append(f"{path.relative_to(REPO)} ({label})")
check("no credentials in application code", not credential_hits, str(credential_hits[:3]))

env_committed = (REPO / ".gitignore").read_text(encoding="utf-8")
check(".env is git-ignored", ".env" in env_committed and ".env.local" in env_committed)

# ============================================================
print("\n2. Hardcoded electrical results")
# ============================================================
# A per-unit voltage or a loading percentage written into UI or service code
# would be a fabricated engineering value.
PU_PATTERN = re.compile(r"\b0\.9[0-9]{3,}\b|\b1\.0[0-9]{3,}\b")
electrical_hits: list[str] = []
for path in ALL_APP:
    if "risk.ts" in path.name or "test" in path.name:
        continue  # documented threshold fallbacks and fixtures
    text = path.read_text(encoding="utf-8", errors="ignore")
    for match in PU_PATTERN.finditer(text):
        line_no = text[: match.start()].count("\n") + 1
        line = text.splitlines()[line_no - 1]
        if line.strip().startswith(("#", "*", "//")) or '"""' in line:
            continue  # prose in a docstring or comment
        electrical_hits.append(f"{path.relative_to(REPO)}:{line_no} {match.group()}")
check("no per-unit voltage literals in code", not electrical_hits, str(electrical_hits[:3]))

# ============================================================
print("\n3. Threshold consistency")
# ============================================================
config = json.loads((REPO / "scenario_config.json").read_text())["thresholds"]
config_values = {k: v["value"] for k, v in config.items() if isinstance(v, dict) and "value" in v}

from app.services.grid_assets import get_grid_asset_service  # noqa: E402

live = get_grid_asset_service().thresholds()
mismatched = [k for k, v in live.items() if k in config_values and config_values[k] != v]
check("live thresholds equal scenario_config.json", not mismatched, str(mismatched))

# The only place a threshold number may appear outside the config is the
# documented fallback table in risk.ts.
threshold_literals: list[str] = []
for path in ALL_APP:
    if path.name in {"risk.ts", "risk.test.ts"}:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for key, value in config_values.items():
        if isinstance(value, float) and value not in (0.0, 1.0):
            if re.search(rf"{key}\s*[:=]\s*{value}", text):
                threshold_literals.append(f"{path.relative_to(REPO)} redefines {key}")
check("no threshold is redefined in code", not threshold_literals, str(threshold_literals[:3]))

fallback_documented = "scenario_config.json" in (FRONTEND / "lib/risk.ts").read_text(encoding="utf-8")
check("the frontend fallback table cites its source", fallback_documented)

# ============================================================
print("\n4. API contract: frontend calls vs backend routes")
# ============================================================
try:
    spec = httpx.get(f"{BASE}/openapi.json", timeout=30).json()
    backend_paths = set(spec["paths"])

    api_client = (FRONTEND / "lib/api.ts").read_text(encoding="utf-8")
    # Collapse template-literal interpolations FIRST. Matching before this
    # truncates `/api/x/${id}/y` at the "$" and reports working routes as
    # missing — which is exactly what it did on the first run.
    resolved = re.sub(r"\$\{[^}]*\}", "{}", api_client)
    called = {
        c.rstrip("/") or "/"
        for c in re.findall(r"[\"'`](/api/[^\"'`\s?]*)", resolved)
    }

    backend_normalised = {re.sub(r"\{[^}]+\}", "{}", p) for p in backend_paths}

    def resolves(call: str) -> bool:
        # A trailing "{}" can come from an interpolated QUERY STRING rather than
        # a path parameter, e.g. `/api/vendors${district ? "?..." : ""}`.
        return call in backend_normalised or call.removesuffix("{}").rstrip("/") in backend_normalised

    missing = sorted(c for c in called if not resolves(c))
    called = {c.removesuffix("{}").rstrip("/") if c.removesuffix("{}").rstrip("/") in backend_normalised else c for c in called}
    check("every frontend call maps to a backend route", not missing, str(missing[:5]))

    unused = sorted(backend_normalised - called - {"/health", "/openapi.json", "/api/me"})
    if unused:
        finding(
            "INFO",
            "API surface",
            f"{len(unused)} routes are not called by the frontend client "
            f"(reachable directly; e.g. {unused[:3]})",
        )
except Exception as exc:  # noqa: BLE001
    check("API contract check", False, f"backend unreachable: {type(exc).__name__}")

# ============================================================
print("\n5. Dead code")
# ============================================================
imported: set[str] = set()
for path in BACKEND_APP + app_sources(BACKEND / "scripts", BACKEND / "seed", BACKEND / "tests"):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)

unreferenced: list[str] = []
for path in BACKEND_APP:
    if path.name == "__init__.py" or path.name == "main.py":
        continue
    module = ".".join(path.relative_to(BACKEND).with_suffix("").parts)
    if module not in imported:
        unreferenced.append(module)
check("no unreferenced backend modules", not unreferenced, str(unreferenced))

frontend_components = {p.stem for p in (FRONTEND / "components").glob("*.tsx")}
frontend_text = "\n".join(
    p.read_text(encoding="utf-8", errors="ignore") for p in FRONTEND_APP
)
unused_components = [c for c in frontend_components if frontend_text.count(c) <= 1]
check("no unused frontend components", not unused_components, str(unused_components))

# ============================================================
print("\n6. Dependencies")
# ============================================================
requirements = [
    re.split(r"[=<>\[]", line)[0].strip()
    for line in (REPO / "requirements.txt").read_text().splitlines()
    if line.strip() and not line.startswith("#")
]
backend_text = "\n".join(
    p.read_text(encoding="utf-8", errors="ignore")
    for p in BACKEND_APP + app_sources(BACKEND / "scripts", BACKEND / "seed", BACKEND / "tests")
)
IMPORT_NAME = {
    "scikit-learn": "sklearn",
    "python-dotenv": "dotenv",
    "pydantic-settings": "pydantic_settings",
    "python-multipart": "multipart",
    "uvicorn": "uvicorn",
    "psycopg": "psycopg",
}
unused_py = [
    pkg
    for pkg in requirements
    if not re.search(rf"\b{re.escape(IMPORT_NAME.get(pkg, pkg))}\b", backend_text)
]
# uvicorn and multipart are used by the server and by FastAPI's form parsing
# rather than imported directly.
# uvicorn runs the server and python-multipart is used by FastAPI's form
# parsing; neither is imported by name.
unused_py = [p for p in unused_py if p not in {"uvicorn", "python-multipart"}]
check("no unused Python dependency", not unused_py, str(unused_py))

package = json.loads((FRONTEND / "package.json").read_text())
unused_js = [
    dep
    for dep in package["dependencies"]
    if dep not in frontend_text and dep.split("/")[-1] not in frontend_text
]
unused_js = [d for d in unused_js if d not in {"react-dom", "next"}]
check("no unused JavaScript dependency", not unused_js, str(unused_js))

# ============================================================
print("\n7. Duplicated logic")
# ============================================================
# The threshold comparison used to be duplicated between the map and the twin.
twin = (FRONTEND / "components/TwinDiagram.tsx").read_text(encoding="utf-8")
grid_map = (FRONTEND / "components/GridMap.tsx").read_text(encoding="utf-8")
check(
    "the twin uses the shared risk module",
    "@/lib/risk" in twin,
    "threshold logic is not re-implemented",
)
if "@/lib/risk" not in grid_map:
    finding(
        "LOW",
        "duplication",
        "GridMap still has its own threshold comparison; it agrees with lib/risk.ts "
        "today but could drift",
    )

pf_solves = len(re.findall(r"pp\.runpp\(", (BACKEND / "app/services/power_flow.py").read_text()))
check(
    "the power flow is solved in one place",
    pf_solves <= 2,
    f"{pf_solves} runpp calls (single-bus and group paths)",
)

# ============================================================
print("\n8. Database state")
# ============================================================
try:
    from app.core.config import get_settings
    import psycopg

    with psycopg.connect(get_settings().database_url) as conn, conn.cursor() as cur:
        cur.execute(
            "select count(*) from information_schema.tables "
            "where table_schema='public' and table_type='BASE TABLE'"
        )
        table_count = cur.fetchone()[0]

        cur.execute(
            "select c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace "
            "where n.nspname='public' and c.relkind='r' and not c.relrowsecurity"
        )
        no_rls = [r[0] for r in cur.fetchall()]
        check("RLS is enabled on every table", not no_rls, str(no_rls))

        cur.execute("select count(*) from pg_policies where schemaname='public'")
        check("RLS policies exist", cur.fetchone()[0] >= 25)

        cur.execute("select filename from public.applied_migrations order by filename")
        applied = [r[0] for r in cur.fetchall()]
        on_disk = sorted(p.name for p in (REPO / "supabase/migrations").glob("*.sql"))
        check("every migration is applied", applied == on_disk, f"{len(applied)}/{len(on_disk)}")

        # Orphans: rows whose parent has gone.
        cur.execute(
            "select count(*) from simulation_results s "
            "left join solar_applications a on a.id = s.application_id where a.id is null"
        )
        orphan_sims = cur.fetchone()[0]
        cur.execute(
            "select count(*) from risk_assessments r "
            "left join solar_applications a on a.id = r.application_id where a.id is null"
        )
        orphan_risks = cur.fetchone()[0]
        check("no orphaned engineering rows", orphan_sims == 0 and orphan_risks == 0,
              f"{orphan_sims} simulations, {orphan_risks} assessments")

        # Every assessed application must have both a simulation and a verdict.
        cur.execute(
            "select count(*) from solar_applications a "
            "where a.status <> 'DRAFT' and not exists "
            "(select 1 from risk_assessments r where r.application_id = a.id) "
            "and exists (select 1 from application_status_history h "
            "where h.application_id = a.id and h.to_status = 'ASSESSED')"
        )
        check("every assessed application has a verdict", cur.fetchone()[0] == 0)

        cur.execute("select count(*) from grid_assets where asset_type='BUS' and pv_eligible")
        check("the 71 eligible buses are loaded", cur.fetchone()[0] == 71)

        cur.execute(
            "select count(*) from grid_assets where asset_type='BUS' "
            "and attributes ? 'hosting_capacity_kw'"
        )
        check("hosting capacity is precomputed", cur.fetchone()[0] == 71)

        cur.execute("select count(*) from grid_assets where asset_type='LINE' and attributes ? 'from_bus'")
        check("line connectivity is intact", cur.fetchone()[0] == 40)

        cur.execute(
            "select count(*) from installations where discom_verified "
            "and discom_verified_by is null"
        )
        check("no verification without a verifier", cur.fetchone()[0] == 0)

        cur.execute("select count(*) from vendors where status='APPROVED' and verified_at is null")
        approved_unverified = cur.fetchone()[0]
        if approved_unverified:
            finding("LOW", "data", f"{approved_unverified} approved vendors have no verified_at timestamp")
except Exception as exc:  # noqa: BLE001
    check("database state", False, f"{type(exc).__name__}: {str(exc)[:80]}")

# ============================================================
print("\n9. Provenance statements are present")
# ============================================================
for label, path, needle in [
    ("footer disclaims the government portal", FRONTEND / "app/layout.tsx", "Not an official DISCOM or PM Surya Ghar portal"),
    ("map declares synthetic placement", BACKEND / "app/api/routes.py", "no geographic coordinates"),
    ("map denies being SCADA", BACKEND / "app/api/routes.py", "not a live SCADA feed"),
    ("grid summary declares provenance", BACKEND / "app/api/routes.py", "synthetic research network"),
    ("scheme denies being the portal", BACKEND / "app/services/scheme.py", "not the official PM Surya Ghar portal"),
    ("routing declares straight-line", BACKEND / "app/services/routing.py", "not a route"),
]:
    check(label, needle in path.read_text(encoding="utf-8"))

# ============================================================
print("\n10. The original research is untouched")
# ============================================================
import subprocess

status = subprocess.run(
    ["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True
).stdout
modified = [
    line for line in status.splitlines()
    if line[:2] in (" M", "M ", " D", "D ", "MM") and not line.split(maxsplit=1)[-1].startswith(("backend/", "frontend/", "docs/", "supabase/"))
]
check("no original research file is modified", not modified, str(modified[:3]))

for artifact in [
    "suryagrid_model_v2.pkl", "feeder_network.json", "scenario_config.json",
    "pv_dataset_enriched_augmented.csv", "enriched_features.json",
]:
    check(f"{artifact} present", (REPO / artifact).exists())

# ============================================================
passed = sum(1 for _, ok, _ in checks if ok)
total = len(checks)
print(f"\n{'=' * 70}")
print(f"  AUDIT: {passed}/{total} checks passed")
if findings:
    print(f"  {len(findings)} advisory finding(s):")
    for severity, area, message in findings:
        print(f"    [{severity}] {area}: {message}")
print(f"  OVERALL: {'PASS' if passed == total else 'FAIL'}")
print("=" * 70)
raise SystemExit(0 if passed == total else 1)
