from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinalPlanViewSet

app_name = 'final_plans'

router = DefaultRouter()
router.register(r'', FinalPlanViewSet, basename='final-plan')

urlpatterns = [
    path('', include(router.urls)),
]

