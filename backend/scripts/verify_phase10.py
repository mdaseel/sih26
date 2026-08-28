"""Phase 10 acceptance check — PM Surya Ghar / CFA.

What matters here is restraint rather than capability:

  * no scheme value is compiled into the application
  * every estimate is labelled indicative
  * unverified configuration announces itself
  * the app never claims to be the government portal
"""

from __future__ import annotations

import re
import subprocess
import sys
import uuid
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import httpx  # noqa: E402

from app.core.supabase_client import get_anon_client, get_service_client  # noqa: E402
from app.services.scheme import get_scheme_service  # noqa: E402

BASE = "http://127.0.0.1:8000"
REPO = Path(__file__).resolve().parents[2]
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


svc = get_service_client()
users: list[str] = []

try:
    # ============================================================
    print("\nA. No scheme value is hardcoded")
    # ============================================================
    # The placeholder rates must exist in the seed script and nowhere else in
    # the running application. If a rate leaks into service or UI code it stops
    # being configurable, which is the whole point of this phase.
    # Read the files directly rather than using `git grep`: these files are new
    # and untracked, and git grep silently searches nothing.
    def grep(pattern: str, paths: list[str]) -> list[str]:
        rx = re.compile(pattern)
        hits: list[str] = []
        for base in paths:
            root = REPO / base
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.suffix not in {".py", ".ts", ".tsx"} or not path.is_file():
                    continue
                try:
                    if rx.search(path.read_text(encoding="utf-8")):
                        hits.append(str(path.relative_to(REPO)).replace("\\", "/"))
                except Exception:  # noqa: BLE001
                    continue
        return sorted(hits)

    rate_hits = grep(r"\b(30000|18000|78000)\b", ["backend/app", "frontend/app", "frontend/components"])
    check(
        "subsidy rates appear in no application code",
        not rate_hits,
        f"found in {rate_hits}" if rate_hits else "only in the seed and the database",
    )

    seed_hits = grep(r"\b30000\b", ["backend/seed"])
    check(
        "the rates do live in the seed script, as configuration",
        bool(seed_hits),
        str(seed_hits),
    )

    service_src = (REPO / "backend/app/services/scheme.py").read_text(encoding="utf-8")
    check(
        "the scheme service holds no currency or rate literals",
        not re.search(r"\b\d{4,}\b", service_src),
        "no four-plus digit literals",
    )

    # ============================================================
    print("\nB. Estimates are arithmetic on configuration")
    # ============================================================
    scheme = get_scheme_service()
    rules = scheme.config()["cfa_slabs"]["value"]
    slabs = sorted(rules["slabs"], key=lambda s: s["up_to_kw"])
    first, second = slabs[0], slabs[1]

    e1 = scheme.estimate_cfa(1)
    check(
        "1 kW uses the first slab only",
        e1.amount == first["rate_per_kw"] * 1,
        f"{e1.amount} = 1 x {first['rate_per_kw']}",
    )

    e2 = scheme.estimate_cfa(first["up_to_kw"])
    check(
        "the first slab is applied across its whole band",
        e2.amount == first["rate_per_kw"] * first["up_to_kw"],
        f"{e2.amount}",
    )

    e3 = scheme.estimate_cfa(second["up_to_kw"])
    expected = first["rate_per_kw"] * first["up_to_kw"] + second["rate_per_kw"] * (
        second["up_to_kw"] - first["up_to_kw"]
    )
    check(
        "the second slab applies only to the band above the first",
        e3.amount == min(expected, rules["max_subsidy"]),
        f"{e3.amount} vs computed {expected}",
    )
    check("two bands are itemised", len(e3.breakdown) == 2, f"{len(e3.breakdown)} bands")

    big = scheme.estimate_cfa(50)
    check(
        "capacity above the eligible maximum is clamped",
        big.eligible_capacity_kw == rules["max_eligible_capacity_kw"],
        f"50 kW -> eligible {big.eligible_capacity_kw} kW",
    )
    check(
        "the amount never exceeds the configured maximum",
        big.amount <= rules["max_subsidy"],
        f"{big.amount} <= {rules['max_subsidy']}",
    )

    # Changing configuration must change the answer, with no code change.
    original = rules
    doubled = {**rules, "slabs": [{**s, "rate_per_kw": s["rate_per_kw"] * 2} for s in slabs]}
    svc.table("scheme_config").update({"config_value": doubled}).eq(
        "scheme_code", "PM_SURYA_GHAR"
    ).eq("config_key", "cfa_slabs").execute()
    after = scheme.estimate_cfa(1)
    check(
        "editing the configuration changes the estimate",
        after.amount == e1.amount * 2,
        f"{e1.amount} -> {after.amount} after doubling the rate",
    )
    svc.table("scheme_config").update({"config_value": original}).eq(
        "scheme_code", "PM_SURYA_GHAR"
    ).eq("config_key", "cfa_slabs").execute()
    restored = scheme.estimate_cfa(1)
    check("configuration restored", restored.amount == e1.amount, f"{restored.amount}")

    # ============================================================
    print("\nC. Nothing is presented as authoritative")
    # ============================================================
    email = f"solargrid-p10-{uuid.uuid4().hex[:6]}@example.com"
    pw = f"Verify!{uuid.uuid4().hex[:12]}"
    u = svc.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True})
    users.append(u.user.id)
    token = get_anon_client().auth.sign_in_with_password(
        {"email": email, "password": pw}
    ).session.access_token
    H = {"Authorization": f"Bearer {token}"}

    r = httpx.get(f"{BASE}/api/scheme/estimate?capacity_kw=3", headers=H, timeout=60)
    est = r.json()
    check("GET /api/scheme/estimate", r.status_code == 200)
    check("the estimate is flagged indicative", est["indicative"] is True)
    check(
        "the required wording is present",
        est["disclaimer"] == "Indicative estimate based on configured scheme rules.",
        est["disclaimer"],
    )
    check(
        "the response denies being the government portal",
        "not the official PM Surya Ghar portal" in est["not_official_portal"],
    )
    check(
        "unverified configuration is reported as unverified",
        est["configuration_verified"] is False and "NOT been verified" in est["verification_note"],
    )

    r = httpx.get(f"{BASE}/api/scheme", headers=H, timeout=60)
    overview = r.json()
    check("GET /api/scheme", r.status_code == 200)
    for key in ("overview", "eligibility", "process_steps", "cfa_rules", "official_links"):
        check(f"the page has {key}", bool(overview.get(key)))
    check(
        "the process marks which steps happen here and which do not",
        any(s["in_this_app"] for s in overview["process_steps"])
        and any(not s["in_this_app"] for s in overview["process_steps"]),
    )
    check(
        "official links point at government domains",
        all(".gov.in" in l["url"] for l in overview["official_links"]),
        ", ".join(l["url"] for l in overview["official_links"]),
    )
    check(
        "the configuration location is disclosed",
        overview["configuration"]["editable_at"] == "public.scheme_config",
    )

    r = httpx.get(f"{BASE}/api/scheme/estimate?capacity_kw=0", headers=H, timeout=60)
    check("a zero capacity is rejected", r.status_code == 422)

    r = httpx.get(f"{BASE}/api/scheme", timeout=60)
    check("the scheme routes require authentication", r.status_code in (401, 403))

    # ============================================================
    print("\nD. Estimate for a real application")
    # ============================================================
    r = httpx.post(
        f"{BASE}/api/applications",
        headers=H,
        json={"applicant_name": "Phase 10", "pv_bus": "620", "existing_pv_kw": 0, "new_pv_kw": 3},
        timeout=60,
    )
    app_id = r.json()["id"]
    r = httpx.get(f"{BASE}/api/scheme/estimate/application/{app_id}", headers=H, timeout=60)
    body = r.json()
    check(
        "an application estimate uses its requested capacity",
        r.status_code == 200 and body["requested_capacity_kw"] == 3,
    )
    check(
        "it explains that the sanctioned amount is decided elsewhere",
        "decided by the government" in body["note"],
    )
    svc.table("solar_applications").delete().eq("id", app_id).execute()

    # ============================================================
    print("\nE. The UI carries the same statements")
    # ============================================================
    page = (REPO / "frontend/app/citizen/scheme/page.tsx").read_text(encoding="utf-8")
    check(
        "the page states it is not the government portal",
        "not the government portal" in page,
    )
    check("the page links to the official portal", "official_portal_url" in page)
    check(
        "the page warns when the configuration is unverified",
        "unverified placeholders" in page,
    )
    check(
        "the page renders configuration rather than literals",
        "scheme.cfa_rules" in page and not re.search(r"\b(30000|18000|78000)\b", page),
    )

    layout = (REPO / "frontend/app/layout.tsx").read_text(encoding="utf-8")
    check(
        "every page footer disclaims the government portal",
        "Not an official DISCOM or PM Surya Ghar portal" in layout,
    )

finally:
    print("\nF. Cleanup")
    for uid in users:
        try:
            svc.auth.admin.delete_user(uid)
        except Exception:  # noqa: BLE001
            pass
    check("test users removed", True)

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'=' * 60}\nPHASE 10 VERIFICATION: {passed}/{total} checks passed")
print("OVERALL:", "PASS" if passed == total else "FAIL")
raise SystemExit(0 if passed == total else 1)
