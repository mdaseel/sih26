"""Request dependencies: authentication and role resolution.

The bearer token is a Supabase JWT issued to the browser by Supabase Auth. The
backend does not mint or trust its own identity claims — it hands the token to
Supabase and uses whatever user comes back, then reads that user's role from
the profiles table with the service client.

Authorization decisions are made here AND enforced again by RLS. Two
independent layers, because either one alone is a single point of failure.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from app.core.config import get_settings
from app.core.supabase_client import SupabaseNotConfigured, get_anon_client
from app.db.service import db
from app.models.enums import UserRole


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str | None
    role: UserRole
    access_token: str

    @property
    def is_discom(self) -> bool:
        return self.role in (UserRole.DISCOM, UserRole.ADMIN)

    @property
    def is_admin(self) -> bool:
        return self.role is UserRole.ADMIN


def _bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ", 1)[1].strip()


async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    settings = get_settings()
    if not settings.supabase_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Supabase is not configured. Set SUPABASE_URL, SUPABASE_ANON_KEY and "
                "SUPABASE_SERVICE_ROLE_KEY in .env, then apply supabase/migrations/."
            ),
        )

    token = _bearer(authorization)
    try:
        auth_response = get_anon_client().auth.get_user(token)
    except SupabaseNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - any auth failure is a 401
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    user = getattr(auth_response, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    profile = db.get_profile(user.id)
    if profile is None:
        raise HTTPException(status_code=403, detail="No profile exists for this user")
    if not profile.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    return CurrentUser(
        id=user.id,
        email=getattr(user, "email", None),
        role=UserRole(profile["role"]),
        access_token=token,
    )


async def require_discom(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """DISCOM or ADMIN only. Used for review and approval routes."""
    if not user.is_discom:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires a DISCOM or ADMIN role",
        )
    return user
