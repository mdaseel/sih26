"""The reconnect guard around the Supabase httpx sessions.

Supabase's edge closes idle keep-alive connections, and an HTTP/2 pool hands
the dead connection out again -- which surfaced as
`RemoteProtocolError: Server disconnected` 500s on vendor reads. These tests
pin the two halves of the rule: a read is replayed, a write is not (unless the
connection was never established, in which case nothing could have run).

No Supabase credentials and no network are needed.
"""

from __future__ import annotations

import httpx
import pytest

from app.core.supabase_client import MAX_RETRIES, _ReconnectingTransport


class FlakyTransport(httpx.BaseTransport):
    """Raises `error` for the first `failures` calls, then answers 200."""

    def __init__(self, error: Exception, failures: int) -> None:
        self.error = error
        self.remaining = failures
        self.attempts = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.attempts += 1
        if self.remaining > 0:
            self.remaining -= 1
            raise self.error
        return httpx.Response(200, json={"ok": True})


def _request(method: str = "GET") -> httpx.Request:
    return httpx.Request(method, "https://example.supabase.co/rest/v1/vendors")


def test_dropped_connection_on_a_read_is_replayed():
    inner = FlakyTransport(httpx.RemoteProtocolError("Server disconnected"), failures=1)
    response = _ReconnectingTransport(inner).handle_request(_request())

    assert response.status_code == 200
    assert inner.attempts == 2


def test_retries_are_bounded_and_the_error_still_surfaces():
    inner = FlakyTransport(httpx.RemoteProtocolError("Server disconnected"), failures=99)

    with pytest.raises(httpx.RemoteProtocolError):
        _ReconnectingTransport(inner).handle_request(_request())

    assert inner.attempts == MAX_RETRIES + 1


def test_a_write_is_not_replayed_once_the_request_may_have_been_sent():
    """A disconnected POST could have been executed; a duplicate insert is
    worse than a 500."""
    inner = FlakyTransport(httpx.RemoteProtocolError("Server disconnected"), failures=1)

    with pytest.raises(httpx.RemoteProtocolError):
        _ReconnectingTransport(inner).handle_request(_request("POST"))

    assert inner.attempts == 1


def test_a_write_is_replayed_when_the_connection_never_opened():
    inner = FlakyTransport(httpx.ConnectError("connection refused"), failures=1)
    response = _ReconnectingTransport(inner).handle_request(_request("POST"))

    assert response.status_code == 200
    assert inner.attempts == 2


def test_a_read_timeout_is_not_retried():
    """The statement may already be running on the server."""
    inner = FlakyTransport(httpx.ReadTimeout("timed out"), failures=1)

    with pytest.raises(httpx.ReadTimeout):
        _ReconnectingTransport(inner).handle_request(_request())

    assert inner.attempts == 1
