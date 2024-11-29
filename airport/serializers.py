from django.db import transaction
from django.utils import timezone
from jsonschema import ValidationError
from rest_framework import serializers

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity"
        )


class AirplaneListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ('id', 'name', 'rows', 'seats_in_row', 'airplane_type', 'capacity')


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    destination = serializers.SlugRelatedField(
        queryset=Airport.objects.all(), slug_field="name"
    )
    source = serializers.SlugRelatedField(
        queryset=Airport.objects.all(), slug_field="name"
    )

    def validate(self, data):
        if data["source"] == data["destination"]:
            raise serializers.ValidationError(
                {"destination": "Source and destination cannot be the same."}
            )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    class Meta:
        model = Route
        fields = ("id", "full_route", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "full_name")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id",
                  "route",
                  "airplane",
                  "departure_time",
                  "arrival_time",
                  "crew"
                  )

    def validate(self, data):
        airplane = data.get("airplane")
        route = data.get("route")
        departure_time = data.get("departure_time")
        arrival_time = data.get("arrival_time")

        previous_flight = (
            Flight.objects.filter(airplane=airplane)
            .order_by("-arrival_time")
            .first()
        )
        previous_arrival_time = None

        if previous_flight:
            previous_arrival_time = previous_flight.arrival_time

            available_routes = Route.objects.filter(
                source=previous_flight.route.destination
            )
            available_route_list = None
            if available_routes:
                available_route_list = ", ".join(
                    [route.full_route for route in available_routes]
                )

            Flight.validate_flight_departure_location(
                route.source,
                previous_flight.route.destination,
                available_route_list,
                ValidationError,
            )

        Flight.validate_flight_time(
            departure_time,
            arrival_time,
            previous_arrival_time,
            ValidationError
        )

        return data


class FlightListSerializer(FlightSerializer):
    route = serializers.SlugRelatedField(read_only=True, slug_field="full_route")
    airplane = serializers.SlugRelatedField(read_only=True, slug_field="name")
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"], attrs["seat"], attrs["flight"].airplane, ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    route = serializers.CharField(source="flight.route.full_route", read_only=True)
    departure_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", source="flight.departure_time", read_only=True
    )
    arrival_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", source="flight.arrival_time", read_only=True
    )

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "route", "departure_time", "arrival_time")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class FlightDetailSerializer(FlightSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    taken_seats = TicketSeatsSerializer(read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew", "taken_seats")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        created_at = self.instance.created_at \
            if self.instance\
            else timezone.now()

        for ticket in data["tickets"]:
            Ticket.validate_ticket_flight(
                created_at, ticket["flight"].departure_time, ValidationError
            )
        return data

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    tickets = TicketDetailSerializer(many=True, read_only=True)

