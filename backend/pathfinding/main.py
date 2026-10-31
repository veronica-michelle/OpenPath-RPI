import math
from pathlib import Path

import networkx as nx
import pandas as pd

# Load excel file and invididual sheets into pandas dataframes
masterData = pd.ExcelFile(Path(__file__).resolve().parents[2] / "data/ATLAS_Graph_Data.xlsx")
landmarksData = pd.read_excel(masterData, sheet_name="Landmarks")
nodesData = pd.read_excel(masterData, sheet_name="Nodes")
edgesData = pd.read_excel(masterData, sheet_name="Edges")


class Node:
    def __init__(self, name: str, latitude: float, longitude: float):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    # Use meters, including the latitude-dependent scale of longitude.
    def dist(self, other: "Node") -> float:
        lat1, lat2 = math.radians(self.latitude), math.radians(other.latitude)
        delta_lat = lat2 - lat1
        delta_lng = math.radians(other.longitude - self.longitude)
        h = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
        )
        return 6371000 * 2 * math.asin(math.sqrt(min(1, max(0, h))))


# Create a networkx graph
G = nx.Graph()

nodes = {}

# Add Landmarks and have nonzero size so we can see them on the rendered graph
for _, row in landmarksData.iterrows():
    node = Node(row["Name"], row["Latitude"], row["Longitude"])
    nodes[row["Name"]] = node
    G.add_node(row["Name"], weight=0, size=10, pos=(row["Latitude"], row["Longitude"]))

# Add Nodes and have zero size so these are not visible on the rendered graph,
# but they are still part of the networkx graph
for _, row in nodesData.iterrows():
    node = Node(row["Name"], row["Latitude"], row["Longitude"])
    nodes[row["Name"]] = node
    G.add_node(row["Name"], weight=0, size=0, pos=(row["Latitude"], row["Longitude"]))

# Add Edges and weight them by the distance between the two nodes
for _, row in edgesData.iterrows():
    # The original source workbook retains this documented misspelling.
    aliases = {"Russel Sage Dining Hall": "Russell Sage Dining Hall"}
    node1 = nodes[aliases.get(row["Node 1 Name"], row["Node 1 Name"])]
    node2 = nodes[aliases.get(row["Node 2 Name"], row["Node 2 Name"])]
    G.add_edge(node1.name, node2.name, weight=node1.dist(node2))

# Run Dijkstra's algorithm to find the shortest path between all pairs of nodes
# in the graph. This will be used to find the shortest path between any two
# landmarks.
paths = nx.all_pairs_dijkstra_path(G, weight="weight")

landmark_hits = {}

for path in paths:
    origin = path[0]
    if origin not in landmarksData["Name"].values:
        continue

    # print(f"Shortest paths from {origin}:")
    destinations = path[1]

    for destination, path in destinations.items():
        if destination not in landmarksData["Name"].values:
            continue

        # print(f"Shortest path from {origin} to {destination}: {path}")
        landmark_hits[origin] = landmark_hits.get(origin, 0) + 1

# print("\nLandmark hits:")
for landmark, hits in landmark_hits.items():
    # print(f"{landmark}: {hits} hits")
    pass


# Verify that the facts the network spat out makes sense.

try:
    assert min(landmark_hits.values()) > 0, (
        "No landmarks were hit in the paths. Check the graph and data."
    )
    assert len(landmark_hits) == len(landmarksData), (
        "Not all landmarks were hit in the paths. Check the graph and data."
    )
    assert all(hits == len(landmarksData) for hits in landmark_hits.values()), (
        "Not every landmark is connected to every other landmark. Check the graph and data."
    )
except AssertionError as e:
    print(f"The data seems to be malformed: {e}")
    raise SystemExit(1) from e
