from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationRunViewSet, HospitalScenarioViewSet

app_name = 'recommendations'

router = DefaultRouter()
router.register(r'runs', RecommendationRunViewSet, basename='recommendation-run')
router.register(r'scenarios', HospitalScenarioViewSet, basename='hospital-scenario')

urlpatterns = [
    path('', include(router.urls)),
]

