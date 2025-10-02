#!/usr/bin/env python3

import os
import sys
import yaml
from PIL import Image


def convert_pgm_to_png(pgm_path):
    png_path = pgm_path.replace(".pgm", ".png")
    with Image.open(pgm_path) as im:
        im.save(png_path)
    return png_path


def read_map_yaml(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    resolution = data.get("resolution", 0.05)
    origin = data.get("origin", [0.0, 0.0, 0.0])
    return resolution, origin


def generate_building_yaml(building_yaml_path, image_filename, resolution, origin):
    building_data = {
        "levels": {
            "L1": {
                "drawing": {
                    "filename": image_filename,
                    "meters_per_pixel": resolution,
                    "offset": {
                        "x": origin[0],
                        "y": origin[1]
                    }
                },
                "elevation": 0.0,
                "vertices": [],
                "lanes": [],
                "layers": {}
            }
        },
        "name": "building",
        "coordinate_system": "reference_image"
    }

    with open(building_yaml_path, "w") as f:
        yaml.dump(building_data, f, sort_keys=False)
    print(f"✅ Created building file: {building_yaml_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 convert_pgm_to_building_yaml.py <map.yaml>")
        sys.exit(1)

    map_yaml_path = sys.argv[1]
    if not map_yaml_path.endswith(".yaml"):
        print("❌ Please provide a valid .yaml file (not .pgm)")
        sys.exit(1)

    map_dir = os.path.dirname(map_yaml_path)
    with open(map_yaml_path, "r") as f:
        map_yaml = yaml.safe_load(f)

    pgm_filename = map_yaml.get("image")
    if not pgm_filename or not pgm_filename.endswith(".pgm"):
        print("❌ .yaml does not reference a .pgm file.")
        sys.exit(1)

    pgm_path = os.path.join(map_dir, pgm_filename)
    png_path = convert_pgm_to_png(pgm_path)

    # Update YAML to point to PNG
    map_yaml["image"] = os.path.basename(png_path)
    with open(map_yaml_path, "w") as f:
        yaml.dump(map_yaml, f)

    resolution, origin = read_map_yaml(map_yaml_path)

    building_yaml_path = os.path.splitext(map_yaml_path)[0] + ".building.yaml"
    generate_building_yaml(
        building_yaml_path,
        os.path.basename(png_path),
        resolution,
        origin
    )


if __name__ == "__main__":
    main()
