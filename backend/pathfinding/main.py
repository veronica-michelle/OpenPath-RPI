import pandas as pd
import networkx as nx


# Load excel file and invididual sheets into pandas dataframes
masterData = pd.ExcelFile("../../data/ATLAS_Graph_Data.xlsx")
landmarksData = pd.read_excel(masterData, sheet_name="Landmarks")
nodesData = pd.read_excel(masterData, sheet_name="Nodes")
edgesData = pd.read_excel(masterData, sheet_name="Edges")

class Node:
    def __init__(self, name: str, latitude: float, longitude: float):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        
    # Should be close enough that the curvature of the earth doesn't matter for our purposes
    def dist(self, other: "Node") -> float:
        return ((self.latitude - other.latitude) ** 2 + (self.longitude - other.longitude) ** 2) ** 0.5

# Create a networkx graph
G = nx.Graph()

nodes = {}

# Add Landmarks and have nonzero size so we can see them on the rendered graph
for _, row in landmarksData.iterrows():
    node = Node(row["Name"], row["Latitude"], row["Longitude"])
    nodes[row["Name"]] = node
    G.add_node(row["Name"], weight=0, size=10, pos=(row["Latitude"], row["Longitude"]))    

# Add Nodes and have zero size so these are not visible on the rendered graph, but they are still part of the networkx graph
for _, row in nodesData.iterrows():
    node = Node(row["Name"], row["Latitude"], row["Longitude"])
    nodes[row["Name"]] = node
    G.add_node(row["Name"], weight=0, size=0, pos=(row["Latitude"], row["Longitude"]))    

# Add Edges and weight them by the distance between the two nodes
for _, row in edgesData.iterrows():
    node1 = nodes[row["Node 1 Name"]]
    node2 = nodes[row["Node 2 Name"]]
    G.add_edge(node1.name, node2.name, weight=node1.dist(node2))

# Run Dijkstra's algorithm to find the shortest path between all pairs of nodes in the graph. This will be used to find the shortest path between any two landmarks.
paths = nx.shortest_path(G)

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
    assert min(landmark_hits.values()) > 0, "No landmarks were hit in the paths. Check the graph and data."
    assert max(landmark_hits.values()) < len(landmarksData), "Some landmarks were hit too many times. Check the graph and data."
    assert len(landmark_hits) == len(landmarksData), "Not all landmarks were hit in the paths. Check the graph and data."
    assert min(landmark_hits.values()) == max(landmark_hits.values()), "Landmarks were hit an unequal number of times. Check the graph and data."
except AssertionError as e:
    print(f"The data seems to be malformed: {e}")
