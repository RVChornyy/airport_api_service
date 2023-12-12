from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import Airport, Airline, Airplane, Crew, Flight, Order
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (AirportSerializer,
                                 AirportDetailSerializer,
                                 AirlineSerializer,
                                 AirplaneSerializer,
                                 AirplaneDetailSerializer,
                                 CrewSerializer,
                                 FlightSerializer,
                                 FlightDetailSerializer,
                                 AirlineDetailSerializer,
                                 FlightListSerializer,
                                 OrderListSerializer,
                                 OrderSerializer,
                                 AirplaneImageSerializer)


class Pagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirportDetailSerializer
        return AirportSerializer


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirlineDetailSerializer
        return AirlineSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightDetailSerializer
        if self.action == "list":
            return FlightListSerializer
        return FlightSerializer

    def get_queryset(self):
        departure = self.request.query_params.get("departure")
        arrival = self.request.query_params.get("arrival")

        queryset = self.queryset.select_related(
            "route__departure",
            "route__arrival",
            "airplane"
        ).prefetch_related("crew")

        if departure:
            queryset = queryset.filter(
                route__departure__closest_big_city__icontains=departure
            )

        if arrival:
            queryset = queryset.filter(
                route__arrival__closest_big_city__icontains=arrival
            )

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure",
                type=OpenApiTypes.STR,
                description="Filter by flight departure",
            ),
            OpenApiParameter(
                "arrival",
                type=OpenApiTypes.STR,
                description="Filter by flight arrival"

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet,):
    queryset = Order.objects.all()
    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tickets__flight__route__departure",
            "tickets__flight__route__arrival",
        )
