#!/usr/bin/env python3
import argparse
import glob
import struct
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    import yaml  # PyYAML
except Exception as e:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise

import requests


def read_png_size(path: Path) -> Tuple[int, int]:
    with path.open("rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")
    width, height = struct.unpack(">II", header[16:24])
    return int(width), int(height)


def read_pgm_size(path: Path) -> Tuple[int, int]:
    with path.open("rb") as f:
        magic = f.readline().strip()
        if magic not in (b"P2", b"P5"):
            raise ValueError(f"Unsupported PGM magic number {magic!r} in {path}")
        line = f.readline()
        while line.startswith(b"#"):
            line = f.readline()
        parts = line.strip().split()
        while len(parts) < 2:
            parts.extend(f.readline().strip().split())
        width = int(parts[0])
        height = int(parts[1])
    return width, height


def get_image_size(path: Path) -> Tuple[int, int]:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return read_png_size(path)
    if suffix in (".pgm", ".ppm"):
        return read_pgm_size(path)
    raise ValueError(f"Unsupported image format for size extraction: {path}")


def candidate_map_yaml_paths(building_path: Path, image_filename: str) -> List[Path]:
    candidates: List[Path] = []
    if building_path.name.endswith(".building.yaml"):
        candidates.append(building_path.with_name(building_path.name.replace(".building.yaml", ".yaml")))
    image_stem = Path(image_filename).stem
    candidates.append(building_path.parent / f"{image_stem}.yaml")
    candidates.append(building_path.parent / f"{image_stem}.yml")
    return candidates


def load_map_metadata(building_path: Path, doc: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    info: Dict[str, Dict[str, float]] = {}
    levels = doc.get("levels", {})
    for lvl in levels.values():
        drawing = lvl.get("drawing", {})
        image_filename = drawing.get("filename")
        if not image_filename or image_filename in info:
            continue

        map_yaml_path = None
        for candidate in candidate_map_yaml_paths(building_path, image_filename):
            if candidate.is_file():
                map_yaml_path = candidate
                break
        if map_yaml_path is None:
            raise FileNotFoundError(f"Map YAML for image '{image_filename}' not found near {building_path}")

        with map_yaml_path.open("r", encoding="utf-8") as f:
            map_yaml = yaml.safe_load(f)

        resolution = map_yaml.get("resolution")
        origin = map_yaml.get("origin")
        image_ref = map_yaml.get("image")

        if resolution is None or origin is None or image_ref is None:
            raise ValueError(f"Map YAML {map_yaml_path} missing resolution/origin/image")
        if not isinstance(origin, (list, tuple)) or len(origin) < 2:
            raise ValueError(f"Map YAML {map_yaml_path} origin must have at least two values")

        origin_x = float(origin[0])
        origin_y = float(origin[1])
        resolution = float(resolution)

        image_path = (map_yaml_path.parent / image_ref).resolve()
        if not image_path.is_file():
            raise FileNotFoundError(f"Map image '{image_path}' referenced in {map_yaml_path} not found")

        width, height = get_image_size(image_path)
        info[image_filename] = {
            "resolution": resolution,
            "origin_x": origin_x,
            "origin_y": origin_y,
            "width": float(width),
            "height": float(height),
        }
    return info


def extract_named_vertices(doc: Dict[str, Any], map_info: Dict[str, Dict[str, float]], level: str = None) -> List[Tuple[str, float, float]]:
    result: List[Tuple[str, float, float]] = []
    levels = doc.get("levels", {})
    for lvl_name, lvl in levels.items():
        if level and lvl_name != level:
            continue
        drawing = lvl.get("drawing", {})
        image_filename = drawing.get("filename")
        if not image_filename:
            raise ValueError(f"Level {lvl_name} missing drawing filename")
        if image_filename not in map_info:
            raise ValueError(f"No map metadata for image '{image_filename}' (level {lvl_name})")

        meta = map_info[image_filename]
        resolution = meta["resolution"]
        origin_x = meta["origin_x"]
        origin_y = meta["origin_y"]
        image_height = meta["height"]

        vertices = lvl.get("vertices", [])
        for v in vertices:
            if not isinstance(v, list) or len(v) < 4:
                continue
            name = v[3]
            if not name:
                continue
            try:
                px = float(v[0])
                py = float(v[1])
            except Exception:
                continue
            x_m = origin_x + px * resolution
            y_m = origin_y + (image_height - py - 1) * resolution
            result.append((str(name), x_m, y_m))
    return result


def post_station(
    base_url: str,
    name: str,
    x: float,
    y: float,
    heading: float = 0.0,
    device_ip: str = "",
    status: str = "enable",
    timeout: float = 5.0,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/api/station/add"
    data = {
        "name": name,
        "x": x,
        "y": y,
        "heading": heading,
        "deviceIP": device_ip,
        "status": status,
    }
    files = {"image": ("", b"")}
    r = requests.post(url, data=data, files=files, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return {"raw": r.text}


def main():
    parser = argparse.ArgumentParser(description="Import stations from *.building.yaml named vertices")
    parser.add_argument("path", nargs="?", default="maps/*.building.yaml", help="Path or glob to .building.yaml file(s)")
    parser.add_argument("--base-url", default="http://localhost:8080", help="API base URL (default: http://localhost:8080)")
    parser.add_argument("--level", help="Level name to import (if omitted, import all levels)")
    parser.add_argument("--dry-run", action="store_true", help="Print stations without posting to API")
    parser.add_argument("--heading", type=float, default=0.0, help="Heading (deg/rad as expected by API) for all stations, default 0.0")
    parser.add_argument("--device-ip", default="", help="Device IP to assign to each station (default empty string)")
    parser.add_argument("--status", default="enable", help="Station status value (default 'enable')")
    args = parser.parse_args()

    files = sorted(glob.glob(args.path))
    if not files:
        print(f"No files matched: {args.path}", file=sys.stderr)
        sys.exit(1)

    all_stations: List[Tuple[str, float, float]] = []
    for fpath in files:
        building_path = Path(fpath)
        with building_path.open("r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        map_info = load_map_metadata(building_path, doc)
        vertices = extract_named_vertices(doc, map_info, level=args.level)
        print(f"Found {len(vertices)} named vertices in {fpath}")
        all_stations.extend(vertices)

    if not all_stations:
        print("No named vertices found.")
        return

    # Deduplicate by name keeping first occurrence
    seen = set()
    unique_stations: List[Tuple[str, float, float]] = []
    for name, x, y in all_stations:
        if name in seen:
            continue
        seen.add(name)
        unique_stations.append((name, x, y))

    print(f"Importing {len(unique_stations)} unique stations")
    for name, x, y in unique_stations:
        if args.dry_run:
            print(f"DRY-RUN add: name={name} x={x:.6f} y={y:.6f} heading={args.heading}")
            continue
        try:
            resp = post_station(
                args.base_url,
                name,
                x,
                y,
                heading=args.heading,
                device_ip=args.device_ip,
                status=args.status,
            )
            print(f"Added station '{name}': {resp}")
        except requests.HTTPError as e:
            print(f"Failed to add '{name}': HTTP {e.response.status_code} {e.response.text}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to add '{name}': {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
