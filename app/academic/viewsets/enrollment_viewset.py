from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from app.academic.models import Enrollment, Period
from app.academic.serializers import EnrollmentSerializer, EnrollmentListSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Enrollments'])
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all().order_by('-enrollment_date')
    serializer_class = EnrollmentSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'student_enrollments']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EnrollmentListSerializer
        return EnrollmentSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
            
        active_period = Period.objects.filter(is_active=True).first()
        
        if hasattr(self.request.user, 'student_profile'):
            return qs.filter(
                student=self.request.user.student_profile,
                period=active_period
            )
            
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            return qs.filter(
                course__teacher_assignments__teacher=teacher,
                course__teacher_assignments__period=active_period,
                period=active_period
            ).distinct()
            
        return qs.none()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='student', description='Filter by student ID', type=str),
            OpenApiParameter(name='course', description='Filter by course ID', type=str),
            OpenApiParameter(name='subject', description='Filter by subject ID', type=str),
            OpenApiParameter(name='period', description='Filter by period ID', type=str),
            OpenApiParameter(name='status', description='Filter by enrollment status', type=str),
        ],
        description="List enrollments with optional filtering"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        student_id = request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        course_id = request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        subject_id = request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        period_id = request.query_params.get('period')
        if period_id:
            queryset = queryset.filter(period_id=period_id)
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='student_id', description='Student ID', type=str, required=True),
        ],
        description="Get all enrollments for a specific student"
    )
    @action(detail=False, methods=['get'])
    def student_enrollments(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({"detail": "student_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        enrollments = self.get_queryset().filter(student_id=student_id)
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)