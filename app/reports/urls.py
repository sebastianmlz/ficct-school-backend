from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.reports.viewsets.bulletin_viewset import BulletinViewSet

router = DefaultRouter()
router.register(r'bulletins', BulletinViewSet, basename='bulletin')

urlpatterns = [
    path('', include(router.urls)),
]