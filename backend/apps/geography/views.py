from rest_framework import viewsets, permissions
from .models import Country, State, City
from .serializers import CountrySerializer, StateSerializer, CitySerializer


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.AllowAny]


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.filter(is_active=True).select_related('state', 'state__country')
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'state__name']

