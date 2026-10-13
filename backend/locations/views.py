from rest_framework.response import Response
from rest_framework.views import APIView

from .geo import haversine_meters
from .mock_data import LOCATIONS, LOCATIONS_BY_ID
from .serializers import LocationSerializer, RouteRequestSerializer


class LocationListView(APIView):
    """GET /api/locations/ — routable destinations (mock data for now)."""

    def get(self, request):
        serializer = LocationSerializer(LOCATIONS, many=True)
        return Response(serializer.data)

class RouteView(APIView):
    """POST /api/route/ — straight-line placeholder route between two locations."""

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        for field in ("start_id", "destination_id"):
            if data[field] not in LOCATIONS_BY_ID:
                return Response(
                    {"detail": f"Unknown {field}: {data[field]!r}"},
                    status=404,
                )

        start = LOCATIONS_BY_ID[data["start_id"]]
        destination = LOCATIONS_BY_ID[data["destination_id"]]
        distance_m = haversine_meters(
            start["lat"], start["lng"], destination["lat"], destination["lng"]
        )

        return Response(
            {
                "route_points": [
                    {"lat": start["lat"], "lng": start["lng"]},
                    {"lat": destination["lat"], "lng": destination["lng"]},
                ],
                "total_distance_m": distance_m,
                "directions": [f"Head toward {destination['name']}."],
                "accessibility_notes": [
                    "Placeholder route — mock data only, not a verified accessible path."
                ],
            }
        )
