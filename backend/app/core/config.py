"""Application configuration, loaded from environment variables.

No credential is ever hardcoded. The service-role key and the database password
are read here, on the backend, and must never be forwarded to a client (Rule 10).

Supabase exposes several different URLs and they are easy to confuse:

    project URL   https://<ref>.supabase.co          <- what the REST/auth client needs
    REST endpoint https://<ref>.supabase.co/rest/v1/ <- project URL + a path
    database URL  postgresql://...pooler.supabase.com:5432/postgres

This module normalises all three. If SUPABASE_URL is given as a postgres
connection string, it is treated as the database URL and the project URL is
derived from SUPABASE_REST_API instead, so a mixed-up .env still works.
"""

from __future__ import annotations

import re
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import REPO_ROOT

_PROJECT_REF = re.compile(r"https://([a-z0-9-]+)\.supabase\.(co|in|net)", re.IGNORECASE)


def _unquote(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in {'"', "'"}:
        v = v[1:-1]
    return v.strip()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Supabase ---
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_rest_api: str = Field(default="", alias="SUPABASE_REST_API")
    supabase_db_url: str = Field(default="", alias="SUPABASE_DB_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")

    # --- App ---
    app_env: str = Field(default="development", alias="APP_ENV")
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    # --- NVIDIA NIM (chatbot) ---
    nvidia_nim_api_key: str = Field(default="", alias="NVIDIA_NIM_API_KEY")
    nvidia_nim_api_key_alt: str = Field(default="", alias="NVIDIA_NIM_API")
    nvidia_nim_base_url: str = Field(
        default="https://integrate.api.nvidia.com/v1", alias="NVIDIA_NIM_BASE_URL"
    )
    nvidia_nim_model: str = Field(
        default="meta/llama-3.2-11b-vision-instruct", alias="NVIDIA_NIM_MODEL"
    )

    @field_validator(
        "supabase_url",
        "supabase_rest_api",
        "supabase_db_url",
        "supabase_anon_key",
        "supabase_service_role_key",
        "cors_origins",
        "nvidia_nim_api_key",
        "nvidia_nim_api_key_alt",
        "nvidia_nim_base_url",
        "nvidia_nim_model",
        mode="before",
    )
    @classmethod
    def _clean(cls, v: object) -> object:
        return _unquote(v) if isinstance(v, str) else v

    # ---------------- derived URLs ----------------

    @property
    def project_url(self) -> str:
        """The https://<ref>.supabase.co base URL the Supabase client needs."""
        for candidate in (self.supabase_url, self.supabase_rest_api):
            if candidate.startswith("http"):
                match = _PROJECT_REF.match(candidate)
                if match:
                    return match.group(0)
                return candidate.split("/rest/", 1)[0].rstrip("/")
        return ""

    @property
    def database_url(self) -> str:
        """The postgresql:// URL, used only for applying migrations."""
        if self.supabase_db_url.startswith("postgres"):
            return self.supabase_db_url
        if self.supabase_url.startswith("postgres"):
            return self.supabase_url
        return ""

    @property
    def project_ref(self) -> str:
        match = _PROJECT_REF.match(self.project_url)
        return match.group(1) if match else ""

    # ---------------- readiness ----------------

    @property
    def supabase_configured(self) -> bool:
        return bool(self.project_url and self.supabase_anon_key)

    @property
    def service_role_configured(self) -> bool:
        return bool(self.project_url and self.supabase_service_role_key)

    @property
    def database_configured(self) -> bool:
        return bool(self.database_url)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def nvidia_api_key(self) -> str:
        if self.nvidia_nim_api_key or self.nvidia_nim_api_key_alt:
            return self.nvidia_nim_api_key or self.nvidia_nim_api_key_alt
        # Fallback: developer put the key in frontend/.env.local (common local setup)
        # Backend .env is authoritative, but we check the frontend file so "it just works" locally.
        try:
            from pathlib import Path

            for cand in (REPO_ROOT / "frontend" / ".env.local", REPO_ROOT / ".env.local"):
                if cand.exists():
                    for line in cand.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k in ("NVIDIA_NIM_API_KEY", "NVIDIA_NIM_API", "NVIDIA_NIM_APIKEY") and v:
                            return v
        except Exception:
            pass
        return ""

    @property
    def nvidia_configured(self) -> bool:
        return bool(self.nvidia_api_key)

    def describe(self) -> dict[str, object]:
        """Config summary safe to log. Never includes key material or passwords."""
        return {
            "app_env": self.app_env,
            "api": f"{self.api_host}:{self.api_port}",
            "cors_origins": self.cors_origin_list,
            "project_ref": self.project_ref or "(unset)",
            "project_url_resolved": bool(self.project_url),
            "anon_key_set": bool(self.supabase_anon_key),
            "service_role_key_set": bool(self.supabase_service_role_key),
            "database_url_set": bool(self.database_url),
            "nvidia_configured": self.nvidia_configured,
            "nvidia_base_url": self.nvidia_nim_base_url,
            "nvidia_model": self.nvidia_nim_model,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
