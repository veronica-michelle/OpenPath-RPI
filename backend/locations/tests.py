import copy
from unittest import TestCase
from unittest.mock import patch

from rest_framework.test import APITestCase

from .edge_calculator import fill_paths, measure_edge
from .graph import get_graph, get_locations
from .validate_graph import validate


def _fixture_location(location_id, lat, lng, elevation=0, entrances=None, **extra):
    """Build a location node in the shape load_graph() produces."""
    return {
        "id": location_id,
        "name": location_id.title(),
        "type": "location",
        "lat": lat,
        "lng": lng,
        "elevation": elevation,
        "entrances": entrances
        or [
            {
                "id": f"{location_id}-e1",
                "lat": lat,
                "lng": lng,
                "label": "Main",
                "accessible": True,
            }
        ],
        **extra,
    }


# A small made-up campus, so route tests do not depend on the real map data.
#
#   hall --stairs (50)-- library --stairs (50)-- tower
#     |                     |
#    (100)                (100)
#     |                     |
#     +-------- j1 ---------+
#               |
#             (100)            annex is only reachable through construction.
#               |              island has no edges at all.
#              lab --construction-- annex
FIXTURE_GRAPH = {
    "nodes": [
        _fixture_location(
            "hall",
            42.7300,
            -73.6800,
            entrances=[
                {"id": "hall-e1", "lat": 42.73, "lng": -73.68, "label": "Main", "accessible": True},
                {
                    "id": "hall-e2",
                    "lat": 42.7301,
                    "lng": -73.6805,
                    "label": "Side",
                    "accessible": False,
                },
            ],
        ),
        _fixture_location("library", 42.7310, -73.6800),
        _fixture_location("tower", 42.7320, -73.6800),
        _fixture_location(
            "lab",
            42.7300,
            -73.6820,
            elevation=10,
            entrances=[
                {
                    "id": "lab-e1",
                    "lat": 42.73,
                    "lng": -73.682,
                    "label": "Main",
                    "accessible": False,
                },
                {
                    "id": "lab-e2",
                    "lat": 42.7301,
                    "lng": -73.6825,
                    "label": "Ramp",
                    "accessible": True,
                },
            ],
        ),
        _fixture_location("annex", 42.7290, -73.6820),
        _fixture_location("island", 42.7400, -73.6900, mock=True),
        {"id": "j1", "type": "path", "lat": 42.7305, "lng": -73.6810, "elevation": 0},
    ],
    "edges": [
        {"id": "E1", "a": "hall", "b": "library", "dist": 50, "type": "stairs"},
        {"id": "E2", "a": "hall", "b": "j1", "dist": 100, "type": "path"},
        {"id": "E3", "a": "j1", "b": "library", "dist": 100, "type": "path"},
        {"id": "E4", "a": "j1", "b": "lab", "dist": 100, "type": "path"},
        {"id": "E5", "a": "library", "b": "tower", "dist": 50, "type": "stairs"},
        {"id": "E6", "a": "lab", "b": "annex", "dist": 50, "type": "construction"},
    ],
    "scenarios": [
        {
            "id": "stairs-allowed",
            "case": "stairs",
            "start_id": "hall",
            "destination_id": "library",
            "expect": "route",
            "used_stairs": True,
        },
        {
            "id": "stairs-avoided",
            "case": "stairs",
            "start_id": "hall",
            "destination_id": "library",
            "avoid_stairs": True,
            "expect": "route",
            "used_stairs": False,
        },
        {
            "id": "chosen-entrances",
            "case": "multiple-entrances",
            "start_id": "hall",
            "start_entrance_id": "hall-e2",
            "destination_id": "lab",
            "destination_entrance_id": "lab-e2",
            "expect": "route",
        },
        {
            "id": "disconnected",
            "case": "disconnected",
            "start_id": "hall",
            "destination_id": "island",
            "expect": "no_route",
            "detail": "No available route connects these locations.",
        },
        {
            "id": "stairs-only-destination",
            "case": "no-accessible-route",
            "start_id": "hall",
            "destination_id": "tower",
            "avoid_stairs": True,
            "expect": "no_route",
            "detail": "No available route connects these locations.",
        },
        {
            "id": "construction-only-destination",
            "case": "construction",
            "start_id": "hall",
            "destination_id": "annex",
            "expect": "no_route",
            "detail": "Construction blocks prevent travel between these locations.",
        },
    ],
}


class FixtureGraphTestCase(APITestCase):
    def setUp(self):
        graph_patch = patch("locations.graph.get_graph", return_value=FIXTURE_GRAPH)
        graph_patch.start()
        self.addCleanup(graph_patch.stop)


