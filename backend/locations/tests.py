from rest_framework.test import APITestCase


class LocationListViewTests(APITestCase):
    def test_returns_sample_locations(self):
        response = self.client.get("/api/locations/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertIn("carnegie", [loc["id"] for loc in response.data])


class RouteViewTests(APITestCase):
    def test_known_locations_have_no_verified_route_yet(self):
        response = self.client.post(
            "/api/route/",
            {
                "start_id": "carnegie",
                "destination_id": "walker",
                "avoid_stairs": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["code"], "no_verified_route")

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
