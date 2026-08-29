"""API routes.

Endpoint map (Phase 2):
    GET  /api/grid/buses               the 71 valid PV connection points
    GET  /api/grid/summary             network + threshold summary
    POST /api/assess                   engineering assessment, no persistence
    POST /api/applications             create an application
    GET  /api/applications             list the caller's applications
    GET  /api/applications/{id}        application + latest assessment
    POST /api/applications/{id}/assess run ML + power flow, persist, return
    GET  /api/simulations/{id}         one stored simulation result

The engineering pipeline is identical in /api/assess and in
/api/applications/{id}/assess — the only difference is whether the result is
written to the database. There is no second code path that could drift.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, get_current_user
from app.db.service import db
from app.models.enums import ApplicationStatus
from app.models.schemas import (
    ApplicationCreate,
    AssessmentOut,
    AssessmentRequest,
    BusOut,
    EngineeringMetricsOut,
)
from app.services.grid_assets import (
    IneligibleBusError,
    UnknownBusError,
    get_grid_asset_service,
)
from app.services.ml_prediction import get_ml_service
from app.services.power_flow import PowerFlowError, get_power_flow_service
from app.services.risk_assessment import get_risk_service
from app.services.site_context import get_site_context_service
from app.services.topology import get_topology_service

router = APIRouter(prefix="/api")

# Statuses an application can still be moved out of by a re-assessment. Once
# the DISCOM has decided, or a vendor is engaged, the assessment is evidence
# rather than a lever — running it again must not rewind the case.
PRE_DECISION_STATUSES = frozenset(
    {
        ApplicationStatus.DRAFT.value,
        ApplicationStatus.SUBMITTED.value,
        ApplicationStatus.ASSESSING.value,
        ApplicationStatus.ASSESSED.value,
        ApplicationStatus.UNDER_DISCOM_REVIEW.value,
        ApplicationStatus.ENGINEERING_REVIEW.value,
    }
)


# ============================================================
#  Core engineering pipeline — the single source of truth
# ============================================================
def run_assessment(pv_bus: str, existing_pv_kw: float, new_pv_kw: float) -> dict[str, Any]:
    """ML pre-screen, then deterministic power flow, then the engineering verdict.

    Order is deliberate and matches the product's stated flow: the model gives
    a fast opinion, the power flow decides.
    """
    grid = get_grid_asset_service()
    try:
        grid.get(pv_bus)  # validates existence and eligibility up front
    except UnknownBusError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IneligibleBusError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    ml = get_ml_service().predict(pv_bus, existing_pv_kw, new_pv_kw)

    try:
        metrics = get_power_flow_service().simulate(pv_bus, existing_pv_kw, new_pv_kw)
    except PowerFlowError as exc:
        # A non-converging case is an engineering result, not a server fault.
        raise HTTPException(status_code=422, detail=f"Power flow failed: {exc}") from exc

    verdict = get_risk_service().evaluate(metrics)

    return {
        "ml": ml.as_dict() | {"prediction": ml.prediction.value},
        "engineering": verdict.as_dict(),
        "metrics": metrics.as_dict(),
        "ml_agrees_with_engineering": ml.prediction == verdict.engineering_risk,
        "_ml_obj": ml,
        "_verdict_obj": verdict,
        "_metrics_obj": metrics,
    }


def _to_out(result: dict[str, Any], **ids: Any) -> AssessmentOut:
    return AssessmentOut(
        ml=result["ml"],
        engineering=result["engineering"],
        metrics=result["metrics"],
        ml_agrees_with_engineering=result["ml_agrees_with_engineering"],
        **ids,
    )


# ============================================================
#  Grid reference data
# ============================================================
@router.get("/grid/buses", response_model=list[BusOut], tags=["grid"])
def list_buses() -> list[dict[str, Any]]:
    """The 71 PV-eligible LV buses. This is the citizen's connection-point list."""
    return get_grid_asset_service().list_eligible()


@router.get("/grid/summary", tags=["grid"])
def grid_summary() -> dict[str, Any]:
    grid = get_grid_asset_service()
    return {
        "feeder_id": grid.feeder_id,
        "network": get_power_flow_service().network_summary(),
        "eligible_bus_count": len(grid.eligible_bus_ids()),
        "thresholds": grid.thresholds(),
        "threshold_source": "scenario_config.json",
        "data_class": "Prototype • Synthetic Grid Data",
        "provenance": (
            "IEEE Comprehensive Test Feeder — a synthetic research network. "
            "Not a real DISCOM topology, and not live SCADA."
        ),
    }


