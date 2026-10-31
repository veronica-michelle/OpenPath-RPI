"""Read the 2 campus data files and prepare map data for the app.

locations.json holds buildings, entrances, and points along paths.
paths.json holds the connections between building or path-point IDs.

The app expects a list of nodes and a list of edges, so this file translates
the saved fields into that shape and preserves existing route behavior and
metadata.

The route distances and current summary use meters and feet in different areas.
The data loader keeps the source elevation in meters and also supplies the feet
value the current summary expects. A path without a measured distance is
estimated from the coordinates of its endpoints during route generation.
"""

import json
import logging
import math
import os
from functools import lru_cache
from pathlib import Path

from .geo import haversine_meters

# Use the team's shared data in both local development and Docker.
DATA_PATH = Path(os.environ.get("OPENPATH_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
LOCATIONS_PATH = DATA_PATH / "locations.json"
PATHS_PATH = DATA_PATH / "paths.json"
PRACTICE_DATA_PATH = Path(__file__).with_name("practice_data")
FEET_PER_METER = 3.28084
WALK_SPEED_MPH = 2.5
logger = logging.getLogger(__name__)


def get_graph():
    # Check file dates so edits to map data appear without restarting Django.
    return _get_graph(
        LOCATIONS_PATH,
        PATHS_PATH,
        LOCATIONS_PATH.stat().st_mtime_ns,
        PATHS_PATH.stat().st_mtime_ns,
    )


@lru_cache(maxsize=1)
def _get_graph(locations_path, paths_path, locations_modified, paths_modified):
    graph = load_graph(locations_path, paths_path)
    node_ids = {node["id"] for node in graph["nodes"]}
    edges = []
    for edge in graph["edges"]:
        if edge["a"] not in node_ids or edge["b"] not in node_ids:
            # Ignore broken links here so the map still shows valid data.
            logger.warning(
                "Skipping path %s: endpoint does not exist (%s -> %s)",
                edge["id"],
                edge["a"],
                edge["b"],
            )
            continue
        edges.append(edge)
    return {**graph, "edges": edges}


# Maintains elevation in meters and in feet value
def _point_fields(point):
    lat, lng = point["coordinates"]
    elevation = point["elevation"]
    for name, value in (("latitude", lat), ("longitude", lng), ("elevation", elevation)):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"{point.get('id')}: {name} must be a finite number")
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        raise ValueError(f"{point.get('id')}: coordinates are outside latitude/longitude bounds")
    return {
        "lat": lat,
        "lng": lng,
        "elevation_m": point["elevation"],
        # Keep meters above, and give the current route summary feet.
        "elevation": point["elevation"] * FEET_PER_METER,
    }


"""Turns the 2 saved objects into the node and edge lists used by routes.
Edges connect building IDs or path-point IDs. A building starts at its first
entrance unless the request names another entrance. Feature, details, and other
saved fields remain attached to the returned items. If a path has no distance,
the route finder estimates a distance from its endpoints' locations.
"""


def load_graph(locations_path, paths_path):

    with Path(locations_path).open(encoding="utf-8") as locations_file:
        locations = json.load(locations_file)
    with Path(paths_path).open(encoding="utf-8") as paths_file:
        paths = json.load(paths_file)
    if not isinstance(locations, dict):
        raise ValueError("locations.json must be a JSON object keyed by node IDs")
    if not isinstance(paths, dict):
        raise ValueError(
            "paths.json must be a JSON object keyed by unique edge IDs, "
            'such as {"E0001": {...}}, not an array. Use {} for no paths.'
        )

    nodes = []
    for node_id, location in locations.items():
        if location.get("id") != node_id:
            raise ValueError(f"location key {node_id!r} does not match its id")
        if "entrances" in location:
            if not location["entrances"]:
                raise ValueError(f"Building {location['id']!r} needs at least one entrance")
            entrances = [
                {
                    **entrance,
                    **_point_fields(entrance),
                    "label": entrance.get("label", entrance["id"]),
                    "accessible": entrance["features"]["accessible"],
                }
                for entrance in location["entrances"]
            ]
            nodes.append(
                {
                    **location,
                    **_point_fields(location["entrances"][0]),
                    "type": "location",
                    "entrances": entrances,
                }
            )
        else:
            nodes.append({**location, **_point_fields(location), "type": "path"})

    edges = []
    for edge_id, path in paths.items():
        features = path["features"]
        distance = path.get("distance")
        if distance is not None and (
            isinstance(distance, bool)
            or not isinstance(distance, (int, float))
            or not math.isfinite(distance)
            or distance < 0
        ):
            raise ValueError(f"path {edge_id!r}: distance must be finite and nonnegative or null")
        edges.append(
            {
                **path,
                "id": edge_id,
                "a": path["from"],
                "b": path["to"],
                "dist": path.get("distance"),
                "type": (
                    "construction"
                    if features["closed"]
                    else "stairs"
                    if features["stairs"]
                    else "path"
                ),
            }
        )
    return {"nodes": nodes, "edges": edges}


# Read the Conceptual Graph files used by the routing practice checks.
def load_practice_graph():
    with (PRACTICE_DATA_PATH / "CGLocations.json").open(encoding="utf-8") as locations_file:
        locations = json.load(locations_file)
    with (PRACTICE_DATA_PATH / "CGPaths.json").open(encoding="utf-8") as paths_file:
        paths = json.load(paths_file)

    ids_by_name = {location["name"]: location["id"] for location in locations}
    nodes = [{**location, "lng": location["long"]} for location in locations]
    edges = [
        {
            "id": path["id"],
            "a": ids_by_name[path["from"]],
            "b": ids_by_name[path["to"]],
            "dist": path["dist"],
            "type": path["type"],
            "verified": path["verified"],
        }
        for path in paths
    ]
    return {"nodes": nodes, "edges": edges}


def get_locations():
    return [node for node in get_graph()["nodes"] if node["type"] in {"location", "entrance"}]


# Return direction of travel in degrees, measured clockwise from north.
def _bearing(a, b):
    lat1, lat2 = math.radians(a["lat"]), math.radians(b["lat"])
    delta_lng = math.radians(b["lng"] - a["lng"])
    y = math.sin(delta_lng) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lng)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


