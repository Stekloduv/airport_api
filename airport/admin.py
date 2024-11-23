from django.contrib import admin
from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Crew,
    Order,
    Ticket,
    Flight,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "airplane_type")
    search_fields = ("name",)
    list_filter = ("airplane_type",)


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "seating_capacity", "cargo_capacity")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "distance")
    search_fields = ("source__name", "destination__name")
    list_filter = ("source", "destination")


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "position")
    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "created_at")
    search_fields = ("customer__name", "status")
    list_filter = ("status", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "flight", "seat_number", "price")
    search_fields = ("flight__route__source__name", "flight__route__destination__name")
    list_filter = ("flight",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "departure_time", "arrival_time")
    list_filter = ("route", "departure_time", "arrival_time")
