"""Routing regressions for measured lengths and entrance selection."""

import copy
import math
from unittest import TestCase
from unittest.mock import patch

from . import graph
from .tests import LOCATIONS_DATA, PATHS_DATA, ControlledGraphAPITestCase
from .validate_graph import validate


class RouteIntegrationTests(ControlledGraphAPITestCase):
    def route(self, **extra):
        return self.client.post(
            "/api/route/", {"start_id": "L01", "destination_id": "L02", **extra}, format="json"
        )

    def test_measured_length_drives_summary_and_arrival(self):
        self.graph["edges"][0]["dist"] = 120.0
        # Make the alternative longer so the measured direct path is selected.
        for edge in self.graph["edges"][1:3]:
            edge["dist"] = 200.0
        route = self.route().data
        self.assertEqual(route["total_distance_m"], 120.0)
        self.assertAlmostEqual(route["distanceFt"], 120.0 * graph.FEET_PER_METER)
        self.assertEqual(route["segmentDistancesFt"], [route["distanceFt"]])
        self.assertAlmostEqual(route["maneuvers"][-1]["atDistance"], route["distanceFt"])

    def test_selected_entrance_controls_elevation_without_mutating_cached_map(self):
        before = copy.deepcopy(self.graph)
        response = self.route(start_entrance_id="L01B")
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.data["elevationGainFt"], 1.5 * graph.FEET_PER_METER)
        self.assertEqual(self.graph, before)

    def test_entrance_from_another_building_is_rejected(self):
        response = self.route(start_entrance_id="L02A")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown start entrance", response.data["detail"])

    def test_stairs_only_door_cannot_be_a_stairs_free_route(self):
        response = self.route(start_entrance_id="L01B", avoid_stairs=True)
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("Construction blocks", response.data["detail"])

    def test_ramp_at_door_allows_stairs_free_route(self):
        self.graph["nodes"][0]["entrances"][1]["features"]["ramp"] = True
        response = self.route(start_entrance_id="L01B", avoid_stairs=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["usedStairs"])

    def test_stairs_only_door_is_reported_even_on_a_flat_path(self):
        self.graph["edges"][0]["type"] = "path"
        self.assertTrue(self.route(start_entrance_id="L01B").data["usedStairs"])

    def test_selected_door_changes_unmeasured_route_choice(self):
        self.graph["nodes"] = [
            {
                "id": "L01",
                "name": "Hall",
                "lat": 42.0,
                "lng": -73.0,
                "entrances": [
                    {"id": "west", "lat": 42.0, "lng": -73.0, "features": {}},
                    {"id": "east", "lat": 42.0, "lng": -72.998, "features": {}},
                ],
            },
            {"id": "L02", "name": "Library", "lat": 42.002, "lng": -72.999},
            {"id": "west-path", "lat": 42.001, "lng": -73.0},
            {"id": "east-path", "lat": 42.001, "lng": -72.998},
        ]
        # get_locations filters on node type, independently of the route graph.
        for node in self.graph["nodes"]:
            node["type"] = "location" if node["id"].startswith("L") else "path"
        self.graph["edges"] = [
            {"a": a, "b": b, "type": "path"}
            for a, b in [
                ("L01", "west-path"),
                ("L01", "east-path"),
                ("west-path", "L02"),
                ("east-path", "L02"),
            ]
        ]
        self.assertIn("west-path", self.route(start_entrance_id="west").data["nodeIds"])
        self.assertIn("east-path", self.route(start_entrance_id="east").data["nodeIds"])


class DataValidationTests(TestCase):
    def test_invalid_distance_is_reported_and_not_routed(self):
        for distance in (-1, math.nan, math.inf, "100", True):
            with self.subTest(distance=distance):
                data = {
                    "nodes": [
                        {"id": "a", "name": "A", "type": "path", "lat": 42, "lng": -73},
                        {"id": "b", "name": "B", "type": "path", "lat": 42.1, "lng": -73},
                    ],
                    "edges": [{"a": "a", "b": "b", "type": "path", "dist": distance}],
                }
                self.assertTrue(any("distance" in e for e in validate(data)[0]))
                with patch("locations.graph.get_graph", return_value=data):
                    self.assertIsNone(graph.find_route("a", "b"))

    def test_invalid_coordinates_fail_with_actionable_error(self):
        for coordinates in ([math.nan, -73], [91, -73], [42, -181], [True, -73]):
            with self.subTest(coordinates=coordinates):
                with self.assertRaises(ValueError):
                    graph._point_fields({"id": "bad", "coordinates": coordinates, "elevation": 1})

    def load_files(self, locations, paths):
        with (
            patch("locations.graph.Path.open"),
            patch(
                "locations.graph.json.load",
                side_effect=[locations, paths],
            ),
        ):
            return graph.load_graph("locations.json", "paths.json")

    def test_mismatched_node_key_is_rejected_before_edges_are_linked(self):
        locations = copy.deepcopy(LOCATIONS_DATA)
        locations["L01"]["id"] = "different-node"
        with self.assertRaisesRegex(ValueError, "does not match its id"):
            self.load_files(locations, copy.deepcopy(PATHS_DATA))

    def test_malformed_measured_distance_is_rejected_at_load(self):
        paths = copy.deepcopy(PATHS_DATA)
        paths["E00001"]["distance"] = "100 meters"
        with self.assertRaisesRegex(ValueError, "distance must be finite"):
            self.load_files(copy.deepcopy(LOCATIONS_DATA), paths)
