from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    RecommendationRun,
    HospitalScenario
)
from .serializers import (
    RecommendationRunSerializer,
    HospitalScenarioSerializer,
    DestinationRecommendationSerializer,
    PackageMatchSerializer
)


class RecommendationRunViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecommendationRunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = RecommendationRun.objects.filter(trip_request__user=self.request.user).prefetch_related('scenarios')
        trip_request_id = self.request.GET.get('trip_request')
        if trip_request_id:
            qs = qs.filter(trip_request_id=trip_request_id)
        return qs


class HospitalScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HospitalScenarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HospitalScenario.objects.filter(recommendation_run__trip_request__user=self.request.user).prefetch_related('budget_lines')

    @action(detail=True, methods=['get'])
    def destinations(self, request, pk=None):
        scenario = self.get_object()
        scope = request.query_params.get('scope')
        queryset = scenario.destinations.all()
        if scope:
            queryset = queryset.filter(tourism_scope=scope)
        serializer = DestinationRecommendationSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def packages(self, request, pk=None):
        scenario = self.get_object()
        matches = scenario.package_matches.all().prefetch_related('credits')
        serializer = PackageMatchSerializer(matches, many=True)
        return Response(serializer.data)

