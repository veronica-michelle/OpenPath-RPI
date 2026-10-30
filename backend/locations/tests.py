"""Check the map loader and its API using small, made-up examples.

The campus files change as the data team adds and reviews locations, so most
tests here use a fixed map kept in this file. That lets these checks focus on
what the backend promises: how it reads buildings, entrances, path points, and
edges, and how its map, location, and route addresses respond to requests.
The examples are only test material; they are not campus data. The validator
checks below also use small maps so their results do not depend on the current
state of the real map.
"""

import copy
from unittest import TestCase
from unittest.mock import mock_open, patch

from rest_framework.test import APITestCase

from . import graph as graph_module
from .validate_graph import validate


# These contrived examples cover a direct stair path, a regular detour, and a closed path.
LOCATIONS_DATA = {
    "L01": {
        "id": "L01",
        "name": "Test Hall",
        "entrances": [
            {
                "id": "L01A",
                "coordinates": [42.0, -73.0],
                "elevation": 10.0,
                "features": {
                    "accessible": True,
                    "stairs": False,
                    "ramp": True,
                    "buttons": [False, True],
                },
            },
            {
                "id": "L01B",
                "coordinates": [42.0001, -73.0],
                "elevation": 10.5,
                "features": {
                    "accessible": False,
                    "stairs": True,
                    "ramp": False,
                    "buttons": [False, False],
                },
            },
        ],
    },
    "L02": {
        "id": "L02",
        "name": "Test Library",
        "entrances": [
            {
                "id": "L02A",
                "coordinates": [42.0, -72.999],
                "elevation": 12.0,
                "features": {
                    "accessible": True,
                    "stairs": False,
                    "ramp": False,
                    "buttons": [True, False],
                },
            }
        ],
    },
    "L03": {
        "id": "L03",
        "name": "Disconnected Building",
        "entrances": [
            {
                "id": "L03A",
                "coordinates": [42.001, -72.999],
                "elevation": 13.0,
                "features": {
                    "accessible": None,
                    "stairs": False,
                    "ramp": False,
                    "buttons": [False, False],
                },
            }
        ],
    },
    "L04": {
        "id": "L04",
        "name": "Isolated Building",
        "entrances": [
            {
                "id": "L04A",
                "coordinates": [42.002, -72.998],
                "elevation": 14.0,
                "features": {
                    "accessible": False,
                    "stairs": False,
                    "ramp": False,
                    "buttons": [False, False],
                },
            }
        ],
    },
    "N001": {"id": "N001", "coordinates": [42.0, -72.9995], "elevation": 11.0},
}

PATHS_DATA = {
    "E00001": {
        "from": "L01",
        "to": "L02",
        "distance": 1.0,
        "features": {
            "paved": True,
            "stairs": True,
            "ramp": False,
            "closed": False,
            "gradient": 0.0,
        },
    },
    "E00002": {
        "from": "L01",
        "to": "N001",
        "features": {
            "paved": True,
            "stairs": False,
            "ramp": False,
            "closed": False,
            "gradient": 0.0,
        },
    },
    "E00003": {
        "from": "N001",
        "to": "L02",
        "distance": None,
        "features": {
            "paved": True,
            "stairs": False,
            "ramp": False,
            "closed": False,
            "gradient": 0.0,
        },
    },
    "E00004": {
        "from": "L02",
        "to": "L03",
        "distance": None,
        "features": {
            "paved": False,
            "stairs": False,
            "ramp": False,
            "closed": True,
            "gradient": 0.0,
        },
    },
}

# Load a fresh copy of the data so that tests cannot modify shared examples
def make_graph():
    with patch(
        "locations.graph.Path.open",
        mock_open(),
    ), patch(
        "locations.graph.json.load",
        side_effect=[copy.deepcopy(LOCATIONS_DATA), copy.deepcopy(PATHS_DATA)],
    ):
        return graph_module.load_graph("locations.json", "paths.json")


# Give each API test the same map instead of the real campus map
class ControlledGraphAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.graph = make_graph()
        graph_patch = patch("locations.graph.get_graph", return_value=self.graph)
        view_map_patch = patch("locations.views.get_graph", return_value=self.graph)
        graph_patch.start()
        view_map_patch.start()
        self.addCleanup(graph_patch.stop)
        self.addCleanup(view_map_patch.stop)

