from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelPackageViewSet

app_name = 'packages'

router = DefaultRouter()
router.register(r'', TravelPackageViewSet, basename='package')

urlpatterns = [
    path('', include(router.urls)),
]

