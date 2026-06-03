"""
state.py
--------
Defines all possible states the pick-and-place system can be in.

Using an Enum keeps the states explicit and prevents typos
(e.g. "SUCCCESS" vs "SUCCESS").  The orchestrator transitions
through these states in order during a normal pick cycle.

         IDLE
          │
          ▼
       DETECTING  ──(no objects)──► FAILED
          │
          ▼
       PLANNING   ──(no path)────► FAILED
          │
          ▼
       EXECUTING
          │
          ▼
        PLACING
          │
          ▼
        SUCCESS

Author : Karthikeyan Raja
"""

from enum import Enum, auto


class PickState(Enum):
    """
    Each state maps to a step in the pick-and-place pipeline.

    auto() assigns an integer value automatically so we don't
    need to manage numbers ourselves.
    """
    IDLE       = auto()   # system is ready and waiting
    DETECTING  = auto()   # camera / AI is scanning the bin
    PLANNING   = auto()   # motion planner is computing a path
    EXECUTING  = auto()   # robot arm is moving to the object
    PLACING    = auto()   # object being moved to place zone
    SUCCESS    = auto()   # pick cycle completed successfully
    FAILED     = auto()   # cycle failed (all retries exhausted)
    CANCELLED  = auto()   # operator manually cancelled the cycle
