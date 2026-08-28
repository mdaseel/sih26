"""Rate limiting, security headers, and error handling.

Rate limiting is in-process
---------------------------
The limiter below keeps its counters in memory, which is honest for a single
uvicorn worker and wrong for several. Two workers means roughly twice the
configured allowance, and a restart clears every counter. That is an acceptable
prototype trade-off, not a solved problem: a multi-worker deployment needs a
shared store (Redis) behind the same interface. The limitation is reported by
/health rather than left for someone to discover under load.

Why the power-flow routes get their own bucket
----------------------------------------------
An assessment costs a real power flow — tens of milliseconds of CPU each, and a
what-if sweep is several. Those endpoints are the ones worth protecting; a
listing endpoint is not.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("solargrid.security")


# ============================================================
#  Rate limiting
# ============================================================
@dataclass(frozen=True)
class Limit:
    requests: int
    window_seconds: int

    def describe(self) -> str:
        return f"{self.requests} per {self.window_seconds}s"


# Simulation-backed endpoints: each call costs real CPU.
EXPENSIVE_LIMIT = Limit(requests=30, window_seconds=60)
# Everything else authenticated.
DEFAULT_LIMIT = Limit(requests=240, window_seconds=60)
# Unauthenticated surface, which is small on purpose.
ANONYMOUS_LIMIT = Limit(requests=60, window_seconds=60)

EXPENSIVE_PREFIXES = (
    "/api/assess",
    "/api/twin",
    "/api/discom/what-if",
    "/api/grid/hosting-capacity",
)
EXPENSIVE_SUFFIXES = ("/assess",)


class SlidingWindowLimiter:
    """Sliding-window counter, one deque of timestamps per key."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: Limit) -> tuple[bool, int, float]:
        """Returns (allowed, remaining, retry_after_seconds)."""
        now = time.monotonic()
        cutoff = now - limit.window_seconds
        hits = self._hits[key]

        while hits and hits[0] < cutoff:
            hits.popleft()

        if len(hits) >= limit.requests:
            retry_after = max(0.0, hits[0] + limit.window_seconds - now)
            return False, 0, retry_after

        hits.append(now)
        return True, limit.requests - len(hits), 0.0

    def reset(self) -> None:
        self._hits.clear()


limiter = SlidingWindowLimiter()


def _client_key(request: Request) -> tuple[str, bool]:
    """Identify the caller.

    Prefers the bearer token so a limit follows the account rather than the
    network address. Only a short fingerprint of the token is kept — never the
    token itself, which would put credentials in memory keyed by string.
    """
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]
        return f"tok:{hash(token) & 0xFFFFFFFF:08x}", True

    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
    return f"ip:{ip}", False


def _limit_for(path: str, authenticated: bool) -> Limit:
    if any(path.startswith(p) for p in EXPENSIVE_PREFIXES) or any(
        path.endswith(s) for s in EXPENSIVE_SUFFIXES
    ):
        return EXPENSIVE_LIMIT
    return DEFAULT_LIMIT if authenticated else ANONYMOUS_LIMIT


# ============================================================
#  Middleware and handlers
# ============================================================
def install_security(app: FastAPI) -> None:
    """Attach rate limiting, security headers and error handling."""

    @app.middleware("http")
    async def rate_limit_and_headers(request: Request, call_next: Callable):
        path = request.url.path

        # Health must answer even under a flood, so a monitor can still see the
        # service is alive rather than being throttled into looking dead.
        if path != "/health":
            key, authenticated = _client_key(request)
            limit = _limit_for(path, authenticated)
            allowed, remaining, retry_after = limiter.check(f"{key}:{limit.requests}", limit)

            if not allowed:
                log.warning("rate limit hit: %s %s", key, path)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many requests. Slow down and try again shortly.",
                        "limit": limit.describe(),
                        "retry_after_seconds": round(retry_after, 1),
                    },
                    headers={"Retry-After": str(int(retry_after) + 1)},
                )
        else:
            remaining, limit = 0, DEFAULT_LIMIT

        response = await call_next(request)

        if path != "/health":
            response.headers["X-RateLimit-Limit"] = str(limit.requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)

        # Cheap defensive headers. This is a JSON API, so the browser should
        # never be sniffing types, framing it, or leaking referrers.
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Deliberate, already-safe messages pass through unchanged.
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        # Field-level detail is useful and safe; the raw input is not echoed
        # back, so a malformed payload cannot be reflected to another reader.
        errors = [
            {
                "field": ".".join(str(p) for p in e.get("loc", [])[1:]) or "body",
                "message": e.get("msg", "invalid"),
                "type": e.get("type", "value_error"),
            }
            for e in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errors})

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        """Anything unexpected.

        The real exception goes to the server log with a reference; the client
        gets the reference and nothing else. Stack traces, driver messages and
        SQL fragments have all been known to carry schema details or
        credentials, so none of it crosses the boundary.
        """
        reference = uuid.uuid4().hex[:12]
        log.exception("unhandled error [%s] %s %s", reference, request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal error occurred.",
                "reference": reference,
                "hint": "Quote this reference when reporting the problem.",
            },
        )


def rate_limit_status() -> dict[str, object]:
    return {
        "strategy": "in-process sliding window",
        "expensive_endpoints": EXPENSIVE_LIMIT.describe(),
        "authenticated_default": DEFAULT_LIMIT.describe(),
        "anonymous": ANONYMOUS_LIMIT.describe(),
        "limitation": (
            "Counters are per-process. With multiple workers the effective limit "
            "multiplies, and a restart clears them. Use a shared store for "
            "multi-worker deployments."
        ),
    }
