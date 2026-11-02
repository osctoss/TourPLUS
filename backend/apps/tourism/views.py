from rest_framework import viewsets, permissions
from .models import DestinationCategory, TouristDestination
from .serializers import DestinationCategorySerializer, TouristDestinationSerializer


class DestinationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DestinationCategory.objects.filter(is_active=True)
    serializer_class = DestinationCategorySerializer
    permission_classes = [permissions.AllowAny]


class TouristDestinationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TouristDestination.objects.filter(is_published=True).select_related('city', 'city__state').prefetch_related('categories', 'cost_estimates')
    serializer_class = TouristDestinationSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'city__name', 'city__state__name']

