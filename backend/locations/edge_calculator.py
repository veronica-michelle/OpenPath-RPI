"""Fill in each edge's distance and gradient from its endpoints in locations.json.

Run from backend/:  python -m locations.edge_calculator path/to/locations.json path/to/paths.json
Rewrites paths.json in place and prints each edge it measured.

Distance is the straight-line distance in meters and is only filled in when
it is missing, so a hand-measured distance for a curved path is kept.
Gradient is always recalculated: degrees of slope going from `from` to `to`
(positive is uphill). Endpoints must name an exact entrance or path point.
Building IDs are invalid because they do not specify a physical connection.
Everything else (paved, stairs, ramp, closed) is left for a person to set.
"""

import json
import math
import sys
from pathlib import Path

from .geo import haversine_meters


def _endpoint(locations, node_id):
    """Resolve an exact door or path point without guessing a building's door."""
    if node_id in locations:
        node = locations[node_id]
        if "entrances" in node:
            raise KeyError(f"building id {node_id!r} is not a path endpoint; use an entrance id")
        return node
    for location in locations.values():
        for entrance in location.get("entrances", []):
            if entrance["id"] == node_id:
                return entrance
    raise KeyError(f"unknown node id {node_id!r}")


def measure_edge(locations, from_id, to_id):
    """Return (distance in meters, gradient in degrees) between two node ids."""
    start, end = _endpoint(locations, from_id), _endpoint(locations, to_id)
    distance = haversine_meters(*start["coordinates"], *end["coordinates"])
    rise = end["elevation"] - start["elevation"]
    gradient = math.degrees(math.atan2(rise, distance)) if distance else 0.0
    return distance, gradient


def fill_paths(locations, paths):
    """Fill in distance and gradient on every edge. Returns {edge_id: problem}."""
    problems = {}
    for edge_id, edge in paths.items():
        try:
            distance, gradient = measure_edge(locations, edge["from"], edge["to"])
        except KeyError as error:
            problems[edge_id] = error.args[0]
            continue
        if not isinstance(edge.get("distance"), (int, float)):
            edge["distance"] = round(distance, 2)
        edge.setdefault("features", {})["gradient"] = round(gradient, 2)
    return problems


def main(argv):
    if len(argv) != 3:
        print("Usage: python -m locations.edge_calculator locations.json paths.json")
        return 1
    locations_path, paths_path = Path(argv[1]), Path(argv[2])
    with locations_path.open(encoding="utf-8") as locations_file:
        locations = json.load(locations_file)
    with paths_path.open(encoding="utf-8") as paths_file:
        paths = json.load(paths_file)

    problems = fill_paths(locations, paths)
    with paths_path.open("w", encoding="utf-8") as paths_file:
        json.dump(paths, paths_file, indent=4, ensure_ascii=False)
        paths_file.write("\n")

    for edge_id, edge in paths.items():
        if edge_id not in problems:
            print(
                f"  {edge_id}: {edge['from']} -> {edge['to']}  "
                f"{edge['distance']} m, {edge['features']['gradient']} deg"
            )
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for edge_id, problem in problems.items():
            print(f"  x {edge_id}: {problem}")
        return 1
    print(f"\nMeasured {len(paths) - len(problems)} edge(s) in {paths_path.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
