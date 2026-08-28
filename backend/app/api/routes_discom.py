"""DISCOM routes — review, approval and network oversight.

Authorization is enforced in two independent places, because either alone is a
single point of failure:

  1. Here, by require_discom, which resolves the caller's role from the
     profiles table on every request.
  2. In Postgres, by RLS plus the column grants in migration 0004 — a citizen's
     token cannot move an application into APPROVED no matter what it sends.

A decision is written with the service role after the role check passes, so
the transition is recorded by the backend rather than asserted by a client.
Every decision is audited.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, require_discom
from app.db.service import db
from app.models.enums import ApplicationStatus
from app.services.grid_assets import get_grid_asset_service
from app.services.power_flow import get_power_flow_service

router = APIRouter(prefix="/api/discom", tags=["discom"])

# Applications still waiting on a DISCOM decision.
AWAITING_REVIEW = (
    ApplicationStatus.SUBMITTED.value,
    ApplicationStatus.ASSESSED.value,
    ApplicationStatus.UNDER_DISCOM_REVIEW.value,
    ApplicationStatus.ENGINEERING_REVIEW.value,
)

# Applications whose capacity is committed to the network.
COMMITTED = (
    ApplicationStatus.APPROVED.value,
    ApplicationStatus.VENDOR_SELECTED.value,
    ApplicationStatus.INSTALLING.value,
    ApplicationStatus.INSTALLED.value,
    ApplicationStatus.VERIFIED.value,
)

CLOSED = (ApplicationStatus.REJECTED.value, ApplicationStatus.CANCELLED.value)


def _latest_risk_by_application() -> dict[str, dict[str, Any]]:
    """Newest risk assessment per application, keyed by application id."""
    rows = (
        db.as_service()
        .table("risk_assessments")
        .select(
            "application_id,engineering_risk,ml_prediction,constraint_type,"
            "constraint_reason,ml_agrees_with_engineering,created_at,simulation_id,"
            "safe_probability,caution_probability,constrained_probability"
        )
        .order("created_at", desc=True)
        .execute()
    ).data or []
    out: dict[str, dict[str, Any]] = {}
    for row in rows:  # newest first, so the first wins
        out.setdefault(row["application_id"], row)
    return out


def _all_applications() -> list[dict[str, Any]]:
    return (
        db.as_service()
        .table("solar_applications")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    ).data or []


# ============================================================
#  Dashboard
# ============================================================
@router.get("/summary")
def summary(user: CurrentUser = Depends(require_discom)) -> dict[str, Any]:
    """Headline numbers for the DISCOM dashboard.

    The two capacity figures are deliberately named for what they actually
    measure. "Approved" is capacity the DISCOM has committed to; "pending" is
    capacity still awaiting a decision. Neither is a measurement of installed
    generation on the real network, which this system does not observe.
    """
    apps = _all_applications()
    risks = _latest_risk_by_application()

    by_risk = {"SAFE": 0, "CAUTION": 0, "CONSTRAINED": 0, "NOT_ASSESSED": 0}
    for a in apps:
        risk = risks.get(a["id"])
        by_risk[risk["engineering_risk"] if risk else "NOT_ASSESSED"] += 1

    approved_kw = sum(float(a["new_pv_kw"]) for a in apps if a["status"] in COMMITTED)
    pending_kw = sum(float(a["new_pv_kw"]) for a in apps if a["status"] in AWAITING_REVIEW)
    existing_kw = sum(float(a["existing_pv_kw"]) for a in apps if a["status"] not in CLOSED)

    disagreements = [
        a["id"]
        for a in apps
        if (r := risks.get(a["id"])) and r["ml_agrees_with_engineering"] is False
    ]

    return {
        "total_applications": len(apps),
        "pending_review": sum(1 for a in apps if a["status"] in AWAITING_REVIEW),
        "approved": sum(1 for a in apps if a["status"] in COMMITTED),
        "rejected": sum(1 for a in apps if a["status"] == ApplicationStatus.REJECTED.value),
        "by_risk": by_risk,
        "approved_solar_kw": round(approved_kw, 2),
        "pending_solar_kw": round(pending_kw, 2),
        "declared_existing_solar_kw": round(existing_kw, 2),
        "ml_engineering_disagreements": len(disagreements),
        "capacity_note": (
            "Approved and pending capacity are sums of application requests. They "
            "are not a measurement of generation installed on the network."
        ),
        "network": get_power_flow_service().network_summary(),
        "data_class": "Prototype • Synthetic Grid Data",
    }


# ============================================================
#  Application queue
# ============================================================
@router.get("/applications")
def applications(user: CurrentUser = Depends(require_discom)) -> list[dict[str, Any]]:
    """Every application, with its latest assessment attached."""
    apps = _all_applications()
    risks = _latest_risk_by_application()

    out = []
    for a in apps:
        risk = risks.get(a["id"])
        out.append(
            {
                **a,
                "engineering_risk": risk["engineering_risk"] if risk else None,
                "ml_prediction": risk["ml_prediction"] if risk else None,
                "constraint_type": risk["constraint_type"] if risk else None,
                "constraint_reason": risk["constraint_reason"] if risk else None,
                "ml_agrees_with_engineering": risk["ml_agrees_with_engineering"] if risk else None,
                "assessed": risk is not None,
            }
        )
    return out


@router.get("/applications/{application_id}")
def application_detail(
    application_id: str, user: CurrentUser = Depends(require_discom)
) -> dict[str, Any]:
    """Full review packet: applicant, assessment, simulation, and history."""
    service = db.as_service()

    app_rows = (
        service.table("solar_applications").select("*").eq("id", application_id).execute()
    ).data or []
    if not app_rows:
        raise HTTPException(status_code=404, detail="Application not found")
    application = app_rows[0]

    risk = db.get_latest_assessment(application_id)
    simulation = (
        db.get_simulation(risk["simulation_id"])
        if risk and risk.get("simulation_id")
        else db.get_latest_simulation(application_id)
    )
    history = (
        service.table("application_status_history")
        .select("*")
        .eq("application_id", application_id)
        .order("created_at", desc=False)
        .execute()
    ).data or []

    bus = None
    try:
        bus = get_grid_asset_service().get(application["pv_bus"]).as_dict()
    except Exception:  # noqa: BLE001 - a stored bus that is no longer eligible
        bus = None

    return {
        "application": application,
        "assessment": risk,
        "simulation": simulation,
        "history": history,
        "bus": bus,
    }


# ============================================================
#  Decisions
# ============================================================
class Decision(BaseModel):
    decision: str = Field(description="APPROVED, ENGINEERING_REVIEW or REJECTED")
    notes: str | None = Field(default=None, max_length=2000)


ALLOWED_DECISIONS = {
    "APPROVED": ApplicationStatus.APPROVED,
    "ENGINEERING_REVIEW": ApplicationStatus.ENGINEERING_REVIEW,
    "REJECTED": ApplicationStatus.REJECTED,
}


@router.post("/applications/{application_id}/decision")
def decide(
    application_id: str,
    payload: Decision,
    user: CurrentUser = Depends(require_discom),
) -> dict[str, Any]:
    """Record a DISCOM decision on an application.

    Reaching this line already required a DISCOM or ADMIN role. The write then
    goes through the service role, so the transition is performed by the
    backend rather than trusted from a client.

    Approving a CONSTRAINED application is permitted but never silent: the
    engineering objection is copied into the audit record, so an override is
    always attributable. The power flow is not overruled — it is accepted with
    a documented decision on top.
    """
    if payload.decision not in ALLOWED_DECISIONS:
        raise HTTPException(
            status_code=422,
            detail=f"decision must be one of {sorted(ALLOWED_DECISIONS)}",
        )

    service = db.as_service()
    rows = (
        service.table("solar_applications").select("*").eq("id", application_id).execute()
    ).data or []
    if not rows:
        raise HTTPException(status_code=404, detail="Application not found")
    application = rows[0]

    if application["status"] in CLOSED:
        raise HTTPException(
            status_code=409,
            detail=f"Application is already {application['status']}",
        )

    risk = db.get_latest_assessment(application_id)
    if risk is None and payload.decision == "APPROVED":
        raise HTTPException(
            status_code=409,
            detail="Cannot approve an application that has not been assessed",
        )

    new_status = ALLOWED_DECISIONS[payload.decision]
    override = (
        payload.decision == "APPROVED"
        and risk is not None
        and risk["engineering_risk"] == "CONSTRAINED"
    )

    updated = (
        service.table("solar_applications")
        .update(
            {
                "status": new_status.value,
                "reviewed_by": user.id,
                "reviewed_at": "now()",
                "review_notes": payload.notes,
            }
        )
        .eq("id", application_id)
        .execute()
    ).data

    db.audit(
        action=f"application.decision.{payload.decision.lower()}",
        entity_type="solar_applications",
        entity_id=application_id,
        actor_id=user.id,
        actor_role=user.role.value,
        before_state={"status": application["status"]},
        after_state={
            "status": new_status.value,
            "notes": payload.notes,
            "engineering_risk": risk["engineering_risk"] if risk else None,
            "override_of_engineering_objection": override,
            "engineering_objection": risk["constraint_reason"] if override else None,
        },
    )

    return {
        "application": updated[0] if updated else None,
        "decision": payload.decision,
        "override_of_engineering_objection": override,
        "engineering_risk": risk["engineering_risk"] if risk else None,
        "note": (
            "Approved against an engineering objection; the objection is recorded "
            "in the audit log."
            if override
            else "Decision recorded."
        ),
    }


# ============================================================
#  Network oversight
# ============================================================
@router.get("/transformers")
def transformers(user: CurrentUser = Depends(require_discom)) -> list[dict[str, Any]]:
    """Distribution transformers with measured loading and requested capacity."""
    service = db.as_service()
    assets = (
        service.table("grid_assets")
        .select("asset_code,name,sn_kva,vn_kv,attributes")
        .eq("asset_type", "TRANSFORMER")
        .execute()
    ).data or []

    buses = (
        service.table("grid_assets")
        .select("asset_code,transformer_association,pv_eligible,existing_load_kw,attributes")
        .eq("asset_type", "BUS")
        .execute()
    ).data or []

    apps = _all_applications()
    pending_by_bus: dict[str, float] = {}
    approved_by_bus: dict[str, float] = {}
    for a in apps:
        if a["status"] in AWAITING_REVIEW:
            pending_by_bus[a["pv_bus"]] = pending_by_bus.get(a["pv_bus"], 0.0) + float(a["new_pv_kw"])
        elif a["status"] in COMMITTED:
            approved_by_bus[a["pv_bus"]] = approved_by_bus.get(a["pv_bus"], 0.0) + float(a["new_pv_kw"])

    thresholds = get_grid_asset_service().thresholds()
    out = []
    for t in assets:
        served = [b for b in buses if b["transformer_association"] == t["asset_code"]]
        eligible = [b for b in served if b["pv_eligible"]]
        capacities = [
            (b["attributes"] or {}).get("hosting_capacity_kw")
            for b in eligible
            if (b["attributes"] or {}).get("hosting_capacity_kw") is not None
        ]
        loading = (t["attributes"] or {}).get("base_loading_pct")

        out.append(
            {
                "name": t["asset_code"],
                "sn_kva": t["sn_kva"],
                "vn_kv": t["vn_kv"],
                "base_loading_pct": loading,
                "loading_status": (
                    None
                    if loading is None
                    else "CONSTRAINED"
                    if loading > thresholds["transformer_loading_hard_pct"]
                    else "CAUTION"
                    if loading >= thresholds["transformer_loading_caution_pct"]
                    else "SAFE"
                ),
                "connection_points": len(eligible),
                "served_buses": len(served),
                "min_hosting_capacity_kw": min(capacities) if capacities else None,
                "total_load_kw": round(
                    sum(float(b["existing_load_kw"] or 0) for b in served), 2
                ),
                "pending_pv_kw": round(
                    sum(pending_by_bus.get(b["asset_code"], 0.0) for b in served), 2
                ),
                "approved_pv_kw": round(
                    sum(approved_by_bus.get(b["asset_code"], 0.0) for b in served), 2
                ),
            }
        )

    out.sort(key=lambda r: (r["base_loading_pct"] is None, -(r["base_loading_pct"] or 0)))
    return out


class WhatIfRequest(BaseModel):
    pv_bus: str = Field(min_length=1, max_length=16)
    existing_pv_kw: float = Field(default=0.0, ge=0, le=5000)
    capacities_kw: list[float] = Field(
        default=[10, 25, 50, 100, 250, 500],
        max_length=24,
        description="Capacities to test. Each one is a real power-flow run.",
    )


@router.post("/what-if")
def what_if(payload: WhatIfRequest, user: CurrentUser = Depends(require_discom)) -> dict[str, Any]:
    """Sweep capacities at one connection point.

    Every point is an independent power-flow solve on the server. Nothing is
    interpolated between them and no trend is fitted, so a capacity that has no
    solution appears as a failed point rather than a gap the eye fills in.

    The exact boundary is not read off this sweep — it comes from the bisection
    in HostingCapacityService, and is returned alongside so the two can be
    compared.
    """
    from app.services.hosting_capacity import get_hosting_capacity_service
    from app.services.ml_prediction import get_ml_service
    from app.services.power_flow import PowerFlowError
    from app.services.risk_assessment import get_risk_service

    grid = get_grid_asset_service()
    try:
        bus = grid.get(payload.pv_bus)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    pf = get_power_flow_service()
    risk = get_risk_service()
    ml = get_ml_service()

    points = []
    for kw in sorted({round(float(c), 3) for c in payload.capacities_kw if c > 0}):
        try:
            metrics = pf.simulate(payload.pv_bus, payload.existing_pv_kw, kw)
            verdict = risk.evaluate(metrics)
            prediction = ml.predict(payload.pv_bus, payload.existing_pv_kw, kw)
            points.append(
                {
                    "new_pv_kw": kw,
                    "converged": True,
                    "engineering_risk": verdict.engineering_risk.value,
                    "constraint_type": verdict.constraint_type.value,
                    "constraint_reason": verdict.constraint_reason,
                    "ml_prediction": prediction.prediction.value,
                    "ml_constrained_probability": round(prediction.constrained_probability, 5),
                    "metrics": metrics.as_dict(),
                }
            )
        except PowerFlowError as exc:
            points.append(
                {
                    "new_pv_kw": kw,
                    "converged": False,
                    "engineering_risk": None,
                    "error": str(exc),
                }
            )

    capacity = get_hosting_capacity_service().capacity_for(payload.pv_bus, payload.existing_pv_kw)

    return {
        "pv_bus": payload.pv_bus,
        "existing_pv_kw": payload.existing_pv_kw,
        "bus": bus.as_dict(),
        "points": points,
        "hosting_capacity": capacity.as_dict(),
        "thresholds": grid.thresholds(),
        "note": (
            "Each row is an independent power-flow solve. Nothing between the rows "
            "is interpolated; the exact limit comes from the bisection above."
        ),
    }


@router.get("/hosting-capacity/feeders")
def feeder_hosting_capacity(user: CurrentUser = Depends(require_discom)) -> dict[str, Any]:
    """Hosting capacity per feeder section, with capacity already committed.

    The capacity figure is the total the section can host with all its
    connections energised at once — measured by bisection on the whole feeder,
    not by adding up per-bus capacities. Both numbers are returned so the
    difference is visible: adding them up overstates the limit, on this feeder
    by up to a factor of 20.
    """
    service = db.as_service()
    sections = (
        service.table("grid_assets")
        .select("asset_code,attributes")
        .eq("asset_type", "FEEDER")
        .neq("asset_code", "IEEE_CompTestFeeder")
        .execute()
    ).data or []

    if not sections:
        raise HTTPException(
            status_code=503,
            detail=(
                "Feeder hosting capacity has not been computed. "
                "Run: python backend/scripts/precompute_grid_map.py"
            ),
        )

    buses = (
        service.table("grid_assets")
        .select("asset_code,feeder_section,pv_eligible,existing_load_kw,attributes")
        .eq("asset_type", "BUS")
        .eq("pv_eligible", True)
        .execute()
    ).data or []
    section_of = {b["asset_code"]: b["feeder_section"] for b in buses}

    apps = _all_applications()
    approved: dict[str, float] = {}
    pending: dict[str, float] = {}
    for a in apps:
        section = section_of.get(a["pv_bus"])
        if section is None:
            continue
        if a["status"] in COMMITTED:
            approved[section] = approved.get(section, 0.0) + float(a["new_pv_kw"])
        elif a["status"] in AWAITING_REVIEW:
            pending[section] = pending.get(section, 0.0) + float(a["new_pv_kw"])

    out = []
    for row in sections:
        name = row["asset_code"]
        attrs = row.get("attributes") or {}
        capacity = float(attrs.get("hosting_capacity_kw") or 0.0)
        current = approved.get(name, 0.0)
        queued = pending.get(name, 0.0)
        remaining = max(0.0, capacity - current - queued)

        # A section's own risk: how much of its capacity is already spoken for.
        used_fraction = (current + queued) / capacity if capacity else 1.0
        section_risk = (
            "CONSTRAINED" if used_fraction >= 1.0 else "CAUTION" if used_fraction >= 0.8 else "SAFE"
        )

        out.append(
            {
                "feeder_section": name,
                "connection_points": int(attrs.get("buses") or 0),
                "current_solar_kw": round(current, 2),
                "pending_solar_kw": round(queued, 2),
                "hosting_capacity_kw": capacity,
                "remaining_capacity_kw": round(remaining, 1),
                "utilisation_pct": round(used_fraction * 100, 1),
                "limiting_constraint": attrs.get("limiting_constraint"),
                "limiting_reason": attrs.get("limiting_reason"),
                "risk": section_risk,
                "per_bus_kw_at_capacity": attrs.get("per_bus_kw"),
                "sum_of_per_bus_kw": attrs.get("sum_of_per_bus_kw"),
                "overstatement_factor": attrs.get("overstatement_factor"),
                "method": attrs.get("method"),
                "distribution": attrs.get("distribution"),
            }
        )

    out.sort(key=lambda r: r["feeder_section"])
    return {
        "sections": out,
        "method_note": (
            "Capacity is bisected with every connection in the section energised "
            "together, so interaction between them is included. Summing each bus's "
            "individual capacity would overstate the limit — sum_of_per_bus_kw is "
            "shown for comparison, not for use."
        ),
        "risk_note": (
            "Section risk reflects how much of the section's capacity is already "
            "committed or queued. It is not a power-flow verdict on any one "
            "application."
        ),
    }


@router.get("/feeders")
def feeders(user: CurrentUser = Depends(require_discom)) -> list[dict[str, Any]]:
    """Feeder sections, with the capacity requested against each."""
    service = db.as_service()
    buses = (
        service.table("grid_assets")
        .select("asset_code,feeder_section,pv_eligible,existing_load_kw,attributes")
        .eq("asset_type", "BUS")
        .eq("pv_eligible", True)
        .execute()
    ).data or []

    apps = _all_applications()
    section_of = {b["asset_code"]: b["feeder_section"] for b in buses}

    grouped: dict[str, dict[str, Any]] = {}
    for b in buses:
        section = b["feeder_section"] or "unassigned"
        g = grouped.setdefault(
            section,
            {
                "feeder_section": section,
                "connection_points": 0,
                "total_load_kw": 0.0,
                "hosting_capacity_kw": 0.0,
                "min_hosting_capacity_kw": None,
                "pending_pv_kw": 0.0,
                "approved_pv_kw": 0.0,
                "applications": 0,
            },
        )
        g["connection_points"] += 1
        g["total_load_kw"] += float(b["existing_load_kw"] or 0)
        cap = (b["attributes"] or {}).get("hosting_capacity_kw")
        if cap is not None:
            g["hosting_capacity_kw"] += cap
            g["min_hosting_capacity_kw"] = (
                cap if g["min_hosting_capacity_kw"] is None else min(g["min_hosting_capacity_kw"], cap)
            )

    for a in apps:
        section = section_of.get(a["pv_bus"])
        if section is None or section not in grouped:
            continue
        grouped[section]["applications"] += 1
        if a["status"] in AWAITING_REVIEW:
            grouped[section]["pending_pv_kw"] += float(a["new_pv_kw"])
        elif a["status"] in COMMITTED:
            grouped[section]["approved_pv_kw"] += float(a["new_pv_kw"])

    for g in grouped.values():
        g["total_load_kw"] = round(g["total_load_kw"], 2)
        g["hosting_capacity_kw"] = round(g["hosting_capacity_kw"], 1)
        g["pending_pv_kw"] = round(g["pending_pv_kw"], 2)
        g["approved_pv_kw"] = round(g["approved_pv_kw"], 2)
        committed = g["pending_pv_kw"] + g["approved_pv_kw"]
        g["remaining_capacity_kw"] = round(max(0.0, g["hosting_capacity_kw"] - committed), 1)
        g["capacity_note"] = (
            "Section capacity is the sum of per-bus hosting capacities, each computed "
            "independently. Simultaneous connections interact, so the true section "
            "limit is lower than this sum."
        )

    return sorted(grouped.values(), key=lambda g: g["feeder_section"])
