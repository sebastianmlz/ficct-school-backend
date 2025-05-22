from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q

from app.authentication.models import Teacher
from app.authentication.serializers import TeacherSerializer, TeacherListSerializer
from app.academic.serializers import CourseListSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Teachers'])
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all().order_by('-created_at')
    serializer_class = TeacherSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'courses']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherListSerializer
        return TeacherSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='Search term for teacher name or ID', type=str),
            OpenApiParameter(name='specialization', description='Filter by specialization', type=str),
        ],
        description="List teachers with optional filtering"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__id__icontains=search)
            )
        
        specialization = request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Get courses assigned to this teacher"
    )
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        teacher = self.get_object()
        courses = teacher.assigned_courses
        
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Partially update a teacher record, including user data",
        methods=["PATCH"]
    )
    def partial_update(self, request, *args, **kwargs):
        """Handle partial updates of teacher data, including nested user data."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)