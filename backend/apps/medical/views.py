from rest_framework import viewsets, permissions
from .models import Specialty, TreatmentCategory
from .serializers import SpecialtySerializer, TreatmentCategorySerializer


class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialty.objects.filter(is_active=True).prefetch_related('treatment_categories')
    serializer_class = SpecialtySerializer
    permission_classes = [permissions.AllowAny]


class TreatmentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TreatmentCategory.objects.filter(is_active=True).select_related('specialty')
    serializer_class = TreatmentCategorySerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['specialty', 'specialty__slug']

