from rest_framework import viewsets, permissions
from .models import Hospital
from .serializers import HospitalListSerializer, HospitalDetailSerializer


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hospital.objects.filter(is_published=True).select_related('city', 'city__state')
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HospitalDetailSerializer
        return HospitalListSerializer

