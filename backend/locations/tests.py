from rest_framework.test import APITestCase

from .graph import get_graph, get_locations


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


class RouteViewTests(APITestCase):
    def test_returns_graph_route_and_summary(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "carnegie", "destination_id": "walker"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nodeIds"][0], "carnegie")
        self.assertEqual(response.data["nodeIds"][-1], "walker")
        self.assertEqual(len(response.data["points"]), len(response.data["nodeIds"]))
        self.assertEqual(response.data["route_points"], response.data["points"])
        self.assertGreater(response.data["total_distance_m"], 0)
        self.assertEqual(response.data["maneuvers"][-1]["type"], "arrive")
        self.assertGreater(response.data["distanceFt"], 0)
        self.assertIn("minutes", response.data)

    def test_avoid_stairs_excludes_stair_edges(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "carnegie", "destination_id": "library", "avoid_stairs": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["usedStairs"])

    def test_stairs_are_available_when_not_excluded(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "carnegie", "destination_id": "library", "avoid_stairs": False},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["usedStairs"])

    def test_entrance_selection_adjusts_route_endpoints(self):
        response = self.client.post(
            "/api/route/",
            {
                "start_id": "carnegie",
                "destination_id": "walker",
                "start_entrance_id": "carnegie-e2",
                "destination_entrance_id": "walker-e2",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["points"][0]["lng"], -73.6830758)
        self.assertEqual(response.data["points"][-1]["lng"], -73.6821182)

    def test_unknown_destination_returns_404(self):
        response = self.client.post(
            "/api/route/",
            {"start_id": "carnegie", "destination_id": "not-a-real-place"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_fields_returns_400(self):
        response = self.client.post("/api/route/", {}, format="json")
        self.assertEqual(response.status_code, 400)
