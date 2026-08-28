# ============================================================
#  SolarGrid AI — backend
#
#  Python 3.12 is deliberate. suryagrid_model_v2.pkl was serialized by
#  scikit-learn 1.3.2, which requires numpy < 2; pandapower 3.4.0 is the newest
#  release that still resolves against numpy 1.26. See requirements.txt.
# ============================================================
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build tools for the scientific wheels, removed again to keep the image small.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt \
    && apt-get purge -y build-essential && apt-get autoremove -y

# The application code.
COPY backend/ /app/backend/

# The engineering artifacts. The model and the feeder network are the product;
# without them the API refuses to start rather than serving empty answers.
COPY suryagrid_model_v2.pkl enriched_features.json feeder_network.json \
     scenario_config.json valid_pv_buses.csv excluded_buses.csv \
     electrical_features.csv pv_dataset_enriched_augmented.csv \
     ml_dataset_test_enriched_v2.csv /app/

ENV ARTIFACTS_DIR=/app \
    PYTHONPATH=/app/backend

# Run as a non-root user.
RUN useradd --create-home --uid 10001 solargrid && chown -R solargrid /app
USER solargrid

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# One worker by default: the rate limiter keeps its counters in process, so
# scaling workers multiplies the effective limit until a shared store is added.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--app-dir", "/app/backend"]
