#!/usr/bin/env python3
"""Automated dock/undock test runner for the Autodock action."""

import argparse
import subprocess
import sys
import time
from typing import Tuple


def build_command(is_dock: bool) -> list[str]:
    """Construct the ros2 CLI command for the requested action."""
    goal_yaml = "{is_dock: True}" if is_dock else "{is_dock: False}"
    return [
        "ros2",
        "action",
        "send_goal",
        "--feedback",
        "autodock",
        "custom_interface/action/Autodock",
        goal_yaml,
    ]


def run_goal(is_dock: bool) -> Tuple[bool, str]:
    """Execute the dock/undock command and return success flag with logs."""
    command = build_command(is_dock)
    direction = "dock" if is_dock else "undock"
    print(f"[INFO] Executing {direction} command: {' '.join(command)}", flush=True)

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "ros2 CLI not found in PATH."

    output = result.stdout or ""
    print(output, flush=True)

    if result.returncode != 0:
        return False, f"ros2 CLI returned non-zero exit status {result.returncode}."

    normalized = output.upper()
    if "SUCCEEDED" in normalized:
        return True, "Goal reported success."

    return False, "Did not receive a success status from the action server."


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Send alternating dock/undock goals to the Autodock action server. "
            "Stops immediately if any goal fails."
        )
    )
    parser.add_argument(
        "-n",
        "--cycles",
        type=int,
        default=30,
        help="Number of dock+undock cycles to run (default: 30).",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=5.0,
        help="Delay in seconds between successive commands (default: 5).",
    )
    args = parser.parse_args()

    if args.cycles <= 0:
        print("[ERROR] Number of cycles must be positive.", file=sys.stderr)
        return 1

    print(
        f"[INFO] Starting dock/undock test for {args.cycles} cycles with {args.delay:.1f}s delay.",
        flush=True,
    )

    for cycle in range(1, args.cycles + 1):
        print(f"[INFO] Cycle {cycle}/{args.cycles}: Docking...", flush=True)
        success, message = run_goal(is_dock=True)
        if not success:
            print(f"[ERROR] Dock cycle {cycle} failed: {message}", file=sys.stderr)
            return 1
        time.sleep(args.delay)

        print(f"[INFO] Cycle {cycle}/{args.cycles}: Undocking...", flush=True)
        success, message = run_goal(is_dock=False)
        if not success:
            print(f"[ERROR] Undock cycle {cycle} failed: {message}", file=sys.stderr)
            return 1

        if cycle < args.cycles:
            time.sleep(args.delay)

    print("[INFO] Completed all requested cycles successfully.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user.", flush=True)
        sys.exit(130)
