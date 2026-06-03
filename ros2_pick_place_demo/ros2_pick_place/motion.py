"""
motion.py
---------
Simulates a motion planner that computes a joint trajectory and
executes it on the robot arm.

In a real deployment this module would:
    - Call MoveIt 2 via the MoveGroupInterface Python API
    - Use IK solvers (KDL, TRAC-IK) to find joint angles
    - Execute via JointTrajectoryController and action servers

For this demo, we simulate the trajectory as a list of 5 waypoints
and "execute" them with a short sleep per waypoint.

Why 5 waypoints?
    A real pick motion has ~5 key poses:
    home → pre-grasp (above object) → grasp → retract → place

Author : Karthikeyan Raja
"""

import time
import math
from typing import Optional


# A single waypoint = 6 joint angles (radians) for a 6-DOF arm
Waypoint = list   # list of 6 floats


class MotionPlanner:
    """
    Plans and executes trajectories for a 6-DOF robot arm.

    Public methods the orchestrator uses:
        plan_to_pose(x, y, z)  → list of waypoints, or None
        execute(trajectory)    → None
        move_to_zone(zone)     → None
        move_home()            → None
    """

    # Time per waypoint during simulated execution
    WAYPOINT_DURATION = 0.2   # seconds

    # Hard-coded home joint configuration (all joints at zero)
    HOME_CONFIG = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def plan_to_pose(
        self,
        x: float,
        y: float,
        z: float,
    ) -> Optional[list]:
        """
        Compute a joint trajectory to reach position (x, y, z).

        In reality this calls an IK solver + path planner.
        Here we compute a simple linear interpolation from home to
        a rough joint-space estimate (good enough to demonstrate the
        concept).

        Returns
        -------
        list of 5 Waypoints, or None if planning failed.
        """
        print(f"[Motion] Planning to ({x:.3f}, {y:.3f}, {z:.3f})")
        time.sleep(0.15)   # simulate 150 ms planning time

        # Very simplified IK: use atan2 for the base rotation and
        # linear estimates for the remaining joints.
        base_angle = math.atan2(y, x)

        # Build 5 waypoints that interpolate from home to target
        trajectory = []
        for step in range(5):
            t = step / 4.0   # 0.0, 0.25, 0.5, 0.75, 1.0
            waypoint = [
                base_angle  * t,             # joint 1  – base rotation
                -0.8        * t,             # joint 2  – shoulder
                1.2         * t,             # joint 3  – elbow
                0.0,                         # joint 4  – wrist 1
                -math.pi / 2 * t,            # joint 5  – wrist 2 (top-down)
                0.0,                         # joint 6  – wrist 3
            ]
            trajectory.append([round(j, 4) for j in waypoint])

        print(f"[Motion] Planned {len(trajectory)} waypoints")
        return trajectory

    def execute(
        self,
        trajectory: list,
        feedback_callback=None,
    ) -> None:
        """
        Execute a trajectory waypoint by waypoint.

        Parameters
        ----------
        trajectory        : list of waypoints from plan_to_pose()
        feedback_callback : optional function(progress_pct: int)
                            called after each waypoint — useful for
                            streaming progress to an action client.
        """
        n = len(trajectory)
        for i, waypoint in enumerate(trajectory):
            time.sleep(self.WAYPOINT_DURATION)
            progress = int((i + 1) / n * 100)
            print(f"[Motion] Step {i+1}/{n}  {progress}%  joints={waypoint}")
            if feedback_callback:
                feedback_callback(progress)

    def move_to_zone(self, zone: str) -> None:
        """Move the arm to a named place zone (e.g. 'P1')."""
        print(f"[Motion] Moving to place zone: {zone}")
        time.sleep(0.4)

    def move_home(self) -> None:
        """Return the arm to the home (rest) position."""
        print(f"[Motion] Returning home  joints={self.HOME_CONFIG}")
        time.sleep(0.3)
