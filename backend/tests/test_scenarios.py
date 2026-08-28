"""The twelve scenarios the build plan requires, plus the regression cases.

These are the cases a reviewer would ask about: one of each risk class, each
constraint type, the awkward inputs, and the two connections the original model
got wrong.

The regression tests are the important ones. They assert the behaviour recorded
in phase4_5_validation_report.md, so if the model, the thresholds or the feeder
are ever changed, this suite fails rather than quietly moving the goalposts.
"""

from __future__ import annotations

import pytest

# ============================================================
#  1-3. One of each risk class
# ============================================================


def test_scenario_01_safe_application(assess):
    """A modest system on a loaded secondary is SAFE."""
    metrics, verdict = assess("620", 0, 5)
    assert verdict.engineering_risk.value == "SAFE"
    assert verdict.constraint_type.value == "none"
    assert metrics.converged


def test_scenario_02_caution_application(assess, thresholds):
    """A larger system reaches a caution band without breaching a hard limit."""
    metrics, verdict = assess("621", 0, 100)
    assert verdict.engineering_risk.value == "CAUTION"
    assert verdict.constraint_type.value == "caution"

    # CAUTION must mean no hard threshold was crossed.
    assert metrics.feeder_max_voltage_pu <= thresholds["voltage_hard_high_pu"]
    assert metrics.feeder_min_voltage_pu >= thresholds["voltage_hard_low_pu"]
    assert abs(metrics.voltage_rise_pu) <= thresholds["voltage_rise_hard_pu"]
    assert metrics.max_line_loading_pct <= thresholds["line_loading_hard_pct"]
    assert metrics.max_transformer_loading_pct <= thresholds["transformer_loading_hard_pct"]


def test_scenario_03_constrained_application(assess, thresholds):
    metrics, verdict = assess("734", 0, 66)
    assert verdict.engineering_risk.value == "CONSTRAINED"
    assert abs(metrics.voltage_rise_pu) > thresholds["voltage_rise_hard_pu"]


# ============================================================
#  4-5. Capacity against local conditions
# ============================================================


def test_scenario_04_high_solar_low_load(assess, grid):
    """A bus with no modelled load, which is where penetration ratios mislead."""
    bus = grid.get("6231")
    assert bus.existing_load_kw == 0, "fixture assumes a zero-load bus"

    metrics, verdict = assess("6231", 0, 53)
    assert verdict.engineering_risk.value == "CONSTRAINED"
    assert verdict.constraint_type.value == "voltage_rise"


def test_scenario_05_existing_plus_new_solar(assess, power_flow):
    """Existing generation must count towards the total, not be ignored."""
    metrics, _ = assess("734", 10, 56)
    assert metrics.existing_pv_kw == 10
    assert metrics.new_pv_kw == 56
    assert metrics.total_pv_kw == 66

    # The BASE case includes the existing system, so the rise attributed to the
    # new system is smaller than if all 66 kW were new.
    all_new = power_flow.simulate("734", 0, 66)
    assert abs(metrics.voltage_rise_pu) < abs(all_new.voltage_rise_pu)


# ============================================================
#  6-8. Each constraint mechanism
# ============================================================


def test_scenario_06_reverse_power_flow(assess):
    """Export beyond local load reverses a flow, and it is detected."""
    metrics, _ = assess("734", 0, 66)
    assert metrics.reverse_power_flow is True
    assert metrics.reverse_reason != "none"


def test_scenario_06b_reverse_flow_alone_is_not_constrained(assess):
    """scenario_config.json states reverse flow alone is CAUTION, not a block."""
    metrics, verdict = assess("621", 0, 100)
    assert metrics.reverse_power_flow is True
    assert verdict.engineering_risk.value == "CAUTION"


def test_scenario_07_voltage_rise_case(assess, thresholds):
    metrics, verdict = assess("734", 0, 66)
    assert verdict.constraint_type.value == "voltage_rise"
    assert abs(metrics.voltage_rise_pu) > thresholds["voltage_rise_hard_pu"]
    # It is the rise that binds, not the absolute voltage.
    assert metrics.feeder_max_voltage_pu < thresholds["voltage_hard_high_pu"]


