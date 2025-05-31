from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from app.academic.models import Grade, Period
from app.academic.serializers import GradeSerializer, GradeDetailSerializer
from core.pagination import CustomPagination
from core.permissions import IsTeacherOrAdmin, IsStudentOwnerOrTeacherOrAdmin

@extend_schema(tags=['Grades'])
class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.select_related(
        'student__user', 'subject', 'period',
        'assessment_item__subject', 'assessment_item__course', 'assessment_item__trimester__period'
    ).all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'student': ['exact'],
        'subject': ['exact'],
        'period': ['exact'],
        'assessment_item': ['exact'],
        'assessment_item__trimester': ['exact'],
        'assessment_item__trimester__period': ['exact'],
        'value': ['exact', 'gte', 'lte'],
    }

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GradeDetailSerializer
        return GradeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsTeacherOrAdmin]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [IsStudentOwnerOrTeacherOrAdmin]
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        period_id = request.query_params.get('period')
        assessment_period_id = request.query_params.get('assessment_item__trimester__period')
        assessment_trimester_id = request.query_params.get('assessment_item__trimester')
        assessment_item_id = request.query_params.get('assessment_item')

        if not period_id and not assessment_period_id and not assessment_trimester_id and not assessment_item_id:
            active_period = Period.objects.filter(is_active=True).first()
            if active_period:
                queryset = queryset.filter(period=active_period)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)