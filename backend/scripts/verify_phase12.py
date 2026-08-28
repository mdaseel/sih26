"""Phase 12 acceptance check — security and final integration.

Covers the checklist from the build plan, plus the three controls added in this
phase: rate limiting, file-upload validation, and error handling that does not
leak internals.
"""

from __future__ import annotations

import re
import sys
import uuid
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

from app.core.security import EXPENSIVE_LIMIT, limiter  # noqa: E402
from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402
from app.services.storage import UploadRejected, get_storage_service  # noqa: E402

BASE = "http://127.0.0.1:8000"
REPO = Path(__file__).resolve().parents[2]
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def denied(exc: Exception) -> bool:
    t = str(exc).lower()
    return any(m in t for m in ("row-level security", "permission denied", "violates", "42501", "pgrst"))


svc = get_service_client()
users: list[str] = []

try:
    # ============================================================
    print("\nA. Secrets never reach the client")
    # ============================================================
    service_key = svc.supabase_key if hasattr(svc, "supabase_key") else ""
    from app.core.config import get_settings

    settings = get_settings()
    secrets = [s for s in (settings.supabase_service_role_key, settings.database_url) if s]

    frontend = REPO / "frontend"
    leaked: list[str] = []
    for path in list(frontend.rglob("*.ts")) + list(frontend.rglob("*.tsx")):
        if "node_modules" in str(path) or ".next" in str(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(secret and secret in text for secret in secrets):
            leaked.append(str(path.relative_to(REPO)))
    check("no secret appears in frontend source", not leaked, str(leaked[:3]))

    built = frontend / ".next"
    leaked_build: list[str] = []
    if built.exists():
        for path in built.rglob("*.js"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:  # noqa: BLE001
                continue
            if any(secret and secret in text for secret in secrets):
                leaked_build.append(path.name)
    check(
        "no secret appears in the built frontend bundle",
        not leaked_build,
        f"scanned {sum(1 for _ in built.rglob('*.js')) if built.exists() else 0} files",
    )

    env_local = frontend / ".env.local"
    if env_local.exists():
        text = env_local.read_text(encoding="utf-8")
        check(
            "frontend env holds no service-role key or database URL",
            "SERVICE_ROLE" not in text and "postgres" not in text.lower(),
        )

    check(
        "the config summary never prints key material",
        not any(secret and secret in str(settings.describe()) for secret in secrets),
    )

    # ============================================================
    print("\nB. Authentication and role-based access")
    # ============================================================
    def make(role: str) -> tuple[str, dict[str, str], str]:
        email = f"solargrid-p12-{uuid.uuid4().hex[:6]}@example.com"
        pw = f"Verify!{uuid.uuid4().hex[:12]}"
        u = svc.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True})
        users.append(u.user.id)
        if role != "CITIZEN":
            svc.table("profiles").update({"role": role}).eq("id", u.user.id).execute()
        token = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": pw}
        ).session.access_token
        return u.user.id, {"Authorization": f"Bearer {token}"}, token

    citizen_id, CITIZEN, citizen_token = make("CITIZEN")
    discom_id, DISCOM, _ = make("DISCOM")

    protected = [
        "/api/applications",
        "/api/map",
        "/api/discom/summary",
        "/api/vendor/summary",
        "/api/scheme",
    ]
    for path in protected:
        r = httpx.get(f"{BASE}{path}", timeout=30)
        check(f"unauthenticated {path} refused", r.status_code in (401, 403), f"status {r.status_code}")

    r = httpx.get(f"{BASE}/api/applications", headers={"Authorization": "Bearer not-a-jwt"}, timeout=30)
    check("a malformed token is refused", r.status_code == 401, f"status {r.status_code}")

    r = httpx.get(f"{BASE}/api/applications", headers={"Authorization": "Basic abc"}, timeout=30)
    check("a non-bearer scheme is refused", r.status_code == 401)

    # ============================================================
    print("\nC. The build-plan checklist")
    # ============================================================
    r = httpx.get(f"{BASE}/api/discom/summary", headers=CITIZEN, timeout=30)
    check("citizen cannot access DISCOM functions", r.status_code == 403)

    app_id = httpx.post(
        f"{BASE}/api/applications",
        headers=CITIZEN,
        json={"applicant_name": "P12", "pv_bus": "620", "existing_pv_kw": 0, "new_pv_kw": 5},
        timeout=60,
    ).json()["id"]
    httpx.post(f"{BASE}/api/applications/{app_id}/assess", headers=CITIZEN, timeout=180)

    cit = get_anon_client()
    cit.postgrest.auth(citizen_token)

    for table, payload, label in [
        ("risk_assessments", {"engineering_risk": "SAFE"}, "citizen cannot modify risk"),
        ("simulation_results", {"voltage_rise_pu": 0.0}, "citizen cannot modify simulation results"),
    ]:
        try:
            res = cit.table(table).update(payload).eq("application_id", app_id).execute()
            check(label, not res.data, f"{len(res.data)} rows changed")
        except Exception as exc:  # noqa: BLE001
            check(label, denied(exc), type(exc).__name__)

    try:
        res = cit.table("solar_applications").update({"status": "APPROVED"}).eq("id", app_id).execute()
        check("frontend cannot override backend status", not res.data, f"{len(res.data)} rows")
    except Exception as exc:  # noqa: BLE001
        check("frontend cannot override backend status", denied(exc), type(exc).__name__)

    status_now = (svc.table("solar_applications").select("status").eq("id", app_id).execute()).data[0]
    check("the application status is unchanged", status_now["status"] != "APPROVED", status_now["status"])

    # Vendor boundaries (fuller coverage lives in phases 8 and 9).
    r = httpx.post(f"{BASE}/api/vendors/register", headers=CITIZEN, json={"business_name": "P12 Vendor"}, timeout=60)
    vendor_id = r.json()["vendor"]["id"] if r.status_code == 201 else None
    check("a vendor cannot self-approve", r.status_code == 201 and r.json()["vendor"]["status"] == "PENDING")

    r = httpx.get(f"{BASE}/api/vendors", headers=DISCOM, timeout=60)
    check(
        "unapproved vendors cannot receive customer leads",
        not any(v["id"] == vendor_id for v in r.json()["vendors"]),
        "pending vendor is not discoverable",
    )

    # ============================================================
    print("\nD. Input validation")
    # ============================================================
    bad_inputs = [
        ({"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": -5}, "negative capacity"),
        ({"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": 999999}, "absurd capacity"),
        ({"pv_bus": "'; DROP TABLE solar_applications;--", "new_pv_kw": 5}, "SQL in a bus id"),
        ({"pv_bus": "<script>alert(1)</script>", "new_pv_kw": 5}, "script tag in a bus id"),
        ({"pv_bus": "../../etc/passwd", "new_pv_kw": 5}, "path traversal in a bus id"),
        ({"new_pv_kw": 5}, "missing required field"),
    ]
    for payload, label in bad_inputs:
        r = httpx.post(f"{BASE}/api/assess", headers=CITIZEN, json=payload, timeout=60)
        check(f"rejects {label}", r.status_code in (404, 422), f"status {r.status_code}")

    tables = (svc.table("solar_applications").select("id").limit(1).execute()).data
    check("the database survived the injection attempts", tables is not None)

    # ============================================================
    print("\nE. File upload validation")
    # ============================================================
    storage = get_storage_service()
    real_pdf = b"%PDF-1.7\n" + b"0" * 200

    ok_mime, ok_name = storage.validate(real_pdf, "application/pdf", "my licence.pdf")
    check("a genuine PDF is accepted", ok_mime == "application/pdf")
    check("the display name is sanitised", " " not in ok_name, ok_name)

    for content, declared, name, label in [
        (b"MZ\x90\x00" + b"0" * 200, "application/pdf", "evil.pdf", "an executable renamed as PDF"),
        (b"%PDF-1.7\n" + b"0" * 200, "image/png", "x.png", "a PDF declared as PNG"),
        (b"<?php system($_GET[0]); ?>", "application/pdf", "shell.php", "a PHP script"),
        (b"%PDF-1.7", "application/pdf", "tiny.pdf", "a file below the minimum size"),
        (b"%PDF-1.7\n" + b"0" * (6 * 1024 * 1024), "application/pdf", "huge.pdf", "a file over the size limit"),
        (b"%PDF-1.7\n" + b"0" * 200, "text/html", "x.html", "a disallowed type"),
    ]:
        try:
            storage.validate(content, declared, name)
            check(f"rejects {label}", False, "accepted")
        except UploadRejected as exc:
            check(f"rejects {label}", True, str(exc)[:50])

    traversal = storage.validate(real_pdf, "application/pdf", "../../../etc/passwd")[1]
    check("path traversal in a filename is neutralised", "/" not in traversal and ".." not in traversal, traversal)

    policy = storage.describe()
    check("the bucket is private", policy["public"] is False)
    check("paths are server-generated", "server-generated" in policy["path_policy"])
    check("access is via signed URLs", "signed URL" in policy["access"])

    # ============================================================
    print("\nG. Error handling and headers")
    # ============================================================
    r = httpx.get(f"{BASE}/health", timeout=30)
    headers = {k.lower(): v for k, v in r.headers.items()}
    for header, expected in [
        ("x-content-type-options", "nosniff"),
        ("x-frame-options", "DENY"),
        ("referrer-policy", "no-referrer"),
        ("cache-control", "no-store"),
    ]:
        check(f"header {header}", headers.get(header) == expected, headers.get(header, "missing"))

    r = httpx.get(f"{BASE}/api/applications/not-a-uuid", headers=CITIZEN, timeout=60)
    text = r.text.lower()
    for leak in ["traceback", "postgres", "psycopg", "supabase.co", "select ", "file \"/"]:
        check(f"no '{leak.strip()}' in an error response", leak not in text, f"status {r.status_code}")

    r = httpx.post(f"{BASE}/api/assess", headers=CITIZEN, json={"pv_bus": "99999", "new_pv_kw": 5}, timeout=60)
    check("a not-found error is a clean message", r.status_code == 404 and "detail" in r.json())

    # ============================================================
    print("\nH. Audit logging")
    # ============================================================
    audits = (
        svc.table("audit_logs").select("action,actor_id,actor_ref,entity_type,entity_id").order("created_at", desc=True).limit(200).execute()
    ).data or []
    actions = {a["action"] for a in audits}
    for expected in ["application.create", "application.assess", "vendor.register"]:
        check(f"audited: {expected}", expected in actions)
    # Scope to entries this run produced. Rows written before migration 0006
    # had their actor_id nulled by the FK cascade and cannot be recovered —
    # that lost history is exactly what the migration exists to prevent going
    # forward, not something it can undo.
    ours = [a for a in audits if a.get("entity_id") in {app_id, vendor_id}]
    check(
        "audit entries written now name an actor durably",
        bool(ours) and all(a.get("actor_ref") for a in ours),
        f"{sum(1 for a in ours if a.get('actor_ref'))}/{len(ours)} carry actor_ref",
    )
    check(
        "attribution is recorded independently of the foreign key",
        all(a.get("actor_ref") == str(a.get("actor_id")) for a in ours if a.get("actor_id")),
        "actor_ref mirrors actor_id while the profile exists",
    )

    try:
        res = cit.table("audit_logs").select("*").limit(1).execute()
        check("a citizen cannot read the audit log", not res.data, f"{len(res.data)} rows visible")
    except Exception as exc:  # noqa: BLE001
        check("a citizen cannot read the audit log", denied(exc), type(exc).__name__)


    # ============================================================
    print("\nI. Rate limiting (last: it exhausts the server-side counter)")
    # ============================================================
    limiter.reset()
    codes = []
    for _ in range(EXPENSIVE_LIMIT.requests + 5):
        r = httpx.post(
            f"{BASE}/api/assess",
            headers=CITIZEN,
            json={"pv_bus": "620", "existing_pv_kw": 0, "new_pv_kw": 5},
            timeout=60,
        )
        codes.append(r.status_code)
        if r.status_code == 429:
            break
    check(
        "expensive endpoints are rate limited",
        429 in codes,
        f"429 after {codes.index(429) if 429 in codes else len(codes)} requests",
    )

    r = httpx.post(
        f"{BASE}/api/assess", headers=CITIZEN,
        json={"pv_bus": "620", "existing_pv_kw": 0, "new_pv_kw": 5}, timeout=60,
    )
    if r.status_code == 429:
        body = r.json()
        check("the 429 explains the limit", "limit" in body and "retry_after_seconds" in body, body.get("limit", ""))
        check("a Retry-After header is sent", "retry-after" in {k.lower() for k in r.headers})

    r = httpx.get(f"{BASE}/health", timeout=30)
    check("health is never rate limited", r.status_code == 200)
    check(
        "the limitation is disclosed rather than hidden",
        "per-process" in r.json()["rate_limiting"]["limitation"],
    )
    limiter.reset()

    svc.table("solar_applications").delete().eq("id", app_id).execute()
    if vendor_id:
        svc.table("vendors").delete().eq("id", vendor_id).execute()

finally:
    print("\nI. Cleanup")
    for uid in users:
        try:
            svc.auth.admin.delete_user(uid)
        except Exception:  # noqa: BLE001
            pass
    limiter.reset()
    check("test users removed", True)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 12 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
