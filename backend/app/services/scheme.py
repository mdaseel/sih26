"""SchemeService — PM Surya Ghar information and indicative CFA estimates.

Everything in this module is CONFIGURATION, not knowledge. Subsidy rates,
eligibility rules, process steps and official links all live in the
scheme_config table and are edited there, never in code. Government policy
changes; a number compiled into an application becomes wrong silently.

Three rules this service holds to:

  1. No figure is presented as authoritative. Every estimate carries
     `indicative: true` and the wording the product requires.
  2. Configuration that has not been checked against the official portal is
     flagged `verification_required`, and that flag travels all the way to the
     screen. A seeded starting value is a placeholder, not a citation.
  3. SolarGrid AI is not the government portal, and says so in the payload
     rather than only in a footer somewhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from app.db.service import db

SCHEME_CODE = "PM_SURYA_GHAR"

NOT_OFFICIAL_PORTAL = (
    "SolarGrid AI is not the official PM Surya Ghar portal and cannot register, "
    "sanction or disburse a subsidy. Apply through the official government portal."
)

INDICATIVE = "Indicative estimate based on configured scheme rules."


@dataclass
class CFAEstimate:
    capacity_kw: float
    eligible_capacity_kw: float
    amount: float
    currency: str
    breakdown: list[dict[str, Any]] = field(default_factory=list)
    capped: bool = False
    max_subsidy: float | None = None
    indicative: bool = True
    disclaimer: str = INDICATIVE
    not_official_portal: str = NOT_OFFICIAL_PORTAL
    configuration_verified: bool = False
    verification_note: str = ""
    source_url: str | None = None
    effective_from: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


class SchemeNotConfigured(RuntimeError):
    """No scheme configuration has been seeded."""


class SchemeService:
    def config(self, scheme_code: str = SCHEME_CODE) -> dict[str, Any]:
        """All active configuration rows for a scheme, keyed by config_key."""
        rows = (
            db.as_service()
            .table("scheme_config")
            .select("config_key,config_value,description,effective_from,source_url")
            .eq("scheme_code", scheme_code)
            .eq("is_active", True)
            .execute()
        ).data or []

        if not rows:
            raise SchemeNotConfigured(
                f"No configuration for {scheme_code}. "
                "Run: python backend/seed/seed_scheme_config.py"
            )

        return {
            r["config_key"]: {
                "value": r["config_value"],
                "description": r["description"],
                "effective_from": r["effective_from"],
                "source_url": r["source_url"],
            }
            for r in rows
        }

    def estimate_cfa(self, capacity_kw: float, scheme_code: str = SCHEME_CODE) -> CFAEstimate:
        """Apply the configured slabs to a capacity.

        Slabs are cumulative thresholds: a slab with up_to_kw = N and
        rate_per_kw = R means capacity up to N attracts rate R, and the next
        slab picks up from N. Arithmetic only — no policy judgement is made
        here, and none should be. Deliberately no example rate is written here,
        so that no figure in this file can be mistaken for a scheme value.
        """
        config = self.config(scheme_code)
        cfa = config.get("cfa_slabs")
        if cfa is None:
            raise SchemeNotConfigured("cfa_slabs is not configured for this scheme")

        rules = cfa["value"]
        slabs = sorted(rules.get("slabs", []), key=lambda s: float(s["up_to_kw"]))
        currency = rules.get("currency", "INR")
        max_subsidy = rules.get("max_subsidy")
        eligible_cap = rules.get("max_eligible_capacity_kw")

        eligible_kw = float(capacity_kw)
        if eligible_cap is not None:
            eligible_kw = min(eligible_kw, float(eligible_cap))

        amount = 0.0
        breakdown: list[dict[str, Any]] = []
        covered = 0.0

        for slab in slabs:
            upper = float(slab["up_to_kw"])
            rate = float(slab["rate_per_kw"])
            band_kw = max(0.0, min(eligible_kw, upper) - covered)
            if band_kw <= 0:
                covered = max(covered, upper)
                continue
            band_amount = band_kw * rate
            amount += band_amount
            breakdown.append(
                {
                    "from_kw": round(covered, 3),
                    "to_kw": round(covered + band_kw, 3),
                    "kw": round(band_kw, 3),
                    "rate_per_kw": rate,
                    "amount": round(band_amount, 2),
                }
            )
            covered = upper

        capped = False
        if max_subsidy is not None and amount > float(max_subsidy):
            amount = float(max_subsidy)
            capped = True

        return CFAEstimate(
            capacity_kw=round(float(capacity_kw), 3),
            eligible_capacity_kw=round(eligible_kw, 3),
            amount=round(amount, 2),
            currency=currency,
            breakdown=breakdown,
            capped=capped,
            max_subsidy=float(max_subsidy) if max_subsidy is not None else None,
            configuration_verified=not rules.get("verification_required", True),
            verification_note=rules.get(
                "verification_note",
                "These rates have not been checked against the official portal.",
            ),
            source_url=cfa.get("source_url") or rules.get("source_url"),
            effective_from=cfa.get("effective_from"),
        )

    def overview(self, scheme_code: str = SCHEME_CODE) -> dict[str, Any]:
        """Everything the scheme page renders."""
        config = self.config(scheme_code)

        def value(key: str, default: Any = None) -> Any:
            entry = config.get(key)
            return entry["value"] if entry else default

        cfa_meta = config.get("cfa_slabs", {})
        rules = cfa_meta.get("value", {}) if cfa_meta else {}

        return {
            "scheme_code": scheme_code,
            "overview": value("overview", {}),
            "eligibility": value("eligibility", []),
            "process_steps": value("process_steps", []),
            "cfa_rules": rules,
            "official_links": value("official_links", []),
            "configuration": {
                "keys": sorted(config),
                "effective_from": cfa_meta.get("effective_from") if cfa_meta else None,
                "verification_required": rules.get("verification_required", True),
                "verification_note": rules.get("verification_note"),
                "editable_at": "public.scheme_config",
            },
            "disclaimer": INDICATIVE,
            "not_official_portal": NOT_OFFICIAL_PORTAL,
        }


@lru_cache
def get_scheme_service() -> SchemeService:
    return SchemeService()
