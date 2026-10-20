from django.urls import path

from .views import LocationListView, MapGraphView, RouteView

urlpatterns = [
    path("map/", MapGraphView.as_view(), name="map-graph"),
    path("locations/", LocationListView.as_view(), name="locations"),
    path("route/", RouteView.as_view(), name="route"),
]
