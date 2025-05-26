from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q, Count
from app.academic.models import Period, Enrollment
from app.academic.serializers import PeriodSerializer, PeriodListSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Academic Periods'])
class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all().order_by('-start_date')
    serializer_class = PeriodSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'current']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PeriodListSerializer
        return PeriodSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='Search by name', type=str),
            OpenApiParameter(name='active', description='Filter by active status', type=bool),
        ],
        description="List academic periods with optional filtering"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        active = request.query_params.get('active')
        if active is not None:
            is_active = active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        queryset = queryset.annotate(enrollment_count=Count('enrollments'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(description="Get the current active academic period")
    @action(detail=False, methods=['get'])
    def current(self, request):
        period = Period.objects.filter(is_active=True).first()
        if not period:
            return Response({"detail": "No active period found."}, status=404)
        serializer = self.get_serializer(period)
        return Response(serializer.data)