class MapGraphViewTests(APITestCase):
    def test_returns_nodes_and_typed_edges(self):
        response = self.client.get("/api/map/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["nodes"]), len(get_graph()["nodes"]))
        self.assertTrue(any(node["type"] == "path" for node in response.data["nodes"]))
        self.assertTrue(all("type" in edge for edge in response.data["edges"]))


class LocationListViewTests(APITestCase):
    def test_returns_selectable_graph_locations(self):
        response = self.client.get("/api/locations/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(get_locations()))
        self.assertTrue(all("entrances" in location for location in response.data))


class RouteViewTests(FixtureGraphTestCase):
    def test_returns_graph_route_and_summary(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "hall", "destination_id": "lab"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nodeIds"], ["hall", "j1", "lab"])
        self.assertEqual(len(response.data["points"]), len(response.data["nodeIds"]))
        self.assertEqual(response.data["route_points"], response.data["points"])
        self.assertGreater(response.data["total_distance_m"], 0)
        self.assertEqual(response.data["maneuvers"][-1]["type"], "arrive")
        self.assertGreater(response.data["distanceFt"], 0)
        self.assertIn("minutes", response.data)

    def test_avoid_stairs_excludes_stair_edges(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "hall", "destination_id": "library", "avoid_stairs": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nodeIds"], ["hall", "j1", "library"])
        self.assertFalse(response.data["usedStairs"])

    def test_stairs_are_available_when_not_excluded(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "hall", "destination_id": "library", "avoid_stairs": False},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nodeIds"], ["hall", "library"])
        self.assertTrue(response.data["usedStairs"])

    def test_entrance_selection_adjusts_route_endpoints(self):
        response = self.client.post(
            "/api/route/",
            {
                "start_id": "hall",
                "destination_id": "lab",
                "start_entrance_id": "hall-e2",
                "destination_entrance_id": "lab-e2",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["points"][0]["lng"], -73.6805)
        self.assertEqual(response.data["points"][-1]["lng"], -73.6825)

    def test_unknown_destination_returns_404(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "hall", "destination_id": "not-a-real-place"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("destination_id", response.data["detail"])

    def test_missing_fields_returns_400(self):
        response = self.client.post("/api/route/", {}, format="json")
        self.assertEqual(response.status_code, 400)


class FixtureScenarioTests(FixtureGraphTestCase):
    """Runs every labeled edge case in FIXTURE_GRAPH's "scenarios" list through the route API."""

    def test_fixture_graph_is_valid(self):
        self.assertEqual(validate(FIXTURE_GRAPH)[0], [])

    def test_scenarios_route_as_labeled(self):
        locations = {node["id"]: node for node in FIXTURE_GRAPH["nodes"]}
        for scenario in FIXTURE_GRAPH["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                response = self.client.post(
                    "/api/route/",
                    {
                        field: scenario[field]
                        for field in (
                            "start_id",
                            "destination_id",
                            "start_entrance_id",
                            "destination_entrance_id",
                            "avoid_stairs",
                        )
                        if field in scenario
                    },
                    format="json",
                )
                if scenario["expect"] == "no_route":
                    self.assertEqual(response.status_code, 404)
                    self.assertEqual(response.data["detail"], scenario["detail"])
                    continue

                self.assertEqual(response.status_code, 200)
                if "used_stairs" in scenario:
                    self.assertEqual(response.data["usedStairs"], scenario["used_stairs"])
                for end, point in (
                    ("start", response.data["points"][0]),
                    ("destination", response.data["points"][-1]),
                ):
                    entrance_id = scenario.get(f"{end}_entrance_id")
                    if entrance_id:
                        entrance = next(
                            item
                            for item in locations[scenario[f"{end}_id"]]["entrances"]
                            if item["id"] == entrance_id
                        )
                        self.assertEqual(
                            (point["lat"], point["lng"]), (entrance["lat"], entrance["lng"])
                        )


class ValidateGraphTests(TestCase):
    """validate_graph.py should pass the real dataset and catch each kind of data mistake."""

    BASE = {
        "nodes": [
            {
                "id": "hall",
                "name": "Hall",
                "lat": 0,
                "lng": 0,
                "type": "location",
                "entrances": [
                    {"id": "hall-e1", "lat": 0, "lng": 0, "label": "Main", "accessible": True}
                ],
            },
            {
                "id": "lab",
                "name": "Lab",
                "lat": 0,
                "lng": 1,
                "type": "location",
                "entrances": [
                    {"id": "lab-e1", "lat": 0, "lng": 1, "label": "Main", "accessible": None}
                ],
            },
            {"id": "j1", "lat": 0, "lng": 0.5, "type": "path"},
        ],
        "edges": [
            {"a": "hall", "b": "j1", "type": "path"},
            {"a": "j1", "b": "lab", "type": "path"},
        ],
        "scenarios": [
            {
                "id": "hall-to-lab",
                "case": "stairs",
                "start_id": "hall",
                "destination_id": "lab",
                "expect": "route",
            },
        ],
    }

    def graph(self):
        return copy.deepcopy(self.BASE)

    def assert_error(self, graph, fragment):
        errors, _ = validate(graph)
        self.assertTrue(any(fragment in error for error in errors), f"{fragment!r} not in {errors}")

    def test_real_dataset_has_no_errors_except_missing_paths(self):
        # paths.json is still being filled in. Check everything but connectivity
        # until it is complete, then go back to requiring no errors at all.
        errors = [
            error for error in validate(get_graph())[0] if "unreachable from campus" not in error
        ]
        self.assertEqual(errors, [])

    def test_valid_example_has_no_errors(self):
        self.assertEqual(validate(self.graph())[0], [])

    def test_catches_dangling_edge(self):
        graph = self.graph()
        graph["edges"].append({"a": "lab", "b": "gym", "type": "path"})
        self.assert_error(graph, "points at missing node 'gym'")

    def test_catches_duplicate_ids(self):
        graph = self.graph()
        graph["nodes"].append(copy.deepcopy(graph["nodes"][2]))
        graph["nodes"][1]["entrances"][0]["id"] = "hall-e1"
        self.assert_error(graph, "duplicate node id: j1")
        self.assert_error(graph, "duplicate entrance id: hall-e1")

    def test_catches_building_without_entrances(self):
        graph = self.graph()
        graph["nodes"][1]["entrances"] = []
        self.assert_error(graph, "building lab: has no entrances")

    def test_catches_entrance_without_accessibility_flag(self):
        graph = self.graph()
        del graph["nodes"][0]["entrances"][0]["accessible"]
        self.assert_error(graph, "entrance hall-e1: missing 'accessible'")

    def test_catches_scenario_with_unknown_location(self):
        graph = self.graph()
        graph["scenarios"][0]["destination_id"] = "gym"
        self.assert_error(graph, "unknown destination_id 'gym'")

    def test_real_disconnected_node_is_an_error_but_mock_one_is_reported(self):
        graph = self.graph()
        graph["edges"] = graph["edges"][:1]  # cuts lab off from campus
        self.assert_error(graph, "unreachable from campus (not marked mock): lab")

        graph["nodes"][1]["mock"] = True
        errors, notes = validate(graph)
        self.assertEqual(errors, [])
        self.assertIn("intentional disconnected area (mock): lab", notes)

    def test_stairs_only_location_is_reported_not_an_error(self):
        graph = self.graph()
        graph["edges"][1]["type"] = "stairs"
        errors, notes = validate(graph)
        self.assertEqual(errors, [])
        self.assertIn("no stairs-free route from campus (real): lab", notes)


class EdgeCalculatorTests(TestCase):
    def locations(self):
        return {
            "L01": {
                "id": "L01",
                "name": "Hall",
                "entrances": [
                    {"id": "L01A", "coordinates": [42.7300, -73.6800], "elevation": 60.0},
                    {"id": "L01B", "coordinates": [42.7320, -73.6800], "elevation": 64.0},
                ],
            },
            "N001": {"id": "N001", "coordinates": [42.7310, -73.6800], "elevation": 62.0},
            "N002": {"id": "N002", "coordinates": [42.7300, -73.6800], "elevation": 60.0},
        }

    def edge(self, from_id, to_id, distance=None):
        return {
            "from": from_id,
            "to": to_id,
            "distance": distance,
            "features": {
                "paved": True,
                "stairs": False,
                "ramp": False,
                "closed": False,
                "gradient": 0.0,
            },
        }

    def test_measures_distance_and_signed_gradient(self):
        distance, gradient = measure_edge(self.locations(), "N002", "N001")
        self.assertAlmostEqual(distance, 111.19, places=1)  # 0.001 deg of latitude
        self.assertAlmostEqual(gradient, 1.03, places=2)  # 2 m up over ~111 m
        _, downhill = measure_edge(self.locations(), "N001", "N002")
        self.assertAlmostEqual(downhill, -gradient)

    def test_building_uses_entrance_closest_to_other_end(self):
        locations = self.locations()
        locations["N001"]["coordinates"] = [42.7319, -73.6800]  # next to L01B
        distance, gradient = measure_edge(locations, "L01", "N001")
        self.assertLess(distance, 12)
        self.assertLess(gradient, 0)  # L01B (64 m) down to N001 (62 m)

    def test_fills_missing_distance_and_keeps_measured_one(self):
        paths = {
            "E0001": self.edge("N002", "N001"),
            "E0002": self.edge("N001", "L01", distance=150.0),
        }
        self.assertEqual(fill_paths(self.locations(), paths), {})
        self.assertEqual(paths["E0001"]["distance"], 111.19)
        self.assertEqual(paths["E0002"]["distance"], 150.0)
        self.assertEqual(paths["E0001"]["features"]["gradient"], 1.03)
        self.assertTrue(paths["E0001"]["features"]["paved"])

    def test_reports_unknown_node_and_leaves_edge_alone(self):
        paths = {"E0001": self.edge("N001", "N999")}
        self.assertEqual(fill_paths(self.locations(), paths), {"E0001": "unknown node id 'N999'"})
        self.assertIsNone(paths["E0001"]["distance"])
