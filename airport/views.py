from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from airport.models import Airport, Airline, Airplane, Crew, Flight, Order
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import AirportSerializer, AirportDetailSerializer, AirlineSerializer, AirplaneSerializer, \
    AirplaneDetailSerializer, CrewSerializer, FlightSerializer, FlightDetailSerializer, AirlineDetailSerializer, \
    FlightListSerializer, OrderListSerializer, OrderSerializer


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
        return AirplaneSerializer


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
        return Order.objects.filter(user=self.request.user)

