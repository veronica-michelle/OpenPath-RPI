"""Small geometry helpers used until real graph-based pathfinding exists."""

import math

EARTH_RADIUS_METERS = 6371000


def haversine_meters(lat1, lng1, lat2, lng2):
    """Great-circle distance in meters between two lat/lng points."""
    to_rad = math.radians

    d_lat = to_rad(lat2 - lat1)
    d_lng = to_rad(lng2 - lng1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_METERS * c


def nearest_location(coord, locations):
    """Return the nearest location and its distance in meters.

    `coord` and the entries in locations can be a (lat, lng) pair or a dictionary with coordinates.
    """
    if not locations:
        return None, None

    def _as_coord(value):
        if value is None:
            return None

        if isinstance(value, (list, tuple)) and len(value) == 2:
            return float(value[0]), float(value[1])

        if isinstance(value, dict):
            lat = value.get("lat")
            lng = value.get("lng")
            if lat is None and "latitude" in value:
                lat = value.get("latitude")
            if lng is None and "longitude" in value:
                lng = value.get("longitude")
            if lat is not None and lng is not None:
                return float(lat), float(lng)

        return None

    start_loc = _as_coord(coord)
    if start_loc is None:
        raise ValueError("coord must be a (lat, lng) pair or dict with lat/lng fields")

    best_loc = None
    best_distance = None

    for location in locations:
        loc_coord = _as_coord(location)
        if loc_coord is None and isinstance(location, dict):
            loc_coord = _as_coord(location.get("coords") or location.get("coordinates"))
        if loc_coord is None:
            continue

        distance = haversine_meters(start_loc[0], start_loc[1], loc_coord[0], loc_coord[1])
        if best_distance is None or distance < best_distance:
            best_loc = location
            best_distance = distance

    return best_loc, best_distance
