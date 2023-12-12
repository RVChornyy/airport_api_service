from datetime import datetime, timedelta

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (Airport,
                            Airplane,
                            Airline,
                            Crew,
                            Flight,
                            Ticket,
                            Order)
from utilities.get_weather import get_weather


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class AirportDetailSerializer(AirportSerializer):
    current_weather = serializers.SerializerMethodField(
        method_name="get_airport_weather"
    )

    class Meta:
        model = Airport
        fields = (
            "id",
            "icao_designator",
            "closest_big_city",
            "current_weather",
        )

    @staticmethod
    def get_airport_weather(obj):
        weather = get_weather(obj.closest_big_city)
        return weather


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = "__all__"


class AirplaneDetailSerializer(AirplaneSerializer):
    airline = AirlineSerializer(many=False, read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "call_sign",
            "type",
            "seats",
            "cruise_mach_speed",
            "airline",
            "image",
        )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class AirplaneAirlineSerializer(AirplaneSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "call_sign",
            "type",
            "seats",
            "image",
        )


class AirlineDetailSerializer(AirlineSerializer):
    airplanes = AirplaneAirlineSerializer(many=True, read_only=True)

    class Meta:
        model = Airline
        fields = (
            "id",
            "name",
            "airplanes",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["seat"],
            attrs["flight"].airplane,
            attrs["flight"].departure_time,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "seat", "flight")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("seat",)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    airplane = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "crew",
            "airplane",
            "route",
            "departure_time",
        )


class FlightDetailSerializer(FlightSerializer):
    departure = serializers.CharField(source="route.departure", read_only=True)
    arrival = serializers.CharField(source="route.arrival", read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    airplane = serializers.StringRelatedField(many=False, read_only=True)
    taken_seats = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )
    tickets_available = serializers.SerializerMethodField(
        method_name="get_tickets_available"
    )
    arrival_time = serializers.SerializerMethodField(
        method_name="get_arrival_time"
    )

    class Meta:
        model = Flight
        fields = (
            "crew",
            "departure",
            "arrival",
            "airplane",
            "taken_seats",
            "tickets_available",
            "departure_time",
            "arrival_time",
        )

    @staticmethod
    def get_arrival_time(obj):
        """
        Function calculates arrival time by adding approximate
        flight time to departure time.
        Flight time is calculating dividing route distance
        by average cruise speed.
        Average cruise speed is measured in knots
        and is a result of multiplication of average mach speed
        by special coefficient(550), that is an average TAS(true air speed)
        at 1 Mach at flight level 360(36000 ft).

        """
        flight_time = timedelta(
            hours=round(
                (obj.route.distance / (obj.airplane.cruise_mach_speed * 550)
                 ), 1)
        )
        print(flight_time)
        return obj.departure_time + flight_time

    @staticmethod
    def get_tickets_available(obj):
        return obj.airplane.seats - obj.tickets.count()


class TicketListSerializer(TicketSerializer):
    flight = serializers.CharField(source="flight.route", read_only=True)
    departure_time = serializers.CharField(
        source="flight.departure_time",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "flight",
            "departure_time",
            "seat"
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(
        many=True,
        read_only=True,
        allow_empty=False
    )
