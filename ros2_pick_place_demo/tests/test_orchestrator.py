"""
tests/test_orchestrator.py
--------------------------
Integration tests for the PickPlaceOrchestrator.

These tests patch (replace) the sub-modules so we can control
what the orchestrator sees — objects found, no objects, planning
failure — and verify it responds correctly in each case.

Author : Karthikeyan Raja
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch, MagicMock

from ros2_pick_place.orchestrator import PickPlaceOrchestrator
from ros2_pick_place.perception   import GraspCandidate
from ros2_pick_place.state        import PickState


# Minimal config used in all tests
BASE_CONFIG = {
    "bin_zone"            : "A1",
    "place_zone"          : "P1",
    "max_retries"         : 2,
    "confidence_threshold": 0.75,
}


def make_candidate(confidence: float = 0.90) -> GraspCandidate:
    """Helper: create a single high-confidence grasp candidate."""
    return GraspCandidate(
        label="box_A", x=0.4, y=0.2, z=0.3, yaw=0.1,
        confidence=confidence
    )


@pytest.fixture
def orchestrator():
    """Create an orchestrator with zero-latency sub-modules."""
    return PickPlaceOrchestrator(BASE_CONFIG)


# ── Happy path ─────────────────────────────────────────────────────────────


def test_successful_pick(orchestrator):
    """A high-confidence detection should produce a SUCCESS result."""
    with patch.object(orchestrator.perception, "detect",
                      return_value=[make_candidate(0.90)]):
        result = orchestrator.run_pick_cycle()

    assert result["success"] is True
    assert result["state"]   == PickState.SUCCESS.name
    assert result["object"]  == "box_A"
    assert result["retries"] == 0


def test_result_contains_all_keys(orchestrator):
    """The result dict must always have all expected keys."""
    with patch.object(orchestrator.perception, "detect",
                      return_value=[make_candidate()]):
        result = orchestrator.run_pick_cycle()

    for key in ("success", "state", "object", "duration", "retries", "error"):
        assert key in result, f"Missing key: {key}"


# ── Failure paths ──────────────────────────────────────────────────────────


def test_empty_bin_causes_failure(orchestrator):
    """When the bin is always empty, result must be FAILED."""
    with patch.object(orchestrator.perception, "detect", return_value=[]):
        result = orchestrator.run_pick_cycle()

    assert result["success"] is False
    assert result["state"]   == PickState.FAILED.name
    assert result["retries"] == BASE_CONFIG["max_retries"]


def test_low_confidence_causes_failure(orchestrator):
    """A candidate below the threshold should also yield FAILED."""
    low_conf_candidate = make_candidate(confidence=0.50)   # below 0.75
    with patch.object(orchestrator.perception, "detect",
                      return_value=[low_conf_candidate]):
        result = orchestrator.run_pick_cycle()

    assert result["success"] is False
    assert "confidence" in result["error"].lower()


def test_planning_failure_causes_retry(orchestrator):
    """If the planner returns None, the orchestrator should retry."""
    with patch.object(orchestrator.perception, "detect",
                      return_value=[make_candidate()]), \
         patch.object(orchestrator.planner, "plan_to_pose",
                      return_value=None):
        result = orchestrator.run_pick_cycle()

    assert result["success"] is False
    # Should have retried max_retries times
    assert result["retries"] == BASE_CONFIG["max_retries"]


# ── Retry recovery ─────────────────────────────────────────────────────────


def test_success_after_one_retry(orchestrator):
    """
    Simulate: first detection returns nothing, second returns an object.
    The orchestrator should succeed on the second attempt.
    """
    call_count = {"n": 0}

    def detect_side_effect(bin_zone):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return []                             # first call: empty bin
        return [make_candidate(0.92)]             # second call: found object

    with patch.object(orchestrator.perception, "detect",
                      side_effect=detect_side_effect):
        result = orchestrator.run_pick_cycle()

    assert result["success"] is True
    assert result["retries"] == 1