# Check that the loader appropriately generates a graph from the node and edge JSON files
class GraphLoaderTests(TestCase):
    def load_files(self, locations, paths):
        with patch("locations.graph.Path.open", mock_open()), patch(
            "locations.graph.json.load", side_effect=[locations, paths]
        ):
            return graph_module.load_graph("locations.json", "paths.json")

    def test_maps_buildings_path_nodes_edges_and_metadata(self):
        graph = self.load_files(copy.deepcopy(LOCATIONS_DATA), copy.deepcopy(PATHS_DATA))
        nodes = {node["id"]: node for node in graph["nodes"]}
        edges = {edge["id"]: edge for edge in graph["edges"]}

        self.assertEqual(nodes["L01"]["type"], "location")
        self.assertEqual((nodes["L01"]["lat"], nodes["L01"]["lng"]), (42.0, -73.0))
        self.assertEqual(nodes["L01"]["entrances"][1]["id"], "L01B")
        self.assertEqual(
            nodes["L01"]["entrances"][1]["features"],
            LOCATIONS_DATA["L01"]["entrances"][1]["features"],
        )
        self.assertAlmostEqual(nodes["L01"]["elevation_m"], 10.0)
        self.assertAlmostEqual(nodes["L01"]["elevation"], 10.0 * graph_module.FEET_PER_METER)
        self.assertEqual(nodes["N001"]["type"], "path")
        self.assertEqual(edges["E00001"]["type"], "stairs")
        self.assertEqual(edges["E00001"]["dist"], 1.0)
        self.assertIsNone(edges["E00002"]["dist"])
        self.assertEqual(edges["E00004"]["type"], "construction")
        self.assertEqual(edges["E00001"]["features"], PATHS_DATA["E00001"]["features"])

    def test_accepts_empty_paths_object(self):
        graph = self.load_files(copy.deepcopy(LOCATIONS_DATA), {})
        self.assertEqual(graph["edges"], [])

    def test_rejects_paths_array_with_format_error(self):
        with self.assertRaisesRegex(ValueError, "JSON object keyed by unique edge IDs"):
            self.load_files(copy.deepcopy(LOCATIONS_DATA), list(PATHS_DATA.values()))

    def test_empty_building_entrances_are_rejected(self):
        locations = copy.deepcopy(LOCATIONS_DATA)
        locations["L01"]["entrances"] = []
        with self.assertRaisesRegex(ValueError, "needs at least one entrance"):
            self.load_files(locations, copy.deepcopy(PATHS_DATA))

