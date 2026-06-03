"""
tests/test_gripper.py
---------------------
Unit tests for GripperController.

These tests verify the open/close state machine and
the idempotency guards (opening an already-open gripper
should not crash or change state incorrectly).

Author : Karthikeyan Raja
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ros2_pick_place.gripper import GripperController


def make_gripper() -> GripperController:
    """Return a fast gripper for tests (zero actuation time)."""
    return GripperController(actuation_time=0.0)


def test_initial_state_is_open():
    """Gripper should start in OPEN state (safe default)."""
    g = make_gripper()
    assert g.is_open is True
    assert g.state == "OPEN"


def test_close_changes_state():
    """close() must set is_open to False."""
    g = make_gripper()
    g.close()
    assert g.is_open is False
    assert g.state == "CLOSED"


def test_open_after_close():
    """open() after close() must set is_open back to True."""
    g = make_gripper()
    g.close()
    g.open()
    assert g.is_open is True


def test_close_twice_is_safe():
    """Calling close() twice must not raise and state stays CLOSED."""
    g = make_gripper()
    g.close()
    g.close()   # second call should be a no-op
    assert g.is_open is False


def test_open_twice_is_safe():
    """Calling open() twice on an already-open gripper must be a no-op."""
    g = make_gripper()
    g.open()    # already open — should not raise
    assert g.is_open is True


def test_pick_sequence():
    """
    Simulate the exact sequence the orchestrator performs:
        open → close (grasp) → open (release)
    """
    g = make_gripper()
    g.open()          # approach: ensure open
    assert g.is_open is True

    g.close()         # grasp
    assert g.is_open is False

    g.open()          # release at place zone
    assert g.is_open is True
