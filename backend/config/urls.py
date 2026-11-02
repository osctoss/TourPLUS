"""
URL Configuration for TourPlus AI
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint reporting API and database connectivity status.
    """
    db_status = 'ok'
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_status = f'error: {str(e)}'

    return Response({
        'status': 'healthy' if db_status == 'ok' else 'degraded',
        'product': 'TourPlus AI',
        'version': '1.0.0',
        'database': db_status,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health_check, name='health-check'),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/catalog/', include('apps.medical.urls')),
    path('api/v1/hospitals/', include('apps.hospitals.urls')),
    path('api/v1/geo/', include('apps.geography.urls')),
    path('api/v1/tourism/', include('apps.tourism.urls')),
    path('api/v1/packages/', include('apps.packages.urls')),
    path('api/v1/trip-requests/', include('apps.trip_planning.urls')),
    path('api/v1/recommendations/', include('apps.recommendations.urls')),
    path('api/v1/final-plans/', include('apps.final_plans.urls')),
]

