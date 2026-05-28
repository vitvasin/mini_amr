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
    use_json: bool = True,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/api/station/add"
    payload = {
        "name": name,
        "x": x,
        "y": y,
        "heading": heading,
        "deviceIP": device_ip,
        "status": status,
    }
    if use_json:
        r = requests.post(url, json=payload, timeout=timeout)
    else:
        files = {"image": ("", b"")}
        r = requests.post(url, data=payload, files=files, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return {"raw": r.text}


def get_station_list(base_url: str, timeout: float = 5.0) -> List[Dict[str, Any]]:
    url = base_url.rstrip("/") + "/api/station/list"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    try:
        payload = r.json()
    except ValueError:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "stations", "items", "result"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def _station_id(entry: Dict[str, Any]) -> Any:
    for key in ("id", "_id", "stationId", "station_id"):
        if key in entry:
            return entry[key]
    return None


def _station_name(entry: Dict[str, Any]) -> str:
    for key in ("name", "stationName", "station_name"):
        if key in entry and entry[key] is not None:
            return str(entry[key])
    return ""


def remove_station(base_url: str, station_id: Any, timeout: float = 5.0) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/api/station/remove"
    r = requests.post(url, json={"id": station_id}, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return {"raw": r.text}


def main():
    parser = argparse.ArgumentParser(description="Import stations from *.building.yaml named vertices")
    parser.add_argument("path", nargs="?", default="maps/*.building.yaml", help="Path or glob to .building.yaml file(s)")
    parser.add_argument("--base-url", default="http://localhost:3000", help="API base URL (default: http://localhost:3000)")
    parser.add_argument("--level", help="Level name to import (if omitted, import all levels)")
    parser.add_argument("--dry-run", action="store_true", help="Print stations without posting to API")
    parser.add_argument("--heading", type=float, default=0.0, help="Heading (deg/rad as expected by API) for all stations, default 0.0")
    parser.add_argument("--device-ip", default="", help="Device IP to assign to each station (default empty string)")
    parser.add_argument("--status", default="enable", help="Station status value (default 'enable')")
    parser.add_argument("--add", help="Add a single station by name")
    parser.add_argument("--addall", action="store_true", help="Add all stations from the provided building file(s)")
    parser.add_argument("--remove", help="Remove a single station by name (from API, no map lookup)")
    parser.add_argument("--removeall", action="store_true", help="Remove all stations from the API")
    parser.add_argument(
        "--update",
        help="Update a single station's coordinates by name. Keeps existing name and heading from the API.",
    )
    parser.add_argument(
        "--legacy-upload",
        action="store_true",
        help="Use multipart/form-data upload (for older API that expects an image field)",
    )
    args = parser.parse_args()

    action_flags = {
        "add": bool(args.add),
        "addall": bool(args.addall),
        "remove": bool(args.remove),
        "removeall": bool(args.removeall),
        "update": bool(args.update),
    }
    chosen_actions = [key for key, enabled in action_flags.items() if enabled]
    if len(chosen_actions) > 1:
        parser.error("Please choose only one of --add, --addall, --remove, --removeall, --update")
    action = chosen_actions[0] if chosen_actions else "addall"
    target_name = args.add or args.remove or args.update

    unique_stations: List[Tuple[str, float, float]] = []
    if action in {"add", "addall", "update"}:
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

        seen = set()
        for name, x, y in all_stations:
            if name in seen:
                continue
            seen.add(name)
            unique_stations.append((name, x, y))

        if action == "add":
            unique_stations = [s for s in unique_stations if s[0] == target_name]
            if not unique_stations:
                print(f"Station '{target_name}' not found in provided map data.", file=sys.stderr)
                return
            print(f"Adding single station: {unique_stations[0][0]}")

    if action == "removeall":
        stations = get_station_list(args.base_url)
        if not stations:
            print("No stations to remove.")
            return
        for entry in stations:
            name = _station_name(entry) or "<unknown>"
            sid = _station_id(entry)
            if sid is None:
                print(f"Skip removing '{name}': no station id", file=sys.stderr)
                continue
            if args.dry_run:
                print(f"DRY-RUN remove: name={name} id={sid}")
                continue
            try:
                resp = remove_station(args.base_url, sid)
                print(f"Removed station '{name}' (id={sid}): {resp}")
            except requests.HTTPError as e:
                print(f"Failed to remove '{name}': HTTP {e.response.status_code} {e.response.text}", file=sys.stderr)
            except Exception as e:
                print(f"Failed to remove '{name}': {e}", file=sys.stderr)
        return

    if action == "remove":
        stations = get_station_list(args.base_url)
        entry = next((s for s in stations if _station_name(s) == target_name), None)
        if entry is None:
            print(f"Station '{target_name}' not found in API list.", file=sys.stderr)
            return
        sid = _station_id(entry)
        if sid is None:
            print(f"Station '{target_name}' does not include an id; cannot remove.", file=sys.stderr)
            return
        if args.dry_run:
            print(f"DRY-RUN remove: name={target_name} id={sid}")
            return
        try:
            resp = remove_station(args.base_url, sid)
            print(f"Removed station '{target_name}' (id={sid}): {resp}")
        except requests.HTTPError as e:
            print(f"Failed to remove '{target_name}': HTTP {e.response.status_code} {e.response.text}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to remove '{target_name}': {e}", file=sys.stderr)
        return

    if action == "update":
        stations = get_station_list(args.base_url)
        entry = next((s for s in stations if _station_name(s) == target_name), None)
        if entry is None:
            print(f"Station '{target_name}' not found in API list; cannot update.", file=sys.stderr)
            return
        sid = _station_id(entry)
        if sid is None:
            print(f"Station '{target_name}' does not include an id; cannot update.", file=sys.stderr)
            return
        coord = next((s for s in unique_stations if s[0] == target_name), None)
        if coord is None:
            print(f"Station '{target_name}' not found in provided map data; cannot update.", file=sys.stderr)
            return
        _, new_x, new_y = coord
        preserved_heading = entry.get("heading", args.heading)
        preserved_device = entry.get("deviceIP", entry.get("device_ip", args.device_ip))
        preserved_status = entry.get("status", args.status)
        if args.dry_run:
            print(
                f"DRY-RUN update: name={target_name} id={sid} x={new_x:.6f} y={new_y:.6f} heading(stay)={preserved_heading}"
            )
            return
        try:
            remove_station(args.base_url, sid)
            resp = post_station(
                args.base_url,
                target_name,
                new_x,
                new_y,
                heading=preserved_heading,
                device_ip=preserved_device,
                status=preserved_status,
                use_json=not args.legacy_upload,
            )
            print(f"Updated station '{target_name}' (id was {sid}): {resp}")
        except requests.HTTPError as e:
            print(f"Failed to update '{target_name}': HTTP {e.response.status_code} {e.response.text}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to update '{target_name}': {e}", file=sys.stderr)
        return

    # Default: add all (or single already filtered)
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
                use_json=not args.legacy_upload,
            )
            print(f"Added station '{name}': {resp}")
        except requests.HTTPError as e:
            print(f"Failed to add '{name}': HTTP {e.response.status_code} {e.response.text}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to add '{name}': {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
