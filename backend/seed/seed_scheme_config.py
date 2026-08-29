"""Seed PM Surya Ghar scheme configuration.

IMPORTANT — read before demonstrating this to anyone.

The subsidy rates below are a STARTING PLACEHOLDER so the calculator has
something to run on. They are marked `verification_required: true`, and that
flag is surfaced in the API and on the scheme page as a visible warning.

Government scheme parameters change. Nothing here should be treated as current
policy until someone has checked it against the official portal and set
`verification_required` to false with the date they checked. That is a
deliberate one-line edit in the database, not a code change:

    update public.scheme_config
    set config_value = jsonb_set(config_value, '{verification_required}', 'false')
    where scheme_code = 'PM_SURYA_GHAR' and config_key = 'cfa_slabs';

Usage:
    python backend/seed/seed_scheme_config.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.service import db  # noqa: E402

OFFICIAL_PORTAL = "https://pmsuryaghar.gov.in"

ROWS = [
    {
        "config_key": "overview",
        "description": "Plain-language description of the scheme.",
        "source_url": OFFICIAL_PORTAL,
        "config_value": {
            "title": "PM Surya Ghar: Muft Bijli Yojana",
            "summary": (
                "A central government scheme supporting rooftop solar on residential "
                "buildings, combining a capital subsidy (Central Financial Assistance) "
                "with net metering through your electricity distribution company."
            ),
            "what_it_covers": [
                "A capital subsidy towards the cost of a residential rooftop system",
                "A route to net metering so surplus generation is credited",
                "A registry of empanelled vendors who can carry out the installation",
            ],
            "official_portal_url": OFFICIAL_PORTAL,
            "not_official_portal": (
                "SolarGrid AI is an independent grid-screening tool. It is not the "
                "government portal and cannot register or sanction a subsidy."
            ),
        },
    },
    {
        "config_key": "eligibility",
        "description": "Eligibility conditions shown to applicants. Edit as policy changes.",
        "source_url": OFFICIAL_PORTAL,
        "config_value": [
            {
                "code": "RESIDENTIAL",
                "label": "Residential consumer",
                "detail": "The connection must be a residential electricity connection.",
            },
            {
                "code": "OWNERSHIP",
                "label": "Suitable roof you may use",
                "detail": "You must own the roof, or have permission to install on it.",
            },
            {
                "code": "VALID_CONNECTION",
                "label": "Active electricity connection",
                "detail": "A valid consumer number with your distribution company.",
            },
            {
                "code": "NO_PRIOR_SUBSIDY",
                "label": "No previous rooftop subsidy",
                "detail": "The premises must not already have claimed a rooftop subsidy.",
            },
            {
                "code": "EMPANELLED_VENDOR",
                "label": "Registered installer",
                "detail": "Installation must be carried out by a registered vendor.",
            },
        ],
    },
    {
        "config_key": "process_steps",
        "description": "End-to-end process, including where this application fits.",
        "source_url": OFFICIAL_PORTAL,
        "config_value": [
            {
                "step": 1,
                "actor": "Citizen",
                "title": "Check whether the grid can host your system",
                "detail": (
                    "Submit a capacity request here. The network is screened by a model "
                    "and verified by a power-flow simulation."
                ),
                "in_this_app": True,
            },
            {
                "step": 2,
                "actor": "Citizen",
                "title": "Register with the national scheme",
                "detail": (
                    "Scheme registration is made with the government, outside "
                    "SolarGrid AI. Nothing here registers you for the subsidy."
                ),
                "in_this_app": False,
            },
            {
                "step": 3,
                "actor": "DISCOM",
                "title": "Technical feasibility approval",
                "detail": "Your distribution company reviews the connection request.",
                "in_this_app": True,
            },
            {
                "step": 4,
                "actor": "Vendor",
                "title": "Installation by a registered vendor",
                "detail": "Choose a verified installer, agree a date, and have the system installed.",
                "in_this_app": True,
            },
            {
                "step": 5,
                "actor": "DISCOM",
                "title": "Inspection and net metering",
                "detail": "The DISCOM inspects the installation and commissions the meter.",
                "in_this_app": True,
            },
            {
                "step": 6,
                "actor": "Government",
                "title": "Subsidy disbursed",
                "detail": (
                    "After verification, the Central Financial Assistance is credited "
                    "to your bank account by the government."
                ),
                "in_this_app": False,
            },
        ],
    },
    {
        "config_key": "cfa_slabs",
        "description": (
            "Central Financial Assistance slabs. PLACEHOLDER VALUES — verify against "
            "the scheme rules in force before relying on any figure."
        ),
        "source_url": OFFICIAL_PORTAL,
        "config_value": {
            "currency": "INR",
            # Cumulative thresholds: the first 2 kW at the first rate, the third
            # kW at the second rate.
            "slabs": [
                {"up_to_kw": 2, "rate_per_kw": 30000},
                {"up_to_kw": 3, "rate_per_kw": 18000},
            ],
            "max_subsidy": 78000,
            "max_eligible_capacity_kw": 3,
            "applies_to": "Residential rooftop systems",
            "verification_required": True,
            "verification_note": (
                "These rates are a seeded placeholder and have NOT been verified against "
                "the scheme rules in force. Check the current scheme parameters, then set "
                "verification_required to false with the date checked."
            ),
            "verified_on": None,
            "source_url": OFFICIAL_PORTAL,
        },
    },
    {
        "config_key": "official_links",
        "description": "Links to official sources. Verify these resolve before a demo.",
        "source_url": OFFICIAL_PORTAL,
        "config_value": [
            {
                "label": "PM Surya Ghar official portal",
                "url": OFFICIAL_PORTAL,
                "detail": "Register, track your application, and see the current scheme rules.",
            },
            {
                "label": "Ministry of New and Renewable Energy",
                "url": "https://mnre.gov.in",
                "detail": "The ministry responsible for the scheme.",
            },
        ],
    },
]


def main() -> int:
    rows = [
        {
            "scheme_code": "PM_SURYA_GHAR",
            "config_key": r["config_key"],
            "config_value": r["config_value"],
            "description": r["description"],
            "source_url": r["source_url"],
            "is_active": True,
        }
        for r in ROWS
    ]

    written = db.upsert_scheme_config(rows)
    print(f"seeded {written} scheme_config rows for PM_SURYA_GHAR")
    for r in ROWS:
        print(f"  {r['config_key']}")

    print(
        "\nWARNING: cfa_slabs holds PLACEHOLDER rates marked verification_required.\n"
        "Check them against the official portal before showing this to anyone, then\n"
        "clear the flag in the database. The app displays the warning until you do."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
