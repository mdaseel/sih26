"""SolarGrid AI — FastAPI application.

The model and the feeder network are loaded once at startup, not per request:
unpickling the forest and parsing the network JSON are the expensive parts,
while a power flow itself is ~50 ms.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.routes_discom import router as discom_router
from app.api.routes_scheme import router as scheme_router
from app.api.routes_vendor_portal import router as vendor_portal_router
from app.api.routes_vendors import router as vendors_router
from app.core import paths
from app.core.config import get_settings
from app.core.security import install_security, rate_limit_status

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("solargrid")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    log.info("SolarGrid AI starting: %s", settings.describe())

    missing = paths.missing_artifacts()
    if missing:
        # Without the model or the network there is no product — fail loudly
        # rather than serving an API that cannot answer anything.
        raise RuntimeError(f"Missing required engineering artifacts: {missing}")

    from app.services.grid_assets import get_grid_asset_service
    from app.services.ml_prediction import get_ml_service
    from app.services.power_flow import get_power_flow_service

    grid = get_grid_asset_service()
    ml = get_ml_service()
    pf = get_power_flow_service()

    log.info("Model loaded: %s (%d features)", paths.MODEL_V2.name, len(ml.feature_names))
    log.info("Network loaded: %s", pf.network_summary())
    log.info("PV-eligible buses: %d", len(grid.eligible_bus_ids()))

    if not settings.supabase_configured:
        log.warning(
            "Supabase is not configured — engineering endpoints work, "
            "persistence and authenticated routes will return 503."
        )

    yield
    log.info("SolarGrid AI shutting down")


app = FastAPI(
    title="SolarGrid AI",
    version="0.2.0",
    description=(
        "Rooftop solar hosting-capacity screening. An ML model pre-screens the "
        "request; a deterministic power flow verifies it. The power flow is the "
        "authority. Grid data is the synthetic IEEE Comprehensive Test Feeder."
    ),
    lifespan=lifespan,
)

settings = get_settings()

# Order matters, and it is the reverse of the reading order: the LAST
# middleware added is the outermost one. CORS must be outside the rate limiter
# so that a 429 -- which the limiter returns without ever calling downstream --
# still carries Access-Control-Allow-Origin. Otherwise the browser discards it
# as a CORS failure and the frontend cannot tell "slow down" from "backend is
# broken".
install_security(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)
app.include_router(discom_router)
app.include_router(vendors_router)
app.include_router(vendor_portal_router)
app.include_router(scheme_router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, Any]:
    """Liveness plus a report of which subsystems are actually usable."""
    s = get_settings()
    return {
        "status": "ok",
        "artifacts_present": not paths.missing_artifacts(),
        "supabase_configured": s.supabase_configured,
        "persistence_available": s.service_role_configured,
        "data_class": "Prototype • Synthetic Grid Data",
        "rate_limiting": rate_limit_status(),
    }
