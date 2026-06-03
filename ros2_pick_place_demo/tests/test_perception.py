"""
tests/test_perception.py
------------------------
Unit tests for the PerceptionModule.

Run with:
    pytest tests/ -v

These tests verify:
    - detect() returns GraspCandidate objects with valid fields
    - candidates are sorted best-confidence-first
    - an empty bin returns an empty list

Author : Karthikeyan Raja
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from ros2_pick_place.perception import PerceptionModule, GraspCandidate


@pytest.fixture
def perception():
    """Create a PerceptionModule with zero latency for fast tests."""
    return PerceptionModule(latency_seconds=0.0)


def test_detect_returns_list(perception):
    """detect() should always return a list (never None)."""
    result = perception.detect("A1")
    assert isinstance(result, list)


def test_candidates_are_grasp_candidates(perception, monkeypatch):
    """Each item in the list must be a GraspCandidate."""
    # Force at least 1 object to be detected
    import random
    monkeypatch.setattr(random, "randint", lambda a, b: 2)

    result = perception.detect("A1")
    assert len(result) > 0
    for c in result:
        assert isinstance(c, GraspCandidate)


def test_candidates_sorted_by_confidence(perception, monkeypatch):
    """Candidates must be sorted highest confidence first."""
    import random
    monkeypatch.setattr(random, "randint", lambda a, b: 3)

    result = perception.detect("A1")
    confidences = [c.confidence for c in result]
    assert confidences == sorted(confidences, reverse=True)


def test_candidate_fields_in_range(perception, monkeypatch):
    """All GraspCandidate fields must be within expected ranges."""
    import random
    monkeypatch.setattr(random, "randint", lambda a, b: 2)

    result = perception.detect("A1")
    for c in result:
        assert 0.0 <= c.confidence <= 1.0
        assert 0.0 < c.x < 1.0
        assert 0.0 < c.y < 1.0
        assert 0.0 < c.z < 1.0
        assert isinstance(c.label, str)
        assert len(c.label) > 0


def test_empty_bin_returns_empty_list(perception, monkeypatch):
    """When randint returns 0, detect() must return an empty list."""
    import random
    monkeypatch.setattr(random, "randint", lambda a, b: 0)

    result = perception.detect("A1")
    assert result == []
