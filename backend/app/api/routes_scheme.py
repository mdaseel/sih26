"""Scheme routes — PM Surya Ghar information and indicative CFA estimates.

Read-only. This application does not register anyone for the scheme, submit
anything to the government, or move any money; it explains the process and
estimates a figure from configured rules.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import CurrentUser, get_current_user
from app.db.service import db
from app.services.scheme import SchemeNotConfigured, get_scheme_service

router = APIRouter(prefix="/api/scheme", tags=["scheme"])


@router.get("")
def scheme_overview(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """Everything the scheme page shows, entirely from configuration."""
    try:
        return get_scheme_service().overview()
    except SchemeNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/estimate")
def cfa_estimate(
    capacity_kw: float = Query(gt=0, le=5000, description="Proposed system size in kW"),
    user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Indicative Central Financial Assistance for a capacity.

    Arithmetic on configured slabs. It is not a sanction, a quotation, or a
    promise of payment, and the response says so.
    """
    try:
        return get_scheme_service().estimate_cfa(capacity_kw).as_dict()
    except SchemeNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/estimate/application/{application_id}")
def estimate_for_application(
    application_id: str, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Estimate for a specific application's requested capacity.

    Read through the caller's own token so RLS decides whether they may see the
    application at all.
    """
    application = db.get_application(user.access_token, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    capacity = float(application["new_pv_kw"])
    try:
        estimate = get_scheme_service().estimate_cfa(capacity).as_dict()
    except SchemeNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "application_id": application_id,
        "application_number": application.get("application_number"),
        "requested_capacity_kw": capacity,
        "estimate": estimate,
        "note": (
            "The estimate covers the requested capacity. The subsidy that is actually "
            "sanctioned depends on the capacity commissioned and on the scheme rules in "
            "force at the time, decided by the government — not by this application."
        ),
    }
