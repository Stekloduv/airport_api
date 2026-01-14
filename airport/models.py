from datetime import timedelta

from django.conf import settings
from django.db import models
from jsonschema import ValidationError


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_as_source"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_as_destination"
    )
    distance = models.FloatField()

    @staticmethod
    def validate_route(source, destination, error_to_raise):
        if source == destination:
            raise error_to_raise("Source and destination airports must be different.")

    @property
    def full_route(self) -> str:
        return f"{self.source.name} - {self.destination.name}"

    def __str__(self):
        return f"{self.source.name} {self.destination.name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.route.destination} - {self.departure_time}"

    @staticmethod
    def validate_flight_departure_location(
        source, previous_destination, available_route_list, error_to_raise
    ):
        if source != previous_destination:
            if available_route_list:
                raise error_to_raise(
                    "Departure location should match the arrival location "
                    "of the previous flight. "
                    f"Available routes with the correct departure location: "
                    f"{available_route_list}."
                )
            else:
                raise error_to_raise(
                    "Departure location should match the arrival location "
                    "of the previous flight. "
                    "There are no routes with the correct departure location. "
                    "You need to create a route first, "
                    "then schedule the flight."
                )

    @staticmethod
    def validate_flight_time(
        departure_time, arrival_time, previous_arrival_time, error_to_raise
    ):
        if departure_time >= arrival_time:
            raise error_to_raise(
                "Departure time must"
                " be earlier than arrival time."
            )

        if previous_arrival_time:
            if departure_time < previous_arrival_time:
                next_possible_departure = (previous_arrival_time
                                           + timedelta(hours=3)
                                           )
                raise error_to_raise(
                    f"Cannot schedule this flight "
                    f"before the previous flight arrives. "
                    f"The airplane's last scheduled flight "
                    f"arrives at {previous_arrival_time}. "
                    f"The next possible departure time is "
                    f"{next_possible_departure}."
                )
            if departure_time < previous_arrival_time + timedelta(hours=3):
                next_possible_departure = (previous_arrival_time
                                           + timedelta(hours=3)
                                           )
                raise error_to_raise(
                    f"The airplane needs a 3-hour rest "
                    f"after its previous flight. "
                    f"The previous flight arrived at {previous_arrival_time}. "
                    f"The next available departure time is "
                    f"{next_possible_departure}."
                )

            time_difference = departure_time - previous_arrival_time
            if time_difference > timedelta(hours=24):
                raise error_to_raise(
                    f"The time difference between consecutive flights "
                    f"shouldn't exceed 24 hours. "
                    f"Previous flight arrived at {previous_arrival_time}, "
                    f"and this flight is scheduled to depart "
                    f"at {departure_time}."
                )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    f"ticket_attr_name: {ticket_attr_name} "
                    f"number must be in available range: "
                    f"(1, {airplane_attr_name}): "
                    f"(1, {count_attrs})"
                )

    @staticmethod
    def validate_ticket_flight(
            order_created_at,
            flight_departure_time,
            error_to_raise
    ):
        if order_created_at > flight_departure_time:
            raise error_to_raise(
                {
                    "order": "Booking for past flights is not available. "
                    f"Order created at {order_created_at} "
                    f"but the flight departs at "
                    f"{flight_departure_time}."
                }
            )

    def clean(self):
        Ticket.validate_ticket(
            self.row, self.seat, self.flight.airplane, ValidationError
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
