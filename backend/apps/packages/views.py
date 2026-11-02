from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TravelPackage
from .serializers import TravelPackageSerializer


class TravelPackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TravelPackage.objects.filter(is_published=True).select_related(
        'agency'
    ).prefetch_related('inclusions', 'package_destinations__destination')
    serializer_class = TravelPackageSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['package_type', 'price_basis', 'agency', 'verification_status']
    search_fields = ['name', 'agency__name', 'description', 'destinations__name']
    ordering_fields = ['price_amount', 'duration_days', 'created_at']
