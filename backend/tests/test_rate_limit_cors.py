"""Rate limiting must not fire on the browser's permission checks.

A CORS preflight carries no Authorization header, so it was counted against
the small anonymous IP bucket: the vendor dashboard spent its whole allowance
on preflights and then got 429s on OPTIONS, which blocks the real request
before it is ever sent.

These run against the real app object. TestClient is used without its context
manager on purpose, so the lifespan (model + feeder network) never loads.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import ANONYMOUS_LIMIT, limiter
from app.main import app

ORIGIN = get_settings().cors_origin_list[0]
PREFLIGHT = {
    "Origin": ORIGIN,
    "Access-Control-Request-Method": "GET",
    "Access-Control-Request-Headers": "authorization",
}


@pytest.fixture
def client():
    limiter.reset()
    yield TestClient(app)
    limiter.reset()


def test_preflights_are_never_rate_limited(client):
    """Well past the anonymous allowance, and every one still answers."""
    for _ in range(ANONYMOUS_LIMIT.requests * 2):
        response = client.options("/api/vendor/summary", headers=PREFLIGHT)
        assert response.status_code == 200, response.text
        assert response.headers["access-control-allow-origin"] == ORIGIN


def test_preflights_do_not_consume_a_callers_allowance(client):
    """A page that preflights seven endpoints must still have its full budget."""
    for _ in range(ANONYMOUS_LIMIT.requests, 0, -1):
        client.options("/api/vendor/summary", headers=PREFLIGHT)

    response = client.get("/api/vendor/summary", headers={"Origin": ORIGIN})
    assert response.status_code != 429


def test_a_real_flood_is_still_limited_and_the_429_survives_cors(client):
    """The limit itself is unchanged -- and the browser can now read the 429."""
    statuses = [
        client.get("/api/vendor/summary", headers={"Origin": ORIGIN}).status_code
        for _ in range(ANONYMOUS_LIMIT.requests + 5)
    ]
    assert 429 in statuses

    throttled = client.get("/api/vendor/summary", headers={"Origin": ORIGIN})
    assert throttled.status_code == 429
    assert throttled.headers["access-control-allow-origin"] == ORIGIN
    assert "Retry-After" in throttled.headers


def test_health_is_never_throttled(client):
    for _ in range(ANONYMOUS_LIMIT.requests + 5):
        client.get("/api/vendor/summary", headers={"Origin": ORIGIN})

    assert client.get("/health").status_code == 200
