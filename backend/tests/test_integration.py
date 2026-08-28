"""Integration tests: the ML layer, the power-flow layer, the API and RLS.

The label-replay test is the one that matters most. It pushes rows from the
existing dataset back through the running services and requires the recomputed
label to equal the stored one. If it ever fails, the application has drifted
away from the data the model was trained on.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from tests.conftest import requires_api, requires_supabase

# ============================================================
#  ML integration
# ============================================================


def test_model_is_the_v2_bundle(ml):
    from app.core import paths

    assert len(ml.feature_names) == 18
    declared = json.loads(paths.MODEL_FEATURES.read_text())["input_features_enriched"]
    assert declared == ml.feature_names, "the pickle and the feature contract disagree"


def test_features_are_assembled_without_simulation(ml, grid):
    """Every model input must come from the feeder database and the request."""
    bus = grid.get("734")
    features = ml.build_features(bus, 0, 66)

    assert len(features) == 18
    assert isinstance(features["pv_bus"], int), (
        "pv_bus must be int: the fitted encoder holds int64 categories, and a "
        "string silently one-hots to all zeros"
    )
    for leaked in ("pv_max_voltage_pu", "delta_pv_bus_voltage_pu", "label", "constraint_type"):
        assert leaked not in features, f"{leaked} would be target leakage"


def test_assembled_features_match_the_stored_dataset(ml, grid):
    from app.core import paths

    df = pd.read_csv(paths.DATASET_CURRENT, dtype={"pv_bus": str})
    stored = df[(df.pv_bus == "734") & (df.new_pv_kw == 66) & (df.existing_pv_kw == 0)].iloc[0]
    features = ml.build_features(grid.get("734"), 0, 66)

    for name, value in features.items():
        if isinstance(value, (int, float)) and name != "pv_bus":
            assert float(value) == pytest.approx(float(stored[name]), abs=1e-6), name


def test_zero_load_penetration_artifact_is_preserved(ml, grid):
    """The model was trained with total/1.0 when a bus has no load.

    'Fixing' this would move every prediction away from validated behaviour.
    """
    bus = grid.get("6231")
    assert bus.existing_load_kw == 0
    assert ml.build_features(bus, 0, 53)["pv_penetration_ratio"] == 53.0


# ============================================================
#  Power-flow integration
# ============================================================


def test_power_flow_uses_the_validated_network(power_flow):
    summary = power_flow.network_summary()
    assert summary["network_file"] == "feeder_network.json", (
        "feeder_network_ldc.json is the abandoned LDC experiment"
    )
    assert summary["buses"] == 114
    assert summary["transformers"] == 30
    assert "FIXED" in summary["regulator_handling"]


def test_label_replay_matches_the_training_data(power_flow, risk):
    """The core guarantee: recomputed labels equal the stored labels."""
    from app.core import paths

    sample = pd.read_csv(paths.DATASET_CURRENT, dtype={"pv_bus": str}).sample(
        40, random_state=2026
    )

    mismatches = []
    for _, row in sample.iterrows():
        metrics = power_flow.simulate(row.pv_bus, float(row.existing_pv_kw), float(row.new_pv_kw))
        verdict = risk.evaluate(metrics)
        if verdict.engineering_risk.value != row.label:
            mismatches.append(
                f"bus {row.pv_bus} ex={row.existing_pv_kw} new={row.new_pv_kw}: "
                f"stored {row.label}, recomputed {verdict.engineering_risk.value}"
            )

    assert not mismatches, "label drift:\n" + "\n".join(mismatches[:5])


def test_thresholds_come_from_the_config_file(grid):
    """No threshold may be redefined in application code."""
    from app.core import paths

    config = json.loads(paths.SCENARIO_CONFIG.read_text())["thresholds"]
    live = grid.thresholds()
    for key, entry in config.items():
        if isinstance(entry, dict) and "value" in entry and key in live:
            assert live[key] == entry["value"], key


def test_group_of_one_matches_the_single_bus_path(power_flow):
    single = power_flow.simulate("734", 0, 30)
    group = power_flow.simulate_group("solo", {"734": 0.0}, {"734": 30.0})
    assert group.voltage_rise_pu == pytest.approx(single.voltage_rise_pu, abs=1e-9)
    assert group.max_transformer_loading_pct == pytest.approx(
        single.max_transformer_loading_pct, abs=1e-9
    )


def test_hosting_capacity_is_bracketed_by_simulation(hosting, assess):
    """The reported capacity is acceptable; just above it is not."""
    capacity = hosting.capacity_for("734").hosting_capacity_kw

    _, at = assess("734", 0, capacity)
    assert at.engineering_risk.value != "CONSTRAINED"

    _, over = assess("734", 0, capacity + 3)
    assert over.engineering_risk.value == "CONSTRAINED"


# ============================================================
#  API integration
# ============================================================


@requires_api
def test_health_reports_subsystem_state(api):
    body = api.get("/health").json()
    assert body["status"] == "ok"
    assert body["artifacts_present"] is True
    assert "Synthetic" in body["data_class"]


@requires_api
def test_assess_endpoint_matches_the_service(api, citizen, assess):
    response = api.post(
        "/api/assess",
        headers=citizen["headers"],
        json={"pv_bus": "734", "existing_pv_kw": 0, "new_pv_kw": 66},
    )
    assert response.status_code == 200
    body = response.json()

    metrics, verdict = assess("734", 0, 66)
    assert body["engineering"]["engineering_risk"] == verdict.engineering_risk.value
    assert body["metrics"]["voltage_rise_pu"] == pytest.approx(metrics.voltage_rise_pu, abs=1e-6)
    assert body["authority"] == "power_flow"


@requires_api
def test_stored_assessment_is_read_not_recomputed(api, citizen, application, service_client):
    before = len(
        (
            service_client.table("simulation_results")
            .select("id")
            .eq("application_id", application["id"])
            .execute()
        ).data
        or []
    )

    for _ in range(3):
        response = api.get(
            f"/api/applications/{application['id']}/assessment", headers=citizen["headers"]
        )
        assert response.status_code == 200

    after = len(
        (
            service_client.table("simulation_results")
            .select("id")
            .eq("application_id", application["id"])
            .execute()
        ).data
        or []
    )
    assert after == before, "reading an assessment must not create new simulations"


@requires_api
def test_invalid_inputs_are_rejected(api, citizen):
    for payload, expected in [
        ({"pv_bus": "99999", "new_pv_kw": 5}, 404),
        ({"pv_bus": "701", "new_pv_kw": 5}, 422),
        ({"pv_bus": "734", "new_pv_kw": -5}, 422),
        ({"pv_bus": "not-a-bus", "new_pv_kw": 5}, 422),
    ]:
        response = api.post("/api/assess", headers=citizen["headers"], json=payload)
        assert response.status_code == expected, payload


# ============================================================
#  Authentication and RLS
# ============================================================


@requires_api
@pytest.mark.parametrize(
    "path", ["/api/applications", "/api/map", "/api/discom/summary", "/api/scheme"]
)
def test_unauthenticated_access_is_refused(api, path):
    assert api.get(path).status_code in (401, 403)


@requires_api
def test_forged_tokens_are_refused(api):
    # An empty bearer value is not tested here: it is an illegal HTTP header,
    # so the client refuses to send it and the server never sees the request.
    # The missing-header case is covered by the unauthenticated test above.
    for token in ["not-a-jwt", "a.b.c", "eyJhbGciOiJIUzI1NiJ9.e30.forged"]:
        response = api.get("/api/applications", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401, token

    assert api.get("/api/applications", headers={"Authorization": "Bearer"}).status_code == 401


@requires_supabase
def test_rls_blocks_writing_engineering_results(citizen, application, service_client):
    from app.core.supabase_client import get_anon_client

    client = get_anon_client()
    client.postgrest.auth(citizen["token"])

    for table, payload in [
        ("risk_assessments", {"engineering_risk": "SAFE"}),
        ("simulation_results", {"voltage_rise_pu": 0.0}),
    ]:
        try:
            result = client.table(table).update(payload).eq("application_id", application["id"]).execute()
            assert not result.data, f"{table} must not be client-writable"
        except Exception as exc:  # noqa: BLE001 - a refusal is the expected outcome
            assert "row-level security" in str(exc).lower() or "permission" in str(exc).lower() or "pgrst" in str(exc).lower()


@requires_supabase
def test_rls_scopes_applications_to_their_owner(make_user, application):
    from app.core.supabase_client import get_anon_client

    stranger = make_user("CITIZEN")
    client = get_anon_client()
    client.postgrest.auth(stranger["token"])

    rows = client.table("solar_applications").select("id").eq("id", application["id"]).execute().data
    assert not rows, "another citizen must not see this application"
