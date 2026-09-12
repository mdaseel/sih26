"""Category-wise rooftop capacity limits — inference-time guard, not training data.

Why this exists
---------------
The citizen form collected `connection_type` (Residential / Commercial /
Institutional) but nothing enforced it: the DB check allowed every
application 3-11 kW, so a commercial shed and a 1BHK faced the same ceiling.
A house cannot host 200 kW and a factory is not served by 10 kW.

Normative basis (national framework, states vary — DISCOM decides):
- Individual residential (PM Surya Ghar): 1-10 kW, CFA to 3 kW (capped
  Rs.78,000), net metering to 10 kW in all states.
- Commercial / Institutional / Industrial: up to sanctioned load, net
  metering cap 500 kW under the 2026 national framework; several states allow
  500-2000 kW and some have moved >500 kW to net billing (CEEW review of 29
  state/UT regulations). We take 500 kW as the default ceiling and leave
  higher state allowances to an explicit DISCOM override, never to the form.
- Minimum 1 kW follows 24 of 29 state regulations.

What this does NOT do
---------------------
- No retraining, no dataset change, no threshold change. The v2 model and
  the power flow accept whatever kW they are given; this only decides which
  *applications* may be filed under which consumer category.
- The engineering assessment endpoints (/api/assess, /api/twin, what-if)
  stay wide (0-5000 kW) so DISCOM feeder studies are unaffected. Only
  application creation is gated.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryLimit:
    min_kw: float
    max_kw: float
    note: str


CATEGORY_LIMITS: dict[str, CategoryLimit] = {
    "Residential": CategoryLimit(
        min_kw=1.0,
        max_kw=10.0,
        note="Individual rooftop under PM Surya Ghar: 1-10 kW, CFA to 3 kW.",
    ),
    "Commercial": CategoryLimit(
        min_kw=1.0,
        max_kw=500.0,
        note="Up to sanctioned load; net metering to 500 kW (state SERC may vary).",
    ),
    "Institutional": CategoryLimit(
        min_kw=1.0,
        max_kw=500.0,
        note="Schools/hospitals treated like commercial rooftop; state schemes vary.",
    ),
    "Industrial": CategoryLimit(
        min_kw=1.0,
        max_kw=500.0,
        note="Default 500 kW net-metering ceiling; larger needs DISCOM/state approval.",
    ),
}

DEFAULT_CATEGORY = "Residential"


def normalize_category(connection_type: str | None) -> str:
    """Map free text to a known category; unknown/blank means Residential.

    The form defaults to Residential and legacy rows carry NULL, so the
    strictest ceiling is the safe default — a commercial applicant declares
    their type to unlock theirs.
    """
    if not connection_type:
        return DEFAULT_CATEGORY
    key = connection_type.strip().lower()
    for known in CATEGORY_LIMITS:
        if known.lower() == key:
            return known
    return DEFAULT_CATEGORY


def limits_for(connection_type: str | None) -> CategoryLimit:
    return CATEGORY_LIMITS[normalize_category(connection_type)]


class CategoryCapacityError(ValueError):
    """Raised when a requested capacity is outside its category's range."""


def check_new_capacity(connection_type: str | None, new_pv_kw: float) -> CategoryLimit:
    lim = limits_for(connection_type)
    if not (lim.min_kw <= float(new_pv_kw) <= lim.max_kw):
        raise CategoryCapacityError(
            f"{normalize_category(connection_type)} rooftop systems are "
            f"{lim.min_kw:g}-{lim.max_kw:g} kW ({lim.note}) — "
            f"requested {float(new_pv_kw):g} kW."
        )
    return lim


def check_existing_capacity(connection_type: str | None, existing_pv_kw: float) -> CategoryLimit:
    lim = limits_for(connection_type)
    if not (0.0 <= float(existing_pv_kw) <= lim.max_kw):
        raise CategoryCapacityError(
            f"Existing solar of {float(existing_pv_kw):g} kW exceeds the "
            f"{normalize_category(connection_type)} ceiling of {lim.max_kw:g} kW."
        )
    return lim
