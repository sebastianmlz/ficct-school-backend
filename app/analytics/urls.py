from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.analytics.viewsets import PerformancePredictionViewSet, DashboardViewSet

router = DefaultRouter()
router.register(r'performance-predictions', PerformancePredictionViewSet, basename='performance-predictions')
router.register(r'dashboards', DashboardViewSet, basename='dashboard')


urlpatterns = [
    path('', include(router.urls)),
]