"""Vendor ratings — citizen feedback with engagement-gated eligibility.

One review per (citizen, vendor, application), only where the citizen engaged
the vendor (appointment or installation) and real work exists (installation at
COMPLETED or beyond). Averages live on vendors.rating via a trigger (migration
0010); this module only validates and writes rows. Flags are computed, never
stored: avg < 2.5 with n >= 3, or >= 2 one-star reviews in 90 days. Vendors
with fewer than 3 reviews are never flagged.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.db.service import db

REVIEW_TAGS = (
    "ON_TIME",
    "CLEAN_WORK",
    "GOOD_COMM",
    "FAIR_PRICE",
    "DELAYS",
    "POOR_FINISH",
    "UNPROFESSIONAL",
)

EDIT_WINDOW_DAYS = 7
FLAG_MIN_REVIEWS = 3
FLAG_AVG_BELOW = 2.5
FLAG_RECENT_ONES = 2
FLAG_RECENT_DAYS = 90

# Installation must have reached real completed work before it can be rated.
RATABLE_INSTALLATION_STATUSES = (
    "COMPLETED",
    "VERIFICATION_PENDING",
    "VERIFIED",
)


class RatingError(ValueError):
    """Caller-facing validation failure (mapped to 422/403/404/409)."""


def _engaged(user_id: str, application_id: str, vendor_id: str) -> bool:
    appt = (
        db.as_service().table("appointments").select("id")
        .eq("application_id", application_id).eq("vendor_id", vendor_id)
        .eq("citizen_id", user_id).limit(1).execute()
    ).data
    if appt:
        return True
    inst = (
        db.as_service().table("installations").select("id")
        .eq("application_id", application_id).eq("vendor_id", vendor_id)
        .limit(1).execute()
    ).data
    if inst:
        return True
    app = (
        db.as_service().table("solar_applications").select("applicant_id")
        .eq("id", application_id).limit(1).execute()
    ).data
    return bool(app and app[0].get("applicant_id") == user_id and _vendor_on_app(application_id, vendor_id))


def _vendor_on_app(application_id: str, vendor_id: str) -> bool:
    rows = (
        db.as_service().table("installations").select("id")
        .eq("application_id", application_id).eq("vendor_id", vendor_id)
        .limit(1).execute()
    ).data
    return bool(rows)


def eligibility(user_id: str, application_id: str, vendor_id: str) -> dict[str, Any]:
    """Why the rate card shows (or doesn't) for this citizen/vendor/app."""
    app = (
        db.as_service().table("solar_applications").select("applicant_id,status")
        .eq("id", application_id).limit(1).execute()
    ).data
    if not app or app[0].get("applicant_id") != user_id:
        return {"eligible": False, "reason": "This application is not yours."}
    if not _engaged(user_id, application_id, vendor_id):
        return {"eligible": False, "reason": "You did not engage this vendor on this application."}
    inst = (
        db.as_service().table("installations").select("status")
        .eq("application_id", application_id).eq("vendor_id", vendor_id)
        .limit(1).execute()
    ).data
    if not inst or str(inst[0].get("status")) not in RATABLE_INSTALLATION_STATUSES:
        return {"eligible": False, "reason": "Rating opens once installation work completes."}
    existing = (
        db.as_service().table("vendor_reviews").select("id,created_at")
        .eq("citizen_id", user_id).eq("vendor_id", vendor_id)
        .eq("application_id", application_id).limit(1).execute()
    ).data
    if existing:
        created = existing[0].get("created_at")
        try:
            age = datetime.now(timezone.utc) - datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            age = timedelta(days=EDIT_WINDOW_DAYS + 1)
        if age <= timedelta(days=EDIT_WINDOW_DAYS):
            return {"eligible": True, "reason": "edit", "review_id": existing[0]["id"]}
        return {"eligible": False, "reason": "Review window closed (7 days)."}
    return {"eligible": True, "reason": "ok"}


def submit_review(
    user_id: str, application_id: str, vendor_id: str,
    rating: int, tags: list[str], comment: str | None,
) -> dict[str, Any]:
    elig = eligibility(user_id, application_id, vendor_id)
    if not elig["eligible"]:
        raise RatingError(elig["reason"])
    if not 1 <= int(rating) <= 5:
        raise RatingError("Rating must be 1-5 stars.")
    tags = [t for t in (tags or []) if t in REVIEW_TAGS]
    if int(rating) <= 2 and not tags and not (comment or "").strip():
        raise RatingError("A 1-2 star review needs at least one tag or a comment.")
    comment = (comment or "").strip()[:500] or None

    if elig.get("reason") == "edit":
        res = (
            db.as_service().table("vendor_reviews")
            .update({"rating": int(rating), "tags": tags, "comment": comment})
            .eq("id", elig["review_id"]).execute()
        )
        return (res.data or [{}])[0]

    try:
        res = (
            db.as_service().table("vendor_reviews")
            .insert({
                "application_id": application_id, "vendor_id": vendor_id,
                "citizen_id": user_id, "rating": int(rating),
                "tags": tags, "comment": comment,
            }).execute()
        )
    except Exception as exc:
        raise RatingError("You have already reviewed this vendor for this application.") from exc
    return (res.data or [{}])[0]


def _mask_name(full: str | None) -> str:
    if not full or not full.strip():
        return "Customer"
    parts = full.strip().split()
    last = f" {parts[-1][0]}." if len(parts) > 1 else ""
    return f"{parts[0]}{last}"


def public_summary(vendor_id: str, limit: int = 10) -> dict[str, Any]:
    rows = (
        db.as_service().table("vendor_reviews")
        .select("rating,tags,comment,created_at,citizen_id")
        .eq("vendor_id", vendor_id).order("created_at", desc=True).limit(500).execute()
    ).data or []
    count = len(rows)
    avg = round(sum(r["rating"] for r in rows) / count, 2) if count else None
    hist: dict[str, int] = {}
    for r in rows:
        for t in r.get("tags") or []:
            hist[t] = hist.get(t, 0) + 1
    latest = []
    for r in rows[: max(0, limit)]:
        prof = (
            db.as_service().table("profiles").select("full_name")
            .eq("id", r["citizen_id"]).limit(1).execute()
        ).data
        latest.append({
            "rating": r["rating"], "tags": r.get("tags") or [],
            "comment": r.get("comment"), "created_at": r.get("created_at"),
            "author": _mask_name((prof[0].get("full_name") if prof else None)),
        })
    return {"vendor_id": vendor_id, "average": avg, "count": count,
            "tag_histogram": hist, "reviews": latest, "flag": flag_for(rows)}


def flag_for(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Quality flag from a vendor's review rows. None = no flag."""
    if len(rows) < FLAG_MIN_REVIEWS:
        return None
    avg = sum(r["rating"] for r in rows) / len(rows)
    if avg < FLAG_AVG_BELOW:
        return {"rule": "low_average", "average": round(avg, 2), "count": len(rows)}
    cutoff = datetime.now(timezone.utc) - timedelta(days=FLAG_RECENT_DAYS)
    recent_ones = 0
    for r in rows:
        try:
            when = datetime.fromisoformat(str(r.get("created_at")).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            continue
        if r.get("rating") == 1 and when >= cutoff:
            recent_ones += 1
    if recent_ones >= FLAG_RECENT_ONES:
        return {"rule": "recent_one_stars", "recent_ones": recent_ones, "count": len(rows)}
    return None


def rating_flags() -> list[dict[str, Any]]:
    """All vendors currently breaching the flag rule (DISCOM queue)."""
    vendors = (
        db.as_service().table("vendors").select("id,business_name,status,rating")
        .execute()
    ).data or []
    out = []
    for v in vendors:
        rows = (
            db.as_service().table("vendor_reviews").select("rating,created_at")
            .eq("vendor_id", v["id"]).execute()
        ).data or []
        flag = flag_for(rows)
        if flag:
            out.append({"vendor": v, "flag": flag})
    return out
