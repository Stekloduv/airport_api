from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneViewSet,
    AirplaneTypeViewSet,
    RouteViewSet,
    CrewViewSet,
    OrderViewSet,
    TicketViewSet,
    FlightViewSet,
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
