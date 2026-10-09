"""Access to the provisional JSON campus graph and graph-based routes.

The JSON shape is an adapter for the current UI and should be aligned with
the team's finalized data organization before it is treated as permanent.
"""

import json
import math
from functools import lru_cache
from pathlib import Path

from .geo import haversine_meters

GRAPH_PATH = Path(__file__).with_name("graph.json")
FEET_PER_METER = 3.28084
WALK_SPEED_MPH = 2.5


@lru_cache(maxsize=1)
def get_graph():
    with GRAPH_PATH.open(encoding="utf-8") as graph_file:
        return json.load(graph_file)


def get_locations():
    return [node for node in get_graph()["nodes"] if node["type"] == "location"]


def _bearing(a, b):
    lat1, lat2 = math.radians(a["lat"]), math.radians(b["lat"])
    delta_lng = math.radians(b["lng"] - a["lng"])
    y = math.sin(delta_lng) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lng)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _build_maneuvers(points):
    distances = [0]
    for before, after in zip(points, points[1:]):
        distances.append(distances[-1] + haversine_meters(
            before["lat"], before["lng"], after["lat"], after["lng"]
        ) * FEET_PER_METER)

    maneuvers = []
    for index in range(1, len(points) - 1):
        incoming = _bearing(points[index - 1], points[index])
        outgoing = _bearing(points[index], points[index + 1])
        delta = (outgoing - incoming + 180) % 360 - 180
        if delta <= -180:
            delta += 360
        magnitude = abs(delta)
        if magnitude < 20:
            continue
        turn_magnitude = "slight" if magnitude < 45 else "sharp" if magnitude >= 135 else None
        maneuvers.append({
            "type": "turn",
            "direction": "right" if delta > 0 else "left",
            "magnitude": turn_magnitude,
            "atDistance": distances[index],
        })
    maneuvers.append({"type": "arrive", "atDistance": distances[-1]})
    return maneuvers


def _find_node_path(start_id, destination_id, avoid_stairs):
    """Small Dijkstra adapter, mirroring the current frontend behavior.

    Replace this internal implementation with the team's routing service
    once its graph interface is finalized; keep the HTTP response contract.
    """
    graph = get_graph()
    nodes = {node["id"]: node for node in graph["nodes"]}
    if start_id not in nodes or destination_id not in nodes:
        return None

    adjacency = {node_id: [] for node_id in nodes}
    for edge in graph["edges"]:
        edge_type = edge.get("type", "path")
        if edge_type == "construction" or (avoid_stairs and edge_type == "stairs"):
            continue
        a, b = nodes.get(edge["a"]), nodes.get(edge["b"])
        if not a or not b:
            continue
        weight = haversine_meters(a["lat"], a["lng"], b["lat"], b["lng"])
        adjacency[a["id"]].append((b["id"], weight, edge))
        adjacency[b["id"]].append((a["id"], weight, edge))

    distances = {node_id: math.inf for node_id in nodes}
    previous = {}
    unvisited = set(nodes)
    distances[start_id] = 0

    while unvisited:
        current = min(unvisited, key=distances.get)
        if math.isinf(distances[current]):
            break
        unvisited.remove(current)
        if current == destination_id:
            break
        for neighbor_id, edge_distance, edge in adjacency[current]:
            if neighbor_id not in unvisited:
                continue
            candidate = distances[current] + edge_distance
            if candidate < distances[neighbor_id]:
                distances[neighbor_id] = candidate
                previous[neighbor_id] = (current, edge)

    if start_id != destination_id and destination_id not in previous:
        return None

    node_ids = [destination_id]
    edges = []
    while node_ids[-1] != start_id:
        parent, edge = previous[node_ids[-1]]
        edges.append(edge)
        node_ids.append(parent)
    node_ids.reverse()
    edges.reverse()
    return node_ids, edges, nodes


def find_route(start_id, destination_id, avoid_stairs=False,
               start_entrance_id="", destination_entrance_id=""):
    result = _find_node_path(start_id, destination_id, avoid_stairs)
    if result is None or start_id == destination_id:
        return None

    node_ids, edges, nodes = result
    points = [{"lat": nodes[node_id]["lat"], "lng": nodes[node_id]["lng"]} for node_id in node_ids]
    for point, location_id, entrance_id in (
        (points[0], start_id, start_entrance_id),
        (points[-1], destination_id, destination_entrance_id),
    ):
        entrance = next(
            (item for item in nodes[location_id].get("entrances", []) if item["id"] == entrance_id),
            None,
        )
        if entrance:
            point.update(lat=entrance["lat"], lng=entrance["lng"])

    distance_m = sum(
        haversine_meters(a["lat"], a["lng"], b["lat"], b["lng"])
        for a, b in zip(points, points[1:])
    )
    elevation_gain = 0
    elevation_loss = 0
    for before, after in zip(node_ids, node_ids[1:]):
        delta = (nodes[after].get("elevation") or 0) - (nodes[before].get("elevation") or 0)
        if delta > 0:
            elevation_gain += delta
        else:
            elevation_loss -= delta

    distance_ft = distance_m * FEET_PER_METER
    minutes = max(1, round(distance_m / 1609.344 / WALK_SPEED_MPH * 60))
    grade = elevation_gain / distance_ft if distance_ft else 0
    destination_name = nodes[destination_id]["name"]
    maneuvers = _build_maneuvers(points)
    return {
        "nodeIds": node_ids,
        "points": points,
        "route_points": points,
        "usedStairs": any(edge.get("type") == "stairs" for edge in edges),
        "distanceFt": distance_ft,
        "total_distance_m": distance_m,
        "elevationGainFt": elevation_gain,
        "elevationLossFt": elevation_loss,
        "minutes": minutes,
        "steepness": "steep" if elevation_gain > 0 and grade >= 0.05 else "flat",
        "directions": [f"Head toward {destination_name}."],
        "maneuvers": maneuvers,
        "accessibility_notes": [
            "Campus paths and accessibility details are provisional and have not been verified on site."
        ],
    }
