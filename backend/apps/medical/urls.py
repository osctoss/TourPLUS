from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpecialtyViewSet, TreatmentCategoryViewSet

app_name = 'medical'

router = DefaultRouter()
router.register(r'specialties', SpecialtyViewSet, basename='specialty')
router.register(r'treatments', TreatmentCategoryViewSet, basename='treatment')

urlpatterns = [
    path('', include(router.urls)),
]

