#!/usr/bin/env python3

"""Utility script to probe AGV path generation outside the ROS node."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from networkx.exception import NetworkXNoPath


def _bootstrap_sys_path():
    """Ensure the workspace packages are importable when running stand-alone."""
    ws_root = Path(__file__).resolve().parents[1]

    # Prefer source tree for rapid testing
    for rel in ("src/delivery_robot_main_controller", "src"):
        src_path = ws_root / rel
        if src_path.is_dir():
            src_str = str(src_path)
            if src_str not in sys.path:
                sys.path.insert(0, src_str)

    # Also add install tree if available (after source paths)
    install_lib = ws_root / "install" / "delivery_robot_main_controller" / "lib"
    if install_lib.is_dir():
        for site in install_lib.glob("python*/site-packages"):
            site_str = str(site)
            if site_str not in sys.path:
                sys.path.insert(0, site_str)


_bootstrap_sys_path()

from delivery_robot_main_controller.generate_agv_path_from_building_yaml import (  # noqa: E402
    compute_path_poses,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute an AGV path using building + map YAML files",
    )

    workspace_root = Path(__file__).resolve().parent.parent
    default_building = workspace_root / "maps" / "NECTEC_4th_Floor.building.yaml"

    parser.add_argument(
        "--building",
        type=Path,
        default=default_building,
        help=f"Path to .building.yaml file (default: {default_building})",
    )
    parser.add_argument(
        "--level",
        default="L1",
        help="Level name inside the building YAML (default: L1)",
    )
    parser.add_argument(
        "--start",
        type=float,
        nargs=2,
        metavar=("X", "Y"),
        required=True,
        help="Start position in map coordinates (meters)",
    )
    parser.add_argument(
        "--goal",
        type=float,
        nargs=2,
        metavar=("X", "Y"),
        required=True,
        help="Goal position in map coordinates (meters)",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    building_yaml = args.building.resolve()
    if not building_yaml.is_file():
        print(f"[ERROR] Building YAML not found: {building_yaml}", file=sys.stderr)
        return 2

    start_pos = tuple(args.start)
    goal_pos = tuple(args.goal)

    print(f"[INFO] Building YAML: {building_yaml}")
    print(f"[INFO] Level: {args.level}")
    print(f"[INFO] Start position: {start_pos}")
    print(f"[INFO] Goal position: {goal_pos}")

    try:
        path_poses = compute_path_poses(
            str(building_yaml),
            start_pos,
            goal_pos,
            level_name=args.level,
        )
    except NetworkXNoPath as exc:
        print(f"[ERROR] No path found: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[ERROR] Unexpected failure: {exc}", file=sys.stderr)
        return 4

    if not path_poses:
        print("[WARN] No poses generated.")
        return 5

    print(f"[INFO] Generated {len(path_poses)} poses:")
    for idx, pose in enumerate(path_poses):
        px = pose.pose.position.x
        py = pose.pose.position.y
        print(f"  #{idx:02d}: x={px:.3f} m, y={py:.3f} m")

    return 0


if __name__ == "__main__":
    sys.exit(main())
