"""
gripper.py
----------
Controls the end-effector (gripper) — open to approach,
close to grasp, open again to release.

In a real deployment this would:
    - Publish to a /gripper_cmd topic (std_msgs/String)
    - Or call a gripper action server (e.g. Robotiq 2F-140 ROS 2 driver)
    - Monitor /gripper_state to confirm the command was executed

For this demo we simulate the open/close with a short delay and
track the current state so tests can verify correct sequencing.

Author : Karthikeyan Raja
"""

import time


class GripperController:
    """
    Simple open/close interface for a 2-finger gripper.

    The orchestrator calls:
        gripper.open()   before approaching the object
        gripper.close()  after reaching the grasp pose
        gripper.open()   after arriving at the place zone
    """

    def __init__(self, actuation_time: float = 0.12):
        """
        Parameters
        ----------
        actuation_time : seconds to simulate open or close motion
        """
        self._actuation_time = actuation_time
        self.is_open = True          # gripper starts in open (safe) state

    def open(self) -> None:
        """Open the gripper to maximum aperture."""
        if self.is_open:
            print("[Gripper] Already open — skipping")
            return
        print("[Gripper] Opening")
        time.sleep(self._actuation_time)
        self.is_open = True
        print("[Gripper] Open ✓")

    def close(self) -> None:
        """Close the gripper to grip an object."""
        if not self.is_open:
            print("[Gripper] Already closed — skipping")
            return
        print("[Gripper] Closing on object")
        time.sleep(self._actuation_time)
        self.is_open = False
        print("[Gripper] Closed ✓")

    @property
    def state(self) -> str:
        """Return 'OPEN' or 'CLOSED' as a human-readable string."""
        return "OPEN" if self.is_open else "CLOSED"
