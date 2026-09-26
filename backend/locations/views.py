from rest_framework.response import Response
from rest_framework.views import APIView

from .mock_data import LOCATIONS, LOCATIONS_BY_ID
from .serializers import LocationSerializer, RouteRequestSerializer


class LocationListView(APIView):
    """GET /api/locations/ — verified entrances available for routing."""

    def get(self, request):
        return Response([])

class RouteView(APIView):
    """POST /api/route/ — return a route only when verified paths exist."""

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

        return Response(
            {
                "code": "no_verified_route",
                "detail": "No verified route is available yet.",
            },
            status=404,
        )
