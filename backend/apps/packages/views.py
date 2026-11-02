from rest_framework import viewsets, permissions
from .models import TravelPackage
from .serializers import TravelPackageSerializer


class TravelPackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TravelPackage.objects.filter(is_published=True).select_related('agency').prefetch_related('inclusions', 'package_destinations__destination')
    serializer_class = TravelPackageSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'agency__name']

