"""Rules that decide what an applicant is told about their own application.

Two of them are easy to get wrong and expensive when wrong:

  * which statuses a re-assessment is allowed to move an application out of —
    get this wrong and re-running the numbers quietly rewinds a decision the
    DISCOM already made;
  * what a drawn distance claims to be — get this wrong and a straight line
    across a river is presented to a customer as a drive.

Neither needs a database or a network.
"""

from __future__ import annotations

from app.api.routes import PRE_DECISION_STATUSES
from app.api.routes_discom import AWAITING_REVIEW
from app.models.enums import ApplicationStatus
from app.services.routing import RoutingService, StraightLineProvider


# ============================================================
#  Status flow
# ============================================================
class TestPreDecisionStatuses:
    def test_an_assessed_application_is_still_pre_decision(self):
        """It has been screened, but nobody has decided anything."""
        assert ApplicationStatus.ASSESSED.value in PRE_DECISION_STATUSES
        assert ApplicationStatus.UNDER_DISCOM_REVIEW.value in PRE_DECISION_STATUSES

    def test_a_decided_application_is_not_moved_by_re_assessing(self):
        for decided in (
            ApplicationStatus.APPROVED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.VENDOR_SELECTED,
            ApplicationStatus.INSTALLING,
            ApplicationStatus.INSTALLED,
            ApplicationStatus.VERIFIED,
            ApplicationStatus.CANCELLED,
        ):
            assert decided.value not in PRE_DECISION_STATUSES, (
                f"{decided.value} would be rewound to UNDER_DISCOM_REVIEW by a re-assessment"
            )

    def test_the_landing_status_is_one_the_discom_queue_picks_up(self):
        """An assessed application must not vanish from the review queue."""
        assert ApplicationStatus.UNDER_DISCOM_REVIEW.value in AWAITING_REVIEW

    def test_the_previous_landing_status_still_reaches_the_queue(self):
        """Rows written before this change carry ASSESSED and must still show."""
        assert ApplicationStatus.ASSESSED.value in AWAITING_REVIEW

    def test_every_pre_decision_status_is_a_real_status(self):
        known = {s.value for s in ApplicationStatus}
        assert PRE_DECISION_STATUSES <= known


# ============================================================
#  Distance and drawn paths
# ============================================================
class TestStraightLineHonesty:
    provider = StraightLineProvider()

    def test_a_straight_line_never_claims_to_be_a_route(self):
        result = self.provider.distance(11.0, 76.9, 11.1, 77.0)

        assert result.is_route is False
        assert result.method == "STRAIGHT_LINE"
        assert "not" in result.note.lower() or "straight" in result.note.lower()

    def test_it_carries_geometry_so_a_map_can_draw_the_connector(self):
        result = self.provider.distance(11.0, 76.9, 11.1, 77.0)

        # [lon, lat] order, matching GeoJSON — a swapped pair would put the
        # line in the Indian Ocean.
        assert result.geometry == [[76.9, 11.0], [77.0, 11.1]]

    def test_the_connector_is_two_points_only(self):
        """It joins the ends. It is not a path, and must not look like one."""
        assert len(self.provider.distance(11.0, 76.9, 12.0, 77.0).geometry or []) == 2

    def test_distance_is_measured_not_invented(self):
        # One degree of latitude is ~111 km anywhere on the globe.
        result = self.provider.distance(11.0, 76.9, 12.0, 76.9)
        assert 110.0 < result.distance_km < 112.0

    def test_no_duration_without_a_routing_provider(self):
        """There is no honest travel time for a straight line."""
        assert self.provider.distance(11.0, 76.9, 11.1, 77.0).duration_minutes is None


class TestRoutingService:
    def test_a_missing_endpoint_yields_no_distance_at_all(self):
        """None, never a placeholder — a fabricated distance would rank vendors."""
        service = RoutingService(StraightLineProvider())

        assert service.distance(None, 76.9, 11.1, 77.0) is None
        assert service.distance(11.0, 76.9, None, None) is None

    def test_straight_line_service_does_not_advertise_real_routes(self):
        service = RoutingService(StraightLineProvider())

        assert service.routing_available is False
        assert service.describe()["returns_real_routes"] is False
