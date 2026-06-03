"""
orchestrator.py
---------------
The main node that coordinates the full pick-and-place cycle.

Pipeline:
    1. Receive a pick request (bin zone + place zone)
    2. Ask the Perception module to detect objects
    3. Ask the Motion Planner to move to the best grasp pose
    4. Command the Gripper to close (pick)
    5. Move to the place zone
    6. Command the Gripper to open (place)
    7. Return home and report success / failure

This node runs standalone without a physical robot.
All hardware calls are simulated so the logic can be
demonstrated and explained in an interview.

Author : Karthikeyan Raja
"""

import time
import json
import threading

# --- ROS 2 imports (used when running inside a ROS 2 workspace) ---
# rclpy is the Python client library for ROS 2.
# If rclpy is not installed, we fall back to a tiny stub so the
# pure-Python demo still runs from the command line.
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String, Bool
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    # Stub so the rest of the file imports cleanly
    class Node:          # type: ignore
        pass

from ros2_pick_place.perception  import PerceptionModule, GraspCandidate
from ros2_pick_place.motion      import MotionPlanner
from ros2_pick_place.gripper     import GripperController
from ros2_pick_place.state       import PickState


class PickPlaceOrchestrator(Node):
    """
    Central coordinator for one pick-and-place cycle.

    Key design decisions (easy to explain in an interview):
    - One class = one responsibility (the 'orchestrator' only coordinates).
    - The state machine is just an Enum + a single method.
    - All tunable values are in config/settings.yaml, not hardcoded here.
    - Retry logic is simple: try up to max_retries times, then give up.
    """

    def __init__(self, config: dict):
        """
        Parameters
        ----------
        config : dict
            Values loaded from config/settings.yaml.
            Keys used here: max_retries, confidence_threshold,
                            bin_zone, place_zone.
        """
        if ROS2_AVAILABLE:
            super().__init__("pick_place_orchestrator")

        # --- config ---
        self.max_retries         = config.get("max_retries", 3)
        self.confidence_threshold = config.get("confidence_threshold", 0.75)
        self.bin_zone            = config.get("bin_zone", "A1")
        self.place_zone          = config.get("place_zone", "P1")

        # --- sub-modules ---
        self.perception = PerceptionModule()
        self.planner    = MotionPlanner()
        self.gripper    = GripperController()

        # --- state ---
        self.state      = PickState.IDLE
        self._lock      = threading.Lock()  # protects state during concurrent calls

        # --- ROS 2 publishers (only when ROS 2 is available) ---
        if ROS2_AVAILABLE:
            self._status_pub = self.create_publisher(
                String, "/pick_status", 10
            )
            self._ready_pub = self.create_publisher(
                Bool, "/system_ready", 10
            )

        self._log(f"Orchestrator ready | bin={self.bin_zone} place={self.place_zone}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_pick_cycle(self) -> dict:
        """
        Execute one complete pick-and-place cycle.

        Returns
        -------
        dict with keys:
            success   (bool)
            state     (str)   – final state name
            object    (str)   – what was picked, or empty string
            duration  (float) – total time in seconds
            retries   (int)   – how many attempts were needed
            error     (str)   – description if failed, else empty
        """
        start_time = time.time()
        retries    = 0
        last_error = ""

        while retries < self.max_retries:

            # ── Step 1: Detect objects ──────────────────────────────
            self._set_state(PickState.DETECTING)
            candidates = self.perception.detect(self.bin_zone)

            if not candidates:
                last_error = "No objects detected in bin"
                self._log(f"Attempt {retries+1}: {last_error}")
                retries += 1
                continue

            # ── Step 2: Select best candidate ──────────────────────
            best = max(candidates, key=lambda c: c.confidence)
            if best.confidence < self.confidence_threshold:
                last_error = (
                    f"Best confidence {best.confidence:.2f} "
                    f"below threshold {self.confidence_threshold}"
                )
                self._log(f"Attempt {retries+1}: {last_error}")
                retries += 1
                continue

            self._log(
                f"Selected: {best.label} at "
                f"({best.x:.3f}, {best.y:.3f}, {best.z:.3f}) "
                f"conf={best.confidence:.2f}"
            )

            # ── Step 3: Plan and execute pick motion ────────────────
            self._set_state(PickState.PLANNING)
            trajectory = self.planner.plan_to_pose(best.x, best.y, best.z)
            if trajectory is None:
                last_error = "Motion planning failed (no valid trajectory)"
                retries += 1
                continue

            self._set_state(PickState.EXECUTING)
            self.gripper.open()
            self.planner.execute(trajectory)
            self.gripper.close()

            # ── Step 4: Place ───────────────────────────────────────
            self._set_state(PickState.PLACING)
            self.planner.move_to_zone(self.place_zone)
            self.gripper.open()

            # ── Step 5: Return home ─────────────────────────────────
            self.planner.move_home()
            self._set_state(PickState.SUCCESS)

            duration = round(time.time() - start_time, 3)
            self._log(f"SUCCESS | object={best.label} | {duration}s | retries={retries}")

            return {
                "success" : True,
                "state"   : PickState.SUCCESS.name,
                "object"  : best.label,
                "duration": duration,
                "retries" : retries,
                "error"   : "",
            }

        # ── All retries exhausted ───────────────────────────────────
        self._set_state(PickState.FAILED)
        duration = round(time.time() - start_time, 3)
        self._log(f"FAILED after {retries} retries | {last_error}")

        return {
            "success" : False,
            "state"   : PickState.FAILED.name,
            "object"  : "",
            "duration": duration,
            "retries" : retries,
            "error"   : last_error,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_state(self, new_state: PickState) -> None:
        """Thread-safe state update + optional ROS 2 publish."""
        with self._lock:
            self.state = new_state

        self._log(f"State → {new_state.name}")

        if ROS2_AVAILABLE:
            msg      = String()
            msg.data = json.dumps({
                "state"     : new_state.name,
                "bin_zone"  : self.bin_zone,
                "place_zone": self.place_zone,
                "timestamp" : time.time(),
            })
            self._status_pub.publish(msg)

            ready      = Bool()
            ready.data = (new_state == PickState.IDLE)
            self._ready_pub.publish(ready)

    def _log(self, message: str) -> None:
        """Unified logging: ROS 2 logger when available, else print."""
        if ROS2_AVAILABLE:
            self.get_logger().info(message)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] [Orchestrator] {message}")
