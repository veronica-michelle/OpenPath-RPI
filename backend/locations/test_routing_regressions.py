"""Routing regressions for measured lengths and entrance selection."""

import copy
import json
import math
from unittest import TestCase
from unittest.mock import mock_open, patch

from rest_framework.test import APITestCase

from . import graph
from .edge_calculator import fill_paths, measure_edge
from .tests import LOCATIONS_DATA, PATHS_DATA, ControlledGraphAPITestCase
from .validate_graph import validate


class PlaceholderDataEndpointTests(APITestCase):
    """Exercise the configured data files through the actual API endpoints."""

    def test_map_exposes_valid_entrance_and_path_connections(self):
        response = self.client.get("/api/map/")
        self.assertEqual(response.status_code, 200)
        points = graph.routing_nodes(response.data)
        self.assertTrue(response.data["edges"])
        self.assertTrue(all(e["a"] in points and e["b"] in points for e in response.data["edges"]))
        self.assertTrue(
            any(e["a"].startswith("N") or e["b"].startswith("N") for e in response.data["edges"])
        )

    def test_route_between_buildings_uses_entrances_and_path_points(self):
        response = self.client.post(
            "/api/route/", {"start_id": "L01", "destination_id": "L03"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nodeIds"][0], "L01A")
        self.assertEqual(response.data["nodeIds"][-1], "L03A")
        self.assertTrue(any(node.startswith("N") for node in response.data["nodeIds"]))


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
        self.graph["edges"].append({"a": "L01B", "b": "L02A", "type": "path"})
        before = copy.deepcopy(self.graph)
        response = self.route(start_entrance_id="L01B")
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.data["elevationGainFt"], 1.5 * graph.FEET_PER_METER)
        self.assertEqual(self.graph, before)

    def test_entrance_from_another_building_is_rejected(self):
        response = self.route(start_entrance_id="L02A")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown start entrance", response.data["detail"])

    def test_disconnected_door_does_not_borrow_another_doors_paths(self):
        self.assertEqual(self.route().status_code, 200)
        response = self.route(start_entrance_id="L01B")
        self.assertEqual(response.status_code, 404)
        self.assertIn("No available route", response.data["detail"])

    def test_destination_door_uses_its_own_paths_in_both_directions(self):
        self.graph["edges"].append({"a": "L01B", "b": "N001", "type": "path"})
        forward = self.route(start_entrance_id="L01B")
        reverse = self.route(start_id="L02", destination_id="L01", destination_entrance_id="L01B")
        self.assertEqual(forward.status_code, 200)
        self.assertEqual(reverse.status_code, 200)
        self.assertEqual(forward.data["nodeIds"], ["L01B", "N001", "L02A"])
        self.assertEqual(reverse.data["nodeIds"], list(reversed(forward.data["nodeIds"])))

    def test_building_does_not_create_an_unrecorded_connection_between_doors(self):
        self.graph["edges"] = [
            {"a": "L02A", "b": "L01A", "type": "path"},
            {"a": "L01B", "b": "L03A", "type": "path"},
        ]
        response = self.route(start_id="L02", destination_id="L03")
        self.assertEqual(response.status_code, 404)

    def test_door_stairs_are_checked_in_the_middle_of_a_route(self):
        self.graph["edges"] = [
            {"a": "L02A", "b": "L01B", "type": "path"},
            {"a": "L01B", "b": "L03A", "type": "path"},
        ]
        response = self.route(start_id="L02", destination_id="L03")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["usedStairs"])
        response = self.route(start_id="L02", destination_id="L03", avoid_stairs=True)
        self.assertEqual(response.status_code, 404)

    def test_building_ids_are_not_walkable_vertices(self):
        self.graph["edges"] = [{"a": "L01", "b": "L02", "type": "path"}]
        self.assertEqual(self.route().status_code, 404)

    def test_stairs_only_door_cannot_be_a_stairs_free_route(self):
        response = self.route(start_entrance_id="L01B", avoid_stairs=True)
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("Construction blocks", response.data["detail"])

    def test_ramp_at_door_allows_stairs_free_route(self):
        self.graph["edges"].append({"a": "L01B", "b": "L02A", "type": "path"})
        self.graph["nodes"][0]["entrances"][1]["features"]["ramp"] = True
        response = self.route(start_entrance_id="L01B", avoid_stairs=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["usedStairs"])

    def test_stairs_only_door_is_reported_even_on_a_flat_path(self):
        self.graph["edges"].append({"a": "L01B", "b": "L02A", "type": "path"})
        self.graph["edges"][0]["type"] = "path"
        self.assertTrue(self.route(start_entrance_id="L01B").data["usedStairs"])

    def test_selected_door_uses_its_recorded_connections(self):
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
            {
                "id": "L02",
                "name": "Library",
                "lat": 42.002,
                "lng": -72.999,
                "entrances": [{"id": "L02A", "lat": 42.002, "lng": -72.999}],
            },
            {"id": "west-path", "lat": 42.001, "lng": -73.0},
            {"id": "east-path", "lat": 42.001, "lng": -72.998},
        ]
        # get_locations filters on node type, independently of the route graph.
        for node in self.graph["nodes"]:
            node["type"] = "location" if node["id"].startswith("L") else "path"
        self.graph["edges"] = [
            {"a": a, "b": b, "type": "path"}
            for a, b in [
                ("west", "west-path"),
                ("east", "east-path"),
                ("west-path", "L02A"),
                ("east-path", "L02A"),
            ]
        ]
        self.assertIn("west-path", self.route(start_entrance_id="west").data["nodeIds"])
        self.assertIn("east-path", self.route(start_entrance_id="east").data["nodeIds"])