@router.get("/grid/topology", tags=["grid"])
def grid_topology() -> dict[str, Any]:
    """The full network graph for the digital twin.

    Nodes and edges are read from feeder_network.json — the same model the
    power flow solves — so the twin can never show a topology the simulation
    does not have.
    """
    return get_topology_service().full_graph()


@router.get("/grid/topology/{bus_id}", tags=["grid"])
def grid_local_topology(bus_id: str) -> dict[str, Any]:
    """Source → bus path plus the customer premises: the affected slice."""
    view = get_topology_service().local_view(bus_id)
    if not view["nodes"]:
        raise HTTPException(status_code=404, detail=f"No path to bus {bus_id}")
    return view


@router.get("/site-context", tags=["gis"])
def site_context(latitude: float, longitude: float, radius_m: int = 160) -> dict[str, Any]:
    """OSM building footprints around a coordinate.

    Fetched via Overpass. Used by the 3D Cesium viewer to render real building geometry
    and roof heights without faking non-existent structures.
    """
    return get_site_context_service().buildings(latitude, longitude, radius_m)


# ============================================================
#  GIS map
# ============================================================
@router.get("/map", tags=["map"])
def map_data(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """Everything the geographic map draws.

    Assets carry the precomputed layer values written by
    scripts/precompute_grid_map.py — base voltage and loading from one BASE
    power flow, hosting capacity from bisection on that same power flow.

    Applications are read with the caller's own token, so Row Level Security
    decides what appears: a citizen sees their own pins, a DISCOM user sees
    every pin. The map does not filter — the database does.
    """
    service = db.as_service()

    assets = (
        service.table("grid_assets")
        .select(
            "asset_type,asset_code,name,vn_kv,sn_kva,transformer_association,feeder_section,"
            "existing_load_kw,base_voltage_pu,pv_eligible,latitude,longitude,"
            "geometry_source,attributes,parent_asset_code"
        )
        .execute()
    ).data or []

    apps = db.list_applications_for_user(user.access_token)
    app_ids = [a["id"] for a in apps]

    risk_by_app: dict[str, dict[str, Any]] = {}
    if app_ids:
        rows = (
            service.table("risk_assessments")
            .select("application_id,engineering_risk,ml_prediction,constraint_type,constraint_reason,created_at,simulation_id")
            .in_("application_id", app_ids)
            .order("created_at", desc=True)
            .execute()
        ).data or []
        for row in rows:  # ordered newest first, so the first wins
            risk_by_app.setdefault(row["application_id"], row)

    sim_by_app: dict[str, dict[str, Any]] = {}
    sim_ids = [r["simulation_id"] for r in risk_by_app.values() if r.get("simulation_id")]
    if sim_ids:
        rows = (
            service.table("simulation_results")
            .select(
                "id,application_id,pv_voltage_pu,voltage_rise_pu,max_transformer_loading_pct,"
                "max_line_loading_pct,reverse_power_flow,solar_penetration_pct"
            )
            .in_("id", sim_ids)
            .execute()
        ).data or []
        for row in rows:
            sim_by_app[row["application_id"]] = row

    coords = {
        a["asset_code"]: (a["latitude"], a["longitude"])
        for a in assets
        if a["asset_type"] == "BUS" and a["latitude"] is not None
    }

    application_points = []
    for a in apps:
        lat, lon = coords.get(a["pv_bus"], (None, None))
        if lat is None:
            continue  # a bus with no placement is omitted rather than guessed at
        risk = risk_by_app.get(a["id"])
        sim = sim_by_app.get(a["id"])
        application_points.append(
            {
                "id": a["id"],
                "application_number": a["application_number"],
                "applicant_name": a["applicant_name"],
                "pv_bus": a["pv_bus"],
                "existing_pv_kw": float(a["existing_pv_kw"]),
                "new_pv_kw": float(a["new_pv_kw"]),
                "total_pv_kw": float(a["total_pv_kw"]),
                "status": a["status"],
                "latitude": lat,
                "longitude": lon,
                "engineering_risk": risk["engineering_risk"] if risk else None,
                "ml_prediction": risk["ml_prediction"] if risk else None,
                "constraint_type": risk["constraint_type"] if risk else None,
                "constraint_reason": risk["constraint_reason"] if risk else None,
                "pv_voltage_pu": float(sim["pv_voltage_pu"]) if sim and sim.get("pv_voltage_pu") is not None else None,
                "voltage_rise_pu": float(sim["voltage_rise_pu"]) if sim and sim.get("voltage_rise_pu") is not None else None,
                "max_transformer_loading_pct": float(sim["max_transformer_loading_pct"])
                if sim and sim.get("max_transformer_loading_pct") is not None
                else None,
                "max_line_loading_pct": float(sim["max_line_loading_pct"])
                if sim and sim.get("max_line_loading_pct") is not None
                else None,
                "reverse_power_flow": sim.get("reverse_power_flow") if sim else None,
                "solar_penetration_pct": float(sim["solar_penetration_pct"])
                if sim and sim.get("solar_penetration_pct") is not None
                else None,
            }
        )

    # Pending solar per bus, from applications not yet rejected or cancelled.
    pending_by_bus: dict[str, float] = {}
    for a in apps:
        if a["status"] in ("REJECTED", "CANCELLED"):
            continue
        pending_by_bus[a["pv_bus"]] = pending_by_bus.get(a["pv_bus"], 0.0) + float(a["new_pv_kw"])

    return {
        "assets": assets,
        "applications": application_points,
        "pending_pv_by_bus": pending_by_bus,
        "thresholds": get_grid_asset_service().thresholds(),
        "anchor_note": (
            "Distances along the feeder are real, taken from the line lengths in the "
            "network model. Absolute placement is illustrative: the IEEE test feeder "
            "carries no geographic coordinates."
        ),
        "data_class": "Prototype • Synthetic Grid Data",
        "liveness": (
            "Real-time-like application simulation — values update immediately after "
            "each assessment. This is not a live SCADA feed."
        ),
    }


@router.get("/grid/hosting-capacity", tags=["map"])
def hosting_capacity_all(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """Hosting capacity for every eligible bus, from the stored precompute."""
    rows = (
        db.as_service()
        .table("grid_assets")
        .select("asset_code,attributes,transformer_association,feeder_section")
        .eq("asset_type", "BUS")
        .eq("pv_eligible", True)
        .execute()
    ).data or []

    out = []
    for r in rows:
        attrs = r.get("attributes") or {}
        if "hosting_capacity_kw" not in attrs:
            continue
        out.append(
            {
                "bus_id": r["asset_code"],
                "transformer_association": r["transformer_association"],
                "feeder_section": r["feeder_section"],
                "hosting_capacity_kw": attrs["hosting_capacity_kw"],
                "limiting_constraint": attrs.get("hosting_capacity_limiting_constraint"),
                "limiting_reason": attrs.get("hosting_capacity_reason"),
                "method": attrs.get("hosting_capacity_method"),
            }
        )

    if not out:
        raise HTTPException(
            status_code=503,
            detail=(
                "Hosting capacity has not been computed. "
                "Run: python backend/scripts/precompute_grid_map.py"
            ),
        )
    return {"buses": out, "count": len(out)}


@router.get("/grid/hosting-capacity/{bus_id}", tags=["map"])
def hosting_capacity_bus(
    bus_id: str, existing_pv_kw: float = 0.0, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Hosting capacity for one bus, computed on demand by bisection."""
    from app.services.hosting_capacity import get_hosting_capacity_service

    try:
        return get_hosting_capacity_service().capacity_for(bus_id, existing_pv_kw).as_dict()
    except UnknownBusError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IneligibleBusError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ============================================================
#  Digital twin
# ============================================================
@router.post("/twin", tags=["twin"])
def twin(payload: AssessmentRequest, user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """Assessment plus the per-element before/after the twin animates.

    Runs the identical pipeline as /api/assess — one ML prediction, one BASE
    power flow, one PV power flow — and additionally returns what happened to
    each asset along the path, so the drawing can colour only what moved.
    """
    grid = get_grid_asset_service()
    try:
        grid.get(payload.pv_bus)
    except UnknownBusError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IneligibleBusError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    ml = get_ml_service().predict(payload.pv_bus, payload.existing_pv_kw, payload.new_pv_kw)

    try:
        metrics, elements = get_power_flow_service().simulate_with_elements(
            payload.pv_bus, payload.existing_pv_kw, payload.new_pv_kw
        )
    except PowerFlowError as exc:
        raise HTTPException(status_code=422, detail=f"Power flow failed: {exc}") from exc

    verdict = get_risk_service().evaluate(metrics)

    return {
        "assessment": AssessmentOut(
            ml=ml.as_dict() | {"prediction": ml.prediction.value},
            engineering=verdict.as_dict(),
            metrics=metrics.as_dict(),
            ml_agrees_with_engineering=ml.prediction == verdict.engineering_risk,
        ).model_dump(),
        "topology": get_topology_service().local_view(payload.pv_bus),
        "elements": elements,
    }


# ============================================================
#  Stateless assessment (what-if / preview)
# ============================================================
@router.post("/assess", response_model=AssessmentOut, tags=["assessment"])
def assess(payload: AssessmentRequest, user: CurrentUser = Depends(get_current_user)) -> AssessmentOut:
    """Run the full engineering pipeline without persisting anything."""
    result = run_assessment(payload.pv_bus, payload.existing_pv_kw, payload.new_pv_kw)
    return _to_out(result)


# ============================================================
#  Applications
# ============================================================
@router.post("/applications", status_code=status.HTTP_201_CREATED, tags=["applications"])
def create_application(
    payload: ApplicationCreate, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    grid = get_grid_asset_service()
    try:
        bus = grid.get(payload.pv_bus)
    except UnknownBusError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IneligibleBusError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    row = payload.model_dump(exclude={"submit"})
    row["applicant_id"] = user.id

    # The load figure comes from the grid, not from the applicant.
    #
    # A citizen is not expected to know the load sanctioned on their service
    # connection, so the form does not ask. The network model does hold a
    # connected load for the chosen connection point, and that is what travels
    # with the application to the DISCOM. It is the model's figure, measured
    # from the same feeder data the power flow runs on -- not a claim about
    # what the DISCOM has sanctioned, which remains theirs to assert and
    # overrides this the moment they say otherwise.
    row["sanctioned_load_kw"] = round(bus.existing_load_kw, 3)
    row["status"] = (
        ApplicationStatus.SUBMITTED.value if payload.submit else ApplicationStatus.DRAFT.value
    )

    # Inserted with the caller's own token so RLS enforces applicant_id = auth.uid().
    created = db.create_application(user.access_token, row)
    if not created:
        raise HTTPException(status_code=400, detail="Application could not be created")

    db.audit(
        action="application.create",
        entity_type="solar_applications",
        entity_id=created.get("id"),
        actor_id=user.id,
        actor_role=user.role.value,
        after_state={"pv_bus": row["pv_bus"], "new_pv_kw": row["new_pv_kw"]},
    )
    return created


@router.get("/applications", tags=["applications"])
def list_applications(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    """RLS decides the rows: a citizen sees their own, DISCOM sees all."""
    return db.list_applications_for_user(user.access_token)


@router.get("/applications/{application_id}", tags=["applications"])
def get_application(
    application_id: str, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    app_row = db.get_application(user.access_token, application_id)
    if app_row is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"application": app_row, "latest_assessment": db.get_latest_assessment(application_id)}


def _stored_assessment(application_id: str) -> AssessmentOut | None:
    """Rebuild the canonical assessment shape from what was stored.

    Reading beats re-simulating: an assessment already carries the thresholds
    that were applied and the metrics that were measured, so replaying the
    power flow to display a past result would burn CPU and, worse, could show
    numbers that differ from the ones actually on record.
    """
    risk = db.get_latest_assessment(application_id)
    if not risk:
        return None

    sim = (
        db.get_simulation(risk["simulation_id"])
        if risk.get("simulation_id")
        else db.get_latest_simulation(application_id)
    )
    if not sim:
        return None

    metric_fields = set(EngineeringMetricsOut.model_fields.keys())

    return AssessmentOut(
        application_id=application_id,
        simulation_id=sim.get("id"),
        assessment_id=risk.get("id"),
        ml={
            "prediction": risk["ml_prediction"],
            "safe_probability": float(risk["safe_probability"]),
            "caution_probability": float(risk["caution_probability"]),
            "constrained_probability": float(risk["constrained_probability"]),
            "model_file": risk["model_file"],
            "model_version": risk["model_version"],
            "feature_count": int(risk["feature_count"]),
        },
        engineering={
            "engineering_risk": risk["engineering_risk"],
            "constraint_type": risk["constraint_type"],
            "constraint_reason": risk["constraint_reason"] or "",
            "thresholds_snapshot": risk.get("thresholds_snapshot") or {},
        },
        metrics={k: v for k, v in sim.items() if k in metric_fields},
        ml_agrees_with_engineering=bool(risk["ml_agrees_with_engineering"]),
        persisted=True,
    )


@router.get("/applications/{application_id}/timeline", tags=["applications"])
def get_application_timeline(
    application_id: str, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Every status this application has actually held, oldest first.

    These rows are written by a database trigger on every status change, so the
    timeline is a record of what happened rather than a story reconstructed
    afterwards from the current state. A stage the application never reached
    has no row here, and the UI must not invent one.

    Read with the caller's own token: RLS returns history only for their own
    application (or any of them, for a DISCOM reviewer).
    """
    if db.get_application(user.access_token, application_id) is None:
        raise HTTPException(status_code=404, detail="Application not found")

    rows = (
        db.as_user(user.access_token)
        .table("application_status_history")
        .select("id,from_status,to_status,note,created_at")
        .eq("application_id", application_id)
        .order("created_at")
        .execute()
    ).data or []

    return {"application_id": application_id, "history": rows}


@router.get("/applications/{application_id}/assessment", tags=["assessment"])
def get_stored_assessment(
    application_id: str, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """The stored assessment, without re-running anything.

    Access is gated by reading the application through the caller's own token
    first, so RLS decides visibility before any privileged read happens.
    """
    if db.get_application(user.access_token, application_id) is None:
        raise HTTPException(status_code=404, detail="Application not found")

    stored = _stored_assessment(application_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="No assessment has been run yet")
    return stored.model_dump()


@router.post("/applications/{application_id}/assess", tags=["assessment"])
def assess_application(
    application_id: str, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Assess an application and persist the result.

    The read goes through the caller's token, so RLS decides whether they may
    see this application at all. The writes go through the service role,
    because simulation_results and risk_assessments deliberately have no client
    write policy — the applicant cannot influence their own verdict.
    """
    app_row = db.get_application(user.access_token, application_id)
    if app_row is None:
        raise HTTPException(status_code=404, detail="Application not found")

    if app_row["applicant_id"] != user.id and not user.is_discom:
        raise HTTPException(status_code=403, detail="Not permitted to assess this application")

    previous_status = app_row["status"]
    db.set_application_status(application_id, ApplicationStatus.ASSESSING.value)

    try:
        result = run_assessment(
            app_row["pv_bus"],
            float(app_row["existing_pv_kw"]),
            float(app_row["new_pv_kw"]),
        )
    except HTTPException:
        db.set_application_status(application_id, previous_status)
        raise

    metrics = result["_metrics_obj"]
    sim_payload = metrics.as_dict() | {"application_id": application_id}
    sim_row = db.insert_simulation_result(sim_payload)

    combined = get_risk_service().combine(result["_ml_obj"], result["_verdict_obj"])
    risk_payload = combined | {
        "application_id": application_id,
        "simulation_id": sim_row.get("id"),
    }
    risk_row = db.insert_risk_assessment(risk_payload)

    # Where the application lands afterwards.
    #
    # Being assessed is an internal milestone, not an outcome: the screening is
    # done but nobody has decided anything, and an applicant reading "assessed"
    # reasonably thinks their request has been dealt with. So an application
    # that was still waiting moves to UNDER_DISCOM_REVIEW -- it is with the
    # DISCOM, which is the true state -- and the DISCOM's own decision is what
    # moves it to APPROVED or REJECTED.
    #
    # An application that had already been decided keeps its decision. Re-running
    # the numbers is not a way to reopen a determination.
    if previous_status in PRE_DECISION_STATUSES:
        db.set_application_status(application_id, ApplicationStatus.UNDER_DISCOM_REVIEW.value)
    else:
        db.set_application_status(application_id, previous_status)
    db.audit(
        action="application.assess",
        entity_type="risk_assessments",
        entity_id=risk_row.get("id"),
        actor_id=user.id,
        actor_role=user.role.value,
        after_state={
            "engineering_risk": combined["engineering_risk"],
            "ml_prediction": combined["ml_prediction"],
        },
    )

    out = _to_out(
        result,
        application_id=application_id,
        simulation_id=sim_row.get("id"),
        assessment_id=risk_row.get("id"),
    )
    out.persisted = True
    return out.model_dump()


@router.get("/simulations/{simulation_id}", tags=["assessment"])
def get_simulation(
    simulation_id: str, user: CurrentUser = Depends(get_current_user)
) -> dict[str, Any]:
    """Read one stored simulation through the caller's token, so RLS applies."""
    res = (
        db.as_user(user.access_token)
        .table("simulation_results")
        .select("*")
        .eq("id", simulation_id)
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return res.data[0]

@router.get("/me", tags=["meta"])
def me(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """The caller's identity and role.

    Used by the frontend to choose which navigation to render. It is a
    convenience only: the role returned here grants nothing, because every
    privileged route re-resolves the role server-side.
    """
    profile = db.get_profile(user.id) or {}
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "is_discom": user.is_discom,
        "full_name": profile.get("full_name"),
        "discom_name": profile.get("discom_name"),
    }
