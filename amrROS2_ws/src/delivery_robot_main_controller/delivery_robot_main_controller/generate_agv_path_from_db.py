#!/usr/bin/env python3
"""
compute_path_poses_from_db
--------------------------
Drop-in replacement for compute_path_poses() that builds the navigation graph
from the SQLite-backed REST API (stations + routes) instead of a .building.yaml file.

Return signature is identical to the yaml version:
    path_poses, vertex_map, path_nodes, start_wp, goal_wp
"""

import math
import networkx as nx
from geometry_msgs.msg import PoseStamped
from . import api_client


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _create_pose(x, y, yaw=None, frame='map'):
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


def _find_nearest_vertex(x, y, vertex_map):
    nearest = None
    min_dist = float('inf')
    for name, (vx, vy) in vertex_map.items():
        dist = math.sqrt((vx - x) ** 2 + (vy - y) ** 2)
        if dist < min_dist:
            min_dist = dist
            nearest = name
    return nearest


def _interpolate_path(path_points, step=0.5):
    """Insert intermediate points every *step* metres along each segment."""
    if len(path_points) < 2:
        return list(path_points)
    dense = []
    for i in range(len(path_points) - 1):
        x1, y1 = path_points[i]
        x2, y2 = path_points[i + 1]
        seg_len = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        n = max(1, math.ceil(seg_len / step))
        for j in range(n):
            t = j / n
            dense.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
    dense.append(path_points[-1])
    return dense


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_graph_from_db():
    """
    Fetch stations and routes from the database API and build a networkx DiGraph.

    Returns
    -------
    G : nx.DiGraph
        Nodes keyed by str(station_id).  One-way routes become a single directed
        edge; bidirectional routes become two directed edges.
    vertex_map : dict
        {str(station_id): (x, y)}  — only enabled stations.
    """
    stations_resp = api_client.get_station_list()
    stations = stations_resp.get('data', [])

    routes_resp = api_client.get_route_list()
    routes = routes_resp.get('data', [])

    # Build vertex_map (skip disabled stations)
    vertex_map = {}
    for s in stations:
        if s.get('status') == 'disable':
            continue
        sid = str(s['_id'])
        vertex_map[sid] = (float(s['x']), float(s['y']))

    # Build directed graph
    G = nx.DiGraph()
    for sid, pos in vertex_map.items():
        G.add_node(sid, pos=pos)

    for route in routes:
        frm = str(route['from_station_id'])
        to  = str(route['to_station_id'])
        if frm not in vertex_map or to not in vertex_map:
            continue
        fx, fy = vertex_map[frm]
        tx, ty = vertex_map[to]
        dist = math.sqrt((tx - fx) ** 2 + (ty - fy) ** 2)
        speed = float(route.get('speed_limit') or 0)
        # Weight = travel time when speed > 0, otherwise Euclidean distance
        weight = (dist / speed) if speed > 0 else dist
        G.add_edge(frm, to, weight=weight)
        if int(route.get('bidirectional', 1)) == 1:
            G.add_edge(to, frm, weight=weight)

    return G, vertex_map


def compute_path_poses_from_db(start_pos, goal_pos, blocked_lanes=None):
    """
    Compute a waypoint path from *start_pos* to *goal_pos* using the route graph
    stored in the database.

    Parameters
    ----------
    start_pos : (x, y)
        Current robot position in the map frame.
    goal_pos  : (x, y) or (x, y, yaw)
        Target position; yaw is applied to the final waypoint if provided.
    blocked_lanes : iterable of (from_id, to_id), optional
        Station-ID pairs (strings or ints) whose edge should be removed before
        pathfinding.  Mirrors the blocked_lanes parameter of the yaml version.

    Returns
    -------
    path_poses  : list[PoseStamped]
    vertex_map  : dict  {str(station_id): (x, y)}
    path_nodes  : list[str]  station IDs along the path
    start_wp    : str   nearest station ID to start_pos
    goal_wp     : str   nearest station ID to goal_pos
    """
    start_x, start_y = float(start_pos[0]), float(start_pos[1])
    goal_x,  goal_y  = float(goal_pos[0]),  float(goal_pos[1])
    goal_yaw = float(goal_pos[2]) if len(goal_pos) >= 3 else None

    G, vertex_map = load_graph_from_db()

    if not vertex_map:
        return [], {}, [], None, None

    # Remove blocked lanes
    if blocked_lanes:
        for lane in blocked_lanes:
            if isinstance(lane, (list, tuple)) and len(lane) >= 2:
                v1, v2 = str(lane[0]), str(lane[1])
                if G.has_edge(v1, v2):
                    G.remove_edge(v1, v2)

    start_wp = _find_nearest_vertex(start_x, start_y, vertex_map)
    goal_wp  = _find_nearest_vertex(goal_x,  goal_y,  vertex_map)

    try:
        path_nodes = nx.shortest_path(G, source=start_wp, target=goal_wp, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return [], vertex_map, [], start_wp, goal_wp

    # Build coordinate list: actual start -> nearest graph entry -> ... -> nearest graph exit -> actual goal
    path_points = [(start_x, start_y)]
    for node in path_nodes:
        point = vertex_map[node]
        if path_points[-1] != point:
            path_points.append(point)
    goal_point = (goal_x, goal_y)
    if path_points[-1] != goal_point:
        path_points.append(goal_point)

    # Densify path so NAV2 cannot deviate far between waypoints
    path_points = _interpolate_path(path_points, step=0.5)

    # Compute heading for each waypoint (face toward next point)
    yaws = []
    for i, (x, y) in enumerate(path_points):
        if i < len(path_points) - 1:
            nx_, ny_ = path_points[i + 1]
            yaw = math.atan2(ny_ - y, nx_ - x)
        elif yaws:
            yaw = yaws[-1]
        else:
            yaw = 0.0
        yaws.append(yaw)

    # Override final heading with the requested goal yaw
    if goal_yaw is not None and yaws:
        yaws[-1] = goal_yaw

    path_poses = [_create_pose(x, y, yaw) for (x, y), yaw in zip(path_points, yaws)]
    return path_poses, vertex_map, path_nodes, start_wp, goal_wp
