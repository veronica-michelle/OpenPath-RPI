from rest_framework.test import APITestCase

from .mock_data import LOCATIONS


class LocationListViewTests(APITestCase):
    def test_returns_mock_locations(self):
        response = self.client.get("/api/locations/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(LOCATIONS))
        self.assertEqual({loc["id"] for loc in response.data}, {loc["id"] for loc in LOCATIONS})

class RouteViewTests(APITestCase):
    def test_known_locations_return_a_placeholder_route(self):
        response = self.client.post(
            "/api/route/",
            {
                "start_id": "carnegie",
                "destination_id": "walker",
                "avoid_stairs": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["route_points"]), 2)
        self.assertGreater(response.data["total_distance_m"], 0)

    def test_unknown_start_returns_404(self):
        response = self.client.post(
            "/api/route/",
            {
                "start_id": "not-a-real-place",
                "destination_id": "carnegie",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_unknown_destination_returns_404(self):
        response = self.client.post(
            "/api/route/",
            {
                "start_id": "carnegie",
                "destination_id": "not-a-real-place",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_fields_returns_400(self):
        response = self.client.post("/api/route/", {}, format="json")
        self.assertEqual(response.status_code, 400)
