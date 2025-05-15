from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import LoggerServiceViewSet

router = DefaultRouter()
router.register(r'logs', LoggerServiceViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]
