"""Enumerations mirroring the Postgres types in 0001_init_schema.sql.

Values are kept identical to the strings the existing pipeline emits, so that
labels flow from scenario_config.json through the model and into the database
without translation.
"""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    CITIZEN = "CITIZEN"
    DISCOM = "DISCOM"
    VENDOR = "VENDOR"
    ADMIN = "ADMIN"


class RiskLevel(StrEnum):
    """The three classes emitted by suryagrid_model_v2.pkl."""

    SAFE = "SAFE"
    CAUTION = "CAUTION"
    CONSTRAINED = "CONSTRAINED"


class ConstraintKind(StrEnum):
    """Mirrors constraint_type in dataset_generation_phase2.py."""

    NONE = "none"
    VOLTAGE = "voltage"
    VOLTAGE_RISE = "voltage_rise"
    LINE_LOADING = "line_loading"
    TRANSFORMER_LOADING = "transformer_loading"
    CAUTION = "caution"


class ApplicationStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ASSESSING = "ASSESSING"
    ASSESSED = "ASSESSED"
    UNDER_DISCOM_REVIEW = "UNDER_DISCOM_REVIEW"
    APPROVED = "APPROVED"
    ENGINEERING_REVIEW = "ENGINEERING_REVIEW"
    REJECTED = "REJECTED"
    VENDOR_SELECTED = "VENDOR_SELECTED"
    INSTALLING = "INSTALLING"
    INSTALLED = "INSTALLED"
    VERIFIED = "VERIFIED"
    CANCELLED = "CANCELLED"


class GridAssetType(StrEnum):
    SUBSTATION = "SUBSTATION"
    FEEDER = "FEEDER"
    TRANSFORMER = "TRANSFORMER"
    BUS = "BUS"
    LINE = "LINE"
    CUSTOMER_POINT = "CUSTOMER_POINT"


class VendorStatus(StrEnum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class InstallationStatus(StrEnum):
    PENDING = "PENDING"
    SITE_VISIT = "SITE_VISIT"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"


class AppointmentStatus(StrEnum):
    REQUESTED = "REQUESTED"
    CONFIRMED = "CONFIRMED"
    RESCHEDULED = "RESCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