# Check the API endpoint used to draw the map.
class MapGraphViewTests(ControlledGraphAPITestCase):
    def test_returns_nodes_and_edges_with_valid_endpoints(self):
        response = self.client.get("/api/map/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["nodes"]), len(LOCATIONS_DATA))
        node_ids = {node["id"] for node in response.data["nodes"]}
        self.assertTrue(any(node["type"] == "path" for node in response.data["nodes"]))
        self.assertTrue(
            all(
                edge["a"] in node_ids and edge["b"] in node_ids
                for edge in response.data["edges"]
            )
        )


# Check that the location picker receives buildings and their entrances.
class LocationListViewTests(ControlledGraphAPITestCase):
    def test_returns_selectable_buildings_and_entrances(self):
        response = self.client.get("/api/locations/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {location["id"] for location in response.data},
            {"L01", "L02", "L03", "L04"},
        )
        self.assertTrue(all("entrances" in location for location in response.data))

    # Check route requests for ordinary, blocked, and invalid trips.

class RouteViewTests(ControlledGraphAPITestCase):
    def route(self, **overrides):
        request = {"start_id": "L01", "destination_id": "L02", **overrides}
        return self.client.post("/api/route/", request, format="json")

    def test_returns_route_and_summary(self):
        response = self.route()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nodeIds"], ["L01", "L02"])
        self.assertEqual(response.data["route_points"], response.data["points"])
        self.assertGreater(response.data["total_distance_m"], 0)
        self.assertGreater(response.data["distanceFt"], 0)
        self.assertEqual(response.data["maneuvers"][-1]["type"], "arrive")

    def test_missing_distance_is_estimated_from_coordinates(self):
        response = self.route(avoid_stairs=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nodeIds"], ["L01", "N001", "L02"])
        self.assertGreater(response.data["total_distance_m"], 0)
        self.assertFalse(response.data["usedStairs"])

    def test_avoid_stairs_uses_accessible_detour(self):
        response = self.route(avoid_stairs=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["usedStairs"])
        self.assertIn("N001", response.data["nodeIds"])

    def test_stairs_are_available_when_not_excluded(self):
        response = self.route(avoid_stairs=False)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["usedStairs"])

    def test_selected_entrances_adjust_route_endpoints(self):
        response = self.route(start_entrance_id="L01B", destination_entrance_id="L02A")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["points"][0], {"lat": 42.0001, "lng": -73.0})
        self.assertEqual(response.data["points"][-1], {"lat": 42.0, "lng": -72.999})

    def test_unknown_destination_returns_404(self):
        response = self.route(destination_id="missing")
        self.assertEqual(response.status_code, 404)

    def test_disconnected_building_returns_404(self):
        response = self.route(destination_id="L04")
        self.assertEqual(response.status_code, 404)
        self.assertIn("No available route", response.data["detail"])

    def test_construction_blocked_route_returns_404(self):
        response = self.client.post(
            "/api/route/", {"start_id": "L02", "destination_id": "L03"}, format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Construction blocks", response.data["detail"])

    def test_same_building_returns_400(self):
        response = self.route(destination_id="L01")
        self.assertEqual(response.status_code, 400)

    def test_missing_fields_returns_400(self):
        response = self.client.post("/api/route/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_entrance_id_returns_400(self):
        response = self.route(start_entrance_id="L01Z", destination_entrance_id="L02B")
        self.assertEqual(response.status_code, 400)

    def test_invalid_destination_id_returns_400(self):
        response = self.route(start_entrance_id="L01A", destination_entrance_id="L02Z")
        self.assertEqual(response.status_code, 400)


class ValidateGraphTests(TestCase):
    # Attempt validating a mock graph independent of the changing campus data

    BASE = {
        "nodes": [
            {
                "id": "hall",
                "name": "Test Hall",
                "lat": 42.0,
                "lng": -73.0,
                "type": "location",
                "entrances": [{"id": "hall-a", "lat": 42.0, "lng": -73.0, "accessible": True}],
            },
            {
                "id": "lab",
                "name": "Test Lab",
                "lat": 42.0,
                "lng": -72.999,
                "type": "location",
                "entrances": [{"id": "lab-a", "lat": 42.0, "lng": -72.999, "accessible": None}],
            },
            {"id": "p1", "lat": 42.0, "lng": -72.9995, "type": "path"},
        ],
        "edges": [
            {"a": "hall", "b": "p1", "type": "path"},
            {"a": "p1", "b": "lab", "type": "path"},
        ],
    }

    def graph(self):
        return copy.deepcopy(self.BASE)

    def assert_error(self, graph, fragment):
        errors, _ = validate(graph)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"{fragment!r} not in {errors}",
        )

    def test_valid_example_has_no_errors(self):
        self.assertEqual(validate(self.graph())[0], [])

    def test_catches_dangling_edge(self):
        graph = self.graph()
        graph["edges"].append({"a": "lab", "b": "missing", "type": "path"})
        self.assert_error(graph, "points at missing node 'missing'")

    def test_catches_duplicate_node_and_entrance_ids(self):
        graph = self.graph()
        graph["nodes"].append(copy.deepcopy(graph["nodes"][2]))
        graph["nodes"][1]["entrances"][0]["id"] = "hall-a"
        self.assert_error(graph, "duplicate node id: p1")
        self.assert_error(graph, "duplicate entrance id: hall-a")

    def test_catches_building_without_entrances(self):
        graph = self.graph()
        graph["nodes"][1]["entrances"] = []
        self.assert_error(graph, "building lab: has no entrances")

    def test_catches_entrance_without_accessibility_flag(self):
        graph = self.graph()
        del graph["nodes"][0]["entrances"][0]["accessible"]
        self.assert_error(graph, "entrance hall-a: missing 'accessible'")

    def test_reports_disconnected_real_and_mock_nodes(self):
        graph = self.graph()
        graph["edges"] = graph["edges"][:1]
        self.assert_error(graph, "unreachable from campus (not marked mock): lab")

        graph["nodes"][1]["mock"] = True
        errors, notes = validate(graph)
        self.assertEqual(errors, [])
        self.assertIn("intentional disconnected area (mock): lab", notes)

    def test_reports_location_reachable_only_by_stairs(self):
        graph = self.graph()
        graph["edges"][1]["type"] = "stairs"
        errors, notes = validate(graph)
        self.assertEqual(errors, [])
        self.assertIn("no stairs-free route from campus (real): lab", notes)
