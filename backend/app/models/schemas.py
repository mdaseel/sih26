"""Request and response models.

Field names follow the existing pipeline wherever one exists, so a value keeps
the same name from scenario_config.json through the power flow, the database
column, and the JSON the frontend renders.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ApplicationStatus, ConstraintKind, RiskLevel


# ============================================================
#  Requests
# ============================================================
class ApplicationCreate(BaseModel):
    """A citizen's connection request.

    Note what is absent: sanctioned_load_kw. That is a DISCOM-side record of
    the load sanctioned on the service connection, and an applicant generally
    does not have it to hand -- asking for it invites a guess, and a guessed
    number would then travel to the DISCOM looking like a declaration. The
    backend fills it from the connection point instead; see
    routes.create_application.
    """

    applicant_name: str = Field(min_length=1, max_length=200)
    contact_phone: str | None = Field(default=None, max_length=20)
    address_line: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = Field(default=None, max_length=10)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    consumer_number: str | None = None
    connection_type: str | None = None
    monthly_consumption_kwh: float | None = Field(default=None, ge=0)

    roof_area_sqm: float | None = Field(default=None, ge=0)
    roof_type: str | None = None
    shading_level: str | None = None

    # The technical inputs the engineering layers consume.
    #
    # pv_bus is optional because a householder cannot know it: which LV bus
    # serves an address is a DISCOM record, not something on an electricity
    # bill. When it is absent the backend resolves it from latitude/longitude
    # (see ConnectionPointService) and stores what it resolved. A client that
    # does know the bus — the DISCOM's own tooling — may still send one.
    pv_bus: str | None = Field(default=None, min_length=1, max_length=16)
    existing_pv_kw: float = Field(default=0.0, ge=0, le=5000)
    new_pv_kw: float = Field(gt=0, le=5000)

    solar_placement: dict[str, Any] | None = Field(default=None, description="Interactive 3D rooftop solar placement geometry and suitability metadata")

    submit: bool = Field(default=True, description="Submit immediately, or keep as DRAFT")

    @field_validator("pv_bus")
    @classmethod
    def _bus_is_digits(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v.isdigit():
            raise ValueError("pv_bus must be a numeric bus identifier, e.g. '734'")
        return v


class AssessmentRequest(BaseModel):
    """Direct engineering assessment, no persistence. Used by what-if tooling."""

    pv_bus: str = Field(min_length=1, max_length=16)
    existing_pv_kw: float = Field(default=0.0, ge=0, le=5000)
    new_pv_kw: float = Field(gt=0, le=5000)

    @field_validator("pv_bus")
    @classmethod
    def _bus_is_digits(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("pv_bus must be a numeric bus identifier, e.g. '734'")
        return v


# ============================================================
#  Responses
# ============================================================
class MLPredictionOut(BaseModel):
    prediction: RiskLevel
    safe_probability: float
    caution_probability: float
    constrained_probability: float
    model_file: str
    model_version: str
    feature_count: int

    # What the forest was given, and how many trees voted on it.
    #
    # Pre-simulation inputs only: bus identity, declared capacities, and the
    # network constants for that connection point. Deliberately absent are the
    # power-flow results — the model predicts from what is known beforehand, and
    # feeding it the answer would make the comparison with the simulation
    # meaningless.
    features_used: dict[str, Any] = Field(default_factory=dict)
    tree_count: int | None = None


class EngineeringMetricsOut(BaseModel):
    """Deterministic power-flow output. Every field is simulated, never assumed."""

    pv_bus: str
    existing_pv_kw: float
    new_pv_kw: float
    total_pv_kw: float

    base_voltage_pu: float
    pv_voltage_pu: float
    voltage_rise_pu: float
    feeder_min_voltage_pu: float
    feeder_max_voltage_pu: float
    min_voltage_bus: str
    max_voltage_bus: str

    base_max_line_loading_pct: float
    max_line_loading_pct: float
    worst_line: str
    base_max_transformer_loading_pct: float
    max_transformer_loading_pct: float
    worst_transformer: str

    base_total_p_kw: float
    pv_total_p_kw: float
    power_loss_kw: float
    delta_losses_kw: float
    reverse_power_flow: bool
    reverse_reason: str
    solar_penetration_pct: float

    converged: bool
    engine: str
    engine_version: str
    network_file: str
    runtime_ms: int


class EngineeringVerdictOut(BaseModel):
    engineering_risk: RiskLevel
    constraint_type: ConstraintKind
    constraint_reason: str
    thresholds_snapshot: dict[str, float]


class AssessmentOut(BaseModel):
    """The complete two-layer result.

    ml is the pre-screen. engineering is the decision. They are reported
    separately and never merged.
    """

    application_id: str | None = None
    simulation_id: str | None = None
    assessment_id: str | None = None

    ml: MLPredictionOut
    engineering: EngineeringVerdictOut
    metrics: EngineeringMetricsOut

    ml_agrees_with_engineering: bool
    authority: str = Field(
        default="power_flow",
        description="Which layer decides the outcome. Always the power flow.",
    )
    data_class: str = Field(
        default="Prototype • Synthetic Grid Data",
        description="Provenance of the underlying network model.",
    )
    disclaimer: str = Field(
        default=(
            "Technical pre-screening on a synthetic IEEE test feeder. "
            "This is not an official DISCOM approval."
        )
    )
    persisted: bool = False


class ApplicationOut(BaseModel):
    id: str
    application_number: str | None = None
    applicant_id: str | None = None
    applicant_name: str
    pv_bus: str
    existing_pv_kw: float
    new_pv_kw: float
    total_pv_kw: float
    status: ApplicationStatus
    created_at: str | None = None
    solar_placement: dict[str, Any] | None = None
    latest_assessment: AssessmentOut | None = None
    raw: dict[str, Any] | None = None


class BusOut(BaseModel):
    bus_id: str
    vn_kv: float
    existing_load_kw: float
    transformer_association: str
    feeder_section: str
    transformer_sn_kva: float
    base_voltage_pu: float
    feeder_distance_km: float
    upstream_r_ohm: float
    upstream_x_ohm: float
    upstream_z_ohm: float
    phase_configuration: str | None = None
    voltage_level_label: str | None = None
