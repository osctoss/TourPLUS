from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Hospital
from .serializers import HospitalListSerializer, HospitalDetailSerializer


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hospital.objects.filter(is_published=True).select_related(
        'city', 'city__state'
    ).prefetch_related(
        'treatment_offerings__treatment_category__specialty',
        'treatment_offerings__cost_estimate'
    )
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'city__state', 'verification_status', 'data_classification', 'international_patient_support']
    search_fields = ['name', 'city__name', 'city__state__name', 'treatment_offerings__treatment_category__name']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HospitalDetailSerializer
        return HospitalListSerializer
