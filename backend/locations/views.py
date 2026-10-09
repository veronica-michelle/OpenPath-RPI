from rest_framework.response import Response
from rest_framework.views import APIView

from .graph import find_route, get_graph, get_locations
from .serializers import LocationSerializer, RouteRequestSerializer


class MapGraphView(APIView):
    """GET /api/map/ — provisional campus nodes and edges."""

    def get(self, request):
        return Response(get_graph())


class LocationListView(APIView):
    """GET /api/locations/ — selectable destination nodes."""

    def get(self, request):
        serializer = LocationSerializer(get_locations(), many=True)
        return Response(serializer.data)


class RouteView(APIView):
    """POST /api/route/ — shortest available graph route."""

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        locations = {location["id"]: location for location in get_locations()}

        for field in ("start_id", "destination_id"):
            if data[field] not in locations:
                return Response({"detail": f"Unknown {field}: {data[field]!r}"}, status=404)

        route = find_route(
            data["start_id"],
            data["destination_id"],
            avoid_stairs=data["avoid_stairs"],
            start_entrance_id=data.get("start_entrance_id", ""),
            destination_entrance_id=data.get("destination_entrance_id", ""),
        )
        if route is None:
            return Response({"detail": "No route found for these locations and preferences."}, status=404)
        return Response(route)
