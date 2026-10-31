from rest_framework.response import Response
from rest_framework.views import APIView

from .graph import construction_blocks_route, find_route, get_graph, get_locations
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

        if data["start_id"] == data["destination_id"]:
            return Response(
                {"detail": "You are not going anywhere: choose two different locations."},
                status=400,
            )

        for end, field in (("start", "start_id"), ("destination", "destination_id")):
            entrance_id = data.get(f"{end}_entrance_id")
            entrances = locations[data[field]].get("entrances", [])
            if entrance_id and not any(item["id"] == entrance_id for item in entrances):
                return Response(
                    {"detail": f"Unknown {end} entrance for this building: {entrance_id!r}"},
                    status=400,
                )
            entrance = next((item for item in entrances if item["id"] == entrance_id), None)
            if entrance is None and entrances:
                entrance = entrances[0]
            features = entrance.get("features", {}) if entrance else {}
            if data["avoid_stairs"] and features.get("stairs") and not features.get("ramp"):
                return Response(
                    {
                        "detail": f"The selected {end} entrance has stairs and no recorded ramp. "
                        "Choose another entrance or turn off Avoid stairs."
                    },
                    status=404,
                )

        route = find_route(
            data["start_id"],
            data["destination_id"],
            avoid_stairs=data["avoid_stairs"],
            start_entrance_id=data.get("start_entrance_id", ""),
            destination_entrance_id=data.get("destination_entrance_id", ""),
        )
        if route is None:
            if construction_blocks_route(
                data["start_id"],
                data["destination_id"],
                data["avoid_stairs"],
                start_entrance_id=data.get("start_entrance_id", ""),
                destination_entrance_id=data.get("destination_entrance_id", ""),
            ):
                detail = "Construction blocks prevent travel between these locations."
            else:
                detail = "No available route connects these locations."
            return Response({"detail": detail}, status=404)
        return Response(route)
