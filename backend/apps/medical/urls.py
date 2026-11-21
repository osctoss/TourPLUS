from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpecialtyViewSet, TreatmentCategoryViewSet

app_name = 'medical'

router = DefaultRouter()
router.register(r'specialties', SpecialtyViewSet, basename='specialty')
router.register(r'treatments', TreatmentCategoryViewSet, basename='treatment')
router.register(r'treatment-categories', TreatmentCategoryViewSet, basename='treatment-category')

urlpatterns = [
    path('', include(router.urls)),
]

