"""Supabase client factories.

Two clients, two very different privilege levels:

    get_anon_client()          -- public key, RLS enforced. Safe.
    get_service_client()       -- service-role key, RLS BYPASSED. Backend only.

Rule 10: the service-role key must never reach the frontend. It is read from
the environment here and never returned, logged, or serialized into any API
response. Use the service client only for writes the database deliberately
forbids to clients: simulation_results, risk_assessments, grid_assets,
audit_logs.
"""

from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


class SupabaseNotConfigured(RuntimeError):
    """Raised when Supabase credentials are absent from the environment."""


@lru_cache
def get_anon_client() -> Client:
    """Client constrained by Row Level Security. Use for user-scoped reads."""
    s = get_settings()
    if not s.supabase_configured:
        raise SupabaseNotConfigured(
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set. Copy .env.example to .env."
        )
    return create_client(s.project_url, s.supabase_anon_key)


@lru_cache
def get_service_client() -> Client:
    """Privileged client that BYPASSES RLS. Never expose to a request handler
    that echoes raw results to an untrusted caller without authorization."""
    s = get_settings()
    if not s.service_role_configured:
        raise SupabaseNotConfigured(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set for privileged writes."
        )
    return create_client(s.project_url, s.supabase_service_role_key)


def get_user_client(access_token: str) -> Client:
    """Client acting AS a specific signed-in user, so RLS applies to them.

    This is the correct client for reading or writing on a user's behalf: the
    database, not the application, decides what they may touch.
    """
    s = get_settings()
    if not s.supabase_configured:
        raise SupabaseNotConfigured("SUPABASE_URL and SUPABASE_ANON_KEY must be set.")
    client = create_client(s.project_url, s.supabase_anon_key)
    client.postgrest.auth(access_token)
    return client
