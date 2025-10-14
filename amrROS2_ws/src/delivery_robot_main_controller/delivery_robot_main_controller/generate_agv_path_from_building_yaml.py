#!/usr/bin/env python3

import os
import struct
import yaml
import math
import networkx as nx
from geometry_msgs.msg import PoseStamped


def _read_image_size(image_path):
    """Return (width, height) for PNG/PGM images without extra deps."""
    suffix = os.path.splitext(image_path)[1].lower()
    if suffix == '.png':
        with open(image_path, 'rb') as f:
            header = f.read(24)
        if header[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError(f"Unsupported PNG header in {image_path}")
        width, height = struct.unpack('>II', header[16:24])
        return float(width), float(height)
    if suffix in ('.pgm', '.ppm'):
        with open(image_path, 'rb') as f:
            magic = f.readline().strip()
            if magic not in (b'P2', b'P5'):
                raise ValueError(f"Unsupported PGM magic number {magic!r} in {image_path}")
            line = f.readline()
            while line.startswith(b'#'):
                line = f.readline()
            parts = line.strip().split()
            while len(parts) < 2:
                parts.extend(f.readline().strip().split())
            width = float(parts[0])
            height = float(parts[1])
        return width, height
    raise ValueError(f"Unsupported image format for size extraction: {image_path}")


def _load_map_yaml_values(building_yaml_path: str):
    """
    Load meters_per_pixel and offset (x, y) from the map .yaml that shares the
    same basename as the provided .building.yaml.

    meters_per_pixel := resolution
    offset := origin[0:2]

    Falls back to (1.0, (0.0, 0.0)) if not found.
    """
    meters_per_pixel = 1.0
    offset_x, offset_y = 0.0, 0.0
    image_height = None

    # Derive map yaml path: replace ".building.yaml" with ".yaml"
    base, ext = os.path.splitext(building_yaml_path)
    map_yaml_path = None
    if base.endswith('.building'):
        map_yaml_path = base[:-9] + '.yaml'  # remove '.building' then add '.yaml'
    else:
        # Fallback: try same directory, same stem (without last extension), add .yaml
        stem = os.path.basename(base)
        map_yaml_path = os.path.join(os.path.dirname(building_yaml_path), f"{stem}.yaml")

    try:
        if os.path.exists(map_yaml_path):
            with open(map_yaml_path, 'r') as f:
                map_data = yaml.safe_load(f) or {}
            # resolution -> meters_per_pixel
            if isinstance(map_data.get('resolution'), (int, float)):
                meters_per_pixel = float(map_data['resolution'])
            # origin -> [x, y, yaw]
            origin = map_data.get('origin')
            if isinstance(origin, (list, tuple)) and len(origin) >= 2:
                offset_x = float(origin[0])
                offset_y = float(origin[1])
            image_ref = map_data.get('image')
            if image_ref:
                image_path = os.path.join(os.path.dirname(map_yaml_path), image_ref)
                if os.path.exists(image_path):
                    _, image_height = _read_image_size(image_path)
    except Exception:
        # Keep defaults on any error
        pass

    return meters_per_pixel, (offset_x, offset_y), image_height


def load_graph_from_building_yaml(building_yaml_path, level_name='L1'):
    with open(building_yaml_path, 'r') as f:
        building_data = yaml.safe_load(f)

    level = building_data['levels'][level_name]
    # Load meters_per_pixel, offset, and image height from the matching map .yaml
    meters_per_pixel, (offset_x, offset_y), image_height = _load_map_yaml_values(building_yaml_path)

    vertices_raw = level['vertices']

    if 'edges' not in level and 'lanes' in level:
        edges = []
        for lane in level['lanes']:
            if isinstance(lane, list) and len(lane) >= 2:
                v1 = f'vertex_{lane[0]}'
                v2 = f'vertex_{lane[1]}'
                edges.append([v1, v2])
    else:
        edges = level.get('edges', [])

    vertex_map = {}
    for i, vertex in enumerate(vertices_raw):
        if isinstance(vertex, dict):
            key = list(vertex.keys())[0]
            value = vertex[key]
            if isinstance(value, dict):
                vertex_map[key] = (value['x'], value['y'])
            elif isinstance(value, list) and len(value) >= 2:
                vx = value[0] * meters_per_pixel + offset_x
                if image_height is not None:
                    vy = offset_y + (image_height - value[1] - 1) * meters_per_pixel
                else:
                    vy = value[1] * meters_per_pixel + offset_y
                vertex_map[key] = (vx, vy)
        elif isinstance(vertex, list) and len(vertex) >= 2:
            key = f'vertex_{i}'
            vx = vertex[0] * meters_per_pixel + offset_x
            if image_height is not None:
                vy = offset_y + (image_height - vertex[1] - 1) * meters_per_pixel
            else:
                vy = vertex[1] * meters_per_pixel + offset_y
            vertex_map[key] = (vx, vy)

    G = nx.Graph()
    for v_name, pos in vertex_map.items():
        G.add_node(v_name, pos=pos)

    for edge in edges:
        v1, v2 = edge[:2]
        if v1 in vertex_map and v2 in vertex_map:
            dist = ((vertex_map[v1][0] - vertex_map[v2][0])**2 + (vertex_map[v1][1] - vertex_map[v2][1])**2)**0.5
            G.add_edge(v1, v2, weight=dist)

    return G, vertex_map


def find_nearest_vertex(x, y, vertex_map):
    nearest = None
    min_dist = float('inf')
    for name, (vx, vy) in vertex_map.items():
        dist = ((vx - x) ** 2 + (vy - y) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            nearest = name
    return nearest


def create_pose(x, y, yaw=None, frame='map'):
    pose = PoseStamped()
    pose.header.frame_id = frame
    pose.header.stamp.sec = 0
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    if yaw is None:
        pose.pose.orientation.z = 0.0
        pose.pose.orientation.w = 1.0
    else:
        half_yaw = yaw * 0.5
        pose.pose.orientation.z = math.sin(half_yaw)
        pose.pose.orientation.w = math.cos(half_yaw)
    return pose


def compute_path_poses(building_yaml_path, start_pos, goal_pos, level_name='L1'):
    start_x, start_y = start_pos[:2]
    goal_x, goal_y = goal_pos[:2]
    goal_yaw = None
    if isinstance(goal_pos, (list, tuple)) and len(goal_pos) >= 3:
        goal_yaw = goal_pos[2]

    G, vertex_map = load_graph_from_building_yaml(building_yaml_path, level_name)
    start_wp = find_nearest_vertex(start_x, start_y, vertex_map)
    goal_wp = find_nearest_vertex(goal_x, goal_y, vertex_map)

    path_nodes = nx.shortest_path(G, source=start_wp, target=goal_wp, weight='weight')

    path_points = []
    for i, node in enumerate(path_nodes):
        if i == 0:
            path_points.append((start_x, start_y))
        elif i == len(path_nodes) - 1:
            path_points.append((goal_x, goal_y))
        else:
            path_points.append(vertex_map[node])

    yaws = []
    for i, (x, y) in enumerate(path_points):
        if i < len(path_points) - 1:
            next_x, next_y = path_points[i + 1]
            yaw = math.atan2(next_y - y, next_x - x)
        elif yaws:
            yaw = yaws[-1]
        else:
            yaw = 0.0
        yaws.append(yaw)

    if goal_yaw is not None and yaws:
        yaws[-1] = goal_yaw

    path_poses = [create_pose(x, y, yaw) for (x, y), yaw in zip(path_points, yaws)]
    return path_poses
