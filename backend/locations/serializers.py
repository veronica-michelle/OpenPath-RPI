from rest_framework import serializers


class LocationSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class PointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class RouteRequestSerializer(serializers.Serializer):
    start_id = serializers.CharField()
    destination_id = serializers.CharField()
    avoid_stairs = serializers.BooleanField(required=False, default=False)


class RouteResponseSerializer(serializers.Serializer):
    route_points = PointSerializer(many=True)
    total_distance_m = serializers.FloatField()
    directions = serializers.ListField(child=serializers.CharField())
    accessibility_notes = serializers.ListField(child=serializers.CharField())