class DataValidationTests(TestCase):
    def test_loader_preserves_the_nested_source_format_and_door_connections(self):
        locations, paths = copy.deepcopy(LOCATIONS_DATA), copy.deepcopy(PATHS_DATA)
        before = copy.deepcopy((locations, paths))
        loaded = self.load_files(locations, paths)
        self.assertEqual((locations, paths), before)
        self.assertEqual(loaded["edges"][0]["a"], "L01A")
        self.assertEqual(loaded["edges"][0]["b"], "L02A")
        self.assertEqual(loaded["nodes"][0]["entrances"][1]["id"], "L01B")
        self.assertNotIn("L01", graph.routing_nodes(loaded))
        self.assertIn("L01B", graph.routing_nodes(loaded))

    def test_runtime_keeps_nested_door_edges_and_logs_invalid_building_edges(self):
        paths = copy.deepcopy(PATHS_DATA)
        paths["placeholder"] = {**paths["E00001"], "from": "L01"}
        loaded = self.load_files(copy.deepcopy(LOCATIONS_DATA), paths)
        graph._get_graph.cache_clear()
        self.addCleanup(graph._get_graph.cache_clear)
        with patch("locations.graph.load_graph", return_value=loaded):
            with self.assertLogs("locations.graph", level="WARNING") as logs:
                result = graph._get_graph("locations.json", "paths.json", 0, 0)
        self.assertEqual(len(result["edges"]), len(PATHS_DATA))
        self.assertIn("placeholder", logs.output[0])
        self.assertIn("entrance or path IDs", logs.output[0])
        self.assertEqual(result["edges"][0]["a"], "L01A")

    def test_validator_reports_building_placeholder_and_disconnected_door(self):
        paths = copy.deepcopy(PATHS_DATA)
        paths["E00001"]["from"] = "L01"
        loaded = self.load_files(copy.deepcopy(LOCATIONS_DATA), paths)
        errors, _ = validate(loaded)
        self.assertTrue(any("unresolved building endpoint 'L01'" in error for error in errors))
        self.assertTrue(any("unreachable" in error and "L01B" in error for error in errors))
        self.assertFalse(any("missing node 'L02A'" in error for error in errors))

    def test_duplicate_door_ids_and_collisions_are_rejected(self):
        for duplicate in ("L01A", "L01", "N001"):
            with self.subTest(duplicate=duplicate):
                locations = copy.deepcopy(LOCATIONS_DATA)
                locations["L01"]["entrances"][1]["id"] = duplicate
                with self.assertRaisesRegex(ValueError, "duplicate routing node id"):
                    self.load_files(locations, copy.deepcopy(PATHS_DATA))

    def test_edge_calculator_rejects_building_and_preserves_placeholder(self):
        paths = copy.deepcopy(PATHS_DATA)
        paths["E00001"]["from"] = "L01"
        before = copy.deepcopy(paths["E00001"])
        problems = fill_paths(LOCATIONS_DATA, paths)
        self.assertIn("use an entrance id", problems["E00001"])
        self.assertEqual(paths["E00001"], before)

    def test_edge_calculator_measures_specified_door_not_nearest_door(self):
        a_distance, _ = measure_edge(LOCATIONS_DATA, "L01A", "N001")
        b_distance, _ = measure_edge(LOCATIONS_DATA, "L01B", "N001")
        self.assertGreater(b_distance, a_distance)

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
            patch("locations.graph.Path.open", mock_open()),
            patch("locations.graph.json.load", side_effect=[locations, paths]),
        ):
            return graph.load_graph("locations.json", "paths.json")

    def test_loader_accepts_trailing_commas_in_data_files(self):
        locations = copy.deepcopy(LOCATIONS_DATA)
        malformed_paths = json.dumps(copy.deepcopy(PATHS_DATA))[:-1] + ",}"
        with (
            patch("locations.graph.Path.open", mock_open()),
            patch(
                "locations.graph.json.load",
                side_effect=[locations, json.JSONDecodeError("bad json", malformed_paths, 0)],
            ),
            patch("locations.graph.Path.read_text", return_value=malformed_paths),
        ):
            loaded = graph.load_graph("locations.json", "paths.json")
        self.assertTrue(loaded["edges"])

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