# Mark noticeable changes in direction and finish with an arrival step.
def _build_maneuvers(points, segment_distances_m=None):
    distances = [0]
    for index, (before, after) in enumerate(zip(points, points[1:])):
        distance_m = (
            segment_distances_m[index]
            if segment_distances_m is not None
            else haversine_meters(before["lat"], before["lng"], after["lat"], after["lng"])
        )
        distances.append(distances[-1] + distance_m * FEET_PER_METER)

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
        maneuvers.append(
            {
                "type": "turn",
                "direction": "right" if delta > 0 else "left",
                "magnitude": turn_magnitude,
                "atDistance": distances[index],
            }
        )
    maneuvers.append({"type": "arrive", "atDistance": distances[-1]})
    return maneuvers


# Choose the lowest-distance route while honoring stair avoidance and closures.
def _find_node_path(
    start_id,
    destination_id,
    avoid_stairs,
    include_construction=False,
    start_entrance_id="",
    destination_entrance_id="",
):
    graph = get_graph()
    nodes = {node["id"]: node for node in graph["nodes"]}
    if start_id not in nodes or destination_id not in nodes:
        return None

    # Choose doors before measuring edges so route choice and elevation agree
    # with the endpoints shown to the user. Do not modify the cached graph.
    for location_id, entrance_id in (
        (start_id, start_entrance_id),
        (destination_id, destination_entrance_id),
    ):
        location = nodes[location_id]
        entrances = location.get("entrances", [])
        entrance = next((item for item in entrances if item["id"] == entrance_id), None)
        if entrance_id and entrance is None:
            return None
        if entrance is None and entrances:
            entrance = entrances[0]
        if entrance:
            features = entrance.get("features", {})
            if avoid_stairs and features.get("stairs") and not features.get("ramp"):
                return None
            nodes[location_id] = {
                **location,
                "_entrance_stairs": bool(features.get("stairs") and not features.get("ramp")),
                **{
                    key: entrance[key]
                    for key in ("lat", "lng", "elevation", "elevation_m")
                    if key in entrance
                },
            }

    # Treat each usable edge as a 2-way connection between its node IDs.
    adjacency = {node_id: [] for node_id in nodes}
    for edge in graph["edges"]:
        edge_type = edge.get("type", "path")
        if (edge_type == "construction" and not include_construction) or (
            avoid_stairs and (edge_type == "stairs" or edge.get("features", {}).get("stairs"))
        ):
            continue
        a, b = nodes.get(edge["a"]), nodes.get(edge["b"])
        if not a or not b:
            continue
        weight = edge.get("dist")
        if weight is None:
            weight = haversine_meters(a["lat"], a["lng"], b["lat"], b["lng"])
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            continue
        if not math.isfinite(weight) or weight < 0:
            continue
        adjacency[a["id"]].append((b["id"], weight, edge))
        adjacency[b["id"]].append((a["id"], weight, edge))

    # Repeatedly visit the nearest remaining node and record its best next step.
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


# Return whether a closure is the only thing blocking the route.
def construction_blocks_route(
    start_id,
    destination_id,
    avoid_stairs=False,
    start_entrance_id="",
    destination_entrance_id="",
):
    return (
        _find_node_path(
            start_id,
            destination_id,
            avoid_stairs,
            include_construction=True,
            start_entrance_id=start_entrance_id,
            destination_entrance_id=destination_entrance_id,
        )
        is not None
    )


# Build the route response and move its endpoints to any selected entrances.
def find_route(
    start_id, destination_id, avoid_stairs=False, start_entrance_id="", destination_entrance_id=""
):
    result = _find_node_path(
        start_id,
        destination_id,
        avoid_stairs,
        start_entrance_id=start_entrance_id,
        destination_entrance_id=destination_entrance_id,
    )
    if result is None or start_id == destination_id:
        return None

    node_ids, edges, nodes = result
    points = [{"lat": nodes[node_id]["lat"], "lng": nodes[node_id]["lng"]} for node_id in node_ids]
    # Keep measured path lengths (curved paths need not equal the chord).
    segment_distances_m = [
        edge["dist"]
        if edge.get("dist") is not None
        else haversine_meters(a["lat"], a["lng"], b["lat"], b["lng"])
        for edge, a, b in zip(edges, points, points[1:])
    ]
    distance_m = sum(segment_distances_m)
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
    maneuvers = _build_maneuvers(points, segment_distances_m)
    return {
        "nodeIds": node_ids,
        "points": points,
        "route_points": points,
        "usedStairs": any(edge.get("type") == "stairs" for edge in edges)
        or any(nodes[node_id].get("_entrance_stairs") for node_id in (start_id, destination_id)),
        "distanceFt": distance_ft,
        "total_distance_m": distance_m,
        "segmentDistancesFt": [distance * FEET_PER_METER for distance in segment_distances_m],
        "elevationGainFt": elevation_gain,
        "elevationLossFt": elevation_loss,
        "minutes": minutes,
        "steepness": "steep" if elevation_gain > 0 and grade >= 0.05 else "flat",
        "directions": [f"Head toward {destination_name}."],
        "maneuvers": maneuvers,
        "accessibility_notes": [
            "Campus paths and accessibility details are provisional and have not "
            "been verified on site."
        ],
    }
