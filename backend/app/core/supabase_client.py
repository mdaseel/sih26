"""Supabase client factories.

Two clients, two very different privilege levels:

    get_anon_client()          -- public key, RLS enforced. Safe.
    get_service_client()       -- service-role key, RLS BYPASSED. Backend only.

Rule 10: the service-role key must never reach the frontend. It is read from
the environment here and never returned, logged, or serialized into any API
response. Use the service client only for writes the database deliberately
forbids to clients: simulation_results, risk_assessments, grid_assets,
audit_logs.

Connection hygiene
------------------
supabase-py builds every sub-client on an httpx session with http2=True, and
we hold those sessions open for the life of the process. Supabase's edge hangs
up idle keep-alive connections after a short while; httpx notices that for
HTTP/1.1 (before reusing a pooled connection it checks whether the socket has
gone readable, which for an idle connection means the server closed it) but an
HTTP/2 connection is only dropped once its own keepalive timer expires. So a
connection the far end has already closed gets handed out again and the next
query dies with RemoteProtocolError: Server disconnected -- a 500 on a request
that was never actually attempted.

_harden() closes that window on every client this module hands out:

  * pooled connections expire well before the edge drops them, and
  * if one dies anyway, the request is replayed on a fresh connection.

Only the transport is replaced. Base URL, headers, auth and timeouts are
whatever supabase-py configured, so query behaviour is unchanged.
"""

from __future__ import annotations

import logging
import time
from functools import lru_cache

import httpx
from supabase import Client, create_client

from app.core.config import get_settings

logger = logging.getLogger("solargrid.supabase")

# Drop pooled connections before Supabase's edge does.
KEEPALIVE_EXPIRY_SECONDS = 20.0

# One original attempt plus this many replays.
MAX_RETRIES = 2

# Connection-level failures: the request did not get an answer, as opposed to
# getting one we dislike. ReadTimeout is deliberately absent -- a timeout means
# PostgREST may well have run the statement.
_RETRYABLE = (
    httpx.RemoteProtocolError,
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadError,
    httpx.WriteError,
)

# Failures raised before any byte reached the server, so replaying them cannot
# duplicate a write.
_NEVER_SENT = (httpx.ConnectError, httpx.ConnectTimeout)

# Everything else is replayed only when the method has no side effect. A POST
# that fails with "Server disconnected" has almost certainly not been executed,
# but "almost certainly" is not good enough to risk a duplicate insert.
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class SupabaseNotConfigured(RuntimeError):
    """Raised when Supabase credentials are absent from the environment."""


class _ReconnectingTransport(httpx.BaseTransport):
    """Replays a request whose connection died underneath it."""

    def __init__(self, inner: httpx.BaseTransport) -> None:
        self._inner = inner

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(MAX_RETRIES + 1):
            try:
                return self._inner.handle_request(request)
            except _RETRYABLE as exc:
                replayable = request.method in _SAFE_METHODS or isinstance(
                    exc, _NEVER_SENT
                )
                if not replayable or attempt == MAX_RETRIES:
                    raise
                logger.warning(
                    "supabase connection lost (%s: %s) on %s %s - retrying (%d/%d)",
                    type(exc).__name__,
                    exc,
                    request.method,
                    request.url,
                    attempt + 1,
                    MAX_RETRIES,
                )
                time.sleep(0.05 * (attempt + 1))
        raise AssertionError("unreachable")  # pragma: no cover

    def close(self) -> None:
        self._inner.close()


def _resilient_session(session: httpx.Client) -> None:
    """Swap in a transport that expires idle connections early and retries."""
    if getattr(session, "_solargrid_hardened", False):
        return
    previous = session._transport
    session._transport = _ReconnectingTransport(
        httpx.HTTPTransport(
            http2=True,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=KEEPALIVE_EXPIRY_SECONDS,
            ),
        )
    )
    session._solargrid_hardened = True
    try:
        previous.close()
    except Exception:  # noqa: BLE001 - a fresh pool has nothing to close
        pass


def _harden(client: Client, *, storage: bool = False) -> Client:
    """Apply the resilient transport to the sub-clients we actually use.

    postgrest and storage are lazily built properties, so touching them here is
    what creates them; functions and realtime are left alone because nothing in
    this backend calls them. A supabase-py release that renames an attribute
    degrades to the library's own behaviour rather than breaking start-up.
    """
    sessions = [("postgrest", lambda: client.postgrest.session)]
    if storage:
        sessions.append(("storage", lambda: client.storage.session))
    sessions.append(("auth", lambda: client.auth._http_client))

    for name, get_session in sessions:
        try:
            _resilient_session(get_session())
        except AttributeError:
            logger.warning(
                "could not harden the supabase %s session; leaving it as built", name
            )
    return client


@lru_cache
def get_anon_client() -> Client:
    """Client constrained by Row Level Security. Use for user-scoped reads."""
    s = get_settings()
    if not s.supabase_configured:
        raise SupabaseNotConfigured(
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set. Copy .env.example to .env."
        )
    return _harden(create_client(s.project_url, s.supabase_anon_key))


@lru_cache
def get_service_client() -> Client:
    """Privileged client that BYPASSES RLS. Never expose to a request handler
    that echoes raw results to an untrusted caller without authorization."""
    s = get_settings()
    if not s.service_role_configured:
        raise SupabaseNotConfigured(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set for privileged writes."
        )
    return _harden(
        create_client(s.project_url, s.supabase_service_role_key), storage=True
    )


@lru_cache(maxsize=32)
def _build_user_client(access_token: str) -> Client:
    s = get_settings()
    client = create_client(s.project_url, s.supabase_anon_key)
    client.postgrest.auth(access_token)
    return _harden(client)


def get_user_client(access_token: str) -> Client:
    """Client acting AS a specific signed-in user, so RLS applies to them.

    This is the correct client for reading or writing on a user's behalf: the
    database, not the application, decides what they may touch.

    Cached per token, and bounded: building one per request left a connection
    pool open to Supabase for every call, which is both a leak and a good way
    to have the edge start dropping connections on us. A token belongs to one
    user for its whole lifetime, so reusing the client cannot mix identities;
    an expired token is refused by Supabase exactly as it would be on a client
    built fresh.
    """
    s = get_settings()
    if not s.supabase_configured:
        raise SupabaseNotConfigured("SUPABASE_URL and SUPABASE_ANON_KEY must be set.")
    return _build_user_client(access_token)
