from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema
from app.academic.models import Trimester
from app.academic.serializers import TrimesterSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Academic Trimesters'])
class TrimesterViewSet(viewsets.ModelViewSet):
    queryset = Trimester.objects.all().order_by('period__start_date', 'start_date')
    serializer_class = TrimesterSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination