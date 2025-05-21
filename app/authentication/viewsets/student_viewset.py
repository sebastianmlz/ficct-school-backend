# filepath: c:\Users\PC Gamer\Desktop\Repositories\python\django\ficct-school-backend\app\authentication\viewsets\student_viewset.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q

from app.authentication.models import Student
from app.authentication.serializers import StudentSerializer, StudentListSerializer
from core.pagination import CustomPagination


@extend_schema(tags=['Students'])
class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student records."""
    
    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action in ['list', 'retrieve', 'profile']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='Search term for student name or ID', type=str),
            OpenApiParameter(name='grade_level', description='Filter by grade level', type=str),
        ],
        description="List students with optional filtering"
    )
    def list(self, request, *args, **kwargs):
        """List students with optional filtering."""
        queryset = self.filter_queryset(self.get_queryset())
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(student_id__icontains=search)
            )
        
        grade_level = request.query_params.get('grade_level', None)
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Get detailed profile of a student with academic information"
    )
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get detailed student profile with academic metrics."""
        student = self.get_object()
        serializer = self.get_serializer(student)
        
        data = serializer.data
        
        data['academic_metrics'] = {
            'current_average': student.current_average,
            'attendance_percentage': student.attendance_percentage,
        }
        
        return Response(data)