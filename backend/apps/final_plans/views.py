from rest_framework import viewsets, permissions
from .models import FinalPlan
from .serializers import FinalPlanSerializer


class FinalPlanViewSet(viewsets.ModelViewSet):
    serializer_class = FinalPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FinalPlan.objects.filter(user=self.request.user).select_related(
            'hospital_scenario', 'package_match'
        ).prefetch_related('destinations__destination')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

