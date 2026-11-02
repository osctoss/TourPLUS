from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripRequestViewSet

app_name = 'trip_planning'

router = DefaultRouter()
router.register(r'', TripRequestViewSet, basename='trip-request')

urlpatterns = [
    path('', include(router.urls)),
]

