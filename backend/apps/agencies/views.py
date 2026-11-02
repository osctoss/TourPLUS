from rest_framework import viewsets, permissions
from .models import TravelAgency
from .serializers import TravelAgencySerializer


class TravelAgencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TravelAgency.objects.filter(is_published=True).select_related('headquarters_city')
    serializer_class = TravelAgencySerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'headquarters_city__name']

