"""
main.py
-------
Entry point for the pick-and-place demo.

Run from the project root with:
    python main.py

Or with custom settings:
    python main.py --bin A2 --place P2 --retries 2

This script:
    1. Loads config from config/settings.yaml
    2. Applies any command-line overrides
    3. Creates the orchestrator
    4. Runs a single pick cycle
    5. Prints a clean result summary

Author : Karthikeyan Raja
"""

import argparse
import sys
from pathlib import Path

# Allow running from the project root without installing the package
sys.path.insert(0, str(Path(__file__).parent))

from ros2_pick_place.orchestrator import PickPlaceOrchestrator
from utils.config_loader           import load_config


def parse_args() -> argparse.Namespace:
    """Define and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ROS 2 Pick-and-Place Demo (standalone simulation)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--bin",     type=str,   default=None,
                        help="Override bin zone (e.g. A1, B2)")
    parser.add_argument("--place",   type=str,   default=None,
                        help="Override place zone (e.g. P1, P2)")
    parser.add_argument("--retries", type=int,   default=None,
                        help="Override max retry count")
    parser.add_argument("--config",  type=str,
                        default="config/settings.yaml",
                        help="Path to settings YAML file")
    return parser.parse_args()


def print_banner() -> None:
    """Print a simple project header."""
    print()
    print("=" * 55)
    print("  ROS 2 Pick-and-Place Demo")
    print("  Author : Karthikeyan Raja")
    print("  Target : Sereact GmbH — Deployment Engineer")
    print("=" * 55)
    print()


def print_result(result: dict) -> None:
    """Print the pick cycle result in a readable format."""
    print()
    print("=" * 55)
    if result["success"]:
        print("  RESULT : SUCCESS ✓")
        print(f"  Object : {result['object']}")
    else:
        print("  RESULT : FAILED ✗")
        print(f"  Reason : {result['error']}")

    print(f"  Time   : {result['duration']} s")
    print(f"  Retries: {result['retries']}")
    print("=" * 55)
    print()


def main() -> None:
    args   = parse_args()
    config = load_config(args.config)

    # Apply command-line overrides (if provided)
    if args.bin     is not None: config["bin_zone"]    = args.bin
    if args.place   is not None: config["place_zone"]  = args.place
    if args.retries is not None: config["max_retries"] = args.retries

    print_banner()
    print(f"Config: bin={config['bin_zone']}  "
          f"place={config['place_zone']}  "
          f"retries={config['max_retries']}  "
          f"conf_threshold={config['confidence_threshold']}")
    print()

    # Create orchestrator and run one pick cycle
    orchestrator = PickPlaceOrchestrator(config)
    result       = orchestrator.run_pick_cycle()

    print_result(result)

    # Exit with code 0 on success, 1 on failure (useful for CI)
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
