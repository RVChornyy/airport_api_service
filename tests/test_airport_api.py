from django.test import TestCase
import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Airplane, Airline, Crew, Route, Flight
from airport.serializers import FlightListSerializer

FLIGHT_URL = reverse("airport:flight-list")


def sample_airport(**params):
    defaults = {
        "icao_designator": "UKBB",
        "closest_big_city": "Boryspil"
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_airline(**params):
    defaults = {
        "name": "Aerosvit"
    }
    defaults.update(params)
    return Airline.objects.create(**defaults)


def sample_airplane(**params):
    defaults = {
        "call_sign": "UR-AAA",
        "type": "AN-2",
        "seats": 10,
        "cruise_mach_speed": .1,
        "airline": sample_airline()
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": "Nikolay",
        "last_name": "Gastello",
        "license_number": "FCL-0001"
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "departure": sample_airport(),
        "arrival": sample_airport(),
        "distance": 100
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_flight(**params):
    airplane = sample_airplane()
    crew = sample_crew()
    route = sample_route()
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2025-12-31T00:00:00Z"
    }
    defaults.update(params)
    flight = Flight.objects.create(**defaults)
    flight.crew.add(crew)

    return flight


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_client(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testuser@test.com",
            "zxcvb98765"
        )
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        sample_flight(departure_time="2024-12-31 00:00:00")
        sample_flight()
        response = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

# All the tests are not implemented already

