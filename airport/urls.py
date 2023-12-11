from django.urls import path, include
from rest_framework import routers

from airport.views import AirportViewSet, AirlineViewSet, AirplaneViewSet, CrewViewSet, FlightViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airlines", AirlineViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("crew", CrewViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
