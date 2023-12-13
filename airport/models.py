from datetime import datetime, timedelta
import pytz

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

from utilities.image_file_paths import airplane_image_file_path


class Airport(models.Model):
    icao_designator = models.CharField(max_length=4)
    closest_big_city = models.CharField(max_length=63)

    class Meta:
        ordering = ["closest_big_city"]

    def __str__(self):
        return f"{self.closest_big_city} ({self.icao_designator})"


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    license_number = models.CharField(max_length=8)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Airline(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    call_sign = models.CharField(max_length=10)
    type = models.CharField(max_length=63)
    seats = models.IntegerField()
    cruise_mach_speed = models.FloatField()
    airline = models.ForeignKey(Airline,
                                on_delete=models.CASCADE,
                                related_name="airplanes")
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)

    def __str__(self):
        return f"{self.type} ({self.call_sign})"


class Route(models.Model):
    departure = models.ForeignKey(Airport,
                                  on_delete=models.CASCADE,
                                  related_name="departures")
    arrival = models.ForeignKey(Airport,
                                on_delete=models.CASCADE,
                                related_name="arrivals")
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.departure} - {self.arrival}"


class Flight(models.Model):
    route = models.ForeignKey(Route,
                              on_delete=models.CASCADE,
                              related_name="flights")
    airplane = models.ForeignKey(Airplane,
                                 on_delete=models.CASCADE,
                                 related_name="flights")
    departure_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.route} at {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    flight = models.ForeignKey(Flight,
                               on_delete=models.CASCADE,
                               related_name="tickets")
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name="tickets")
    seat = models.IntegerField()

    @staticmethod
    def validate_ticket(seat, airplane, departure_time, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (seat, "seat", "seats"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )
            tz_zone = pytz.timezone("UTC")
            if departure_time < (datetime.now(tz_zone) + timedelta(hours=2)):
                raise error_to_raise(
                    "Sorry, but you can not bye tickets in less than two"
                    "hours before departure time. Please chose another flight!"
                )

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.flight.airplane,
            self.flight.departure_time,
            ValidationError,
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
        return (
            f"{str(self.flight)} seat: {self.seat})"
        )

    class Meta:
        unique_together = ("flight", "seat")
        ordering = ["seat"]
