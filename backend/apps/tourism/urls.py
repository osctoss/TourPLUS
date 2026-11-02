from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DestinationCategoryViewSet, TouristDestinationViewSet

app_name = 'tourism'

router = DefaultRouter()
router.register(r'categories', DestinationCategoryViewSet, basename='destination-category')
router.register(r'destinations', TouristDestinationViewSet, basename='tourist-destination')

urlpatterns = [
    path('', include(router.urls)),
]

