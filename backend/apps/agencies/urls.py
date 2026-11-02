from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelAgencyViewSet

app_name = 'agencies'

router = DefaultRouter()
router.register(r'', TravelAgencyViewSet, basename='agency')

urlpatterns = [
    path('', include(router.urls)),
]

