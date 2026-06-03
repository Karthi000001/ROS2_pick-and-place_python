"""
perception.py
-------------
Simulates a camera + AI perception pipeline that detects objects
in a bin and returns a list of grasp candidates ranked by confidence.

In a real Sereact deployment this module would:
    - Subscribe to a ROS 2 sensor_msgs/PointCloud2 topic
    - Run a neural network (e.g. FoundationPose or PickNet) on the data
    - Return real 3-D grasp poses in the robot's base frame

For this portfolio demo, we generate realistic-looking synthetic data
so the full orchestration logic can be demonstrated and tested without
any physical hardware.

Author : Karthikeyan Raja
"""

import random
import time
from dataclasses import dataclass


@dataclass
class GraspCandidate:
    """
    Represents one object detected in the bin and a suggested grasp pose.

    Attributes
    ----------
    label      : human-readable object name (e.g. "box_A")
    x, y, z    : position of the object centre in metres (robot base frame)
    yaw        : rotation around the vertical axis in radians
    confidence : detection confidence, 0.0 – 1.0 (higher is better)
    """
    label     : str
    x         : float
    y         : float
    z         : float
    yaw       : float
    confidence: float


class PerceptionModule:
    """
    Wraps the object-detection pipeline.

    The public method `detect(bin_zone)` is the only interface the
    orchestrator needs to know about — it returns a list of
    GraspCandidates, sorted best-first.
    """

    # Simulated objects that could appear in a bin
    _OBJECT_TYPES = ["box_A", "box_B", "cylinder_C", "pouch_D"]

    def __init__(self, latency_seconds: float = 0.3):
        """
        Parameters
        ----------
        latency_seconds : simulated inference time (default 300 ms)
        """
        self._latency = latency_seconds

    def detect(self, bin_zone: str) -> list:
        """
        Scan the given bin zone and return grasp candidates.

        Parameters
        ----------
        bin_zone : label of the bin to scan (e.g. "A1")

        Returns
        -------
        list of GraspCandidate, sorted by confidence descending.
        An empty list means no objects were found.
        """
        print(f"[Perception] Scanning bin zone: {bin_zone}")
        time.sleep(self._latency)           # simulate inference time

        # Randomly decide how many objects are in the bin (0–3)
        n_objects = random.randint(0, 3)
        if n_objects == 0:
            print("[Perception] Bin appears empty")
            return []

        candidates = []
        for i in range(n_objects):
            candidate = GraspCandidate(
                label      = random.choice(self._OBJECT_TYPES),
                x          = round(random.uniform(0.35, 0.55), 3),
                y          = round(random.uniform(0.10, 0.30), 3),
                z          = round(random.uniform(0.20, 0.40), 3),
                yaw        = round(random.uniform(-0.5, 0.5), 3),
                confidence = round(random.uniform(0.60, 0.98), 2),
            )
            candidates.append(candidate)

        # Sort best confidence first so the orchestrator can simply
        # pick candidates[0] as the best option.
        candidates.sort(key=lambda c: c.confidence, reverse=True)

        for c in candidates:
            print(
                f"[Perception]  {c.label:12s} "
                f"pos=({c.x}, {c.y}, {c.z})  "
                f"conf={c.confidence}"
            )

        return candidates
