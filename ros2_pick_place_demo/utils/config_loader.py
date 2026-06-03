"""
utils/config_loader.py
----------------------
Loads settings from a YAML file and returns them as a plain dict.

Using a YAML config file (rather than hardcoding values) is an
important software engineering practice — it means you can change
settings (e.g. bin zone, confidence threshold) without touching
the source code.

Author : Karthikeyan Raja
"""

from pathlib import Path

# PyYAML is listed in requirements.txt.
# If not installed, we fall back to hard-coded defaults so the
# demo still runs in a minimal environment.
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# Defaults used if the YAML file is missing or YAML is not installed
DEFAULT_CONFIG = {
    "bin_zone"            : "A1",
    "place_zone"          : "P1",
    "max_retries"         : 3,
    "confidence_threshold": 0.75,
    "perception_latency"  : 0.3,
    "waypoint_duration"   : 0.2,
    "gripper_actuation"   : 0.12,
}


def load_config(path: str = "config/settings.yaml") -> dict:
    """
    Load configuration from *path*.

    If the file does not exist or PyYAML is unavailable, the
    DEFAULT_CONFIG values are returned.

    Parameters
    ----------
    path : relative or absolute path to the YAML settings file

    Returns
    -------
    dict of configuration key-value pairs
    """
    config_path = Path(path)

    if not YAML_AVAILABLE:
        print(f"[Config] PyYAML not installed — using defaults")
        return DEFAULT_CONFIG.copy()

    if not config_path.exists():
        print(f"[Config] '{path}' not found — using defaults")
        return DEFAULT_CONFIG.copy()

    with open(config_path, "r") as fh:
        loaded = yaml.safe_load(fh) or {}

    # Merge: loaded values override defaults, missing keys get defaults
    config = {**DEFAULT_CONFIG, **loaded}
    print(f"[Config] Loaded from {path}")
    return config
