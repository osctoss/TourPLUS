from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import TripRequest, TripRequestInterest
from .serializers import TripRequestSerializer


class TripRequestViewSet(viewsets.ModelViewSet):
    serializer_class = TripRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Enforce strict patient ownership
        return TripRequest.objects.filter(user=self.request.user).select_related('specialty', 'treatment_category').prefetch_related('interests')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_request(self, request, pk=None):
        trip_request = self.get_object()
        if trip_request.status != TripRequest.Status.DRAFT:
            return Response({'error': 'Only draft requests can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
        
        trip_request.status = TripRequest.Status.SUBMITTED
        trip_request.submitted_at = timezone.now()
        trip_request.save()
        return Response(TripRequestSerializer(trip_request).data)

