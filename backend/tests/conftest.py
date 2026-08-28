"""Shared fixtures.

Engineering fixtures are session-scoped: loading the model and the network is
the expensive part, while a power flow itself is milliseconds.

Tests that need Supabase are skipped rather than failed when it is not
configured, so the engineering suite still runs on a machine with no database.
"""

from __future__ import annotations

import sys
import uuid
import warnings
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

warnings.filterwarnings("ignore")

BASE_URL = "http://127.0.0.1:8000"


# ============================================================
#  Engineering layer
# ============================================================
@pytest.fixture(scope="session")
def grid():
    from app.services.grid_assets import get_grid_asset_service

    return get_grid_asset_service()


@pytest.fixture(scope="session")
def power_flow():
    from app.services.power_flow import get_power_flow_service

    return get_power_flow_service()


@pytest.fixture(scope="session")
def risk():
    from app.services.risk_assessment import get_risk_service

    return get_risk_service()


@pytest.fixture(scope="session")
def ml():
    from app.services.ml_prediction import get_ml_service

    return get_ml_service()


@pytest.fixture(scope="session")
def hosting():
    from app.services.hosting_capacity import get_hosting_capacity_service

    return get_hosting_capacity_service()


@pytest.fixture(scope="session")
def thresholds(grid):
    return grid.thresholds()


@pytest.fixture(scope="session")
def assess(power_flow, risk):
    """Run one scenario and return (metrics, verdict)."""

    def _assess(bus: str, existing_kw: float, new_kw: float):
        metrics = power_flow.simulate(bus, existing_kw, new_kw)
        return metrics, risk.evaluate(metrics)

    return _assess


# ============================================================
#  Live stack
# ============================================================
def _supabase_ready() -> bool:
    try:
        from app.core.config import get_settings

        return get_settings().service_role_configured
    except Exception:  # noqa: BLE001
        return False


def _api_ready() -> bool:
    try:
        import httpx

        return httpx.get(f"{BASE_URL}/health", timeout=5).status_code == 200
    except Exception:  # noqa: BLE001
        return False


requires_supabase = pytest.mark.skipif(
    not _supabase_ready(), reason="Supabase is not configured"
)
requires_api = pytest.mark.skipif(
    not _api_ready(), reason=f"backend is not running at {BASE_URL}"
)


@pytest.fixture(scope="session")
def service_client():
    from app.core.supabase_client import get_service_client

    return get_service_client()


@pytest.fixture(scope="session")
def api():
    import httpx

    return httpx.Client(base_url=BASE_URL, timeout=180)


@pytest.fixture(scope="session")
def make_user(service_client):
    """Create throwaway accounts, removed when the session ends."""
    from app.core.supabase_client import get_anon_client

    created: list[str] = []

    def _make(role: str = "CITIZEN") -> dict:
        email = f"solargrid-pytest-{uuid.uuid4().hex[:8]}@example.com"
        password = f"Pytest!{uuid.uuid4().hex[:12]}"
        user = service_client.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        created.append(user.user.id)
        if role != "CITIZEN":
            service_client.table("profiles").update({"role": role}).eq(
                "id", user.user.id
            ).execute()
        token = get_anon_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        ).session.access_token
        return {
            "id": user.user.id,
            "email": email,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"},
        }

    yield _make

    for user_id in created:
        try:
            service_client.auth.admin.delete_user(user_id)
        except Exception:  # noqa: BLE001
            pass


@pytest.fixture
def citizen(make_user):
    return make_user("CITIZEN")


@pytest.fixture
def discom(make_user):
    return make_user("DISCOM")


@pytest.fixture
def application(api, citizen, service_client):
    """A submitted, assessed application. Removed afterwards."""
    created = api.post(
        "/api/applications",
        headers=citizen["headers"],
        json={
            "applicant_name": "Pytest Applicant",
            "pv_bus": "620",
            "existing_pv_kw": 0,
            "new_pv_kw": 5,
        },
    ).json()
    api.post(f"/api/applications/{created['id']}/assess", headers=citizen["headers"])

    yield created

    try:
        service_client.table("solar_applications").delete().eq("id", created["id"]).execute()
    except Exception:  # noqa: BLE001
        pass
