from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q, Count
from app.academic.models import Course, Enrollment, Period, TeacherAssignment
from app.academic.serializers import CourseSerializer, CourseListSerializer
from app.authentication.serializers import StudentListSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Courses'])
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('year', 'name')
    serializer_class = CourseSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'students']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
            
        active_period = Period.objects.filter(is_active=True).first()
        
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            return qs.filter(
                teacher_assignments__teacher=teacher,
                teacher_assignments__period=active_period
            ).distinct()
            
        if hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
            return qs.filter(
                enrollments__student=student,
                enrollments__period=active_period,
                enrollments__status='active'
            ).distinct()
            
        return qs.none()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='Search by name or code', type=str),
            OpenApiParameter(name='year', description='Filter by year', type=int),
            OpenApiParameter(name='active', description='Filter by active status', type=bool),
        ],
        description="List courses with optional filtering"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        year = request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        active = request.query_params.get('active')
        if active is not None:
            is_active = active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        queryset = queryset.annotate(student_count=Count('enrollments'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(description="Get students enrolled in this course")
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        course = self.get_object()
        active_period = Period.objects.filter(is_active=True).first()
        enrollments = Enrollment.objects.filter(
            course=course, 
            status='active',
            period=active_period
        )
        students = [enrollment.student for enrollment in enrollments]
        page = self.paginate_queryset(students)
        if page is not None:
            serializer = StudentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)