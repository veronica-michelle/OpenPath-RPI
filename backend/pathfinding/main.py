import json

import networkx as nx

try:
    with open("../../data/locations.json") as f:
        locations = json.load(f)
except FileNotFoundError:
    print("Location data file not found.")
    locations = {}

try:
    with open("../../data/paths.json") as f:
        paths = json.load(f)
except FileNotFoundError:
    print("Path data file not found.")
    paths = {}


class Node:
    def __init__(self, name: str, latitude: float, longitude: float):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    # Should be close enough that the curvature of the earth doesn't matter for our purposes
    # Should add more filters in later weeks (i.e. accessibility, stairs, ramps, etc.)
    def dist(self, other: "Node") -> float:
        return (
            (self.latitude - other.latitude) ** 2 + (self.longitude - other.longitude) ** 2
        ) ** 0.5


# Create a networkx graph
G = nx.Graph()

nodes = {}

# Map of entrance ID to building name for easy lookup
endpoints = {}

for _, location_data in locations.items():
    # Buildings have a "name" field, while nodes do not.
    # We will use this to differentiate between the two.
    if "name" in location_data:
        name = location_data["name"]

        location_id = location_data["id"]
        endpoints[location_id] = name
        lat, lon = location_data["coordinates"]
        node = Node(location_id, lat, lon)
        nodes[location_id] = node
        G.add_node(node, weight=0, size=0, pos=(lat, lon))

        for entrance in location_data["entrances"]:
            entrance_id = entrance["id"]
            lat, lon = entrance["coordinates"]

            node = Node(entrance_id, lat, lon)

            nodes[entrance_id] = node
            G.add_node(node, weight=0, size=0, pos=(lat, lon))
    else:
        node_id = location_data["id"]
        lat, lon = location_data["coordinates"]

        node = Node(node_id, lat, lon)

        nodes[node_id] = node
        G.add_node(node, weight=0, size=0, pos=(lat, lon))

# Add Edges and weight them by the distance between the two nodes
for _, path in paths.items():
    from_node = nodes[path["from"]]
    to_node = nodes[path["to"]]
    G.add_edge(from_node, to_node, weight=from_node.dist(to_node))

# Calculate weighted shortest paths using Dijkstra
paths = dict(nx.all_pairs_dijkstra_path(G, weight="weight"))

landmark_hits = {}

for origin, destinations in paths.items():
    origin_id = origin.name

    if origin_id not in endpoints:
        continue

    for destination, path in destinations.items():
        destination_id = destination.name

        if origin_id == destination_id:
            continue

        # Not an endpoint we want.
        if destination_id not in endpoints:
            continue

        origin_name = endpoints[origin_id]
        destination_name = endpoints[destination_id]

        print(
            f"Shortest path from {origin_name} "
            f"to {destination_name}: "
            f"{[node.name for node in path]}"
        )

        landmark_hits[origin_id] = landmark_hits.get(origin_id, 0) + 1

print("\nLandmark hits:")
for landmark, hits in landmark_hits.items():
    landmark_name = endpoints[landmark]
    print(f"{landmark_name}: {hits} hits")
    pass


# Verify that the facts the network spat out makes sense.

try:
    assert min(landmark_hits.values()) > 0, (
        "No landmarks were hit in the paths. Check the graph and data."
    )
    assert max(landmark_hits.values()) < len(endpoints), (
        "Some landmarks were hit too many times. Check the graph and data."
    )
    assert len(landmark_hits) == len(endpoints), (
        "Not all landmarks were hit in the paths. Check the graph and data."
    )
    assert min(landmark_hits.values()) == max(landmark_hits.values()), (
        "Landmarks were hit an unequal number of times. Check the graph and data."
    )
except AssertionError as e:
    print(f"The data seems to be malformed: {e}")