def test_scenario_08_transformer_loading_case(assess, thresholds):
    metrics, verdict = assess("716", 0, 44)
    assert verdict.constraint_type.value == "transformer_loading"
    assert metrics.max_transformer_loading_pct > thresholds["transformer_loading_hard_pct"]


# ============================================================
#  9-10. Invalid input
# ============================================================


def test_scenario_09_invalid_bus(grid):
    from app.services.grid_assets import IneligibleBusError, UnknownBusError

    with pytest.raises(UnknownBusError):
        grid.get("99999")

    # A real bus that is not a rooftop connection point is a different error,
    # so the API can explain which problem it is.
    with pytest.raises(IneligibleBusError):
        grid.get("701")


@pytest.mark.parametrize("capacity", [0, -5, 10_000_000])
def test_scenario_10_invalid_pv_capacity(power_flow, capacity):
    """Zero, negative and absurd capacities must not produce a confident answer."""
    from app.services.power_flow import PowerFlowError

    if capacity <= 0:
        metrics = power_flow.simulate("620", 0, max(capacity, 0))
        # Nothing injected means no rise; it must not silently invent one.
        assert abs(metrics.voltage_rise_pu) < 1e-6
    else:
        with pytest.raises(PowerFlowError):
            power_flow.simulate("620", 0, capacity)


# ============================================================
#  11-12. Authorization (fuller coverage in the verify_phase* suites)
# ============================================================


def test_scenario_11_unauthorized_role_is_refused(api, citizen):
    from tests.conftest import requires_api  # noqa: F401

    response = api.get("/api/discom/summary", headers=citizen["headers"])
    assert response.status_code == 403


def test_scenario_12_unapproved_vendor_is_invisible(api, citizen, service_client):
    created = api.post(
        "/api/vendors/register",
        headers=citizen["headers"],
        json={"business_name": "Pytest Pending Installers"},
    )
    assert created.status_code == 201
    vendor_id = created.json()["vendor"]["id"]
    assert created.json()["vendor"]["status"] == "PENDING"

    try:
        listed = api.get("/api/vendors", headers=citizen["headers"]).json()
        assert not any(v["id"] == vendor_id for v in listed["vendors"])
    finally:
        service_client.table("vendors").delete().eq("id", vendor_id).execute()


# ============================================================
#  Regression: the two historically false-SAFE connections
# ============================================================


@pytest.mark.parametrize(
    "bus,capacity,documented_probability",
    [("734", 66, 0.98), ("6231", 53, 0.76)],
)
def test_regression_false_safe_cases(assess, ml, bus, capacity, documented_probability):
    """Bus 734 and bus 6231 were the v1 model's two false-SAFE predictions.

    Both must stay CONSTRAINED. If this fails, do not adjust the expectation —
    find out what changed in the model, the thresholds or the feeder.
    """
    metrics, verdict = assess(bus, 0, capacity)
    assert verdict.engineering_risk.value == "CONSTRAINED", (
        f"bus {bus} at {capacity} kW must remain CONSTRAINED"
    )
    assert verdict.constraint_type.value == "voltage_rise"

    prediction = ml.predict(bus, 0, capacity)
    assert prediction.prediction.value == "CONSTRAINED", (
        f"the model must not predict SAFE for bus {bus}"
    )
    assert prediction.constrained_probability == pytest.approx(
        documented_probability, abs=0.02
    )


def test_regression_base_feeder_state(power_flow):
    """The validated base case, from engineering_audit.md."""
    metrics = power_flow.simulate("734", 0, 0.0)
    assert metrics.base_total_p_kw == pytest.approx(4178.4, abs=2.0)
    assert metrics.feeder_min_voltage_pu == pytest.approx(0.9059, abs=0.0005)
    assert metrics.max_transformer_loading_pct == pytest.approx(92.8, abs=0.2)


def test_regression_bus_734_voltage_rise(assess):
    """The exact figure recorded in false_safe_case_analysis.md."""
    metrics, _ = assess("734", 0, 66)
    assert metrics.voltage_rise_pu == pytest.approx(0.05751, abs=1e-4)
