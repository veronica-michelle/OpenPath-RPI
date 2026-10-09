from rest_framework import serializers


class LocationSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    elevation = serializers.FloatField(required=False, allow_null=True)
    entrances = serializers.ListField(child=serializers.DictField(), required=False)


class PointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class RouteRequestSerializer(serializers.Serializer):
    start_id = serializers.CharField()
    destination_id = serializers.CharField()
    start_entrance_id = serializers.CharField(required=False, allow_blank=True)
    destination_entrance_id = serializers.CharField(required=False, allow_blank=True)
    avoid_stairs = serializers.BooleanField(required=False, default=False)


class RouteResponseSerializer(serializers.Serializer):
    nodeIds = serializers.ListField(child=serializers.CharField())
    points = PointSerializer(many=True)
    route_points = PointSerializer(many=True)
    usedStairs = serializers.BooleanField()
    distanceFt = serializers.FloatField()
    total_distance_m = serializers.FloatField()
    elevationGainFt = serializers.FloatField()
    elevationLossFt = serializers.FloatField()
    minutes = serializers.IntegerField()
    steepness = serializers.CharField()
    directions = serializers.ListField(child=serializers.CharField())
    maneuvers = serializers.ListField(child=serializers.DictField())
    accessibility_notes = serializers.ListField(child=serializers.CharField())
